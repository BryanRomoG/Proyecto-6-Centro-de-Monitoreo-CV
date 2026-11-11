"""Registro persistente de medios locales bajo raíces permitidas por configuración."""
from pathlib import Path
from typing import Literal
import hashlib
import sqlite3

from pydantic import BaseModel, ConfigDict, Field

from .camera import ImageSource, VideoSource, decode
from .config import Settings
from .events import uid, utc_now


class SourceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    name: str = Field(min_length=1, max_length=100)
    kind: Literal["images", "video"]
    path: str = Field(min_length=1, max_length=500)
    sample_hz: float = Field(default=2, gt=0, le=60)
    loop: bool = False
    collection: str | None = Field(default=None,max_length=100)
    dataset_manifest: str | None = None


def allowed_path(settings: Settings, value: str) -> Path:
    path = settings.path(value)
    roots = [settings.path(root) for root in settings.media_roots]
    if not any(path.is_relative_to(root) for root in roots):
        raise ValueError("Ruta fuera de los directorios de medios permitidos")
    # resolve también impide escapar por enlaces simbólicos/junctions.
    if not path.exists():
        raise ValueError("La ruta no existe")
    return path


def settings_for(settings: Settings, source: dict) -> Settings:
    path = allowed_path(settings, source["path"])
    values = settings.model_dump()
    values["source"].update(kind=source["kind"], source_id=source["id"],
                             sample_hz=source["sample_hz"], loop=source["loop"],
                             collection=source.get("collection"),dataset_manifest=source.get("dataset_manifest"))
    values["source"]["images_dir" if source["kind"] == "images" else "video_file"] = str(path)
    return Settings.model_validate(values)


class SourceRegistry:
    def __init__(self, settings: Settings, database):
        self.settings, self.db = settings, database

    def register(self, request: SourceRequest) -> dict:
        path = allowed_path(self.settings, request.path)
        if request.dataset_manifest:
            allowed_path(self.settings,request.dataset_manifest)
        for old in self.db.list("sources"):
            if self.settings.path(old["path"]) == path and old["kind"] == request.kind:
                raise ValueError("Esta fuente ya está registrada; usar su identificador")
        record = {**request.model_dump(), "id": uid("source"), "created_at": utc_now()}
        config = settings_for(self.settings, record)
        source = ImageSource(config) if request.kind == "images" else VideoSource(config)
        try:
            if request.kind == "images":
                # No ocultar errores futuros: una secuencia puede contener archivos corruptos.
                record["total_frames"] = len(source.paths)
                members = []
                invalid = []
                for member in source.paths:
                    resolved = member.resolve()
                    allowed_path(self.settings, str(resolved))
                    with resolved.open("rb") as handle:
                        members.append({"name": member.name, "sha256": hashlib.file_digest(handle,"sha256").hexdigest()})
                    try:
                        decode(resolved.read_bytes())
                    except (ValueError,OSError):
                        invalid.append(member.name)
                if len(invalid) == len(members):
                    raise ValueError("La carpeta no contiene ninguna imagen decodificable")
                record["manifest"] = members
                record["invalid_images"] = invalid
            else:
                record.update(total_frames=source.total, fps=source.fps, duration_seconds=source.total/source.fps)
                with path.open("rb") as handle:
                    record["sha256"] = hashlib.file_digest(handle, "sha256").hexdigest()
        finally:
            source.close()
        # Normalizar a ruta relativa si está dentro del proyecto; nunca publicar otras rutas.
        from .config import ROOT
        record["path"] = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        try:
            self.db.insert_record("sources", record)
        except sqlite3.IntegrityError as exc:
            raise ValueError("La fuente ya fue registrada por otra operación") from exc
        return record

    def validate(self, identity: str) -> tuple[dict, Settings]:
        record = self.db.get("sources", identity)
        if record is None:
            raise KeyError(identity)
        config = settings_for(self.settings, record)
        if record["kind"] == "images":
            # Revalidar hijos en cada arranque; un enlace agregado después no debe escapar.
            for path in config.path(config.source.images_dir).iterdir():
                if path.is_file():
                    allowed_path(self.settings, str(path.resolve()))
        return record, config


def sync_collections(settings,db,manifest_path=None):
    """Solo registra colecciones verificadas del manifiesto local; nunca descarga en el servidor."""
    import json
    from .config import ROOT
    from .datasets import CATEGORIES
    path=manifest_path or ROOT/'data/media/datasets/manifest.json'
    if not path.is_file():return {'registered':[],'existing':[],'errors':[]}
    allowed_path(settings,str(path))
    manifest=json.loads(path.read_text(encoding='utf-8'))
    registry=SourceRegistry(settings,db);result={'registered':[],'existing':[],'errors':[]}
    for category in CATEGORIES:
        rows=[r for r in manifest['images'] if r['category']==category]
        if not rows:continue
        folder=(ROOT/rows[0]['path']).parent.resolve()
        try:
            allowed_path(settings,str(folder))
            expected={r['image_id']+'.jpg':r['sha256'] for r in rows}
            actual={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.suffix.lower() in {'.jpg','.jpeg','.png','.webp'} and p.is_file()}
            if expected!=actual:raise ValueError('La colección difiere de los archivos/SHAs del manifiesto')
            old=next((s for s in db.list('sources') if settings.path(s['path'])==folder),None)
            if old:
                result['existing'].append(old['id']);continue
            record=registry.register(SourceRequest(name=CATEGORIES[category][0],kind='images',path=str(folder),
                          sample_hz=2,collection=category,dataset_manifest=str(path)))
            result['registered'].append(record['id'])
        except (ValueError,OSError) as exc:result['errors'].append({'collection':category,'error':str(exc)})
    return result
