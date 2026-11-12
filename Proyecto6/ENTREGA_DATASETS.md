> Copia pública derivada: los enlaces a registros locales se sustituyeron por notas explícitas. El original se conserva.

# Ampliación del dataset y portal · reporte de entrega

Entrega individual. Nombre académico y matrícula pendientes. Sin commits ni push.
Implementación local Windows/Python 3.12, FastAPI/SQLite/YOLOX-Nano CPU, sin cámara.

## 1. Originales descargados

**80 fotografías distintas**, 80 IDs, 80 URLs originales, 80 SHA-256 y MD5 de origen
distintos. Diez por categoría: personas, animales, vehículos, bicicletas/transporte,
objetos, múltiples, difíciles/oclusión y despejadas. Se conservaron los JPEG del espejo,
sin crear ochenta modificaciones de dog.jpg. Manifiesto (registro local o recurso regenerable; consultar el índice público).

## 2. Duplicados y volumen

Cero exactos y cero casi duplicados rechazados en el conjunto real; los mecanismos
se probaron con casos unitarios identificados. Red inicial: 77,877,535 bytes (51,500,986
metadatos + 26,376,549 JPEG), bajo 200 MB. Reanudación: 80 reusos y cero bytes de red.
Las capturas PNG/evidencias posteriores ocupan espacio adicional y no son nuevas fotos.

## 3. Procedencia y licencias

Open Images validation, espejo oficial CVDF y metadatos oficiales. Las 80 filas
seleccionadas declaran CC BY 2.0; se verificaron individualmente. Autor, título,
nombre/URL original, página, licencia, fecha UTC, tamaño/resolución y hashes están en
JSON/CSV. Los ZIP incorporan ATTRIBUTION.json; galería/evento muestran crédito/enlaces.
[Explicación y fuentes primarias](Docs/DATASETS.md). No se asume una licencia uniforme
para todo el dataset ni se reclama la autoría del contenido externo.

## 4. Fuentes registradas

Ocho colecciones nuevas, cada una con diez archivos y un ID persistente, junto a las
dos fuentes locales anteriores. Se registran al iniciar normalmente el portal o
ejecutar el lote. Los SHA se verifican antes de registrar y antes de inferir. Las
fuentes pueden seleccionarse, pausarse, continuarse, detenerse y consultar su historial.
IDs y configuración (registro local o recurso regenerable; consultar el índice público).

## 5. Inferencias reales y escenarios

Lote final: **80 eventos/entradas únicas, 569 detecciones, 52 clases y 71 alertas**.
Zonas: 47 aceptadas por política, 82 en duda, 440 bajas. Dos imágenes sin detecciones.
Se procesa todo el conjunto sin escoger/alterar puntuaciones para producir ejemplos.
Una colección despejada produjo una de las salidas vacías; otras fotos de esa misma
colección tuvieron detecciones débiles. No se promete que cada categoría produzca
un escenario ni que las 52 clases sean correctas. No se calculó accuracy/mAP.

Como comprobación visual puntual, el evento `evt-b42b4f6a634f4f40802620282a03f1e2`
contiene personas (scores 0.837741, 0.829614 y 0.807278) y mesa (0.802495), clases
presentes en su captura conservada (registro local o recurso regenerable; consultar el índice público).
También se revisaron visualmente perro/persona en la galería y automóvil en la
reproducción de vehículos de Edge. Son ejemplos de reconocimiento semántico, no
validación cuantitativa de todas las cajas o de las 52 clases.

Ejecuciones seleccionadas (registro local o recurso regenerable; consultar el índice público) y
ejemplos con IDs/score original (registro local o recurso regenerable; consultar el índice público).
Cada run conserva fuente, modelo/version/hash, configuración, hora, entradas/IDs,
eventos, ventanas, PNG, alertas y métricas. G1–G7 y M01–M20 se recalcularon en los ocho
paquetes. Las latencias medias varían por escena/fuente sin demostrar causalidad.
Los lotes de desarrollo y recorridos de controles se conservan, pero no cuentan
como otras fotografías. El dataset sigue teniendo 80 originales.

## 6. Referencias sin imagen

La pantalla anterior agrupaba fallos técnicos y archivos perdidos. Al comenzar se
encontraron 10 eventos sin referencia:
cinco source_error y cinco decode_error, incluyendo los ocho históricos más antiguos.
No había un PNG declarado faltante ni ruta que reparar. IDs originales (registro local o recurso regenerable; consultar el índice público).
Las suites agregaron eventos técnicos nuevos; el contador actual se documenta en
auditoría (registro local o recurso regenerable; consultar el índice público).
No se fabricaron capturas, cambiaron hashes/payloads ni borraron evidencias.

El portal separa capturas disponibles, técnicos sin captura, pendientes de comprobación
y anomalías verdaderas. En el cierre hay 18 técnicos,
0 anomalías y 0 pendientes. No fue necesaria restauración.
Solo se permite recuperar un archivo perdido desde bytes que igualen el SHA histórico.

## 7. Galería optimizada e integración

SQL parametrizado con filtros y LIMIT/OFFSET; materializa solo la página, no cientos
de payloads. Alertas resueltas en un lote. JPEG <=320x240 con ETag/304 y caché privada;
lazy loading con cuatro solicitudes, cancelación, timeout, mensajes y reintentos.
No descarga PNG completos al abrir. El original se obtiene al abrir/descargar.
Filtros: colección prevista, clase predicha, fuente, run, fecha y zona; se conserva
consulta/página tras refresco. La categoría no se muestra como una predicción.

Durante la implementación se detectó una carrera entre llegada de un evento y su
inventario: ahora figura pendiente, no perdido, y conteos/página usan una lectura
consistente. Edge detectó además un frame de la ejecución anterior al reiniciar:
ahora se limpia la vista y se aceptan solo snapshots del run iniciado. Se mantiene
el polling de un segundo; no se exige respuesta visual instantánea al backend.

## 8. Pruebas

Las 68 pruebas anteriores se ejecutaron primero y pasaron. Cierre: **87
aprobadas, cero fallos/errores/omisiones** (27.020 s), más **1 prueba
E2E aprobada en Edge** (17.738 s). JUnit en el índice (registro local o recurso regenerable; consultar el índice público).
Incluyen HTTP simulado solo en pruebas unitarias del descargador, datos corruptos,
licencias, hashes, similitud, SQL, paginación, referencias/restauración, thumbnails,
fuentes y ejecución real de YOLOX. La E2E usa servidor/modelo/descarga reales, sin mocks.

Edge confirmó filtros rápidos, refresco, cambios de sección, reintento ante error real,
ZIP nativo con atribución/hash, dos fuentes con pausa/continuación/parada y móvil.
Máximo observado de miniaturas en la apertura: 3;
cero solicitudes de PNG completo en esa comprobación. Pip check y sintaxis JS correctos.
Los intentos E2E fallidos se conservaron y se distinguen del cierre aprobado.

## 9. Rendimiento observado

Cinco consultas reales de 25 elementos con 1133 capturas disponibles:
375.6, 364.2, 446.1, 483.2, 394.6 ms; respuesta de
52609 bytes. Es una medición local sin prueba de carga ni
comparativa controlada con la edición anterior. El primer inventario puede tardar más
porque verifica hashes/formatos. Observaciones (registro local o recurso regenerable; consultar el índice público).

## 10. Archivos y evidencias

Inventario (registro local o recurso regenerable; consultar el índice público), índice (registro local o recurso regenerable; consultar el índice público),
[dataset/licencias](Docs/DATASETS.md), [manual](MANUAL_USUARIO.md) y [extras](Docs/EXTRAS.md).
Nuevos scripts download_demo_dataset/run_dataset_demo/audit_gallery, módulos datasets/gallery,
pruebas unitarias/E2E y selección congelada. Configuración/fuentes/productor, SQL,
derivados, endpoints, interfaz y documentación adaptados. Proyecto1–5 y Docs oficiales
intactos. Evidencias anteriores y payloads previos comparados por SHA en cierre (registro local o recurso regenerable; consultar el índice público).

## 11. Comandos exactos de PowerShell y demostración

Desde la raíz (instalación de Python/dependencias/modelo en [README](README.md)):

```powershell
Set-Location .\Proyecto6
.\.venv\Scripts\python.exe scripts/download_demo_dataset.py --target-per-category 10 --max-mb 200 --seed 6
.\.venv\Scripts\python.exe scripts/run_dataset_demo.py --sample-hz 4
.\.venv\Scripts\python.exe scripts/audit_gallery.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn monitor_cv.main:create_app --factory --app-dir src --host 127.0.0.1 --port 8006
```

Con servidor activo, opcional en otra terminal desde Proyecto6:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-browser-test.txt
.\.venv\Scripts\python.exe -m pytest browser_tests -q
.\.venv\Scripts\python.exe scripts/verify_metrics.py evidencias/datasets/ejecuciones/dataset-f316f59912a04cf1bb4a2bf2a1f3bc9a/animales
.\.venv\Scripts\python.exe scripts/verify_extras.py evidencias/datasets/ejecuciones/dataset-f316f59912a04cf1bb4a2bf2a1f3bc9a/animales
```

Navegador: Fuentes → colección → Iniciar → Reproducción → Pausar/Continuar/Detener.
Elegir otra después de detener. Galería → colección/clase/zona/fecha → aplicar;
abrir evento y alertas; seleccionar capturas y descargar ZIP. Históricos → run.
La [guía de dataset](Docs/DATASETS.md) amplía cada paso y el procedimiento sin red.

## 12. Pendientes y Git

No quedan pruebas relevantes fallando ni categorías incompletas en esta selección.
Nombre/matrícula, evaluación docente y publicación remota permanecen pendientes.
Licencia según metadatos oficiales, sin comprobación independiente de autoría original;
no se certifica calidad/accuracy. No hay prueba de carga prolongada. La herramienta
integrada tuvo límites de interacción; Edge headless verificó esos recorridos reales.
La retención de PNG no tiene TTL y ocupa disco adicional al volumen de descarga.
No se realizaron staging, commits ni push. Rama main sin commit; origin existe pero
no se utilizó. La auditoría no detectó archivos candidatos >20 MiB, credenciales de
operación ni .git anidados; dos coincidencias de URL son fixtures negativos conocidos.
