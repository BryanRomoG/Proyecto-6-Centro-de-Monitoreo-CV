"""Relaciona hashes de bytes locales, LF de Git y HEAD sin normalizar originales."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

from run_demo import ROOT,code_manifest


def sha(data):return hashlib.sha256(data).hexdigest()


def build(output):
    paths=list(code_manifest())+['data/media/datasets/manifest.json']
    rows={}
    for name in paths:
        data=(ROOT/name).read_bytes();lf=data.replace(b'\r\n',b'\n')
        result=subprocess.run(['git','show','HEAD:Proyecto6/'+name],cwd=ROOT,capture_output=True)
        previous=result.stdout if result.returncode==0 else None
        rows[name]={'worktree_sha256':sha(data),'lf_sha256':sha(lf),'crlf_count':data.count(b'\r\n'),
                    'head_sha256':sha(previous) if previous is not None else None,
                    'same_as_head_bytes':data==previous,
                    'same_as_head_except_crlf':previous is not None and lf==previous.replace(b'\r\n',b'\n')}
    report={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
            'files':rows,'git_or_files_modified':False,
            'scope':'Git fija LF para texto; los manifiestos históricos registran bytes locales CRLF. Este mapa explica la equivalencia sin cambiar ni declarar iguales hashes distintos.',
            'limits':'Los archivos nuevos/modificados no pertenecen al HEAD anterior. La copia instalada y probada es el árbol de trabajo, no un clone remoto. PNG/JPEG/ONNX no se normalizan.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8',newline='\n') as handle:json.dump(report,handle,indent=2,ensure_ascii=False)
    print(json.dumps({'files':len(rows),'crlf_files':sum(bool(r['crlf_count']) for r in rows.values()),
                      'unchanged_content_after_lf':sum(r['same_as_head_except_crlf'] for r in rows.values()),'modified_originals':False}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    build(parser.parse_args().output)
