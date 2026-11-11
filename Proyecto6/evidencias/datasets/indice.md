# Evidencias del dataset y galería · 0.3

Nombre académico y matrícula pendientes. Entrega individual; no se autoasigna nota.

- [Verificación final](verificacion-final.json): hashes, procedencia, ocho fuentes,
  recálculos G1–G7/M01–M20, thumbnails/304/ZIP y tiempos reales de consulta.
- [Dataset y licencias](../../Docs/DATASETS.md), [reporte completo](../../ENTREGA_DATASETS.md).
- [Lote final seleccionado](ejecuciones/dataset-f316f59912a04cf1bb4a2bf2a1f3bc9a/summary.json): 80 eventos con 80 entradas distintas,
  569 detecciones de 52 clases y 71 alertas. No se cuentan las repeticiones como escenas nuevas.
- [JUnit principal](pruebas/pytest-cierre.xml): 87 aprobadas; [JUnit Edge](pruebas/pytest-edge-cierre.xml): 1 aprobada.
- [Navegador real](navegador/edge-bed24221288d46e49a4109ea6e7f47c6/verification.json): reintento, filtros rápidos, refresco, paginación,
  ZIP nativo con atribución, dos fuentes YOLOX y móvil sin desbordamiento.
- [Auditoría de referencias](referencias/audit-0614f874bdc64bb3a5a1adbd9f5093ed.json),
  [auditoría del repositorio](auditoria-repositorio.json), [conservación](cierre.json).

| Colección | Run | Detecciones / vacías / alertas | Inferencia media (ms) |
| --- | --- | --- | --- |
| [escenas_despejadas](ejecuciones/dataset-f316f59912a04cf1bb4a2bf2a1f3bc9a/escenas_despejadas/result.json) | `run-00b55429f17f4cb09a1c4c39b65d95b2` | 23 / 1 / 8 | 17.178 |
| [baja_confianza](ejecuciones/dataset-f316f59912a04cf1bb4a2bf2a1f3bc9a/baja_confianza/result.json) | `run-6aa2c20d06074541b95cd9f195ccf982` | 86 / 1 / 9 | 19.295 |
| [escenas_multiples](ejecuciones/dataset-f316f59912a04cf1bb4a2bf2a1f3bc9a/escenas_multiples/result.json) | `run-66a68e2135f14873b1552e10fb0ab9f0` | 161 / 0 / 10 | 18.051 |
| [objetos](ejecuciones/dataset-f316f59912a04cf1bb4a2bf2a1f3bc9a/objetos/result.json) | `run-c006280c924e42ecbb094c58668c7979` | 80 / 0 / 10 | 17.534 |
| [bicicletas](ejecuciones/dataset-f316f59912a04cf1bb4a2bf2a1f3bc9a/bicicletas/result.json) | `run-bdc71983a9bf46c9a80e7858df169f4f` | 53 / 0 / 10 | 18.642 |
| [vehiculos](ejecuciones/dataset-f316f59912a04cf1bb4a2bf2a1f3bc9a/vehiculos/result.json) | `run-a15a53ae11c442cd8fa181a1bfbbd938` | 68 / 0 / 10 | 18.078 |
| [animales](ejecuciones/dataset-f316f59912a04cf1bb4a2bf2a1f3bc9a/animales/result.json) | `run-a304b5fdd4ac49d89381a38b15acaabb` | 28 / 0 / 6 | 17.816 |
| [personas](ejecuciones/dataset-f316f59912a04cf1bb4a2bf2a1f3bc9a/personas/result.json) | `run-72b70fce9e7747cc91295f67eece6a46` | 70 / 0 / 8 | 16.031 |

Cada carpeta contiene run/config/modelo, primarios events/alerts/windows/actions.jsonl,
capturas PNG, base/extras, hashes de código y recálculos. Sus IDs permiten enlazar
entrada original, fuente, modelo, puntuaciones, captura y alertas. Los dos frames
vacíos se conservan con lista de detecciones vacía y estado explícito.

## Iteraciones conservadas

Los lotes anteriores de esta ampliación se conservan como iteraciones; no se suman
como otras fotografías originales. La tabla selecciona únicamente el lote cuyo código
coincide con la versión final. Las pruebas de controles crean además runs parciales
reutilizando originales. Las evidencias de C1/C2/S1–S7 anteriores a esta tarea no cambiaron.

Se conservan también intentos E2E fallidos: uno esperaba la actualización de polling
instantánea; otro permitió detectar un ID de frame anterior al iniciar otra fuente.
Se corrigió la vista para limpiarse y aceptar solo el run iniciado. El reporte Edge
seleccionado arriba es la ejecución posterior completa, sin respuestas HTTP simuladas.

La herramienta integrada presentó problemas de accionabilidad; Edge headless con un
perfil nuevo verificó los mismos flujos y la descarga nativa. Los scripts y sus
dependencias opcionales están versionados en browser_tests y requirements-browser-test.
