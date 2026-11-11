# Recorrido observado del portal

Servidor local en `http://127.0.0.1:8006`, iniciado con el comando del README.
Se consultaron páginas HTML y se recorrieron detalles de eventos y alertas en el
navegador integrado. Se verificó que la imagen tuviera `complete=true` y anchura
natural positiva, además de la respuesta HTTP y el SHA del PNG. Se observó regla,
severidad, acción sugerida y enlace al evento correcto.

| Escenario | Evento e imagen observados | Alerta observada |
| --- | --- | --- |
| C1 | [Captura de evento](C1-evento-verificado.png): evt-8dc816d8d72448d2a7ad99bdd77ade9f | [Captura de alerta](C1-alerta-verificada.png): alert-46f7efdb4e2244e784d5711146f8dc08 |
| C2 | [Captura de evento](C2-evento-verificado.png): evt-0a38174a0c704752bdeb952ca9111398 | [Captura de alerta](C2-alerta-verificada.png): alert-578c4011dfd345ed930c99dcbd57887f |

[Registro estructurado de navegador](browser-verification.json).
Las subcarpetas con el run_id contienen HTML efectivamente servido y su verificación
HTTP. Esas copias incluyen una base al servidor local para CSS/enlaces; las capturas
PNG son consultables sin servidor. Para regenerar, ejecutar C1/C2 y `verify_portal.py`
según el README; los nuevos UUID deben usarse en el recorrido.

Los estados inexistentes/vacíos se verificaron por HTTP y en tests; la captura visual
del dashboard sin datos recientes no se presenta como medición de un sistema activo.
Ninguna captura visual aislada acredita la procedencia de scores: se conserva también
la cadena de inferencias y los hashes del modelo y código.
