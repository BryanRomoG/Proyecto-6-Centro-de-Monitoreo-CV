# Inventario base G1–G7

Los siete grupos aplican: hay inferencia, entrada visual, proceso local, detecciones,
persistencia, una fuente identificada y alertas. No se excluye ningún grupo. No se
reclaman métricas de calidad predictiva. Unidad de análisis explícita: un intento procesa
un frame; una detección es una salida posterior a NMS, piso 0.10 y tope 100.

Todas las observaciones se guardan en `events.jsonl`/SQLite, y cada resultado en
`metrics.json` o tabla `metrics`. Se segmenta por `run_id` (modelo/configuración fija).
La ventana móvil selecciona eventos con timestamp de finalización UTC en
`[corte-60 s,corte]`, configurable. Cada snapshot conserva corte, IDs y denominadores.
Las muestras de RAM y tiempos pertenecen al proceso productor, no al servidor que
consulta posteriormente. No se suman tiempos de distintas ejecuciones.

| Grupo / métrica base | Unidad | Fórmula y población | Observación primaria / adquisición | Ausencia y exclusiones |
| --- | --- | --- | --- | --- |
| G1 · Tiempo medio de inferencia | ms | `sum(inference_ms)/N` en frames técnicamente exitosos con tiempo medido dentro de la ventana | `perf_counter` justo antes/después de `session.run`; `inference_ms` por evento | `null` si N=0. Incluye frames sin detecciones; excluye captura, pre/post, fallos ONNX y errores de fuente. |
| G2 · FPS de procesamiento | frames/s | `frames exitosos / sum(attempt_elapsed_s)` para todos los intentos seleccionados | Intervalo monotónico entre finalizaciones; primero desde inicio del loop. Incluye espera de fuente, muestreo, trabajo y persistencia anterior. | `null` si no hay intentos o denominador no positivo; 0 si hay tiempo observado y ningún éxito. No confundir con velocidad nominal de la cámara. |
| G3 · RSS medio del productor | MiB | `sum(rss_bytes)/N/1048576` en intentos con medición | `psutil.Process().memory_info().rss` al concluir cada intento | `null` sin muestras; no mide RAM del equipo ni pico entre muestras. |
| G4 · Proporción de baja confianza | proporción [0,1] | `detecciones finales s<inferior / detecciones finales puntuadas` en frames exitosos de la ventana | Scores originales, clase/caja, zona, piso/NMS y umbrales del evento | `null` si no hay detecciones; frames vacíos no aportan ceros. Denominador de detecciones, no de frames ni anclas pre-NMS. |
| G5 · Cobertura de trazabilidad | proporción [0,1] | `eventos con campos y referencias íntegros / eventos de la ventana` | IDs, fuente/modelo SHA, config y hash, estado; imagen obligatoria en éxitos y SHA-256 de archivo si está vinculada | `null` si no hay eventos. Errores con identidad/estado pueden estar completos sin imagen. Archivo ausente/corrupto o ruta fuera del almacén no cumple. |
| G6 · Tiempo desde el último reporte de imagen | s | `max(0,corte-max(captured_at))` en toda la ejecución hasta el corte | Recepción local UTC del frame; `last_report_event_id` | `null` si nunca se recibió imagen. Un error de red sin frame no renueva frescura. Sigue envejeciendo fuera de la ventana de 60 s. Reloj local único; no pretende medir timestamp del sensor. |
| G7 · Alertas abiertas | alertas | `count(estado_al_corte in {active,acknowledged})` de toda la ejecución | Creación e historial persistidos; IDs `active_alert_ids` | 0 si no hay alertas abiertas; no implica estado saludable. Reconocer mantiene abierta; resolver la excluye desde ese cambio. Sin expiración automática. |

G2 es un cociente sobre intervalos completos asociados a las finalizaciones elegidas;
un intervalo puede iniciar antes del borde izquierdo de la ventana. No se divide
artificialmente entre 60 s si solo se observaron pocos segundos. La duración final no
incluye el tiempo posterior al último intento. Los timestamps UTC fijan la selección;
las duraciones se miden con reloj monotónico para evitar restas de pared en G1/G2.

## Adquisición, trazabilidad y recálculo (M1–M5)

1. Ejecutar `scripts/run_demo.py --scenario C1` y C2. Se exportan observaciones,
   snapshots, hashes del código, modelo y configuración efectiva.
2. Cada snapshot contiene `event_ids`, `last_report_event_id`, `active_alert_ids` y
   denominadores en `primary`. Revisar los eventos y alertas de esos IDs.
3. Ejecutar `scripts/verify_metrics.py <carpeta-run>` desde Proyecto6. Usa el instante
   guardado; volver a consultar G6 con la hora actual produciría legítimamente otro valor.
4. El script reconstruye los siete valores, verifica archivos y hashes y compara con
   tolerancia de coma flotante 1e-9. También calcula fórmulas directamente desde datos.
5. Los tests verifican a mano los siete grupos con un caso conocido de 20 ms,
   2 FPS, 100 MiB, razón baja 1, cobertura 1, frescura 2 s y una alerta. El caso
   sintético comprueba aritmética, no procedencia del modelo. Los tests reales ejecutan
   YOLOX y recalculan las exportaciones de C1/C2.

Las capturas conservadas son parte de la verificación de G5; copiar solo JSON sin
las imágenes produce cobertura inferior. El agregado no puede demostrar por sí solo
que una puntuación salió del modelo; esa procedencia se acredita con la cadena real.
No se asignan valores M1–M5 ni puntos R2 automáticamente desde este inventario.

## Contrato ampliado M01–M20

Los IDs M01–M20 de esta ampliación son indicadores de software; no son los niveles
M1–M5 de evaluación de la rúbrica. El contrato completo, consumido por los endpoints
y exportaciones, está en [metric_specs.py](src/monitor_cv/metric_specs.py). Cada fila
incluye definición, fórmula, unidad, población/ventana, adquisición, observaciones
primarias, ausencia de datos y recálculo. Los resultados concretos se conservan en
`extras.json` de cada paquete enlazado en el [índice actual](evidencias/ampliacion/indice.md).

| ID | Indicador | Diferencia respecto a la base |
| --- | --- | --- |
| M01 | p50 y p95 de latencia | Una sola distribución, una sola familia; G1 es media. |
| M02 | Proporción de errores técnicos | Fuente, decodificación e inferencia / intentos. |
| M03 | Frames descartados | Contabilidad de lectura y muestreo, no eventos inferidos. |
| M04 | FPS de lectura | Frames leídos, incluidos descartados; G2 cuenta éxitos procesados. |
| M05 | Fallos de fuente | Conteo de source_error; distinto de ausencia de detecciones. |
| M06 | CPU del productor | CPU acumulada / tiempo observado; porcentaje de un núcleo, puede superar 100. |
| M07 | Máximo RSS muestreado | Informativo; no se reclama bono separado de la instrumentación de G3. |
| M08 | Detecciones por clase | Distribución de salidas finales, sin etiquetas verdaderas. |
| M09 | Histograma de confianza | Distribución completa con bins fijos; G4 solo cuenta zona baja. |
| M10 | Proporción de frames vacíos | Denominador de frames exitosos, no detecciones. |
| M11 | Detecciones por imagen | Intensidad de salidas posteriores a NMS. |
| M12 | Proporción de duda | Zona intermedia, distinta de G4. |
| M13 | Entradas recibidas inválidas | decode_error / intentos con bytes; excluye fallo sin entrada. |
| M14 | Cobertura de capturas | Captura existente / frames decodificados; G5 además verifica campos y hash. |
| M15 | Actividad por fuente/ejecución | Un solo indicador segmentado; no un bono por cada fuente o run. |
| M16 | Alertas generadas por minuto observado | Creaciones, aun después de resolver; G7 es stock abierto. |
| M17 | Tiempo de reconocimiento | Cambio real de alerta menos creación, al corte. |
| M18 | Tiempo de resolución de alerta | Resolución real menos creación; no mide recuperación del servicio. |
| M19 | Alertas repetidas | Misma regla/run con separación <=10 s; no elimina registros. |
| M20 | Distancia KS a referencia fija | Máxima diferencia entre CDF empíricas de scores; descriptiva. |

No se reclama throughput con otro nombre de G2, ni frescura con otro nombre de G6.
No hay métrica de duplicados rechazados ni tiempo de detección con inicio conocido:
se prueban rechazos y reglas, pero no se inventa un instrumento o inicio de incidente.

M20 utiliza solamente eventos de ventanas completas, con la misma identidad de
modelo/configuración y mínimo de detecciones. Las ventanas que construyen referencia
no se tratan como nueva comparación. Valores ausentes son `null`; sin observaciones
no se fabrican ceros. Las gráficas no interpolan puntos nuevos. La referencia fija
no acredita calidad, independencia estadística ni drift predictivo confirmado.

Los tiempos/CPU pausados se excluyen de G2/M06. G6 sí envejece con el reloj de pared.
Las tasas en intervalos cortos tienen efectos de borde; no se confunden FPS nominales,
de lectura y de procesamiento. Las series se separan por run/configuración; las
exportaciones agregadas que no admiten filtro por clase lo rechazan explícitamente.

El historial de alertas es append-only. Para un corte anterior a una resolución,
G7 y M17/M18 reconstruyen solo cambios anteriores o iguales a ese corte. Las
observaciones originales, scores y snapshots anteriores nunca se reescriben.

Recálculo: `python scripts/verify_extras.py <paquete>` reconstruye valores desde
events/alerts/windows y capturas. `tests/test_extra_metrics.py` comprueba aritmética
con datos unitarios identificados; `tests/test_distribution.py` comprueba distancias
conocidas; `tests/test_additional_scenarios.py` repite escenarios con ONNX real.
El recálculo comparte el agregador de producción; se complementa con fórmulas
independientes de G1–G7 y casos aritméticos conocidos, sin presentarlo como un segundo
instrumento independiente. El [inventario](Docs/EXTRAS.md) separa potencial y evaluación.


## Fotografías públicas y disponibilidad · 0.3

Las colecciones usan collection/source_id/run_id/input_image.image_id. El SHA de
entrada identifica el JPEG adquirido; el SHA de captura identifica el PNG. Las
etiquetas de Open Images no sustituyen las predicciones ni cambian G4/M08/M09/M12.
La galería separa disponibles, técnicos sin captura, pendientes y anomalías. Un error
sin bytes decodificables puede estar completo para G5 por su identidad/diagnóstico;
un éxito con PNG ausente/hash incorrecto falla G5. M14 usa frames decodificados como
denominador, no todos los intentos. No se inventan capturas ni se reclaman estos
conteos como nuevos bonos. Ver [lote y recálculos](evidencias/datasets/indice.md).
Las diferencias de latencia son observaciones, sin causalidad por clase ni accuracy.
