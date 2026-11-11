# Evidencias de la ampliación

Entrega individual, versión 0.2.0. Nombre académico y matrícula pendientes.
Fecha UTC del cierre: 2026-11-11T00:03:50.768148+00:00. No hay calificación autoasignada.

- [Verificación final](verificacion-final.json): 68 pruebas, cero fallos/errores/skips, recálculos e identidad de código.
- [JUnit](pruebas/pytest.xml), [auditoría](auditoria_repositorio.json), [conservación](conservacion.json).
- [Lote final](ejecuciones/batch-f257a33483834710994f454dbb16000d/summary.json), [calibración real](ejecuciones/batch-f257a33483834710994f454dbb16000d/calibration.json).
- [C1/C2 servidos por HTTP](portal/C1-C2-http-final.json) y [reproducción exacta desde PNG](modelo-reproduccion.json).
- [Capturas del portal](portal/), [recorridos HTTP/exportaciones](funciones/).
- [Inventario F/M/S](../../Docs/EXTRAS.md), [matriz R1–R7](cumplimiento.md).
- [Reporte de entrega](../../ENTREGA_AMPLIACION.md), [manual](../../MANUAL_USUARIO.md).

## Ejecuciones seleccionadas

| Caso | Run | Intentos / detecciones / alertas | Condición observada |
| --- | --- | --- | --- |
| [C1](ejecuciones/batch-f257a33483834710994f454dbb16000d/C1/result.json) | `run-0584836099f54a7eaceec13d30ca2084` | 10 / 76 / 10 | ok |
| [C2](ejecuciones/batch-f257a33483834710994f454dbb16000d/C2/result.json) | `run-a1bcc6f11db4465fb54a34f57ee9709c` | 10 / 65 / 10 | ok |
| [S1](ejecuciones/batch-f257a33483834710994f454dbb16000d/S1/result.json) | `run-5537f01575dc4e3194e13b7743c24bbc` | 4 / 24 / 3 | ok, source_error |
| [S2](ejecuciones/batch-f257a33483834710994f454dbb16000d/S2/result.json) | `run-51db13717933430e802157704194445c` | 3 / 0 / 0 | no_detections |
| [S3](ejecuciones/batch-f257a33483834710994f454dbb16000d/S3/result.json) | `run-6329525ad3ec46b9b197c23311c4fcf0` | 1 / 8 / 1 | ok |
| [S4](ejecuciones/batch-f257a33483834710994f454dbb16000d/S4/result.json) | `run-747a89d404d942c2bcf761965f760a1b` | 25 / 125 / 26 | ok |
| [S5](ejecuciones/batch-f257a33483834710994f454dbb16000d/S5/result.json) | `run-caf7236291d44e90bd06210f96104d82` | 3 / 16 / 2 | ok, decode_error |
| [S6-v1](ejecuciones/batch-f257a33483834710994f454dbb16000d/S6-v1/result.json) | `run-71379fe9ae7343c9b64aaa82a0808085` | 2 / 16 / 2 | ok |
| [S6-v2](ejecuciones/batch-f257a33483834710994f454dbb16000d/S6-v2/result.json) | `run-b6b1e03a8e544e3fab803f9d3dd35f85` | 2 / 16 / 2 | ok |
| [S7](ejecuciones/batch-f257a33483834710994f454dbb16000d/S7/result.json) | `run-547d7cf8066f4a15ac71e6e84de3f78a` | 4 / 24 / 3 | ok, inference_error |
| [Video](ejecuciones/batch-f257a33483834710994f454dbb16000d/Video/result.json) | `run-fa332eaacd6046bd912f5a1e1a301bda` | 21 / 128 / 21 | ok |

S6 compuesto compara las dos versiones: hashes distintos y mismos scores. En S7 solo
el intento fallido está inyectado; los restantes ejecutan ONNX. En S1 se retira un
archivo entre lecturas y luego se procesa la siguiente imagen existente. No se
presenta ningún escenario como transmisión de cámara física.

Cada carpeta contiene result.json, run.json, events/alerts/windows/actions.jsonl,
metrics.json, extras.json, metric-verification.json, code-sha256.json y sus PNG.
Los IDs enlazan capturas y alertas; hash del PNG y de entrada se distinguen.

## Recorridos HTTP conservados

- [http-2b672fa66fe546109b3b698bbcbfd4d2](funciones/http-2b672fa66fe546109b3b698bbcbfd4d2/verification.json): run `run-c24e0b08d67446c493b2d1920799c423`; verificaciones verdaderas, sin observaciones ausentes: True.
- [http-4211c52d7c024f99b9decca0946640c9](funciones/http-4211c52d7c024f99b9decca0946640c9/verification.json): run `run-c24e0b08d67446c493b2d1920799c423`; verificaciones verdaderas, sin observaciones ausentes: True.
- [http-99fab5c316b34f5ba6bcfa94e27a6883](funciones/http-99fab5c316b34f5ba6bcfa94e27a6883/verification.json): run `run-747a89d404d942c2bcf761965f760a1b`; verificaciones verdaderas, sin observaciones ausentes: False.
- [http-b8cfedd615304ac68142ae0fffda648e](funciones/http-b8cfedd615304ac68142ae0fffda648e/verification.json): run `run-c24e0b08d67446c493b2d1920799c423`; verificaciones verdaderas, sin observaciones ausentes: True.
- [http-d3e69037e2d0405c981240ed593673b0](funciones/http-d3e69037e2d0405c981240ed593673b0/verification.json): run `run-9197cff5c13848fb8485d295eca202d6`; verificaciones verdaderas, sin observaciones ausentes: False.
- [http-e875c88699ad42e7a533beaa51731017](funciones/http-e875c88699ad42e7a533beaa51731017/verification.json): run `run-c24e0b08d67446c493b2d1920799c423`; verificaciones verdaderas, sin observaciones ausentes: True.

Los recorridos del run `run-c24e0b08d67446c493b2d1920799c423` acreditan pausa
con frame congelado y gestión persistente real de una alerta. Los reportes anteriores
al reinicio del servidor abarcan la implementación previa de la ampliación; el lote
final y el recorrido S4 corresponden al código final y añaden M20. No se sustituyen
resultados históricos por los actuales.

## Navegador y límites de la evidencia

Se registró/seleccionó video, inició, pausó y continuó el procesamiento; se verificó
imagen anotada con el mismo ID, dashboard, históricos, filtros y galería. Una alerta
se reconoció y resolvió con comentarios reales, sin modificar el evento. Se registró
una secuencia de imágenes por el formulario de Fuentes.

Capturas F1–F8 en portal/ documentan esas pantallas. `F7-intento-puntero.png` conserva
un intento de clic interceptado por la herramienta; la resolución se completó con
teclado. La herramienta integrada no confirmó un evento nativo de descarga; los
ZIP/CSV/JSON se validaron como respuestas HTTP y bytes guardados, sin afirmar que
el navegador confirmó la descarga. El informe de navegador agrega las dimensiones
realmente comprobadas; una captura sola no certifica funcionalidad.

El [registro de navegador](portal/browser-verification.json) identifica los alcances
y hashes. Las capturas de escritorio seleccionadas son
[dashboard](portal/F1-edge-dashboard.png), [reproducción](portal/F2-edge-reproduccion.png),
[históricos](portal/F3-edge-escritorio.png) y [fuentes](portal/F8-edge-fuentes.png),
tomadas con Edge headless en un perfil de prueba nuevo. El navegador integrado
también se recorrió con disposición estrecha; al redimensionarlo algunas capturas
conservaron un lienzo mayor que su disposición. Se conservan como registro de esa
herramienta y no se usan para acreditar dimensiones de escritorio.

El último recorrido `http-d3e69037e2d0405c981240ed593673b0` acredita F2 con el código
final: tres intentos reales, 18 detecciones, mismo evento anotado y pausa congelada.
La ejecución se detuvo al terminar; el servicio quedó disponible sin productor activo.
F7 no se ejerció en ese run ni en S4: está acreditado por el run de revisión real
y el recorrido `http-e875c88699ad42e7a533beaa51731017`; los campos no observados
permanecen explícitos en sus reportes, sin convertirlos en éxitos.

## Evidencias anteriores

Se conservan los 106 archivos protegidos del manifiesto preexistente. El índice de
la primera versión y sus resultados C1/C2 no se actualizaron: describen esa versión.
El lote preliminar `batch-337fccf17c184ce4930c12a5a7c76961` también se conserva,
pero no sustituye al lote final seleccionado arriba.
