# Entradas generadas para escenarios

`scripts/run_scenarios.py` crea una carpeta nueva con UUID por batería. Contiene
recortes/transformaciones del archivo público y fallos de entrada controlados.
Se regenera desde el código y la imagen identificada por SHA-256; no se copia P1–P5.
Las capturas y observaciones seleccionadas viajan en `evidencias/ampliacion/ejecuciones/`.
Los directorios generados se excluyen de Git para no multiplicar imágenes correlacionadas
de calibración que no son necesarias para evaluar la cadena conservada.
