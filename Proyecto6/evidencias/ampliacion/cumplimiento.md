# Matriz de cumplimiento técnico R1–R7

Estado local comprobado, sujeto a evaluación docente; no equivale a 100 puntos otorgados.
Fuentes exclusivamente locales para la entrega, con YOLOX-Nano real CPU.

| Criterio | Implementación y evidencia | Estado / límites |
| --- | --- | --- |
| R1 | Secuencias y video progresivos, detector reutilizado, pesos/descriptor SHA, candidates/post-NMS, tres zonas y posición. C1/C2/Video del lote final; reproducción exacta de dos PNG. | Verificado localmente. No depende de cámara/carrito. |
| R2 | G1 latencia, G2 FPS, G3 RSS, G4 baja confianza, G5 trazabilidad, G6 frescura, G7 alertas abiertas. Observaciones, fórmulas, adquisición y recálculo por corte/IDs. | Siete grupos aplicables; ninguno excluido. Auditoría aritmética y pruebas; sin métricas de calidad inventadas. |
| R3 | Inferior 0.60, superior 0.80; piso 0.10 independiente, NMS 0.45/tope 100. Ventanas de cinco frames, mínimo cinco detecciones, dos de referencia y dos sostenidas, aumento 0.20. | Referencia original de C1/C2 preservada; nueva ejecución S4 verifica cambio y recuperación. Scores no calibrados como probabilidad de acierto. |
| R4 | SQLite, evento por intento, PNG de frame decodificado sin TTL, hashes y enlaces por ID, fallos diagnosticados. | HTTP del evento/imagen y ZIP comparados con bytes originales; errores sin imagen no generan capturas falsas. |
| R5 | Reglas de baja confianza/cambio sostenido, severidad, motivo, acción, config/modelo/IDs y origen; historial de revisión separado. | Cadena alerta→eventos→capturas y transacciones probadas. Reconocer/resolver no cambia scores. |
| R6 | C1 diez imágenes normales y C2 diez degradadas, con inferencias ONNX, métricas, eventos, capturas y alertas de scores bajos. | Ambos observados de nuevo y consultados por HTTP; evidencia anterior preservada. Recortes son material de prueba, no dataset de evaluación. |
| R7 | README PowerShell sin hardware, requisitos/lock, arquitectura, manual, métricas, procedencia, escenarios, extras y manifiestos. | Nombre/matrícula y commit autorizado pendientes; CI remoto no ejecutado. No se inventan identificadores académicos. |

Consultar el [índice](indice.md) y [verificación final](verificacion-final.json) para
runs y resultados concretos. Los eventos primarios conservan campos de modelo,
configuración, tiempos y RSS; los snapshots conservan corte, población y denominador.
Las fuentes con errores y frames vacíos prueban semántica de ausencias sin sustituir
una inferencia real por un mock. Las pruebas unitarias sintéticas están identificadas.

La primera entrega y su matriz conservan el alcance que tuvieron entonces. Esta
matriz describe la ampliación actual sin reescribir resultados anteriores. La rúbrica
y guía originales están intactas; EXTRAS es un documento nuevo autorizado.
