"""Verifica consultas HTML reales y su cadena alerta → evento → imagen por HTTP."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from monitor_cv.events import utc_now
from verify_metrics import read_lines


def verify(directory: Path, base_url: str) -> dict:
    result_path = directory / "result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    events = read_lines(directory / "events.jsonl")
    alerts = read_lines(directory / "alerts.jsonl")
    event = next((e for e in events if any(d["zone"] == "low" for d in e["detections"])), events[0])
    alert = next((a for a in alerts if event["id"] in a["event_ids"]), None)
    paths = {"events": f"/events?run_id={result['run_id']}", "event": f"/events/{event['id']}",
             "alerts": f"/alerts?run_id={result['run_id']}", "image": f"/images/{event['id']}"}
    if alert:
        paths["alert"] = f"/alerts/{alert['id']}"
    evidence = ROOT / "evidencias/portal" / result["run_id"]
    evidence.mkdir(parents=True, exist_ok=True)
    checks = {}
    with httpx.Client(base_url=base_url, timeout=15, trust_env=False) as client:
        for name, path in paths.items():
            response = client.get(path)
            ok = response.status_code == 200
            if name == "image":
                ok = ok and hashlib.sha256(response.content).hexdigest() == event["image_sha256"]
            else:
                ok = ok and "<html" in response.text
                if name in {"event", "events", "alert"}:
                    ok = ok and event["id"] in response.text
                # Guardar el HTML realmente servido; enlaces absolutos locales documentados.
                html = response.text.replace('<head>', f'<head><base href="{base_url}/">', 1)
                (evidence / f"{name}.html").write_text(html, encoding="utf-8")
            checks[name] = {"url": base_url + path, "status_code": response.status_code, "ok": ok}
        checks["missing"] = {"ok": client.get("/events/nonexistent-for-verification").status_code == 404}
        checks["empty"] = {"ok": "No hay eventos" in client.get("/events?run_id=nonexistent-for-verification").text}
    report = {"timestamp": utc_now(), "run_id": result["run_id"], "event_id": event["id"],
              "alert_id": alert["id"] if alert else None, "checks": checks,
              "ok": all(c["ok"] for c in checks.values()),
              "level": "HTML e imagen por HTTP; navegador se registra por separado"}
    (evidence / "http-verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if report["ok"]:
        result["portal_verification"] = "HTML e imagen HTTP verificados; ver evidencias/portal"
        result["status"] = "chain_and_html_observed_pending_browser"
        result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--base-url", default="http://127.0.0.1:8006")
    args = parser.parse_args()
    report = verify(args.directory, args.base_url)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["ok"] else 1)
