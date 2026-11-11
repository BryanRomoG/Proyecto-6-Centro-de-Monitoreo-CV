# Resultado de verificación local

Python 3.12.10 / Windows / Pytest 8.3.5. **39 pruebas pasaron, cero fallaron y cero
se omitieron**, en la ejecución final registrada en [pytest.xml](pytest.xml).
El entorno emitió una advertencia de deprecación del alias BlockingPortal de AnyIO
usado por Starlette; no produjo fallos. `python -m pip check` informó
`No broken requirements found`.

Incluye: límites de zonas, validación de configuración/overrides, mínimo de muestras,
referencia/continuidad, parser MJPEG fragmentado/acotado, secuencia y corrupción,
pre/posprocesamiento y scores, verificación de modelo/descarga y escritura temporal,
G1–G7 con valores conocidos y datos ausentes, trazabilidad de imágenes, persistencia
tras reapertura, rollback, HTML/detalles/errores del portal, C1/C2 reales y fallos
inyectados de runtime/fuente. Los dobles de pruebas llevan `synthetic=true`.

Las pruebas reales necesitan `download_model.py` y `prepare_demo.py` antes de pytest.
Los resultados del navegador y el recálculo de ejecuciones completas se conservan
por separado en el [índice](../indice.md). Las salidas de escenarios se produjeron
con el modelo oficial, no con los dobles que prueban manejo de fallos.

Hubo un error de sintaxis en un decorador durante la primera recolección de tests;
se corrigió antes de la suite final. El resultado vigente acredita la versión
identificada por los hashes de código de las ejecuciones seleccionadas.
