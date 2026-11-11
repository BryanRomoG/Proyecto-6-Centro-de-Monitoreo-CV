"""Comprueba recepción de un JPEG fresco de la cámara configurada, sin controlar el carrito."""
from pathlib import Path
import argparse
import json
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from monitor_cv.camera import MjpegSource, decode
from monitor_cv.config import load_settings
from monitor_cv.events import utc_now


def main():
    settings = load_settings()
    stop = threading.Event()
    reader = MjpegSource(settings)
    result = {"timestamp": utc_now(), "source_id": settings.source.source_id,
              "configured_url": settings.source.url, "hardware_verified": False}
    try:
        packet = next(reader.packets(stop))
        if packet.error:
            result["error"] = packet.error
        else:
            rgb = decode(packet.data)
            result.update(hardware_verified=True, captured_at=packet.captured_at,
                          width=rgb.shape[1], height=rgb.shape[0])
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        stop.set()
        try:
            reader.close()
        except Exception as exc:
            result["close_error"] = str(exc)
    out = ROOT / "evidencias/camara.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["hardware_verified"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
