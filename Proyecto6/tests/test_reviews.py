"""Contratos unitarios e integración SQLite/HTTP; no simulan evidencia del modelo."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import json

from fastapi.testclient import TestClient
import pytest

from monitor_cv.alerts import evaluate
from monitor_cv.database import Database
from monitor_cv.main import create_app
from monitor_cv.reviews import ReviewRequest, Reviews, detection_id, validated_event
from monitor_cv.service import MonitorService


@pytest.fixture
def reviewed(settings,event):
    event['detections']=[{'class_id':16,'class_name':'dog','confidence':.65,'bbox':[0,0,25,25],'zone':'doubt'},
                         {'class_id':15,'class_name':'cat','confidence':.17,'bbox':[1,1,25,25],'zone':'low'}]
    service=MonitorService(settings)
    db=service.db
    db.save_run({'id':event['run_id'],'status':'completed','started_at':event['timestamp']})
    alert=evaluate(event,None,settings)[0]
    db.save_observation(event,[alert],None)
    return service,event,alert


def body(**kw):
    return {'status':'confirmed','reason':'Comprobación visual del objeto','actor':'revisor-local',
            'request_id':'review-request-01','expected_version':0,**kw}


@pytest.mark.parametrize('status,label',[('confirmed',None),('false_positive',None),('corrected','wolf'),('pending',None)])
def test_review_states_history_and_restart(reviewed,status,label):
    service,event,alert=reviewed
    original=deepcopy(service.db.get('events',event['id']))
    before=(service.settings.data_dir/event['image_ref']).read_bytes()
    with TestClient(create_app(service.settings,service=service)) as client:
        path='/api/events/e-1/detections/'+detection_id('e-1',0)+'/reviews'
        response=client.post(path,json=body(status=status,corrected_label=label))
        assert response.status_code==200,response.text
        r=response.json()['review']
        assert r['status']==status and r['original_label']=='dog' and r['corrected_label']==label
        assert r['actor']=='revisor-local' and r['timestamp'] and r['reason']
        assert client.get('/events/e-1/review').status_code==200
        assert client.get('/images/e-1/reviewed').status_code==200
    # Nueva conexión y nueva app (equivalente al estado persistente tras reinicio).
    second=MonitorService(service.settings)
    with TestClient(create_app(service.settings,service=second)) as client:
        data=client.get('/api/events/e-1/reviews').json()
        assert data['detections'][0]['status']==status and len(data['history'])==1
        assert data['detections'][0]['history'][0]['id']==r['id']
        assert data['original']==original and second.db.get('alerts',alert['id'])['status']=='active'
    assert before==(service.settings.data_dir/event['image_ref']).read_bytes()


def test_dog_cat_projection_originals_and_idempotency(reviewed):
    service,event,_=reviewed;store=Reviews(service.db)
    first=store.save(event,detection_id('e-1',0),ReviewRequest(**body()))
    assert store.save(event,detection_id('e-1',0),ReviewRequest(**body()))==first
    store.save(event,detection_id('e-1',1),ReviewRequest(**body(status='false_positive',request_id='review-request-02')))
    view=store.view(event)
    assert len(view['history'])==2 and len(view['overlaps'])==1
    assert [d['original']['class_name'] for d in view['validated']]==['dog']
    projection=validated_event(event,view)
    assert len(projection['detections'])==1 and projection['detections'][0]['confidence']==.65
    assert service.db.get('events','e-1')==event
    with pytest.raises(ValueError,match='Idempotencia'):
        store.save(event,detection_id('e-1',0),ReviewRequest(**body(reason='Otra decisión')))
    with pytest.raises(ValueError,match='actualizar'):
        store.save(event,detection_id('e-1',0),ReviewRequest(**body(request_id='another-request-01')))


def test_concurrent_review_and_append_history(reviewed):
    service,event,_=reviewed;store=Reviews(service.db);identity=detection_id('e-1',0)
    def save(i):
        try:return store.save(event,identity,ReviewRequest(**body(request_id=f'concurrent-request-{i}')))
        except ValueError:return None
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(save,[1,2]))
    assert sum(r is not None for r in results)==1
    store.save(event,identity,ReviewRequest(**body(status='false_positive',expected_version=1,request_id='third-request-01')))
    changes=store.view(event)['history']
    assert [r['version'] for r in changes]==[1,2] and changes[1]['previous_review_id']==changes[0]['id']


@pytest.mark.parametrize('change',[{'reason':'   '},{'status':'unknown'},{'status':'corrected'},
    {'corrected_label':'bad'},{'actor':' '},{'expected_version':-1},{'request_id':'x'},{'confidence':.99}])
def test_invalid_review_rejected(reviewed,change):
    service,_,_=reviewed
    with TestClient(create_app(service.settings,service=service)) as client:
        assert client.post('/api/events/e-1/detections/'+detection_id('e-1',0)+'/reviews',json=body(**change)).status_code==422


def test_empty_missing_capture_and_unknown(reviewed):
    service,event,_=reviewed
    with TestClient(create_app(service.settings,service=service)) as client:
        assert client.get('/api/events/unknown/reviews').status_code==404
        assert client.post('/api/events/e-1/detections/unknown/reviews',json=body()).status_code==404
        assert client.get('/api/events/e-1/reviews').json()['history']==[]
        (service.settings.data_dir/event['image_ref']).unlink()
        assert client.post('/api/events/e-1/detections/'+detection_id('e-1',0)+'/reviews',json=body()).status_code==409
        assert client.get('/images/e-1/reviewed').status_code==404
        empty={**event,'id':'empty','status':'no_detections','detections':[]}
        service.db.save_observation(empty,[],None)
        assert client.get('/api/events/empty/reviews').json()['detections']==[]
        assert client.get('/events/empty/review').status_code==200


def test_alert_review_links_resolution_original_payload_unchanged(reviewed):
    service,event,alert=reviewed;store=Reviews(service.db)
    with service.db.connect() as db:original=db.execute('SELECT payload FROM alerts WHERE id=?',(alert['id'],)).fetchone()[0]
    review=store.save(event,detection_id('e-1',1),ReviewRequest(**body(status='false_positive')))
    with TestClient(create_app(service.settings,service=service)) as client:
        path='/api/alerts/'+alert['id']+'/changes'
        change={'action':'acknowledge','comment':'Revisión humana: no invalida la regla automática',
                'request_id':'alert-review-01','expected_version':0,'reason_code':'false_positive','review_ids':[review['id']]}
        assert client.post(path,json={**change,'review_ids':['missing']}).status_code==409
        assert client.post(path,json={**change,'review_ids':[]}).status_code==409
        response=client.post(path,json=change);assert response.status_code==200,response.text
        first=response.json()['change']
        assert client.post(path,json=change).json()['change']==first
        change.update(action='resolve',request_id='alert-review-02',expected_version=1)
        response=client.post(path,json=change);assert response.status_code==200,response.text
        a=response.json()['alert'];assert a['status']=='resolved' and a['history'][-1]['review_ids']==[review['id']]
        assert client.get('/api/events/e-1').json()==event
    with service.db.connect() as db:assert original==db.execute('SELECT payload FROM alerts WHERE id=?',(alert['id'],)).fetchone()[0]


def test_academic_identity_stays_out_of_technical_api(reviewed):
    service,_,_=reviewed
    with TestClient(create_app(service.settings,service=service)) as client:
        page=client.get('/').text
        assert 'Bryan Edgardo Romo Gonzalez' in page and '745268' in page
        assert 'Nombre y matrícula pendientes' not in page
        assert '745268' not in client.get('/api/configuration').text
