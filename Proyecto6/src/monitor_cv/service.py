"""Productor de imágenes/video con controles sincronizados y observaciones persistentes."""
from __future__ import annotations

from dataclasses import asdict
import logging
import platform
from pathlib import Path
import subprocess
import sys
import threading
import time

import psutil

from . import __version__
from .alerts import evaluate
from .camera import decode, open_source, png_bytes
from .confidence import ConfidenceMonitor, zone
from .config import ROOT, Settings
from .database import Database
from .detector import Detector
from .events import sha256_bytes, uid, utc_now
from .metrics import calculate

LOG = logging.getLogger(__name__)


def revision():
    result = subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


class MonitorService:
    def __init__(self, settings: Settings, database=None, detector_factory=Detector, source_factory=None):
        self.settings = settings
        self.base_settings = settings
        self.db = database or Database(settings.data_dir / settings.storage.database)
        self.detector_factory = detector_factory
        self.source_factory = source_factory
        self.stop_signal = threading.Event()
        self.pause_signal = threading.Event()
        self.thread = None
        self.lock = threading.RLock()
        self.processing_lock = threading.RLock()
        self.run_id = None
        self.run = None
        self.latest_event = None
        self.error = None
        self.state = "idle"
        self.paused_total = 0.
        self.pause_started = None
        self.paused_cpu_total = 0.
        self.pause_cpu_started = 0.
        self.dataset_inputs = {}

    def start(self, max_frames=None, *, settings=None):
        with self.lock:
            if self.thread and self.thread.is_alive():
                raise ValueError("Ya hay una ejecución activa")
            chosen = settings or self.base_settings
            if chosen.data_dir != self.base_settings.data_dir:
                raise ValueError("No cambiar el almacén durante el servicio")
            detector = self.detector_factory(chosen)
            source = (self.source_factory or open_source)(chosen)
            self.settings = chosen
            self.dataset_inputs = {}
            if chosen.source.dataset_manifest:
                import json
                from .sources import allowed_path
                manifest_path=allowed_path(chosen,chosen.source.dataset_manifest)
                manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
                folder=chosen.path(chosen.source.images_dir)
                self.dataset_inputs={Path(row['path']).name:row for row in manifest['images']
                    if row['category']==chosen.source.collection and chosen.path(row['path']).parent==folder}
            self.stop_signal.clear()
            self.pause_signal.clear()
            self.error = None
            self.latest_event = None
            self.paused_total, self.pause_started = 0., None
            self.paused_cpu_total = 0.
            self.run_id = uid("run")
            self.state = "running"
            self.thread = threading.Thread(target=self._execute, args=(detector, source, self.run_id, max_frames), daemon=True)
            self.thread.start()
            return self.run_id

    def _action(self, action, before, after):
        record = {"id": uid("action"), "run_id": self.run_id, "timestamp": utc_now(),
                  "action": action, "from_state": before, "to_state": after}
        self.db.insert_record("actions", record)
        if self.run:
            self.run["status"] = after
            self.db.save_run(self.run)

    def pause(self):
        # Al responder, ninguna inferencia queda en vuelo; la UI mantiene el último frame.
        with self.processing_lock:
            if self.state != "running":
                raise ValueError("Solo se puede pausar una ejecución en marcha")
            self.pause_started = time.perf_counter()
            self.pause_cpu_started = sum(psutil.Process().cpu_times()[:2])
            self.pause_signal.set()
            self._action("pause", self.state, "paused")
            self.state = "paused"
        return self.status()

    def resume(self):
        with self.processing_lock:
            if self.state != "paused":
                raise ValueError("No hay una ejecución pausada")
            self.paused_total += time.perf_counter() - self.pause_started
            self.paused_cpu_total += max(0.,sum(psutil.Process().cpu_times()[:2])-self.pause_cpu_started)
            self.pause_started = None
            self._action("resume", self.state, "running")
            self.state = "running"
            self.pause_signal.clear()
        return self.status()

    def stop(self):
        self.stop_signal.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=self.settings.source.timeout_seconds + 3)
        if self.thread and self.thread.is_alive():
            self.state = "stopping"
        return self.status()

    def status(self):
        with self.lock:
            event = self.latest_event
            return {"state": self.state, "run_id": self.run_id, "error": self.error,
                    "config_sha256": self.settings.fingerprint,
                    "source": self.settings.source.model_dump(),
                    "model": self.run.get("model") if self.run else None,
                    "latest_event_id": event["id"] if event else None,
                    "frame_index": event.get("frame_index") if event else None,
                    "position_seconds": event.get("position_seconds") if event else None,
                    "total_frames": event.get("total_frames") if event else None,
                    "frames_processed": self.run.get("events_processed", 0) if self.run else 0}

    def current(self):
        with self.lock:
            if self.latest_event is None:
                return {"state": self.state, "event": None}
            e = self.latest_event
            return {"state": self.state, "event": e,
                    "image_url": f"/images/{e['id']}" if e.get("image_ref") else None,
                    "annotated_url": f"/images/{e['id']}/annotated" if e.get("image_ref") else None}

    def _execute(self, detector, source, run_id, max_frames):
        settings = self.settings
        rev = revision()
        run = {"id": run_id, "started_at": utc_now(), "finished_at": None, "status": "running",
               "model": detector.identity, "config": settings.model_dump(), "config_sha256": settings.fingerprint,
               "application_version": __version__, "git_revision": rev,
               "environment": {"python": sys.version, "platform": platform.platform()},
               "source": settings.source.model_dump(), "synthetic": bool(detector.synthetic), "events_processed": 0}
        self.run = run
        monitor = ConfidenceMonitor(settings.confidence)
        process = psutil.Process()
        previous_cpu = sum(process.cpu_times()[:2])
        previous_completion, previous_paused = time.perf_counter(), 0.
        previous_paused_cpu = 0.
        try:
            self.db.save_run(run)
            iterator = iter(source.packets(self.stop_signal))
            while not self.stop_signal.is_set():
                if self.pause_signal.is_set():
                    self.stop_signal.wait(.03)
                    continue
                with self.processing_lock:
                    if self.stop_signal.is_set() or self.pause_signal.is_set():
                        continue
                    try:
                        packet = next(iterator)
                    except StopIteration:
                        break
                    started = time.perf_counter()
                    event = self._process(packet, detector, run_id)
                    completion = time.perf_counter()
                    event["attempt_elapsed_s"] = max(1e-9, completion-previous_completion-(self.paused_total-previous_paused))
                    event["paused_seconds_excluded"] = self.paused_total-previous_paused
                    event["processing_ms"] = (completion-started)*1000
                    event["rss_bytes"] = process.memory_info().rss
                    cpu = sum(process.cpu_times()[:2])
                    event["cpu_seconds_delta"] = max(0., cpu-previous_cpu-(self.paused_cpu_total-previous_paused_cpu))
                    event["cpu_percent"] = event["cpu_seconds_delta"]/event["attempt_elapsed_s"]*100
                    previous_completion, previous_cpu, previous_paused = completion, cpu, self.paused_total
                    previous_paused_cpu = self.paused_cpu_total
                    window = monitor.add(event)
                    event["confidence_state"] = monitor.last_state
                    if window:
                        window.update(run_id=run_id, config_sha256=settings.fingerprint)
                    alerts = evaluate(event, window, settings)
                    self.db.save_observation(event, alerts, window)
                    self.db.save_metrics(self.metrics(run_id))
                    run["events_processed"] += 1
                    with self.lock:
                        # Publicar solo DESPUÉS de persistir: imagen/detecciones comparten un ID inmutable.
                        self.latest_event = event
                    if max_frames is not None and run["events_processed"] >= max_frames:
                        break
                # Nunca mantener el bloqueo de procesamiento durante la espera de reproducción.
                effective_hz = min(settings.source.sample_hz,getattr(source,"fps",settings.source.sample_hz))
                remaining = max(0., 1/effective_hz-(time.perf_counter()-started))
                self.stop_signal.wait(remaining)
            run["status"] = "stopped" if self.stop_signal.is_set() else "completed"
            self.state = run["status"]
        except Exception as exc:
            LOG.exception("Error de procesamiento")
            self.error = f"{type(exc).__name__}: {exc}"
            run.update(status="error", error=self.error)
            self.state = "error"
        finally:
            if self.pause_started is not None:
                self.paused_total += time.perf_counter()-self.pause_started
                self.pause_started = None
            try:
                source.close()
            except Exception as exc:
                self.error = f"Cierre de fuente: {exc}"
                run.update(status="error", error=self.error)
                self.state = "error"
            run.update(finished_at=utc_now(), paused_seconds=self.paused_total)
            try:
                self.db.save_run(run)
            except Exception as exc:
                self.error = f"Persistencia final: {exc}"
                self.state = "error"
                LOG.exception("No se pudo conservar estado final")

    def _process(self, packet, detector, run_id):
        settings = self.settings
        event = {"id": uid("evt"), "run_id": run_id, "frame_id": uid("frame"),
                 "timestamp": utc_now(), "captured_at": packet.captured_at,
                 "source_id": settings.source.source_id, "source_kind": settings.source.kind,
                 "input_name": packet.name, "input_sha256": sha256_bytes(packet.data) if packet.data else None,
                 "task": "object_detection", "model": detector.identity,
                 "config_sha256": settings.fingerprint, "config": settings.model_dump(),
                 "application_version": __version__, "synthetic": bool(detector.synthetic),
                 "status": "source_error" if packet.error else "ok", "error": packet.error,
                 "detections": [], "candidates": [], "inference_ms": None,
                 "inference_executed": False, "image_ref": None, "image_sha256": None}
        event['collection']=settings.source.collection
        if settings.source.dataset_manifest and packet.name not in self.dataset_inputs:
            event.update(status='source_error',error='Imagen fuera del manifiesto de esta colección; no se ejecuta inferencia')
            return event
        if origin:=self.dataset_inputs.get(packet.name):
            event['input_image']={k:origin.get(k) for k in ['image_id','dataset','path','sha256','category','original_url','landing_url','author','author_url','title','license_url','license_name','redistribution']}
            if packet.data and sha256_bytes(packet.data)!=origin['sha256']:
                event.update(status='source_error',error='La entrada difiere del SHA del dataset; no se ejecuta inferencia')
                return event
        for key in ["frame_index", "position_seconds", "total_frames", "read_frames", "discarded_frames", "read_elapsed_s"]:
            event[key] = getattr(packet, key, None)
        if packet.data and not packet.error:
            try:
                rgb = decode(packet.data)
            except Exception as exc:
                event.update(status="decode_error", error=str(exc))
            else:
                image = png_bytes(rgb)
                relative = f"images/{event['id']}.png"
                path = settings.data_dir/relative
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("xb") as handle:
                    handle.write(image)
                event.update(image_ref=relative, image_sha256=sha256_bytes(image))
                try:
                    event.update(detector.infer(rgb))
                    event["inference_executed"] = True
                    for d in event["detections"]:
                        d["zone"] = zone(d["confidence"], settings.confidence.lower, settings.confidence.upper)
                    if not event["detections"]:
                        event["status"] = "no_detections"
                except Exception as exc:
                    event.update(status="inference_error", error=str(exc), detections=[])
        event["timestamp"] = utc_now()
        return event

    def metrics(self, run_id=None):
        run_id = run_id or self.run_id
        if run_id is None:
            latest = self.db.list("runs", limit=1)
            run_id = latest[0]["id"] if latest else "no-run"
        return calculate(self.db.list("events", run_id), self.db.list("alerts", run_id),
                         run_id=run_id, data_dir=self.settings.data_dir,
                         window_seconds=self.settings.metrics.window_seconds)

