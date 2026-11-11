"""Configuración validada y huella de los valores efectivos (incluye overrides)."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, model_validator

ROOT = Path(__file__).resolve().parents[2]


class Section(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Source(Section):
    kind: Literal["images", "video", "mjpeg"] = "images"
    source_id: str = Field(default="fuente-local-01", min_length=1)
    collection: str | None = None
    dataset_manifest: str | None = None
    url: str | None = None
    images_dir: str = "data/demo/normal"
    video_file: str = "data/media/demo.mp4"
    sample_hz: float = Field(default=2, gt=0, le=60)
    loop: bool = False
    timeout_seconds: float = Field(default=5, gt=0, le=60)
    retry_seconds: float = Field(default=2, gt=0, le=60)

    @model_validator(mode="after")
    def safe_url(self):
        if self.url is None:
            if self.kind == "mjpeg":
                raise ValueError("El adaptador legado MJPEG requiere una URL explícita")
            return self
        url = urlsplit(self.url)
        if (url.scheme != "http" or not url.hostname or url.port != 81
                or url.path != "/stream" or url.query or url.fragment
                or url.username or url.password):
            raise ValueError("URL de cámara: http://<host>:81/stream, sin credenciales")
        return self


class Detector(Section):
    model: str = "modelo/yolox_nano.onnx"
    descriptor: str = "modelo/descriptor.yaml"
    input_size: Literal[416] = 416
    padding: int = Field(default=114, ge=0, le=255)
    score_floor: float = Field(default=.10, gt=0, lt=1)
    nms_iou: float = Field(default=.45, gt=0, le=1)
    max_detections: int = Field(default=100, gt=0, le=1000)


class Confidence(Section):
    lower: float = Field(default=.60, ge=0, le=1)
    upper: float = Field(default=.80, ge=0, le=1)
    window_frames: int = Field(default=5, ge=1)
    min_detections: int = Field(default=5, ge=1)
    reference_windows: int = Field(default=2, ge=1)
    sustained_windows: int = Field(default=2, ge=2)
    increase: float = Field(default=.20, gt=0, le=1)


class Alerts(Section):
    low_min_detections: int = Field(default=1, ge=1)


class Metrics(Section):
    window_seconds: float = Field(default=60, gt=0)


class Storage(Section):
    data_dir: str = "data/runtime"
    database: str = "monitor.sqlite3"

    @model_validator(mode="after")
    def filename(self):
        if not self.database or Path(self.database).name != self.database:
            raise ValueError("database debe ser un nombre de archivo")
        return self


class Server(Section):
    autostart: bool = False


class Settings(Section):
    version: Literal[1] = 1
    source: Source = Field(default_factory=Source)
    detector: Detector = Field(default_factory=Detector)
    confidence: Confidence = Field(default_factory=Confidence)
    alerts: Alerts = Field(default_factory=Alerts)
    metrics: Metrics = Field(default_factory=Metrics)
    storage: Storage = Field(default_factory=Storage)
    server: Server = Field(default_factory=Server)
    media_roots: list[str] = Field(default_factory=lambda: ["data/demo", "data/media", "data/scenarios"])

    @model_validator(mode="after")
    def thresholds(self):
        if not self.detector.score_floor < self.confidence.lower < self.confidence.upper:
            raise ValueError("Exigir 0 < piso < inferior < superior <= 1 para observar las tres zonas")
        return self

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()

    def path(self, value: str) -> Path:
        return (ROOT / value).resolve()

    @property
    def data_dir(self) -> Path:
        return self.path(self.storage.data_dir)


def load_settings(path: str | Path | None = None, *, environ: bool = True) -> Settings:
    if environ:
        load_dotenv(ROOT / ".env", override=False)
    selected = path or (os.getenv("MONITOR_SETTINGS") if environ else None) or "config/settings.yaml"
    selected = Path(selected)
    if not selected.is_absolute():
        selected = ROOT / selected
    data = yaml.safe_load(selected.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("settings.yaml debe contener un mapa")
    if environ:
        for variable, section, key in [
            ("MONITOR_SOURCE", "source", "kind"),
            ("MONITOR_CAMERA_URL", "source", "url"),
            ("MONITOR_IMAGES_DIR", "source", "images_dir"),
            ("MONITOR_VIDEO_FILE", "source", "video_file"),
            ("MONITOR_DATA_DIR", "storage", "data_dir"),
        ]:
            if variable in os.environ:
                data.setdefault(section, {})[key] = os.environ[variable]
        if "MONITOR_AUTOSTART" in os.environ:
            value = os.environ["MONITOR_AUTOSTART"].lower()
            if value not in {"true", "false"}:
                raise ValueError("MONITOR_AUTOSTART debe ser true o false")
            data.setdefault("server", {})["autostart"] = value == "true"
    return Settings.model_validate(data)
