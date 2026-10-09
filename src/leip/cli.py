import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv
from .agent import extract, reference_extraction
from .source import DEFAULT_URL, capture, read_table
from .storage import persist
from .validation import validate


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="LEIP: mediana de inflación BCU a 12 y 24 meses")
    parser.add_argument("--url", default=DEFAULT_URL, help="Publicación HTML BCU explícita; no descubre automáticamente la última")
    parser.add_argument("--demo", action="store_true", help="Extracción determinística sin LLM; no usa la API")
    parser.add_argument("--no-db", action="store_true", help="Guardar solo JSON")
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    run = {"_id": str(uuid4()), "created_at": datetime.now(timezone.utc).isoformat(), "contract_version": "bcu-inflation-median-v1", "mode": "deterministic_demo" if args.demo else "langchain_openai", "model": None if args.demo else os.getenv("OPENAI_MODEL", "gpt-5.5"), "status": "held", "observations": []}
    try:
        if not args.demo and not os.getenv("OPENAI_API_KEY"):
            raise ValueError("Falta OPENAI_API_KEY. Completá .env o ejecutá --demo.")
        artifact = capture(args.url, args.output_dir / "artifacts")
        run["artifact"] = artifact
        table = read_table(Path(artifact["path"]).read_bytes())
        run["tool_evidence"] = table
        extraction = reference_extraction(table) if args.demo else extract(table)
        run["observations"] = extraction.model_dump()["observations"]
        validate(extraction, table)
        run["validation"] = "source_cells_match"
        # Una ejecución de un solo agente no satisface el consenso A/B/C de LEIP.
        run["status"] = "candidate_for_review"
    except Exception as error:
        # No registrar cuerpos de respuesta/API ni secretos en los artefactos.
        run["error_type"] = type(error).__name__
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / f"{run['_id']}.json").write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
        parser.exit(1, f"Extracción retenida ({type(error).__name__}). Revisá configuración, acceso y formato de la publicación.\n")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    path = args.output_dir / f"{run['_id']}.json"
    path.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(run, ensure_ascii=False, indent=2))
    print(f"JSON: {path}")
    if not args.no_db:
        try:
            persist(run, os.getenv("MONGODB_URI", "mongodb://localhost:27017"), os.getenv("MONGODB_DATABASE", "leip"))
            print("Ejecución guardada en MongoDB.")
        except Exception as error:
            parser.exit(1, f"MongoDB no disponible ({type(error).__name__}); el JSON está guardado en {path}.\n")


if __name__ == "__main__":
    main()
