> Copia pública derivada: los enlaces a registros locales se sustituyeron por notas explícitas. El original se conserva.

> Actualización vigente: grupo O2026_ESI3906B, suite 115 +2 Edge; ver [informe de publicación](INFORME_PUBLICACION.md), [política segura](Docs/PUBLICACION_SEGURA.md) y [matriz pública](evidencias/publicacion_segura/evaluacion-publica.json). Las cifras previas del cuerpo describen el cierre anterior; esta actualización no es una nota oficial.

# Entrega final · Proyecto 6

**Bryan Edgardo Romo Gonzalez · 745268 · individual · ITESO · Machine Learning.**
Profesor Victor Hugo Martinez Sanchez. Fecha de entrega: **13/11/2026**.
Grupo/sección: **O2026_ESI3906B**. [Ficha académica](Docs/IDENTIDAD.md).
Repositorio: https://github.com/BryanRomoG/Proyecto-6-Centro-de-Monitoreo-CV.
Revisión local: 2026-11-12T02:02:05.565091+00:00.

## 1. Datos académicos incorporados

La ficha, README, procedencia y portal usan los datos definitivos. academic.json solo
alimenta la identificación visual. No se duplicó la matrícula en eventos/revisiones,
nombres de imágenes ni el endpoint técnico de configuración. Las capturas nuevas de
Edge ocultan la identificación lateral. Los reportes históricos conservan lo que
decían en su fecha; sus marcadores pendientes no son la identificación actual.

## 2. Archivos creados y modificados

Nuevos: reviews.py, test_reviews.py, test_public_scenarios.py, test_reviews_portal.py,
academic.json, run_public_scenarios.py, verify_public_portal.py, final_audit.py,
prepare_git_plan.py, code_revision_map.py; documentación de identidad/revisión/escenarios/
Git, esta entrega, evaluación e índice de cierre. Cambios en aplicación, SQLite,
anotación, registro de fuentes, contrato de métricas, frontend, aislamiento de pruebas,
versionado 0.4 y enlaces SSR de exportación. El workflow P6 prepara medios/datasets.
El [plan exacto](Docs/PLAN_GIT.md) y sus inventarios enumeran rutas. No se modificó
código de Proyecto1–Proyecto5 ni los dos documentos del profesor.

## 3. Revisión manual implementada

Selección por ID individual; pendiente/confirmada/falso positivo/corregida; etiqueta
original y humana separadas; motivo, actor local, fecha, UUID, versión e historial.
Vista original frente a solo validadas; superposición como aviso, sin supresión ni
cambio NMS. Los conflictos y reenvíos se controlan en SQLite y cliente. Sin captura
íntegra no se guarda una validación visual. [Flujo y contratos](Docs/REVISION_MANUAL.md).

## 4. Demostración real dog/cat

Evento `evt-37c2579bd3af445fb8a683807642e8ee`, foto Open Images `488d4412c71bf3f1` (Marco, CC BY 2.0).
Dog **0.6565653975020709**, duda, confirmado; cat **0.17536601693758413**, bajo,
falso positivo. La capa validada muestra solo dog. Se verificaron sin cambios el
evento original, ambas predicciones y el PNG SHA `3cfc4c8afade41cc0bd86d81c86fbe42d083b4f565d0ce73ee55142d4777ba52`.
La revisión fue asistida por Codex bajo revisor-local, sin atribuir una firma al
estudiante ni obtener métricas de calidad. Captura y revisión (registro local o recurso regenerable; consultar el índice público).

## 5. Alertas, trazabilidad y persistencia

La alerta `alert-75e89e2ac05841dda4ebc8dc04347dea` fue reconocida y resuelta desde Edge
con motivo/comentario y revisión vinculada. La condición original de baja confianza
fue real y sigue conservada. Los cambios son append-only. Un reinicio real conservó
las dos revisiones idénticas; nuevas conexiones y apps también se prueban en la suite.

## 6. Estado R1–R7

Estimación interna local: R1=15, R2=25, R3=15, R4=15, R5=15, R6=10, R7=5: **100/100**.
Cada subcriterio, evidencia y limitación está en la [matriz](EVALUACION_ESTIMADA.md).
Es una valoración de la versión de trabajo identificada por hashes, no una nota
oficial ni una afirmación sobre el commit remoto anterior.

## 7. Métricas base G1–G7

Aplican los siete grupos: media de inferencia, FPS procesados, RSS medio, proporción
baja, trazabilidad íntegra, antigüedad de último frame y alertas abiertas. M1–M5 tienen
definición, adquisición, cálculo/ausencias, observaciones y verificación por grupo.
R2=25×35/(5×7)=25. Se recalcularon 22 paquetes, con fórmulas
independientes para la base y pruebas aritméticas. [Definiciones](METRICAS.md).

## 8. Funcionalidades extra

F1 dashboard 10; F2 reproducción 15; F3 gráficos 10; F4 filtros 10; F5 galería 15;
F6 exportación 10; F7 ciclo de alertas 15; F8 fuentes 10; F9 adquisición 10;
F10 revisión por detección 15. **F=120**. F9 ya tenía otro significado; no se renumeró.
Los niveles y fronteras están en [EXTRAS](Docs/EXTRAS.md).

## 9. Métricas extra

M01–M20 se auditaron individualmente con grupo, fórmula, población/ventana, unidad,
instrumento, datos, ausencia, valor y recálculo. **M=90**. M07 es informativa y vale
cero de bono por compartir RSS con G3; p50/p95 cuentan como una familia. M08 se
estima conservadoramente en 3 por conteo segmentado. No se asignan puntos extra
por repetir un cálculo con otro color, clase, fuente o ventana. Resultados por fila (registro local o recurso regenerable; consultar el índice público).

## 10. Escenarios extra

S1 interrupción 10; S2 sin detecciones 5; S3 poco tráfico 5; S4 cambio sostenido 8;
S5 corrupta 10; S6 cambio de configuración 8; S7 fallo controlado del adaptador 10.
**S=56**. Fallos/diagnóstico/reacción y verificación posterior sustentan S1/S5/S7;
solo la excepción técnica S7 es inyectada y se identifica así. [Detalle](Docs/ESCENARIOS.md).

## 11. Puntos estimados sustentados

**Base 100 + F120 + M90 + S56 = 366.** Extras 266, sin límite global ni normalización.
Se asigna un solo nivel por elemento. Calificación oficial: **pendiente del profesor**.
La [evaluación](EVALUACION_ESTIMADA.md) justifica cada nivel, incluidos ceros y la
reducción de M08 frente al potencial antiguo. No hay promesa de puntos docentes.

## 12. Puntos pendientes de demostrar

La matriz no suma reservas ni niveles superiores incompletos: pendientes técnicos
contabilizados, 0. Publicación autorizada y comprobación del commit definitivo
son tareas pendientes separadas. No se afirma clone remoto, CI remoto, carga prolongada
ni evaluación de calidad. Cualquier nivel distinto que adopte el profesor prevalece.

## 13. Riesgos de doble conteo

Capturas mínimas/R4 y consultas/R5 no son otros extras. F5 añade coordinación visual
y distribución; F10 decisiones por detección. El puente con alertas no convierte
un formulario en otro bono. F2 acredita controles; F8 registro/validación. F9 es una
adquisición, no ocho ni ochenta. M07 no se suma, percentiles son una familia y el
video/C1_PUBLIC/C2_PUBLIC no se reclaman como S8/S9. S4 no es otra copia de C2.

## 14. Mejoras adicionales

Historiales de alerta se cargan por lote: la consulta completa medida pasó de 4.20 s
a 1.20 s en una comprobación local, sin pretender un benchmark general. Los enlaces
CSV/JSON ya respetan filtros desde el HTML inicial; no dependen de la hidratación JS.
Un run desconocido permanece como filtro vacío. Nuevos runs usan rutas relativas.
Pruebas reales y C1/C2 públicos usan bases aisladas. La galería conserva SQL paginado,
miniaturas <=320×240, lazy loading, máximo cuatro solicitudes, cancelación, caché,
errores y reintentos verificados. No carga PNG completos al abrirse.

## 15. Pruebas automatizadas y resultados

Antecedente del estudiante: 87 passed/1 warning/49.08 s, conservado como declarado.
Línea base observada: 87 sin fallos. Cierre: **107 passed**, una advertencia conocida,
cero fallos/errores/skips. Otra instalación con venv nuevo pasó las **107 pruebas**,
pip check e instalación editable. No se eliminaron pruebas; se añadieron 17 de revisión,
una de escenarios públicos y dos de exportación SSR. Resultados (registro local o recurso regenerable; consultar el índice público).

## 16. Navegador

**Dos tests Edge pasaron**, sin respuestas simuladas: galería, reintento por error real,
cambios rápidos, filtros/recarga, ZIP y CSV nativos, fuentes, pausa/reanudación/cambio,
inferencia real, nueve secciones, revisión perro/gato, alertas, vacío y vista móvil.
Otro recorrido de los C1/C2 públicos pasó nueve comprobaciones de eventos, capturas,
hashes, galería y alertas. Los intentos fallidos previos se conservan, con sus correcciones.

## 17. Escenarios reproducidos

La suite repitió C1/C2, video y S1–S7 con modelo real; los errores controlados se
etiquetan. Los paquetes históricos permanecen intactos y se recalcularon. Además,
C1_PUBLIC/C2_PUBLIC ejecutaron 20 fotos existentes en runtime independiente:
161/86 detecciones y 10/9 alertas, con modelo/política idénticos, sin scores prefijados.
La base principal no recibe esas repeticiones y no se cuentan como 20 originales nuevos.

## 18. Evidencias nuevas

Índice (registro local o recurso regenerable; consultar el índice público), JUnit, resúmenes, auditoría, hashes de código,
mapa CRLF/LF, reinicio, revisiones, capturas Edge y paquetes públicos completos.
Hay un resumen publicable y una proyección explícita sin rutas personales; los JSON
originales completos se conservan localmente, sin modificar hashes para ocultar datos.

## 19. Documentación actualizada

README raíz/P6, PROCEDENCIA, METRICAS, ARQUITECTURA, manuales, Docs/DATASETS/EXTRAS y
nuevos IDENTIDAD/REVISION_MANUAL/ESCENARIOS/PLAN_GIT, matriz y este informe. Las guías
oficiales y evidencias antiguas conservan sus bytes. Las dependencias no se actualizaron
para ocultar la deprecación de Starlette. [Entrada de documentación](README.md).

## 20. Git y publicación

Existe el commit previo `0b0a7b459d299e4741753e08f4c7133da65f76f4` en main y origin
del repositorio indicado. No se ejecutó add/commit/push ni se cambió el remoto.
No hay .git anidados ni candidatos >20 MiB. Dos coincidencias de credenciales en URL
son fixtures de pruebas; no se imprimieron valores. El plan identifica las rutas
personales de registros históricos y la licencia individual no acreditada de dog.jpg.
La selección pública sigue pendiente de esa revisión; **no se declara todo el árbol
listo para publicarse sin selección**. Modelo excluido y descargable con SHA verificado;
80 fotos con procedencia/licencia identificada por fila y manifiesto reproducible.

## 21. Pendientes antes de entregar

El escaneo de privacidad adicional (registro local o recurso regenerable; consultar el índice público)
detectó posibles contactos en archivos históricos y en el autor público de una foto.
Los valores no se imprimieron y los originales no se alteraron. Revisar esas rutas y
la atribución de la imagen `26557008b4fcf408` antes de publicar manifest/eventos raw.
No se incluyó un correo personal en la ficha académica del estudiante.

Grupo confirmado O2026_ESI3906B; revisar metadatos históricos y derechos de las fotos
legadas; autorizar posteriormente un commit/push si procede; verificar la entrega
seleccionada desde esa revisión. La ruta profunda de Windows puede causar WinError
206: usar una ruta corta. La copia aislada probada usa bytes existentes de medios;
no prueba un clone remoto publicado ni garantiza derechos del material legado.
Git convierte texto a LF: el mapa de bytes explica los hashes locales sin cambiarlos.

La galería principal auditada muestra **1347 capturas disponibles,
22 eventos técnicos sin captura, 0 archivos faltantes
y 0 pendientes** al corte. Los ocho casos originales no incluían IDs en la solicitud;
la auditoría cubre todos los eventos conservados y no encontró referencias declaradas
con archivo ausente. Los técnicos son errores de lectura/decodificación sin imagen
válida recibida, no capturas perdidas. No se inventaron imágenes ni se restauraron bytes
innecesariamente. Las 80 fotos ocupan 26,376,549 bytes y siguen siendo 80 SHA distintos.

## 22. Comandos exactos de PowerShell

Desde la raíz del repositorio, para una instalación nueva (red para dependencias,
modelo y fotos ausentes; Edge solo para pruebas de navegador):

```powershell
Set-Location -LiteralPath .\Proyecto6
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock-windows.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/download_model.py --destino modelo
.\.venv\Scripts\python.exe scripts/download_demo_dataset.py --target-per-category 10 --max-mb 200
# Solo para reproducir también los escenarios/pruebas legados:
.\.venv\Scripts\python.exe scripts/prepare_media.py
.\.venv\Scripts\python.exe -m pytest -q
$env:MONITOR_DATA_DIR = 'data/runtime'
$env:MONITOR_AUTOSTART = 'false'
.\.venv\Scripts\python.exe -m uvicorn monitor_cv.main:create_app --factory --app-dir src --host 127.0.0.1 --port 8007
```

La instancia de auditoría ya está en <http://127.0.0.1:8007>. No iniciar otra en el
mismo puerto mientras siga activa. Para C1/C2 independientes, en otra terminal P6:

```powershell
.\.venv\Scripts\python.exe scripts/run_public_scenarios.py --sample-hz 4
# El comando imprime una carpeta única; asignar su summary.json real:
$resumenPublico = Get-Content -LiteralPath 'evidencias/cierre_final/escenarios-publicos/public-1d8aeb9f8b9a484b8e5b6088895d73fb/summary.json' -Raw | ConvertFrom-Json
$env:MONITOR_DATA_DIR = $resumenPublico.runtime_data_dir
.\.venv\Scripts\python.exe -m uvicorn monitor_cv.main:create_app --factory --app-dir src --host 127.0.0.1 --port 8008
```

La ruta mostrada corresponde al lote verificado de este cierre. Para uno nuevo usar
la ruta que imprima, con sus nuevos IDs. No mezclar la base aislada con la principal.
Recálculo sin iniciar servidores:

```powershell
.\.venv\Scripts\python.exe scripts/verify_metrics.py 'evidencias/cierre_final/escenarios-publicos/public-1d8aeb9f8b9a484b8e5b6088895d73fb/C1_PUBLIC'
.\.venv\Scripts\python.exe scripts/verify_metrics.py 'evidencias/cierre_final/escenarios-publicos/public-1d8aeb9f8b9a484b8e5b6088895d73fb/C2_PUBLIC'
.\.venv\Scripts\python.exe scripts/verify_extras.py 'evidencias/cierre_final/escenarios-publicos/public-1d8aeb9f8b9a484b8e5b6088895d73fb/C2_PUBLIC'
```

Pruebas Edge con servidor principal activo, sin productor activo y al menos 50
capturas históricas (en copia vacía, ejecutar una vez run_dataset_demo.py para poblarla):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-browser-test.txt
$env:MONITOR_TEST_URL = 'http://127.0.0.1:8007'
$env:MONITOR_BROWSER_EVIDENCE = 'evidencias/cierre_final/navegador'
.\.venv\Scripts\python.exe -m pytest browser_tests -q
$auditoriaActual = 'evidencias/cierre_final/audit-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
.\.venv\Scripts\python.exe scripts/final_audit.py --output $auditoriaActual
```

final_audit está orientado al conjunto histórico conservado en esta entrega. Una
copia seleccionada sin esos paquetes no puede verificar registros que no contiene;
usar allí verify_metrics/verify_extras sobre sus propios lotes, sin afirmar accesos
inexistentes. La reproducción de la app no depende de una DB previa; los IDs de
la demostración local sí. [Plan Git y comandos propuestos](Docs/PLAN_GIT.md).

## 23. Recomendaciones por efecto en la evaluación

1. Resolver selección/licencias y revisar qué evidencia será accesible para el profesor;
   protege trazabilidad y reproducibilidad R4/R7 y la verificabilidad de los extras.
2. Conservar el grupo confirmado O2026_ESI3906B y recorrer la revisión; revisar autoría/asistencia y
   no presentar decisiones locales como una medición de accuracy.
3. Autorizar y comprobar una revisión Git definitiva cuando se decida publicar; incluir
   índices/manifiestos y evidencia necesaria, sin entornos, DB ni modelos grandes.
4. Conservar íntegros C1/C2 y S1–S7, con sus límites; no añadir repeticiones como bonos.
5. Si se amplía M08, una distribución derivada con tratamiento de ausencia y verificación
   podría justificar reevaluar su nivel. Ahora se acredita solo el conteo simple.

### Recorrido manual breve para el estudiante

- Abrir [el caso perro/gato](http://127.0.0.1:8007/events/evt-37c2579bd3af445fb8a683807642e8ee/review): alternar
  original/validada y comprobar ambas predicciones frente a solo dog validado.
- Recargar y consultar historial/motivos; abrir la alerta resuelta y verificar su origen.
- En Galería cambiar colección, clase, zona y run; pasar página y descargar una selección
  con atribución. Un filtro de run inexistente debe mostrar vacío.
- En Fuentes iniciar una colección, pausar, continuar, detener y elegir otra; comprobar
  eventos/históricos por ejecución. Esto crea un run de demostración identificado.
- Grupo confirmado O2026_ESI3906B; revisar la selección Git antes de autorizarla.


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
