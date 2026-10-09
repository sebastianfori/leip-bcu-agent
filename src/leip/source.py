"""Captura del HTML y lectura determinística de una tabla acotada."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import re
import ssl
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import httpx
import truststore

DEFAULT_URL = "https://www.bcu.gub.uy/Politica-Economica-y-Mercados/Expectativas%20para%20la%20inflacin%20y%20la%20economa/Monitor_trimestral_set26.html"
MONTHS = dict(zip(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "setiembre", "octubre", "noviembre", "diciembre"], range(1, 13)))
MONTHS["septiembre"] = 9


def capture(url: str, directory: Path) -> dict:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "www.bcu.gub.uy" or parsed.port not in (None, 443):
        raise ValueError("Solo se admiten URLs HTTPS del sitio www.bcu.gub.uy.")
    # No seguir redirecciones: evita descargar otro origen sin autorización.
    with httpx.stream("GET", url, timeout=30, follow_redirects=False, verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)) as response:
        response.raise_for_status()
        if "text/html" not in response.headers.get("content-type", ""):
            raise ValueError("El prototipo solo admite HTML.")
        chunks, size = [], 0
        for chunk in response.iter_bytes():
            size += len(chunk)
            if size > 10_000_000:
                raise ValueError("La publicación excede el límite de 10 MB.")
            chunks.append(chunk)
    raw = b"".join(chunks)
    digest = sha256(raw).hexdigest()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{digest}.html"
    if not path.exists():
        path.write_bytes(raw)
    return {"source_url": url, "sha256": digest, "path": str(path), "retrieved_at": datetime.now(timezone.utc).isoformat()}


def read_table(raw: bytes) -> dict:
    soup = BeautifulSoup(raw, "html.parser", from_encoding="utf-8")
    matches = []
    for index, table in enumerate(soup.find_all("table")):
        text = table.get_text(" ", strip=True)
        if "EXPECTATIVAS DE INFLACIÓN" in text.upper() and "Mediana" in text and "próximos 12 meses" in text:
            matches.append((index, table))
    if len(matches) != 1:
        raise ValueError("No hay una única tabla de inflación reconocible; requiere revisión.")
    index, table = matches[0]
    rows = [[c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])] for tr in table.find_all("tr")]
    headers = [row for row in rows if any("próximos 12 meses" in c for c in row)]
    medians = [row for row in rows if row and row[0].casefold() == "mediana"]
    if len(headers) != 1 or len(medians) != 1 or len(headers[0]) != len(medians[0]):
        raise ValueError("Encabezados o fila Mediana cambiaron; requiere revisión.")
    header, median = headers[0], medians[0]
    title = table.get_text(" ", strip=True)
    publication = re.search(r"EXPECTATIVAS DE INFLACIÓN\s+([A-Za-záéíóú]+)\s+de\s+(\d{4})", title, re.I)
    if not publication or publication[1].lower() not in MONTHS:
        raise ValueError("No se pudo identificar el mes de encuesta.")
    survey_month = f"{publication[2]}-{MONTHS[publication[1].lower()]:02d}"
    cells = []
    for horizon in (12, 24):
        positions = [i for i, c in enumerate(header) if f"próximos {horizon} meses" in c]
        if len(positions) != 1:
            raise ValueError(f"No hay un único horizonte de {horizon} meses.")
        col = positions[0]
        label, original = header[col], median[col]
        dates = re.findall(r"([A-Za-záéíóú]+)\s+(\d{4})", label)
        if len(dates) != 2 or any(m.lower() not in MONTHS for m, _ in dates):
            raise ValueError("Período objetivo no reconocido.")
        start, end = [f"{year}-{MONTHS[month.lower()]:02d}" for month, year in dates]
        start_year, start_month = map(int, start.split("-"))
        end_year, end_month = map(int, end.split("-"))
        if start != survey_month or (end_year - start_year) * 12 + end_month - start_month + 1 != horizon:
            raise ValueError("El período no corresponde al mes de encuesta y al horizonte.")
        if not re.fullmatch(r"-?\d+(?:,\d+)?", original):
            raise ValueError("Valor ausente o formato numérico inesperado.")
        cells.append({"cell_id": f"table:{index}/mediana/column:{col}", "horizon_months": horizon, "target_start": start, "target_end": end, "horizon_label": label, "raw_value": original, "value": float(original.replace(",", "."))})
    return {"country": "URY", "survey_month": survey_month, "variable": "inflation_expectation", "statistic": "median", "unit": "percent", "cells": cells}
