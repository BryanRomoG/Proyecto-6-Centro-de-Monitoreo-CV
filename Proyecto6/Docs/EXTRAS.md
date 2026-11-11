# Inventario de adicionales · entrega individual

Este inventario describe implementación y comprobación técnica local, no una
calificación docente. **Puntos confirmados: pendientes de evaluación en todas las
filas** (no se presupone cero otorgado ni el potencial como obtenido). Los niveles
potenciales no se acumulan entre sí: F 5/10/15, M 3/5/8, S 5/8/10. No se calcula una
nota total. El nivel propuesto es una aspiración conservadora revisable por el docente.

La base G1–G7 está designada en [METRICAS](../METRICAS.md); R1–R7 y C1/C2 no se
reclaman como adicionales. El [índice de evidencias](../evidencias/ampliacion/indice.md)
identifica el lote final, recorridos HTTP, capturas, recálculos y pruebas.

## Funcionalidades F

Todas están implementadas y verificadas por API/pruebas; las pantallas se recorrieron
en navegador. El mecanismo nativo de descarga de la herramienta integrada quedó sin
confirmar; F5/F6 conservan verificación HTTP y de archivos, con esa limitación explícita.

| ID | Aportación distinta | Potencial | Evidencia y reproducción | Pruebas / alcance |
| --- | --- | ---: | --- | --- |
| F1 | Dashboard dinámico: ejecución/fuente/modelo, contadores, tiempos, RAM, confianza, última actividad y estados. Amplía las consultas mínimas. | 10 | Abrir `/`, iniciar fuente y observar polling; `portal/F1-edge-dashboard.png`, `funciones/*/dashboard.json`. | Conteos contra eventos y datos sin ejecución; `test_extended.py`, `verify_features.py`. |
| F2 | Reproducción anotada por ID del evento, posición y controles que congelan productor/imagen juntos. | 15 | `/playback`: iniciar, pausar, continuar, detener; `portal/F2-edge-reproduccion.png`, controles y frames persistidos. | Video real, pausa sin evento nuevo, cabecera X-Event-ID, caja/score del mismo frame; pruebas unitarias y reales. |
| F3 | Nueve gráficas históricas, selección por período/run y series separadas. | 10 | `/history`; `portal/F3-edge-escritorio.png`, `funciones/*/history.json`. | Totales de puntos/clases/intervalos contra observaciones; sin interpolación ni series inventadas. |
| F4 | Filtros combinados, búsqueda, ordenamiento y páginas sobre eventos/alertas. | 10 | `/events`, `/alerts`; `portal/F4-filtros.png`. | Clase/zona/score sobre la misma detección, sin resultados, límites inválidos y paginación; `test_extended.py`. |
| F5 | Galería con derivados anotados, enlaces a evento/alertas, selección y ZIP seguro. No es la mera captura obligatoria. | 10 | `/gallery`; `portal/F5-galeria.png`, verificación de SHA de PNG descargados. | Rutas fuera del almacén bloqueadas, IDs válidos, límites de lote/tamaño; descarga HTTP verificada. |
| F6 | Exportaciones filtradas CSV/JSON de eventos, alertas, métricas, ventanas y runs; incluye extras/unidades. | 10 | Enlaces Exportar en cada pantalla; CSV/JSON guardados en `funciones/`. | Filas contra consulta original, Unicode y fórmulas neutralizadas; `test_extended.py`, `verify_features.py`. |
| F7 | Ciclo abierta→reconocida→resuelta y comentarios append-only, fechas y versiones. Amplía alertas obligatorias. | 15 | Abrir alerta, reconocer, comentar y resolver; `portal/F7-resuelta.png`, historial exportado. | Transiciones inválidas, request_id repetido, dos revisores concurrentes, evento/score inmutables. |
| F8 | Registro persistido de fuentes locales, identidad, validación y consulta de historial; no se vuelve a contar el control de F2. | 10 | `/sources`, registrar ruta relativa permitida y seleccionar en reproducción. | Faltantes, corrupción, duplicados, escapes/symlinks resueltos y muestreo; `test_extended.py`. |

Reproducción común en PowerShell: iniciar según [README](../README.md), preparar
medios, ejecutar `python scripts/verify_features.py --run-id <ID_REAL>`. Las rutas
de evidencia de esta tabla son relativas a `evidencias/ampliacion/`. Las pruebas están
en [tests](../tests/); los mecanismos unitarios con datos prefijados no prueban inferencia.

## Métricas M

El [contrato ejecutable](../src/monitor_cv/metric_specs.py) registra los diez campos
solicitados: identidad, definición, fórmula, unidad, población/ventana, ausencia,
instrumento, observaciones primarias, valor exportado y recálculo. El [manual de
métricas](../METRICAS.md) explica las diferencias y límites. `extras.json` contiene el
contrato, valores, IDs, denominadores y corte exacto, no solo una captura visual.

Estado de las siguientes filas: **implementada y verificada** con resultados reales
del lote final y pruebas aritméticas, salvo M07 que es informativa sin solicitud de
bono. M17/M18 tienen observaciones reales en el paquete HTTP del run revisado por
navegador; las ejecuciones sin gestión de alertas muestran `null`, correctamente.

Resultados decisivos del cierre: S4 registra distancias KS `null, null, 0.8, 0.8, 0.0`
(construcción de referencia, cambio, recuperación). El paquete HTTP
`http-e875c88699ad42e7a533beaa51731017` conserva un reconocimiento real de
108.410487 s y una resolución de 167.551718 s, medidos desde creación, con sus
timestamps/IDs. Son tiempos de revisión de una alerta de demostración, no SLA.

| ID | Descripción / diferencia | Potencial | Observación decisiva y recálculo |
| --- | --- | ---: | --- |
| M01 | Distribución p50/p95 de inferencia; una familia, diferente de media G1. | 5 | Tiempos por evento C1/C2 y percentil lineal. |
| M02 | Errores técnicos / intentos, no error predictivo. | 5 | S1/S5/S7: status y denominador. |
| M03 | Frames leídos descartados por muestreo. | 3 | Video: read_frames/discarded_frames y frame_index. |
| M04 | FPS de lectura, etapa separada de procesamiento G2. | 5 | Video: todos los frames leídos frente a inferidos. |
| M05 | Fallos de lectura de fuente, no todos los errores M02. | 3 | S1: source_error. |
| M06 | CPU del productor por tiempo observado; distinto de RAM G3. | 5 | CPU acumulada/delta y duración monotónica, pausas excluidas. |
| M07 | Máximo RSS muestreado. Mismo instrumento G3, sin bono independiente solicitado. | 0 | RSS real; se muestra y recalcula, no suma como extra distinto. |
| M08 | Conteos por clase; no accuracy. | 5 | Detecciones finales y class_name C1/C2. |
| M09 | Histograma de scores, no proporción baja G4. | 5 | Scores originales, bordes fijos y bins. |
| M10 | Frames sin detecciones / éxitos. | 5 | S2: ONNX ejecutado y lista vacía. |
| M11 | Detecciones por frame exitoso. | 5 | C1/S2: cuenta incluyendo frames vacíos. |
| M12 | Zona de duda / detecciones finales, distinta de baja G4. | 5 | Umbrales originales y zonas de cada evento. |
| M13 | Entradas inválidas / intentos con bytes. | 5 | S5: decode_error; fuente sin bytes no entra. |
| M14 | Capturas existentes / frames decodificados, distinta de integridad integral G5. | 5 | PNG por ID e intento decodificado, incluido inference_error. |
| M15 | Actividad por fuente/run; una sola métrica segmentada. | 3 | IDs y número de eventos persistidos. |
| M16 | Alertas creadas por minuto observado; no stock abierto G7. | 5 | Creación y duración de intentos. |
| M17 | Tiempo medio de reconocimiento de alerta. | 5 | Historial de acción real, fecha de creación y corte. |
| M18 | Tiempo medio de resolución de alerta, no recuperación del servicio. | 5 | Resolución real por navegador y recálculo posterior. |
| M19 | Repeticiones de misma regla/run separadas <=10s. | 5 | Alertas ordenadas, IDs y timestamps; sin deduplicar evidencia. |
| M20 | Distancia KS empírica de scores respecto a referencia fija. | 8 | S4: ventanas y scores originales, comparación y recuperación; no p-value/drift. |

Comando por paquete: `python scripts/verify_extras.py <CARPETA>`. La selección de
paquetes/resultados está en [verificacion-final.json](../evidencias/ampliacion/verificacion-final.json).
Pruebas de recálculo y aritmética: `test_extended.py`, `test_extra_metrics.py`,
`test_distribution.py`, `test_additional_scenarios.py`. G1–G7 además tienen fórmulas
independientes en `scripts/verify_metrics.py`. No se solicitan bonos por renombrar
throughput/frescura de base ni uno por cada percentil/clase/ventana.

## Escenarios S

Estado: **ejecutados y verificados localmente**, con expectativa/observación exportada.
Cada paquete contiene configuración efectiva, identidad de modelo/código, eventos,
capturas disponibles, alertas, ventanas y métricas. El lote final enlazado en el índice
conserva también la calibración exploratoria y hashes de sus entradas. Los niveles
potenciales siguen sujetos al alcance que el docente considere demostrado.

| ID | Condición distinta y aceptación | Potencial | Evidencia / pruebas |
| --- | --- | ---: | --- |
| S1 | Interrupción controlada de archivo entre lecturas; source_error y siguiente imagen real recuperada. | 8 | `S1/result.json`, eventos antes/fallo/después; no se simula pérdida de una cámara. |
| S2 | Recorte fotográfico real sin detecciones; estado no_detections, sin scores ni alerta baja. | 5 | `S2/`, recorte y salida ONNX vacía. |
| S3 | Una muestra no alcanza ventana/mínimo: insufficient_evidence, sin declarar normalidad. | 5 | `S3/`, eventos y ausencia de ventanas completas. |
| S4 | Referencia real, dos ventanas consecutivas de cambio, alerta sostenida y vuelta a política. | 8 | `S4/`, calibration.json y cinco ventanas; no es repetición aislada de C2. |
| S5 | PNG corrupto: decode_error, diagnóstico y continuidad en siguiente frame real. | 8 | `S5/`, entrada inválida y eventos antes/después; distinto de fuente sin archivo S1. |
| S6 | Misma escena/modelo y configuración versionada: scores iguales, hashes/run distintos, sin mezclar series. | 8 | `S6-v1/`, `S6-v2/`, resumen compuesto S6. |
| S7 | Excepción inyectada del adaptador de inferencia, evento diagnosticado y recuperación real. | 8 | `S7/`, fault_simulated=true y inference_executed=false en fallo; ONNX real antes/después. |

Reproducción: `python scripts/run_scenarios.py` desde Proyecto6 crea un lote nuevo sin
sobrescribir ninguno. `python -m pytest tests/test_additional_scenarios.py -q` repite
la aceptación con modelo real. Una excepción técnica inyectada prueba el mecanismo
de recuperación; no se presenta como fallo espontáneo de ONNX ni predicción real.
Los recortes/repeticiones de una misma escena son observaciones correlacionadas y
no demuestran cambio de calidad ni una población representativa.

## Pendientes de evaluación y límites

Revisar nombre académico/matrícula, nivel de cada elemento y aceptación docente.
No hay commit autorizado para fijar una entrega remota; los manifiestos locales
permiten comparar el código exacto. No se probó carga prolongada ni notificación
externa; el alcance es una aplicación local con polling, SQLite y archivos. No hay
comprobación del evento de descarga nativo del navegador integrado, aunque los
bytes exportados/ZIP y los controles de selección sí están verificados.


## Edición 0.3 · adquisición pública y galería integrada

F9 · Adquisición selectiva pública con autor/licencia por imagen, presupuesto,
reanudación, SHA, pHash/dHash, deduplicación y registro automático de ocho colecciones.
**Implementada y verificada; potencial aspirado F=10, confirmado pendiente docente.**
Difiere del lector/selector F8 y de la documentación base: adquiere, valida y conserva
la procedencia de 80 escenas distintas. Evidencia en [DATASETS](DATASETS.md),
[manifiestos](../data/media/datasets/manifest.json) y [índice](../evidencias/datasets/indice.md).
Reproducción: download_demo_dataset.py; prueba test_datasets_gallery.py y lote real
run_dataset_demo.py. No se solicita un bono por cada categoría o foto.

F4/F5/F6/F8 se amplían con SQL, filtros de colección, páginas reales, thumbnails,
errores técnicos separados, control de solicitudes, atribución ZIP e historial por
fuente. No se reclaman otra vez como funciones equivalentes. Edge sí confirmó la
descarga nativa del ZIP en esta edición; la limitación del navegador integrado en
la edición anterior queda conservada en sus reportes. Pruebas: 87 de la suite y una
E2E con Edge/YOLOX sin mocks. Los conteos por dataset no se multiplican como métricas
ni las repeticiones de los 80 originales como escenarios independientes. No se
modifican puntos confirmados, no se calcula nota ni se garantiza una calificación.
