# Verificación · 9 de octubre de 2026

## Comprobado en esta computadora

- Instalación en un entorno virtual Python 3.12; dependencias fijadas en `requirements.lock.txt`.
- `pytest -q`: **10 pruebas aprobadas**, incluyendo construcción del grafo LangChain sin llamada a OpenAI y persistencia con mongomock.
- `python -m leip.cli --demo --no-db`: descarga HTTPS real del monitor BCU de setiembre de 2026, captura del HTML, lectura de tabla, controles y JSON correctos.
- Resultados: mediana a 12 meses **4,60 %**; mediana a 24 meses **4,55 %**. Períodos: 2026-09 a 2027-08 y 2026-09 a 2028-08, respectivamente.
- SHA-256 de la captura de prueba: `5f22ea04cd99be89c7691912c84143a812a46b5f390142e3d13aa5c37660e767`.
- Verificación TLS habilitada; se usa el almacén de confianza del sistema con `truststore`.

## Pendiente de comprobar

- Llamada real al modelo: no se encontró `OPENAI_API_KEY` configurada. La construcción del agente está comprobada; la respuesta real y su costo requieren una clave y acceso al modelo seleccionado.
- MongoDB real: Docker estaba instalado pero su motor no estaba disponible. El almacenamiento se verificó con mongomock. Ejecutar Docker Desktop, `docker compose up -d` y `leip --demo` para verificar el servidor real.
- Consenso triple, investigación y publicación automática: fuera del alcance de este prototipo.

No confundir la demo determinística con una extracción hecha por el modelo. Los datos obtenidos siguen siendo candidatos para revisión.
