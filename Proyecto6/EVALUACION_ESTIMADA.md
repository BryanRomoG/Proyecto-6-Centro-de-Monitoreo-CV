> Copia pública derivada: los enlaces a registros locales se sustituyeron por notas explícitas. El original se conserva.

> Actualización vigente: grupo O2026_ESI3906B, suite 115 +2 Edge; ver [informe de publicación](INFORME_PUBLICACION.md), [política segura](Docs/PUBLICACION_SEGURA.md) y [matriz pública](evidencias/publicacion_segura/evaluacion-publica.json). Las cifras previas del cuerpo describen el cierre anterior; esta actualización no es una nota oficial.

# Evaluación interna estimada · Proyecto 6

**Bryan Edgardo Romo Gonzalez · 745268 · entrega individual, ITESO.**
Profesor Victor Hugo Martinez Sanchez. Entrega 13/11/2026. Grupo: **O2026_ESI3906B**.
[Ficha académica](Docs/IDENTIDAD.md), [guía oficial](Docs/guia-proyecto-6.html) y
[rúbrica oficial](Docs/prompt-evaluacion-proyecto-6.md), ambas conservadas byte por byte.

**Estimación local: base 100 + extras 266 = 366 puntos sustentados.**
Extras F=120, M=90, S=56. Puntos técnicos pendientes en esta matriz: 0.
La calificación oficial sigue **PENDIENTE del profesor**. No hay tope global de extras,
normalización ni compuerta. Los niveles de un mismo adicional no se apilan. Esta cifra
no es una nota otorgada y no implica que todos los niveles máximos sean elegibles.

## Alcance y límites

Se evalúa el árbol de trabajo local actual, con manifiesto de archivos y pruebas,
partiendo de HEAD `0b0a7b459d299e4741753e08f4c7133da65f76f4`. Los cambios actuales
no están en ese commit. La identidad del código probado (registro local o recurso regenerable; consultar el índice público)
relaciona ambos estados; no se afirma que el commit previo incluya revisión manual.
Una revisión exclusiva del remoto/commit anterior debe comprobar su propia cobertura.
No se inventa un requisito de push o cámara para la evaluación funcional local.

La publicación permanece condicionada a la [selección Git](Docs/PLAN_GIT.md): rutas
personales en metadatos históricos, licencia fotográfica individual del ejemplo antiguo,
autorización de commit/push. El grupo ya está confirmado: O2026_ESI3906B. Son pendientes de
publicación, separados de la evidencia local sustentada; no se suman puntos por ellos.
No se realizó clone remoto, CI remoto, ensayo prolongado ni evaluación de calidad.

## Base R1–R7

| ID | Máximo | Sustentado | Pendiente | No otorgado | Fundamento |
| --- | --- | --- | --- | --- | --- |
| R1.1 | 5 | 5 | 0 | 0 | Fuente progresiva con frecuencia declarada; imágenes y video reales. |
| R1.2 | 5 | 5 | 0 | 0 | ONNX CPU, raw outputs/PNG/IDs; replay actual exacto del perro y pruebas reales. |
| R1.3 | 5 | 5 | 0 | 0 | Descriptor SHA, 80 clases COCO, letterbox 416 BGR NCHW float32 0–255, runtime identificado. |
| R2 | 25 | 25 | 0 | 0 | G=7, M1–M5 completos por grupo: 25×35/(5×7)=25. |
| R3.1 | 5 | 5 | 0 | 0 | Piso 0.10 < inferior 0.60 < superior 0.80; justificación con referencia observada. |
| R3.2 | 5 | 5 | 0 | 0 | low/doubt/accepted conservadas, NMS 0.45, candidatas y frames sin detecciones explícitos. |
| R3.3 | 5 | 5 | 0 | 0 | Ventanas de 5 frames, mínimo 5 detecciones, 2 ventanas de referencia y 2 persistentes; insuficiencia distinta de normalidad. |
| R4.1 | 5 | 5 | 0 | 0 | IDs, tiempos, fuente, modelo, config, estado, detecciones/capturas e integridad. |
| R4.2 | 5 | 5 | 0 | 0 | SQLite, reinicio y consultas reales en Eventos y detalle. |
| R4.3 | 5 | 5 | 0 | 0 | PNG sin TTL, SHA conservado; cero archivos declarados faltantes en auditoría actual. |
| R5.1 | 5 | 5 | 0 | 0 | Reglas por frame y cambio sostenido; ventanas, datos mínimos y ausencia definidas. |
| R5.2 | 5 | 5 | 0 | 0 | Alertas reales C2/S4/datasets con reglas, configuración y eventos vinculados. |
| R5.3 | 5 | 5 | 0 | 0 | Consulta web con momento, motivo, severidad y acción sugerida; originales persistidos. |
| R6.1 | 5 | 5 | 0 | 0 | C1 real: 10 frames/76 detecciones/10 alertas; normalidad técnica, sin forzar salud de confianza. |
| R6.2 | 5 | 5 | 0 | 0 | C2 real: 10 frames/65 detecciones/10 alertas; scores y umbrales conservados. |
| R7.1 | 2 | 2 | 0 | 0 | README, lock, scripts, fuentes locales, configuración y comandos; instalación y suite en venv independiente. |
| R7.2 | 2 | 2 | 0 | 0 | Paquetes/índices accesibles, recálculo de 22 paquetes, HEAD previo + manifiesto exacto del árbol probado. La evaluación local incluye los cambios sin commit. |
| R7.3 | 1 | 1 | 0 | 0 | Autoría individual identificada, asistencia declarada, adaptaciones P5, modelo/dataset ajenos atribuidos. |


Los máximos suman 100; sustentados + pendientes + no otorgados = 100. Cada crédito
se vincula al índice de cumplimiento (registro local o recurso regenerable; consultar el índice público), datos primarios,
recálculos, contratos de pruebas y recorridos reales. No se usa un extra para compensar
un grupo obligatorio. Los límites de publicación no se presentan como resultados de
un clone público que no se ejecutó.

### R2: todos los grupos aplican

Hay inferencia (G1), lectura/muestreo (G2), proceso CPU/RAM (G3), predicciones (G4),
persistencia/capturas (G5), fuentes versionadas (G6) y alertas (G7). No hay exclusiones.

| Grupo | Base / población | M1 | M2 | M3 | M4 | M5 |
| --- | --- | --- | --- | --- | --- | --- |
| G1 | Inferencia media (ms) | 1 | 1 | 1 | 1 | 1 |
| G2 | FPS de procesamiento | 1 | 1 | 1 | 1 | 1 |
| G3 | RSS medio (MiB) | 1 | 1 | 1 | 1 | 1 |
| G4 | Proporción baja | 1 | 1 | 1 | 1 | 1 |
| G5 | Cobertura de trazabilidad | 1 | 1 | 1 | 1 | 1 |
| G6 | Antigüedad último frame (s) | 1 | 1 | 1 | 1 | 1 |
| G7 | Alertas abiertas | 1 | 1 | 1 | 1 | 1 |


`R2 = 25 × 35 / (5 × 7) = 25`. No redondear 25/7 por fila. M1 es definición/unidad/
fórmula/población/ventana; M2 adquisición instrumentada; M3 cálculo y ausencias; M4
IDs/observaciones; M5 resultado y recálculo. Las definiciones completas están en
[METRICAS](METRICAS.md). Se recalcularon 22 paquetes; el verificador G1–G7 tiene
fórmulas independientes y tests aritméticos conocidos. El recálculo de extras comparte
agregador y se complementa con tests aritméticos; no se presenta como otro instrumento.

R3 conserva s<0.60 baja, 0.60<=s<0.80 duda, s>=0.80 aceptada por política, piso 0.10,
NMS 0.45. Los vacíos y fallos son estados separados. Ventanas 5 frames, mínimo 5
detecciones, 2 de referencia, aumento 0.20 por 2 ventanas. No se usa confianza como acierto.
C1 y C2 permanecen separados: C1 también tiene alertas legítimas por scores débiles.

## Funcionalidades adicionales

| ID | Función | Reclamado | Demostrado | Estimado | Pendiente | Complejidad y control de doble conteo |
| --- | --- | --- | --- | --- | --- | --- |
| F1 | Dashboard avanzado | 10 | 10 | 10 | 0 | Contadores, snapshot y procedencia por run; consulta parametrizada y estados sin datos. No se cuentan las consultas mínimas de eventos/alertas como dashboard. |
| F2 | Reproducción con detecciones | 15 | 15 | 15 | 0 | Coordina productor, pausa/reanudación, frame anotado por ID, progreso y cambio de fuente; borde de frame viejo corregido y probado. Los controles se acreditan aquí; F8 acredita registro/validación de medios. |
| F3 | Gráficas históricas | 10 | 10 | 10 | 0 | Nueve gráficas de datos persistidos, fechas/run, series separadas y huecos sin interpolar; recuentos verificados. Las nueve gráficas son una función; las métricas tienen su prueba propia. |
| F4 | Filtros avanzados | 10 | 10 | 10 | 0 | Consultas combinadas de eventos/alertas, orden, fechas/zonas/clase y páginas; misma detección satisface clase/score/zona. No se cobra otra función por el filtro de colección ni por cambiar parámetros. |
| F5 | Galería y distribución de capturas | 15 | 15 | 15 | 0 | Coordina miniaturas/caché, cuatro solicitudes, cancelación, reintento, estados faltantes y ZIP con atribución; normal/fallo probados en Edge. La conservación obligatoria R4 no da este bono; filtros F4 no se suman otra vez. |
| F6 | Exportación parametrizada | 10 | 10 | 10 | 0 | CSV/JSON filtrados de seis tipos, unidades y protección frente a fórmulas; filas y descarga nativa CSV/ZIP verificadas. CSV y JSON son un flujo; el ZIP de imágenes pertenece a F5. |
| F7 | Gestión del ciclo de alertas | 15 | 15 | 15 | 0 | Estados persistidos, versiones, comentarios, idempotencia y concurrencia; sin reescribir alerta original. No se cobra la consulta mínima R5; F10 acredita decisión sobre cada detección. |
| F8 | Registro y validación de fuentes | 10 | 10 | 10 | 0 | Registro persistido, rutas permitidas, manifiesto de entrada, duplicados, corrupción, historial y selección entre colecciones. No se vuelve a cobrar pausa/reanudación F2. No se solicita 15 por el simple selector. |
| F9 | Adquisición selectiva pública | 10 | 10 | 10 | 0 | CLI reproducible, presupuesto, licencia por fila, integridad, hash perceptual, omisiones y reuso sin descarga; registro visible en portal. Una adquisición de 80 originales; no ocho funciones ni un bono por fotografía. |
| F10 | Revisión individual de detecciones | 15 | 15 | 15 | 0 | Decisiones humanas versionadas, original frente a validada, historial, conflictos, reinicio real, imagen ausente y vínculo de gestión de alerta. F9 ya existía para adquisición. La semántica de revisión es independiente de galería/alertas; no se cobra cada subcontrol. |


F9 conservó su identidad de adquisición; la nueva revisión usa F10. No hay diez
funciones nuevas en esta intervención: se auditan nueve previas y una añadida. F5
se propone en 15 por coordinación de imágenes/solicitudes/errores verificada; F1/F3/
F4/F6/F8/F9 se conservan en 10 sin presumir una complejidad máxima por cantidad de código.

## Métricas adicionales

| ID / grupo | Indicador | Reclamado | Demostrado / estimado | Pendiente | Paquete decisivo | Control |
| --- | --- | --- | --- | --- | --- | --- |
| M01 / G1 | Distribución de latencia | 5 | 5 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Una familia p50/p95; no un bono por percentil. |
| M02 / G1 | Tasa de errores técnicos | 5 | 5 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Indicador distinto; no un bono por fuente, clase, ventana o gráfico. |
| M03 / G2 | Descartes por muestreo | 3 | 3 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Indicador distinto; no un bono por fuente, clase, ventana o gráfico. |
| M04 / G2 | FPS de lectura | 5 | 5 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Indicador distinto; no un bono por fuente, clase, ventana o gráfico. |
| M05 / G2 | Fallos de lectura | 3 | 3 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Indicador distinto; no un bono por fuente, clase, ventana o gráfico. |
| M06 / G3 | CPU del productor | 5 | 5 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Indicador distinto; no un bono por fuente, clase, ventana o gráfico. |
| M07 / G3 | Pico RSS muestreado | 0 | 0 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Mismo RSS de G3; informativa, sin bono. |
| M08 / G4 | Distribución por clase | 5 | 3 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Conteos por clase: se acredita 3 conservadoramente, no 5 solo por llamarlos distribución. |
| M09 / G4 | Histograma de confianza | 5 | 5 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Indicador distinto; no un bono por fuente, clase, ventana o gráfico. |
| M10 / G4 | Frames sin detecciones | 5 | 5 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Indicador distinto; no un bono por fuente, clase, ventana o gráfico. |
| M11 / G4 | Detecciones por imagen | 5 | 5 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Indicador distinto; no un bono por fuente, clase, ventana o gráfico. |
| M12 / G4 | Proporción de duda | 5 | 5 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Indicador distinto; no un bono por fuente, clase, ventana o gráfico. |
| M13 / G5 | Entradas inválidas | 5 | 5 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Indicador distinto; no un bono por fuente, clase, ventana o gráfico. |
| M14 / G5 | Cobertura de imágenes | 5 | 5 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Indicador distinto; no un bono por fuente, clase, ventana o gráfico. |
| M15 / G6 | Actividad por fuente y ejecución | 3 | 3 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Indicador distinto; no un bono por fuente, clase, ventana o gráfico. |
| M16 / G7 | Alertas por tiempo observado | 5 | 5 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Indicador distinto; no un bono por fuente, clase, ventana o gráfico. |
| M17 / G7 | Tiempo medio de reconocimiento | 5 | 5 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Indicador distinto; no un bono por fuente, clase, ventana o gráfico. |
| M18 / G7 | Tiempo medio de resolución de alerta | 5 | 5 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Indicador distinto; no un bono por fuente, clase, ventana o gráfico. |
| M19 / G7 | Alertas repetidas | 5 | 5 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Indicador distinto; no un bono por fuente, clase, ventana o gráfico. |
| M20 / G4 | Distancia KS de scores frente a referencia | 8 | 8 | 0 | Datos (registro local o recurso regenerable; consultar el índice público) | Comparación de CDF con referencia, distinta de G4 y de histograma M09. |


Por cada M, el JSON de evaluación (registro local o recurso regenerable; consultar el índice público) incluye
grupo, fórmula, unidad, población/ventana, instrumento, observaciones, ausencia,
resultado concreto, paquete, recálculo, riesgos y trabajo faltante. El contrato
[metric_specs.py](src/monitor_cv/metric_specs.py) es consumido por las exportaciones.
M07 es informativa (0) por compartir RSS con G3. M08 solicita 5 en el inventario previo,
pero aquí recibe 3 por conteos segmentados simples: los 2 puntos restantes **no se
cuentan como pendientes ni acreditados**. M01 es una familia de percentiles. M04 mide
lectura de frames incluidos descartes, mientras G2 mide procesamiento exitoso.
M14 es existencia de captura/decodificados, G5 además integridad de metadatos y SHA.
M17/M18 tienen tiempos humanos reales de 108.4104869 y 167.551718 s en su paquete,
sin afirmar recuperación del servicio. M20 compara distribuciones contra referencia;
KS no prueba drift, independencia estadística ni calidad predictiva.

## Escenarios adicionales

| ID | Nivel reclamado/demostrado | Pendiente | Condición, reacción y evidencia |
| --- | --- | --- | --- |
| S1 | 10 | 0 | Archivo ausente entre lecturas; restauración en finally y continuidad. ok → source_error → ok → ok; diagnóstico de lectura, dos inferencias posteriores y capturas íntegras. |
| S2 | 5 | 0 | Escena sin detecciones reales. Tres no_detections, cero detecciones/alertas; sin score artificial. |
| S3 | 5 | 0 | Poco tráfico y evidencia insuficiente. Una muestra, ninguna ventana completa, insufficient_evidence. |
| S4 | 8 | 0 | Cambio sostenido y retorno a referencia. Cinco ventanas: referencia ×2, pendiente, sostenido, dentro de política; KS null/null/0.8/0.8/0. |
| S5 | 10 | 0 | Bytes recibidos corruptos y continuidad. ok → decode_error → ok; diagnóstico, omisión controlada y PNG/inferencia posterior verificados. |
| S6 | 8 | 0 | Cambio de configuración persistido sin mezclar series. Dos runs, superior 0.80/0.85, mismo modelo/scores y hashes diferentes. |
| S7 | 10 | 0 | Fallo técnico controlado del adaptador y recuperación. ok → inference_error → ok → ok; fallo INYECTADO, ONNX real antes/después y diagnóstico/captura conservados. |


Los [escenarios](Docs/ESCENARIOS.md) describen preparación, configuración, comandos,
IDs, expectativas y resultados. S1/S5/S7 se proponen en 10 al verificar explícitamente
fallo, diagnóstico/reacción, continuidad/recuperación e inferencias/capturas posteriores;
los estados no se fabrican. S7 solo simula una excepción técnica y la etiqueta como tal.
S4 sigue en 8: cambio temporal y recuperación sin afirmar fallo predictivo. S6 compara
configuración, no pretende otro modelo. El video complementario no cuenta como S8.

## Evidencia, incidencias y recomendaciones

Ver índice final (registro local o recurso regenerable; consultar el índice público), [informe organizado](ENTREGA_FINAL.md)
y pruebas (registro local o recurso regenerable; consultar el índice público). Se conserva el antecedente
del estudiante 87 passed/1 warning/49.08 s, distinto de la línea base observada nueva.
Se preservan también los intentos fallidos: la primera navegación agotó su espera de
históricos; se corrigió el N+1 de alertas y se repitió correctamente. La primera
comparación de replay del auditor confundió tuplas/listas de cajas; la serialización
JSON canónica confirmó valores exactamente iguales, sin cambiar resultados del modelo.

Prioridad antes de entregar: revisar selección/licencias y metadatos de publicación;
mantener el grupo confirmado O2026_ESI3906B; recorrer las pantallas; autorizar y vincular una revisión
Git definitiva si procede; verificar acceso desde ese commit en otra máquina. No se
añaden bonos decorativos ni se llena SQLite con repeticiones para aumentar cifras.

## Complemento público y representación de bytes

C1_PUBLIC/C2_PUBLIC se ejecutaron en SQLite aislado sobre 20 fotos ya incluidas en
los 80 originales, con política idéntica y rutas relativas. Se observaron 161/86
detecciones y 10/9 alertas. No suman otro escenario ni nuevas fotografías. El
índice (registro local o recurso regenerable; consultar el índice público) permite recalcularlos y ver el recorrido
Edge. Ofrecen una alternativa al ejemplo legado con licencia fotográfica pendiente.

El mapa de revisión (registro local o recurso regenerable; consultar el índice público) registra SHA de los
bytes locales, representación LF y contenido HEAD: había 12 archivos con CRLF en
la muestra de 71. No se normalizaron originales ni se cambiaron hashes antiguos.
Git puede representar texto como LF; una igualdad semántica tras normalización no
se presenta como igualdad de bytes. Las imágenes y pesos conservan sus SHA exactos.

La descarga nativa CSV detectó un enlace SSR inicialmente sin filtros. Se corrigió
la generación del servidor y se añadieron dos regresiones (Eventos/Alertas), además
del recorrido Edge. Los filtros por un run desconocido conservan el valor y muestran
cero resultados, sin ampliar silenciosamente la consulta durante la inicialización.


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
