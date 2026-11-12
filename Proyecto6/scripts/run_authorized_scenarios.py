"""C1/C2, video y S1–S7 con fotos CC BY; nunca descarga dog.jpg ni modifica evidencias previas."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from monitor_cv.config import Settings,load_settings
from monitor_cv.detector import Detector
from monitor_cv.camera import decode
from monitor_cv.events import uid,utc_now
from monitor_cv.datasets import permitted_license
from run_scenarios import run_suite,save_json

EXCLUDED='26557008b4fcf408'


def run(output:Path,*,base:Settings|None=None):
    data=(base or load_settings(environ=False)).model_dump()
    if base is None:data['storage']['data_dir']='data/runtime/'+uid('authorized')
    base=Settings.model_validate(data)
    manifest=json.loads((ROOT/'data/media/datasets/manifest.json').read_text(encoding='utf-8'))
    detector=Detector(base);observations=[]
    for item in manifest['images']:
        if item['image_id']==EXCLUDED:continue
        if not permitted_license(item['license_url']):raise ValueError('Licencia no permitida')
        path=ROOT/item['path'];raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=item['sha256']:raise ValueError('SHA de entrada incorrecto')
        detections=detector.infer(decode(raw))['detections']
        low=sum(d['confidence']<base.confidence.lower for d in detections)
        observations.append({'name':item['image_id'],'path':item['path'],'sha256':item['sha256'],
                             'detections':detections,'count':len(detections),'low':low,
                             'ratio':low/len(detections) if detections else None,
                             'attribution':{k:item.get(k) for k in ['author','author_url','title','original_url','landing_url','license_url']}})
    eligible=[r for r in observations if r['count']]
    reference=min(eligible,key=lambda r:r['ratio']);changed=max(eligible,key=lambda r:r['ratio'])
    empty=next((r for r in observations if not r['count']),None)
    calibration={'timestamp':utc_now(),'observations':observations,'reference':reference['name'],
                 'changed':changed['name'],'empty':empty['name'] if empty else None,
                 'gap':changed['ratio']-reference['ratio'],
                 'method':'Exploración real de fotos existentes; política fijada antes de la ejecución. No altera puntuaciones.',
                 'new_original_photographs':0,'excluded_image_id':EXCLUDED}
    media=ROOT/'data/scenarios'/uid('authorized-media');media.mkdir(parents=True)
    video=media/'demo.mp4'
    writer=cv2.VideoWriter(str(video),cv2.VideoWriter_fourcc(*'mp4v'),8,(640,480))
    if not writer.isOpened():raise ValueError('No se pudo crear MP4')
    try:
        for row in [reference,changed]:
            with Image.open(ROOT/row['path']) as im:rgb=np.asarray(im.convert('RGB').resize((640,480)))
            for _ in range(20):writer.write(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR))
    finally:writer.release()
    # run_suite usa rutas absolutas solo en memoria para acceder a las fotos.
    paths=lambda row:None if row is None else {**row,'path':str(ROOT/row['path'])}
    results=run_suite(output,base=base,authorized_inputs={'reference':paths(reference),'changed':paths(changed),
                           'empty':paths(empty),'calibration':calibration,'video':video})
    save_json(output/'authorized-inputs.json',{'calibration':calibration,'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
                    'unique_source_photographs':len({reference['sha256'],changed['sha256']}|({empty['sha256']} if empty else set())),
                    'frames_reused_explicitly':True,'new_original_photographs':0})
    return results


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    output=args.output or ROOT/'evidencias/publicacion_segura/escenarios'/uid('authorized')
    result=run(output)
    print(json.dumps({'output':output.relative_to(ROOT).as_posix(),'results':{k:r['observed'] for k,r in result.items()}}))
    raise SystemExit(0 if all(r['observed'] for r in result.values()) else 1)
