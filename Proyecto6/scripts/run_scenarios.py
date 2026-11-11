"""Ejecuta base y extras con salidas reales; fallos inyectados se identifican explícitamente."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

import numpy as np
from PIL import Image,ImageEnhance,ImageFilter

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from monitor_cv.camera import ImageSource,decode
from monitor_cv.analytics import extras
from monitor_cv.config import Settings,load_settings
from monitor_cv.detector import Detector
from monitor_cv.events import json_text,uid,utc_now
from monitor_cv.service import MonitorService
from prepare_media import prepare_media
from run_demo import code_manifest
from verify_metrics import verify


def save_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')


def export(service,run_id,output):
    output.mkdir(parents=True,exist_ok=False)
    for table in ['events','alerts','windows','actions']:
        rows=list(reversed(service.db.list(table,run_id)))
        (output/(table+'.jsonl')).write_text(''.join(json_text(r)+'\n' for r in rows),encoding='utf-8')
        if table=='events':
            for e in rows:
                if e['image_ref']:
                    destination=output/e['image_ref']
                    destination.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(service.settings.data_dir/e['image_ref'],destination)
    save_json(output/'run.json',service.db.get('runs',run_id))
    save_json(output/'metrics.json',service.metrics(run_id))
    save_json(output/'extras.json',extras(service.db.list('events',run_id),service.db.list('alerts',run_id),service.settings.data_dir,cutoff=utc_now(),windows=service.db.list('windows',run_id)))
    save_json(output/'code-sha256.json',code_manifest())
    save_json(output/'metric-verification.json',verify(output))


def settings_for(base,folder,source_id,*,video=False):
    data=base.model_dump()
    data['source'].update(kind='video' if video else 'images',source_id=source_id,sample_hz=20,loop=False)
    data['source']['video_file' if video else 'images_dir']=str(folder.resolve())
    return Settings.model_validate(data)


def calibration(root,base):
    folder=root/'calibration'
    folder.mkdir(parents=True,exist_ok=True)
    detector=Detector(base)
    with Image.open(ROOT/'data/demo/source.jpg') as im:
        image=im.convert('RGB')
    variants=[('original',image,{'identity':True}),
              ('dog-crop',image.crop((110,180,350,555)),{'crop':[110,180,350,555]})]
    for blur in [2,4,6,8,12,16]:
        for brightness in [.35,.65,1.]:
            modified=ImageEnhance.Brightness(image).enhance(brightness).filter(ImageFilter.GaussianBlur(blur))
            variants.append((f'blur-{blur}-brightness-{brightness}',modified,{'blur':blur,'brightness':brightness}))
    for index,box in enumerate([(0,520,90,575),(0,0,70,70),(600,450,750,570),(10,350,90,430)]):
        variants.append((f'background-{index}',image.crop(box),{'crop':box,'background_candidate':True}))
    observations=[]
    for name,im,transform in variants:
        path=folder/(name+'.png')
        im.save(path)
        result=detector.infer(decode(path.read_bytes()))
        detections=result['detections']
        count=len(detections)
        low=sum(d['confidence']<base.confidence.lower for d in detections)
        observations.append({'name':name,'path':str(path),'transform':transform,
                             'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                             'detections':detections,'count':count,'low':low,'ratio':low/count if count else None})
    eligible=[r for r in observations if r['count']]
    reference=min(eligible,key=lambda r:r['ratio'])
    changed=max(eligible,key=lambda r:r['ratio'])
    empty=next((r for r in observations if r['count']==0 and r['transform'].get('background_candidate')),None)
    summary={'timestamp':utc_now(),'model':detector.identity,'config':base.model_dump(),
             'observations':observations,'reference':reference['name'],'changed':changed['name'],
             'gap':changed['ratio']-reference['ratio'],'empty':empty['name'] if empty else None,
             'method':'Selección por inferencias exploratorias; luego nueva ejecución con política fijada y scores sin cambios.'}
    save_json(root/'calibration.json',summary)
    return reference,changed,empty,summary


def sequence(folder,paths):
    folder.mkdir(parents=True,exist_ok=True)
    for i,path in enumerate(paths):
        shutil.copyfile(path,folder/f'{i:03}.png')
    return folder


class InterruptedImages(ImageSource):
    """Interrupción REAL de archivo nuevo; nunca toca entradas/evidencias anteriores."""
    def packets(self,stop):
        iterator=super().packets(stop)
        for index,path in enumerate(self.paths):
            if index==1:
                backup=path.with_suffix('.suspendido')
                path.rename(backup)
                try:
                    yield next(iterator)
                finally:
                    backup.rename(path)
            else:
                yield next(iterator)


class InjectedFailureDetector(Detector):
    """S7: un fallo simulado del adaptador; los demás intentos sí ejecutan ONNX."""
    def __init__(self,settings):
        super().__init__(settings)
        self.calls=0

    def infer(self,rgb):
        self.calls+=1
        if self.calls==2:
            raise RuntimeError('S7: fallo de inferencia INYECTADO; ONNX no ejecutado en este intento')
        return super().infer(rgb)


def run_suite(output:Path,*,base:Settings|None=None):
    prepare_media()
    base=base or load_settings(environ=False)
    output.mkdir(parents=True,exist_ok=False)
    inputs=ROOT/'data/scenarios'/output.name
    inputs.mkdir(parents=True,exist_ok=False)
    reference,changed,empty,cal=calibration(inputs,base)
    normal=ROOT/'data/demo/normal/000.png'
    results={}
    services={}

    def execute(name,config,*,factory=Detector,source_factory=None,expectation,accept):
        service=MonitorService(config,detector_factory=factory,source_factory=source_factory)
        run=service.start()
        service.thread.join(60)
        if service.thread.is_alive():
            service.stop()
            raise RuntimeError('Escenario no terminó en el plazo configurado')
        events=list(reversed(service.db.list('events',run)))
        alerts=service.db.list('alerts',run)
        windows=list(reversed(service.db.list('windows',run)))
        observed=accept(events,alerts,windows) and service.error is None
        export(service,run,output/name)
        result={'scenario':name,'run_id':run,'expectation':expectation,'observed':observed,
                'event_statuses':[e['status'] for e in events],
                'event_ids':[e['id'] for e in events],'alert_ids':[a['id'] for a in alerts],
                'config_sha256':config.fingerprint,'model_sha256':service.db.get('runs',run)['model']['sha256'],
                'fault_simulated':name=='S7','portal_verification':'Pendiente de recorrido HTTP/navegador en esta nueva ejecución',
                'scope':'Éxitos con YOLOX real; cada intento fallido indica inference_executed=false'}
        save_json(output/name/'result.json',result)
        results[name]=result
        services[name]=service
        return events,alerts,windows

    good=lambda es,aa,ww:bool(es) and all(e['status'] in {'ok','no_detections'} and e['inference_executed'] for e in es)
    execute('C1',settings_for(base,ROOT/'data/demo/normal','C1-imagenes'),expectation='Fuente progresiva y 10 inferencias reales persistidas',accept=good)
    execute('C2',settings_for(base,ROOT/'data/demo/baja-confianza','C2-imagenes'),
            expectation='Puntuaciones bajas reales, capturas y alertas según configuración fija',
            accept=lambda es,aa,ww:good(es,aa,ww) and any(a['rule_id']=='low-confidence-v1' for a in aa))
    video=settings_for(base,ROOT/'data/media/demo.mp4','video-local',video=True)
    values=video.model_dump();values['source']['sample_hz']=4
    execute('Video',Settings.model_validate(values),expectation='MP4 real, posiciones, muestreo y descarte contable',
            accept=lambda es,aa,ww:good(es,aa,ww) and sum(e['read_frames'] for e in es)==40 and sum(e['discarded_frames'] for e in es)>0)
    folder=sequence(inputs/'S1',[normal]*4)
    execute('S1',settings_for(base,folder,'S1-interrupcion'),source_factory=InterruptedImages,
            expectation='Archivo interrumpido produce source_error y siguientes frames reales recuperan el procesamiento',
            accept=lambda es,aa,ww:len(es)==4 and es[1]['status']=='source_error' and es[2]['inference_executed'])
    if empty:
        folder=sequence(inputs/'S2',[Path(empty['path'])]*3)
        execute('S2',settings_for(base,folder,'S2-sin-objetos'),expectation='Recorte fotográfico real sin detecciones ni alerta baja',
                accept=lambda es,aa,ww:all(e['status']=='no_detections' and e['detections']==[] and e['inference_executed'] for e in es) and not aa)
    else:
        results['S2']={'scenario':'S2','observed':False,'pending':'No se encontró recorte real sin detecciones; no se fabricó puntuación'}
    folder=sequence(inputs/'S3',[normal])
    execute('S3',settings_for(base,folder,'S3-poca-evidencia'),expectation='Una muestra no completa la ventana ni declara normalidad',
            accept=lambda es,aa,ww:len(es)==1 and not ww and es[0]['confidence_state']=='insufficient_evidence')
    if cal['gap']>=base.confidence.increase:
        folder=sequence(inputs/'S4',[Path(reference['path'])]*10+[Path(changed['path'])]*10+[Path(reference['path'])]*5)
        execute('S4',settings_for(base,folder,'S4-cambio-sostenido'),
                expectation='Dos ventanas de referencia, dos de cambio sostenido y recuperación con scores reales',
                accept=lambda es,aa,ww:any(a['rule_id']=='sustained-confidence-v1' for a in aa)
                    and len(ww)==5 and ww[-1]['state']=='within_policy' and good(es,aa,ww))
    else:
        results['S4']={'scenario':'S4','observed':False,'pending':'Las observaciones no alcanzan el aumento fijado; no se alteró la política'}
    folder=sequence(inputs/'S5',[normal]*3)
    (folder/'001.png').write_bytes(b'S5: entrada corrupta deliberada, no imagen')
    execute('S5',settings_for(base,folder,'S5-corrupta'),expectation='Imagen corrupta genera decode_error y el siguiente frame sigue con ONNX real',
            accept=lambda es,aa,ww:len(es)==3 and es[1]['status']=='decode_error' and es[2]['inference_executed'])
    folder=sequence(inputs/'S6',[normal]*2)
    first=settings_for(base,folder,'S6-versiones')
    data=first.model_dump();data['confidence']['upper']=.85
    second=Settings.model_validate(data)
    a,_,_=execute('S6-v1',first,expectation='Configuración inicial identificada',accept=good)
    b,_,_=execute('S6-v2',second,expectation='Otra configuración: mismo modelo/scores, identidad y series distintas',accept=good)
    results['S6']={'scenario':'S6','observed':first.fingerprint!=second.fingerprint and a[0]['detections'][0]['confidence']==b[0]['detections'][0]['confidence'],
                   'runs':[results['S6-v1']['run_id'],results['S6-v2']['run_id']],
                   'configs':[first.fingerprint,second.fingerprint],
                   'expectation':'No mezclar referencias ni series incompatibles'}
    folder=sequence(inputs/'S7',[normal]*4)
    execute('S7',settings_for(base,folder,'S7-fallo-inyectado'),factory=InjectedFailureDetector,
            expectation='Fallo controlado identificado, captura/diagnóstico y ONNX real antes/después',
            accept=lambda es,aa,ww:len(es)==4 and es[1]['status']=='inference_error' and not es[1]['inference_executed']
                and es[0]['inference_executed'] and es[2]['inference_executed'])
    save_json(output/'calibration.json',cal)
    save_json(output/'summary.json',{'timestamp':utc_now(),'scenarios':results,
              'code':code_manifest(),'method':'Sin scores inyectados. S1 usa interrupción real de archivo; solo S7 simula un fallo técnico.',
              'academic_points_confirmed':None,'academic_note':'Potencial de extras sujeto a evaluación docente; no autoasignado'})
    return results


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    output=args.output or ROOT/'evidencias/ampliacion/ejecuciones'/uid('batch')
    result=run_suite(output)
    print(json.dumps({'directory':str(output),'results':{k:r['observed'] for k,r in result.items()}},indent=2))
    raise SystemExit(0 if all(r['observed'] for r in result.values()) else 2)
