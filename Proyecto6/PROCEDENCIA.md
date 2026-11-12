> Copia pública derivada: los enlaces a registros locales se sustituyeron por notas explícitas. El original se conserva.

# Procedencia y aportación individual

Estudiante: **Bryan Edgardo Romo Gonzalez · 745268**.
[Ficha académica definitiva](Docs/IDENTIDAD.md). Entrega individual de Machine Learning, ITESO.
Entrega individual preparada con asistencia de Codex; revisar código y evidencia antes
de presentar. No se atribuye al estudiante entrenamiento ni autoría original de YOLOX.

## Componentes adaptados

| Original consultado | Copia/adaptación autónoma | Dependencias y cambios |
| --- | --- | --- |
| `../Proyecto5/src/p5/detector_onnx.py` | `src/monitor_cv/_yolox.py` y wrapper `detector.py` | NumPy, Pillow y dataclass local Detection. Se conservan letterbox, rejillas, decodificación y NMS; se elimina import de p5 y el cargador de configuración anterior. No se recortan/clampan puntuaciones: se rechazan scores inválidos. El wrapper mide ONNX por separado y conserva candidatas pre-NMS. |
| `../Proyecto5/src/p5/contrato.py` | `src/monitor_cv/events.py:Detection` | Solo dataclass de clase, ID, confianza y bbox. No se importan comandos ni estados del carrito. |
| `../Proyecto5/scripts/capturar_esp32.py` | `src/monitor_cv/_mjpeg.py` y adaptador `camera.py` | Biblioteca estándar, lector incremental JPEG, buffer acotado, último frame, reconexión, frescura y cierre de socket. No se copian visor, anotador ni lógica de conducción. |
| `../Proyecto5/scripts/capturas_core.py:anchored_clock` | `src/monitor_cv/_mjpeg.py` | Reloj monotónico anclado a UTC, sin dependencias internas de datasets. |
| `../Proyecto5/scripts/descargar_modelo.py` | `scripts/download_model.py` | urllib/ssl/hashlib + PyYAML; descarga temporal, tamaño y SHA antes de renombrar. Se usa CA del sistema o CA explícita en vez de certifi directo; TLS siempre activo. |
| `../Proyecto5/modelo/descriptor.yaml` | `modelo/descriptor.yaml` | Se retiran clases de política de obstáculos; se conservan artefacto, URL, hash, clases COCO y contrato. No se copia el modelo binario de P5: se descarga de la fuente oficial. |

Las fuentes originales se revisaron en lectura y sus hashes anteriores están en
integridad_inicial.json (registro local o recurso regenerable; consultar el índice público). La comprobación final
está en auditoria_repositorio.json (registro local o recurso regenerable; consultar el índice público).
Los documentos originales de Docs están cubiertos por la misma verificación.

## Desarrollo de esta entrega

La edición 0.4 añade el [módulo de revisión](src/monitor_cv/reviews.py), integración
de Eventos/Alertas, capa de imagen validada, historial SQLite independiente, pruebas,
normalización de nuevas rutas de colecciones y auditoría final. Es desarrollo de
esta entrega individual asistido por Codex; no se atribuye al estudiante autoría
de YOLOX, fotografías o librerías. El actor técnico local no replica la identidad
académica en cada registro. La ficha y fecha definitivas están en
[IDENTIDAD](Docs/IDENTIDAD.md). No se usó hardware ni cámara para estas evidencias.

Configuración Pydantic y hash efectivo, fuentes reproducibles y muestreo, wrapper ONNX,
eventos de monitoreo, ventanas y referencia fija, reglas de baja confianza/cambio sostenido,
persistencia SQLite, capturas PNG, inventario G1–G7, portal, pruebas, comandos de evidencia,
documentación y configuración general del repositorio. Sin imports de Proyecto1–Proyecto5,
sin copiar entornos, conjuntos de datos, resultados o políticas STOP/FORWARD.

## Referencias externas

- [YOLOX de Megvii](https://github.com/Megvii-BaseDetection/YOLOX) y
  [release 0.1.1rc0](https://github.com/Megvii-BaseDetection/YOLOX/releases/tag/0.1.1rc0).
  Código del proyecto bajo [Apache-2.0](https://github.com/Megvii-BaseDetection/YOLOX/blob/main/LICENSE).
  Ge et al., [YOLOX](https://arxiv.org/abs/2107.08430).
- [Imagen pública dog.jpg](https://github.com/Megvii-BaseDetection/YOLOX/blob/main/assets/dog.jpg)
  usada únicamente como escena de demostración; no se reclama su autoría. URL y SHA se
  guardan en `data/demo/manifest.json`. No se presume que la licencia del código describa
  por sí sola los derechos de cada imagen externa.
- [ONNX Runtime Python](https://onnxruntime.ai/docs/get-started/with-python.html),
  [FastAPI/Jinja2](https://fastapi.tiangolo.com/advanced/templates/).

Las instrucciones heredadas de Proyecto3/Proyecto4 se mantienen como antecedentes;
sus equipos/roles no definen la autoría de este trabajo individual.

## Ampliación de fuentes locales y extras

La ejecución predeterminada usa secuencias o video local. El lector MJPEG heredado
queda como código opcional de compatibilidad; no se requiere cámara ni carrito y
el portal solo permite iniciar imágenes/video. Los originales anteriores permanecen
sin cambios. La auditoría vigente está en
auditoria_repositorio.json (registro local o recurso regenerable; consultar el índice público).

Se añadieron lectura/muestreo de video, registro de fuentes y validación de rutas,
control de pausa y sincronización por ID, portal en español, consultas y gráficas,
galería/ZIP, exportaciones seguras, historial transaccional de alertas, instrumentación
CPU/lectura, catálogo de métricas y escenarios S1–S7. Son desarrollo de esta entrega
individual con asistencia de Codex, no componentes originales del Proyecto 5.

La imagen pública se transforma mediante recorte/degradación reproducibles para
obtener observaciones distintas del mismo detector. El video de demostración se
construye con esas imágenes: es material de prueba, no una cámara física ni un nuevo
dataset representativo. `calibration.json` conserva todos los resultados explorados;
no se alteran scores para elegir una condición. S7 inyecta un fallo técnico declarado,
con inferencia real antes/después. Las pruebas unitarias con scores prefijados se
identifican como pruebas de mecanismos, nunca como evidencia del modelo.

Las evidencias de la primera entrega se conservan byte a byte. El manifiesto
preexistentes-sha256.json (registro local o recurso regenerable; consultar el índice público) y la
verificación de conservación (registro local o recurso regenerable; consultar el índice público) registran esa
comprobación. Los nuevos lotes tienen sus propios IDs, configuración y hashes de código.


## Fotografías públicas incorporadas · 0.3

Se adquirieron 80 escenas distintas de Open Images desde el espejo oficial CVDF.
Autor, título, URLs y licencia de cada fila están en el manifiesto (registro local o recurso regenerable; consultar el índice público)
y [documentación](Docs/DATASETS.md). No se deduce licencia de fotografía desde licencia
de código. Se conservan bytes del espejo; PNG, anotaciones y miniaturas son derivados
identificados. Los ZIP de capturas del dataset conservan atribución.
Adquisición/licencias/hash, fuente con identidad de entrada, consultas SQL, inventario
derivado de capturas, miniaturas/cache/reintento y pruebas Edge son desarrollo de
esta entrega asistido, no autoría del dataset o del modelo. La auditoría (registro local o recurso regenerable; consultar el índice público)
y conservación (registro local o recurso regenerable; consultar el índice público) comprueban los originales/evidencias
y payloads históricos. Las nuevas fuentes no importan código de los antecedentes.


## Identificación académica vigente

Grupo **O2026_ESI3906B**. [Canvas del curso](https://canvas.iteso.mx/courses/57431).
Identidad completa en [IDENTIDAD.md](Docs/IDENTIDAD.md).


## Actualización para publicación segura

Grupo confirmado **O2026_ESI3906B**, [Canvas](https://canvas.iteso.mx/courses/57431).
La selección pública y sus límites vigentes se describen en [PUBLICACION_SEGURA](Docs/PUBLICACION_SEGURA.md)
y el [índice GitHub](evidencias/publicacion_segura/INDICE_GITHUB.md). Hay 80 fotografías
locales conservadas y 79 seleccionadas para distribución/reproducción pública; una
se omite por contacto en su atribución, sin modificar el original. C1/C2, video y S1–S7
tienen alternativas reales con licencia identificada. Los 366 puntos son estimados,
no calificación oficial. Los archivos antiguos ya públicos requieren una decisión
posterior sobre la selección Git; no se ejecutó add, commit ni push.
