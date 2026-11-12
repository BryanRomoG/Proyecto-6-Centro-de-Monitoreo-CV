"""Prepara entradas nuevas con atribución CC BY, conservando cualquier demo anterior."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from prepare_demo import prepare

ROOT=Path(__file__).resolve().parents[1]
IMAGE_ID='488d4412c71bf3f1'


def prepare_authorized(destination: Path | None=None):
    destination=destination or ROOT/'data/demo'
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('El destino contiene archivos; conservarlos y elegir otro destino')
    selection=json.loads((ROOT/'config/dataset-selection.json').read_text(encoding='utf-8'))
    item=next(i for i in selection['images'] if i['image_id']==IMAGE_ID)
    path=ROOT/item['path']
    if hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
        raise ValueError('La imagen autorizada no coincide con el SHA esperado')
    manifest=prepare(destination,input_path=path)
    manifest['origin']={k:item[k] for k in ['image_id','author','author_url','title','original_url','landing_url','license_url','sha256']}
    manifest['origin']['dataset']='Open Images'
    manifest['note']='Variaciones de píxeles de una foto CC BY; no son escenas independientes. Scores producidos exclusivamente por YOLOX.'
    (destination/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'data/demo')
    args=parser.parse_args()
    result=prepare_authorized(args.output)
    print(json.dumps({'images':len(result['inputs']),'image_id':IMAGE_ID}))
