import hashlib
from pathlib import Path
import urllib.request

import pytest

from download_model import HashNoCoincideError, descargar, leer_descriptor


def test_download_hash_size_and_atomicity(tmp_path, monkeypatch):
    import io
    class Response(io.BytesIO):
        pass
    data = b"test-model-payload"
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: Response(data))
    target = tmp_path / "model.onnx"
    digest = hashlib.sha256(data).hexdigest()
    descargar("https://example.invalid/model", target, digest, len(data))
    assert target.read_bytes() == data
    with pytest.raises(HashNoCoincideError):
        descargar("https://example.invalid/model", target, "0" * 64, len(data))
    assert target.read_bytes() == data
    assert not target.with_name("model.onnx.parcial").exists()
    with pytest.raises(HashNoCoincideError):
        descargar("https://example.invalid/model", target, digest, len(data) + 1)


def test_descriptor_rejects_path_escape(tmp_path):
    path = tmp_path / "descriptor.yaml"
    path.write_text('archivo: ../escape.onnx\nurl: https://example.invalid\nbytes: 2\nsha256: "' + "0" * 64 + '"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="sin carpetas"):
        leer_descriptor(path)
