# Manual de usuario

Edición actual: [revisión humana](Docs/REVISION_MANUAL.md),
[cierre y evidencias](ENTREGA_FINAL.md). Identificación académica definitiva en
[IDENTIDAD](Docs/IDENTIDAD.md); grupo confirmado O2026_ESI3906B.

## Revisar una detección y gestionar su alerta

En Galería abre el evento y pulsa **Revisar detecciones individualmente**. Selecciona
la detección por ID, el estado humano, motivo y actor local; si corriges la etiqueta,
escribe la clase revisada. Guardar conserva el score y etiqueta originales. La tabla
separa estado humano y predicción; el selector de vista alterna cajas originales con
las confirmadas/corregidas. Las pendientes y falsos positivos no aparecen como validadas.

El historial muestra cada cambio. Una recarga o reinicio conserva las revisiones.
Si otro revisor guardó primero, pulsa Actualizar revisión antes de decidir de nuevo.
Sin detecciones no hay nada que confirmar; sin imagen íntegra la validación se bloquea.
La advertencia de superposición no afirma que dos cajas sean el mismo objeto.

Desde la revisión abre una alerta vinculada. Selecciona motivo, revisiones pertinentes
y comentario; Reconocer y después Resolver. Resolver cierra la gestión, sin borrar la
alerta ni afirmar que la condición automática de baja confianza fuera errónea. El
[caso perro/gato](Docs/REVISION_MANUAL.md) conserva las dos predicciones originales
y muestra solo el perro en la capa humana. No se requiere cargar fotografías manualmente.

## Colecciones públicas incorporadas en 0.3

En Fuentes aparecen ocho colecciones nuevas de diez fotografías distintas cada una.
No hay que subir imágenes: se adquieren con el [descargador documentado](Docs/DATASETS.md).
Seleccionar la colección, configurar frames/s e Iniciar. Reproducción permite pausar,
continuar y detener; detener antes de cambiar de fuente. El enlace “Historial de esta
fuente” muestra sus runs; “Capturas de esta colección” abre los filtros de la galería.

En Galería, “Colección prevista” describe cómo se seleccionó una imagen. “Clase COCO”
y “Zona” consultan las salidas reales. Una colección puede tener treinta capturas
de tres ejecuciones de sus diez originales: no son treinta fotografías diferentes.
Aplicar filtros, pasar de página y refrescar conserva la consulta. Las imágenes
completas solo se solicitan al abrirlas; las miniaturas se cargan al entrar en pantalla.
Si falla una consulta o miniatura aparece Reintentar. Los errores de lectura y
decodificación sin captura tienen un detalle explícito y no cuentan como imágenes.
El ZIP de capturas de dataset incluye atribución; conservarla junto a los archivos.

El portal trabaja con **archivos locales**, no con una cámara. Las predicciones no
se editan. Los nombres de clase se conservan tal como los publica COCO.

## Registrar y reproducir

1. Preparar modelo/medios con el [README](README.md) e iniciar el servidor.
2. Abrir **Fuentes**. Registrar nombre, tipo imágenes/video, ruta dentro de un directorio
   permitido y muestreo. El servidor valida existencia, tipo y posibilidad de decodificar.
   No introducir URLs ni rutas fuera de las raíces que muestra Configuración.
3. Seleccionar fuente en el desplegable. Elegir frecuencia y si se repite; pulsar Iniciar.
   La configuración queda fijada para esa ejecución, con ID y hash propios.
4. Abrir **Reproducción**. El frame, las cajas y la tabla comparten un ID de evento.
   Rojo indica baja confianza, ámbar duda y verde aceptación por política.
5. Pausar conserva el último frame y suspende nuevos intentos. Continuar mantiene la
   misma ejecución; Detener la finaliza. Para cambiar de fuente, detener e iniciar otra.
6. El fin del archivo se muestra como Finalizada. Un frame ilegible aparece como error
   técnico; no recibe confianza cero. Puede seguir el siguiente frame de una secuencia.
   Si el archivo completo es inválido, corregirlo o seleccionar otro e iniciar de nuevo.

Las opciones de fuente/muestreo se bloquean durante ejecución o pausa para evitar que
la selección visual contradiga la fuente que realmente se procesa.

## Consultar y filtrar

**Dashboard** actualiza por polling. Informa éxito técnico, errores, FPS, latencia,
RAM, detecciones, eventos, alertas sin resolver, actividad y referencia temporal.
Los valores de último snapshot se identifican con fecha: no se presentan como actuales
cuando el replay ya terminó y la ventana móvil no contiene muestras.

**Eventos** permite ID, fechas locales, fuente, ejecución, clase, zona, estado y rango
de puntuaciones. Los filtros de clase/zona/rango deben cumplirse en una misma detección,
no en detecciones diferentes del frame. Aplicar, cambiar orden o usar Anterior/Siguiente.
El detalle conserva configuración, candidatas, resultados e imagen. No hay etiquetas de
verdad ni autorización para corregir una puntuación desde la interfaz.

**Alertas** permite ID, fecha, regla, severidad, estado, ejecución y evento de origen.
Abrir una alerta y seguir el enlace al evento y su imagen. Las listas muestran vacíos
explícitos; una consulta inválida muestra error, no resultados inventados.

## Gestionar alertas

En el detalle de una alerta abierta, añadir una nota y pulsar **Reconocer**. Solo después
se habilita **Resolver**. Se pueden añadir comentarios en cualquier estado. Cada acción
conserva fecha, versión, comentario y estado anterior/nuevo. Un conflicto de versión
solicita actualizar la vista, evitando sobrescribir la revisión de otro cliente.

Reconocida sigue contando como sin resolver en G7. Resuelta deja de contarse desde el
instante de resolución. El historial permite reconstruir cortes anteriores. El evento,
la captura y las puntuaciones no se modifican. Resolver una revisión no significa que
el modelo sea correcto ni que un incidente físico se haya recuperado.

Todos los controles se pueden activar mediante teclado. El recorrido de evidencia
incluye una resolución con Enter después de enfocar el botón.

## Galería, históricos y exportaciones

**Galería** filtra capturas reales por clase, fecha, ejecución y otras condiciones de
evento. Alternar cajas, abrir original, consultar evento/alertas y descargar original
o una selección ZIP. Se rechazan rutas inválidas, referencias ausentes y selecciones
por encima de 100 IDs/50 MiB. Las capturas exigidas no caducan automáticamente.

**Métricas e históricos** ofrece nueve gráficos. Seleccionar ejecución/período y
agrupación de tiempo. Hover o foco de teclado muestra observación e ID. Los puntos
son registros reales: una ventana sin suficientes muestras muestra ese estado. La
referencia de confianza es fija por ejecución; comparar distribuciones no confirma drift.
Seleccionar todas las ejecuciones mantiene separadas las series y los indicadores por run.

**Exportar CSV/JSON** descarga todas las coincidencias, no solo la página visible.
Eventos y alertas respetan sus filtros. Métricas y ventanas se exportan completas por
ejecución/fecha; filtrar una clase no fracciona retroactivamente un agregado persistido.
Indicadores adicionales sí se recalculan sobre su selección y declaran IDs/población.
El CSV neutraliza fórmulas de texto; conservar JSON para fidelidad de tipos y estructuras.

**Ejecuciones** enlaza fuente, modelo y consulta por ID. **Configuración** es una vista
del estado efectivo y raíces permitidas; los cambios globales se realizan en YAML/.env
con el servidor detenido. No hay botón de guardar decorativo.


## Actualización para publicación segura

Grupo confirmado **O2026_ESI3906B**, [Canvas](https://canvas.iteso.mx/courses/57431).
La selección pública y sus límites vigentes se describen en [PUBLICACION_SEGURA](Docs/PUBLICACION_SEGURA.md)
y el [índice GitHub](evidencias/publicacion_segura/INDICE_GITHUB.md). Hay 80 fotografías
locales conservadas y 79 seleccionadas para distribución/reproducción pública; una
se omite por contacto en su atribución, sin modificar el original. C1/C2, video y S1–S7
tienen alternativas reales con licencia identificada. Los 366 puntos son estimados,
no calificación oficial. Los archivos antiguos ya públicos requieren una decisión
posterior sobre la selección Git; no se ejecutó add, commit ni push.
