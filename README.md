# Proyecto 6 · Centro de monitoreo de computer vision

Repositorio de entrega individual, ITESO. Nombre académico y matrícula pendientes de confirmación.
El desarrollo actual está en [Proyecto6](Proyecto6/README.md): imágenes o video local
→ YOLOX-Nano CPU → métricas, eventos, capturas, alertas → portal en español.
No requiere cámara física ni carrito.

| Carpeta | Contenido |
| --- | --- |
| Proyecto1 | Antecedente: portal de anotación. |
| Proyecto2 | Antecedente: calidad y versionado de datos. |
| Proyecto3 | Antecedente: clasificador y entrenamiento. |
| Proyecto4 | Antecedente: cámara e inferencia edge. |
| Proyecto5 | Antecedente: detector YOLOX-Nano y ESP32-CAM; consultado sin modificar. |
| [Proyecto6](Proyecto6/README.md) | Aplicación autónoma de monitoreo y evidencias. |

Los antecedentes conservan sus archivos, instrucciones y reglas locales de exclusión.
No son dependencias de ejecución de Proyecto6. Los modelos se obtienen mediante
descarga verificada; no se copian datasets completos ni entornos anteriores.
Los archivos locales, credenciales, cachés y modelos pesados se excluyen desde la raíz.
Las imágenes seleccionadas de Proyecto6/evidencias pueden incorporarse a Git.

Consulta [instalación y comandos](Proyecto6/README.md),
[matriz R1–R7 actual](Proyecto6/evidencias/ampliacion/cumplimiento.md),
[procedencia](Proyecto6/PROCEDENCIA.md) y [métricas](Proyecto6/METRICAS.md).
La [entrega ampliada](Proyecto6/ENTREGA_AMPLIACION.md) incluye resultados de pruebas,
escenarios y el [inventario de extras](Proyecto6/Docs/EXTRAS.md). Las evidencias de
la primera versión se conservan junto con las nuevas ejecuciones, sin sobreescribirlas.

La [ampliación de datasets](Proyecto6/ENTREGA_DATASETS.md) añade 80 fotografías
distintas de Open Images, ocho colecciones y una galería paginada con miniaturas.
Consultar [procedencia, licencias y reproducción](Proyecto6/Docs/DATASETS.md).

Los workflows heredados se conservan para ejecución manual. El CI de Proyecto6
no requiere AWS, Docker ni servicios de los antecedentes.
Antes de cualquier commit, ejecutar `Proyecto6/scripts/audit_repository.py` y revisar
privacidad de las imágenes seleccionadas. No se prepararon commits ni se enviaron cambios.
