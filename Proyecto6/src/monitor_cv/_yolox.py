# Adaptado de Proyecto5/src/p5/detector_onnx.py; ver PROCEDENCIA.md.
"""Detector real (P5-04, #56): YOLOX-Nano en ONNX Runtime CPU sobre cuadros completos.

Cumple la interfaz `Detector` del recorrido (P5-14): `nombre`, `model_sha256`, `synthetic`
y `detectar(frame) -> list[Detection]`. Solo lee los bytes de la imagen indicada por
`frame.image_path`: no abre anotaciones ni usa el nombre del archivo para decidir.

Preprocesamiento (letterbox de YOLOX): la imagen RGB se escala por
`r = min(S/H, S/W)` con Pillow BILINEAR, se pega arriba a la izquierda en un lienzo SxS
gris `relleno` y se pasa a BGR, NCHW, float32 0-255 sin normalizar.

Posprocesamiento: se decodifica la rejilla (strides 8/16/32), `score = objectness x
prob_clase` con la mejor clase por ancla, se descarta lo menor a `umbral_confianza`, NMS
por clase con `nms_iou`, cajas `xyxy` divididas entre `r` (pixeles del cuadro original)
y recortadas a sus bordes. Una caja que queda sin area se descarta.
Adaptación P6: puntuaciones fuera de [0,1] se rechazan, no se sustituyen.

Fallos: imagen ilegible, salida con forma inesperada o valores no finitos levantan
`DetectorError`; el recorrido lo registra como `status=error` (nunca via libre).
Pesos con otro SHA-256 o config invalida levantan `ModeloInvalidoError` al cargar.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import numpy as np
import yaml
from PIL import Image

from .events import Detection

STRIDES = (8, 16, 32)
NOMBRE = "yolox_nano"


class DetectorError(RuntimeError):
    """Un cuadro no se pudo procesar; el recorrido lo registra como `status=error`."""


class ModeloInvalidoError(ValueError):
    """Configuracion, pesos o descriptor rechazados al cargar el detector."""


class Sesion(Protocol):
    """Lo que se usa de `onnxruntime.InferenceSession` (inyectable en pruebas)."""

    def run(self, output_names: Any, input_feed: dict[str, np.ndarray]) -> list[np.ndarray]: ...


@dataclass(frozen=True)
class ConfigDetector:
    modelo: Path
    descriptor: Path
    tamano_entrada: int
    relleno: int
    umbral_confianza: float
    nms_iou: float
    max_detecciones: int
    config_sha256: str


def sha256_archivo(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        while bloque := f.read(1 << 20):
            h.update(bloque)
    return h.hexdigest()


def leer_imagen(ruta: str | Path) -> np.ndarray:
    """Decodifica la imagen completa a RGB uint8 HxWx3; si no se puede, `DetectorError`."""
    try:
        with Image.open(ruta) as im:
            im.load()
            return np.asarray(im.convert("RGB"))
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        raise DetectorError(f"imagen ilegible: {type(exc).__name__}: {exc}") from exc


def letterbox(rgb: np.ndarray, tamano: int, relleno: int) -> tuple[np.ndarray, float]:
    """Tensor NCHW BGR float32 y la escala `r` para regresar al cuadro original."""
    alto, ancho = rgb.shape[:2]
    r = min(tamano / alto, tamano / ancho)
    nuevo_ancho, nuevo_alto = int(ancho * r), int(alto * r)
    escalada = Image.fromarray(rgb).resize((nuevo_ancho, nuevo_alto), Image.BILINEAR)
    lienzo = np.full((tamano, tamano, 3), relleno, dtype=np.uint8)
    lienzo[:nuevo_alto, :nuevo_ancho] = np.asarray(escalada)
    bgr = lienzo[:, :, ::-1]
    return np.ascontiguousarray(bgr.transpose(2, 0, 1)[None], dtype=np.float32), r


def _rejilla(tamano: int) -> tuple[np.ndarray, np.ndarray]:
    rejillas, strides = [], []
    for stride in STRIDES:
        lado = tamano // stride
        yv, xv = np.meshgrid(np.arange(lado), np.arange(lado), indexing="ij")
        rejillas.append(np.stack((xv, yv), 2).reshape(-1, 2))
        strides.append(np.full((lado * lado, 1), stride))
    return np.concatenate(rejillas).astype(np.float32), np.concatenate(strides).astype(np.float32)


def nms(cajas: np.ndarray, scores: np.ndarray, iou_max: float) -> list[int]:
    """Indices que sobreviven al NMS, en orden de confianza descendente."""
    orden = scores.argsort()[::-1]
    areas = (cajas[:, 2] - cajas[:, 0]) * (cajas[:, 3] - cajas[:, 1])
    quedan: list[int] = []
    while orden.size:
        i = int(orden[0])
        quedan.append(i)
        resto = orden[1:]
        x1 = np.maximum(cajas[i, 0], cajas[resto, 0])
        y1 = np.maximum(cajas[i, 1], cajas[resto, 1])
        x2 = np.minimum(cajas[i, 2], cajas[resto, 2])
        y2 = np.minimum(cajas[i, 3], cajas[resto, 3])
        inter = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)
        iou = inter / np.maximum(areas[i] + areas[resto] - inter, 1e-9)
        orden = resto[iou <= iou_max]
    return quedan


def decodificar(
    salida: np.ndarray,
    r: float,
    ancho: int,
    alto: int,
    config: ConfigDetector,
    clases: list[str],
) -> list[Detection]:
    """Salida cruda `[1, N, 5 + C]` de YOLOX a detecciones en pixeles del cuadro original."""
    anclas = sum((config.tamano_entrada // s) ** 2 for s in STRIDES)
    esperada = (1, anclas, 5 + len(clases))
    if salida.shape != esperada:
        raise DetectorError(f"salida malformada: forma {salida.shape}, se esperaba {esperada}")
    if not np.isfinite(salida).all():
        raise DetectorError("salida no finita del modelo (NaN o infinito)")
    o = salida[0].astype(np.float64)
    rejilla, strides = _rejilla(config.tamano_entrada)
    centro = (o[:, :2] + rejilla) * strides
    with np.errstate(over="ignore"):
        lados = np.exp(o[:, 2:4]) * strides
    cajas = np.concatenate((centro - lados / 2, centro + lados / 2), axis=1) / r
    por_clase = o[:, 4:5] * o[:, 5:]
    clase = por_clase.argmax(1)
    score = por_clase.max(1)
    sel = score >= config.umbral_confianza
    cajas, clase, score = cajas[sel], clase[sel], score[sel]
    if not np.isfinite(cajas).all() or not np.isfinite(score).all():
        raise DetectorError("salida no finita al decodificar las cajas")
    cajas[:, [0, 2]] = cajas[:, [0, 2]].clip(0, ancho)
    cajas[:, [1, 3]] = cajas[:, [1, 3]].clip(0, alto)
    detecciones: list[Detection] = []
    for c in np.unique(clase):
        idx = np.flatnonzero(clase == c)
        for k in nms(cajas[idx], score[idx], config.nms_iou):
            x1, y1, x2, y2 = (round(float(v), 2) for v in cajas[idx[k]])
            if x1 < x2 and y1 < y2:
                conf = float(score[idx[k]])
                if not 0 <= conf <= 1:
                    raise DetectorError("score fuera de [0,1]")
                detecciones.append(Detection(clases[int(c)], int(c), conf, (x1, y1, x2, y2)))
    detecciones.sort(key=lambda d: d.confidence, reverse=True)
    return detecciones[: config.max_detecciones]

