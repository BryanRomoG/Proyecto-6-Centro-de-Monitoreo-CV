"""Contratos de privacidad, copia derivada y atribución sin modificar originales."""
import hashlib
import json
from pathlib import Path
import pytest
from prepare_public_release import broken_links,findings,project_bytes,scrub,EXCLUDED_IMAGE
from monitor_cv.config import ROOT
from prepare_authorized_demo import prepare_authorized


def test_public_selection_preserves_attribution_and_omits_contact_photo():
    public=json.loads((ROOT/'config/dataset-selection-public.json').read_text(encoding='utf-8'))
    original=json.loads((ROOT/'config/dataset-selection.json').read_text(encoding='utf-8'))
    rows={r['image_id']:r for r in original['images']}
    assert len(public['images'])==79
    assert len({r['sha256'] for r in public['images']})==79
    assert EXCLUDED_IMAGE not in {r['image_id'] for r in public['images']}
    for row in public['images']:
        assert row==rows[row['image_id']]
        assert row['author'] and row['author_url'] and row['license_url']
        assert not any('contact_or_example' in f['types'] for f in findings(row['author']))


def test_sanitized_json_records_fields_and_preserves_original_hash(tmp_path):
    source=tmp_path/'event.json'
    fixture_path='C:'+'\\Users\\'+'someone\\OneDrive - campus\\private\\images'
    source.write_text(json.dumps({'id':'evt-original','config':{'source':{'images_dir':fixture_path}},
                                 'config_sha256':'original-config-hash','score':.17536601693758413}),encoding='utf-8')
    before=hashlib.sha256(source.read_bytes()).hexdigest();changes=[]
    projected=json.loads(project_bytes(source,changes))
    assert hashlib.sha256(source.read_bytes()).hexdigest()==before
    assert projected['config']['source']['images_dir']=='[LOCAL_PATH_OMITTED]'
    assert projected['config_sha256']=='original-config-hash' and projected['score']==.17536601693758413
    assert changes[0]['field']=='$/config/source/images_dir'


def test_public_projection_never_rewrites_executable_code(tmp_path):
    path=tmp_path/'script.py'
    content="original = 'C:' + '\\\\Users\\\\'\n"
    path.write_text(content,encoding='utf-8')
    changes=[]
    assert project_bytes(path,changes)==path.read_bytes() and changes==[]


def test_secret_rejects_copy_without_exposing_value():
    with pytest.raises(ValueError,match='Posible secreto'):
        scrub({'secret':'ghp_'+'a'*40},[])


def test_link_validation_checks_selection_boundaries(tmp_path):
    (tmp_path/'ok.md').write_text('[correcto](ok.md) [ausente](missing.json) [fuera](../private.json)',encoding='utf-8')
    assert {r['target'] for r in broken_links(tmp_path)}=={'missing.json','../private.json'}


def test_authorized_preparation_refuses_overwriting_old_demo(tmp_path):
    (tmp_path/'source.jpg').write_bytes(b'old input')
    with pytest.raises(ValueError,match='conservarlos'):
        prepare_authorized(tmp_path)
    assert (tmp_path/'source.jpg').read_bytes()==b'old input'


def test_legacy_preparer_cannot_download_unlicensed_sample(tmp_path):
    from prepare_demo import prepare
    with pytest.raises(ValueError,match='No se descarga dog.jpg'):
        prepare(tmp_path/'new-demo')
    assert not (tmp_path/'new-demo').exists()


def test_confirmed_academic_section_is_rendered_without_technical_leak(settings):
    from fastapi.testclient import TestClient
    from monitor_cv.application import create_app
    with TestClient(create_app(settings)) as client:
        page=client.get('/').text
        assert 'O2026_ESI3906B' in page and 'https://canvas.iteso.mx/courses/57431' in page
        assert '745268' not in json.dumps(client.get('/api/configuration').json())
