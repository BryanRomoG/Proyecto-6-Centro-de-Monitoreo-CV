"""Revisión humana append-only, independiente de las predicciones del detector."""
from copy import deepcopy
import hashlib
import json

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import Literal

from .events import json_text, uid, utc_now


class ReviewRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    status: Literal['pending', 'confirmed', 'false_positive', 'corrected']
    corrected_label: str | None = Field(default=None, max_length=100)
    reason: str = Field(min_length=1, max_length=2000)
    actor: str = Field(default='revisor-local', min_length=1, max_length=100)
    request_id: str = Field(min_length=8, max_length=100)
    expected_version: int = Field(ge=0)

    @field_validator('reason', 'actor', 'corrected_label')
    @classmethod
    def text(cls, value):
        if value is not None and not value.strip():
            raise ValueError('El texto no puede estar vacío')
        return value.strip() if value is not None else value

    @model_validator(mode='after')
    def label(self):
        if (self.status == 'corrected') != (self.corrected_label is not None):
            raise ValueError('Solo una etiqueta corregida requiere corrected_label')
        return self


def detection_id(event_id, index):
    # Índice de la lista inmutable: funciona también para eventos históricos sin ID individual.
    return 'det-' + hashlib.sha256(f'{event_id}:{index}'.encode()).hexdigest()[:24]


def overlap(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    intersection = max(0, x2-x1)*max(0, y2-y1)
    area = lambda box: max(0, box[2]-box[0])*max(0, box[3]-box[1])
    union = area(a)+area(b)-intersection
    return intersection/union if union else 0


class Reviews:
    def __init__(self, database):
        self.db = database
        with database.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS detection_reviews(
                    id TEXT PRIMARY KEY,event_id TEXT NOT NULL REFERENCES events(id),
                    detection_id TEXT NOT NULL,version INTEGER NOT NULL,
                    request_id TEXT UNIQUE NOT NULL,payload TEXT NOT NULL,
                    UNIQUE(event_id,detection_id,version));
                CREATE INDEX IF NOT EXISTS review_event ON detection_reviews(event_id,detection_id,version);
            ''')

    def view(self, event):
        with self.db.connect() as db:
            history = [json.loads(row[0]) for row in db.execute(
                'SELECT payload FROM detection_reviews WHERE event_id=? ORDER BY rowid', (event['id'],))]
        detections = []
        for index, original in enumerate(event['detections']):
            identity = detection_id(event['id'], index)
            changes = [r for r in history if r['detection_id'] == identity]
            detections.append({'id': identity, 'index': index, 'original': deepcopy(original),
                               'review': changes[-1] if changes else None,
                               'status': changes[-1]['status'] if changes else 'pending',
                               'version': changes[-1]['version'] if changes else 0, 'history': changes})
        warnings = []
        for index, a in enumerate(detections):
            for b in detections[index+1:]:
                iou = overlap(a['original']['bbox'], b['original']['bbox'])
                if iou >= .5:
                    warnings.append({'detection_ids': [a['id'], b['id']], 'iou': iou,
                                     'message': 'Cajas superpuestas: revisar; pueden ser objetos distintos.'})
        return {'event_id': event['id'], 'detections': detections, 'history': history,
                'validated': [d for d in detections if d['status'] in {'confirmed', 'corrected'}],
                'overlaps': warnings, 'overlap_threshold': .5,
                'notice': 'Revisión humana; conserva puntuaciones, zonas y métricas originales. No mide accuracy.'}

    def save(self, event, identity, request):
        pairs = {detection_id(event['id'], i): (i, d) for i, d in enumerate(event['detections'])}
        if identity not in pairs:
            raise KeyError(identity)
        index, original = pairs[identity]
        content = request.model_dump(exclude={'request_id', 'expected_version'})
        if request.status == 'corrected' and request.corrected_label == original['class_name']:
            raise ValueError('Para conservar la etiqueta original utiliza Confirmada')
        with self.db.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            previous = db.execute('SELECT payload FROM detection_reviews WHERE request_id=?', (request.request_id,)).fetchone()
            if previous:
                old = json.loads(previous[0])
                if old['event_id'] != event['id'] or old['detection_id'] != identity or any(old[k] != v for k, v in content.items()):
                    raise ValueError('Idempotencia: identificador reutilizado con otra revisión')
                return old
            previous = db.execute('SELECT payload FROM detection_reviews WHERE event_id=? AND detection_id=? ORDER BY version DESC LIMIT 1',
                                  (event['id'], identity)).fetchone()
            old = json.loads(previous[0]) if previous else None
            version = old['version'] if old else 0
            if version != request.expected_version:
                raise ValueError('La detección ya fue revisada: actualizar antes de guardar')
            record = {'id': uid('review'), 'event_id': event['id'], 'detection_id': identity,
                      'detection_index': index, 'original_label': original['class_name'],
                      'original_detection_sha256': hashlib.sha256(json_text(original).encode()).hexdigest(),
                      'timestamp': utc_now(), 'version': version+1, 'previous_review_id': old['id'] if old else None,
                      'request_id': request.request_id, **content}
            db.execute('INSERT INTO detection_reviews VALUES(?,?,?,?,?,?)',
                       (record['id'], event['id'], identity, version+1, request.request_id, json_text(record)))
        return record


def validated_event(event, view):
    """Proyección derivada; no se escribe sobre el evento ni la imagen de entrada."""
    result = deepcopy(event)
    result['detections'] = []
    for detection in view['validated']:
        item = deepcopy(detection['original'])
        review = detection['review']
        label = review['corrected_label'] or item['class_name']
        item['review_label'] = 'Revisión humana: '+label
        result['detections'].append(item)
    return result
