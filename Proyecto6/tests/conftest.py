import io
from pathlib import Path
import sys

import numpy as np
from PIL import Image
import pytest

from monitor_cv.config import Settings
from monitor_cv.events import sha256_bytes, utc_now


@pytest.fixture
def settings(tmp_path):
    return Settings.model_validate({"source": {"images_dir": str(tmp_path / "input"), "sample_hz": 60},
                                    "storage": {"data_dir": str(tmp_path / "runtime")}})


@pytest.fixture
def image_bytes():
    out = io.BytesIO()
    Image.fromarray(np.full((48, 64, 3), 114, np.uint8)).save(out, format="PNG")
    return out.getvalue()


@pytest.fixture
def event(settings, image_bytes):
    stamp = utc_now()
    path = settings.data_dir / "images/e-1.png"
    path.parent.mkdir(parents=True)
    path.write_bytes(image_bytes)
    return {"id": "e-1", "run_id": "r-1", "frame_id": "f-1", "timestamp": stamp,
            "captured_at": stamp, "source_id": "unit-test", "status": "ok", "synthetic": True,
            "model": {"sha256": "unit-test-model"}, "config": settings.model_dump(),
            "config_sha256": settings.fingerprint, "detections": [
                {"class_id": 0, "class_name": "person", "confidence": .4,
                 "bbox": [0, 0, 10, 10], "zone": "low"}], "candidates": [],
            "inference_ms": 20., "attempt_elapsed_s": .5, "rss_bytes": 104857600,
            "image_ref": "images/e-1.png", "image_sha256": sha256_bytes(image_bytes)}
