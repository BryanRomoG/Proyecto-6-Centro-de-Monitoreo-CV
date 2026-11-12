"""Caso histórico real: revisión desde Edge, sin sustituir respuestas o inferencias."""
import hashlib
import json
import os
from pathlib import Path
import uuid
import csv
import time
from io import StringIO

import httpx
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
EVENT='evt-37c2579bd3af445fb8a683807642e8ee'


def test_real_dog_cat_review_and_all_routes():
    output=ROOT/os.getenv('MONITOR_BROWSER_EVIDENCE','evidencias/cierre_final/navegador')/('review-'+uuid.uuid4().hex)
    output.mkdir(parents=True)
    base=os.getenv('MONITOR_TEST_URL','http://127.0.0.1:8006')
    report={'event_id':EVENT,'mocked_responses':False,'ok':False,'checks':{}}
    checks=report['checks']
    with httpx.Client(base_url=base,timeout=30,trust_env=False) as api, sync_playwright() as p:
        event_id=os.getenv('MONITOR_REVIEW_EVENT',EVENT)
        response=api.get('/api/events/'+event_id)
        if response.status_code==404 and not os.getenv('MONITOR_REVIEW_EVENT'):
            # Una copia nueva no contiene los IDs de otra base local. Generar un run real
            # de la colección animales solo si no existe el caso histórico.
            assert api.get('/api/status').json()['state'] not in {'running','paused'}
            source=next(s for s in api.get('/api/sources').json() if s.get('collection')=='animales')
            started=api.post('/api/monitor/start',json={'source_id':source['id'],'sample_hz':20,'loop':False})
            assert started.status_code==202
            deadline=time.monotonic()+30
            while api.get('/api/status').json()['state']=='running' and time.monotonic()<deadline:time.sleep(.1)
            status=api.get('/api/status').json();assert status['state']=='completed',status
            candidates=api.get('/api/events',params={'run_id':status['run_id'],'limit':100}).json()
            event_id=next(e['id'] for e in candidates if e.get('input_image',{}).get('image_id')=='488d4412c71bf3f1')
            response=api.get('/api/events/'+event_id)
        assert response.status_code==200,response.text
        report['event_id']=event_id
        original=response.json()
        before=api.get('/images/'+event_id).content
        assert [(d['class_name'],d['zone']) for d in original['detections']]==[('dog','doubt'),('cat','low')]
        report['original_scores']={d['class_name']:d['confidence'] for d in original['detections']}
        browser=p.chromium.launch(channel='msedge',headless=True)
        page=browser.new_page(viewport={'width':1366,'height':1000})
        page.set_default_timeout(20000)
        expect.set_options(timeout=20000)
        errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
        try:
            page.goto(base+'/events/'+event_id+'/review')
            expect(page.locator('#review-detections tr')).to_have_count(2)
            page.wait_for_function("document.querySelector('#review-image').naturalWidth>0")
            page.screenshot(path=str(output/'predicciones-originales.png'),mask=[page.locator('aside small')])
            for name,status,reason in [('dog','confirmed','Observación visual de la captura: corresponde a un perro.'),
                                      ('cat','false_positive','La caja cat se superpone al mismo perro; no se observa un gato en esta captura.')]:
                data=api.get('/api/events/'+event_id+'/reviews').json()
                detection=next(d for d in data['detections'] if d['original']['class_name']==name)
                page.locator('#review-detection').select_option(detection['id'])
                if detection['status']!=status:
                    page.locator('#review-status').select_option(status)
                    page.locator('#review-reason').fill(reason)
                    page.locator('#review-save').click()
                    expect(page.locator('#feedback')).to_contain_text('Revisión guardada')
                    expect(page.locator('#review-reason')).to_have_value('')
                expect(page.locator('#review-detections')).to_contain_text('Confirmada' if status=='confirmed' else 'Falso positivo')
            page.locator('#review-layer').select_option('reviewed')
            expect(page.locator('#review-summary')).to_contain_text('1 validadas')
            page.wait_for_function("document.querySelector('#review-image').complete && document.querySelector('#review-image').naturalWidth>0")
            page.screenshot(path=str(output/'revision-validada.png'),mask=[page.locator('aside small')])
            view=api.get('/api/events/'+event_id+'/reviews').json()
            assert [d['original']['class_name'] for d in view['validated']]==['dog']
            assert len(view['overlaps'])==1
            checks['dog_confirmed_cat_rejected_and_overlap_warning']=True
            page.reload();expect(page.locator('#review-detections')).to_contain_text('Falso positivo')
            expect(page.locator('#review-detections')).to_contain_text('Confirmada')
            checks['reload_persists_review']=True
            alert_id=view['alerts'][0]
            page.goto(base+'/alerts/'+alert_id)
            expect(page.locator('#alert-review-links input')).to_have_count(2)
            cat=next(d for d in view['detections'] if d['original']['class_name']=='cat')
            page.locator('#alert-reason').select_option('false_positive')
            page.locator('input[value="'+cat['review']['id']+'"]').check()
            comment='Revisión humana: cat se rechaza y dog se confirma. La baja confianza automática fue real; se cierra la gestión de esta alerta.'
            for action,required in [('acknowledge','active'),('resolve','acknowledged')]:
                alert=api.get('/api/alerts/'+alert_id).json()
                if alert['status']==required:
                    page.locator('#alert-comment').fill(comment)
                    page.locator('#'+action).click()
                    expect(page.locator('#alert-state')).to_have_text('Reconocida' if action=='acknowledge' else 'Resuelta')
            expect(page.locator('#alert-state')).to_have_text('Resuelta')
            page.screenshot(path=str(output/'alerta-revisada.png'),mask=[page.locator('aside small')])
            alert=api.get('/api/alerts/'+alert_id).json()
            assert cat['review']['id'] in alert['history'][-1]['review_ids']
            checks['alert_resolution_keeps_automatic_condition_and_review_links']=True
            assert api.get('/api/events/'+event_id).json()==original
            assert api.get('/images/'+event_id).content==before
            checks['original_event_and_capture_unchanged']=True
            for route,selector in [('/','#dashboard-cards article'),('/playback','#frame-empty'),
                ('/events','#query-results tr'),('/alerts','#query-results tr'),('/history','#historical-charts svg'),
                ('/gallery','#gallery-grid article'),('/sources','#sources-list article'),('/runs','#runs-list table'),
                ('/configuration','#configuration-content')]:
                page.goto(base+route)
                expect(page.locator(selector).first).to_be_visible()
                if route=='/configuration':expect(page.locator(selector)).to_contain_text('allowed_media_roots')
                expect(page.locator('#app-error')).to_be_hidden()
            checks['all_nine_sections_render_real_data']=True
            page.goto(base+'/events?run_id=run-ausente-demo')
            expect(page.locator('#query-count')).to_contain_text('0 registros coincidentes')
            expect(page.locator('#query-results')).to_contain_text('No hay eventos')
            expect(page.locator('[name=run_id]')).to_have_value('run-ausente-demo')
            checks['unknown_run_stays_empty_after_client_initialization']=True
            page.goto(base+'/events?run_id='+original['run_id'])
            expect(page.locator('#query-results tr')).to_have_count(10)
            with page.expect_download() as transfer:
                page.locator('#export-csv').click()
            downloaded=transfer.value
            content=Path(downloaded.path()).read_bytes()
            rows=list(csv.DictReader(StringIO(content.decode('utf-8-sig'))))
            assert len(rows)==10 and {row['id'] for row in rows}=={e['id'] for e in api.get('/api/events',params={'run_id':original['run_id']}).json()}
            checks['native_filtered_csv_download_verified']=True
            report['csv_download']={'filename':downloaded.suggested_filename,'sha256':hashlib.sha256(content).hexdigest(),'rows':len(rows)}
            issue=api.get('/api/gallery/issues',params={'limit':1}).json()['items'][0]
            page.goto(base+'/events/'+issue['id']+'/review')
            expect(page.locator('#review-summary')).to_contain_text('0 predicciones')
            expect(page.locator('#review-save')).to_be_disabled()
            expect(page.locator('#review-image')).to_be_hidden()
            checks['real_technical_event_has_explicit_empty_review']=True
            page.goto(base+'/events/'+event_id+'/review')
            page.set_viewport_size({'width':390,'height':844})
            expect(page.locator('#review-detections tr')).to_have_count(2)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            checks['mobile_review_no_document_overflow']=True
            page.screenshot(path=str(output/'revision-movil.png'),mask=[page.locator('aside small')])
            assert not errors,errors
            report.update(ok=True,review=view,alert=alert,original_event=original,
                          original_capture_sha256=hashlib.sha256(before).hexdigest(),javascript_errors=errors)
        finally:
            browser.close()
            (output/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
