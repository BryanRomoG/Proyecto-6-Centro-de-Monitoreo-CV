# Eventos exportados

Los registros canónicos están en `../escenarios/<normal|baja-confianza>/<run_id>/events.jsonl`.
Cada evento enlaza su PNG en `images/` de la misma carpeta e incluye la configuración
efectiva completa, su hash, modelo y puntuaciones reales. Se mantienen juntos para
que el recálculo sea portable, evitando duplicar observaciones.
El [índice](../indice.md) identifica las ejecuciones seleccionadas.
