# Dataset público de demostración · 80 fotografías distintas

Entrega individual. Las categorías son **objetivos de selección**, no las clases
predichas ni etiquetas creadas por YOLOX. Las fotografías no se modificaron para
provocar puntuaciones. Los ejemplos anteriores del perro/bicicleta y sus evidencias
se conservan para reproducir C1/C2; el nuevo material amplía las demostraciones.

## Material adquirido

Se descargaron 80 archivos JPEG de Open Images, diez por colección, mediante
peticiones HTTPS selectivas al espejo público CVDF. Son fotografías distintas con
80 IDs y SHA-256 diferentes. No son 80 transformaciones de una imagen. El espejo
oficial limita el lado mayor a 1024 píxeles; se conservan esos bytes tal como llegaron.

| Carpeta | Selección prevista | Archivos |
| --- | --- | ---: |
| personas | Personas según anotaciones públicas | 10 |
| animales | Perros y gatos | 10 |
| vehiculos | Automóviles y motocicletas | 10 |
| bicicletas | Bicicletas y otros transportes | 10 |
| objetos | Objetos domésticos | 10 |
| escenas_multiples | Al menos cuatro clases de interés anotadas | 10 |
| baja_confianza | Oclusión anotada en al menos la mitad de tres o más cajas | 10 |
| escenas_despejadas | Naturaleza/pocos objetos previstos; no garantiza salida vacía | 10 |

La categoría histórica de carpeta `baja_confianza` se presenta en el portal como
“Escenas difíciles: oclusión anotada (no predicción)”. No se seleccionó por score del
detector. La selección no garantiza diez escenas nocturnas: el criterio reproducible
de dificultad utilizado es oclusión del dataset. La luminancia media se registra
como descripción, sin confundir oscuridad con baja confianza.

Adquisición inicial: **77,877,535 bytes de red**, incluidos 51,500,986 bytes de cuatro
tablas de metadatos. Los JPEG ocupan 26,376,549 bytes. Límite: 200,000,000 bytes;
no se descargó ningún archivo ZIP ni dataset completo. Cero duplicados exactos y
cero casi duplicados rechazados en esta selección; eso es un resultado observado,
no un objetivo artificial. La reanudación validó los 80 archivos con **cero bytes de red**.

## Procedencia y licencia por fotografía

- [Manifiesto JSON](../data/media/datasets/manifest.json) y
  [CSV](../data/media/datasets/manifest.csv): identidad, nombre original, dataset,
  URLs original/página/espejo, autor/perfil, título, licencia y fuente de la licencia,
  fecha de descarga UTC, SHA-256, bytes, resolución y categoría prevista.
- [Selección congelada](../config/dataset-selection.json): IDs/URLs y SHA esperados,
  semilla y metadatos con sus hashes. Permite repetir la misma adquisición.
- [Reportes de descarga](../evidencias/datasets/descargas/): éxitos, reusos, errores,
  omisiones, duplicados, déficits por categoría y presupuesto de cada invocación.

Se consultó la **fila individual** de `validation-images-with-rotation.csv`. Las 80
filas aceptadas identifican CC BY 2.0 y autor. El programa admite esa URL de licencia
mediante lista explícita; una licencia desconocida o no admitida se omite. No se
deduce la licencia fotográfica de la licencia del código de Open Images/YOLOX.

Mantener junto a los archivos el manifiesto con autor, título, enlace de procedencia
y licencia. Las capturas PNG, anotaciones y miniaturas son derivados identificados;
no reemplazan el JPEG adquirido. El ZIP de capturas de dataset incluye
`ATTRIBUTION.json`. El autor y el enlace de licencia también se muestran en la galería.
El MD5 publicado del original se conserva como metadato; no se compara con el JPEG
redimensionado del espejo como si ambos fueran los mismos bytes.

Fuentes primarias consultadas:

- [Descargas y formato oficial de Open Images](https://storage.googleapis.com/openimages/web/download_v7.html).
- [Espejo CVDF y redimensionamiento](https://github.com/cvdfoundation/open-images-dataset).
- [Descargador oficial: acceso anónimo por ID](https://github.com/openimages/dataset/blob/main/downloader.py).
- [CC BY 2.0: atribución y condiciones](https://creativecommons.org/licenses/by/2.0/).

No se accedió a contenido privado ni se eludieron autenticación o controles. El uso
es una demostración local; no se infieren identidades ni atributos de personas.

## Adquisición reproducible en Windows PowerShell

Desde la raíz del repositorio, con la instalación del [README](../README.md):

```powershell
Set-Location .\Proyecto6
.\.venv\Scripts\python.exe scripts/download_demo_dataset.py --target-per-category 10 --max-mb 200 --seed 6
```

El script valida Pillow y OpenCV, dimensiones y formato antes de escribir; calcula
SHA-256, pHash DCT de 63 bits y dHash. Rechaza pHash a distancia <=5 o dHash <=3
acompañado de RMSE <=3 en grises 16x16, para cubrir recompression en escenas lisas.
La tolerancia pHash se configura con `--near-distance`. No se altera la imagen usada
por el detector: las representaciones reducidas sirven solo para detectar duplicados.

La selección congelada evita volver a descargar tablas o elegir otras escenas en
una segunda máquina. Si falta un JPEG se solicita ese ID y exige su SHA guardado.
Un archivo local con SHA distinto se informa; no se sobrescribe como si fuera válido.
Cambiar `--target-per-category` permite usar un subconjunto de los IDs congelados;
pedir más que los disponibles deja déficits explícitos. `--seed` afecta únicamente
el descubrimiento inicial, no cambia los IDs ya congelados. Para una selección nueva,
usar una copia separada del proyecto/configuración y conservar la anterior.

En una instalación sin selección previa se descargan únicamente los cuatro CSV
oficiales y candidatos necesarios, nunca todos los píxeles. Sus URLs y SHA quedan
registrados. La caché de metadatos en data/.cache está excluida de Git.
El límite incluye también archivos rechazados y metadatos transferidos durante esa
invocación; no representa un límite de disco de las capturas generadas después.

Si una red bloquea HTTPS o un archivo deja de estar disponible, el reporte conserva
el error/ID; no se afirma éxito. Repetir el mismo comando en una red con acceso a
storage.googleapis.com y open-images-dataset.s3.amazonaws.com. No desactivar TLS.

## Integración y demostración en el navegador

```powershell
.\.venv\Scripts\python.exe -m uvicorn monitor_cv.main:create_app --factory --app-dir src --host 127.0.0.1 --port 8006
```

1. Abrir <http://127.0.0.1:8006/sources>. El inicio normal del servidor registra las
   ocho colecciones verificadas; no descarga imágenes en segundo plano. Registra
   una vez por ruta/ID y conserva las dos fuentes locales anteriores.
2. Seleccionar una colección y configurar frames/s. Iniciar; abrir Reproducción para
   observar el frame anotado con sus scores originales. Pausar, continuar y detener.
3. Después de detener, seleccionar otra colección. El historial por fuente conserva
   sus ejecuciones; cada nueva ejecución tiene ID/modelo/configuración propios.
4. Abrir Galería y filtrar por colección prevista, clase real, zona, fuente, ejecución
   o fecha. La categoría no sustituye las predicciones de la tabla.
5. Abrir evento → captura/procedencia → alertas. En Históricos seleccionar el run;
   modelos/configuraciones diferentes mantienen series y referencias separadas.

Para preparar **todas** las ejecuciones históricas y recálculos automáticamente:

```powershell
.\.venv\Scripts\python.exe scripts/run_dataset_demo.py --sample-hz 4
.\.venv\Scripts\python.exe scripts/audit_gallery.py
.\.venv\Scripts\python.exe -m pytest -q
```

El lote CLI registra resultados históricos en la misma base. Para visualizar un
procesamiento activo en Reproducción, iniciarlo desde el portal; no se presenta un
lote CLI finalizado como video en vivo. El [índice de evidencias](../evidencias/datasets/indice.md)
enlaza la ejecución final, eventos/alertas/ventanas, capturas, código y recálculos.
Cada ejecución puede volver a usar las mismas 80 imágenes sin contarlas como nuevas.

## Referencias sin captura y galería

El contador anterior mezclaba eventos técnicos sin bytes decodificables con archivos
perdidos. La auditoría inicial encontró diez eventos sin `image_ref` (cinco errores de
fuente y cinco de decodificación), incluyendo los ocho casos históricos más antiguos;
no faltaba un archivo declarado. Las pruebas posteriores agregan nuevos casos de
esos mismos mecanismos, por lo que el contador técnico puede aumentar.

Ahora se separan capturas disponibles, eventos técnicos sin captura e incidencias
reales: referencia ausente, archivo faltante, ruta insegura, hash incorrecto o
archivo corrupto. El detalle enlaza cada evento y su razón. No se fabricaron imágenes,
no se cambiaron hashes/payloads históricos y no se borró evidencia.

`audit_gallery.py --restore-exact` solo puede restituir un archivo faltante desde
evidencia cuyo SHA coincide exactamente con el ya registrado; no inventa nuevas rutas
ni cambia eventos. No fue necesaria ninguna restauración en esta entrega.

La galería consulta SQLite con LIMIT/OFFSET y filtros parametrizados, envía solo los
campos necesarios de esa página y resuelve enlaces de alertas en un lote. Miniaturas
JPEG <=320x240, lazy loading, máximo cuatro solicitudes, cancelación al cambiar de
consulta/sección, timeout, reintento y ETag/304 evitan cargar PNG completos. Los
originales se obtienen al abrir/descargar. Las consultas JSON usan no-store; los
derivados tienen caché privada con validación por evento/firma.

## Alcance de resultados

El lote final procesa las 80 imágenes sin filtrar scores para construir casos.
Los resultados y ejemplos de alta/duda/baja/vacía están en el reporte de entrega.
La categoría despejada no garantiza ausencia de salidas: el piso 0.10 también expone
predicciones débiles. La confianza no es probabilidad calibrada de acierto. Etiquetas
de Open Images y comprobación visual de ejemplos no constituyen evaluación formal
de accuracy/mAP. Las diferencias de tiempo observadas no prueban causalidad por clase.
