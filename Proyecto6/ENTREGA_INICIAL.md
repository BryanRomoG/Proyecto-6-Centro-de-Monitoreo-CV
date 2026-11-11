# Informe de la primera implementación · 10 de noviembre de 2026

1. **Archivos y estructura.** Se creó el paquete `src/monitor_cv` con main, detector,
   camera, metrics, confidence, events, alerts, database, config y service; adaptaciones
   internas `_yolox` y `_mjpeg`; portal HTML/CSS/JS; configuración YAML; descargador,
   preparación/replay, verificadores de métricas/portal/cámara y auditoría; pruebas,
   dependencias, lock Windows, .env.example y evidencias. Los PNG y registros reales
   están agrupados por ejecución. [Índice completo](evidencias/indice.md).
2. **Reutilización.** Se adaptaron el detector YOLOX-Nano, Detection, lector MJPEG,
   reloj anclado, descriptor y descargador del Proyecto 5. Se eliminaron dependencias
   de `p5` y políticas del carrito. [Procedencia exacta](PROCEDENCIA.md).
3. **README y Git.** Recreados [README local](README.md) y [.gitignore](.gitignore).
   Adaptados README raíz, .gitignore, .gitattributes y configuración heredada de CI.
   Se conservan todos los antecedentes, sin exclusiones completas. Workflows anteriores
   se mantienen manuales; se añadió CI CPU propio, todavía no ejecutado en GitHub.
4. **Arquitectura implementada.** Una fuente progresiva → modelo real con hash →
   zonas/ventanas → eventos, imágenes, alertas y métricas persistentes en SQLite →
   portal FastAPI. Imágenes PNG sin pérdida, sin expiración. Un productor por proceso.
5. **Entorno.** Instalado `.venv` propio con Python 3.12.10 y dependencias directas
   fijadas. `pip check`: sin dependencias rotas. Modelo descargado desde Megvii,
   3,659,407 bytes y SHA-256 verificado. No se usaron paquetes ni pesos de otros proyectos.
6. **Pruebas/resultados.** **39 pasaron, 0 fallaron, 0 omitidas**. Una advertencia
   de deprecación AnyIO/Starlette. C1 y C2 finales: diez inferencias cada uno, veinte
   imágenes/eventos y veinte alertas bajas en total. C1: 76 detecciones (46 bajas,
   30 aceptadas). C2: 65 detecciones (43 bajas, 15 duda, 7 aceptadas). G1–G7 coinciden
   con el recálculo. HTML y navegador muestran imagen y cadena alerta→evento.
7. **R1–R7.** R1–R6 cuentan con implementación y evidencia local dentro del alcance
   de imágenes. Referencia temporal persistida; cambio sostenido probado por unitarios
   identificados como sintéticos. R7 tiene instalación/procedencia y evidencias, con
   revisión Git y datos académicos pendientes. No se asigna una nota ni se reclaman
   extras. [Matriz detallada](evidencias/cumplimiento.md).
8. **Bloqueos/límites.** La cámara configurada no entregó un JPEG fresco en las dos
   comprobaciones, incluida una fuera del sandbox. Falta verificar hardware/red,
   nombre académico y matrícula, un clon limpio en otra máquina y CI remoto.
   Sin commit inicial no puede vincularse todavía a una revisión Git; se guardaron
   hashes de código. El escaneo heurístico de candidatos no halló claves privadas ni
   tokens por sus patrones; dos URLs de pruebas se revisaron como valores ficticios.
   No hubo repositorios .git anidados ni archivos candidatos superiores a 20 MiB.
9. **Inicio exacto.** Desde la raíz, ejecutar en PowerShell:

   ```powershell
   Set-Location .\Proyecto6
   .\.venv\Scripts\python.exe -m uvicorn monitor_cv.main:create_app --factory --app-dir src --host 127.0.0.1 --port 8006
   ```

   Abrir <http://127.0.0.1:8006>. Durante esta implementación se dejó un servidor local
   disponible en ese puerto; no iniciar otro mientras siga ocupado. Para instalar en
   otra máquina y repetir C1/C2, seguir los comandos completos del [README](README.md).
10. **Siguiente fase.** Verificar ESP32-CAM en la LAN, reunir una referencia del dominio
    real y revisar la sensibilidad de la política sin alterar scores. Completar identidad
    y asociar evidencia a una revisión mediante un commit únicamente cuando se autorice.
    Después, ampliar pruebas prolongadas, cuotas y resolución de alertas si se desea.

No se realizaron commits, push ni cambios en configuración Git. Los hashes de los
antecedentes y documentos originales se contrastan en la [auditoría](evidencias/auditoria_repositorio.json).
