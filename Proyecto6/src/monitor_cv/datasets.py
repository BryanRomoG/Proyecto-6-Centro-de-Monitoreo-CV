"""Adquisición selectiva de Open Images con licencia por fila e identidad de bytes."""
from __future__ import annotations

from collections import Counter,defaultdict
import csv
from datetime import datetime,timezone
from io import BytesIO
import json
import hashlib
import re
from pathlib import Path
from urllib.parse import urlsplit,unquote

import cv2
import httpx
import numpy as np
from PIL import Image

BASE='https://storage.googleapis.com/openimages/'
METADATA={
    'images':BASE+'2018_04/validation/validation-images-with-rotation.csv',
    'labels':BASE+'v5/validation-annotations-human-imagelabels-boxable.csv',
    'boxes':BASE+'v5/validation-annotations-bbox.csv',
    'classes':BASE+'v7/oidv7-class-descriptions.csv',
}
CATEGORIES={
    'personas':('Personas',{'Person','Man','Woman','Boy','Girl'}),
    'animales':('Perros y gatos',{'Dog','Cat'}),
    'vehiculos':('Automóviles y motocicletas',{'Car','Motorcycle'}),
    'bicicletas':('Bicicletas y transporte',{'Bicycle','Bus','Train','Airplane','Boat'}),
    'objetos':('Objetos domésticos',{'Chair','Table','Coffee cup','Bottle','Book','Mobile phone','Laptop','Clock','Television','Oven','Fork','Spoon','Knife','Sofa bed','Couch','Bed','Refrigerator','Sink','Microwave oven'}),
    'escenas_multiples':('Varias clases anotadas',set()),
    'baja_confianza':('Escenas difíciles: oclusión anotada (no predicción)',set()),
    'escenas_despejadas':('Pocos objetos previstos (no garantiza cero detecciones)',{'Tree','Flower','Plant','Mountain','Sky','Sea','Lake','Waterfall','Snow','Cloud','Rock','Palm tree'}),
}
CC_BY='https://creativecommons.org/licenses/by/2.0/'


def stamp():return datetime.now(timezone.utc).isoformat()
def sha(data):return hashlib.sha256(data).hexdigest()
def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temporary.replace(path)


def permitted_license(value):
    # Lista explícita. No se infiere licencia de una imagen desde la del código/dataset.
    return value.rstrip('/').replace('http://','https://')==CC_BY.rstrip('/')


def public_url(value):
    u=urlsplit(value)
    if u.scheme!='https' or u.username or u.password or u.port not in (None,443):
        raise ValueError('Solo HTTPS público sin credenciales')
    if u.hostname not in {'storage.googleapis.com','open-images-dataset.s3.amazonaws.com'}:
        raise ValueError('Host de descarga fuera de las fuentes oficiales permitidas')
    return value


class Budget:
    def __init__(self,maximum=200_000_000):self.maximum,self.transferred=maximum,0
    def add(self,count):
        if self.transferred+count>self.maximum:raise ValueError('Límite total de descarga alcanzado')
        self.transferred+=count


def fetch(client,url,budget,*,maximum=8_000_000):
    public_url(url)
    with client.stream('GET',url,follow_redirects=False) as response:
        response.raise_for_status()
        declared=int(response.headers.get('content-length',0))
        if declared>maximum or declared>budget.maximum-budget.transferred:
            raise ValueError('Archivo supera presupuesto o límite individual')
        blocks=[];size=0
        for block in response.iter_bytes():
            size+=len(block);budget.add(len(block))
            if size>maximum:raise ValueError('Archivo supera límite individual')
            blocks.append(block)
    return b''.join(blocks)


def inspect_image(data):
    with Image.open(BytesIO(data)) as im:
        image_format=im.format
        if im.format not in {'JPEG','PNG','WEBP'}:raise ValueError('Formato visual no permitido')
        if im.width*im.height>25_000_000:raise ValueError('Imagen demasiado grande')
        im.verify()
    with Image.open(BytesIO(data)) as im:
        rgb=im.convert('RGB');width,height=rgb.size
        gray=np.asarray(rgb.convert('L').resize((32,32),Image.Resampling.LANCZOS),dtype=np.float32)
        dct=cv2.dct(gray)[:8,:8].flatten()
        bits=dct[1:]>np.median(dct[1:])
        phash=f'{sum(int(bit)<<i for i,bit in enumerate(bits)):016x}'
        luminance=float(np.asarray(rgb.convert('L')).mean())
        dh=np.asarray(rgb.convert('L').resize((9,8),Image.Resampling.LANCZOS))
        dbits=(dh[:,1:]>dh[:,:-1]).flatten()
        dhash=f'{sum(int(bit)<<i for i,bit in enumerate(dbits)):016x}'
        gray16=list(rgb.convert('L').resize((16,16),Image.Resampling.LANCZOS).getdata())
    decoded=cv2.imdecode(np.frombuffer(data,np.uint8),cv2.IMREAD_COLOR)
    if decoded is None:raise ValueError('OpenCV no puede decodificar la imagen')
    return {'width':width,'height':height,'bytes':len(data),'sha256':sha(data),'phash':phash,'dhash':dhash,'perceptual_gray16':gray16,
            'mean_luminance_0_255':luminance,'format':image_format}


def hamming(a,b):return (int(a,16)^int(b,16)).bit_count()


def near_duplicate(a,b,threshold=5):
    if hamming(a['phash'],b['phash'])<=threshold:return True
    # pHash se vuelve inestable en gradientes uniformes por coeficientes casi cero.
    # dHash más error fotométrico pequeño cubre recompression sin igualar cielos distintos.
    if 'dhash' not in a or 'dhash' not in b:return False
    rmse=float(np.sqrt(np.mean((np.asarray(a['perceptual_gray16'],float)-np.asarray(b['perceptual_gray16'],float))**2)))
    return hamming(a['dhash'],b['dhash'])<=3 and rmse<=3


def metadata(cache,client,budget):
    result={};provenance={}
    for key,url in METADATA.items():
        path=cache/(key+'.csv');sidecar=cache/(key+'.json')
        cached=False
        if path.is_file() and sidecar.is_file():
            recorded=json.loads(sidecar.read_text(encoding='utf-8'))
            cached=sha(path.read_bytes())==recorded['sha256'] and recorded['url']==url
        if not cached:
            data=fetch(client,url,budget,maximum=40_000_000)
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
            write_json(sidecar,{'url':url,'sha256':sha(data),'bytes':len(data),'downloaded_at':stamp()})
        result[key]=path;provenance[key]=json.loads(sidecar.read_text(encoding='utf-8'))
    return result,provenance


def candidates(files,seed):
    with files['classes'].open(encoding='utf-8',newline='') as handle:names=dict(csv.reader(handle))
    positive=defaultdict(set)
    with files['labels'].open(encoding='utf-8',newline='') as handle:
        for row in csv.DictReader(handle):
            if row['Confidence']=='1':positive[row['ImageID']].add(names.get(row['LabelName'],row['LabelName']))
    boxes=defaultdict(lambda:{'names':set(),'count':0,'occluded':0})
    with files['boxes'].open(encoding='utf-8',newline='') as handle:
        for row in csv.DictReader(handle):
            b=boxes[row['ImageID']];b['names'].add(names.get(row['LabelName'],row['LabelName']))
            b['count']+=1;b['occluded']+=int(row['IsOccluded']=='1')
    images={}
    with files['images'].open(encoding='utf-8',newline='') as handle:
        for row in csv.DictReader(handle):
            if permitted_license(row['License']) and row['OriginalURL'] and row['OriginalLandingURL']:
                images[row['ImageID']]=row
    cocoish=set.union(*(CATEGORIES[k][1] for k in ['personas','animales','vehiculos','bicicletas','objetos']))
    result={}
    for category,(_,wanted) in CATEGORIES.items():
        eligible=[]
        for identity,row in images.items():
            labels=positive[identity];b=boxes[identity]
            if category=='escenas_multiples':valid=len(b['names']&cocoish)>=4
            elif category=='baja_confianza':valid=b['count']>=3 and b['occluded']/b['count']>=.5
            elif category=='escenas_despejadas':valid=bool(labels&wanted) and not (b['names']&cocoish)
            else:valid=bool(labels&wanted)
            if valid:
                eligible.append({'image_id':identity,'original_name':unquote(urlsplit(row['OriginalURL']).path.rsplit('/',1)[-1]),
                    'dataset':'Open Images V7 / validation (CVDF pixels V4/V5)',
                    'original_url':row['OriginalURL'],'landing_url':row['OriginalLandingURL'],
                    'download_url':f'https://open-images-dataset.s3.amazonaws.com/validation/{identity}.jpg',
                    'author':row['Author'] or None,'author_url':row['AuthorProfileURL'] or None,'title':row['Title'],
                    'license_url':row['License'],'license_name':'CC BY 2.0','license_evidence':METADATA['images'],
                    'redistribution':'allowed_with_attribution; unmodified CVDF file (official resize <=1024px)',
                    'upstream_original_md5':row['OriginalMD5'],'original_size_reported':row['OriginalSize'],
                    'category':category,'category_label':CATEGORIES[category][0],'dataset_labels':sorted(labels),
                    'annotation_summary':{'box_classes':sorted(b['names']),'boxes':b['count'],'occluded_boxes':b['occluded']},
                    'rotation_metadata':row.get('Rotation'),'category_is_prediction':False})
        result[category]=sorted(eligible,key=lambda r:sha(f'{seed}:{category}:{r["image_id"]}'.encode()))
    return result


def acquire(root:Path,*,target=10,max_bytes=200_000_000,seed=6,near_distance=5,client=None,selection=None):
    if not 1<=target<=100 or not 0<=near_distance<=20:raise ValueError('Objetivo/hash perceptual fuera de rango')
    folder=root/'data/media/datasets';manifest_path=folder/'manifest.json'
    selection=selection or root/'config/dataset-selection.json'
    budget=Budget(max_bytes);report={'id':stamp().replace(':','-'),'started_at':stamp(),'downloaded':0,'reused':0,'exact_duplicates':0,'near_duplicates':0,'skipped':[],'errors':[]}
    previous=json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.is_file() else {'images':[]}
    previous={r['image_id']:r for r in previous['images']}
    owned=client is None
    client=client or httpx.Client(timeout=40,headers={'User-Agent':'ITESO-P6-local-demo/0.3 (selective public dataset acquisition)'})
    try:
        frozen=json.loads(selection.read_text(encoding='utf-8')) if selection.is_file() else None
        if frozen:
            pools={k:[r for r in frozen['images'] if r['category']==k] for k in CATEGORIES}
            meta=frozen['metadata'];seed=frozen['selection_seed']
        else:
            files,meta=metadata(root/'data/.cache/openimages',client,budget);pools=candidates(files,seed)
        accepted=[];identities=set();digests=set();hashes=[]
        # Seleccionar primero condiciones menos frecuentes; ninguna foto cuenta en dos categorías.
        for category in ['escenas_despejadas','escenas_multiples','baja_confianza','animales','vehiculos','bicicletas','objetos','personas']:
            count=0
            for row in pools[category]:
                if count>=target:break
                identity=row['image_id']
                if not re.fullmatch('[0-9a-f]{16}',identity):
                    report['errors'].append({'id':identity,'error':'Identificador Open Images inválido'});continue
                if identity in identities:continue
                if not permitted_license(row.get('license_url','')):
                    report['skipped'].append({'id':identity,'reason':'license_not_allowed'});continue
                path=folder/category/(identity+'.jpg')
                if not path.resolve().is_relative_to(root.resolve()):raise ValueError('Destino fuera del proyecto')
                existing=previous.get(identity) or row
                try:
                    if path.is_file():
                        data=path.read_bytes();facts=inspect_image(data)
                        if existing.get('sha256') and facts['sha256']!=existing['sha256']:raise ValueError('SHA local distinto del manifiesto; no se sobrescribe')
                        reused=True
                    else:
                        data=fetch(client,row['download_url'],budget);facts=inspect_image(data);reused=False
                        if row.get('sha256') and row['sha256']!=facts['sha256']:raise ValueError('SHA descargado distinto de selección congelada')
                    if facts['sha256'] in digests:
                        report['exact_duplicates']+=1;report['skipped'].append({'id':identity,'reason':'exact_duplicate'});continue
                    nearest=next((old for old,h in hashes if near_duplicate(h,facts,near_distance)),None)
                    if nearest:
                        report['near_duplicates']+=1;report['skipped'].append({'id':identity,'reason':'perceptual_near_duplicate','similar_to':nearest});continue
                    if not reused:
                        path.parent.mkdir(parents=True,exist_ok=True)
                        with path.open('xb') as handle:handle.write(data)
                    record={**row,**facts,'path':path.relative_to(root).as_posix(),
                            'downloaded_at':existing.get('downloaded_at') if reused and existing.get('downloaded_at') else stamp()}
                    accepted.append(record);identities.add(identity);digests.add(facts['sha256']);hashes.append((identity,facts));count+=1
                    report['reused' if reused else 'downloaded']+=1
                except (OSError,ValueError,httpx.HTTPError) as exc:
                    report['errors'].append({'id':identity,'category':category,'error':str(exc)})
                    if budget.transferred>=budget.maximum:break
        result={'schema_version':1,'dataset':'Open Images','selection_seed':seed,'target_per_category':target,
                'phash':'63 AC bits of DCT 8x8 from 32x32 grayscale; Hamming <= threshold; or dHash64 <=3 and RMSE gray16 <=3',
                'near_distance':near_distance,'metadata':meta,'images':accepted}
        write_json(manifest_path,result)
        if not frozen and accepted:write_json(selection,result)
        # CSV UTF-8 conserva atribución/procedencia; campos compuestos van serializados.
        from .exporting import csv_text
        (folder/'manifest.csv').write_text(csv_text('events',accepted),encoding='utf-8')
        report.update(finished_at=stamp(),network_bytes=budget.transferred,limit_bytes=budget.maximum,
                      accepted=len(accepted),categories=dict(Counter(r['category'] for r in accepted)),
                      deficits={k:max(0,target-sum(r['category']==k for r in accepted)) for k in CATEGORIES},
                      unique_sha256=len(digests),manifest_sha256=sha(manifest_path.read_bytes()))
        write_json(root/'evidencias/datasets/descargas'/('download-'+report['id']+'.json'),report)
        return report
    except (httpx.HTTPError,OSError,ValueError) as exc:
        report['errors'].append({'stage':'metadata_or_manifest','error':str(exc)})
        report.update(finished_at=stamp(),accepted=0,network_bytes=budget.transferred,limit_bytes=budget.maximum,
                      existing_manifest_entries=len(previous),completed=False)
        write_json(root/'evidencias/datasets/descargas'/('download-'+report['id']+'.json'),report)
        return report
    finally:
        if owned:client.close()
