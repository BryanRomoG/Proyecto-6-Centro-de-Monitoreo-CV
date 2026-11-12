"""Prueba E2E opcional: servidor local real, Edge y YOLOX; no se simulan respuestas."""
from datetime import datetime,timezone
import hashlib,json,os,time,uuid,zipfile
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright,expect

ROOT=Path(__file__).resolve().parents[1]


def test_collections_gallery_recovery_and_real_controls():
    output=ROOT/os.getenv('MONITOR_BROWSER_EVIDENCE','evidencias/datasets/navegador')/('edge-'+uuid.uuid4().hex);output.mkdir(parents=True)
    base=os.getenv('MONITOR_TEST_URL','http://127.0.0.1:8006')
    report={'timestamp':datetime.now(timezone.utc).isoformat(),'base_url':base,'ok':False,'checks':{},'mocked_responses':False,
            'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    checks=report['checks'];own_runs=[]
    with httpx.Client(base_url=base,timeout=30,trust_env=False) as api,sync_playwright() as engine:
        assert api.get('/api/status').json()['state'] not in {'running','paused'},'Detener productor antes de esta prueba E2E'
        browser=engine.chromium.launch(channel='msedge',headless=True)
        context=browser.new_context(viewport={'width':1366,'height':1000},accept_downloads=True)
        page=context.new_page();page.set_default_timeout(15000)
        active=set();maximum=[0];full_images=[];thumbs=[]
        def request(request):
            if '/thumbnail' in request.url:
                thumbs.append(request.url);active.add(request);maximum[0]=max(maximum[0],len(active))
            elif '/images/' in request.url:full_images.append(request.url)
        page.on('request',request)
        page.on('requestfinished',lambda request:active.discard(request))
        page.on('requestfailed',lambda request:active.discard(request))
        try:
            page.goto(base+'/gallery')
            expect(page.locator('#gallery-grid article')).to_have_count(25)
            first=page.locator('#gallery-grid img').first;first.scroll_into_view_if_needed()
            page.wait_for_function("document.querySelector('#gallery-grid img').naturalWidth>0")
            checks['paged_25']=True;checks['no_full_images_on_open']=not full_images
            checks['thumbnail_concurrency_at_most_4']=maximum[0]<=4
            report['initial_thumbnail_requests']=len(thumbs);report['maximum_thumbnail_concurrency']=maximum[0]
            page.screenshot(mask=[page.locator('aside small')],path=str(output/'galeria-escritorio.png'),full_page=False)
            assert checks['no_full_images_on_open'] and checks['thumbnail_concurrency_at_most_4']
            # Un error real de validación, seguido de reintento desde el botón visible.
            page.locator('[name=min_score]').fill('0.9');page.locator('[name=max_score]').fill('0.1')
            page.get_by_role('button',name='Aplicar filtros',exact=True).click()
            expect(page.locator('#gallery-retry')).to_be_visible()
            page.screenshot(mask=[page.locator('aside small')],path=str(output/'galeria-error-y-reintento.png'))
            page.locator('[name=min_score]').fill('');page.locator('[name=max_score]').fill('')
            page.locator('#gallery-retry').click();expect(page.locator('#gallery-retry')).to_be_hidden()
            expect(page.locator('#gallery-load-state')).to_contain_text('Página cargada')
            checks['real_validation_error_and_button_retry']=True
            for category in ['personas','vehiculos','animales']:
                page.locator('#collection-filter').select_option(category)
                page.get_by_role('button',name='Aplicar filtros',exact=True).click()
            expect(page.locator('#gallery-grid article').first).to_contain_text('Colección prevista: animales')
            page.wait_for_function("[...document.querySelectorAll('#gallery-grid article')].every(e=>e.textContent.includes('Colección prevista: animales'))")
            checks['rapid_filter_latest_response_wins']=True
            page.reload();expect(page.locator('#collection-filter')).to_have_value('animales')
            expect(page.locator('#gallery-grid article').first).to_contain_text('Colección prevista: animales')
            checks['reload_keeps_filters']=True
            # Una colección nueva tiene diez escenas; paginar sobre la galería completa
            # evita exigir repeticiones históricas de animales para alcanzar una segunda página.
            page.goto(base+'/gallery')
            expect(page.locator('#gallery-grid article')).to_have_count(25)
            page.get_by_role('button',name='Siguiente',exact=True).click()
            expect(page.locator('#page-label')).to_have_text('Página 2')
            assert 'offset=25' in page.url;checks['page_2_url_and_backend']=True
            # Cambios de documento mientras se inicializa la consulta anterior.
            for route in ['/sources','/gallery?collection=vehiculos','/sources','/gallery?collection=animales']:
                page.goto(base+route,wait_until='domcontentloaded')
            expect(page.locator('#gallery-load-state')).to_contain_text('Página cargada')
            expect(page.locator('#gallery-grid article').first).to_contain_text('Colección prevista: animales')
            checks['rapid_section_navigation_recovers']=True
            page.locator('.capture-selection').first.check()
            with page.expect_download() as waiting:page.locator('#download-selection').click()
            download=waiting.value;archive_path=output/'capturas.zip';download.save_as(archive_path)
            with zipfile.ZipFile(archive_path) as archive:
                credit=json.loads(archive.read('ATTRIBUTION.json'))
                assert credit[0]['author'] and credit[0]['license_url']
                event=api.get('/api/events/'+credit[0]['file'][:-4]).json()
                assert hashlib.sha256(archive.read(credit[0]['file'])).hexdigest()==event['image_sha256']
            checks['native_browser_download_and_attribution']=True
            report['download']={'filename':download.suggested_filename,'sha256':hashlib.sha256(archive_path.read_bytes()).hexdigest()}
            # Dos fuentes reales desde los controles de la interfaz, sin API de inicio simulada.
            sources=api.get('/api/sources').json();by_category={s.get('collection'):s for s in sources if s.get('collection')}
            assert len(by_category)==8;checks['eight_collections_registered']=True
            for category in ['animales','vehiculos']:
                page.goto(base+'/playback');expect(page.locator('#source-select option')).to_have_count(len(sources)+1)
                page.locator('#source-select').select_option(by_category[category]['id'])
                page.locator('#playback-hz').fill('2');page.locator('#playback-loop').check()
                page.get_by_role('button',name='Iniciar',exact=True).click()
                page.wait_for_function("document.querySelector('#processed-frame').dataset.eventId")
                run=api.get('/api/status').json()['run_id'];own_runs.append(run)
                page.get_by_role('button',name='Pausar',exact=True).click()
                expect(page.locator('#global-status')).to_have_text('Pausada')
                current=api.get('/api/playback/current').json();event=current['event']
                assert event['collection']==category and event['inference_executed'] and not event['synthetic']
                assert event['input_sha256']==event['input_image']['sha256']
                time.sleep(.2);assert api.get('/api/playback/current').json()['event']['id']==event['id']
                # El portal publica por polling de 1 s: esperar el mismo ID, no asumir actualización instantánea.
                expect(page.locator('#processed-frame')).to_have_attribute('data-event-id',event['id'])
                page.wait_for_function("document.querySelector('#processed-frame').complete&&document.querySelector('#processed-frame').naturalWidth>0")
                assert page.locator('#processed-frame').get_attribute('data-event-id')==event['id']
                page.screenshot(mask=[page.locator('aside small')],path=str(output/(category+'-reproduccion.png')))
                page.get_by_role('button',name='Continuar',exact=True).click()
                page.wait_for_function('(old)=>document.querySelector("#processed-frame").dataset.eventId!==old',arg=event['id'])
                page.get_by_role('button',name='Detener',exact=True).click();expect(page.locator('#global-status')).to_have_text('Detenida')
            checks['two_collections_real_pause_resume_stop']=True;report['control_runs']=own_runs
            page.set_viewport_size({'width':390,'height':844});page.goto(base+'/gallery?collection=animales')
            expect(page.locator('#gallery-load-state')).to_contain_text('Página cargada')
            size=page.evaluate('({viewport:innerWidth,content:document.documentElement.scrollWidth})')
            assert size['content']<=size['viewport'];checks['mobile_no_horizontal_overflow']=True;report['mobile']=size
            page.locator('#gallery-grid img').first.scroll_into_view_if_needed()
            page.wait_for_function("document.querySelector('#gallery-grid img').naturalWidth>0")
            page.screenshot(mask=[page.locator('aside small')],path=str(output/'galeria-movil.png'))
            report['browser']=browser.version;report['ok']=all(checks.values())
        finally:
            state=api.get('/api/status').json()
            if state['run_id'] in own_runs and state['state'] in {'running','paused'}:api.post('/api/monitor/stop')
            (output/'verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
            browser.close()
    assert report['ok']
