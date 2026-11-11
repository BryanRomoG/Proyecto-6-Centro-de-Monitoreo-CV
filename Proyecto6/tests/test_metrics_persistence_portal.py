from copy import deepcopy
from datetime import datetime, timedelta, timezone
import sqlite3

from fastapi.testclient import TestClient
import pytest

from monitor_cv.alerts import evaluate
from monitor_cv.database import Database
from monitor_cv.main import create_app
from monitor_cv.metrics import calculate, trace_complete
from monitor_cv.service import MonitorService


def test_seven_metrics_by_hand(event, settings):
    now = (datetime.fromisoformat(event["timestamp"]) + timedelta(seconds=2)).isoformat()
    alert = evaluate(event, None, settings)[0]
    result = calculate([event], [alert], run_id="r-1", data_dir=settings.data_dir,
                       window_seconds=60, now=now)
    assert result["values"] == {"G1": 20., "G2": 2., "G3": 100., "G4": 1., "G5": 1., "G6": 2., "G7": 1}
    assert result["event_ids"] == ["e-1"]
    assert result["active_alert_ids"] == [alert["id"]]


def test_missing_no_detections_and_window(event, settings):
    empty = calculate([], [], run_id="r-1", data_dir=settings.data_dir, window_seconds=60)
    assert all(empty["values"][g] is None for g in ["G1", "G2", "G3", "G4", "G5", "G6"])
    assert empty["values"]["G7"] == 0 and empty["state"] == "insufficient_evidence"
    event["status"], event["detections"] = "no_detections", []
    result = calculate([event], [], run_id="r-1", data_dir=settings.data_dir,
                       window_seconds=60, now=event["timestamp"])
    assert result["values"]["G4"] is None and result["values"]["G1"] == 20
    future = (datetime.fromisoformat(event["timestamp"]) + timedelta(seconds=61)).isoformat()
    aged = calculate([event], [], run_id="r-1", data_dir=settings.data_dir, window_seconds=60, now=future)
    assert aged["values"]["G1"] is None and aged["values"]["G6"] == 61
    assert aged["values"]["G5"] is None


def test_trace_detects_missing_corrupted_image(event, settings):
    assert trace_complete(event, settings.data_dir)
    (settings.data_dir / event["image_ref"]).write_bytes(b"tampered")
    assert not trace_complete(event, settings.data_dir)
    event["image_ref"] = "../outside.png"
    assert not trace_complete(event, settings.data_dir)


def test_transaction_restart_and_portal(event, settings):
    path = settings.data_dir / "test.sqlite3"
    db = Database(path)
    db.save_run({"id": "r-1", "started_at": event["timestamp"], "status": "test"})
    alert = evaluate(event, None, settings)[0]
    db.save_observation(event, [alert], None)
    reopened = Database(path)
    assert reopened.get("events", event["id"]) == event
    assert reopened.get("alerts", alert["id"])["event_ids"] == [event["id"]]
    service = MonitorService(settings, database=reopened)
    with TestClient(create_app(settings, service=service)) as client:
        for page in ["/", "/events", "/alerts", f"/events/{event['id']}", f"/alerts/{alert['id']}"]:
            response = client.get(page)
            assert response.status_code == 200 and "<html" in response.text
        assert f'/events/{event["id"]}' in client.get(f"/alerts/{alert['id']}").text
        assert f'/images/{event["id"]}' in client.get(f"/events/{event['id']}").text
        assert client.get(f"/images/{event['id']}").headers["content-type"] == "image/png"
        assert client.get("/api/events?run_id=r-1").json()[0]["id"] == "e-1"
        assert client.get("/api/events?limit=0").status_code == 422
        assert client.get("/events?page=0").status_code == 422
        assert client.get("/events?run_id=missing").status_code == 200
        assert "No hay eventos" in client.get("/events?run_id=missing").text
        for missing in ["/events/missing", "/alerts/missing", "/images/missing", "/api/events/missing"]:
            assert client.get(missing).status_code == 404
        assert client.get("/api/metrics?run_id=r-1").json()["values"]["G7"] == 1
    with pytest.raises(sqlite3.IntegrityError):
        db.save_observation(event, [alert], None)
    assert len(db.list("events")) == 1
    with pytest.raises(ValueError):
        db.list("events;DROP TABLE runs")


def test_atomic_failure_does_not_leave_event(event, settings):
    db = Database(settings.data_dir / "rollback.sqlite3")
    db.save_run({"id": "r-1"})
    bad = evaluate(event, None, settings)[0]
    bad["event_id"] = "absent"
    with pytest.raises(sqlite3.IntegrityError):
        db.save_observation(event, [bad], None)
    assert db.list("events") == [] and db.list("alerts") == []


def test_low_alert_condition_and_no_false_error_alert(event, settings):
    assert len(evaluate(event, None, settings)) == 1
    for state in ["no_detections", "inference_error", "source_error"]:
        other = deepcopy(event)
        other["status"] = state
        other["detections"] = []
        assert evaluate(other, None, settings) == []
