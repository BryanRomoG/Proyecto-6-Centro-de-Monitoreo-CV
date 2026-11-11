# Entradas y datos locales

`demo/` contiene una escena pública pequeña y sus variantes reproducibles generadas
por `scripts/prepare_demo.py`, con hashes y transformaciones en su manifest. Se pueden
incluir en Git como entrada seleccionada; no son un dataset de evaluación de calidad.

`runtime/` contiene SQLite y capturas de ejecución, ignorados por Git. Los escenarios
exportan las observaciones necesarias a `../evidencias/escenarios/` sin TTL.
`tmp/` es trabajo temporal excluido. Ningún comando de preparación copia datos de P1–P5.
