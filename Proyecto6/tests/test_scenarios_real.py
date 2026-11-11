from pathlib import Path

import pytest

from monitor_cv.config import ROOT, Settings
from monitor_cv.service import MonitorService
from run_demo import export_run
from verify_metrics import verify


@pytest.mark.real
@pytest.mark.parametrize("scenario,folder", [("C1", "normal"), ("C2", "baja-confianza")])
def test_real_scenario_and_independent_recalculation(tmp_path, scenario, folder):
    if not (ROOT / "modelo/yolox_nano.onnx").is_file() or not (ROOT / f"data/demo/{folder}").is_dir():
        pytest.skip("Requiere download_model.py y prepare_demo.py")
    settings = Settings.model_validate({"source": {"images_dir": f"data/demo/{folder}", "sample_hz": 60},
                                        "storage": {"data_dir": str(tmp_path / "runtime")}})
    service = MonitorService(settings)
    run_id = service.start(max_frames=3)
    service.thread.join(timeout=30)
    assert not service.thread.is_alive() and service.error is None
    directory = tmp_path / "export"
    report = export_run(service, run_id, directory, scenario)
    assert report["inference_chain_observed"]
    assert report["successful_frames"] == 3
    assert verify(directory)["ok"]
    assert all(not e["synthetic"] for e in service.db.list("events", run_id))
