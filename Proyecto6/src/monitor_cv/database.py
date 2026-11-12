"""SQLite con transacciones, claves foráneas y conexiones cortas por operación."""
from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3

from .events import json_text


class Database:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS events(
                    id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id),
                    timestamp TEXT NOT NULL, status TEXT NOT NULL, payload TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS event_run ON events(run_id, timestamp);
                CREATE INDEX IF NOT EXISTS event_source ON events(json_extract(payload,'$.source_id'),timestamp);
                CREATE INDEX IF NOT EXISTS event_collection ON events(json_extract(payload,'$.collection'),timestamp);
                CREATE TABLE IF NOT EXISTS image_assets(
                    event_id TEXT PRIMARY KEY REFERENCES events(id),state TEXT NOT NULL,
                    signature TEXT,diagnostic TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS image_state ON image_assets(state,event_id);
                CREATE TABLE IF NOT EXISTS alerts(
                    id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id),
                    event_id TEXT NOT NULL REFERENCES events(id), timestamp TEXT NOT NULL,
                    status TEXT NOT NULL, payload TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS alert_run ON alerts(run_id, timestamp);
                CREATE TABLE IF NOT EXISTS windows(
                    id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS metrics(
                    id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
                CREATE UNIQUE INDEX IF NOT EXISTS source_path ON sources(json_extract(payload,'$.kind'),json_extract(payload,'$.path'));
                CREATE TABLE IF NOT EXISTS actions(id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS alert_changes(
                    id TEXT PRIMARY KEY, alert_id TEXT NOT NULL REFERENCES alerts(id),
                    version INTEGER NOT NULL, request_id TEXT UNIQUE NOT NULL, payload TEXT NOT NULL,
                    UNIQUE(alert_id,version));
                PRAGMA user_version=3;
            """)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.execute("PRAGMA foreign_keys=ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    def save_run(self, run: dict):
        with self.connect() as db:
            db.execute("INSERT INTO runs VALUES(?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload",
                       (run["id"], json_text(run)))

    def save_observation(self, event: dict, alerts: list[dict], window: dict | None):
        with self.connect() as db:
            db.execute("INSERT INTO events VALUES(?,?,?,?,?)",
                       (event["id"], event["run_id"], event["timestamp"], event["status"], json_text(event)))
            if window:
                db.execute("INSERT INTO windows VALUES(?,?,?)", (window["id"], event["run_id"], json_text(window)))
            for a in alerts:
                db.execute("INSERT INTO alerts VALUES(?,?,?,?,?,?)",
                           (a["id"], a["run_id"], a["event_id"], a["timestamp"], a["status"], json_text(a)))

    def save_metrics(self, metrics: dict):
        with self.connect() as db:
            db.execute("INSERT INTO metrics VALUES(?,?,?)",
                       (metrics["id"], metrics["run_id"], json_text(metrics)))

    def get(self, table: str, identity: str) -> dict | None:
        self._table(table)
        with self.connect() as db:
            row = db.execute(f"SELECT payload FROM {table} WHERE id=?", (identity,)).fetchone()
        result = json.loads(row[0]) if row else None
        return self.enrich_alert(result) if result and table == "alerts" else result

    def list(self, table: str, run_id: str | None = None, *, limit: int | None = None,
             offset: int = 0) -> list[dict]:
        self._table(table)
        where, args = (" WHERE run_id=?", [run_id]) if run_id and table != "runs" else ("", [])
        query = f"SELECT payload FROM {table}{where} ORDER BY rowid DESC"
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            args.extend([limit, offset])
        with self.connect() as db:
            result = [json.loads(row[0]) for row in db.execute(query, args)]
        return self.enrich_alerts(result) if table == "alerts" else result

    def insert_record(self, table: str, record: dict):
        if table not in {"sources", "actions"}:
            raise ValueError("Registro no permitido")
        with self.connect() as db:
            if table == "sources":
                db.execute("INSERT INTO sources VALUES(?,?)", (record["id"], json_text(record)))
            else:
                db.execute("INSERT INTO actions VALUES(?,?,?)", (record["id"], record["run_id"], json_text(record)))

    @staticmethod
    def event_predicate(filters):
        clauses=[];args=[]
        for key,column in [('run_id','e.run_id'),('source',"json_extract(e.payload,'$.source_id')"),
                           ('collection',"json_extract(e.payload,'$.collection')"),('status','e.status')]:
            if (value:=getattr(filters,key)) is not None:clauses.append(column+'=?');args.append(value)
        if filters.q:clauses.append('instr(lower(e.id),?)>0');args.append(filters.q.casefold())
        for key,op in [('start','>='),('end','<=')]:
            if value:=getattr(filters,key):clauses.append(f'julianday(e.timestamp){op}julianday(?)');args.append(value)
        detection=[]
        for key,field,op in [('class_name','class_name','='),('zone','zone','='),('min_score','confidence','>='),('max_score','confidence','<=')]:
            if (value:=getattr(filters,key)) is not None:
                detection.append(f"json_extract(d.value,'$.{field}'){op}?");args.append(value)
        if detection:clauses.append("EXISTS(SELECT 1 FROM json_each(e.payload,'$.detections') d WHERE "+' AND '.join(detection)+')')
        return clauses,args

    def search_events(self,filters,*,paginate=True,available=False,slim=False,states=False):
        clauses,args=self.event_predicate(filters)
        joins=' LEFT JOIN image_assets i ON i.event_id=e.id' if available or states else ''
        base=' FROM events e'+joins
        where=(' WHERE '+' AND '.join(clauses)) if clauses else ''
        with self.connect() as db:
            db.execute('BEGIN')  # Conteos y página pertenecen a la misma vista durante un productor concurrente.
            counts=dict(db.execute("SELECT COALESCE(i.state,'unchecked'),count(*)"+base+where+" GROUP BY i.state",args)) if states else {}
            if available:clauses.append("i.state='available'")
            where=(' WHERE '+' AND '.join(clauses)) if clauses else ''
            total=db.execute('SELECT count(*)'+base+where,args).fetchone()[0]
            sort={'timestamp':'e.timestamp','id':'e.id','detection_count':"json_array_length(e.payload,'$.detections')",
                  'confidence':"COALESCE((SELECT max(json_extract(value,'$.confidence')) FROM json_each(e.payload,'$.detections')),-1)",
                  'severity':"COALESCE(json_extract(e.payload,'$.severity'),'')"}[filters.sort]
            order='DESC' if filters.order=='desc' else 'ASC'
            fields=['id','run_id','timestamp','source_id','source_kind','collection','input_name','input_image','status','detections','image_ref','image_sha256']
            projection='json_object('+','.join(f"'{key}',json_extract(e.payload,'$.{key}')" for key in fields)+')' if slim else 'e.payload'
            query='SELECT '+projection+base+where+f' ORDER BY {sort} {order}, e.id {order}'
            if paginate:query+=' LIMIT ? OFFSET ?';args=[*args,filters.limit,filters.offset]
            rows=[json.loads(row[0]) for row in db.execute(query,args)]
        return {'items':rows,'total':total,'offset':filters.offset,'limit':filters.limit,'image_states':counts}

    def alert_links(self,identities):
        if not identities:return {}
        placeholders=','.join('?' for _ in identities)
        with self.connect() as db:
            rows=db.execute("SELECT a.id,j.value FROM alerts a JOIN json_each(a.payload,'$.event_ids') j WHERE j.value IN ("+placeholders+')',identities).fetchall()
        result={identity:[] for identity in identities}
        for alert,event in rows:result[event].append(alert)
        return result

    def enrich_alert(self, alert: dict) -> dict:
        with self.connect() as db:
            changes = [json.loads(row[0]) for row in db.execute(
                "SELECT payload FROM alert_changes WHERE alert_id=? ORDER BY version", (alert["id"],))]
        return self.alert_projection(alert,changes)

    def enrich_alerts(self, alerts):
        """Una consulta de historial por lote; evita abrir una conexión por alerta."""
        if not alerts:return []
        groups={a['id']:[] for a in alerts}
        with self.connect() as db:
            rows=db.execute('SELECT alert_id,payload FROM alert_changes WHERE alert_id IN (SELECT value FROM json_each(?)) ORDER BY version',
                            (json.dumps(list(groups)),)).fetchall()
        for identity,payload in rows:groups[identity].append(json.loads(payload))
        return [self.alert_projection(a,groups[a['id']]) for a in alerts]

    @staticmethod
    def alert_projection(alert, changes):
        result = dict(alert)
        result.update(version=0, history=[], acknowledged_at=None, resolved_at=None)
        for change in changes:
            result["status"] = change["to_state"]
            result["version"] = change["version"]
            if change["action"] == "acknowledge":
                result["acknowledged_at"] = change["timestamp"]
            if change["action"] == "resolve":
                result["resolved_at"] = change["timestamp"]
        result["history"] = changes
        return result

    def transition_alert(self, identity: str, *, action: str, comment: str,
                         request_id: str, expected_version: int, reason_code: str | None = None,
                         review_ids: list[str] | None = None, actor: str = 'revisor-local') -> dict:
        from .events import uid, utc_now
        review_ids=list(dict.fromkeys(review_ids or []))
        reasons={'false_positive','validated','reviewed_unchanged','technical_verified'}
        if reason_code is not None and reason_code not in reasons:raise ValueError('Motivo de revisión inválido')
        if not actor.strip():raise ValueError('Actor vacío')
        if review_ids and not reason_code:raise ValueError('Los vínculos de revisión requieren un motivo')
        if reason_code and not comment.strip():raise ValueError('Explica la decisión de revisión')
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute("SELECT payload FROM alert_changes WHERE request_id=?", (request_id,)).fetchone()
            if existing:
                old = json.loads(existing[0])
                if (old["alert_id"] != identity or old["action"] != action or old["comment"] != comment
                    or old.get('reason_code')!=reason_code or old.get('review_ids',[])!=review_ids
                    or old.get('actor','revisor-local')!=actor):
                    raise ValueError("Idempotencia: identificador reutilizado con otra acción")
                return old
            row = db.execute("SELECT payload FROM alerts WHERE id=?", (identity,)).fetchone()
            if not row:
                raise KeyError(identity)
            original = json.loads(row[0])
            linked_reviews=[]
            for review_id in review_ids:
                row=db.execute('SELECT payload FROM detection_reviews WHERE id=?',(review_id,)).fetchone()
                review=json.loads(row[0]) if row else None
                if not review or review['event_id'] not in original['event_ids']:
                    raise ValueError('La revisión no corresponde a un evento de esta alerta')
                linked_reviews.append(review)
            if reason_code in {'false_positive','validated'} and not review_ids:
                raise ValueError('Este motivo requiere revisiones de detecciones vinculadas')
            if reason_code=='false_positive' and not any(r['status']=='false_positive' for r in linked_reviews):
                raise ValueError('Vincula la revisión que confirmó el falso positivo')
            if reason_code=='validated' and not any(r['status'] in {'confirmed','corrected'} for r in linked_reviews):
                raise ValueError('Vincula una detección validada')
            previous = db.execute("SELECT payload FROM alert_changes WHERE alert_id=? ORDER BY version DESC LIMIT 1", (identity,)).fetchone()
            last = json.loads(previous[0]) if previous else None
            state, version = (last["to_state"], last["version"]) if last else (original["status"], 0)
            if version != expected_version:
                raise ValueError("La alerta cambió: actualizar antes de actuar")
            target = {("active", "acknowledge"): "acknowledged",
                      ("acknowledged", "resolve"): "resolved"}.get((state, action))
            if action == "comment":
                if not comment.strip():
                    raise ValueError("El comentario no puede estar vacío")
                target = state
            if target is None:
                raise ValueError("Transición de alerta no permitida")
            change = {"id": uid("change"), "alert_id": identity, "timestamp": utc_now(),
                      "action": action, "from_state": state, "to_state": target,
                      "comment": comment, "version": version+1, "request_id": request_id,
                      'reason_code':reason_code,'review_ids':review_ids,'actor':actor}
            db.execute("INSERT INTO alert_changes VALUES(?,?,?,?,?)",
                       (change["id"], identity, change["version"], request_id, json_text(change)))
        return change

    @staticmethod
    def _table(table):
        if table not in {"runs", "events", "alerts", "windows", "metrics", "sources", "actions"}:
            raise ValueError("Tabla no permitida")
