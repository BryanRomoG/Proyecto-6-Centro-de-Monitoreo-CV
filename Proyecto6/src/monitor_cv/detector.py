"""YOLOX-Nano real, sesión CPU y observaciones sin modificar puntuaciones."""
from __future__ import annotations

from dataclasses import asdict
from time import perf_counter

import numpy as np
import onnxruntime as ort
import yaml

from ._yolox import ConfigDetector, DetectorError, decodificar, letterbox, sha256_archivo
from .config import Settings


class Detector:
    synthetic = False

    def __init__(self, settings: Settings):
        d = settings.detector
        model, descriptor = settings.path(d.model), settings.path(d.descriptor)
        info = yaml.safe_load(descriptor.read_text(encoding="utf-8"))
        if not model.is_file():
            raise ValueError("Falta modelo: ejecutar python scripts/download_model.py --destino modelo")
        obtained = sha256_archivo(model)
        if obtained != info["sha256"] or model.stat().st_size != info["bytes"]:
            raise ValueError("Modelo rechazado: SHA-256 o tamaño no coincide con descriptor")
        self.classes = info["clases"]
        if not isinstance(self.classes, list) or len(self.classes) != 80:
            raise ValueError("Descriptor debe identificar las 80 clases COCO")
        self.config = ConfigDetector(model, descriptor, d.input_size, d.padding, d.score_floor,
                                     d.nms_iou, d.max_detections, settings.fingerprint)
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        options.inter_op_num_threads = 1
        self.session = ort.InferenceSession(str(model), sess_options=options,
                                            providers=["CPUExecutionProvider"])
        entry = self.session.get_inputs()[0]
        if entry.shape != [1, 3, d.input_size, d.input_size] or entry.type != "tensor(float)":
            raise ValueError(f"Entrada ONNX incompatible: {entry.shape} {entry.type}")
        self.input_name = entry.name
        self.identity = {"name": info["nombre"], "version": info["version"],
                         "sha256": obtained, "descriptor_sha256": sha256_archivo(descriptor),
                         "runtime": f"onnxruntime=={ort.__version__}",
                         "providers": self.session.get_providers(), "classes": self.classes,
                         "preprocessing": f"Pillow bilinear letterbox top-left {d.input_size} padding{d.padding} BGR NCHW float32 0-255"}

    def infer(self, rgb: np.ndarray) -> dict:
        height, width = rgb.shape[:2]
        start = perf_counter()
        tensor, ratio = letterbox(rgb, self.config.tamano_entrada, self.config.relleno)
        before = perf_counter()
        try:
            output = np.asarray(self.session.run(None, {self.input_name: tensor})[0])
        except Exception as exc:
            raise DetectorError(f"ONNX Runtime: {type(exc).__name__}: {exc}") from exc
        after = perf_counter()
        detections = decodificar(output, ratio, width, height, self.config, self.classes)
        probabilities = output[0, :, 4:5].astype(np.float64) * output[0, :, 5:].astype(np.float64)
        scores = probabilities.max(1)
        candidates = [{"anchor": int(i), "class_id": int(probabilities[i].argmax()),
                       "confidence": float(scores[i])}
                      for i in np.flatnonzero(scores >= self.config.umbral_confianza)]
        return {"width": width, "height": height,
                "inference_ms": (after - before) * 1000,
                "preprocess_ms": (before - start) * 1000,
                "postprocess_ms": (perf_counter() - after) * 1000,
                "detections": [asdict(d) for d in detections], "candidates": candidates}
