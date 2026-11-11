"""Ejecuta C1/C2 con YOLOX real y exporta evidencia nueva en una carpeta por run."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from monitor_cv.config import Settings, load_settings
from monitor_cv.events import json_text
from monitor_cv.service import MonitorService


def code_manifest() -> dict:
    paths = list((ROOT / "src").rglob("*.py")) + list((ROOT / "scripts").glob("*.py"))
    paths += list((ROOT / "tests").glob("*.py"))
    paths += list((ROOT / "web").rglob("*.html")) + list((ROOT / "web").rglob("*.css")) + list((ROOT / "web").rglob("*.js"))
    paths += [ROOT / "config/settings.yaml", ROOT / "requirements.txt", ROOT / "pyproject.toml", ROOT / "modelo/descriptor.yaml"]
    if (ROOT / "requirements-lock-windows.txt").is_file():
        paths.append(ROOT / "requirements-lock-windows.txt")
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def export_run(service: MonitorService, run_id: str, output: Path, scenario: str) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    events = list(reversed(service.db.list("events", run_id)))
    alerts = list(reversed(service.db.list("alerts", run_id)))
    windows = list(reversed(service.db.list("windows", run_id)))
    metrics = service.metrics(run_id)
    for event in events:
        if event["image_ref"]:
            target = output / event["image_ref"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(service.settings.data_dir / event["image_ref"], target)
    for name, rows in [("events", events), ("alerts", alerts), ("windows", windows)]:
        (output / f"{name}.jsonl").write_text("".join(json_text(row) + "\n" for row in rows), encoding="utf-8")
    run = service.db.get("runs", run_id)
    (output / "run.json").write_text(json_text(run) + "\n", encoding="utf-8")
    (output / "metrics.json").write_text(json_text(metrics) + "\n", encoding="utf-8")
    (output / "code-sha256.json").write_text(json.dumps(code_manifest(), indent=2) + "\n", encoding="utf-8")
    manifest = ROOT / "data/demo/manifest.json"
    if manifest.is_file():
        shutil.copyfile(manifest, output / "inputs-manifest.json")
    successes = [e for e in events if e["status"] in {"ok", "no_detections"}]
    low = [e for e in events if any(d["zone"] == "low" for d in e["detections"])]
    linked = [a for a in alerts if a["rule_id"] == "low-confidence-v1"
              and any(e["id"] in a["event_ids"] and e["image_ref"] for e in low)]
    real_chain = bool(successes) and all(not e["synthetic"] for e in successes)
    observed = real_chain and (bool(low and linked) if scenario == "C2" else len(successes) == len(events))
    report = {"scenario": scenario, "run_id": run_id, "inference_chain_observed": observed,
              "portal_verification": "pending; ejecutar recorrido HTML y navegador",
              "status": "partial_pending_portal" if observed else "not_demonstrated",
              "events": len(events), "successful_frames": len(successes), "low_frames": len(low),
              "low_alerts": len(linked), "config_sha256": service.settings.fingerprint,
              "model_sha256": run["model"]["sha256"],
              "command": f".\\.venv\\Scripts\\python.exe scripts/run_demo.py --scenario {scenario}"}
    (output / "result.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=["C1", "C2"], required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--images", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    settings = load_settings(args.config, environ=False)
    folder = "normal" if args.scenario == "C1" else "baja-confianza"
    data = settings.model_dump()
    data["source"]["kind"] = "images"
    data["source"]["images_dir"] = str(args.images.resolve()) if args.images else f"data/demo/{folder}"
    settings = Settings.model_validate(data)
    service = MonitorService(settings)
    run_id = service.start()
    service.thread.join()
    output = (args.output or ROOT / "evidencias/escenarios" / folder) / run_id
    report = export_run(service, run_id, output, args.scenario)
    print(json.dumps({"output": str(output.relative_to(ROOT)) if output.is_relative_to(ROOT) else str(output), **report}, indent=2))
    if service.error:
        print(service.error, file=sys.stderr)
        return 1
    return 0 if report["inference_chain_observed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
