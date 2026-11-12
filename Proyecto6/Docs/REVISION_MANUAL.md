> Copia pública derivada: los enlaces a registros locales se sustituyeron por notas explícitas. El original se conserva.

# Revisión humana por detección

La demostración de cierre fue asistida por Codex con inspección visual y acciones
reales en Edge bajo el actor `revisor-local`. No se registra como firma personal
del estudiante ni como etiqueta de verdad para evaluar calidad predictiva.

Desde **Eventos → abrir evento → Revisar detecciones individualmente** se muestran
la captura, cajas, predicciones, scores y zonas originales, IDs de evento/detección,
fuente, fecha, ejecución, modelo, configuración y alertas vinculadas. La galería
enlaza con ese mismo evento. No se necesita una nueva inferencia para revisar.

1. Seleccionar una detección por su clase e ID.
2. Elegir Pendiente, Confirmada, Falso positivo o Etiqueta corregida manualmente.
3. Solo para corrección, escribir la nueva etiqueta; la original se conserva.
4. Explicar el motivo, usar un actor local y guardar.
5. Cambiar la vista a **Solo detecciones validadas por revisión humana**. Esta capa
   incluye confirmadas/corregidas, excluye pendientes/rechazadas y no inventa scores.
6. Volver a Predicciones originales: permanecen todas las detecciones iniciales.
7. Abrir una alerta vinculada, seleccionar motivo y las revisiones correspondientes,
   comentar, reconocer y resolver. Una resolución conserva la condición automática.

## Caso real documentado

Evento `evt-37c2579bd3af445fb8a683807642e8ee`, ejecución
`run-2716c09f7fe7419994bf45a5c91a19e7`, imagen Open Images `488d4412c71bf3f1`.
Autor Marco, [original](https://www.flickr.com/photos/ggould75/731829314),
[CC BY 2.0](https://creativecommons.org/licenses/by/2.0/).

| Predicción original | Score inmutable | Zona | Resultado de revisión |
| --- | ---: | --- | --- |
| dog | 0.6565653975020709 | Duda | Confirmada por observación visual de un perro |
| cat | 0.17536601693758413 | Baja confianza | Falso positivo; caja sobre el mismo perro |

La advertencia de solapamiento usa IoU geométrico >=0.5. No evalúa calidad, no borra
cajas, no decide identidad de objetos y no modifica NMS. La capa validada muestra
solo `dog`. La API original y el SHA-256 del PNG se comprobaron sin cambios.

Alerta `alert-75e89e2ac05841dda4ebc8dc04347dea`, reconocida y resuelta por la interfaz
con revisión vinculada y motivo explícito. La condición automática de baja confianza
fue real y sigue siendo válida históricamente. Confirmar un perro no aumenta su score.

El índice final (registro local o recurso regenerable; consultar el índice público) enlaza el recorrido Edge y el
reinicio real. En la base local actual: abrir `/events/<ID>/review`. En una copia nueva,
esos IDs históricos no aparecen automáticamente: reproducir la colección animales y
abrir su imagen `488d4412c71bf3f1`, que tendrá un ID nuevo. No importar eventos como
si fueran inferencias nuevas. El paquete original sigue siendo recalculable sin DB.

## Persistencia, límites y contratos

SQLite añade `detection_reviews`: cada fila es una revisión inmutable con UUID,
evento, detección, índice original, clase original, clase corregida opcional, hash de
la detección original, estado, motivo, actor, fecha, versión, revisión previa y
request_id único. Los IDs de detección derivan de evento+índice de la lista original;
no se reescriben eventos antiguos para agregarlos. No hay UPDATE/DELETE de revisiones.

Una transacción `BEGIN IMMEDIATE` y la versión esperada impiden pisar otra revisión.
Reenviar el mismo request_id y contenido devuelve la misma revisión; reutilizarlo con
otro contenido da conflicto. La interfaz bloquea clics simultáneos y conserva la clave
de reintento si falla la respuesta. Recargar consulta el estado persistido.

Sin detecciones se muestra un estado vacío. Sin captura íntegra se permite consultar
el historial, pero guardar una validación visual devuelve 409. IDs desconocidos dan
404, contratos inválidos 422 y conflictos 409. No existe autenticación de actores:
uso local, sin atribuir firma o permisos de un sistema multiusuario.

- `GET /api/events/{id}/reviews`: proyección original, revisiones e historial.
- `POST /api/events/{id}/detections/{detection_id}/reviews`: revisión versionada.
- `GET /images/{id}/reviewed`: PNG derivado, no-store y capa humana identificada.
- Cambios de alerta: `reason_code`, `review_ids`, actor y comentario append-only;
  las revisiones deben pertenecer a eventos de la alerta. Validada/falso positivo
  requieren decisiones compatibles. El historial conserva la revisión usada entonces.

Pruebas: [test_reviews.py](../tests/test_reviews.py) y
[test_reviews_portal.py](../browser_tests/test_reviews_portal.py). Las pruebas unitarias
usan fixtures sintéticos declarados; Edge usa el evento y fotografía históricos reales.
F10 es el ID estable nuevo: F9 ya designaba adquisición de datasets. No se reclaman
por separado el formulario, el solapamiento, el historial o la vista validada.


## Selección pública vigente

Ver [publicación segura](PUBLICACION_SEGURA.md) e [índice GitHub](../evidencias/publicacion_segura/INDICE_GITHUB.md): 79 fotos autorizadas para la selección, nuevos C1/C2/S1–S7 reales y copias derivadas con trazabilidad. Los registros anteriores se conservan localmente; no equivalen a bytes aprobados para publicar.
