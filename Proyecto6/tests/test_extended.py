"""Pruebas unitarias, contratos HTTP y pruebas reales marcadas separadamente."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import csv
from datetime import datetime,timedelta
from io import BytesIO,StringIO
import json
from pathlib import Path
import threading
import time
import zipfile

import cv2
from fastapi.testclient import TestClient
import numpy as np
from PIL import Image
import pytest

from monitor_cv.alerts import evaluate
from monitor_cv.analytics import extras,history
from monitor_cv.camera import VideoSource
from monitor_cv.config import ROOT,Settings
from monitor_cv.database import Database
from monitor_cv.exporting import safe_cell
from monitor_cv.main import create_app
from monitor_cv.metrics import calculate
from monitor_cv.query import Filters,filter_records
from monitor_cv.service import MonitorService
from monitor_cv.sources import SourceRegistry,SourceRequest


@pytest.fixture
def media(settings,image_bytes,tmp_path):
    folder=Path(settings.source.images_dir)
    folder.mkdir()
    for i in range(8):
        (folder/f'{i:03}.png').write_bytes(image_bytes)
    data=settings.model_dump()
    data['media_roots']=[str(tmp_path)]
    return Settings.model_validate(data)


@pytest.fixture
def seeded(event,settings):
    db=Database(settings.data_dir/'extended.sqlite3')
    db.save_run({'id':event['run_id'],'started_at':event['timestamp'],'status':'completed'})
    alert=evaluate(event,None,settings)[0]
    db.save_observation(event,[alert],None)
    return db,alert


def make_video(path,count=12):
    writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*('mp4v' if path.suffix=='.mp4' else 'MJPG')),8,(64,48))
    assert writer.isOpened()
    for i in range(count):
        writer.write(np.full((48,64,3),30+i*5,np.uint8))
    writer.release()


@pytest.mark.parametrize('suffix',['.avi','.mp4'])
def test_video_sampling_positions_and_read_accounting(media,tmp_path,suffix):
    path=tmp_path/('sample'+suffix)
    make_video(path)
    data=media.model_dump()
    data['source'].update(kind='video',video_file=str(path),sample_hz=2)
    source=VideoSource(Settings.model_validate(data))
    try:
        packets=list(source.packets(threading.Event()))
    finally:
        source.close()
    assert [p.frame_index for p in packets]==[0,4,8,11]
    assert [p.position_seconds for p in packets]==[0,.5,1,1.375]
    assert sum(p.read_frames for p in packets)==12
    assert sum(p.discarded_frames for p in packets)==8
    assert all(p.total_frames==12 and p.error is None for p in packets)


def test_source_registration_safety_duplicates_and_corruption(media,image_bytes,tmp_path):
    db=Database(media.data_dir/'source.sqlite3')
    registry=SourceRegistry(media,db)
    request=SourceRequest(name='Prueba',kind='images',path=media.source.images_dir,sample_hz=3)
    record=registry.register(request)
    assert record['total_frames']==8
    assert registry.validate(record['id'])[1].source.sample_hz==3
    with pytest.raises(ValueError,match='registrada'):
        registry.register(request)
    for path in ['../README.md',str(tmp_path.parent/'outside'),str(tmp_path/'missing')]:
        with pytest.raises(ValueError):
            registry.register(SourceRequest(name='Fuera',kind='images',path=path))
    broken=tmp_path/'broken.mp4'
    broken.write_bytes(b'not-a-video')
    with pytest.raises(ValueError):
        registry.register(SourceRequest(name='Inválido',kind='video',path=str(broken)))
    folder=tmp_path/'badimages'
    folder.mkdir()
    (folder/'broken.png').write_bytes(b'invalid')
    with pytest.raises(ValueError,match='decodificable'):
        registry.register(SourceRequest(name='Corrupta',kind='images',path=str(folder)))
    (folder/'valid.png').write_bytes(image_bytes)
    mixed=registry.register(SourceRequest(name='Mixta',kind='images',path=str(folder)))
    assert mixed['invalid_images']==['broken.png']


@pytest.mark.parametrize('values',[{'min_score':.8,'max_score':.2},{'start':'bad-date'},
    {'start':'2026-11-11','end':'2026-11-10'},{'sort':'arbitrary-sql'},
    {'zone':'wrong'},{'status':'healthy'},{'offset':-1},{'page':0}])
def test_filters_invalid(values):
    with pytest.raises(ValueError):
        Filters.model_validate(values)


def test_filters_same_detection_order_and_timezone(event):
    event['detections'] += [{'class_name':'dog','zone':'accepted','confidence':.9}]
    assert not filter_records([event],Filters(class_name='dog',zone='low'),'events')
    assert filter_records([event],Filters(class_name='dog',zone='accepted',min_score=.8),'events')
    assert not filter_records([event],Filters(q="'; DROP TABLE events;"),'events')
    assert Filters(start='2026-11-10T10:00:00-06:00').start=='2026-11-10T16:00:00+00:00'


def test_alert_lifecycle_idempotency_and_immutable_event(seeded,event,settings):
    db,alert=seeded
    original=db.get('events',event['id'])
    with pytest.raises(ValueError):
        db.transition_alert(alert['id'],action='resolve',comment='No',request_id='invalid-step',expected_version=0)
    kwargs=dict(action='acknowledge',comment='Revisada',request_id='request-unit-1',expected_version=0)
    first=db.transition_alert(alert['id'],**kwargs)
    assert db.transition_alert(alert['id'],**kwargs)==first
    assert db.get('alerts',alert['id'])['status']=='acknowledged'
    assert calculate([event],db.list('alerts'),run_id=event['run_id'],data_dir=settings.data_dir,window_seconds=60)['values']['G7']==1
    db.transition_alert(alert['id'],action='resolve',comment='Revisión terminada',request_id='request-unit-2',expected_version=1)
    managed=db.get('alerts',alert['id'])
    assert managed['status']=='resolved' and len(managed['history'])==2
    assert managed['acknowledged_at'] and managed['resolved_at']
    assert db.get('events',event['id'])==original
    assert calculate([event],[managed],run_id=event['run_id'],data_dir=settings.data_dir,window_seconds=60)['values']['G7']==0
    historical=calculate([event],[managed],run_id=event['run_id'],data_dir=settings.data_dir,window_seconds=60,now=event['timestamp'])
    assert historical['values']['G7']==1
    with pytest.raises(ValueError):
        db.transition_alert(alert['id'],action='comment',comment='changed request',request_id='request-unit-1',expected_version=2)


def test_alert_concurrency_exactly_one_transition(seeded):
    db,alert=seeded
    def change(index):
        try:
            db.transition_alert(alert['id'],action='acknowledge',comment=str(index),request_id='parallel-'+str(index),expected_version=0)
            return True
        except ValueError:
            return False
    with ThreadPoolExecutor(max_workers=2) as executor:
        assert sorted(executor.map(change,[1,2]))==[False,True]
    assert len(db.get('alerts',alert['id'])['history'])==1


@pytest.mark.parametrize('value',['=1+1','+SUM(A1)','-cmd','@formula','  =x','\tdata','\rdata'])
def test_csv_formula_cells(value):
    assert safe_cell(value).startswith("'")
    assert safe_cell(-2)==-2


def test_api_filters_exports_gallery_and_missing_states(seeded,event,settings):
    db,alert=seeded
    service=MonitorService(settings,database=db)
    with TestClient(create_app(settings,service=service)) as client:
        query=client.get('/api/query/events',params={'run_id':'r-1','class_name':'person','zone':'low','min_score':.3,'max_score':.5,'limit':1}).json()
        assert query['total']==1 and query['items'][0]['id']==event['id']
        assert client.get('/api/query/events?class_name=dog').json()['total']==0
        assert client.get('/api/events?min_score=.8&max_score=.2').status_code==422
        assert client.get('/api/events?typo=bad').status_code==422
        exported=client.get('/api/export/events?run_id=r-1&format=json').json()
        assert exported==query['items']
        csv_result=client.get('/api/export/events?run_id=r-1&format=csv').text
        rows=list(csv.DictReader(StringIO(csv_result.lstrip('\ufeff'))))
        assert rows[0]['id']==event['id']
        assert client.get('/api/export/metrics?class_name=person').status_code==422
        gallery=client.get('/api/gallery?run_id=r-1').json()
        assert gallery['total']==1 and gallery['items'][0]['alerts']==[alert['id']]
        annotated=client.get('/images/e-1/annotated')
        assert annotated.status_code==200 and annotated.headers['X-Event-ID']=='e-1'
        assert client.get('/images/e-1').content==(settings.data_dir/event['image_ref']).read_bytes()
        selection=client.post('/api/gallery/download',json={'ids':['e-1']})
        archive=zipfile.ZipFile(BytesIO(selection.content))
        assert archive.namelist()==['e-1.png']
        assert archive.read('e-1.png')==(settings.data_dir/event['image_ref']).read_bytes()
        assert client.post('/api/gallery/download',json={'ids':['../escape']}).status_code==422
        assert client.post('/api/gallery/download',json={'ids':['missing']}).status_code==404
        assert client.post('/api/alerts/'+alert['id']+'/changes',json={'action':'acknowledge','comment':'UI','expected_version':0,'request_id':'http-request-1'}).status_code==200
        assert client.get('/api/alerts?status=acknowledged').json()[0]['id']==alert['id']
        for page in ['/','/playback','/history','/gallery','/sources','/runs','/configuration']:
            assert client.get(page).status_code==200
        dashboard=client.get('/api/dashboard?run_id=r-1').json()
        assert dashboard['events']==1 and dashboard['detections']==1
        (settings.data_dir/event['image_ref']).unlink()
        assert client.get('/api/gallery?run_id=r-1').json()['missing_images']==1
        assert client.get('/images/e-1').status_code==404


def test_additional_metrics_and_historical_calculations(event,settings):
    other=deepcopy(event)
    other.update(id='e-2',inference_ms=40,cpu_seconds_delta=.1,read_frames=5,discarded_frames=4)
    event.update(cpu_seconds_delta=.1,read_frames=1,discarded_frames=0)
    now=other['timestamp']
    result=extras([event,other],[],settings.data_dir,cutoff=now)
    values=result['values']
    assert values['M01']=={'p50':30.,'p95':39.}
    assert values['M02']==0 and values['M03']==4 and values['M04']==6
    assert values['M06']==20 and values['M07']==100
    assert values['M08']=={'person':2}
    assert sum(values['M09']['counts'])==2
    assert values['M10']==0 and values['M11']==1 and values['M12']==0
    assert values['M13']==0 and values['M14']==1
    assert values['M17'] is None and values['M18'] is None
    empty=extras([],[],settings.data_dir,cutoff=now)
    assert empty['values']['M01'] is None and empty['values']['M14'] is None
    other['run_id']='r-2'
    plot=history([event,other],[],[],10)
    assert set(plot['series'])=={'r-1','r-2'}
    assert sum(b['events'] for b in plot['intervals'])==2
    assert len(plot['intervals'])==1


@pytest.mark.real
def test_real_pause_resume_snapshot_and_video(tmp_path):
    if not (ROOT/'modelo/yolox_nano.onnx').is_file():
        pytest.skip('Requiere pesos reales')
    data=Settings().model_dump()
    data['source'].update(images_dir='data/demo/normal',sample_hz=10,loop=True)
    data['storage']['data_dir']=str(tmp_path/'runtime')
    settings=Settings.model_validate(data)
    service=MonitorService(settings)
    service.start()
    deadline=time.monotonic()+5
    while service.latest_event is None and time.monotonic()<deadline:
        time.sleep(.01)
    assert service.latest_event
    assert service.pause()['state']=='paused'
    before=service.current()['event']['id']
    count=len(service.db.list('events',service.run_id))
    time.sleep(.12)
    assert len(service.db.list('events',service.run_id))==count
    assert service.current()['event']['id']==before
    service.resume()
    deadline=time.monotonic()+5
    while service.current()['event']['id']==before and time.monotonic()<deadline:
        time.sleep(.01)
    assert service.current()['event']['id']!=before
    service.stop()
    assert [a['action'] for a in reversed(service.db.list('actions',service.run_id))]==['pause','resume']
    assert any(e['paused_seconds_excluded']>0 for e in service.db.list('events',service.run_id))
    with TestClient(create_app(settings,service=service)) as client:
        frame=client.get('/api/playback/current').json()
        assert frame['event']['id'] in frame['annotated_url']
        assert client.get(frame['annotated_url']).headers['X-Event-ID']==frame['event']['id']
        assert client.post('/api/monitor/resume').status_code==409
    video=tmp_path/'real.mp4'
    make_video(video)
    data['source'].update(kind='video',video_file=str(video),loop=False,sample_hz=60)
    player=MonitorService(Settings.model_validate(data))
    run=player.start(max_frames=3)
    player.thread.join(15)
    rows=player.db.list('events',run)
    assert len(rows)==3 and all(e['inference_executed'] and not e['synthetic'] for e in rows)
