"""Recorrido Edge de C1/C2 públicos aislados; no inicia inferencias ni modifica datos."""
import argparse
import hashlib
import json
from pathlib import Path
import uuid

import httpx
from playwright.sync_api import sync_playwright,expect

ROOT=Path(__file__).resolve().parents[1]


def verify(url,summary_path):
    summary=json.loads(summary_path.read_text(encoding='utf-8'))
    output=ROOT/'evidencias/cierre_final/navegador'/('public-'+uuid.uuid4().hex);output.mkdir(parents=True)
    report={'ok':False,'mocked_responses':False,'isolated':summary['isolated_from_main_runtime'],'checks':{}}
    checks=report['checks']
    with httpx.Client(base_url=url,trust_env=False,timeout=30) as api,sync_playwright() as engine:
        browser=engine.chromium.launch(channel='msedge',headless=True)
        page=browser.new_page(viewport={'width':1366,'height':1000})
        try:
            for scenario,data in summary['scenarios'].items():
                run=data['run_id'];events=api.get('/api/events',params={'run_id':run,'limit':100}).json()
                assert len(events)==10 and all(e['inference_executed'] and not e['synthetic'] for e in events)
                page.goto(url+'/events?run_id='+run)
                expect(page.locator('#query-results tr')).to_have_count(10)
                checks[scenario+'_events_visible']=True
                event=events[0];page.goto(url+'/events/'+event['id'])
                expect(page.locator('.capture')).to_be_visible()
                raw=api.get('/images/'+event['id']).content
                assert hashlib.sha256(raw).hexdigest()==event['image_sha256']
                assert event['config']['source']['images_dir'].startswith('data/media/datasets/')
                checks[scenario+'_image_link_hash_and_relative_config']=True
                page.screenshot(path=str(output/(scenario+'-evento.png')),mask=[page.locator('aside small')])
                page.goto(url+'/gallery?run_id='+run)
                expect(page.locator('#gallery-grid article')).to_have_count(10)
                page.wait_for_function("document.querySelector('#gallery-grid img').naturalWidth>0")
                checks[scenario+'_gallery_visible']=True
                alerts=api.get('/api/alerts',params={'run_id':run,'limit':100}).json()
                assert alerts
                page.goto(url+'/alerts/'+alerts[0]['id'])
                expect(page.locator('h2')).to_contain_text('low-confidence-v1')
                expect(page.locator('#alert-state')).to_have_text('Abierta')
                checks[scenario+'_real_alert_visible']=True
            assert api.get('/api/status').json()['state']=='idle'
            checks['no_processing_started_by_browser_check']=True
            report.update(ok=True,summary=summary,test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        finally:
            browser.close();(output/'verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'ok':report['ok'],'checks':len(checks),'output':output.relative_to(ROOT).as_posix()}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:8008')
    parser.add_argument('--summary',type=Path,required=True)
    args=parser.parse_args();verify(args.url,args.summary)
