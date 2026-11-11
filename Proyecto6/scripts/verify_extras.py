"""Recalcula todos los extras de un paquete con corte fijo y datos primarios locales."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from monitor_cv.analytics import extras
from verify_metrics import read_lines


def verify(directory:Path):
    stored=json.loads((directory/'extras.json').read_text(encoding='utf-8'))
    windows=read_lines(directory/'windows.jsonl') if (directory/'windows.jsonl').exists() else []
    obtained=extras(read_lines(directory/'events.jsonl'),read_lines(directory/'alerts.jsonl'),directory,cutoff=stored['cutoff'],windows=windows)
    matches={key:value==obtained['values'][key] for key,value in stored['values'].items()}
    return {'ok':all(matches.values()),'matches':matches,'values':obtained['values'],
            'event_ids':obtained['event_ids'],'alert_ids':obtained['alert_ids']}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    args=parser.parse_args()
    result=verify(args.directory)
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['ok'] else 1)
