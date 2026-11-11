"""Zonas y ventanas no solapadas, referencia fija y persistencia de cambio."""
from __future__ import annotations

from .config import Confidence
from .events import uid, utc_now


def zone(score: float, lower: float, upper: float) -> str:
    if not 0 <= score <= 1:
        raise ValueError("Confianza debe estar en [0,1]")
    return "low" if score < lower else "doubt" if score < upper else "accepted"


class ConfidenceMonitor:
    def __init__(self, config: Confidence):
        self.config = config
        self.pending = []
        self.reference = []
        self.streak = []
        self.last_state = "insufficient_evidence"

    def add(self, event: dict) -> dict | None:
        self.pending.append(event)
        if len(self.pending) < self.config.window_frames:
            self.last_state = "insufficient_evidence"
            return None
        events, self.pending = self.pending, []
        detections = [d for e in events if e["status"] == "ok" for d in e["detections"]]
        count = len(detections)
        low = sum(d["zone"] == "low" for d in detections)
        result = {"id": uid("window"), "timestamp": utc_now(),
                  "event_ids": [e["id"] for e in events],
                  "detections": count, "low": low, "ratio": low / count if count else None,
                  "state": "insufficient_evidence", "baseline_ratio": None,
                  "reference_window_ids": [w["id"] for w in self.reference],
                  "sustained_window_ids": [], "sustained_event_ids": []}
        # No comparar ventanas con fallos técnicos ni referencia contaminada por fallos.
        eligible = (count >= self.config.min_detections
                    and all(e["status"] in {"ok", "no_detections"} for e in events))
        if not eligible:
            self.streak.clear()
        elif len(self.reference) < self.config.reference_windows:
            self.reference.append(result.copy())
            result["state"] = "collecting_reference"
        else:
            base_count = sum(w["detections"] for w in self.reference)
            baseline = sum(w["low"] for w in self.reference) / base_count
            result["baseline_ratio"] = baseline
            if result["ratio"] - baseline >= self.config.increase:
                self.streak.append(result.copy())
                self.streak = self.streak[-self.config.sustained_windows:]
                result["state"] = "change_pending"
                if len(self.streak) >= self.config.sustained_windows:
                    result["state"] = "sustained_change"
                    result["sustained_window_ids"] = [w["id"] for w in self.streak]
                    result["sustained_event_ids"] = [i for w in self.streak for i in w["event_ids"]]
            else:
                self.streak.clear()
                result["state"] = "within_policy"
        self.last_state = result["state"]
        return result
