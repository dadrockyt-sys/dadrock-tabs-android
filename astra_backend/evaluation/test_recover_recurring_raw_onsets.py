import unittest, numpy as np
from recover_recurring_raw_onsets import recover
from extract_raw_bend_starts import MIDI_OFFSET, model_frame_times


def alignment(n=5):
    return {'reviewStatus':'complete','independentOfPredictions':True,
            'segments':[{'beatStart':4*i,'beatEnd':4*(i+1),'timeStart':2*i,'timeEnd':2*(i+1)} for i in range(n)]}

def core_event(i,m,rel=1,midi=60):
    return {'id':i,'midi':midi,'start':(m-1)*2+rel*.5,
            'repeatEvidence':{'measureIndex':m,'relativeBeat':rel,'distinctMeasureSupport':3,'recurringCore':True}}

def partition(measures=(1,3,4),rel=1,midi=60):
    rows=[core_event(str(m),m,rel,midi) for m in measures]
    return {'status':'complete','recurringCoreEvents':rows,'diagnostics':{'referenceLabelsRead':False}}

def raw(n=800):
    return {'note':np.zeros((n,88),np.float32),'onset':np.zeros((n,88),np.float32),'contour':np.zeros((n,264),np.float32)}

def paint_onset(r,source_time,midi=60,offset=.5,scale=1.0,value=.7):
    times=model_frame_times(r['onset'].shape[0]); iso=offset+scale*source_time
    f=int(np.argmin(np.abs(times-iso))); b=midi-MIDI_OFFSET
    r['onset'][f,b]=value
    r['onset'][max(0,f-1),b]=value*.5
    r['onset'][min(len(times)-1,f+1),b]=value*.4

class RecurringRawOnsetRecoveryTests(unittest.TestCase):
    def test_recovers_internal_gap_from_standard_onset_peak(self):
        r=raw(); paint_onset(r,2.5)
        out=recover(partition(),r,alignment(),[],affine_offset=.5,affine_scale=1.0)
        self.assertEqual(len(out['recoveredEvents']),1)
        self.assertEqual(out['recoveredEvents'][0]['midi'],60)
        self.assertEqual(out['recoveredEvents'][0]['recoveryEvidence']['measureIndex'],2)

    def test_does_not_fill_leading_or_trailing_missing_measures(self):
        r=raw(); paint_onset(r,.5); paint_onset(r,8.5)
        out=recover(partition(measures=(2,3,4)),r,alignment(),[],affine_offset=.5,affine_scale=1.0)
        self.assertEqual(out['recoveredEvents'],[])

    def test_subthreshold_onset_does_not_recover(self):
        r=raw(); paint_onset(r,2.5,value=.49)
        out=recover(partition(),r,alignment(),[],affine_offset=.5,affine_scale=1.0)
        self.assertEqual(out['recoveredEvents'],[])

    def test_pitch_must_come_from_existing_recurring_key(self):
        r=raw(); paint_onset(r,2.5,midi=61)
        out=recover(partition(midi=60),r,alignment(),[],affine_offset=.5,affine_scale=1.0)
        self.assertEqual(out['recoveredEvents'],[])

    def test_existing_decoded_event_is_preferred_to_raw_synthesis(self):
        r=raw(); existing=[{'id':'x','midi':60,'start':2.51,'amplitude':.4}]
        out=recover(partition(),r,alignment(),existing,affine_offset=.5,affine_scale=1.0)
        self.assertEqual(len(out['recoveredEvents']),1)
        self.assertEqual(out['recoveredEvents'][0]['recoveryEvidence']['kind'],'existing-decoded-recurring-gap')

    def test_requires_complete_reference_blind_partition(self):
        r=raw(); p=partition(); p['diagnostics']['referenceLabelsRead']=True
        with self.assertRaises(ValueError):
            recover(p,r,alignment(),[],affine_offset=.5,affine_scale=1.0)

if __name__=='__main__':
    unittest.main()
