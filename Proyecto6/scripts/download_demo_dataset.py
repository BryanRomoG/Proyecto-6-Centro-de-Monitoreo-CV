"""Descarga selectiva verificable, máximo 200 MB incluyendo metadatos, sin dataset completo."""
import argparse,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from monitor_cv.datasets import acquire

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target-per-category',type=int,default=10)
    parser.add_argument('--max-mb',type=float,default=200)
    parser.add_argument('--seed',type=int,default=6)
    parser.add_argument('--near-distance',type=int,default=5)
    args=parser.parse_args()
    result=acquire(ROOT,target=args.target_per_category,max_bytes=int(args.max_mb*1_000_000),seed=args.seed,near_distance=args.near_distance)
    print(json.dumps(result,indent=2,ensure_ascii=False))
    raise SystemExit(0 if result['accepted'] else 1)
