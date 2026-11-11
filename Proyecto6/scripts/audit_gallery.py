"""Clasifica referencias sin alterar eventos. Restauración opcional exige el SHA histórico."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from monitor_cv.config import load_settings
from monitor_cv.database import Database
from monitor_cv.gallery import Gallery
from monitor_cv.query import Filters
from monitor_cv.events import uid,utc_now
from monitor_cv.datasets import write_json

def audit(restore=False):
    settings=load_settings(environ=False);db=Database(settings.data_dir/settings.storage.database)
    gallery=Gallery(db,settings.data_dir);gallery.refresh(force=True)
    repairs=gallery.repair_exact(ROOT/'evidencias') if restore else []
    state=gallery.page(Filters(limit=1));issues=gallery.issues(Filters(limit=500))
    report={'timestamp':utc_now(),'available':state['total'],'states':state['image_states'],
            'missing_images':state['missing_images'],'technical_without_image':state['technical_without_image'],
            'issues':issues,'repairs':repairs,'historical_payloads_modified':False,
            'note':'Un evento de source_error/decode_error sin image_ref no declara un archivo perdido. Ninguna imagen se fabrica ni se cambia un SHA.'}
    destination=ROOT/'evidencias/datasets/referencias'/f'{uid("audit")}.json';write_json(destination,report)
    return {'file':str(destination),'available':state['total'],'states':state['image_states'],'repairs':len(repairs)}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--restore-exact',action='store_true')
    args=parser.parse_args();print(json.dumps(audit(args.restore_exact),indent=2))
