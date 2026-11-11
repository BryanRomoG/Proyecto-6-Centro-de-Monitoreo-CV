"""Procesa todas las fotografías del manifiesto, sin escoger scores ni sobrescribir runs."""
import argparse
from collections import Counter
import hashlib,json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from monitor_cv.config import load_settings,Settings
from monitor_cv.service import MonitorService
from monitor_cv.sources import sync_collections,SourceRegistry
from monitor_cv.events import uid,utc_now
from run_scenarios import export,save_json
from verify_metrics import read_lines
from verify_extras import verify as verify_extras


def run(output,sample_hz=4):
    output.mkdir(parents=True,exist_ok=False)
    settings=load_settings(environ=False);service=MonitorService(settings)
    registration=sync_collections(settings,service.db)
    if registration['errors']:raise ValueError(registration['errors'])
    registry=SourceRegistry(settings,service.db)
    manifest_path=ROOT/'data/media/datasets/manifest.json'
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    results={};all_events=[];all_alerts=[]
    for source in service.db.list('sources'):
        if not source.get('collection') or source.get('dataset_manifest') is None:continue
        _,chosen=registry.validate(source['id']);data=chosen.model_dump();data['source'].update(sample_hz=sample_hz,loop=False)
        chosen=Settings.model_validate(data);run_id=service.start(settings=chosen)
        service.thread.join(180)
        if service.thread.is_alive():service.stop();raise TimeoutError('Tiempo máximo de colección superado')
        folder=output/source['collection'];export(service,run_id,folder)
        events=read_lines(folder/'events.jsonl');alerts=read_lines(folder/'alerts.jsonl')
        all_events.extend(events);all_alerts.extend(alerts)
        expected=[r['sha256'] for r in manifest['images'] if r['category']==source['collection']]
        seen=[e.get('input_sha256') for e in events]
        real=all(e['inference_executed'] and not e['synthetic'] for e in events)
        verification=verify_extras(folder);save_json(folder/'extra-verification.json',verification)
        result={'run_id':run_id,'source_id':source['id'],'collection':source['collection'],
                'events':len(events),'detections':sum(len(e['detections']) for e in events),
                'classes':dict(Counter(d['class_name'] for e in events for d in e['detections'])),
                'zones':dict(Counter(d['zone'] for e in events for d in e['detections'])),
                'no_detections':[e['id'] for e in events if e['status']=='no_detections'],
                'alerts':len(alerts),'all_real':real,'all_inputs_seen_once':sorted(expected)==sorted(seen),
                'extras_recalculated':verification['ok'],'mean_inference_ms':sum(e['inference_ms'] for e in events if e['inference_ms'] is not None)/len(events)}
        save_json(folder/'result.json',result);results[source['collection']]=result
        print(json.dumps({'collection':source['collection'],'events':len(events),'all_real':real}),flush=True)
    examples={}
    for zone in ['accepted','doubt','low']:
        examples[zone]=[{'event_id':e['id'],'run_id':e['run_id'],'image_id':e['input_image']['image_id'],
                         'class':d['class_name'],'score':d['confidence'],'zone':d['zone']}
                        for e in all_events for d in e['detections'] if d['zone']==zone][:5]
    examples['no_detections']=[{'event_id':e['id'],'run_id':e['run_id'],'image_id':e['input_image']['image_id']} for e in all_events if e['status']=='no_detections']
    success=all(r['all_real'] and r['all_inputs_seen_once'] and r['extras_recalculated'] for r in results.values()) and len(results)==8
    summary={'timestamp':utc_now(),'manifest_sha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
             'collections':results,'registration':registration,'events':len(all_events),
             'unique_inputs':len({e['input_sha256'] for e in all_events}),
             'classes':dict(Counter(d['class_name'] for e in all_events for d in e['detections'])),
             'zones':dict(Counter(d['zone'] for e in all_events for d in e['detections'])),
             'alerts':len(all_alerts),'examples':examples,'ok':success,
             'limits':'No scores alterados, ni filtro de salida para construir casos. Las categorías/etiquetas del dataset no son predicciones ni evaluación de accuracy.',
             'command':f'python scripts/run_dataset_demo.py --sample-hz {sample_hz}'}
    save_json(output/'summary.json',summary)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--sample-hz',type=float,default=4)
    args=parser.parse_args();directory=ROOT/'evidencias/datasets/ejecuciones'/uid('dataset')
    result=run(directory,args.sample_hz)
    print(json.dumps({'directory':str(directory),'events':result['events'],'zones':result['zones'],'ok':result['ok']},indent=2))
    raise SystemExit(0 if result['ok'] else 1)
