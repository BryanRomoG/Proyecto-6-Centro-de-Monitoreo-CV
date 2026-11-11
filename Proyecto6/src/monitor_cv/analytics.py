"""Consultas históricas y métricas adicionales con observaciones primarias enlazadas."""
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from .images import image_path
from .metrics import epoch, alert_state_at
from .metric_specs import CATALOG
from .distribution import compare_windows


def extras(events: list[dict], alerts: list[dict], data_dir: Path, *, cutoff: str, windows=()) -> dict:
    """Población explícita: selección filtrada; descarta observaciones posteriores al corte."""
    end = epoch(cutoff)
    events = [e for e in events if epoch(e["timestamp"]) <= end]
    alerts = [a for a in alerts if epoch(a["timestamp"]) <= end]
    good = [e for e in events if e["status"] in {"ok", "no_detections"}]
    scored = [d for e in good for d in e["detections"]]
    times = [e["inference_ms"] for e in good if e.get("inference_ms") is not None]
    seconds = sum(e["attempt_elapsed_s"] for e in events)
    reads = [e for e in events if e.get("read_frames") is not None]
    cpu = [e for e in events if e.get("cpu_seconds_delta") is not None]
    ram = [e["rss_bytes"] for e in events if e.get("rss_bytes") is not None]
    valid_images = [e for e in events if e["status"] in {"ok", "no_detections", "inference_error"}]
    linked = 0
    for event in valid_images:
        try:
            image_path(data_dir, event)
            linked += 1
        except FileNotFoundError:
            pass
    bins = np.linspace(0,1,11)
    histogram = np.histogram([d["confidence"] for d in scored], bins=bins)[0].tolist()
    acknowledgments, resolutions, repeat = [], [], 0
    previous = {}
    for alert in sorted(alerts,key=lambda a:a["timestamp"]):
        key = (alert["run_id"],alert["rule_id"])
        ts = epoch(alert["timestamp"])
        if key in previous and ts-previous[key] <= 10:
            repeat += 1
        previous[key] = ts
        for change in alert.get("history", []):
            if epoch(change["timestamp"]) > end:
                continue
            if change["action"] == "acknowledge":
                acknowledgments.append(epoch(change["timestamp"])-ts)
            if change["action"] == "resolve":
                resolutions.append(epoch(change["timestamp"])-ts)
    ratio = lambda n,d: n/d if d else None
    activity = Counter(f"{e['source_id']} / {e['run_id']}" for e in events)
    values = {
        "M01": {"p50": float(np.percentile(times,50)), "p95":float(np.percentile(times,95))} if times else None,
        "M02": ratio(sum(e["status"] not in {"ok","no_detections"} for e in events),len(events)),
        "M03": sum(e.get("discarded_frames") or 0 for e in reads) if reads else None,
        "M04": ratio(sum(e["read_frames"] for e in reads),seconds) if reads else None,
        "M05": sum(e["status"] == "source_error" for e in events),
        "M06": ratio(sum(e["cpu_seconds_delta"] for e in cpu)*100,
                     sum(e["attempt_elapsed_s"] for e in cpu)),
        "M07": max(ram)/1048576 if ram else None,
        "M08": dict(Counter(d["class_name"] for d in scored)),
        "M09": {"edges":bins.tolist(),"counts":histogram} if scored else None,
        "M10": ratio(sum(e["status"] == "no_detections" for e in good),len(good)),
        "M11": ratio(len(scored),len(good)),
        "M12": ratio(sum(d["zone"] == "doubt" for d in scored),len(scored)),
        "M13": ratio(sum(e["status"] == "decode_error" for e in events),sum(e["status"] != "source_error" for e in events)),
        "M14": ratio(linked,len(valid_images)),
        "M15": dict(activity),
        "M16": ratio(len(alerts)*60,seconds),
        "M17": float(np.mean(acknowledgments)) if acknowledgments else None,
        "M18": float(np.mean(resolutions)) if resolutions else None,
        "M19": repeat,
        "M20": compare_windows(events,windows,cutoff),
    }
    return {"cutoff":cutoff,"values":values,"catalog":CATALOG,"event_ids":[e["id"] for e in events],
            "alert_ids":[a["id"] for a in alerts],
            "primary":{"attempts":len(events),"successful_frames":len(good),"detections":len(scored),
                       "observed_seconds":seconds,"acknowledgments":acknowledgments,"resolutions":resolutions,
                       "decoded_frames":len(valid_images),"linked_images":linked},
            "run_configs":{e["run_id"]:e["config_sha256"] for e in events}}


def history(events: list[dict], alerts: list[dict], windows: list[dict], interval_seconds: int) -> dict:
    buckets = defaultdict(lambda:{"events":0,"errors":0,"alerts":Counter(),"event_ids":[],"alert_ids":[]})
    for event in events:
        key = int(epoch(event["timestamp"])//interval_seconds)*interval_seconds
        bucket = buckets[key]
        bucket["events"] += 1
        bucket["errors"] += event["status"] not in {"ok","no_detections"}
        bucket["event_ids"].append(event["id"])
    for alert in alerts:
        key = int(epoch(alert["timestamp"])//interval_seconds)*interval_seconds
        buckets[key]["alerts"][alert["severity"]] += 1
        buckets[key]["alert_ids"].append(alert["id"])
    groups = defaultdict(list)
    for e in sorted(events,key=lambda e:e["timestamp"]):
        groups[e["run_id"]].append({"event_id":e["id"],"timestamp":e["timestamp"],
            "inference_ms":e.get("inference_ms"),
            "fps":1/e["attempt_elapsed_s"] if e["status"] in {"ok","no_detections"} and e["attempt_elapsed_s"]>0 else None,
            "ram_mib":e["rss_bytes"]/1048576 if e.get("rss_bytes") is not None else None})
    ids = {e["id"] for e in events}
    selected_windows = [w for w in windows if set(w["event_ids"]).issubset(ids)]
    return {"series":dict(groups), "windows":selected_windows,
            "interval_seconds":interval_seconds,
            "intervals":[{"epoch":k,**v,"alerts":dict(v["alerts"])} for k,v in sorted(buckets.items())],
            "note":"Sin interpolación. Series de modelos/configuraciones distintos permanecen separadas por ejecución."}
