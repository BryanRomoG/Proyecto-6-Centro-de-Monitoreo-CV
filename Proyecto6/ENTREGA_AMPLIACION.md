# Entrega ampliada · Centro de Monitoreo de CV

Entrega individual con asistencia de Codex. Nombre académico y matrícula pendientes.
Implementación 0.2.0 en Windows/Python 3.12.10, ONNX Runtime CPU. Sin cámara ni carrito.
Este es un reporte técnico del desarrollo, no un reporte docente de calificación.

## 1. Archivos creados y modificados

El [inventario exacto de código](evidencias/ampliacion/archivos-codigo.json) compara
el manifiesto anterior con el actual: 17 nuevos, 13 modificados,
ningún original eliminado. No se usa un diff de Git inexistente para inventar un historial.
Se añadieron fuentes/consultas/analítica/distribución/exportación/derivados y aplicación;
se adaptaron productor, configuración, base de datos, métricas y portal. Se añadieron
scripts de medios/escenarios/verificación y pruebas. Documentación actualizada:
[README](README.md), [METRICAS](METRICAS.md), [PROCEDENCIA](PROCEDENCIA.md),
[arquitectura](ARQUITECTURA.md), [manual](MANUAL_USUARIO.md), [extras](Docs/EXTRAS.md).
El [manual de ejecución](MANUAL_EJECUCION.md) detalla instalación, recálculo y diagnóstico.
En raíz se actualizó el README. Configuración y exclusión de entradas generadas de
P6 cambiaron sin excluir completos los antecedentes. Las nuevas evidencias están en
[ampliacion](evidencias/ampliacion/indice.md).

## 2. Funcionalidades implementadas

Una cadena común imágenes/video→YOLOX→eventos/ventanas/alertas→SQLite/PNG→portal.
Registro de rutas permitidas, muestreo, fin/error de medio, pausa/continuación y
reproducción anotada sincronizada. La interfaz en español usa polling sin servicios
externos. Los errores son visibles y cada intento fallido se distingue de una
inferencia exitosa sin detecciones.

## 3. Estado R1–R7

Los siete criterios tienen implementación y verificación local. La [matriz](evidencias/ampliacion/cumplimiento.md)
enlaza pruebas y límites; G1–G7 se recalcularon en todas las ejecuciones seleccionadas.
La nota base y los puntos adicionales requieren evaluación, no se autoasignan.

## 4. Extras funcionales

F1 dashboard, F2 reproducción anotada, F3 nueve gráficas, F4 filtros avanzados,
F5 galería/ZIP, F6 CSV/JSON, F7 revisión de alertas, F8 registro de fuentes. Cada
uno tiene alcance, potencial y evidencia propios en [EXTRAS](Docs/EXTRAS.md).

## 5. Métricas adicionales verificadas

M01–M20 instrumentadas y recalculadas, con contrato/IDs/corte/denominador; M07 se
mantiene informativa sin bono independiente. p50/p95 forman una sola familia. G2/G6
no se vuelven a reclamar como throughput/frescura. M17/M18 usan cambios reales
de alerta; M20 compara distribuciones de scores sin inferir drift ni calidad.
Ver [resultados por caso](evidencias/ampliacion/verificacion-final.json) y [métricas](METRICAS.md).

## 6. Escenarios ejecutados

C1, C2, Video y S1–S7 cumplieron las condiciones técnicas; S6 tiene dos ejecuciones.
[Lote final](evidencias/ampliacion/ejecuciones/batch-f257a33483834710994f454dbb16000d/summary.json).
S1 interrumpe un archivo; S2 usa un recorte fotográfico sin detecciones; S3 conserva
insuficiencia; S4 observa cambio sostenido y recuperación; S5 corrupción; S6 versiones;
S7 excepción declarada del adaptador con ONNX real antes/después. No se fabricaron
scores ni alertas para cumplirlos. No se evalúa calidad predictiva.

## 7. Pruebas y resultados

Auditoría inicial: las 39 pruebas previas volvieron a pasar antes de ampliar.
Cierre: **68 aprobadas, 0 fallos, 0 errores, 0 omitidas** (95.190 s).
[JUnit](evidencias/ampliacion/pruebas/pytest.xml). Incluye video real, imágenes/ONNX,
pausa/sincronización, filtros/exportaciones, seguridad de rutas, SQL persistido,
concurrencia/idempotencia y escenarios. Los casos sintéticos unitarios comprueban
mecanismos/aritmética; los marcados real ejecutan pesos verificados. `pip check`
sin conflictos y `node --check` sin errores. Advertencia de dependencia Starlette/AnyIO;
el MP4 corrupto emite diagnóstico de OpenCV esperado. Los avisos ICC de las imágenes
de prueba no alteran la aceptación ni los scores guardados.

## 8. Errores encontrados y corregidos

Se corrigieron el registro del filtro de presentación Jinja, los valores de controles
al navegar durante pausa, el tratamiento de fechas locales al recargar filtros y
el cierre contable del último frame de video. También se hicieron históricas las
consultas de estado de alerta al corte y se rechazó el duplicado de fuente concurrente
como validación. Un clic de la herramienta sobre Resolver fue interceptado; la acción
se completó con teclado. No se ocultan esos límites de observación del navegador.

## 9. Evidencias generadas

Nuevo lote con resultados/primarios/PNG/config/hash y recálculos; reportes HTTP,
CSV/JSON y ZIP comparados; screenshots; JUnit; inventario y auditoría de conservación.
[Índice completo](evidencias/ampliacion/indice.md). Las 106 evidencias/documentos
protegidos conservan su SHA, sin modificar C1/C2 anteriores. Proyecto1–5 y los dos
documentos originales de Docs no cambiaron; solo se agregó EXTRAS autorizado.

## 10. Ejecución exacta en PowerShell

Desde la raíz del repositorio:

```powershell
Set-Location .\Proyecto6
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock-windows.txt
.\.venv\Scripts\python.exe scripts/download_model.py --destino modelo
.\.venv\Scripts\python.exe scripts/prepare_media.py
.\.venv\Scripts\python.exe -m uvicorn monitor_cv.main:create_app --factory --app-dir src --host 127.0.0.1 --port 8006
```

Abrir http://127.0.0.1:8006 y seguir [manual de usuario](MANUAL_USUARIO.md).
En otra terminal, desde Proyecto6 (la batería crea una carpeta nueva):

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
node --check web/static/js/portal.js
.\.venv\Scripts\python.exe scripts/run_scenarios.py
.\.venv\Scripts\python.exe scripts/verify_metrics.py evidencias/ampliacion/ejecuciones/batch-f257a33483834710994f454dbb16000d/C1
.\.venv\Scripts\python.exe scripts/verify_metrics.py evidencias/ampliacion/ejecuciones/batch-f257a33483834710994f454dbb16000d/C2
.\.venv\Scripts\python.exe scripts/verify_extras.py evidencias/ampliacion/ejecuciones/batch-f257a33483834710994f454dbb16000d/S4
.\.venv\Scripts\python.exe scripts/verify_features.py --run-id run-747a89d404d942c2bcf761965f760a1b
.\.venv\Scripts\python.exe scripts/audit_repository.py --compare evidencias/integridad_inicial.json
```

Los paquetes conservados se recalculan sin SQLite; el recorrido HTTP requiere que
esa ejecución exista en la base local. En otro equipo usar el run_id recién generado.
Para fuentes propias usar data/media; registrar ruta, seleccionar, muestreo y ejecutar.
Más opciones y semántica de reproducción en [README](README.md).

## 11. Pendientes reales

Nombre académico/matrícula y evaluación docente. CI remoto/commit no ejecutados.
La herramienta no confirmó la descarga nativa del navegador integrado: contenido
y headers sí se verificaron por HTTP/pruebas. Sin prueba de carga prolongada, login
ni notificaciones externas. Retención de capturas sin TTL requiere espacio en disco;
formatos de video dependen de códecs OpenCV. Las entradas repetidas de una sola escena
no prueban calidad ni generalización. El servidor se deja disponible sin productor activo.

## 12. Estado de Git y revisión previa a commit

Rama main, sin commits ni staging/push efectuados. Existe origin configurado, no se
modificó ni se utilizó para enviar cambios. La auditoría no detectó .git anidados,
archivos candidatos >20 MiB ni nombres sensibles; las dos coincidencias heurísticas
de URL con credenciales son fixtures de pruebas negativas (Proyecto5 y Proyecto6),
no credenciales de operación. No se imprimen valores sensibles en el reporte.
Las capturas de esta ampliación provienen de la escena pública declarada; no contienen
video personal. La revisión heurística no certifica ausencia universal de datos privados.
Antecedentes íntegros y conservados en Git según las exclusiones locales existentes.
