"""C1/C2 complementarios con fotos CC BY identificadas; no usa el ejemplo dog.jpg."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from monitor_cv.config import Settings,load_settings
from monitor_cv.datasets import permitted_license
from monitor_cv.events import uid,utc_now,json_text
from monitor_cv.service import MonitorService
from monitor_cv.sources import SourceRegistry,sync_collections
from run_scenarios import export,save_json
from verify_extras import verify as verify_extras


def run(output:Path,*,base=None,sample_hz=4):
    if base is None:
        data=load_settings(environ=False).model_dump()
        data['storage']['data_dir']='data/runtime/'+uid('public')
        base=Settings.model_validate(data)
    output.mkdir(parents=True,exist_ok=False)
    service=MonitorService(base)
    registration=sync_collections(base,service.db)
    if registration['errors']:raise ValueError(registration['errors'])
    registry=SourceRegistry(base,service.db);results={}
    for scenario,collection in [('C1_PUBLIC','escenas_multiples'),('C2_PUBLIC','baja_confianza')]:
        source=next(s for s in service.db.list('sources') if s.get('collection')==collection)
        _,chosen=registry.validate(source['id']);data=chosen.model_dump()
        data['source'].update(sample_hz=sample_hz,loop=False)
        chosen=Settings.model_validate(data)
        run_id=service.start(settings=chosen)
        service.thread.join(60)
        if service.thread.is_alive():service.stop();raise TimeoutError('La colección no terminó')
        events=list(reversed(service.db.list('events',run_id)))
        alerts=service.db.list('alerts',run_id)
        policies={key:chosen.model_dump()[key] for key in ['detector','confidence','alerts','metrics']}
        valid=bool(events) and len(events)==source['total_frames'] and service.error is None
        valid=valid and all(e['inference_executed'] and not e['synthetic'] and
                           permitted_license(e['input_image']['license_url']) for e in events)
        if scenario=='C2_PUBLIC':valid=valid and any(a['rule_id']=='low-confidence-v1' for a in alerts)
        folder=output/scenario;export(service,run_id,folder)
        checks=verify_extras(folder);save_json(folder/'extra-verification.json',checks)
        result={'scenario':scenario,'collection':collection,'run_id':run_id,'source_id':source['id'],
                'observed':valid and checks['ok'],'policy_sha256':hashlib.sha256(json_text(policies).encode()).hexdigest(),
                'events':len(events),'detections':sum(len(e['detections']) for e in events),'alerts':len(alerts),
                'input_sha256':[e['input_sha256'] for e in events],
                'expectation':'Inferencias progresivas reales y monitoreo coherente'+
                  ('; alerta por baja confianza real' if scenario=='C2_PUBLIC' else '; sin exigir ausencia de alertas'),
                'scope':'Complementa los C1/C2 históricos sin modificarlos; estas fotos ya pertenecen a los 80 originales.'}
        save_json(folder/'result.json',result);results[scenario]=result
    policy_equal=results['C1_PUBLIC']['policy_sha256']==results['C2_PUBLIC']['policy_sha256']
    summary={'timestamp':utc_now(),'scenarios':results,'same_model_and_monitoring_policy':policy_equal,
             'runtime_data_dir':base.storage.data_dir,'isolated_from_main_runtime':base.data_dir!=load_settings(environ=False).data_dir,
             'ok':policy_equal and all(r['observed'] for r in results.values()),
             'unique_inputs':len({sha for r in results.values() for sha in r['input_sha256']}),
             'new_original_photographs':0,'additional_scenario_bonus_claimed':False,
             'command':'python scripts/run_public_scenarios.py --sample-hz '+str(sample_hz)}
    save_json(output/'summary.json',summary)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample-hz',type=float,default=4)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    directory=(args.output or ROOT/'evidencias/cierre_final/escenarios-publicos'/uid('public')).resolve()
    result=run(directory,sample_hz=args.sample_hz)
    print(json.dumps({'output':directory.relative_to(ROOT).as_posix(),'ok':result['ok'],
                      'unique_inputs':result['unique_inputs'],'new_original_photographs':0}))
    raise SystemExit(0 if result['ok'] else 1)
