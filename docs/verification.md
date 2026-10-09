# Verificación · 9 de octubre de 2026

## Comprobado en esta computadora

- Instalación en un entorno virtual Python 3.12; dependencias fijadas en `requirements.lock.txt`.
- `pytest -q`: **12 pruebas aprobadas**, incluyendo construcción de los grafos Gemini/OpenAI sin llamadas al proveedor, horizontes permitidos y persistencia con mongomock.
- `python -m leip.cli --demo --no-db`: descarga HTTPS real del monitor BCU de setiembre de 2026, captura del HTML, lectura de tabla, controles y JSON correctos.
- Resultados: mediana a 12 meses **4,60 %**; mediana a 24 meses **4,55 %**. Períodos: 2026-09 a 2027-08 y 2026-09 a 2028-08, respectivamente.
- SHA-256 de la captura de prueba: `5f22ea04cd99be89c7691912c84143a812a46b5f390142e3d13aa5c37660e767`.
- Verificación TLS habilitada; se usa el almacén de confianza del sistema con `truststore`.
- MongoDB real: se inició el servicio con `docker compose up -d`, se ejecutó `leip --demo` y se confirmó por consulta independiente que la ejecución quedó guardada con dos observaciones y estado `candidate_for_review`.
- Agente real Gemini: se ejecutó `python -m leip.cli` con `LLM_PROVIDER=gemini` y `gemini-3.7-flash`; produjo ambas observaciones, pasó la comparación contra las celdas BCU y se guardó en MongoDB. Ejecución: `5ec43fb8-2457-4bd5-996e-266ee76299d4`.
- La inferencia usa Gemini Developer API en la nube. No se ejecuta un modelo local ni se aprovisionan recursos Azure.

## Pendiente de comprobar

- OpenAI sigue siendo una opción configurable, pero no se verificó una extracción exitosa con ese proveedor.
- Consenso triple, investigación y publicación automática: fuera del alcance de este prototipo.

No confundir la demo determinística con una extracción hecha por el modelo. Los datos obtenidos siguen siendo candidatos para revisión.
