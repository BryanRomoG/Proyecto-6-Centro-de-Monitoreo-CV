"""Dobles sintéticos para fallos; no son evidencia de C1/C2."""
from copy import deepcopy
from pathlib import Path
import threading

import pytest

from monitor_cv.camera import Packet
from monitor_cv.config import Settings
from monitor_cv.main import create_app
from monitor_cv.service import MonitorService
from fastapi.testclient import TestClient


class TestDetector:
    __test__ = False
    synthetic = True
    identity = {"sha256": "unit-test-only", "name": "test-double"}

    def __init__(self, settings):
        pass

    def infer(self, rgb):
        raise RuntimeError("injected-runtime-error")


def test_inference_and_decode_errors_are_persistent(settings, image_bytes):
    folder = Path(settings.source.images_dir)
    folder.mkdir()
    (folder / "1.png").write_bytes(image_bytes)
    (folder / "2.png").write_bytes(b"broken")
    service = MonitorService(settings, detector_factory=TestDetector)
    run = service.start()
    service.thread.join(5)
    rows = list(reversed(service.db.list("events", run)))
    assert [e["status"] for e in rows] == ["inference_error", "decode_error"]
    assert rows[0]["image_ref"] and rows[0]["inference_ms"] is None
    assert all(e["synthetic"] for e in rows)
    assert service.db.list("alerts", run) == []
    assert service.db.get("runs", run)["status"] == "completed"
    assert service.metrics(run)["values"]["G4"] is None


def test_missing_model_start_rejected(settings):
    def missing(settings):
        raise ValueError("model missing for test")
    service = MonitorService(settings, detector_factory=missing)
    with TestClient(create_app(settings, service=service)) as client:
        response = client.post("/api/monitor/start")
        assert response.status_code == 409
        assert "model missing" in response.json()["detail"]
        assert client.get("/api/status").json()["state"] == "idle"


def test_source_error_and_stop_no_duplicate_run(settings, monkeypatch):
    import monitor_cv.service as module
    ready, release = threading.Event(), threading.Event()
    class Source:
        def packets(self, stop):
            yield Packet("disconnected", None, None, "source timeout test")
            ready.set()
            release.wait(3)
        def close(self):
            pass
    monkeypatch.setattr(module, "open_source", lambda _: Source())
    service = MonitorService(settings, detector_factory=TestDetector)
    run = service.start()
    assert ready.wait(3)
    with pytest.raises(ValueError, match="activa"):
        service.start()
    release.set()
    service.stop()
    events = service.db.list("events", run)
    assert len(events) == 1 and events[0]["status"] == "source_error"
    assert events[0]["captured_at"] is None
    assert service.metrics(run)["values"]["G6"] is None
