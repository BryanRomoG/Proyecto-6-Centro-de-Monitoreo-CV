"""Recorrido HTTP de funciones con datos persistidos; complementa la observación en navegador."""
import argparse
import csv
import hashlib
from io import BytesIO,StringIO
import json
from pathlib import Path
import sys
import time
import zipfile

import httpx

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from monitor_cv.analytics import extras
from monitor_cv.events import uid,utc_now
from verify_extras import verify as verify_extras


def verify(base_url,run_id,output):
    output.mkdir(parents=True,exist_ok=False)
    checks={}
    with httpx.Client(base_url=base_url,timeout=30,trust_env=False) as client:
        def get(path,**kwargs):
            response=client.get(path,**kwargs)
            response.raise_for_status()
            return response
        events=get('/api/export/events',params={'run_id':run_id}).json()
        alerts=get('/api/export/alerts',params={'run_id':run_id}).json()
        params={'run_id':run_id,'class_name':'car','zone':'low','min_score':.1,'max_score':.6}
        queried=get('/api/query/events',params=params).json()
        expected=[e for e in events if any(d['class_name']=='car' and d['zone']=='low' and .1<=d['confidence']<=.6 for d in e['detections'])]
        checks['F4_combined_filter']={e['id'] for e in queried['items']}=={e['id'] for e in expected}
        checks['F4_empty']=get('/api/query/events',params={'run_id':run_id,'q':'definitely-absent-event'}).json()['total']==0
        checks['F4_invalid']=client.get('/api/query/events?min_score=.9&max_score=.1').status_code==422
        for kind in ['events','alerts','metrics','confidence','runs','extras']:
            filters={'run_id':run_id}
            if kind=='events':
                filters.update(params)
            records=get('/api/export/'+kind,params={**filters,'format':'json'}).json()
            response=get('/api/export/'+kind,params={**filters,'format':'csv'})
            parsed=list(csv.DictReader(StringIO(response.text.lstrip('\ufeff'))))
            checks['F6_'+kind+'_rows']=len(parsed)==(len(records)*7 if kind=='metrics' else len(records))
            (output/(kind+'.csv')).write_bytes(response.content)
            (output/(kind+'.json')).write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding='utf-8')
        # Las observaciones completas se conservan aparte de la exportación filtrada.
        (output/'events.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events),encoding='utf-8')
        (output/'alerts.jsonl').write_text(''.join(json.dumps(a,ensure_ascii=False)+'\n' for a in alerts),encoding='utf-8')
        windows=get('/api/windows',params={'run_id':run_id}).json()
        (output/'windows.jsonl').write_text(''.join(json.dumps(w,ensure_ascii=False)+'\n' for w in windows),encoding='utf-8')
        event=next(e for e in events if e.get('image_ref'))
        gallery=get('/api/gallery',params={'run_id':run_id}).json()
        checks['F5_links']=all(e['id'] in e['image_url'] and e['id'] in e['annotated_url'] for e in gallery['items'])
        selected=[e['id'] for e in gallery['items'][:2]]
        response=client.post('/api/gallery/download',json={'ids':selected})
        response.raise_for_status()
        archive=zipfile.ZipFile(BytesIO(response.content))
        checks['F5_download']=set(archive.namelist())=={identity+'.png' for identity in selected}
        for identity in selected:
            original=get('/images/'+identity).content
            checks['F5_sha_'+identity]=archive.read(identity+'.png')==original
        checks['F5_invalid_path']=client.post('/api/gallery/download',json={'ids':['../outside']}).status_code==422
        checks['F8_path_block']=client.post('/api/sources',json={'name':'rechazo de seguridad','kind':'images','path':'../Proyecto5'}).status_code==422
        historical=get('/api/history',params={'run_id':run_id}).json()
        checks['F3_series']=set(historical['series'])==({run_id} if events else set())
        checks['F3_points']=sum(len(series) for series in historical['series'].values())==len(events)
        checks['F3_intervals']=sum(row['events'] for row in historical['intervals'])==len(events)
        checks['F3_classes']=sum(historical['extras']['values']['M08'].values())==sum(len(e['detections']) for e in events)
        (output/'history.json').write_text(json.dumps(historical,indent=2),encoding='utf-8')
        dashboard=get('/api/dashboard',params={'run_id':run_id}).json()
        checks['F1_counts']=dashboard['events']==len(events) and dashboard['detections']==sum(len(e['detections']) for e in events)
        (output/'dashboard.json').write_text(json.dumps(dashboard,indent=2),encoding='utf-8')
        current=get('/api/playback/current').json()
        if current['event'] and current['event']['run_id']==run_id:
            identity=current['event']['id']
            checks['F2_id']=identity in current['image_url'] and identity in current['annotated_url']
            checks['F2_image_header']=get(current['annotated_url']).headers['X-Event-ID']==identity
            if current['state']=='paused':
                time.sleep(.15)
                after=get('/api/playback/current').json()
                checks['F2_paused_frozen']=after['event']['id']==identity
        for path in ['/','/playback','/events','/alerts','/history','/gallery','/sources','/runs','/configuration']:
            checks['HTML_'+path]=get(path).status_code==200
        # Snapshot independiente para recálculo de M01–M19, incluidos cambios de alerta reales.
        for e in events:
            if e.get('image_ref'):
                path=output/e['image_ref']
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(get('/images/'+e['id']).content)
        measured=extras(events,alerts,output,cutoff=utc_now(),windows=windows)
        (output/'extras.json').write_text(json.dumps(measured,indent=2),encoding='utf-8')
        checks['M_recalculation']=verify_extras(output)['ok']
        managed=[a for a in alerts if a.get('history')]
        checks['F7_persistent_history']=all(a['history'] and a['version']>=1 for a in managed) if managed else None
        report={'timestamp':utc_now(),'run_id':run_id,'directory':str(output),'checks':checks,
                'ok':all(value is not False for value in checks.values()),
                'unobserved':[key for key,value in checks.items() if value is None],
                'scope':'HTTP sobre eventos reales; los screenshots y acciones de navegador se registran por separado',
                'download_sha256':hashlib.sha256(response.content).hexdigest()}
        (output/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--base-url',default='http://127.0.0.1:8006')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    print(json.dumps(verify(args.base_url,args.run_id,args.output or ROOT/'evidencias/ampliacion/funciones'/uid('http')),indent=2))
