# LEIP · Agente BCU

Prototipo para la próxima tutoría: un agente de **LangChain + OpenAI** extrae la **mediana de inflación esperada a 12 y 24 meses** de una publicación HTML del Banco Central del Uruguay, verifica la salida contra las celdas capturadas y conserva la ejecución en **MongoDB** y JSON.

## Ejecutar en Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
Copy-Item .env.example .env
docker compose up -d
.\.venv\Scripts\leip.exe --demo
```

Para usar el agente real, completá `OPENAI_API_KEY` en `.env` y ejecutá:

```powershell
.\.venv\Scripts\leip.exe
```

El modelo se configura con `OPENAI_MODEL`. La API de OpenAI requiere su propia clave y facturación; iniciar sesión en ChatGPT no configura esa clave. Nunca subas `.env` al repositorio.

Sin Docker ni API podés comprobar descarga, lectura, validación y JSON:

```powershell
.\.venv\Scripts\leip.exe --demo --no-db
```

`--demo` es una extracción determinística, **no** una ejecución simulada del agente. `--no-db` desactiva solamente MongoDB. La publicación inicial es **setiembre de 2026**, fijada explícitamente para una prueba reproducible; no se presenta como búsqueda automática de la última publicación. Se puede seleccionar otro monitor HTML compatible con `--url URL_BCU`.

## Datos conservados

- País implícito de la fuente: Uruguay; variable: expectativa de inflación; estadístico: mediana; unidad: porcentaje.
- Mes de encuesta separado del período objetivo y del horizonte de 12/24 meses.
- Valor original con coma y valor numérico normalizado.
- URL, fecha UTC de descarga, SHA-256 y copia del HTML en `data/artifacts/`.
- Identificador de tabla/celda, encabezados y resultado de herramienta.
- Identificador único de ejecución, contrato, modelo, estado y resultado de validación.

Los datos se guardan en `leip.extraction_runs`. Cada intento es un documento nuevo: no se borra el histórico. La captura completa queda en disco; al desplegar, ese directorio necesita almacenamiento persistente o un almacén de objetos.

## Límites del prototipo

Solo admite el monitor HTML con una tabla de inflación reconocible. PDF, Excel, descubrimiento de publicaciones, otros estadísticos y las expectativas de PIB, tipo de cambio y TPM quedan para siguientes iteraciones. Los cambios de formato, ausencias o inconsistencias detienen el flujo. El agente no recibe herramientas para publicar, ejecutar código ni modificar fuentes.

Un único agente no satisface la arquitectura completa de consenso de LEIP. Los resultados válidos quedan como **`candidate_for_review`**, nunca como datos aprobados automáticamente; los fallos quedan **`held`**. Comparar las celdas acredita correspondencia con esta tabla, no una auditoría económica independiente.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Las pruebas cubren errores de valores y períodos, duplicados, tablas ambiguas, faltantes, orígenes no admitidos y preservación del historial. La persistencia se prueba con mongomock; una prueba con MongoDB real se documenta por separado en `docs/verification.md`.

## Decisiones y próximos pasos

Ver [arquitectura y decisiones](docs/architecture.md). Para la tutoría: explicar qué hace cada componente, justificar MongoDB y LangChain, mostrar el JSON y luego implementar extractores B/C independientes y un validador de consenso antes de habilitar publicación.

Referencias: [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents), [salida estructurada](https://docs.langchain.com/oss/python/langchain/structured-output), [OpenAI quickstart](https://developers.openai.com/api/docs/quickstart), [fuente BCU](https://www.bcu.gub.uy/Politica-Economica-y-Mercados/Expectativas%20para%20la%20inflacin%20y%20la%20economa/Monitor_trimestral_set26.html).
