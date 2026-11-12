"""Audita originales, datasets, evidencia y recálculos sin añadir inferencias a SQLite."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from monitor_cv.config import Settings,load_settings
from monitor_cv.database import Database
from monitor_cv.detector import Detector
from monitor_cv.camera import decode
from monitor_cv.gallery import Gallery
from monitor_cv.query import Filters
from monitor_cv.reviews import Reviews
from monitor_cv.datasets import permitted_license,inspect_image,near_duplicate
from monitor_cv.events import utc_now
from run_demo import code_manifest
from verify_metrics import verify as base_verify
from verify_extras import verify as extra_verify
from audit_repository import audit,snapshot


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))


def run(output):
    output.mkdir(parents=True,exist_ok=False)
    settings=load_settings(environ=False)
    db=Database(settings.data_dir/settings.storage.database)
    manifest=read(ROOT/'data/media/datasets/manifest.json')
    rows=manifest['images'];seen=[];failures=[];near=[]
    for row in rows:
        path=ROOT/row['path'];info=inspect_image(path.read_bytes())
        if (info['sha256']!=row['sha256'] or not permitted_license(row['license_url'])
            or not row.get('author') or not row.get('original_url') or not row.get('downloaded_at')):failures.append(row['image_id'])
        for previous in seen:
            if near_duplicate(info,previous['info']):near.append([row['image_id'],previous['id']])
        seen.append({'id':row['image_id'],'info':info})
    baseline=read(ROOT/'evidencias/cierre_final/preexistentes.json')
    changed=[name for name,sha in baseline['files'].items() if not (ROOT.parent/name).is_file() or digest(ROOT.parent/name)!=sha]
    changed_tables={}
    with db.connect() as connection:
        for table,originals in baseline['tables'].items():
            now={i:hashlib.sha256(payload.encode()).hexdigest() for i,payload in connection.execute('SELECT id,payload FROM '+table)}
            changed_tables[table]=[i for i,sha in originals.items() if now.get(i)!=sha]
    earlier=read(ROOT/'evidencias/integridad_inicial.json');current=snapshot()
    originals_changed=[name for name,sha in earlier.items() if current.get(name)!=sha]
    packages={}
    paths=list((ROOT/'evidencias/ampliacion/ejecuciones/batch-f257a33483834710994f454dbb16000d').glob('*/metrics.json'))
    paths+=list((ROOT/'evidencias/datasets/ejecuciones/dataset-f316f59912a04cf1bb4a2bf2a1f3bc9a').glob('*/metrics.json'))
    paths+=list((ROOT/'evidencias/ampliacion/funciones/http-e875c88699ad42e7a533beaa51731017').glob('metrics.json'))
    paths+=list((ROOT/'evidencias/cierre_final/escenarios-publicos').glob('*/*/metrics.json'))
    for path in paths:
        directory=path.parent
        base=base_verify(directory) if (directory/'events.jsonl').is_file() and isinstance(read(path),dict) else None
        extra=extra_verify(directory) if (directory/'extras.json').is_file() else None
        packages[directory.relative_to(ROOT).as_posix()]={'base':base,'extras':extra}
    gallery=Gallery(db,settings.data_dir);gallery.refresh(force=True)
    page=gallery.page(Filters(limit=1));issues=gallery.issues(Filters(limit=500))
    event=db.get('events','evt-37c2579bd3af445fb8a683807642e8ee')
    view=Reviews(db).view(event)
    # Inferencia directa del PNG histórico íntegro, sin un nuevo evento/run ni score prefijado.
    image=settings.data_dir/event['image_ref'];assert digest(image)==event['image_sha256']
    detector=Detector(Settings.model_validate(event['config']))
    inference=detector.infer(decode(image.read_bytes()))
    original=[{k:v for k,v in d.items() if k!='zone'} for d in event['detections']]
    same=json.loads(json.dumps(inference['detections']))==original
    sources=[s for s in db.list('sources') if s.get('collection')]
    report={'timestamp':utc_now(),'files_changed':changed,'original_project_and_teacher_changes':originals_changed,
            'original_payload_changes':changed_tables,'datasets':{'images':len(rows),'unique_sha256':len({r['sha256'] for r in rows}),
            'unique_original_urls':len({r['original_url'] for r in rows}),'categories':dict(Counter(r['category'] for r in rows)),
            'licenses':dict(Counter(r['license_url'] for r in rows)),'bytes':sum(r['bytes'] for r in rows),
            'integrity_errors':failures,'near_duplicate_pairs':near,'redownloaded':0},
            'collections':[{k:s[k] for k in ['id','name','collection','total_frames']} for s in sources],
            'gallery':{k:page[k] for k in ['total','technical_without_image','missing_images','pending_images']},
            'image_issues':issues,'packages':packages,'review':view,'original_event':event,
            'linked_alerts':[db.get('alerts',i) for i in db.alert_links([event['id']])[event['id']]],
            'current_model_replay':{'model':detector.identity,'event_id':event['id'],'capture_sha256':digest(image),
              'matches_historical_predictions':same,'result':inference,'synthetic':False,'new_db_events':0},
            'repository':audit(),'code_sha256':code_manifest()}
    report['ok']=(not changed and not originals_changed and not any(changed_tables.values()) and not failures
                  and not near and same and page['missing_images']==0
                  and all((not v['base'] or v['base']['ok']) and (not v['extras'] or v['extras']['ok']) for v in packages.values()))
    (output/'audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'ok':report['ok'],'output':output.relative_to(ROOT).as_posix(),'packages':len(packages),
                      'datasets':report['datasets'],'gallery':report['gallery'],'same_real_predictions':same},ensure_ascii=False))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=run(args.output.resolve())
    raise SystemExit(0 if result['ok'] else 1)
