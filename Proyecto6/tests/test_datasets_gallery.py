"""Casos unitarios con HTTP simulado y una integración real con fotografías públicas."""
from copy import deepcopy
from io import BytesIO
import hashlib,json
from pathlib import Path
import time

from fastapi.testclient import TestClient
import httpx
import numpy as np
from PIL import Image
import pytest

from monitor_cv.config import ROOT,Settings
from monitor_cv.database import Database
from monitor_cv.datasets import acquire,inspect_image,near_duplicate,permitted_license,Budget,fetch,CC_BY
from monitor_cv.gallery import Gallery
from monitor_cv.metrics import trace_complete
from monitor_cv.main import create_app
from monitor_cv.query import Filters,filter_records,search
from monitor_cv.service import MonitorService
from monitor_cv.sources import SourceRegistry,SourceRequest,sync_collections


def photo(quality=90):
    yy,xx=np.mgrid[:96,:128];rgb=np.stack([xx*2,yy*2,(xx+yy)%256],axis=2).astype('uint8')
    stream=BytesIO();Image.fromarray(rgb).save(stream,'JPEG',quality=quality);return stream.getvalue()


def selection(root,licenses=None):
    rows=[{'image_id':f'{i:016x}','category':'animales','license_url':license,
           'download_url':f'https://open-images-dataset.s3.amazonaws.com/validation/{i:016x}.jpg'}
          for i,license in enumerate(licenses or [CC_BY])]
    path=root/'config/selection.json';path.parent.mkdir();path.write_text(json.dumps({'metadata':{},'selection_seed':6,'images':rows}),encoding='utf-8');return path


@pytest.mark.parametrize('license,expected',[(CC_BY,True),('http://creativecommons.org/licenses/by/2.0/',True),
    ('https://creativecommons.org/licenses/by-nc/2.0/',False),('unknown',False),('',False)])
def test_license_is_per_image_allowlist(license,expected):assert permitted_license(license)==expected


def test_selective_download_manifest_and_offline_reuse(tmp_path):
    chosen=selection(tmp_path);calls=[]
    def response(request):calls.append(str(request.url));return httpx.Response(200,content=photo())
    with httpx.Client(transport=httpx.MockTransport(response)) as client:
        first=acquire(tmp_path,target=1,selection=chosen,client=client)
        second=acquire(tmp_path,target=1,selection=chosen,client=client)
    assert first['downloaded']==1 and first['network_bytes']==len(photo())
    assert second['downloaded']==0 and second['reused']==1 and second['network_bytes']==0 and len(calls)==1
    manifest=json.loads((tmp_path/'data/media/datasets/manifest.json').read_text(encoding='utf-8'))
    row=manifest['images'][0];assert row['sha256']==hashlib.sha256(photo()).hexdigest() and row['width']==128
    assert (tmp_path/row['path']).read_bytes()==photo()
    assert row['downloaded_at'] and row['license_url']==CC_BY


@pytest.mark.parametrize('kind',['exact','near','corrupt','license','sha_mismatch','budget'])
def test_acquisition_rejects_invalid_inputs(tmp_path,kind):
    chosen=selection(tmp_path,[CC_BY,CC_BY] if kind in {'exact','near'} else ['unknown' if kind=='license' else CC_BY])
    if kind=='sha_mismatch':
        document=json.loads(chosen.read_text());document['images'][0]['sha256']='0'*64;chosen.write_text(json.dumps(document))
    def response(request):
        data=b'invalid' if kind=='corrupt' else photo(80 if kind=='near' and request.url.path.endswith('1.jpg') else 90)
        return httpx.Response(200,content=data)
    with httpx.Client(transport=httpx.MockTransport(response)) as client:
        report=acquire(tmp_path,target=2,max_bytes=5 if kind=='budget' else 200000,selection=chosen,client=client)
    if kind=='exact':assert report['accepted']==1 and report['exact_duplicates']==1
    elif kind=='near':assert report['accepted']==1 and report['near_duplicates']==1
    else:assert report['accepted']==0
    assert report['network_bytes']<=report['limit_bytes']
    if kind=='license':assert report['skipped'][0]['reason']=='license_not_allowed' and report['network_bytes']==0


def test_perceptual_identity_and_url_security():
    a,b=inspect_image(photo(90)),inspect_image(photo(80))
    assert a['sha256']!=b['sha256'] and near_duplicate(a,b)
    with httpx.Client(transport=httpx.MockTransport(lambda r:httpx.Response(200,content=photo()))) as client:
        with pytest.raises(ValueError):fetch(client,'http://127.0.0.1/private',Budget())
    with pytest.raises((OSError,ValueError)):inspect_image(b'broken')


def seed(db,event,index,**values):
    row={**deepcopy(event),'id':f'gallery-{index:03}','collection':'animales' if index%2 else 'personas',**values}
    db.save_observation(row,[],None);return row


def test_sql_filters_match_python_and_page_only_requested_rows(event,settings):
    db=Database(settings.data_dir/'new.sqlite3');db.save_run({'id':'r-1'})
    rows=[seed(db,event,i) for i in range(130)]
    queries=[Filters(collection='animales',limit=7,offset=14),Filters(class_name='person',zone='low',min_score=.3,max_score=.5,limit=5),
             Filters(q='gallery-01',sort='id',order='asc',limit=4),Filters(collection='absent')]
    for selected in queries:
        expected=filter_records(rows,selected,'events');actual=search(db,'events',selected)
        assert actual['total']==len(expected) and actual['items']==expected[selected.offset:selected.offset+selected.limit]
    assert len(search(db,'events',Filters(limit=25))['items'])==25


def test_gallery_distinguishes_technical_missing_unsafe_and_tampered(event,settings,tmp_path):
    db=Database(settings.data_dir/'gallery.sqlite3');db.save_run({'id':'r-1'})
    good=seed(db,event,0)
    technical=seed(db,event,1,status='source_error',image_ref=None,image_sha256=None,detections=[])
    absent=seed(db,event,2,image_ref='images/missing.png')
    unsafe=seed(db,event,3,image_ref=str(tmp_path.parent/'outside.png'))
    mismatch=seed(db,event,4,image_sha256='0'*64)
    gallery=Gallery(db,settings.data_dir);result=gallery.page(Filters())
    assert result['total']==1 and result['technical_without_image']==1 and result['missing_images']==3
    assert result['image_states']=={'available':1,'technical_without_image':1,'missing_file':1,'unsafe_path':1,'hash_mismatch':1}
    assert not trace_complete(absent,settings.data_dir) and not trace_complete(mismatch,settings.data_dir)
    assert len(gallery.issues(Filters(limit=2,offset=1))['items'])==2
    assert db.get('events',technical['id'])==technical
    # Restaurar solo el archivo ausente desde bytes cuyo SHA ya era el esperado.
    evidence=tmp_path/'evidence';evidence.mkdir();(evidence/'missing.png').write_bytes((settings.data_dir/event['image_ref']).read_bytes())
    repairs=gallery.repair_exact(evidence)
    assert repairs[0]['event_id']==absent['id'] and db.get('events',absent['id'])==absent


def test_thumbnails_are_small_cached_and_missing_is_explicit(event,settings):
    db=Database(settings.data_dir/'thumb.sqlite3');db.save_run({'id':'r-1'});row=seed(db,event,0)
    service=MonitorService(settings,database=db)
    with TestClient(create_app(settings,service=service)) as client:
        gallery=client.get('/api/gallery?limit=1').json()
        assert len(gallery['items'])==1 and 'candidates' not in gallery['items'][0] and 'config' not in gallery['items'][0]
        url=gallery['items'][0]['annotated_thumbnail_url'];response=client.get(url)
        assert response.status_code==200 and response.headers['content-type']=='image/jpeg'
        with Image.open(BytesIO(response.content)) as image:assert image.width<=320 and image.height<=240
        assert client.get(url,headers={'If-None-Match':response.headers['etag']}).status_code==304
        assert client.get('/api/gallery/issues').json()['total']==0
        original=(settings.data_dir/event['image_ref']);original.unlink()
        assert client.get(url).status_code==404
        assert client.get('/api/gallery').json()['missing_images']==1
        assert 'Referencia declarada cuyo archivo no existe' in client.get('/events/'+row['id']).text


def test_newly_arrived_frame_is_pending_not_missing(event,settings,monkeypatch):
    db=Database(settings.data_dir/'pending.sqlite3');db.save_run({'id':'r-1'});seed(db,event,0)
    gallery=Gallery(db,settings.data_dir)
    # Reproduce la carrera: evento ingresado después del recorrido de archivos.
    monkeypatch.setattr(gallery,'refresh',lambda:None)
    pending=gallery.page(Filters())
    assert pending['pending_images']==1 and pending['missing_images']==0


def test_dataset_zip_preserves_license_attribution(event,settings):
    import zipfile
    db=Database(settings.data_dir/'credits.sqlite3');db.save_run({'id':'r-1'})
    record=seed(db,event,0,input_image={'image_id':'unit-image','author':'Autor de prueba',
        'title':'Fixture unitario','license_url':CC_BY,'landing_url':'https://example.org/unit'})
    with TestClient(create_app(settings,service=MonitorService(settings,database=db))) as client:
        response=client.post('/api/gallery/download',json={'ids':[record['id']]})
        with zipfile.ZipFile(BytesIO(response.content)) as archive:
            credits=json.loads(archive.read('ATTRIBUTION.json'))
            assert credits[0]['author']=='Autor de prueba' and credits[0]['license_url']==CC_BY
            assert archive.read(record['id']+'.png')==(settings.data_dir/event['image_ref']).read_bytes()


@pytest.mark.real
def test_real_dataset_collections_switch_and_persist(tmp_path):
    path=ROOT/'data/media/datasets/manifest.json'
    if not path.is_file():pytest.skip('Ejecutar download_demo_dataset.py; sin fotos no se acredita inferencia')
    manifest=json.loads(path.read_text(encoding='utf-8'))
    assert len(manifest['images'])==len({r['sha256'] for r in manifest['images']})==80
    assert all(permitted_license(r['license_url']) and r['author'] and hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in manifest['images'])
    values=Settings().model_dump();values['storage']['data_dir']=str(tmp_path/'runtime')
    settings=Settings.model_validate(values);db=Database(settings.data_dir/'monitor.sqlite3')
    registered=sync_collections(settings,db);assert len(registered['registered'])==8 and not registered['errors']
    assert len(sync_collections(settings,db)['existing'])==8
    registry=SourceRegistry(settings,db);service=MonitorService(settings,database=db)
    for identity in registered['registered'][:2]:
        source,chosen=registry.validate(identity)
        run=service.start(max_frames=1,settings=chosen);service.thread.join(15)
        assert not service.thread.is_alive()
        event=db.list('events',run)[0]
        assert event['inference_executed'] and not event['synthetic'] and event['collection']==source['collection']
        assert event['input_image']['sha256']==event['input_sha256'] and trace_complete(event,settings.data_dir)
    assert len(db.list('runs'))==2
