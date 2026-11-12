> Copia pública derivada: los enlaces a registros locales se sustituyeron por notas explícitas. El original se conserva.

# Escenarios verificados

Además de los originales, se ejecutaron C1_PUBLIC/C2_PUBLIC con Open Images en un
almacén independiente. Son una alternativa de los dos escenarios base, no S8/S9:
20 entradas reutilizadas de los 80 originales, 161/86 detecciones y 10/9 alertas.
La política es idéntica y las rutas son relativas. El
índice de cierre (registro local o recurso regenerable; consultar el índice público) enlaza paquetes y navegador.

```powershell
.\.venv\Scripts\python.exe scripts/run_public_scenarios.py --sample-hz 4
```

El script crea por defecto SQLite/capturas en un runtime aislado e imprime la carpeta
de evidencia. Leer `runtime_data_dir` en su summary.json para abrir ese almacén con
MONITOR_DATA_DIR; no depende de la base histórica. No ejecuta las otras seis colecciones
ni vuelve a descargar imágenes. No se reclaman bonos por esta repetición.

Los paquetes históricos seleccionados (registro local o recurso regenerable; consultar el índice público) se conservan
sin cambios. La auditoría actual (registro local o recurso regenerable; consultar el índice público) vuelve a
recalcularlos y las pruebas reales repiten su aceptación con SQLite aislado. No se
cuentan las reproducciones como nuevas fotografías, métricas o escenarios.

| ID | Entrada / expectativa | Observado y evidencia primaria | Diagnóstico, reacción y comprobación |
| --- | --- | --- | --- |
| C1 | 10 frames normales; inferencia y monitoreo progresivos | 10 intentos, 76 detecciones, 10 alertas; modelo/config propios del paquete C1 | Operación técnicamente normal. El piso 0.10 conserva salidas débiles, por lo que también dispara alertas. No se fabrica un estado saludable. |
| C2 | 10 frames preparados de baja confianza; misma política/modelo de comparación | 10 intentos, 65 detecciones, 10 alertas; PNG, scores y reglas originales | La baja confianza procede de ONNX. No se fijan scores ni se cambian umbrales para aparentar el resultado. |
| S1 | Retirar temporalmente un archivo entre lecturas | Secuencia ok → source_error → ok → ok | Excepción de lectura diagnosticada, restauración del archivo en finally, continuidad del stream y dos inferencias posteriores. Sin imagen inventada para el fallo. |
| S2 | Recorte de fotografía sin objetos detectados | Tres inferencias reales no_detections, listas vacías, cero alertas bajas | Lista vacía explícita; no se inventa score 0 ni error predictivo. |
| S3 | Una sola imagen, ventana de cinco frames | Un intento, insufficient_evidence y ninguna ventana completa | No confundir poca evidencia con normalidad. La alerta por frame conserva su regla independiente. |
| S4 | 10 frames de referencia, 10 cambiados, 5 de retorno | Estados collecting_reference ×2 → change_pending → sustained_change → within_policy; KS null/null/0.8/0.8/0 | Regla fijada antes del lote: aumento >=0.20 durante dos ventanas; alerta sostenida y retorno observado. No confirma drift ni pérdida de calidad. |
| S5 | Imagen PNG deliberadamente corrupta entre dos válidas | ok → decode_error → ok | Bytes recibidos inválidos, diagnóstico de decodificación, omisión controlada y captura/inferencia real posterior íntegra. Diferente de archivo ausente en S1. |
| S6 | Misma escena/modelo; superior 0.80 y después 0.85 | Dos runs de dos frames; scores iguales y hashes de configuración distintos | Persistencia de las versiones y separación de referencias/series. Es cambio de configuración, no un modelo nuevo ni otro bono por variar un parámetro. |
| S7 | Excepción controlada en la segunda llamada del adaptador | ok → inference_error → ok → ok | Fallo INYECTADO, inference_executed=false en ese intento; captura y diagnóstico retenidos, dos inferencias ONNX reales posteriores. No se presenta como fallo espontáneo del runtime. |

S1/S5/S7 acreditan fallo, diagnóstico, reacción, continuidad/recuperación y verificación
posterior con imágenes e integridad recalculadas. El nivel interno propuesto se explica
en [EXTRAS](EXTRAS.md); no se cuenta C2 otra vez como S4 ni el video de apoyo como S8.
En S1 la continuidad se verifica sobre imágenes siguientes: no se afirma haber repetido
la lectura interrumpida. En S5 se omite la entrada corrupta: no se dice que sus bytes
fueron reparados. Las escenas preparadas son correlacionadas, no una muestra estadística.

## Reproducción

Desde Proyecto6, preparar modelo/medios según el [manual](../MANUAL_EJECUCION.md):

```powershell
.\.venv\Scripts\python.exe scripts/run_scenarios.py
```

El comando crea un lote único e imprime su ruta. Con esa ruta:

```powershell
$loteActual = 'RUTA_IMPRESA_POR_EL_COMANDO'
.\.venv\Scripts\python.exe scripts/verify_metrics.py (Join-Path $loteActual 'C1')
.\.venv\Scripts\python.exe scripts/verify_metrics.py (Join-Path $loteActual 'C2')
.\.venv\Scripts\python.exe scripts/verify_extras.py (Join-Path $loteActual 'S4')
```

No hay hardware necesario. El test real usa un almacén temporal independiente y no
agrega sus escenarios a la base del portal. Los comandos CLI de demostración sí crean
runs reales cuando el usuario los solicita. La evidencia histórica conserva sus rutas
de origen como metadatos; la reproducción reconstruye entradas en el checkout actual.

Las 80 fotos de Open Images aportan otra demostración de diversidad: 569 detecciones,
52 clases, zonas 440 bajas/82 dudas/47 aceptadas y dos fotos sin detecciones en el lote
seleccionado. Se procesaron todas, sin escoger resultados por score. Ver
[DATASETS](DATASETS.md) e índice de ese lote (registro local o recurso regenerable; consultar el índice público).


## Selección pública vigente

Ver [publicación segura](PUBLICACION_SEGURA.md) e [índice GitHub](../evidencias/publicacion_segura/INDICE_GITHUB.md): 79 fotos autorizadas para la selección, nuevos C1/C2/S1–S7 reales y copias derivadas con trazabilidad. Los registros anteriores se conservan localmente; no equivalen a bytes aprobados para publicar.
