# Referencia y elección de política de confianza

Los umbrales inferior 0.60 y superior 0.80 y el piso 0.10 se fijaron en settings.yaml
antes de ejecutar C1/C2. Se adoptan como separación operativa de casos a investigar,
no como probabilidad calibrada de acierto. Las observaciones posteriores permiten
comprobar que la política deja visibles las tres zonas y registrar su sensibilidad.
No se ajustaron puntuaciones ni se cambiaron umbrales para fabricar C2.

| Ejecución | Detecciones finales | Bajas | Duda | Aceptadas | Mínimo / máximo |
| --- | --- | --- | --- | --- | --- |
| C1 | 76 | 46 | 0 | 30 | 0.100153 / 0.839510 |
| C2 | 65 | 43 | 15 | 7 | 0.106027 / 0.891176 |

Las salidas fuertes de la escena quedan mayoritariamente sobre 0.80, algunas salidas
intermedias en duda y candidatas débiles por debajo de 0.60. Por eso se mantiene el
piso 0.10 separado del inferior: observar débiles es parte del objetivo. Esta política
produce alertas en todos los frames de C1 y C2; no se interpreta su frecuencia como
evidencia de errores predictivos. Debe revisarse con imágenes representativas de la
cámara antes de uso continuo, porque puede ser ruidosa. C1 acredita operación normal
del sistema, no ausencia de alertas. El umbral no demuestra generalización.

El [JSON de referencia](referencia_confianza.json) conserva todas las puntuaciones por
evento y los IDs, conteos y cocientes de las ventanas observadas. Las primeras dos
ventanas elegibles de cada ejecución son la referencia fija local del monitor;
se guardan en SQLite y en los paquetes windows.jsonl. Diez frames alcanzan esas dos
ventanas, pero no demuestran una transición sostenida posterior. La regla sostenida
está implementada, configurada y probada con datos sintéticos identificados; no se
reclama un escenario real de drift. Son variantes correlacionadas de una única escena.

C1 y C2 usan el mismo artefacto, preprocesamiento, NMS y umbrales. Los hashes efectivos
difieren por la carpeta fuente; por diseño no comparten serie temporal ni referencia.
No se comparan como si fueran la misma configuración. Los pasos para repetir la
ejecución y recalcular resultados están en el [README](../README.md).
