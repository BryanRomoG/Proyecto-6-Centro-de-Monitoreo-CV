"""Referencias seguras y anotación derivada de un evento inmutable."""
from io import BytesIO
from pathlib import Path
import hashlib,json,threading

from PIL import Image, ImageDraw, ImageFont

COLORS = {"low": "#c5283d", "doubt": "#a56300", "accepted": "#067443"}
THUMBNAIL_LOCK=threading.Lock()


def image_path(data_dir: Path, event: dict) -> Path:
    if not event.get("image_ref"):
        raise FileNotFoundError("Evento sin captura")
    path = (data_dir / event["image_ref"]).resolve()
    if not path.is_relative_to(data_dir.resolve()) or not path.is_file():
        raise FileNotFoundError("Captura ausente o ruta no permitida")
    return path


def render(path: Path, event: dict, *, limit=None, annotated=True, output_format='PNG') -> bytes:
    with Image.open(path) as source:
        image = source.convert("RGB")
    original_width=image.width
    if limit:image.thumbnail(limit,Image.Resampling.LANCZOS)
    scale=image.width/original_width
    draw = ImageDraw.Draw(image)
    size = max(13, round(image.width/60))
    try:
        font = ImageFont.truetype("arial.ttf", size)
    except OSError:
        font = ImageFont.load_default(size=size)
    for d in event["detections"] if annotated else []:
        color = COLORS[d["zone"]]
        box = tuple(v*scale for v in d["bbox"])
        draw.rectangle(box, outline=color, width=max(2, round(image.width/300)))
        label = f"{d['class_name']} {d['confidence']:.3f}"
        x, y = box[0], max(0, box[1]-size-6)
        text_box = draw.textbbox((x,y),label,font=font)
        draw.rectangle(text_box, fill=color)
        draw.text((x,y),label,fill="white",font=font)
    out = BytesIO()
    image.save(out, format=output_format,**({'quality':74,'optimize':True} if output_format=='JPEG' else {}))
    return out.getvalue()


def annotate(path:Path,event:dict)->bytes:
    return render(path,event)


def thumbnail(data_dir:Path,event:dict,*,annotated=False):
    path=image_path(data_dir,event);stat=path.stat()
    identity=hashlib.sha256(json.dumps([event['id'],event.get('image_sha256'),stat.st_mtime_ns,stat.st_size,
        event['detections'],annotated,'thumb-320-v1'],sort_keys=True).encode()).hexdigest()
    cached=data_dir/'thumbnails'/(identity+'.jpg')
    with THUMBNAIL_LOCK:
        if not cached.is_file():
            # No generar un derivado de bytes alterados que se atribuya al hash histórico.
            if hashlib.sha256(path.read_bytes()).hexdigest()!=event['image_sha256']:
                raise FileNotFoundError('La captura difiere del hash histórico')
            data=render(path,event,limit=(320,240),annotated=annotated,output_format='JPEG')
            cached.parent.mkdir(parents=True,exist_ok=True)
            with cached.open('xb') as handle:handle.write(data)
    return cached,identity
