"""Filtros compartidos por tablas, galería, gráficas y exportaciones."""
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Filters(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    q: str | None = Field(default=None, max_length=150)
    start: str | None = None
    end: str | None = None
    source: str | None = None
    collection: str | None = Field(default=None,max_length=100)
    run_id: str | None = None
    class_name: str | None = None
    zone: Literal["low", "doubt", "accepted"] | None = None
    status: Literal["ok","no_detections","source_error","decode_error","inference_error",
                    "active","acknowledged","resolved","running","paused","stopped","completed","error"] | None = None
    min_score: float | None = Field(default=None, ge=0, le=1)
    max_score: float | None = Field(default=None, ge=0, le=1)
    rule: str | None = None
    severity: Literal["warning", "high", "info"] | None = None
    event_id: str | None = None
    sort: Literal["timestamp", "id", "confidence", "detection_count", "severity"] = "timestamp"
    order: Literal["asc", "desc"] = "desc"
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
    page: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def ranges(self):
        for key in ["start", "end"]:
            if value := getattr(self, key):
                stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if stamp.tzinfo is None:
                    stamp = stamp.replace(tzinfo=timezone.utc)
                setattr(self, key, stamp.astimezone(timezone.utc).isoformat())
        if self.start and self.end and self.start > self.end:
            raise ValueError("El inicio debe ser anterior al final")
        if self.min_score is not None and self.max_score is not None and self.min_score > self.max_score:
            raise ValueError("Rango de puntuación invertido")
        if self.page is not None:
            self.offset = (self.page - 1) * self.limit
        return self


def filter_records(rows: list[dict], filters: Filters, kind: str) -> list[dict]:
    """Predicado único: filtros de detección se satisfacen en la MISMA detección."""
    def matches(row):
        if filters.q and filters.q.casefold() not in row["id"].casefold():
            return False
        if filters.run_id and row.get("run_id", row["id"] if kind == "runs" else None) != filters.run_id:
            return False
        stamp = row.get("timestamp", row.get("started_at"))
        if filters.start or filters.end:
            if not stamp:
                return False
            dt = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            if filters.start and dt < datetime.fromisoformat(filters.start):
                return False
            if filters.end and dt > datetime.fromisoformat(filters.end):
                return False
        if filters.source and row.get("source_id", row.get("source", {}).get("source_id")) != filters.source:
            return False
        if filters.collection and row.get('collection',row.get('source',{}).get('collection')) != filters.collection:
            return False
        if filters.status and row.get("status") != filters.status:
            return False
        if kind == "events":
            if any(v is not None for v in [filters.class_name, filters.zone, filters.min_score, filters.max_score]):
                if not any((not filters.class_name or d["class_name"] == filters.class_name)
                           and (not filters.zone or d["zone"] == filters.zone)
                           and (filters.min_score is None or d["confidence"] >= filters.min_score)
                           and (filters.max_score is None or d["confidence"] <= filters.max_score)
                           for d in row.get("detections", [])):
                    return False
        if kind == "alerts":
            if filters.rule and row["rule_id"] != filters.rule:
                return False
            if filters.severity and row["severity"] != filters.severity:
                return False
            if filters.event_id and filters.event_id not in row["event_ids"]:
                return False
        return True
    selected = [row for row in rows if matches(row)]
    def key(row):
        if filters.sort == "confidence":
            value = max((d["confidence"] for d in row.get("detections", [])), default=-1)
        elif filters.sort == "detection_count":
            value = len(row.get("detections", []))
        elif filters.sort == "timestamp":
            value = row.get("timestamp", row.get("started_at", ""))
        else:
            value = row.get(filters.sort, "")
        return value, row["id"]
    return sorted(selected, key=key, reverse=filters.order == "desc")


def search(db, table: str, filters: Filters, *, paginate=True) -> dict:
    if table=='events':return db.search_events(filters,paginate=paginate)
    # Esta primera versión de consultas filtra JSON completos; no implica escalabilidad ilimitada.
    rows = filter_records(db.list(table, filters.run_id), filters, table)
    return {"total": len(rows), "offset": filters.offset, "limit": filters.limit,
            "items": rows[filters.offset:filters.offset+filters.limit] if paginate else rows}
