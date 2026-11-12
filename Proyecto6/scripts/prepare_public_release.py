"""Audita y materializa una copia pública revisable. No ejecuta mutaciones de Git."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
sys.path.insert(0,str(ROOT/'src'))
from monitor_cv.events import utc_now

EXCLUDED_IMAGE='26557008b4fcf408'
EMAIL=re.compile(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}')
LOCAL=re.compile(r'(?:[A-Za-z]:[\\/](?:Users|home)[\\/][^\s\"<>|]+|/home/[A-Za-z0-9_.-]+(?:/[^\s\"<>|]+)?)',re.I)
SECRET=re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')


def sha(data):return hashlib.sha256(data).hexdigest()
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def names(*args):return set(git(*args,'-z').decode('utf-8').strip('\0').split('\0'))-{''}


def findings(text):
    result=[]
    for number,line in enumerate(text.splitlines(),1):
        decoded=line.replace('\\\\','\\')
        kinds=[]
        if LOCAL.search(decoded):kinds.append('local_profile_path')
        if EMAIL.search(line):kinds.append('contact_or_example')
        if SECRET.search(line):kinds.append('possible_secret')
        if kinds:result.append({'line':number,'types':kinds})
    return result


def audit(output:Path,*,remote=False):
    tracked=names('ls-files');modified=names('diff','--name-only');new=names('ls-files','--others','--exclude-standard')
    ignored=names('ls-files','--others','--ignored','--exclude-standard')
    head=git('rev-parse','HEAD').decode().strip()
    remote_info={'checked':False,'published_findings':'unknown'};remote_paths=set()
    if remote:
        import httpx
        url='https://api.github.com/repos/BryanRomoG/Proyecto-6-Centro-de-Monitoreo-CV'
        try:
            with httpx.Client(timeout=40) as client:
                repo=client.get(url);repo.raise_for_status()
                ref=client.get(url+'/git/ref/heads/main');ref.raise_for_status();remote_sha=ref.json()['object']['sha']
                tree=client.get(url+'/git/trees/'+remote_sha,params={'recursive':'1'});tree.raise_for_status()
                data=tree.json()
                if data.get('truncated'):raise ValueError('Árbol remoto incompleto')
                remote_paths={r['path'] for r in data['tree'] if r['type']=='blob'}
                remote_info={'checked':True,'public':repo.json().get('private') is False,'main_sha':remote_sha,
                             'matches_local_head':remote_sha==head,'method':'API pública GET repo/ref/tree; sin fetch ni cambios de Git'}
        except Exception as exc:remote_info={'checked':False,'error_type':type(exc).__name__,'published_findings':'unknown'}
    rows=[];issues=[]
    for name in sorted(tracked|new):
        path=REPO/name
        if not path.is_file():continue
        raw=path.read_bytes();found=[]
        if len(raw)<8_000_000:
            try:found=findings(raw.decode('utf-8'))
            except UnicodeError:pass
        prior=[]
        if name in tracked and found and remote_info.get('matches_local_head') and name in remote_paths:
            try:prior=findings(git('show','HEAD:'+name).decode('utf-8'))
            except (UnicodeError,subprocess.CalledProcessError):pass
        item={'path':name,'git_state':'modified' if name in modified else 'tracked' if name in tracked else 'new',
              'bytes':len(raw),'sha256':sha(raw),'remote_contains_path':name in remote_paths if remote_info.get('checked') else None}
        rows.append(item)
        if found:
            issues.append({**item,'findings':found,'findings_in_published_HEAD':prior,
                          'sensitivity':'manual_review_required' if any('possible_secret' in f['types'] for f in found) else 'contact_or_local_path; no secreto confirmado por este escaneo',
                          'resolution':'original histórico intacto; copia pública seleccionada o exclusión del paquete'})
    report={'timestamp':utc_now(),'head':head,'branch':git('branch','--show-current').decode().strip(),
            'staged':sorted(names('diff','--cached','--name-only')),'remote':remote_info,
            'counts':{'tracked':len(tracked),'modified':len(modified),'new':len(new),'ignored':len(ignored),'files_with_findings':len(issues)},
            'files':rows,'issues':issues,'ignored_paths':sorted(ignored),
            'limits':'Escaneo heurístico sin valores sensibles; remoto solo árbol HEAD, no garantiza ausencia en otras ramas o todo el historial.'}
    write(output,report)
    return report


def scrub(value,changes,field='$'):
    if isinstance(value,dict):return {k:scrub(v,changes,field+'/'+k) for k,v in value.items()}
    if isinstance(value,list):return [scrub(v,changes,field+'/'+str(i)) for i,v in enumerate(value)]
    if isinstance(value,str):
        match=LOCAL.search(value)
        # Una ruta de OneDrive puede contener espacios: omitir también su sufijo,
        # conservando el mensaje previo y los campos técnicos separados del evento.
        clean=value[:match.start()]+'[LOCAL_PATH_OMITTED]' if match else value
        if clean!=value:changes.append({'field':field,'reason':'ruta de perfil local innecesaria; original conservado'})
        if SECRET.search(clean):raise ValueError('Posible secreto: revisión requerida, sin imprimir valor')
        return clean
    return value


def project_bytes(source,changes):
    raw=source.read_bytes()
    # La sanitización nunca reescribe código ejecutable, plantillas ni documentos
    # oficiales HTML. Si contienen una incidencia real, la auditoría bloquea su selección.
    if source.suffix in {'.py','.js','.css','.html','.svg'}:return raw
    if source.suffix=='.json':
        value=scrub(json.loads(raw.decode('utf-8')),changes)
        return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
    if source.suffix=='.jsonl':
        values=[scrub(json.loads(line),changes,'$line/'+str(i)) for i,line in enumerate(raw.decode('utf-8').splitlines(),1) if line]
        return ''.join(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n' for v in values).encode()
    try:text=raw.decode('utf-8')
    except UnicodeError:return raw
    clean=LOCAL.sub('[LOCAL_PATH_OMITTED]',text)
    if clean!=text:changes.append({'field':'text','reason':'rutas de perfil local innecesarias'})
    if SECRET.search(clean):raise ValueError('Posible secreto en la selección')
    return clean.encode()


def markdown_links(text):
    return list(re.finditer(r'\[([^\]\n]+)\]\((?:<([^>]+)>|([^\s)]+))(?:\s+"[^"]*")?\)',text))


def broken_links(directory):
    broken=[]
    for path in directory.rglob('*.md'):
        for match in markdown_links(path.read_text(encoding='utf-8')):
            target=match.group(2) or match.group(3)
            if target.startswith(('#','http:','https:','mailto:','data:')):continue
            target=unquote(target.split('#')[0])
            resolved=(path.parent/target).resolve()
            if not resolved.is_relative_to(directory.resolve()) or not resolved.exists():
                broken.append({'path':path.relative_to(directory).as_posix(),'target':target})
    return broken


def build(destination:Path,*,evidence:Path|None=None):
    for required in ['evidencias/publicacion_segura/INDICE_GITHUB.md','Docs/PUBLICACION_SEGURA.md','config/dataset-selection-public.json']:
        if not (ROOT/required).is_file():raise ValueError('Falta un documento obligatorio para la selección pública: '+required)
    destination=destination.resolve()
    if destination.exists():raise ValueError('Elegir un destino nuevo; no sobrescribir otra selección')
    destination.mkdir(parents=True)
    sources=[];ledger=[]
    for folder,patterns in [('src',['*.py']),('scripts',['*.py']),('tests',['*.py']),('browser_tests',['*.py']),
                             ('web',['*.html','*.css','*.js','*.svg']),('Docs',['*.md','*.html'])]:
        for pattern in patterns:sources.extend((ROOT/folder).rglob(pattern))
    sources+=list(ROOT.glob('*.md'))+list(ROOT.glob('requirements*.txt'))
    sources += [ROOT/p for p in ['pyproject.toml','.gitignore','.env.example','config/settings.yaml','config/academic.json','modelo/descriptor.yaml'] if (ROOT/p).is_file()]
    for source in sorted(set(sources)):
        if '__pycache__' in source.parts:continue
        relative=source.relative_to(ROOT)
        copy_one(source,destination/'Proyecto6'/relative,ledger)
    public_selection=ROOT/'config/dataset-selection-public.json'
    for name in ['dataset-selection.json','dataset-selection-public.json']:
        copy_one(public_selection,destination/'Proyecto6/config'/name,ledger)
    # Solo evidencia con fotografías acreditadas: paquete de revisión y nueva suite autorizada.
    selected=ROOT/'evidencias/publicacion_segura'
    if selected.exists():
        for source in selected.rglob('*'):
            relative=source.relative_to(selected)
            if relative.parts[0]=='escenarios':continue  # originales locales; se exportan las proyecciones de publico/
            if source.is_file() and source.suffix not in ['.sqlite3','.db','.log']:
                copy_one(source,destination/'Proyecto6/evidencias/publicacion_segura'/source.relative_to(selected),ledger)
    review=ROOT/'evidencias/cierre_final/revision'
    for source in review.iterdir():
        if source.is_file():copy_one(source,destination/'Proyecto6/evidencias/publicacion_segura/revision'/source.name,ledger)
    for source in [REPO/'.gitignore',REPO/'.gitattributes',REPO/'.github/workflows/p6-ci.yml']:
        copy_one(source,destination/source.relative_to(REPO),ledger)
    readme='# Entrega pública propuesta: Proyecto 6\n\nCopia local revisada, aún sin commit ni publicación. No representa un clone remoto.\n\n[Proyecto 6](Proyecto6/README.md) · [Índice público](Proyecto6/evidencias/publicacion_segura/INDICE_GITHUB.md) · [Publicación segura](Proyecto6/Docs/PUBLICACION_SEGURA.md).\n\nLos antecedentes Proyecto1–Proyecto5 se conservan intactos en el repositorio original. Esta copia selecciona exclusivamente la entrega Proyecto6; no retira archivos del repositorio existente ni de su historial.\n'
    (destination/'README.md').write_text(readme,encoding='utf-8')
    critical=[r for r in broken_links(destination) if r['path']=='Proyecto6/evidencias/publicacion_segura/INDICE_GITHUB.md']
    if critical:raise ValueError('El índice público contiene referencias no incluidas; corregir la selección antes de exportar')
    # Los documentos públicos se identifican como proyecciones y sustituyen enlaces exclusivamente locales.
    for path in destination.rglob('*.md'):
        if path.name=='prompt-evaluacion-proyecto-6.md':continue
        text=path.read_text(encoding='utf-8');edits=[]
        for match in markdown_links(text):
            target=match.group(2) or match.group(3)
            if target.startswith(('#','http:','https:','mailto:','data:')):continue
            resolved=(path.parent/unquote(target.split('#')[0])).resolve()
            if not resolved.is_relative_to(destination) or not resolved.exists():
                edits.append((match.start(),match.end(),match.group(1)+' (registro local o recurso regenerable; consultar el índice público)'))
        for start,end,replacement in reversed(edits):text=text[:start]+replacement+text[end:]
        if edits:
            text='> Copia pública derivada: los enlaces a registros locales se sustituyeron por notas explícitas. El original se conserva.\n\n'+text
            ledger.append({'destination':path.relative_to(destination).as_posix(),'transformation':'local_markdown_links_to_explicit_notes','count':len(edits)})
        path.write_text(text,encoding='utf-8',newline='\n')
    problems=[]
    for path in destination.rglob('*'):
        if not path.is_file():continue
        try:found=findings(path.read_text(encoding='utf-8'))
        except UnicodeError:continue
        # Se conservan correos sintéticos en tests y expresiones regulares; solo se permiten los dominios reservados.
        if found:
            text=path.read_text(encoding='utf-8')
            contacts=[e for e in EMAIL.findall(text) if not e.lower().endswith(('.test','.invalid','example.com','example.org','example.net'))]
            severe=any('possible_secret' in f['types'] or 'local_profile_path' in f['types'] for f in found)
            if contacts or severe:problems.append({'path':path.relative_to(destination).as_posix(),'types':sorted({t for f in found for t in f['types']})})
    files=[{'path':p.relative_to(destination).as_posix(),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(destination.rglob('*')) if p.is_file()]
    report={'timestamp':utc_now(),'head_parent':git('rev-parse','HEAD').decode().strip(),'not_a_remote_clone':True,
            'selection_files':files,'transformations':ledger,'broken_links':broken_links(destination),'privacy_findings':problems,
            'originals_preserved':True,'publication_excluded_photo':EXCLUDED_IMAGE,
            'omitted':'P1–P5 originales, bases locales, modelos, fotos dog.jpg y derivados, metadatos con contacto y evidencia raw no seleccionada',
            'ok':not problems and not broken_links(destination)}
    write(destination/'PUBLICATION_MANIFEST.json',report)
    if evidence:write(evidence,report)
    return report


def copy_one(source,target,ledger):
    changes=[];raw=source.read_bytes();projected=project_bytes(source,changes)
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(projected)
    ledger.append({'source':source.relative_to(REPO).as_posix(),'destination':target.as_posix().split('/Proyecto6/')[-1] if '/Proyecto6/' in target.as_posix() else source.relative_to(REPO).as_posix(),
                   'source_sha256':sha(raw),'copy_sha256_before_markdown_projection':sha(projected),'fields_changed':changes,
                   'scope':'copia derivada, no reescribe original ni sus hashes'})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    ap=sub.add_parser('audit');ap.add_argument('--output',type=Path,required=True);ap.add_argument('--remote',action='store_true')
    bp=sub.add_parser('build');bp.add_argument('--destination',type=Path,required=True);bp.add_argument('--report',type=Path)
    args=parser.parse_args()
    result=audit(args.output,remote=args.remote) if args.command=='audit' else build(args.destination,evidence=args.report)
    print(json.dumps({'command':args.command,'ok':result.get('ok'),'counts':result.get('counts'),'issues':len(result.get('privacy_findings',[])),'broken_links':len(result.get('broken_links',[]))}))
    raise SystemExit(0 if result.get('ok',True) else 1)
