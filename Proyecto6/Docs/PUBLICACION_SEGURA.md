# Publicación segura y actualización académica

Grupo confirmado **O2026_ESI3906B**. [Canvas](https://canvas.iteso.mx/courses/57431).
[Identidad académica](IDENTIDAD.md): Bryan Edgardo Romo Gonzalez, matrícula 745268,
profesor Victor Hugo Martinez Sanchez, ITESO / Machine Learning, individual,
entrega 13/11/2026. La matrícula solo se conserva donde aporta identificación académica.

## Estado y alcance

Se preparó una selección pública derivada y reproducible del Proyecto6, con copias
sanitizadas y créditos. **El repositorio existente completo aún requiere resolver
sus archivos ya publicados**. No confundir esta selección con un commit autorizado,
un clone remoto comprobado ni una ejecución de GitHub Actions. La aplicación funciona
localmente; los 100 base +266 extra =366 son estimaciones internas sujetas al profesor.

No se ejecutó git add/commit/push/reset/clean, ni se cambió el índice, historial o remoto.
Los proyectos anteriores, documentos oficiales, predicciones y evidencias originales
permanecen intactos. Las nuevas ejecuciones usan almacenamiento aislado.

## Archivos recomendados y archivos locales

Publicar tras revisión: código src/web, scripts, pruebas, dependencias, descriptor del
modelo, settings sin credenciales, academic.json autorizado, documentos vigentes,
selección dataset-selection-public.json e índice/evidencias públicas de esta fase.
La copia materializada tiene PUBLICATION_MANIFEST.json: lista exacta de rutas, bytes,
SHA-256 y transformaciones. El manifiesto se verifica antes de copiar o preparar archivos.

Mantener locales: entornos/cachés, SQLite/WAL, pesos ONNX, temporales, entradas/MP4
legadas de dog.jpg, originales de auditorías con perfil personal, manifiesto completo
de 80 fotos con contacto, raw C1_PUBLIC que incluye esa foto y capturas antiguas no
seleccionadas. No se excluyen completos Proyecto1–Proyecto5. Las imágenes autorizadas
se recuperan con URLs y SHA; no se necesita duplicar sus bytes en GitHub.

## Privacidad encontrada y soluciones

La auditoría anterior registró 158 rutas de perfil. La nueva inspección amplía patrones
y separa cada incidencia por ruta, línea, tipo, estado Git y presencia en el HEAD remoto;
ver [clasificación sin valores sensibles](../evidencias/publicacion_segura/privacidad.json).
El remoto público se consultó mediante GET de metadatos/ref/tree: su main coincide con
el HEAD padre 0b0a7b459d299e4741753e08f4c7133da65f76f4. Archivos versionados en ese árbol
ya están publicados; archivos nuevos solo locales todavía no lo están en main.
No se inspeccionaron exhaustivamente otras ramas ni todos los commits.

Las rutas de Windows revelan contexto local, pero no son contraseñas. Contactos de
antecedentes y metadatos requieren minimización. Dominios sintéticos en fixtures no
son secretos. El detector de tokens es heurístico y no certifica ausencia absoluta.
El [registro de sanitización](../evidencias/publicacion_segura/sanitizacion.json) da
original/copias, SHA de ambos, campos retirados y motivo. Los originales no se reescriben.
Las copias de contactos de antecedentes se identifican explícitamente; no sustituyen
autores de fotos ni atribuciones legales. Las capturas nuevas del navegador ocultan
la identificación lateral; el portal conserva la identificación académica solicitada.

.gitignore no retira archivos rastreados ni borra el historial. No se puede declarar
resuelto el material ya público sin una decisión posterior sobre esas rutas. Cualquier
retirada futura del árbol también dejaría el commit anterior accesible; no se propone
reescritura automática ni eliminación de evidencia local.

## Licencias

dog.jpg proviene del ejemplo YOLOX; la licencia Apache del código no acredita su
licencia fotográfica individual. Se conservan bytes originales localmente y se omiten
de la selección nueva, junto con sus derivados. No se realizó una nueva descarga de esa foto.
C1/C2 y S1–S7 ahora tienen alternativas reales con fotos de Open Images acreditadas.

Las 80 fotos locales mantienen íntegros sus créditos y licencias por imagen. La selección
pública contiene **79**: se excluye 26557008b4fcf408 porque el nombre de autor oficial
incorpora un contacto. No se inventa un autor alternativo ni se elimina ese crédito
del manifiesto histórico. Su perfil público se documenta mediante URL, sin reproducir
el dato de contacto: https://www.flickr.com/people/linvoyage/ . Reincorporarla requeriría
resolver una forma de atribución autorizada. Las 79 restantes conservan autor, perfil,
título, URL original, licencia, fechas y SHA originales. Las capturas PNG y video son
derivados expresamente identificados. [Dataset público](../config/dataset-selection-public.json).

La licencia [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) exige atribución,
enlace y declaración de adaptaciones; no equivale a garantizar cualquier derecho de
terceros. [Open Images](https://storage.googleapis.com/openimages/web/download_v7.html)
publica metadatos por fotografía. La revisión se limita al material seleccionado.

## Evidencias de los criterios y estimaciones

El [índice GitHub](../evidencias/publicacion_segura/INDICE_GITHUB.md) relaciona R1–R7,
F1–F10, M01–M20 y C1/C2/S1–S7 con archivos presentes, IDs, resultados y reproducción.
El [recálculo](../evidencias/publicacion_segura/verificacion-paquetes.json) valida G1–G7
y los extras de once paquetes autorizados. No se transfieren capturas de dog.jpg.
La [revisión dog/cat](../evidencias/publicacion_segura/publico/revision/revision-publicable.json)
conserva scores y la alerta automática original; la gestión resuelta y decisiones humanas
son capas posteriores. No es una firma autenticada del estudiante ni un ground truth.

La [matriz pública](../evidencias/publicacion_segura/evaluacion-publica.json) conserva
100 base, F120/M90/S56 =266 extra estimados. M07 no se acredita como bono y M08 mantiene
3 puntos. No se duplican percentiles, repeticiones o escenarios alternativos. El nivel
de complejidad y la aceptación de evidencias quedan sujetos al evaluador externo.
R7 no se presenta como una publicación actual de esta versión: falta autorización Git
y observar el commit/CI remotos correspondientes. Los nuevos hashes distinguen cada
árbol de trabajo y ejecución del HEAD previo.

## Reproducción en Windows PowerShell

Usar una ruta corta para evitar WinError 206, Python 3.12 y la selección materializada.
Desde su carpeta Proyecto6:

Estos comandos son para la copia pública nueva. No ejecutar la adquisición de 79
sobre el directorio local histórico de 80: se conserva su manifiesto original.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock-windows.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/download_model.py --destino modelo
.\.venv\Scripts\python.exe scripts/download_demo_dataset.py --selection config/dataset-selection-public.json --target-per-category 10 --max-mb 200
.\.venv\Scripts\python.exe scripts/prepare_authorized_demo.py --output data/media/authorized_demo
.\.venv\Scripts\python.exe scripts/prepare_media.py --demo-dir data/media/authorized_demo --output data/media/authorized_video
$env:MONITOR_IMAGES_DIR='data/media/authorized_demo/normal'
$env:MONITOR_VIDEO_FILE='data/media/authorized_video/demo.mp4'
$env:P6_TEST_DEMO_DIR='data/media/authorized_demo'
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe scripts/run_authorized_scenarios.py
# Para preparar galería con variedad, ejecutar una vez sobre una base nueva:
.\.venv\Scripts\python.exe scripts/run_dataset_demo.py --sample-hz 4
# Caso técnico real para la prueba de eventos sin captura, antes de iniciar servidor:
.\.venv\Scripts\python.exe scripts/run_technical_demo.py
.\.venv\Scripts\python.exe -m uvicorn monitor_cv.application:create_app --factory --app-dir src --host 127.0.0.1 --port 8007
```

Si las imágenes ya existen con SHA válido, el adquiridor las reutiliza. Hay un déficit
intencionado de una foto en escenas_multiples (9 frente al objetivo 10), no un fallo
ocultado. El preparador no sobrescribe destinos anteriores: elegir otro nombre si existe.
Para Edge, otra consola desde Proyecto6 y el productor detenido:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-browser-test.txt
$env:MONITOR_TEST_URL='http://127.0.0.1:8007'
.\.venv\Scripts\python.exe -m pytest browser_tests -q
```

Requiere Microsoft Edge instalado y la galería poblada (>=50 capturas). Las pruebas
registran controles reales y pueden crear ejecuciones parciales adicionales. No crean
escenas originales nuevas. La demostración dog/cat en una base nueva obtiene otros IDs.
Los fallos de lectura/decodificación S1/S5 se marcan explícitamente; si no hay un evento
técnico en la base del portal se prepara una entrada corrupta aislada, sin inventar PNG.
No se requiere base privada, ESP32-CAM ni carrito. El video local se prueba realmente.

## Navegador

Abrir http://127.0.0.1:8007/ . Revisar el grupo en el pie. En Fuentes elegir animales,
iniciar, pausar/reanudar y detener; cambiar a otra colección crea otra ejecución.
Galería: filtrar colección/clase/run/fecha/zona, cambiar página, refrescar y abrir un
evento. En animales localizar 488d4412c71bf3f1, confirmar dog y rechazar cat con motivo;
alternar vista original/validada y gestionar la alerta con revisión vinculada. Volver
a cargar el navegador y reiniciar servidor conserva las revisiones en la misma SQLite.
History muestra métricas por fuente/run; las categorías previstas nunca son predicciones.

## CI y límites de la comprobación

El workflow P6 usa Python 3.12, dependencias declaradas, modelo oficial y la selección
autorizada de 79 fotos. Prepara una demo CC BY en data/media/authorized_demo y usa esa
ruta en las pruebas; no descarga dog.jpg. No requiere hardware, rutas de perfil, DB
privada, secretos ni sube automáticamente evidencias. Los workflows P1–P5 no se editan.
Comprobar YAML y ejecutar localmente sus pasos no equivale a observar GitHub Actions.
La ejecución remota queda pendiente hasta un push autorizado.

## Lista exacta y futura publicación, sin ejecutar

La [lista de candidatos](../evidencias/publicacion_segura/archivos-proximo-commit.txt)
enumera archivos de trabajo revisados; el manifiesto de la copia seleccionada describe
además las proyecciones de documentos. La selección no autoriza incluir automáticamente
los originales ni resuelve los archivos ya rastreados del commit anterior. Conservar
una copia local completa antes de cualquier decisión futura sobre el índice.

Solo **después de autorización y de resolver la selección existente**, se propone:

```powershell
# PROPUESTA: no ejecutada. Revisar cada ruta y hash de la selección materializada.
git status --short
git diff --check
$archivosRevisados = Get-Content -LiteralPath 'Proyecto6/evidencias/publicacion_segura/archivos-proximo-commit.txt'
# No continuar mientras haya rutas antiguas pendientes en el árbol o copia pública sin reconciliar.
git add --pathspec-from-file='Proyecto6/evidencias/publicacion_segura/archivos-proximo-commit.txt'
git diff --cached --stat
git diff --cached --check
git commit -m "Prepara entrega académica P6 y evidencias públicas verificables"
# Requiere autorización de publicación, revisión del árbol y resultado de CI posterior:
git push origin main
```

No se ejecutaron esos comandos de escritura. No usar git add . ni force push. Excluir
una ruta de esta lista no la elimina del árbol Git si ya estaba versionada. La lista
de rutas históricas a resolver y sus copias se mantiene en la clasificación de privacidad.
Antes de entregar: confirmar selección final, tratar bytes/ficheros previamente públicos,
autorizar Git, comprobar commit remoto y Actions, y conservar informe/paquete verificables.


## Resultados finales comprobados

Suite local: 115 aprobadas; copia independiente: 115 aprobadas, sin omisiones. Edge: 2 locales y 2 en copia independiente. Se descargaron de nuevo 79 réplicas verificadas (25,430,005 bytes), no escenas nuevas; los 80 originales locales siguen intactos. Los once paquetes autorizados se recalculan. Se comprobaron 2718 archivos protegidos y 3086 filas previas sin cambios. Detalle en [pruebas](../evidencias/publicacion_segura/pruebas.json), [portabilidad](../evidencias/publicacion_segura/portabilidad.json) e [integridad](../evidencias/publicacion_segura/integridad.json).
