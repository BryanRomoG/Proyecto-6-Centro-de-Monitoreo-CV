"""Identidad y serialización de observaciones; sin políticas de movimiento."""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from uuid import uuid4


@dataclass(frozen=True)
class Detection:
    # Contrato mínimo adaptado de Proyecto5/src/p5/contrato.py.
    class_name: str
    class_id: int
    confidence: float
    bbox: tuple[float, float, float, float]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
