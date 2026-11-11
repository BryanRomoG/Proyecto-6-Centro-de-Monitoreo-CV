"""Recalcula G1–G7 de un paquete exportado, con el mismo instante de corte."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from monitor_cv.metrics import calculate


def read_lines(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def verify(directory: Path) -> dict:
    events = read_lines(directory / "events.jsonl")
    alerts = read_lines(directory / "alerts.jsonl")
    stored = json.loads((directory / "metrics.json").read_text(encoding="utf-8"))
    obtained = calculate(events, alerts, run_id=stored["run_id"], data_dir=directory,
                         window_seconds=stored["window_seconds"], now=stored["timestamp"])
    matches = {k: (v is None and obtained["values"][k] is None) or
               (v is not None and obtained["values"][k] is not None and
                math.isclose(v, obtained["values"][k], rel_tol=1e-9, abs_tol=1e-9))
               for k, v in stored["values"].items()}
    # Revisión aritmética independiente de las observaciones, además del recálculo de producción.
    ts = lambda s: datetime.fromisoformat(s).timestamp()
    end = ts(stored["timestamp"])
    sample = [e for e in events if e["run_id"] == stored["run_id"] and end-stored["window_seconds"] <= ts(e["timestamp"]) <= end]
    success = [e for e in sample if e["status"] in {"ok", "no_detections"}]
    scored = [d for e in success for d in e["detections"]]
    timed = [e["inference_ms"] for e in success if e["inference_ms"] is not None]
    fps_denominator = sum(e["attempt_elapsed_s"] for e in sample)
    def unresolved_at_cutoff(alert):
        state = "active" if alert.get("history") else alert["status"]
        for change in alert.get("history", []):
            if ts(change["timestamp"]) <= end:
                state = change["to_state"]
        return state in {"active", "acknowledged"}
    independent = {"G1": sum(timed)/len(timed) if timed else None,
                   "G2": len(success)/fps_denominator if fps_denominator else None,
                   "G3": sum(e["rss_bytes"] for e in sample if e.get("rss_bytes") is not None) /
                         len([e for e in sample if e.get("rss_bytes") is not None]) / 1048576
                         if any(e.get("rss_bytes") is not None for e in sample) else None,
                   "G4": sum(d["confidence"] < e["config"]["confidence"]["lower"]
                             for e in success for d in e["detections"])/len(scored) if scored else None,
                   "G7": sum(unresolved_at_cutoff(a) and ts(a["timestamp"]) <= end for a in alerts)}
    reports = [e for e in events if e["run_id"] == stored["run_id"] and e.get("captured_at") and ts(e["timestamp"]) <= end]
    independent["G6"] = max(0, end-max(ts(e["captured_at"]) for e in reports)) if reports else None
    complete = 0
    for e in sample:
        good = all(e.get(k) for k in ["id", "run_id", "frame_id", "timestamp", "source_id", "model", "config", "config_sha256", "status"])
        good = good and bool(e["model"].get("sha256"))
        if e["status"] in {"ok", "no_detections"}:
            good = good and bool(e.get("image_ref"))
        if e.get("image_ref"):
            import hashlib
            path = (directory / e["image_ref"]).resolve()
            good = (good and path.is_relative_to(directory.resolve()) and path.is_file()
                    and hashlib.sha256(path.read_bytes()).hexdigest() == e.get("image_sha256"))
        complete += bool(good)
    independent["G5"] = complete/len(sample) if sample else None
    independent_ok = all((v is None and stored["values"][k] is None) or
                         (v is not None and stored["values"][k] is not None and math.isclose(v, stored["values"][k], rel_tol=1e-9))
                         for k, v in independent.items())
    return {"run_id": stored["run_id"], "matches": matches,
            "independent_values": independent, "independent_ok": independent_ok,
            "values": obtained["values"], "ok": all(matches.values()) and independent_ok}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    report = verify(args.directory)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["ok"] else 1)
