"""Etiquetas de interfaz; las claves técnicas y clases COCO se conservan en registros."""
LABELS={"ok":"Con detecciones","no_detections":"Sin detecciones","source_error":"Error de lectura",
        "decode_error":"Imagen inválida","inference_error":"Error de inferencia","active":"Abierta",
        "acknowledged":"Reconocida","resolved":"Resuelta","low":"Baja confianza","doubt":"Duda",
        "accepted":"Aceptada por política","warning":"Advertencia","high":"Alta","info":"Informativa"}


def spanish(value):
    return LABELS.get(value,value)
