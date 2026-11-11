"""Prepara un MP4 reproducible desde la escena pública; no requiere cámara física."""
import hashlib
import json
from pathlib import Path

import cv2
from PIL import Image
import numpy as np

from prepare_demo import prepare

ROOT=Path(__file__).resolve().parents[1]


def prepare_media():
    if not (ROOT/'data/demo/manifest.json').exists():
        prepare(ROOT/'data/demo')
    folder=ROOT/'data/media'
    folder.mkdir(parents=True,exist_ok=True)
    output=folder/'demo.mp4'
    # No sobreescribir entradas previas si su archivo ya es verificable.
    if output.exists() and (folder/'manifest.json').exists():
        old=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
        if hashlib.sha256(output.read_bytes()).hexdigest()==old['sha256']:
            return old
        raise ValueError('El video existente cambió; conservarlo y usar otro nombre antes de regenerar')
    writer=cv2.VideoWriter(str(output),cv2.VideoWriter_fourcc(*'mp4v'),8,(640,480))
    if not writer.isOpened():
        raise ValueError('OpenCV no pudo crear MP4 con mp4v')
    inputs=[]
    try:
        for name in ['normal','baja-confianza']:
            for path in sorted((ROOT/'data/demo'/name).glob('*.png')):
                with Image.open(path) as im:
                    rgb=np.asarray(im.convert('RGB').resize((640,480),Image.Resampling.BILINEAR))
                for _ in range(2):
                    writer.write(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR))
                inputs.append({'path':path.relative_to(ROOT).as_posix(),
                               'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'repetitions':2})
    finally:
        writer.release()
    manifest={'path':'data/media/demo.mp4','fps':8,'frames':40,'source':'Archivo generado de imágenes públicas, no cámara',
              'codec':'mp4v','size':[640,480],'inputs':inputs,'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    return manifest


if __name__=='__main__':
    print(json.dumps(prepare_media(),indent=2))
