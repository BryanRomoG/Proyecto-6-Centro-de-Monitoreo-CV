from copy import deepcopy

from monitor_cv.distribution import compare_windows,ks_distance


def test_ks_by_hand_identical_disjoint_missing():
    assert ks_distance([.8,.9],[.8,.9])==0
    assert ks_distance([.8,.9],[.1,.2])==1
    assert ks_distance([.1,.3],[.2,.4])==.5
    assert ks_distance([], [.4]) is None


def test_reference_comparison_change_recovery_and_insufficient(event):
    events=[]
    for i,score in enumerate([.8,.9,.1,.2,.8,.9]):
        row=deepcopy(event)
        row['id']='sample-'+str(i)
        row['detections'][0]['confidence']=score
        row['config']['confidence'].update(window_frames=2,min_detections=2,reference_windows=1)
        events.append(row)
    windows=[{'id':'w'+str(i),'run_id':event['run_id'],'timestamp':event['timestamp'],
              'state':'collecting_reference' if i==0 else 'within_policy',
              'event_ids':[row['id'] for row in events[i*2:i*2+2]]} for i in range(3)]
    result=compare_windows(events,windows,event['timestamp'])
    assert [w['distance'] for w in result]==[None,1,0]
    missing=compare_windows(events[2:],windows,event['timestamp'])
    assert all(w['distance'] is None for w in missing)
    events[-1]['config_sha256']='other-config'
    assert compare_windows(events,windows,event['timestamp'])[-1]['distance'] is None
