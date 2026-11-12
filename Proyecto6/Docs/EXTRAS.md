> Copia pública derivada: los enlaces a registros locales se sustituyeron por notas explícitas. El original se conserva.

# Inventario de extras verificado

Referencia actual: [evaluación interna](../EVALUACION_ESTIMADA.md),
matriz estructurada (registro local o recurso regenerable; consultar el índice público) e
índice (registro local o recurso regenerable; consultar el índice público). La calificación oficial está pendiente
del profesor. Se acredita un solo nivel por elemento, sin límite global ni compuerta.

## Funcionalidades

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

F1–F8 son los IDs históricos. F9 ya estaba ocupado por adquisición; F10 corresponde
a revisión de detecciones. No se renumeran evidencias anteriores. Formularios, capas,
advertencias y cambios de alerta no se multiplican como otras funcionalidades.

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

Las observaciones/resultados y los diez campos del contrato están en el JSON enlazado.
Los siete indicadores base se designan primero en [METRICAS](../METRICAS.md).
M07 no solicita bono; M08 se valora conservadoramente en 3 por su cálculo simple.
No se cuentan p50 y p95 separados, ni un bono por clase/run/fuente/ventana.

## Escenarios

| ID | Nivel reclamado/demostrado | Pendiente | Condición, reacción y evidencia |
| --- | --- | --- | --- |
| S1 | 10 | 0 | Archivo ausente entre lecturas; restauración en finally y continuidad. ok → source_error → ok → ok; diagnóstico de lectura, dos inferencias posteriores y capturas íntegras. |
| S2 | 5 | 0 | Escena sin detecciones reales. Tres no_detections, cero detecciones/alertas; sin score artificial. |
| S3 | 5 | 0 | Poco tráfico y evidencia insuficiente. Una muestra, ninguna ventana completa, insufficient_evidence. |
| S4 | 8 | 0 | Cambio sostenido y retorno a referencia. Cinco ventanas: referencia ×2, pendiente, sostenido, dentro de política; KS null/null/0.8/0.8/0. |
| S5 | 10 | 0 | Bytes recibidos corruptos y continuidad. ok → decode_error → ok; diagnóstico, omisión controlada y PNG/inferencia posterior verificados. |
| S6 | 8 | 0 | Cambio de configuración persistido sin mezclar series. Dos runs, superior 0.80/0.85, mismo modelo/scores y hashes diferentes. |
| S7 | 10 | 0 | Fallo técnico controlado del adaptador y recuperación. ok → inference_error → ok → ok; fallo INYECTADO, ONNX real antes/después y diagnóstico/captura conservados. |

Reproducción y límites en [ESCENARIOS](ESCENARIOS.md). Datos primarios C1/C2/S1–S7 y
video en lote histórico (registro local o recurso regenerable; consultar el índice público). El índice final enlaza los
22 paquetes recalculados. Las pruebas reales nuevas usan almacenamiento aislado.

Totales internos sustentados: F=120, M=90, S=56; extras=266. No son puntos
otorgados por el docente. Pendientes técnicos contabilizados: 0; publicación y
evaluación docente se registran aparte. No se presume nivel 15/8/10 automáticamente.


## Selección pública vigente

Ver [publicación segura](PUBLICACION_SEGURA.md) e [índice GitHub](../evidencias/publicacion_segura/INDICE_GITHUB.md): 79 fotos autorizadas para la selección, nuevos C1/C2/S1–S7 reales y copias derivadas con trazabilidad. Los registros anteriores se conservan localmente; no equivalen a bytes aprobados para publicar.
