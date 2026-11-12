import json

import pytest

from monitor_cv.config import ROOT, Settings, load_settings
from monitor_cv.events import uid
from run_authorized_scenarios import run as run_suite
from verify_extras import verify


@pytest.mark.real
def test_all_scenarios_with_real_outputs_and_labelled_fault(tmp_path):
    if not (ROOT/'modelo/yolox_nano.onnx').is_file() or not (ROOT/'data/media/datasets/manifest.json').is_file():
        pytest.skip('Requiere pesos e imágenes públicas preparadas')
    directory=tmp_path/uid('suite')
    data=load_settings(environ=False).model_dump()
    data['storage']['data_dir']=str(tmp_path/'isolated-runtime')
    results=run_suite(directory,base=Settings.model_validate(data))
    assert all(result['observed'] for result in results.values()),results
    assert results['S7']['fault_simulated'] is True
    assert results['S1']['fault_simulated'] is False
    for name in ['C1','C2','Video','S1','S2','S3','S4','S5','S6-v1','S6-v2','S7']:
        assert verify(directory/name)['ok']
    windows=[json.loads(line) for line in (directory/'S4/windows.jsonl').read_text(encoding='utf-8').splitlines()]
    assert [w['state'] for w in windows]==['collecting_reference','collecting_reference','change_pending','sustained_change','within_policy']
