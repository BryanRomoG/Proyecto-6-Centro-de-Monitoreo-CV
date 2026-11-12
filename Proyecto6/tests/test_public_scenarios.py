"""C1/C2 reales que solo requieren fotos con licencia individual identificada."""
import json
from monitor_cv.config import ROOT,Settings,load_settings
from run_public_scenarios import run
from verify_metrics import verify
import pytest


@pytest.mark.real
def test_public_scenarios_real_and_isolated(tmp_path):
    if not (ROOT/'modelo/yolox_nano.onnx').is_file() or not (ROOT/'data/media/datasets/manifest.json').is_file():
        pytest.skip('Requiere modelo y adquisición pública documentada')
    data=load_settings(environ=False).model_dump();data['storage']['data_dir']=str(tmp_path/'runtime')
    output=tmp_path/'public-scenarios'
    result=run(output,base=Settings.model_validate(data),sample_hz=60)
    assert result['ok'] and result['same_model_and_monitoring_policy']
    images=json.loads((ROOT/'data/media/datasets/manifest.json').read_text(encoding='utf-8'))['images']
    counts={case:sum(r['category']==collection for r in images) for case,collection in [('C1_PUBLIC','escenas_multiples'),('C2_PUBLIC','baja_confianza')]}
    assert result['unique_inputs']==sum(counts.values()) and result['new_original_photographs']==0
    assert not result['additional_scenario_bonus_claimed']
    for case in ['C1_PUBLIC','C2_PUBLIC']:
        assert result['scenarios'][case]['events']==counts[case]
        assert verify(output/case)['ok']
