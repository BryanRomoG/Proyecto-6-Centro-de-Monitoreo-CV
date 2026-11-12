"""Portal y API comparten consultas; controles y cambios de alerta son persistentes."""
from contextlib import asynccontextmanager
from io import BytesIO
import json
import re
from typing import Literal
from urllib.parse import urlencode
import zipfile

from fastapi import Body, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .analytics import extras, history
from .config import ROOT, Settings, load_settings
from .events import utc_now
from .exporting import csv_text
from .images import annotate, image_path, thumbnail
from .gallery import Gallery
from .query import Filters, filter_records, search
from .presentation import spanish
from .service import MonitorService
from .sources import SourceRegistry, SourceRequest, sync_collections
from .reviews import Reviews, ReviewRequest, validated_event


class StartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    source_id: str | None = None
    sample_hz: float | None = Field(default=None, gt=0, le=60)
    loop: bool | None = None


class ChangeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal["acknowledge", "resolve", "comment"]
    comment: str = Field(default="", max_length=2000)
    request_id: str = Field(min_length=8, max_length=100)
    expected_version: int = Field(ge=0)
    reason_code: Literal['false_positive', 'validated', 'reviewed_unchanged', 'technical_verified'] | None = None
    review_ids: list[str] = Field(default_factory=list, max_length=100)
    actor: str = Field(default='revisor-local', min_length=1, max_length=100)


class Selection(BaseModel):
    ids: list[str] = Field(min_length=1, max_length=100)


def create_app(settings: Settings | None = None, *, service: MonitorService | None = None):
    auto_collections=settings is None and service is None
    settings = settings or load_settings()
    service = service or MonitorService(settings)
    db = service.db
    registry = SourceRegistry(settings, db)
    gallery_store=Gallery(db,settings.data_dir)
    reviews=Reviews(db)
    if auto_collections:sync_collections(settings,db)
    templates = Jinja2Templates(directory=ROOT/"web/templates")
    templates.env.filters["es"] = spanish
    templates.env.globals['academic']=json.loads((ROOT/'config/academic.json').read_text(encoding='utf-8'))

    @asynccontextmanager
    async def lifespan(app):
        if settings.server.autostart:
            service.start()
        try:
            yield
        finally:
            service.stop()

    app = FastAPI(title="Centro de monitoreo CV · Imágenes y video", version="0.4.0", lifespan=lifespan)
    app.state.service = service
    app.mount("/static", StaticFiles(directory=ROOT/"web/static"), name="static")

    def require(table, identity):
        result = db.get(table,identity)
        if result is None:
            raise HTTPException(404,"Registro no encontrado")
        return result

    def filters(request):
        # No aceptar silenciosamente claves mal escritas: errores visibles al usuario.
        values = {k:v for k,v in request.query_params.items() if v != "" and k not in {"format","interval_seconds","kind"}}
        try:
            return Filters.model_validate(values)
        except (ValidationError,ValueError) as exc:
            raise HTTPException(422,str(exc)) from exc

    def scoped_alerts(selected, events):
        af = Filters(run_id=selected.run_id,start=selected.start,end=selected.end,
                     rule=selected.rule,severity=selected.severity,event_id=selected.event_id)
        alerts = search(db,"alerts",af,paginate=False)["items"]
        if any([selected.class_name,selected.zone,selected.source,selected.collection,selected.status,selected.q,
                selected.min_score is not None,selected.max_score is not None]):
            ids = {e["id"] for e in events}
            alerts = [a for a in alerts if ids.intersection(a["event_ids"])]
        return alerts

    def render(request,title,view,**context):
        export_query=urlencode({key:value for key,value in request.query_params.items()
                                if key not in {'format','limit','offset','page','interval_seconds','kind'}})
        return templates.TemplateResponse(request=request,name="portal.html",
            context={"title":title,"view":view,"export_query":export_query,**context})

    @app.get("/",response_class=HTMLResponse)
    def home(request:Request):
        return render(request,"Dashboard","dashboard")

    def page(view,title):
        def route(request:Request):
            return render(request,title,view)
        app.add_api_route("/"+view,route,response_class=HTMLResponse,include_in_schema=False)
    for view,title in [("playback","Reproducción procesada"),("history","Métricas e históricos"),
                       ("gallery","Galería de capturas"),("sources","Administración de fuentes"),
                       ("runs","Historial de ejecuciones"),("configuration","Configuración efectiva")]:
        page(view,title)

    @app.get("/events",response_class=HTMLResponse)
    def events(request:Request):
        result = search(db,"events",filters(request))
        return render(request,"Eventos","events",items=result["items"],total=result["total"])

    @app.get("/events/{identity}",response_class=HTMLResponse)
    def event_page(request:Request,identity:str):
        from .gallery import STATES
        item=require('events',identity)
        image_state=gallery_store.classify(item['status'],item.get('image_ref'),item.get('image_sha256'))[0]
        return render(request,"Detalle del evento","event",item=item,image_state=image_state,image_reason=STATES[image_state])

    @app.get('/events/{identity}/review',response_class=HTMLResponse)
    def review_page(request:Request,identity:str):
        item=require('events',identity)
        return render(request,'Revisión humana de detecciones','review',item=item)

    @app.get('/api/events/{identity}/reviews')
    def review_view(identity:str):
        item=require('events',identity)
        state,_,reason=gallery_store.classify(item['status'],item.get('image_ref'),item.get('image_sha256'))
        result=reviews.view(item)
        result.update(original=item,image_state=state,image_reason=reason,alerts=db.alert_links([identity]).get(identity,[]))
        return result

    @app.post('/api/events/{identity}/detections/{detection}/reviews')
    def review_detection(identity:str,detection:str,body:ReviewRequest):
        item=require('events',identity)
        state=gallery_store.classify(item['status'],item.get('image_ref'),item.get('image_sha256'))[0]
        if state!='available':raise HTTPException(409,'Captura no disponible o no íntegra: no es posible validar visualmente')
        try:
            result=reviews.save(item,detection,body)
            return {'review':result,'view':reviews.view(item)}
        except KeyError as exc:raise HTTPException(404,'Detección no encontrada') from exc
        except ValueError as exc:raise HTTPException(409,str(exc)) from exc

    @app.get('/images/{identity}/reviewed')
    def reviewed_image(identity:str):
        item=require('events',identity)
        state=gallery_store.classify(item['status'],item.get('image_ref'),item.get('image_sha256'))[0]
        if state!='available':raise HTTPException(404,'Captura no disponible o no íntegra')
        view=reviews.view(item)
        return Response(annotate(image_path(settings.data_dir,item),validated_event(item,view)),media_type='image/png',
                        headers={'X-Event-ID':identity,'X-Image-Layer':'human-review','Cache-Control':'no-store'})

    @app.get("/alerts",response_class=HTMLResponse)
    def alerts(request:Request):
        result = search(db,"alerts",filters(request))
        return render(request,"Alertas","alerts",items=result["items"],total=result["total"])

    @app.get("/alerts/{identity}",response_class=HTMLResponse)
    def alert_page(request:Request,identity:str):
        return render(request,"Detalle de alerta","alert",item=require("alerts",identity))

    @app.get("/images/{identity}")
    def image(identity:str, download:bool=False):
        try:
            path = image_path(settings.data_dir,require("events",identity))
        except FileNotFoundError as exc:
            raise HTTPException(404,str(exc)) from exc
        return FileResponse(path,media_type="image/png",filename=f"{identity}.png" if download else None)

    @app.get("/images/{identity}/annotated")
    def annotated(identity:str):
        event = require("events",identity)
        try:
            data = annotate(image_path(settings.data_dir,event),event)
        except (FileNotFoundError,OSError) as exc:
            raise HTTPException(404,"No se pudo cargar la captura") from exc
        return Response(data,media_type="image/png",headers={"X-Event-ID":identity})

    @app.get('/images/{identity}/thumbnail')
    def image_thumbnail(request:Request,identity:str,annotated:bool=False):
        try:path,etag=thumbnail(settings.data_dir,require('events',identity),annotated=annotated)
        except (FileNotFoundError,OSError,ValueError) as exc:raise HTTPException(404,'Miniatura no disponible') from exc
        headers={'ETag':'"'+etag+'"','Cache-Control':'private, max-age=86400','X-Event-ID':identity}
        if request.headers.get('if-none-match')==headers['ETag']:return Response(status_code=304,headers=headers)
        return FileResponse(path,media_type='image/jpeg',headers=headers)

    @app.post("/api/gallery/download")
    def download_selected(selection:Selection):
        paths = []
        credits=[]
        for identity in dict.fromkeys(selection.ids):
            if not re.fullmatch(r"[A-Za-z0-9_-]+",identity):
                raise HTTPException(422,"Identificador inválido")
            try:
                event=require('events',identity)
                paths.append((identity,image_path(settings.data_dir,event)))
                if event.get('input_image'):credits.append({'file':identity+'.png',**event['input_image'],
                    'changes':'Captura PNG decodificada del JPEG oficial CVDF. No se incluye anotación en este ZIP.'})
            except FileNotFoundError as exc:
                raise HTTPException(404,str(exc)) from exc
        if sum(p.stat().st_size for _,p in paths)>50*1024*1024:
            raise HTTPException(413,"La selección supera 50 MiB")
        output = BytesIO()
        with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED) as archive:
            for identity,path in paths:
                archive.write(path,f"{identity}.png")
            if credits:archive.writestr('ATTRIBUTION.json',json.dumps(credits,ensure_ascii=False,indent=2))
        return Response(output.getvalue(),media_type="application/zip",headers={"Content-Disposition":"attachment; filename=capturas.zip"})

    @app.get("/api/status")
    def status():
        return service.status()

    @app.get("/api/playback/current")
    def current():
        return service.current()

    @app.post("/api/monitor/start",status_code=202)
    def start(body:StartRequest|None=Body(default=None)):
        chosen = settings
        try:
            if body and body.source_id:
                _,chosen = registry.validate(body.source_id)
            if body and (body.sample_hz is not None or body.loop is not None):
                data = chosen.model_dump()
                if body.sample_hz is not None:
                    data["source"]["sample_hz"] = body.sample_hz
                if body.loop is not None:
                    data["source"]["loop"] = body.loop
                chosen = Settings.model_validate(data)
            if chosen.source.kind == "mjpeg":
                raise ValueError("El portal actual solo inicia imágenes o video local")
            return {"run_id":service.start(settings=chosen)}
        except KeyError as exc:
            raise HTTPException(404,"Fuente no encontrada") from exc
        except Exception as exc:
            raise HTTPException(409,str(exc)) from exc

    @app.post("/api/monitor/stop")
    def stop():
        return service.stop()

    @app.post("/api/monitor/pause")
    def pause():
        try:
            return service.pause()
        except ValueError as exc:
            raise HTTPException(409,str(exc)) from exc

    @app.post("/api/monitor/resume")
    def resume():
        try:
            return service.resume()
        except ValueError as exc:
            raise HTTPException(409,str(exc)) from exc

    @app.get("/api/sources")
    def sources():
        return db.list("sources")

    @app.post("/api/sources",status_code=201)
    def add_source(body:SourceRequest):
        try:
            return registry.register(body)
        except (ValueError,OSError) as exc:
            raise HTTPException(422,str(exc)) from exc

    @app.get("/api/sources/{identity}")
    def source(identity:str):
        return require("sources",identity)

    @app.get("/api/events")
    def api_events(request:Request):
        return search(db,"events",filters(request))["items"]

    @app.get("/api/alerts")
    def api_alerts(request:Request):
        return search(db,"alerts",filters(request))["items"]

    @app.get("/api/query/{kind}")
    def query(kind:Literal["events","alerts"],request:Request):
        return search(db,kind,filters(request))

    @app.get("/api/events/{identity}")
    def api_event(identity:str):
        return require("events",identity)

    @app.get("/api/alerts/{identity}")
    def api_alert(identity:str):
        return require("alerts",identity)

    @app.post("/api/alerts/{identity}/changes")
    def change(identity:str,body:ChangeRequest):
        try:
            result = db.transition_alert(identity,**body.model_dump())
            return {"change":result,"alert":db.get("alerts",identity)}
        except KeyError as exc:
            raise HTTPException(404,"Alerta no encontrada") from exc
        except ValueError as exc:
            raise HTTPException(409,str(exc)) from exc

    @app.get("/api/runs")
    def runs(request:Request):
        return search(db,"runs",filters(request))["items"]

    @app.get("/api/runs/{identity}")
    def run(identity:str):
        return require("runs",identity)

    @app.get("/api/runs/{identity}/actions")
    def actions(identity:str):
        require("runs",identity)
        return db.list("actions",identity)

    @app.get("/api/windows")
    def windows(run_id:str):
        return db.list("windows",run_id)

    @app.get("/api/metrics")
    def metrics(run_id:str|None=None):
        return service.metrics(run_id)

    @app.get("/api/configuration")
    def configuration():
        return {"settings":service.settings.model_dump(),"config_sha256":service.settings.fingerprint,
                "allowed_media_roots":settings.media_roots,"author":"Entrega individual; identificación académica en el portal"}

    @app.get("/api/gallery")
    def gallery(request:Request,response:Response):
        response.headers['Cache-Control']='no-store'
        return gallery_store.page(filters(request))

    @app.get('/api/gallery/issues')
    def gallery_issues(request:Request,response:Response):
        response.headers['Cache-Control']='no-store'
        return gallery_store.issues(filters(request))

    @app.get("/api/history")
    def historical(request:Request,interval_seconds:int=Query(default=10,ge=1,le=86400)):
        selected = filters(request)
        events = search(db,"events",selected,paginate=False)["items"]
        alerts = scoped_alerts(selected,events)
        result = history(events,alerts,db.list("windows",selected.run_id),interval_seconds)
        selected_windows = db.list("windows",selected.run_id)
        result["extras"] = extras(events,alerts,settings.data_dir,cutoff=utc_now(),windows=selected_windows)
        result["extras_by_run"] = {run:extras([e for e in events if e["run_id"]==run],
                    [a for a in alerts if a["run_id"]==run],settings.data_dir,cutoff=result["extras"]["cutoff"],windows=selected_windows)
                    for run in sorted({e["run_id"] for e in events})}
        return result

    @app.get("/api/dashboard")
    def dashboard(run_id:str|None=None):
        if run_id is None:
            latest = db.list("runs",limit=1)
            run_id = service.run_id or (latest[0]["id"] if latest else None)
        run = db.get("runs",run_id) if run_id else None
        events = db.list("events",run_id) if run_id else []
        alerts = db.list("alerts",run_id) if run_id else []
        successful = [e for e in events if e["status"] in {"ok","no_detections"}]
        extra = extras(events,alerts,settings.data_dir,cutoff=utc_now(),windows=db.list("windows",run_id) if run_id else [])
        latest = events[0] if events else None
        return {"run":run,"status":service.status(),"events":len(events),"successful":len(successful),
                "errors":len(events)-len(successful),"detections":sum(len(e["detections"]) for e in events),
                "last_activity":latest["timestamp"] if latest else None,
                "confidence_state":latest.get("confidence_state") if latest else "insufficient_evidence",
                "metrics":service.metrics(run_id),"extras":extra,
                "last_snapshot":(db.list("metrics",run_id,limit=1) or [None])[0] if run_id else None}

    @app.get("/api/export/{kind}")
    def export(kind:Literal["events","alerts","metrics","confidence","runs","extras"],request:Request,
               format:Literal["json","csv"]="json"):
        selected = filters(request)
        if kind == "extras":
            events = search(db,"events",selected,paginate=False)["items"]
            alerts = scoped_alerts(selected,events)
            result = extras(events,alerts,settings.data_dir,cutoff=utc_now(),windows=db.list("windows",selected.run_id))
            rows = [{"id":identity,"timestamp":result["cutoff"],"value":value,
                     "unit":result["catalog"][identity]["unit"],"event_ids":result["event_ids"],
                     "alert_ids":result["alert_ids"],"run_configs":result["run_configs"]}
                    for identity,value in result["values"].items()]
        elif kind in {"events","alerts","runs"}:
            rows = search(db,kind,selected,paginate=False)["items"]
        else:
            # Métricas/ventanas están asociadas a conjuntos de eventos, no a una clase individual.
            if any([selected.class_name,selected.zone,selected.source,selected.collection,selected.min_score is not None,
                    selected.max_score is not None,selected.rule,selected.severity,selected.event_id,selected.status]):
                raise HTTPException(422,"Métricas y confianza admiten filtros de ID, ejecución y fechas; no filtrar parcialmente un agregado")
            rows = filter_records(db.list("metrics" if kind=="metrics" else "windows",selected.run_id),selected,kind)
        body = json.dumps(rows,ensure_ascii=False,allow_nan=False) if format=="json" else csv_text(kind,rows)
        return Response(body,media_type="application/json" if format=="json" else "text/csv; charset=utf-8",
                        headers={"Content-Disposition":f"attachment; filename={kind}.{format}"})

    return app
