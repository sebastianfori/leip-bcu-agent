# LEIP · Agente BCU

Prototipo para la próxima tutoría: un agente de **LangChain + Gemini** extrae la **mediana de inflación esperada a 12 y 24 meses** de una publicación HTML del Banco Central del Uruguay, verifica la salida contra las celdas capturadas y conserva la ejecución en **MongoDB** y JSON. La inferencia se hace en la nube de Google; no descarga ni ejecuta un modelo en tu PC. OpenAI queda como proveedor opcional.

## Ejecutar en Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
Copy-Item .env.example .env
docker compose up -d
.\.venv\Scripts\leip.exe --demo
```

Para usar el agente real, creá una clave en [Google AI Studio](https://aistudio.google.com/api-keys) de un proyecto marcado **Free tier**, sin activar facturación, y completá en `.env`:

```dotenv
LLM_PROVIDER=gemini
GEMINI_API_KEY=tu_clave
GEMINI_MODEL=gemini-3.7-flash
```

Luego ejecutá:

```powershell
.\.venv\Scripts\leip.exe
```

La cuota gratuita de Gemini depende del modelo, proyecto y límites disponibles. Una suscripción de la app Gemini no determina el nivel de facturación de la API. Usá una clave de un proyecto Free tier para evitar cobros; este programa no puede comprobar ni cambiar la facturación de tu cuenta. Si se agota la cuota, se detiene: no cambia automáticamente a OpenAI ni Azure. Se limita a 2048 tokens de salida por llamada y 8 pasos de grafo, sin reintentos automáticos del proveedor Google. Los límites de tokens no son un tope de gasto monetario para proyectos con facturación activada.

Este proyecto no usa créditos de Azure. Nunca subas `.env` al repositorio. Para volver a OpenAI, elegí `LLM_PROVIDER=openai` y configurá `OPENAI_API_KEY` y `OPENAI_MODEL`; esa API requiere su propia cuota y facturación.

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


Referencias: [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents), [salida estructurada](https://docs.langchain.com/oss/python/langchain/structured-output), [Gemini y LangChain](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai), [cuota gratuita y precios de Gemini](https://ai.google.dev/gemini-api/docs/pricing), [fuente BCU](https://www.bcu.gub.uy/Politica-Economica-y-Mercados/Expectativas%20para%20la%20inflacin%20y%20la%20economa/Monitor_trimestral_set26.html).
