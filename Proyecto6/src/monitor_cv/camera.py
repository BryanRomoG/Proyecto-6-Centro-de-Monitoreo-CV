"""Fuentes progresivas: secuencia finita o último JPEG fresco de la ESP32-CAM."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
import threading
import time

import cv2
import numpy as np
from PIL import Image

from ._mjpeg import ReconnectingStream
from .config import Settings
from .events import utc_now


@dataclass
class Packet:
    name: str
    captured_at: str | None
    data: bytes | None
    error: str | None = None
    frame_index: int | None = None
    position_seconds: float | None = None
    total_frames: int | None = None
    read_frames: int = 1
    discarded_frames: int = 0
    read_elapsed_s: float = 0.0


def decode(data: bytes) -> np.ndarray:
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Imagen recibida no decodificable")
    height, width = frame.shape[:2]
    if height * width > 25_000_000:
        raise ValueError("Imagen supera 25 megapíxeles")
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def png_bytes(rgb: np.ndarray) -> bytes:
    out = BytesIO()
    Image.fromarray(rgb).save(out, format="PNG")
    return out.getvalue()


class ImageSource:
    def __init__(self, settings: Settings):
        self.directory = settings.path(settings.source.images_dir)
        if not self.directory.is_dir():
            raise ValueError(f"No existe la secuencia: {self.directory}")
        self.paths = sorted(p for p in self.directory.iterdir()
                            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
        if not self.paths:
            raise ValueError("Secuencia sin imágenes; preparar entradas con scripts/prepare_demo.py")
        self.loop = settings.source.loop
        self.sample_hz = settings.source.sample_hz

    def packets(self, stop: threading.Event):
        while not stop.is_set():
            for index, path in enumerate(self.paths):
                if stop.is_set():
                    return
                try:
                    started = time.perf_counter()
                    data = path.read_bytes()
                    yield Packet(path.name, utc_now(), data, frame_index=index,
                                 position_seconds=index / self.sample_hz, total_frames=len(self.paths),
                                 read_elapsed_s=time.perf_counter() - started)
                except OSError as exc:
                    yield Packet(path.name, None, None, f"Lectura de imagen: {exc}", frame_index=index,
                                 total_frames=len(self.paths), read_frames=0)
            if not self.loop:
                return

    def close(self):
        pass


class MjpegSource:
    def __init__(self, settings: Settings):
        s = settings.source
        self.timeout = s.timeout_seconds
        self.reader = ReconnectingStream(s.url, s.timeout_seconds, s.timeout_seconds, s.retry_seconds)
        # Un JPEG idéntico no renueva su fecha: conserva la política del lector P5.
        self.reader.thread.start()

    def packets(self, stop: threading.Event):
        last = None
        while not stop.is_set():
            deadline = time.monotonic() + self.timeout
            while not stop.is_set():
                latest = self.reader.snapshot()
                if (latest and latest[1] != last and
                        self.reader.is_current(latest[1], self.timeout, time.monotonic())):
                    last = latest[1]
                    stamp = datetime.fromtimestamp(last / 1e9, timezone.utc).isoformat()
                    yield Packet(f"mjpeg-{last}", stamp, latest[0])
                    break
                if self.reader.error or time.monotonic() >= deadline:
                    yield Packet("mjpeg-error", None, None,
                                 self.reader.error or "Sin JPEG fresco; reconexión automática activa")
                    break
                stop.wait(.05)

    def close(self):
        self.reader.close()


def open_source(settings: Settings):
    if settings.source.kind == "images":
        return ImageSource(settings)
    if settings.source.kind == "video":
        return VideoSource(settings)
    return MjpegSource(settings)  # Adaptador legado opcional; no se ofrece en el portal.


class VideoSource:
    """Lectura secuencial: todos los frames se leen, solo posiciones muestreadas se infieren."""
    def __init__(self, settings: Settings):
        self.path = settings.path(settings.source.video_file)
        if not self.path.is_file():
            raise ValueError("No existe el archivo de video")
        self.capture = cv2.VideoCapture(str(self.path))
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.total = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.sample_hz = settings.source.sample_hz
        self.loop = settings.source.loop
        if not self.capture.isOpened() or not np.isfinite(self.fps) or self.fps <= 0 or self.total <= 0:
            self.close()
            raise ValueError("Video inválido, vacío o sin FPS/longitud verificables")
        ok, first = self.capture.read()
        if not ok or first is None:
            self.close()
            raise ValueError("Video sin primer frame decodificable")
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def packets(self, stop: threading.Event):
        while not stop.is_set():
            index, read, skipped, next_time, elapsed = 0, 0, 0, 0., 0.
            while not stop.is_set() and index < self.total:
                start = time.perf_counter()
                ok, bgr = self.capture.read()
                elapsed += time.perf_counter() - start
                if not ok or bgr is None:
                    yield Packet(self.path.name, None, None,
                                 f"Lectura de video falló antes del final declarado: frame {index}/{self.total}",
                                 frame_index=index, total_frames=self.total, read_frames=read,
                                 discarded_frames=skipped, read_elapsed_s=elapsed)
                    return
                read += 1
                position = index / self.fps
                if position + 1e-9 >= next_time or index == self.total-1:
                    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                    yield Packet(self.path.name, utc_now(), png_bytes(rgb), frame_index=index,
                                 position_seconds=position, total_frames=self.total,
                                 read_frames=read, discarded_frames=skipped, read_elapsed_s=elapsed)
                    next_time += 1 / min(self.sample_hz, self.fps)
                    read, skipped, elapsed = 0, 0, 0.
                else:
                    skipped += 1
                index += 1
            if not self.loop:
                return
            if not self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0):
                raise ValueError("El códec no permite reiniciar el video")

    def close(self):
        self.capture.release()
