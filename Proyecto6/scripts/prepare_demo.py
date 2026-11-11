"""Prepara secuencias públicas pequeñas; transformaciones de píxeles, nunca de scores."""
from __future__ import annotations

import argparse
from io import BytesIO
import hashlib
import json
from pathlib import Path
import urllib.request

from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
URL = "https://raw.githubusercontent.com/Megvii-BaseDetection/YOLOX/main/assets/dog.jpg"
DEMO_SHA256 = "5a9522051c3cec2bbd2f6323fccba32e8fbf3ddcc2b3e2fd46b04c720bc6f866"


def prepare(destination: Path, input_path: Path | None = None) -> dict:
    destination.mkdir(parents=True, exist_ok=True)
    source_path = destination / "source.jpg"
    if input_path:
        original = input_path.read_bytes()
        origin = {"kind": "user_image", "name": input_path.name}
    elif source_path.exists():
        original = source_path.read_bytes()
        origin = {"kind": "public_demo", "url": URL}
    else:
        with urllib.request.urlopen(URL, timeout=30) as response:
            original = response.read(10 * 1024 * 1024)
        origin = {"kind": "public_demo", "url": URL}
    if not input_path and hashlib.sha256(original).hexdigest() != DEMO_SHA256:
        raise ValueError("La entrada pública cambió: no corresponde al SHA-256 de referencia")
    source_path.write_bytes(original)
    with Image.open(BytesIO(original)) as source:
        image = source.convert("RGB")
        image.thumbnail((960, 960))
    manifest = {"origin": origin, "source_sha256": hashlib.sha256(original).hexdigest(),
                "note": "Variaciones correlacionadas de una escena; no son observaciones independientes ni validación de calidad.",
                "inputs": []}
    variants = [("normal", i, {"brightness": brightness, "blur": 0})
                for i, brightness in enumerate([1, .95, 1.05, .9, 1.1, .98, 1.02, .92, 1.08, 1])]
    variants += [("baja-confianza", i, {"brightness": brightness, "blur": blur})
                 for i, (brightness, blur) in enumerate([(.8, 2), (.65, 3), (.5, 4), (.8, 5), (.6, 6), (.7, 2), (.55, 3), (.9, 4), (.7, 5), (.5, 6)])]
    for scenario, index, transform in variants:
        modified = ImageEnhance.Brightness(image).enhance(transform["brightness"])
        if transform["blur"]:
            modified = modified.filter(ImageFilter.GaussianBlur(transform["blur"]))
        relative = f"{scenario}/{index:03d}.png"
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        modified.save(path, format="PNG")
        manifest["inputs"].append({"path": relative, "transform": transform,
                                   "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "data/demo")
    parser.add_argument("--input", type=Path)
    args = parser.parse_args()
    result = prepare(args.output, args.input)
    print(f"Preparadas {len(result['inputs'])} imágenes; fuente sha256={result['source_sha256']}")
