"""Registra un error real de decodificación y una imagen CC BY; ejecutar con productor detenido."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from monitor_cv.config import Settings,load_settings
from monitor_cv.events import uid
from monitor_cv.service import MonitorService


def run():
    selection=json.loads((ROOT/'config/dataset-selection-public.json').read_text(encoding='utf-8'))
    item=next(i for i in selection['images'] if i['image_id']=='488d4412c71bf3f1')
    source=ROOT/item['path']
    if hashlib.sha256(source.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('SHA de entrada incorrecto')
    folder=ROOT/'data/media'/uid('technical');folder.mkdir(parents=True)
    (folder/'000-invalid.jpg').write_bytes(b'DEMOSTRACION TECNICA: entrada corrupta deliberada; no es una imagen')
    shutil.copyfile(source,folder/'001-valid.jpg')
    data=load_settings(environ=False).model_dump()
    data['source'].update(kind='images',images_dir=folder.relative_to(ROOT).as_posix(),source_id=folder.name,sample_hz=4,loop=False,collection=None,dataset_manifest=None)
    service=MonitorService(Settings.model_validate(data));run_id=service.start()
    service.thread.join(30)
    if service.thread.is_alive():service.stop();raise TimeoutError('La demostración no terminó')
    events=list(reversed(service.db.list('events',run_id)))
    ok=len(events)==2 and events[0]['status']=='decode_error' and events[0]['image_ref'] is None and events[1]['inference_executed']
    result={'run_id':run_id,'controlled_corrupt_input':True,'ok':ok,'events':[{k:e[k] for k in ['id','status','image_ref','inference_executed']} for e in events],
            'valid_input_attribution':{k:item[k] for k in ['image_id','author','title','landing_url','license_url','sha256']},
            'new_original_photographs':0}
    print(json.dumps(result,ensure_ascii=False))
    if not ok:raise RuntimeError('No se observó la secuencia esperada')
    return result


if __name__=='__main__':run()
