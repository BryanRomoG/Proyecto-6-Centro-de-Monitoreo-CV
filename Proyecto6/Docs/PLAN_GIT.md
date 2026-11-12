# Plan Git vigente: selección pública sin modificar el índice

La decisión vigente está en [PUBLICACION_SEGURA.md](PUBLICACION_SEGURA.md), con
comandos posteriores propuestos y limitaciones. El índice previo de cierre conserva
la trazabilidad original de 158 archivos; no se borra ni altera ese inventario.
[Clasificación actual](../evidencias/publicacion_segura/privacidad.json) ·
[Copias e integridad](../evidencias/publicacion_segura/sanitizacion.json) ·
[Índice GitHub](../evidencias/publicacion_segura/INDICE_GITHUB.md) ·
[Lista exacta de candidatos](../evidencias/publicacion_segura/archivos-proximo-commit.txt).

Grupo confirmado O2026_ESI3906B; [Canvas](https://canvas.iteso.mx/courses/57431).
El supuesto de repositorio sin commits es histórico: main/origin ya existen y HEAD
es 0b0a7b459d299e4741753e08f4c7133da65f76f4. La API pública confirmó el mismo main remoto.
Se mantienen Proyecto1–Proyecto5 intactos como antecedentes, sin ignorar carpetas completas.

Las incidencias iniciales eran rutas personales, contactos de antecedentes, autor con
contacto en 26557008b4fcf408 y dog.jpg/derivados sin licencia fotográfica individual
acreditada. Se preservan originales y se preparan copias públicas derivadas. Open Images:
80 fotos locales, 79 seleccionadas públicamente con atribuciones intactas. C1/C2/S1–S7
autorizados sustituyen la necesidad de redistribuir dog.jpg, sin eliminar los casos viejos.

El paquete propuesto selecciona P6; no certifica la privacidad de todo el historial
existente. El .gitignore no retira lo ya rastreado. No se ejecuta git rm --cached ni
ningún otro cambio de índice; las rutas históricas públicas requieren una decisión
posterior explícita. Un nuevo commit que retire una ruta tampoco borra commits previos.

Los JSON locales completos y documentos con enlaces solo locales no se publican a
ciegas: la copia materializada registra cada proyección y verifica enlaces internos.
La lista exacta para preparar después se vuelve a comparar con hashes y estado Git.
No se realizaron add, commit, push, reset, clean, cambios de remoto ni reescritura.
La autorización y la observación real de GitHub Actions siguen pendientes.
