"""G1–G7 desde eventos/alertas persistidos y comprobación de referencias de imágenes."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import hashlib

from .events import uid, utc_now


def epoch(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def alert_state_at(alert: dict, cutoff: float) -> str:
    # El payload original se conserva; cambios posteriores no contaminan snapshots pasados.
    state = "active" if alert.get("history") else alert["status"]
    for change in alert.get("history", []):
        if epoch(change["timestamp"]) <= cutoff:
            state = change["to_state"]
    return state


def trace_complete(event: dict, data_dir: Path) -> bool:
    required = ("id", "run_id", "frame_id", "timestamp", "source_id", "model", "config_sha256", "config", "status")
    if any(not event.get(k) for k in required):
        return False
    if not event["model"].get("sha256"):
        return False
    if event["status"] in {"ok", "no_detections"} and not event.get("image_ref"):
        return False
    if event.get("image_ref"):
        path = (data_dir / event["image_ref"]).resolve()
        if not path.is_relative_to(data_dir.resolve()) or not path.is_file():
            return False
        with path.open("rb") as handle:
            if hashlib.file_digest(handle, "sha256").hexdigest() != event.get("image_sha256"):
                return False
    return True


def calculate(events: list[dict], alerts: list[dict], *, run_id: str, data_dir: Path,
              window_seconds: float, now: str | None = None) -> dict:
    now = now or utc_now()
    end = epoch(now)
    # Aislamiento por ejecución: nunca mezclar modelos/configuraciones de otras corridas.
    all_run = [e for e in events if e["run_id"] == run_id and epoch(e["timestamp"]) <= end]
    selected = [e for e in all_run if end - window_seconds <= epoch(e["timestamp"])]
    successes = [e for e in selected if e["status"] in {"ok", "no_detections"}]
    timed = [e for e in successes if e.get("inference_ms") is not None]
    duration = sum(e["attempt_elapsed_s"] for e in selected)
    detections = [d for e in successes for d in e["detections"]]
    low = sum(d["zone"] == "low" for d in detections)
    rss = [e["rss_bytes"] for e in selected if e.get("rss_bytes") is not None]
    traced = sum(trace_complete(e, data_dir) for e in selected)
    reports = [e for e in all_run if e.get("captured_at")]
    latest = max(reports, key=lambda e: epoch(e["captured_at"]), default=None)
    active = [a for a in alerts if a["run_id"] == run_id
              and alert_state_at(a, end) in {"active", "acknowledged"} and epoch(a["timestamp"]) <= end]
    values = {
        "G1": sum(e["inference_ms"] for e in timed) / len(timed) if timed else None,
        "G2": len(successes) / duration if selected and duration > 0 else None,
        "G3": sum(rss) / len(rss) / 1048576 if rss else None,
        "G4": low / len(detections) if detections else None,
        "G5": traced / len(selected) if selected else None,
        "G6": max(0, end - epoch(latest["captured_at"])) if latest else None,
        "G7": len(active),
    }
    return {"id": uid("metric"), "run_id": run_id, "timestamp": now,
            "window_seconds": window_seconds, "values": values,
            "units": {"G1": "ms", "G2": "frames/s", "G3": "MiB", "G4": "proporción",
                      "G5": "proporción", "G6": "s", "G7": "alertas"},
            "event_ids": [e["id"] for e in selected],
            "last_report_event_id": latest["id"] if latest else None,
            "active_alert_ids": [a["id"] for a in active],
            "primary": {"successful_frames": len(successes), "attempt_elapsed_s": duration,
                        "scored_detections": len(detections), "low_detections": low,
                        "traced_events": traced, "eligible_events": len(selected)},
            "state": "observed" if selected else "insufficient_evidence"}
