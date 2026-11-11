from copy import deepcopy

import pytest
import yaml

from monitor_cv.config import Confidence, Settings, load_settings
from monitor_cv.confidence import ConfidenceMonitor, zone


@pytest.mark.parametrize("score,expected", [(0, "low"), (.599999, "low"), (.6, "doubt"), (.79999, "doubt"), (.8, "accepted"), (1, "accepted")])
def test_boundary_zones(score, expected):
    assert zone(score, .6, .8) == expected


@pytest.mark.parametrize("score", [-.01, 1.1, float("nan")])
def test_invalid_score(score):
    with pytest.raises(ValueError):
        zone(score, .6, .8)


@pytest.mark.parametrize("data", [
    {"confidence": {"lower": .8, "upper": .6}},
    {"confidence": {"lower": .6, "upper": .6}},
    {"detector": {"score_floor": .65}},
    {"source": {"sample_hz": 0}},
    {"source": {"sample_hz": float("nan")}},
    {"source": {"url": "http://user:secret@camera:81/stream"}},
    {"unknown": True}, {"storage": {"database": "../other.sqlite3"}},
])
def test_rejects_invalid_config(data):
    with pytest.raises(ValueError):
        Settings.model_validate(data)


def test_env_fingerprint_and_unknown_field(tmp_path, monkeypatch):
    path = tmp_path / "settings.yaml"
    path.write_text("version: 1\n", encoding="utf-8")
    base = load_settings(path, environ=False)
    monkeypatch.setenv("MONITOR_CAMERA_URL", "http://192.168.68.109:81/stream")
    effective = load_settings(path)
    assert effective.source.url.endswith("109:81/stream")
    assert base.fingerprint != effective.fingerprint
    assert load_settings(path, environ=False).fingerprint == base.fingerprint


def test_reference_sustained_and_insufficient(event):
    conf = Confidence(window_frames=1, min_detections=1, reference_windows=1,
                      sustained_windows=2, increase=.2)
    monitor = ConfidenceMonitor(conf)
    high = deepcopy(event)
    high["detections"][0]["zone"] = "accepted"
    base = monitor.add(high)
    assert base["state"] == "collecting_reference"
    first = monitor.add(event)
    assert first["state"] == "change_pending" and first["baseline_ratio"] == 0
    change = monitor.add(event)
    assert change["state"] == "sustained_change"
    assert base["id"] in change["reference_window_ids"]
    assert len(change["sustained_window_ids"]) == 2
    empty = deepcopy(event)
    empty["status"], empty["detections"] = "no_detections", []
    assert monitor.add(empty)["state"] == "insufficient_evidence"
    assert monitor.add(event)["state"] == "change_pending"  # insuficiencia rompe continuidad
    assert monitor.add(high)["state"] == "within_policy"


def test_partial_window_and_errors_not_normal(event):
    monitor = ConfidenceMonitor(Confidence(window_frames=2, min_detections=1, reference_windows=1))
    assert monitor.add(event) is None
    bad = deepcopy(event)
    bad["status"], bad["detections"] = "inference_error", []
    window = monitor.add(bad)
    assert window["state"] == "insufficient_evidence"
    assert monitor.reference == []
