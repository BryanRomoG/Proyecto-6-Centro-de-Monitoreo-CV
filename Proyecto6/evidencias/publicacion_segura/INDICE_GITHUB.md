# Índice de evidencia destinada a GitHub

Esta selección pública derivada es distinta del índice local completo. Los originales
permanecen intactos. No hay commit, push ni calificación oficial de esta ampliación.
Código: árbol de trabajo posterior al HEAD padre `0b0a7b459d299e4741753e08f4c7133da65f76f4`;
cada ejecución conserva [hashes del código](publico/escenarios/C1/code-sha256.json).
El manifiesto de la copia seleccionada registra sus propios bytes y las transformaciones.

[Matriz interna](evaluacion-publica.json) · [Sanitización e integridad](sanitizacion.json) ·
[Auditoría de privacidad](privacidad.json) · [Verificación aritmética de los once paquetes](verificacion-paquetes.json) ·
[Política de publicación](../../Docs/PUBLICACION_SEGURA.md).

## Requisitos obligatorios

| Criterio | Evidencia pública o reproducción |
| --- | --- |
| R1 | [C1: eventos e inferencias reales](publico/escenarios/C1/events.jsonl), [modelo y configuración](publico/escenarios/C1/run.json); video local en su paquete |
| R2 | [G1–G7](publico/escenarios/C1/metrics.json), [recálculo](publico/escenarios/C1/metric-verification.json), [definiciones](../../METRICAS.md) |
| R3 | [Ventanas de referencia y cambio sostenido](publico/escenarios/S4/windows.jsonl); piso/NMS y dos umbrales fijados en cada evento/config |
| R4 | [Eventos](publico/escenarios/C2/events.jsonl), PNG enlazados por image_ref con SHA, captura disponible distinta de evento técnico |
| R5 | [Alertas reales](publico/escenarios/C2/alerts.jsonl), [gestión y revisión humana](publico/revision/revision-publicable.json) |
| R6 | [C1 autorizado](publico/escenarios/C1/result.json), [C2 autorizado](publico/escenarios/C2/result.json); sustituyen bytes del ejemplo dog.jpg, no reescriben casos históricos |
| R7 | [Instalación](../../Docs/PUBLICACION_SEGURA.md), [procedencia](../../PROCEDENCIA.md), [recursos externos](../../config/dataset-selection-public.json), hashes por ejecución. Publicación/CI remotos pendientes. |

## Funcionalidades distintas

La navegación se verifica con [pruebas Edge de galería](../../browser_tests/test_portal.py)
y [revisión manual](../../browser_tests/test_reviews_portal.py), sin sustituir respuestas.

| ID | Funcionalidad | Evidencia / reproducción |
| --- | --- | --- |
| F1 | Dashboard | `/`, métricas por ejecución y procedencia; prueba de nueve rutas |
| F2 | Reproducción | `/playback`, [Video](publico/escenarios/Video/result.json), pausa/reanudación real en Edge |
| F3 | Gráficas | `/history`, series de las ejecuciones y distribuciones, filtros por run |
| F4 | Filtros | `/events`, `/alerts`, `/gallery`; pruebas de filtro y exportación nativa |
| F5 | Galería | Paginación SQL, miniaturas, cola <=4, errores/reintento; prueba Edge |
| F6 | Exportación | CSV/JSON filtrados, ZIP y atribución comprobados; no se cuenta de nuevo la galería |
| F7 | Gestión de alertas | [Historial original y resolución](publico/revision/revision-publicable.json) |
| F8 | Registro de fuentes | `/sources`; ocho colecciones, frecuencias y controles, ejecuciones distintas |
| F9 | Adquisición | [Script](../../scripts/download_demo_dataset.py), [79 créditos intactos](../../config/dataset-selection-public.json), validación SHA/duplicados/licencias |
| F10 | Revisión por detección | [Dog confirmado y cat rechazado](publico/revision/revision-publicable.json), [captura sin alterar](publico/revision/evt-37c2579bd3af445fb8a683807642e8ee.png), [atribución](publico/revision/ATTRIBUTION.json) |

## Métricas adicionales

Todas mantienen fórmula/unidad/instrumentación/ausencia en la matriz. M07 sigue sin
bono; M08 mantiene el nivel conservador de 3. Las capas humanas no alteran scores.

| Métrica | Resultado, observaciones y reproducción |
| --- | --- |
| M01 · Distribución de latencia | [Datos y resultado](publico/escenarios/C1/extras.json); 5 puntos estimados |
| M02 · Tasa de errores técnicos | [Datos y resultado](publico/escenarios/S7/extras.json); 5 puntos estimados |
| M03 · Descartes por muestreo | [Datos y resultado](publico/escenarios/Video/extras.json); 3 puntos estimados |
| M04 · FPS de lectura | [Datos y resultado](publico/escenarios/C1/extras.json); 5 puntos estimados |
| M05 · Fallos de lectura | [Datos y resultado](publico/escenarios/S1/extras.json); 3 puntos estimados |
| M06 · CPU del productor | [Datos y resultado](publico/escenarios/C1/extras.json); 5 puntos estimados |
| M07 · Pico RSS muestreado | [Datos y resultado](publico/escenarios/C1/extras.json); 0 puntos estimados |
| M08 · Distribución por clase | [Datos y resultado](publico/escenarios/C1/extras.json); 3 puntos estimados |
| M09 · Histograma de confianza | [Datos y resultado](publico/escenarios/C1/extras.json); 5 puntos estimados |
| M10 · Frames sin detecciones | [Datos y resultado](publico/escenarios/S2/extras.json); 5 puntos estimados |
| M11 · Detecciones por imagen | [Datos y resultado](publico/escenarios/C1/extras.json); 5 puntos estimados |
| M12 · Proporción de duda | [Datos y resultado](publico/escenarios/C1/extras.json); 5 puntos estimados |
| M13 · Entradas inválidas | [Datos y resultado](publico/escenarios/S5/extras.json); 5 puntos estimados |
| M14 · Cobertura de imágenes | [Datos y resultado](publico/escenarios/C1/extras.json); 5 puntos estimados |
| M15 · Actividad por fuente y ejecución | [Datos y resultado](publico/escenarios/C1/extras.json); 3 puntos estimados |
| M16 · Alertas por tiempo observado | [Datos y resultado](publico/escenarios/C2/extras.json); 5 puntos estimados |
| M17 · Tiempo medio de reconocimiento | [Datos y resultado](publico/revision/alert-times.json); 5 puntos estimados |
| M18 · Tiempo medio de resolución de alerta | [Datos y resultado](publico/revision/alert-times.json); 5 puntos estimados |
| M19 · Alertas repetidas | [Datos y resultado](publico/escenarios/C2/extras.json); 5 puntos estimados |
| M20 · Distancia KS de scores frente a referencia | [Datos y resultado](publico/escenarios/S4/extras.json); 8 puntos estimados |

## Escenarios adicionales

| Escenario | Resultado | Evidencia |
| --- | --- | --- |
| S1 | observed=True; Archivo interrumpido produce source_error y siguientes frames reales recuperan el procesamiento | [Resultado](publico/escenarios/S1/result.json) |
| S2 | observed=True; Recorte fotográfico real sin detecciones ni alerta baja | [Resultado](publico/escenarios/S2/result.json) |
| S3 | observed=True; Una muestra no completa la ventana ni declara normalidad | [Resultado](publico/escenarios/S3/result.json) |
| S4 | observed=True; Dos ventanas de referencia, dos de cambio sostenido y recuperación con scores reales | [Resultado](publico/escenarios/S4/result.json) |
| S5 | observed=True; Imagen corrupta genera decode_error y el siguiente frame sigue con ONNX real | [Resultado](publico/escenarios/S5/result.json) |
| S6 | observed=True; No mezclar referencias ni series incompatibles | [Resultado](publico/escenarios/S6-v1/result.json) |
| S7 | observed=True; Fallo controlado identificado, captura/diagnóstico y ONNX real antes/después | [Resultado](publico/escenarios/S7/result.json) |

S6 incluye también [la segunda configuración](publico/escenarios/S6-v2/result.json).
Solo S7 inyecta un fallo técnico, marcado explícitamente; no inyecta detecciones.
[Calibración real y créditos](publico/escenarios/authorized-inputs.json) documenta la
elección de fotos existentes, repeticiones y cero fotografías originales nuevas.
No se cuentan estas alternativas como siete bonos adicionales nuevos.

## Comandos y restricciones

Desde Proyecto6, con Python 3.12 y dependencias instaladas:

```powershell
.\.venv\Scripts\python.exe scripts/download_model.py --destino modelo
.\.venv\Scripts\python.exe scripts/download_demo_dataset.py --selection config/dataset-selection-public.json --max-mb 200
.\.venv\Scripts\python.exe scripts/prepare_authorized_demo.py --output data/media/authorized_demo
$env:P6_TEST_DEMO_DIR='data/media/authorized_demo'
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe scripts/run_authorized_scenarios.py
.\.venv\Scripts\python.exe scripts/verify_metrics.py evidencias/publicacion_segura/publico/escenarios/C1
.\.venv\Scripts\python.exe scripts/verify_extras.py evidencias/publicacion_segura/publico/escenarios/S4
```

El preparador exige un destino vacío; no repetirlo sobre entradas anteriores.
La descarga selectiva reutiliza imágenes verificadas. Requiere red pública HTTPS;
no necesita ESP32-CAM, cuentas, base privada ni carrito. 79 originales seleccionados,
una exclusión por contacto en atribución. Open Images no garantiza derechos de terceros:
[condiciones oficiales](https://storage.googleapis.com/openimages/web/download_v7.html) y
[CC BY 2.0](https://creativecommons.org/licenses/by/2.0/). El modelo se recupera del
[release oficial YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.onnx).

Los hashes del original y de una copia sanitizada pueden ser distintos: el registro
explica campos/rutas eliminados. No se recalcula ni sustituye un hash histórico.
La base local anterior no se distribuye. IDs de nuevas reproducciones serán otros.
Los registros de pruebas y portabilidad del cierre actual se añaden al finalizar su ejecución.

El [mapa de bytes locales/LF/HEAD](git-byte-map.json) distingue hashes de trabajo y
normalización futura de Git, sin alterar originales. [Reinicio real](reinicio.json)
confirma persistencia en la base histórica y en la independiente.


## Verificación de esta selección

[Pruebas finales](pruebas.json), [portabilidad con adquisición real de 79 fotos](portabilidad.json), [integridad de originales](integridad.json), [resultado de 79 inferencias](dataset-79-resultados.json), [Edge galería](navegador/galeria/verification.json) y [Edge revisión](navegador/revision/verification.json). [Estado actual de las tres revisiones históricas](current-review-state.json).
