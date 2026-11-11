"""Contrato de métricas adicionales: una familia de percentiles, sin duplicar G1–G7."""

ROWS = [
 ("M01","Distribución de latencia", "percentile(inference_ms,[50,95],linear)","ms","inference_ms en éxitos","null sin inferencias temporizadas"),
 ("M02","Tasa de errores técnicos","errores(source/decode/inference)/intentos","proporción","status por evento","null sin intentos"),
 ("M03","Descartes por muestreo","sum(discarded_frames)","frames","contadores de lectura video por evento","null sin instrumentación de lectura; 0 observado es válido"),
 ("M04","FPS de lectura","sum(read_frames)/sum(attempt_elapsed_s)","frames/s","lecturas reales incluidas las no inferidas","null sin lectura o duración; elegible como extra de etapa con video"),
 ("M05","Fallos de lectura","count(status=source_error)","intentos","status de fuente","0 si no se registraron fallos; población e IDs conservados"),
 ("M06","CPU del productor","100*sum(cpu_seconds_delta)/sum(attempt_elapsed_s)","% de un núcleo","psutil cpu_times; se excluye tiempo/CPU pausado","null sin instrumentación; puede superar 100 con varios núcleos"),
 ("M07","Pico RSS muestreado","max(rss_bytes)/1048576","MiB","RSS observado, no pico continuo","null sin muestras; mismo instrumento de G3, no se reclama bono independiente por parametrización"),
 ("M08","Distribución por clase","count(detecciones finales) agrupado por class_name","detecciones","clase por detección después de NMS","mapa vacío sin detecciones"),
 ("M09","Histograma de confianza","histogram(scores,edges=0,.1,...,1)","detecciones/bin","confidence original por detección final","null sin scores; ceros de bins observados no son puntos inventados"),
 ("M10","Frames sin detecciones","count(no_detections)/frames exitosos","proporción","status y detecciones por frame","null sin éxitos; no equivale a baja confianza"),
 ("M11","Detecciones por imagen","count(detecciones finales)/frames exitosos","detecciones/frame","lista de detecciones, incluido vacío","null sin éxitos"),
 ("M12","Proporción de duda","count(lower<=score<upper)/detecciones finales","proporción","score y zona/config originales","null sin detecciones"),
 ("M13","Entradas inválidas","count(decode_error)/intentos con bytes recibidos","proporción","decode_error; excluye source_error sin bytes","null sin entradas recibidas"),
 ("M14","Cobertura de imágenes","capturas existentes/frames decodificados","proporción","image_ref en ok/no_detections/inference_error; existencia y ruta permitida","null sin frames decodificados; distinta de integridad/metadatos G5"),
 ("M15","Actividad por fuente y ejecución","count(eventos) por(source_id,run_id)","eventos","identificadores persistidos","mapa vacío sin observaciones; no se multiplican bonos por segmentación"),
 ("M16","Alertas por tiempo observado","60*count(alertas creadas)/sum(attempt_elapsed_s)","alertas/min","timestamp de creación; todas las alertas aunque se resolvieran después","null sin duración de intentos; no equivale a alertas abiertas G7"),
 ("M17","Tiempo medio de reconocimiento","mean(acknowledge.timestamp-alert.timestamp)","s","historial de cambios de alerta","null sin reconocimientos antes del corte"),
 ("M18","Tiempo medio de resolución de alerta","mean(resolve.timestamp-alert.timestamp)","s","historial de cambios; no se afirma recuperación del servicio","null sin resoluciones antes del corte"),
 ("M19","Alertas repetidas","count(misma ejecución/regla con separación <=10 s)","alertas","timestamps originales ordenados por run/regla","0 si no se observan repeticiones; no elimina alertas válidas por frame"),
 ("M20","Distancia KS de scores frente a referencia","max_s |CDF_referencia(s)-CDF_ventana(s)|","D en [0,1]","scores finales, event_ids y ventanas persistidas de la misma configuración/modelo","null con referencia/ventana insuficiente; referencia no se puntúa como muestra nueva; sin p-value ni conclusión de drift"),
]

CATALOG = {identity:{"id":identity,"name":name,"definition":name,"formula":formula,"unit":unit,
           "primary_observations":primary,"missing":missing,
           "population_window":"Eventos/alertas filtrados, hasta cutoff; ejecuciones identificadas por run_id/config_sha256",
           "instrumentation":"Productor y SQLite; ver eventos, alertas e historial por sus IDs",
           "verification":"python scripts/verify_extras.py <paquete>; tests/test_extended.py y test_extra_metrics.py",
           "bonus_requested":identity!="M07"} for identity,name,formula,unit,primary,missing in ROWS}
