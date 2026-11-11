from copy import deepcopy
from datetime import datetime,timedelta

from monitor_cv.analytics import extras


def test_alert_time_metrics_and_repeats_by_hand(event,settings):
    start=datetime.fromisoformat(event['timestamp'])
    stamp=lambda seconds:(start+timedelta(seconds=seconds)).isoformat()
    first={'id':'a1','run_id':event['run_id'],'rule_id':'low','timestamp':stamp(0),'status':'resolved',
           'history':[{'action':'acknowledge','timestamp':stamp(3)}, {'action':'resolve','timestamp':stamp(8)}]}
    second={'id':'a2','run_id':event['run_id'],'rule_id':'low','timestamp':stamp(5),'status':'active','history':[]}
    observed=extras([event],[first,second],settings.data_dir,cutoff=stamp(10))
    assert observed['values']['M16']==240
    assert observed['values']['M17']==3
    assert observed['values']['M18']==8
    assert observed['values']['M19']==1
    before=extras([event],[first,second],settings.data_dir,cutoff=stamp(1))
    assert before['values']['M17'] is None and before['values']['M18'] is None
    assert before['values']['M19']==0


def test_error_empty_and_invalid_metrics_by_hand(event,settings):
    empty=deepcopy(event)
    empty.update(id='empty',status='no_detections',detections=[])
    invalid=deepcopy(event)
    invalid.update(id='invalid',status='decode_error',detections=[],image_ref=None)
    missing=deepcopy(event)
    missing.update(id='missing',status='source_error',detections=[],image_ref=None)
    result=extras([empty,invalid,missing],[],settings.data_dir,cutoff=event['timestamp'])['values']
    assert result['M02']==2/3 and result['M05']==1
    assert result['M10']==1 and result['M11']==0
    assert result['M13']==1/2 and result['M14']==1
