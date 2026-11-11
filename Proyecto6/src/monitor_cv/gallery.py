"""Inventario derivado reparable; no modifica eventos ni hashes históricos."""
import hashlib,json,threading,time
from pathlib import Path

from PIL import Image

STATES={
 'available':'Captura disponible',
 'technical_without_image':'Evento técnico sin captura: no se recibió una imagen decodificable',
 'missing_reference':'El evento esperaba captura pero no conserva referencia',
 'missing_file':'Referencia declarada cuyo archivo no existe',
 'unsafe_path':'La referencia sale del almacén permitido',
 'hash_mismatch':'Los bytes no coinciden con el hash histórico',
 'corrupt':'El archivo no es una imagen decodificable',
}


class Gallery:
    def __init__(self,db,data_dir):
        self.db,self.data_dir=db,Path(data_dir).resolve()
        self.lock=threading.Lock();self.last_check=0.

    def refresh(self,*,force=False):
        """Stat ligero por consulta; hash/decodificación solo cuando cambia firma."""
        with self.lock:
            scan=True
            with self.db.connect() as db:
                sql="""SELECT e.id,e.status,json_extract(e.payload,'$.image_ref'),
                    json_extract(e.payload,'$.image_sha256'),i.signature,i.state
                    FROM events e LEFT JOIN image_assets i ON i.event_id=e.id"""
                if not scan:sql+=' WHERE i.event_id IS NULL'
                rows=db.execute(sql).fetchall()
            updates=[]
            for identity,status,ref,expected,previous,old_state in rows:
                state,signature,diagnostic=self.classify(status,ref,expected,previous,old_state,force)
                if state!=old_state or signature!=previous:updates.append((identity,state,signature,diagnostic))
            if updates:
                with self.db.connect() as db:
                    db.executemany('INSERT INTO image_assets VALUES(?,?,?,?) ON CONFLICT(event_id) DO UPDATE SET state=excluded.state,signature=excluded.signature,diagnostic=excluded.diagnostic',updates)
            if scan:self.last_check=time.monotonic()

    def classify(self,status,ref,expected,previous=None,old_state=None,force=False):
        if not ref:
            state='technical_without_image' if status in {'source_error','decode_error'} else 'missing_reference'
            return state,None,STATES[state]
        path=(self.data_dir/ref).resolve()
        if not path.is_relative_to(self.data_dir):return 'unsafe_path',None,STATES['unsafe_path']
        if not path.is_file():return 'missing_file',None,STATES['missing_file']
        stat=path.stat();signature=f'{stat.st_mtime_ns}:{stat.st_size}:{expected}'
        if not force and signature==previous and old_state:return old_state,signature,STATES[old_state]
        try:
            with path.open('rb') as handle:actual=hashlib.file_digest(handle,'sha256').hexdigest()
            if actual!=expected:return 'hash_mismatch',signature,STATES['hash_mismatch']
            with Image.open(path) as im:im.verify()
        except (OSError,ValueError):return 'corrupt',signature,STATES['corrupt']
        return 'available',signature,STATES['available']

    def page(self,filters):
        self.refresh()
        result=self.db.search_events(filters,available=True,slim=True,states=True)
        links=self.db.alert_links([e['id'] for e in result['items']])
        for event in result['items']:
            identity=event['id']
            event.update(image_url=f'/images/{identity}',annotated_url=f'/images/{identity}/annotated',
                         thumbnail_url=f'/images/{identity}/thumbnail',
                         annotated_thumbnail_url=f'/images/{identity}/thumbnail?annotated=true',
                         alerts=links.get(identity,[]),image_state='available')
        counts=result['image_states']
        result['technical_without_image']=counts.get('technical_without_image',0)
        result['pending_images']=counts.get('unchecked',0)
        result['missing_images']=sum(v for k,v in counts.items() if k not in {'available','technical_without_image','unchecked'})
        return result

    def issues(self,filters):
        self.refresh();clauses,args=self.db.event_predicate(filters)
        clauses.append("i.state<>'available'")
        sql=' FROM events e JOIN image_assets i ON i.event_id=e.id WHERE '+' AND '.join(clauses)
        with self.db.connect() as db:
            count=db.execute('SELECT count(*)'+sql,args).fetchone()[0]
            rows=db.execute('SELECT e.id,e.run_id,e.status,e.timestamp,i.state,i.diagnostic'+sql+' ORDER BY e.timestamp DESC,e.id DESC LIMIT ? OFFSET ?',[*args,filters.limit,filters.offset]).fetchall()
        return {'total':count,'items':[dict(zip(['id','run_id','status','timestamp','image_state','reason'],row)) for row in rows],
                'offset':filters.offset,'limit':filters.limit}

    def repair_exact(self,evidence_root):
        """Reparación opcional: únicamente restituye bytes con el SHA ya registrado."""
        self.refresh(force=True);results=[]
        with self.db.connect() as db:
            rows=db.execute("SELECT e.payload FROM events e JOIN image_assets i ON i.event_id=e.id WHERE i.state='missing_file'").fetchall()
        for row in rows:
            e=json.loads(row[0]);target=(self.data_dir/e['image_ref']).resolve()
            if not target.is_relative_to(self.data_dir):continue
            for source in Path(evidence_root).rglob(target.name):
                if source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest()==e['image_sha256']:
                    target.parent.mkdir(parents=True,exist_ok=True)
                    with target.open('xb') as handle:handle.write(source.read_bytes())
                    results.append({'event_id':e['id'],'restored_from':str(source),'sha256':e['image_sha256']});break
        self.refresh(force=True)
        return results
