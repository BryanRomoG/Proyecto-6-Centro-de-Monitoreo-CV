"""Reglas de monitoreo; cada alerta conserva su condición y observaciones."""
from .events import uid


def evaluate(event: dict, window: dict | None, settings) -> list[dict]:
    alerts = []
    def make(rule, reason, event_ids, severity="warning"):
        return {"id": uid("alert"), "run_id": event["run_id"],
                "event_id": event["id"], "timestamp": event["timestamp"],
                "rule_id": rule, "config_sha256": event["config_sha256"],
                "severity": severity, "status": "active", "reason": reason,
                "event_ids": event_ids, "window_id": window["id"] if window else None,
                "suggested_action": "Revisar imágenes, iluminación, oclusión y preprocesamiento; no inferir acierto ni drift solo por confianza."}
    count = sum(d["zone"] == "low" for d in event["detections"])
    if event["status"] == "ok" and count >= settings.alerts.low_min_detections:
        alert = make("low-confidence-v1",
                     f"{count} detecciones con s < {settings.confidence.lower}; mínimo por frame: {settings.alerts.low_min_detections}",
                     [event["id"]])
        alert["window_id"] = None
        alerts.append(alert)
    if window and window["state"] == "sustained_change":
        alert = make("sustained-confidence-v1",
                     f"Aumento >= {settings.confidence.increase} durante {settings.confidence.sustained_windows} ventanas elegibles frente a referencia fija",
                     window["sustained_event_ids"], "high")
        alert["window_ids"] = window["sustained_window_ids"]
        alert["reference_window_ids"] = window["reference_window_ids"]
        alerts.append(alert)
    return alerts
