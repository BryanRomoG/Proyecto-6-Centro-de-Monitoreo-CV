from io import BytesIO
from pathlib import Path
import os
import threading

import numpy as np
from PIL import Image
import pytest

from monitor_cv._mjpeg import JpegParser
from monitor_cv._yolox import ConfigDetector, DetectorError, decodificar, letterbox
from monitor_cv.camera import ImageSource, decode
from monitor_cv.config import ROOT, Settings
from monitor_cv.detector import Detector


def test_mjpeg_fragmented_and_multiple():
    parser = JpegParser()
    assert parser.feed(b"multipart noise\xff") == []
    assert parser.feed(b"\xd8jpeg\xff") == []
    assert parser.feed(b"\xd9\r\n\xff\xd8second\xff\xd9") == [b"\xff\xd8jpeg\xff\xd9", b"\xff\xd8second\xff\xd9"]


def test_mjpeg_bounded_buffer():
    parser = JpegParser()
    with pytest.raises(ValueError):
        parser.feed(b"\xff\xd8" + b"a" * (8 * 1024 * 1024))
    parser = JpegParser()
    parser.feed(b"noise" * 100)
    assert len(parser.buffer) <= 1


def test_sequence_decode_corruption_and_stop(settings, image_bytes):
    folder = Path(settings.source.images_dir)
    folder.mkdir()
    (folder / "002.png").write_bytes(b"corrupt")
    (folder / "001.png").write_bytes(image_bytes)
    source = ImageSource(settings)
    packets = list(source.packets(threading.Event()))
    assert [p.name for p in packets] == ["001.png", "002.png"]
    assert decode(packets[0].data).shape == (48, 64, 3)
    with pytest.raises(ValueError):
        decode(packets[1].data)
    stopped = threading.Event()
    stopped.set()
    assert list(source.packets(stopped)) == []


def test_letterbox_and_decode_preserves_scores(tmp_path):
    rgb = np.full((100, 200, 3), [10, 20, 30], dtype=np.uint8)
    tensor, ratio = letterbox(rgb, 416, 114)
    assert tensor.shape == (1, 3, 416, 416) and ratio == 2.08
    assert list(tensor[0, :, 0, 0]) == [30, 20, 10]
    assert np.all(tensor[0, :, -1, -1] == 114)
    config = ConfigDetector(tmp_path / "x", tmp_path / "y", 416, 114, .1, .45, 100, "test")
    output = np.zeros((1, 3549, 85), dtype=np.float32)
    output[0, 0, :4] = [1, 1, 1, 1]
    output[0, 0, 4], output[0, 0, 5] = .5, .8
    detections = decodificar(output, 1, 416, 416, config, [str(i) for i in range(80)])
    assert len(detections) == 1
    assert detections[0].confidence == float(output[0, 0, 4]) * float(output[0, 0, 5])
    output[0, 0, 1] = np.nan
    with pytest.raises(DetectorError):
        decodificar(output, 1, 416, 416, config, [str(i) for i in range(80)])


def test_model_integrity_rejected(settings, tmp_path):
    path = tmp_path / "bad.onnx"
    path.write_bytes(b"wrong model")
    data = settings.model_dump()
    data["detector"]["model"] = str(path)
    with pytest.raises(ValueError, match="SHA-256"):
        Detector(Settings.model_validate(data))


@pytest.mark.real
def test_real_detector_contract():
    settings = Settings()
    if not settings.path(settings.detector.model).is_file():
        pytest.skip("Pesos ausentes; ejecutar download_model.py")
    detector = Detector(settings)
    image = ROOT / os.getenv('P6_TEST_DEMO_DIR','data/demo') / 'normal/000.png'
    if not image.is_file():
        pytest.skip("Entrada ausente; ejecutar prepare_demo.py")
    output = detector.infer(decode(image.read_bytes()))
    assert not detector.synthetic
    assert output["inference_ms"] > 0
    assert len(output["detections"]) > 0
    assert all(0 <= d["confidence"] <= 1 for d in output["detections"])
    assert all(d["bbox"][0] < d["bbox"][2] for d in output["detections"])
    assert output["candidates"]
