"""Inventario de publicación: solo lee Git/archivos; nunca agrega, elimina ni publica."""
from pathlib import Path
import argparse
import json
import os
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)


def build(output):
    tracked=set(git('ls-files','-z').decode('utf-8').strip('\0').split('\0'))
    changed=set(git('diff','--name-only','-z').decode('utf-8').strip('\0').split('\0'))-{''}
    added=set(git('ls-files','--others','--exclude-standard','-z').decode('utf-8').strip('\0').split('\0'))-{''}
    profile=os.environ.get('USERPROFILE',str(Path.home()))
    needles={profile,profile.replace('\\','/'),profile.replace('\\','\\\\')}
    personal_paths=[];large=[];total=0
    for name in sorted(tracked|added):
        path=ROOT/name
        if not path.is_file():continue
        size=path.stat().st_size;total+=size
        if size>20*1024*1024:large.append({'path':name,'bytes':size})
        if size>5*1024*1024:continue
        try:text=path.read_text(encoding='utf-8')
        except (UnicodeError,OSError):continue
        if any(n in text for n in needles):personal_paths.append(name)
    report={'head':git('rev-parse','HEAD').decode().strip(),'branch':git('branch','--show-current').decode().strip(),
            'remote':git('remote','get-url','origin').decode().strip(),'index_changed':bool(git('diff','--cached','--name-only')),
            'tracked_files':len(tracked),'candidate_total_bytes':total,'over_20_mib':large,
            'modified_paths':sorted(changed),'new_paths':sorted(added),'personal_path_files':personal_paths,
            'personal_path_count':len(personal_paths),
            'protected_projects_modified':sorted(n for n in changed if any(n.startswith(f'Proyecto{i}/') for i in range(1,6))),
            'no_git_mutations_executed':True,
            'publication_status':'NO PUBLICAR sin revisar selección, rutas históricas y licencia de dog.jpg legado',
            'license_note':'Open Images: 80 licencias CC BY 2.0 individuales verificadas. No atribuir automáticamente Apache-2.0 a la fotografía dog.jpg de YOLOX o a derivados históricos.',
            'privacy_note':'Solo rutas de archivos afectados; no se imprimen valores privados o credenciales. Los originales históricos permanecen intactos. .gitignore no retira archivos ya rastreados.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as handle:json.dump(report,handle,indent=2,ensure_ascii=False)
    print(json.dumps({'head':report['head'],'modified':len(changed),'new':len(added),
                      'personal_path_files':len(personal_paths),'over_20_mib':len(large),'index_changed':report['index_changed']}))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    build(parser.parse_args().output)
