# Matriz R1–R7 · estado local

Revisión de implementación, no calificación. Se leyeron íntegros los dos documentos
del profesor. Implementado = código existente; verificado = prueba/ejecución observada;
pendiente = límite explícito. No aplicable se usa solo con justificación real.
Los siete grupos G1–G7 aplican y tienen indicadores distintos; ninguno se excluye.

| Subcriterio | Implementado | Verificado | Pendiente / límite |
| --- | --- | --- | --- |
| R1.1 · fuente progresiva | Secuencia ordenada y MJPEG con muestreo configurable | 10 frames C1 y 10 C2 a 2 Hz nominales; parser fragmentado y errores | ESP32-CAM física no entregó JPEG fresco; ver camara.json. No invalida la fuente alternativa. |
| R1.2 · inferencia real | YOLOX-Nano ONNX CPU, resultados por imagen | Pesos descargados/verificados; tests reales y events.jsonl, no scores inyectados | Probar dominio de cámara cuando esté disponible. |
| R1.3 · identidad/entorno | SHA, descriptor, clases, preprocesamiento, runtime y config | Modelo y forma comprobados al cargar, entorno en run.json | Ninguno para el modelo local probado. |
| R2 · G1 | Tiempo medio exclusivo de session.run | Recálculo C1/C2 y caso aritmético conocido | Sin benchmark de carga prolongada. |
| R2 · G2 | FPS con intervalos monotónicos de intentos | Recálculo C1/C2 y caso conocido | No mide FPS físico de cámara. |
| R2 · G3 | RSS de proceso en MiB | Mediciones reales Psutil y recálculo | No mide picos entre muestras. |
| R2 · G4 | Proporción baja por detección final | Scores originales y denominador; casos vacíos | No representa tasa de error predictivo. |
| R2 · G5 | Campos y referencias verificadas por SHA | Cobertura exportada 1; tests de imagen ausente/corrupta y path escape | Revisar disco a largo plazo. |
| R2 · G6 | Tiempo desde reporte real de imagen | Recálculo con corte fijo; error de fuente no renueva reporte | Reloj local; no timestamp del sensor. |
| R2 · G7 | Alertas activas por ejecución | IDs persistidos y conteo recalculado | Sin ciclo de resolución; todas permanecen abiertas. |
| R3.1 · umbrales/justificación | Inferior .60, superior .80, piso .10; validación y referencia | Pruebas de límites y referencia_confianza.json/md | Ampliar referencia de dominio real; no hay calibración formal ni se exige. |
| R3.2 · zonas/bajas/vacíos | Tres zonas y estados separados; candidatas pre-NMS | Observadas las tres zonas en datos reales; sin confianza cero artificial | Ninguno para casos probados. |
| R3.3 · referencia/ventanas/regla | Referencia fija por run, ventanas no solapadas, mínimo y continuidad | Referencia persistida en C1/C2; secuencia sostenida y evidencia insuficiente en unitarios | Cambio sostenido real es un escenario opcional no demostrado. |
| R4.1 · evento completo | UUID, fechas, fuente, modelo, config, resultados y estado | Exportación real y lectura desde SQLite | Ninguno para campos probados. |
| R4.2 · persistencia/portal | SQLite transaccional y HTML de consulta/detalle | Reapertura, rollback y consultas HTTP/navegador | Carga prolongada no probada. |
| R4.3 · imágenes vinculadas | PNG sin pérdida por imagen decodificada, sin TTL | SHA y carga real en navegador | Errores de fuente/decodificación no tienen captura válida; está documentado. |
| R5.1 · reglas explícitas | Baja por frame y aumento sostenido por ventanas | Configuración, límites, vacíos y fallos en tests | Ninguno para reglas base implementadas. |
| R5.2 · alertas reales vinculadas | ID de regla, config y eventos/ventanas | 10 alertas bajas en cada escenario seleccionado | No se atribuye a confianza un diagnóstico de drift. |
| R5.3 · persistencia/portal | Motivo, momento, severidad y acción | HTML, navegación y screenshots de la cadena alerta→evento | Sin envíos externos ni reconocimiento; no se requieren. |
| R6.1 · C1 | Escenario reproducible y paquete de observaciones | 10/10 frames exitosos, métricas y portal observado | Alcance: una escena pública y variantes correlacionadas. |
| R6.2 · C2 | Transformaciones de píxeles con política fijada | 10/10 frames con salidas bajas reales, imagen/evento/alerta y navegador | No implica calidad predictiva ni prueba física. |
| R7.1 · instalación/ejecución | Dependencias fijadas, lock Windows, .env.example y comandos | Venv 3.12 creado, instalación y pip check exitosos; scripts ejecutados | CI remoto y clon nuevo en otra máquina pendientes. |
| R7.2 · evidencia/Git | Índice, observaciones, scripts de recálculo y hashes | C1/C2 seleccionados conservan identidad de código probada | Sin commit inicial: falta asociar evidencia a revisión Git autorizada. |
| R7.3 · autoría/reuso | PROCEDENCIA.md y referencias exactas | Detector y lector desacoplados; antecedentes intactos por hash | Confirmar nombre académico completo y matrícula; revisión personal del estudiante. |

Evidencia: [índice](indice.md), [pruebas](pruebas/pytest.xml),
[métricas](metricas/), [portal](portal/recorrido.md), [auditoría](auditoria_repositorio.json).
No se asignan puntos ni se declara una nota final; R7 conserva pendientes explícitos.
El esquema de evaluación distingue cinco comprobaciones M1–M5 por métrica; el
[inventario](../METRICAS.md) documenta definición, adquisición, cálculo, trazabilidad
y procedimiento de verificación sin autoasignarse sus valores.
