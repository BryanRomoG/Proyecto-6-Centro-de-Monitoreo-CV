"""Distancia descriptiva entre CDF de scores; sin p-value ni afirmación de drift."""
import numpy as np

from .metrics import epoch


def ks_distance(reference, sample):
    if not reference or not sample:
        return None
    a,b=np.sort(reference),np.sort(sample)
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError('Scores no finitos: no se calcula distancia')
    support=np.unique(np.concatenate([a,b]))
    return float(np.max(np.abs(np.searchsorted(a,support,side='right')/len(a)
                               -np.searchsorted(b,support,side='right')/len(b))))


def compare_windows(events,windows,cutoff):
    indexed={e['id']:e for e in events}
    comparisons=[]
    for run in sorted({e['run_id'] for e in events}):
        current=[e for e in events if e['run_id']==run]
        policy=current[0]['config']['confidence']
        ordered=sorted([w for w in windows if w['run_id']==run and epoch(w['timestamp'])<=epoch(cutoff)],key=lambda w:w['timestamp'])
        refs=[w for w in ordered if w['state']=='collecting_reference'][:policy['reference_windows']]
        ref_ids=[identity for w in refs for identity in w['event_ids']]
        reference_complete=len(refs)==policy['reference_windows'] and all(identity in indexed for identity in ref_ids)
        reference=[d['confidence'] for identity in ref_ids if identity in indexed for d in indexed[identity]['detections']]
        ref_keys={(indexed[i]['config_sha256'],indexed[i]['model']['sha256']) for i in ref_ids if i in indexed}
        for window in ordered:
            identities=window['event_ids']
            valid=all(i in indexed for i in identities)
            sample=[d['confidence'] for i in identities if i in indexed for d in indexed[i]['detections']]
            keys={(indexed[i]['config_sha256'],indexed[i]['model']['sha256']) for i in identities if i in indexed}
            is_reference=window in refs
            eligible=reference_complete and valid and len(reference)>=policy['min_detections'] and len(sample)>=policy['min_detections']
            eligible=eligible and len(ref_keys)==1 and keys==ref_keys and all(indexed[i]['status'] in {'ok','no_detections'} for i in identities)
            comparisons.append({'run_id':run,'window_id':window['id'],'reference_window_ids':[w['id'] for w in refs],
                                'event_ids':identities,'reference_event_ids':ref_ids,
                                'reference_count':len(reference),'sample_count':len(sample),
                                'state':'reference' if is_reference else 'observed' if eligible else 'insufficient_evidence',
                                'distance':ks_distance(reference,sample) if eligible and not is_reference else None})
    return comparisons or None
