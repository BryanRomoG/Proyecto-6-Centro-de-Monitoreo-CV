# Índice de evidencias · Proyecto 6

Fecha de revisión local: 2026-11-10. Estudiante: identidad académica completa pendiente de confirmación.
Windows / Python 3.12.10 / ONNX Runtime 1.22.0 CPU. Sin commit inicial autorizado:
la revisión del código se identifica mediante code-sha256.json de cada paquete.
No se otorgan puntos automáticamente ni se sustituye la revisión docente.

## Ejecuciones seleccionadas

### C1 · run-02611233986c44e7bc84a568aff98a87

- [Resultado observado](escenarios/normal/run-02611233986c44e7bc84a568aff98a87/result.json), [ejecución y configuración](escenarios/normal/run-02611233986c44e7bc84a568aff98a87/run.json), [código probado](escenarios/normal/run-02611233986c44e7bc84a568aff98a87/code-sha256.json).
- [Eventos](escenarios/normal/run-02611233986c44e7bc84a568aff98a87/events.jsonl), [alertas](escenarios/normal/run-02611233986c44e7bc84a568aff98a87/alerts.jsonl), [ventanas/referencia](escenarios/normal/run-02611233986c44e7bc84a568aff98a87/windows.jsonl), [imágenes](escenarios/normal/run-02611233986c44e7bc84a568aff98a87/images/).
- [Métricas primarias y resultado](escenarios/normal/run-02611233986c44e7bc84a568aff98a87/metrics.json), [recálculo independiente](metricas/C1-recalculo.json).
- [HTML y verificación HTTP](portal/run-02611233986c44e7bc84a568aff98a87/http-verification.json), [evento en navegador](portal/C1-evento-verificado.png), [alerta en navegador](portal/C1-alerta-verificada.png).
- Muestra trazada: `evt-8dc816d8d72448d2a7ad99bdd77ade9f` → su PNG; alerta `alert-46f7efdb4e2244e784d5711146f8dc08` → ese evento.
- 10 frames exitosos, 10 alertas bajas reales. No se alteraron puntuaciones. C1 también produce alertas conforme a la regla.

### C2 · run-a6497225005a48ba99f7f5b52429ff82

- [Resultado observado](escenarios/baja-confianza/run-a6497225005a48ba99f7f5b52429ff82/result.json), [ejecución y configuración](escenarios/baja-confianza/run-a6497225005a48ba99f7f5b52429ff82/run.json), [código probado](escenarios/baja-confianza/run-a6497225005a48ba99f7f5b52429ff82/code-sha256.json).
- [Eventos](escenarios/baja-confianza/run-a6497225005a48ba99f7f5b52429ff82/events.jsonl), [alertas](escenarios/baja-confianza/run-a6497225005a48ba99f7f5b52429ff82/alerts.jsonl), [ventanas/referencia](escenarios/baja-confianza/run-a6497225005a48ba99f7f5b52429ff82/windows.jsonl), [imágenes](escenarios/baja-confianza/run-a6497225005a48ba99f7f5b52429ff82/images/).
- [Métricas primarias y resultado](escenarios/baja-confianza/run-a6497225005a48ba99f7f5b52429ff82/metrics.json), [recálculo independiente](metricas/C2-recalculo.json).
- [HTML y verificación HTTP](portal/run-a6497225005a48ba99f7f5b52429ff82/http-verification.json), [evento en navegador](portal/C2-evento-verificado.png), [alerta en navegador](portal/C2-alerta-verificada.png).
- Muestra trazada: `evt-0a38174a0c704752bdeb952ca9111398` → su PNG; alerta `alert-578c4011dfd345ed930c99dcbd57887f` → ese evento.
- 10 frames exitosos, 10 alertas bajas reales. No se alteraron puntuaciones. C1 también produce alertas conforme a la regla.

## Correspondencia y revisión

| Criterio | Evidencia principal |
| --- | --- |
| R1 | Configuración/modelo de run.json, imagen PNG y salidas events.jsonl de ambos paquetes. |
| R2 | [Inventario G1–G7](../METRICAS.md), metrics.json y [recálculos](metricas/). |
| R3 | [Referencia observada](referencia_confianza.md), [scores y ventanas](referencia_confianza.json), tests de límites y persistencia temporal. |
| R4 | Eventos, images y HTML del portal; persistencia reiniciada en pruebas. |
| R5 | alerts.jsonl, vínculos, motivo/severidad/acción en HTML y screenshots. |
| R6 | C1 y C2 seleccionados arriba, manifests de entrada, modelo real y recorrido en navegador. |
| R7 | [README](../README.md), [procedencia](../PROCEDENCIA.md), lock Windows y hashes de código. Asociación Git/autoría completa pendientes. |

[Matriz detallada](cumplimiento.md), [recorrido del portal](portal/recorrido.md),
[pruebas](pruebas/pytest.xml), [integridad de originales](auditoria_repositorio.json),
[cámara física](camara.json). No hay exclusiones de grupos G1–G7.

La [reinferencia de entradas conservadas](modelo-reproduccion.json) reprodujo
exactamente las salidas guardadas de la muestra de C1 y C2, y comprobó que los hashes
del código probado siguen coincidiendo con los archivos actuales.

Las carpetas run-8c668ffb3cbb456dab715c697b6a6f80 y run-7aa2214933c94f5a8c1f4aa59d9af341
son ejecuciones preliminares conservadas con sus propios hashes; no se cuentan como
escenarios distintos ni representan la versión final. Dashboard-preliminar es una
captura de una consulta histórica sin muestras dentro de la ventana móvil.

## Extras

Se implementó un dashboard sencillo, paginación, filtro por ejecución y control del
productor. Se muestran para uso, pero **no se solicitan puntos extra en esta versión**:
no se presenta inventario de bonos sin verificación propia de cada nivel. El stream
visual y las gráficas históricas no están implementados. El cambio sostenido se
verificó con dobles unitarios, sin reclamar escenario adicional real.

Los hashes reflejan el código ejecutado. Este índice y las capturas se incorporaron
después; no modifican el comportamiento. Antes de entregar, un commit autorizado
debe asociar estos hashes con una revisión y completar el identificador del estudiante.
No se requiere que un commit contenga su propio hash. No se hicieron commits ni push.
