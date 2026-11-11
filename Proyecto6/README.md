# Proyecto 6 · Centro de monitoreo de computer vision

Entrega **individual**, ITESO. **Nombre académico completo y matrícula pendientes**.
Versión 0.3.0: inferencia real sobre **secuencias de imágenes y archivos de video**,
sin cámara física ni carrito. El código y los resultados de los proyectos anteriores
se conservan como antecedentes y no son dependencias de ejecución.

El sistema transforma imágenes en detecciones YOLOX-Nano, métricas G1–G7, capturas,
eventos y alertas trazables. Incluye dashboard con polling, reproducción anotada,
nueve gráficas históricas, filtros, galería, exportaciones, gestión de alertas y fuentes.
La confianza alta significa “aceptada por política”, no necesariamente correcta.

La demostración principal incorpora **80 fotografías públicas diferentes de Open
Images**, diez por cada una de ocho colecciones, con autor/licencia individual y
SHA-256. [Dataset, licencias y adquisición](Docs/DATASETS.md),
[reporte de esta ampliación](ENTREGA_DATASETS.md) e
[índice actual](evidencias/datasets/indice.md). El material anterior se conserva para
comparar y reproducir resultados; ya no es la única fuente de demostración.

```powershell
# Desde Proyecto6, después de instalar las dependencias del proyecto:
.\.venv\Scripts\python.exe scripts/download_demo_dataset.py --target-per-category 10 --max-mb 200
.\.venv\Scripts\python.exe scripts/run_dataset_demo.py --sample-hz 4
.\.venv\Scripts\python.exe scripts/audit_gallery.py
```

Al iniciar normalmente el portal se registran las colecciones locales verificadas.
En Fuentes seleccionar una, Iniciar y abrir Reproducción. Después de detener se puede
elegir otra. Cada JPEG se procesa con el detector real. El lote CLI deja resultados
históricos; el procesamiento visible se inicia desde los controles del portal.
La galería usa páginas SQL, miniaturas <=320x240 y hasta cuatro peticiones, con
cancelación/reintento. Separa errores técnicos sin captura de archivos perdidos.

- [Manual de usuario](MANUAL_USUARIO.md), [manual de ejecución](MANUAL_EJECUCION.md), [arquitectura](ARQUITECTURA.md).
- [Métricas base y adicionales](METRICAS.md), [procedencia](PROCEDENCIA.md).
- [Inventario de extras](Docs/EXTRAS.md), [índice actual de evidencias](evidencias/ampliacion/indice.md).
- [Matriz R1–R7 actual](evidencias/ampliacion/cumplimiento.md).
- [Entrega inicial conservada](ENTREGA_INICIAL.md) e [índice histórico](evidencias/indice.md).
  Sus resultados se mantienen como evidencia de la versión anterior, sin modificarlos.

## Instalación reproducible · Windows 11 / PowerShell

Instalar Python **3.12 de 64 bits**. Desde la raíz del repositorio:

```powershell
py -0p
Set-Location .\Proyecto6
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock-windows.txt
.\.venv\Scripts\python.exe -m pip check
if (!(Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe scripts/download_model.py --destino modelo
.\.venv\Scripts\python.exe scripts/prepare_media.py
```

No se necesita activar el entorno ni modificar ExecutionPolicy. El lock corresponde
al árbol probado con Python 3.12.10 en Windows. Las dependencias directas están fijadas
en [requirements.txt](requirements.txt); en Linux con Python 3.12 usar ese archivo,
porque el lock Windows incluye pyreadline3. El CI local del proyecto usa CPU.
No son necesarios PyTorch, GPU, Docker, AWS, servicios de pago ni los entornos de P1–P5.

`prepare_media.py` reutiliza las imágenes públicas pequeñas de la demostración o las
descarga si faltan; verifica el SHA de origen y genera un MP4 de 40 frames a 8 FPS
con códec mp4v. [Manifest de video](data/media/manifest.json) y
[manifest de imágenes](data/demo/manifest.json) identifican entradas y transformaciones.
Es un archivo generado, **no una cámara en vivo**. La disponibilidad de otros códecs
depende de OpenCV/FFmpeg; se prueban AVI/MJPEG y MP4/mp4v.

## Iniciar el portal

Desde Proyecto6:

```powershell
.\.venv\Scripts\python.exe -m uvicorn monitor_cv.main:create_app --factory --app-dir src --host 127.0.0.1 --port 8006
```

Abrir <http://127.0.0.1:8006>. API en <http://127.0.0.1:8006/docs>.
Un solo proceso/worker produce datos. No usar varios workers ni ejecutar otro
productor simultáneamente sobre el mismo SQLite. Si el puerto está ocupado por
una ejecución anterior, detener esa terminal con Ctrl+C. Tras cambiar código Python
o filtros de plantillas, reiniciar el servidor.

En **Fuentes**, registrar:
- Imágenes: nombre, tipo “Secuencia de imágenes”, ruta `data/demo/normal`.
- Video: nombre, tipo “Archivo de video”, ruta `data/media/demo.mp4`.

Elegir fuente, muestreo y repetición; pulsar **Iniciar**. En **Reproducción** se muestran
captura, cajas, clases, confianza, número de frame, posición y progreso.
**Pausar**, **Continuar** y **Detener** actúan sobre la ejecución real.
La pausa mantiene el último resultado y no genera nuevos eventos. Cambiar de fuente
requiere terminar la ejecución actual; las opciones quedan bloqueadas mientras está activa.

Para medios propios, copiarlos en `data/media/` y registrar allí su ruta relativa.
Las raíces permitidas se configuran en YAML; el portal no puede leer el resto del disco.
Se rechazan rutas externas, inexistentes, videos inválidos y duplicados de fuente.
Una secuencia mixta informa las imágenes corruptas al registrarse y las registra como
errores al reproducirse; una carpeta sin ninguna imagen válida no se acepta.

## Configuración

[config/settings.yaml](config/settings.yaml) define muestreo, modelo, umbrales,
referencia, ventanas, reglas, almacén y directorios permitidos. `.env` es local y
no se versiona. Ejemplo para video predeterminado:

```dotenv
MONITOR_SOURCE=video
MONITOR_VIDEO_FILE=data/media/demo.mp4
MONITOR_AUTOSTART=false
```

Para imágenes usar `MONITOR_SOURCE=images` y
`MONITOR_IMAGES_DIR=data/demo/normal`. Las rutas relativas parten de Proyecto6,
independientemente del directorio desde donde se invoque un script.
El adaptador MJPEG se conserva como código legado opcional, pero el portal actual
solo ofrece imágenes y video. No se comprueba la ESP32-CAM ni se exige su acceso.

Cada ejecución conserva configuración efectiva completa y SHA-256, fuente, modelo,
versión de aplicación, entorno e IDs únicos. Una modificación produce una nueva serie;
el historial previo conserva su configuración. Las gráficas de tiempos, confianza y
clases separan ejecuciones y no mezclan modelos/configuraciones como una sola serie.

## Modelo y política

YOLOX-Nano oficial, release Megvii `0.1.1rc0`, COCO 80 clases; no hubo entrenamiento.
[Descriptor](modelo/descriptor.yaml): 3,659,407 bytes y SHA-256
`c789161ed43c8269fcd4e67c67eeeb4e80c622da2eb296a20bc6007bd18a0b7d`.
El descargador verifica tamaño/hash y TLS antes de instalar el archivo.
Si la red institucional usa CA propia, configurar `SSL_CERT_FILE`; no omitir TLS.

Entrada BGR NCHW float32 0–255, letterbox 416×416 arriba/izquierda, relleno 114,
Pillow bilinear; salida cruda [1,3549,85], strides 8/16/32.
Score real = objectness × mejor clase. Piso **0.10**, NMS por clase IoU **0.45**,
tope **100 detecciones**. Se guardan candidatas sobre el piso antes de NMS y detecciones
finales. No se alteran scores. Las cajas se expresan en píxeles xyxy del frame original.

Zonas por detección final: s<0.60 baja; 0.60≤s<0.80 duda; s≥0.80 aceptada por política.
Los frames sin detecciones, entradas inválidas y fallos técnicos tienen estados
separados; no reciben una confianza artificial de cero.
Una detección baja por frame válido genera una alerta de advertencia según el mínimo
configurable. Esa regla funciona aunque todavía falte evidencia para la regla temporal.

Regla temporal: ventanas no solapadas de 5 intentos, mínimo 5 detecciones y sin fallos
técnicos. Las primeras 2 ventanas elegibles forman una referencia fija por ejecución.
Un aumento de al menos 0.20 en proporción baja durante 2 ventanas consecutivas produce
una alerta alta. Una ventana insuficiente rompe continuidad; no declara normalidad.
La referencia, ventanas y eventos se conservan; el cambio de confianza no confirma drift.
[Justificación y observaciones iniciales](evidencias/referencia_confianza.md).

## Métricas y portal

G1 tiempo ONNX medio; G2 FPS de procesamiento; G3 RSS; G4 proporción baja;
G5 trazabilidad con hash de imagen; G6 tiempo desde el último reporte de imagen;
G7 alertas **sin resolver**, abiertas o reconocidas, al instante consultado.
El historial de cambios permite recalcular G7 en un corte anterior a una resolución.

Se instrumentaron 20 indicadores complementarios M01–M20: percentiles, errores,
lectura/muestreo, CPU, pico RSS observado, distribuciones, vacíos/duda, entradas inválidas,
capturas, actividad, tasas y tiempos de alertas, repetición y distancia KS de scores
contra referencia. **M07 no se reclama como bono separado de la familia RSS de G3**.
Throughput equivalente a G2 y frescura equivalente a G6 tampoco se reclaman otra vez.
Definiciones, fórmulas, unidades, ventanas y recálculo en [METRICAS.md](METRICAS.md).

El dashboard distingue valores actuales de último snapshot histórico e informa su
fecha. Su polling actualiza sin recargar; no rellena datos ausentes. La reproducción
anotada se deriva de un solo ID de evento inmutable: no superpone cajas de otro frame.
Las nueve gráficas admiten ejecución/período, hover y foco de teclado. No se interpolan
muestras faltantes ni se agregan puntos ficticios. Las clases mantienen sus nombres COCO.

Eventos/alertas incluyen filtros, orden y paginación. Galería enlaza capturas con eventos
y alertas; descarga originales o selección ZIP (hasta 100 IDs y 50 MiB).
Exportaciones CSV/JSON conservan IDs, timestamps y unidades y neutralizan fórmulas en
celdas de texto. Exportar eventos/alertas respeta sus filtros; métricas/ventanas agregadas
admiten ejecución y fecha, sin fragmentarlas por clase de forma engañosa.
El endpoint de extras sí recalcula sobre la selección de eventos que indica.

Alertas: **abierta → reconocida → resuelta**, con comentarios, timestamps e historial
append-only. Las operaciones usan versión esperada e ID idempotente. Una resolución
no modifica el evento ni sus puntuaciones; comentarios adicionales se conservan.
No se cierra automáticamente una alerta porque una ventana posterior parezca normal.

## C1, C2 y escenarios adicionales

El comando anterior de primera versión continúa disponible:

```powershell
.\.venv\Scripts\python.exe scripts/run_demo.py --scenario C1
.\.venv\Scripts\python.exe scripts/run_demo.py --scenario C2
```

La batería ampliada ejecuta base, video y S1–S7 en una carpeta nueva con UUID:

```powershell
.\.venv\Scripts\python.exe scripts/run_scenarios.py
```

- C1/C2: inferencias reales sobre secuencias, métricas, eventos, capturas y alertas.
  C1 también puede generar alertas bajas: éxito técnico no equivale a alta confianza.
- Video: MP4 real, posiciones, conteo de lecturas y descarte por muestreo.
- S1: se interrumpe un archivo NUEVO de prueba y se restaura; error de lectura y continuidad.
- S2: recorte de una fotografía real que el modelo procesa sin detecciones.
- S3: secuencia corta que conserva “evidencia insuficiente”.
- S4: selección desde calibración real, referencia, persistencia de cambio y recuperación.
- S5: bytes corruptos producen error de decodificación y luego se procesa otra imagen.
- S6: dos configuraciones identificadas con mismo modelo y puntuaciones; series separadas.
- S7: fallo técnico **inyectado** en un intento, con diagnóstico y ONNX real antes/después.
  No se presenta ese intento fallido como una inferencia ejecutada.

La calibración conserva todas sus salidas exploratorias antes de construir S4; la
demostración posterior mantiene umbrales y scores reales. Se usan variantes
correlacionadas de una escena pública; no son muestras independientes ni prueba de calidad.
La distancia KS es descriptiva, sin p-value ni afirmación de drift.
Los fallos, aceptación esperada/observada y ámbitos de simulación están documentados
en cada result.json. Si una condición no se observa, el script la deja pendiente y
no cambia scores ni reglas para declarar éxito.

El replay de imágenes usa intervalos entre inicios sin ráfagas de recuperación.
El video lee secuencialmente, descarta frames intermedios según posición nominal y
conserva el último frame para cerrar la contabilidad. Su ritmo máximo se limita
también por los FPS del archivo. No se duplican frames para alcanzar una tasa mayor.
Para videos de tasa variable, la posición index/FPS es nominal. La primera muestra
es inmediata; tasas calculadas en ejecuciones muy cortas pueden superar la tasa
nominal por el efecto del borde inicial. Los tiempos de pausa se excluyen de G2/CPU.

## Pruebas y recálculo

```powershell
.\.venv\Scripts\python.exe -m pytest --junitxml=evidencias/ampliacion/pruebas/pytest.xml
.\.venv\Scripts\python.exe -m pip check
node --check web/static/js/portal.js
```

Node solo sirve para comprobar sintaxis de JavaScript si está instalado; no es
dependencia para iniciar el portal. Las pruebas reales se omiten expresamente si faltan
pesos/entradas: un skip no acredita inferencia real. Preparar modelo/medios primero.

Prueba opcional del navegador real, con Edge instalado y servidor en puerto 8006:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-browser-test.txt
.\.venv\Scripts\python.exe -m pytest browser_tests -q
```

Usa un perfil nuevo y Edge headless, sin descargar otro navegador. Incluye filtros
rápidos, refresco, recuperación de errores, ZIP con atribución, vista móvil y controles
con inferencia real de dos colecciones. No ejecutarla mientras otra persona mantiene
un productor activo. Los paquetes opcionales no son necesarios para usar el portal.

Después de ejecutar la batería (usar la ruta exacta que imprime):

```powershell
$lote = Get-ChildItem .\evidencias\ampliacion\ejecuciones -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
.\.venv\Scripts\python.exe scripts/verify_metrics.py (Join-Path $lote.FullName 'C1')
.\.venv\Scripts\python.exe scripts/verify_metrics.py (Join-Path $lote.FullName 'C2')
.\.venv\Scripts\python.exe scripts/verify_extras.py (Join-Path $lote.FullName 'S4')
```

Con el servidor ejecutándose, copiar un run_id real de Ejecuciones:

```powershell
.\.venv\Scripts\python.exe scripts/verify_features.py --run-id 'REEMPLAZAR_POR_RUN_ID_REAL'
```

Este recorrido guarda verificaciones HTTP, exportaciones e imágenes con IDs.
No acredita por sí solo la observación en navegador; esa evidencia se registra aparte.
La herramienta integrada no confirmó el evento de descarga del navegador durante una
prueba; el ZIP y sus PNG sí se verificaron por HTTP y pruebas automatizadas.

## Persistencia, integridad y límites

SQLite guarda runs, eventos, ventanas, snapshots, fuentes, controles y cambios de
alerta. La migración añade tablas/índices sin borrar los registros de la primera versión.
Las imágenes decodificadas se guardan como PNG sin pérdida, sin TTL ni limpieza automática.
Se conservan hash de entrada recibida y hash del PNG; una imagen anotada es un derivado
descargable, nunca reemplaza el original. Los errores de lectura/decodificación no
producen capturas ficticias.

Datos locales en data/runtime se excluyen de Git; las evidencias seleccionadas se
conservan junto a JSON/JSONL y pueden versionarse. Las entradas generadas de escenarios
se regeneran por código y se excluyen para evitar copias repetidas de calibración.

No se afirma una calificación de 100 ni bonos confirmados. El inventario separa nivel
potencial, evidencia y revisión pendiente. Nombre/matrícula, vinculación a un commit
autorizado y CI remoto permanecen pendientes. No se hicieron commits ni push.

Límites: servicio local sin autenticación ni notificaciones externas; sin prueba de
carga prolongada. Consultas históricas filtran JSON en Python; la galería/polling y la
retención permanente requieren vigilar disco para uso largo. Un error de disco puede
detener una ejecución y dejar una captura huérfana para revisión. Las anotaciones de
alertas son revisiones técnicas, no etiquetas de verdad. Los formatos dependen de los
códecs disponibles. No se reclama evaluación de accuracy, IoU, precision/recall ni mAP.

