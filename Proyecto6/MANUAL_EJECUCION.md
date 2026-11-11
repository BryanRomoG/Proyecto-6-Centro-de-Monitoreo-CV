# Manual de ejecución · PowerShell sin hardware

La instalación completa y versiones están en [README](README.md). Ejecutar los
comandos desde Proyecto6; se invoca Python del entorno directamente, sin cambiar
ExecutionPolicy. Los antecedentes no se instalan ni importan.

## Preparar e iniciar

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock-windows.txt
.\.venv\Scripts\python.exe -m pip check
if (!(Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe scripts/download_model.py --destino modelo
.\.venv\Scripts\python.exe scripts/prepare_media.py
.\.venv\Scripts\python.exe -m uvicorn monitor_cv.main:create_app --factory --app-dir src --host 127.0.0.1 --port 8006
```

Abrir <http://127.0.0.1:8006>. Fuentes → registrar Secuencia `data/demo/normal` o
Video `data/media/demo.mp4` → seleccionar → Iniciar. El video de ejemplo es generado
con imágenes, identificado como reproducción local. No necesita ESP32-CAM.
Reproducción muestra el frame procesado; Pausar/Continuar/Detener controlan el
productor. Ctrl+C termina el servidor. Más recorridos en [manual de usuario](MANUAL_USUARIO.md).

## Pruebas y nuevos escenarios

En otra terminal, desde Proyecto6:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/run_scenarios.py
```

El segundo comando imprime una carpeta nueva: copiar su ruta exacta. Los escenarios
no sobrescriben los anteriores. Para exportar JUnit sin reemplazar el cierre conservado:

```powershell
$pruebaActual = 'evidencias/ampliacion/pruebas/pytest-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.xml'
.\.venv\Scripts\python.exe -m pytest -q --junitxml=$pruebaActual
```

Con un lote nuevo guardado, sustituir la ruta y usar:

```powershell
$loteActual = 'RUTA_COMPLETA_IMPRESA_POR_RUN_SCENARIOS'
.\.venv\Scripts\python.exe scripts/verify_metrics.py (Join-Path $loteActual 'C1')
.\.venv\Scripts\python.exe scripts/verify_metrics.py (Join-Path $loteActual 'C2')
.\.venv\Scripts\python.exe scripts/verify_extras.py (Join-Path $loteActual 'S4')
```

Con servidor activo, copiar un run_id desde Ejecuciones y verificar sus consultas:

```powershell
.\.venv\Scripts\python.exe scripts/verify_features.py --run-id 'RUN_ID_REAL'
```

Los paquetes seleccionados se recalculan sin depender de la base SQLite. Consultarlos
en el portal sí requiere la base local que los produjo, o regenerar el lote y usar
sus nuevos IDs. No se importan silenciosamente paquetes como si fueran nuevas inferencias.

## Configuración y diagnóstico

- Imágenes/video propios: colocar dentro de data/media. Las raíces se definen en
  [settings.yaml](config/settings.yaml); registrar rutas externas es rechazado.
- `.env` heredado: usar MONITOR_SOURCE=images/video y rutas locales según
  [.env.example](.env.example). Reiniciar después de cambiar código/configuración.
- Puerto ocupado: detener la terminal anterior con Ctrl+C. Usar un solo worker.
- Modelo ausente/hash incorrecto: ejecutar el descargador; no renombrar otros pesos
  como si fueran YOLOX-Nano ni desactivar la comprobación SHA.
- Red/certificados: obtener dependencias y pesos con conexión válida; no desactivar TLS.
- Video ilegible: comprobar archivo, FPS/metadatos/códec; el error se muestra en el
  registro. MP4/mp4v y AVI/MJPEG fueron probados en este entorno.
- Sin referencia o sin detecciones: es un estado válido; no rellenar scores ni cambiar
  el umbral para ocultarlo. Ver [semántica de métricas](METRICAS.md).
- Base/capturas: data/runtime es local y está excluido de Git. Conservarlo mientras
  se consultan runs existentes. No hay eliminación automática de imágenes.

Antes de preparar cualquier commit (ninguno autorizado todavía):

```powershell
.\.venv\Scripts\python.exe scripts/audit_repository.py --compare evidencias/integridad_inicial.json
```

Revisar también privacidad del material propio que se seleccione como evidencia.
El escáner es heurístico y no inspecciona contenido visual de manera exhaustiva.


## Dataset público y prueba real de navegador

Consultar [DATASETS](Docs/DATASETS.md) para descarga selectiva y selección congelada.
Ejecutar download_demo_dataset.py, después run_dataset_demo.py y finalmente iniciar
uvicorn según los comandos anteriores. Para validar solo interfaz con Edge instalado,
servidor activo y ningún productor activo: instalar requirements-browser-test.txt y
ejecutar `python -m pytest browser_tests -q`. No necesita instalar otro navegador.
Los reportes/screenshot/ZIP nativo se guardan en evidencias/datasets/navegador.
`python scripts/audit_gallery.py` clasifica referencias sin alterar eventos.
`--restore-exact` permite restituir únicamente bytes con el SHA ya conservado.
