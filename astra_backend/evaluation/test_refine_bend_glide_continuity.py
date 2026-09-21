import unittest
import numpy as np
from extract_raw_bend_starts import MIDI_OFFSET, model_frame_times
from refine_bend_glide_continuity import refine


def arrays(n=180):
    return {'note':np.zeros((n,88),np.float32),'onset':np.zeros((n,88),np.float32),'contour':np.zeros((n,264),np.float32)}

def candidate(frame=40,midi=57):
    return {'frame':frame,'time':float(model_frame_times(180)[frame]),'midi':midi,'onsetActivation':.7,'policyTag':'synthetic'}

def paint_path(raw,c,pitches,sal=.4):
    times=model_frame_times(raw['contour'].shape[0]); t=c['time']
    l=np.searchsorted(times,t+.035,'left'); r=np.searchsorted(times,t+.240,'right')
    seq=list(pitches)
    if len(seq)<r-l: seq += [seq[-1]]*((r-l)-len(seq))
    for i,pitch in enumerate(seq[:r-l]):
        b=int(round((pitch-MIDI_OFFSET)*3)); raw['contour'][l+i,b]=sal

class GlideContinuityTests(unittest.TestCase):
    def test_smooth_multi_bin_bend_passes(self):
        raw=arrays(); c=candidate(); paint_path(raw,c,[57,57,57+1/3,57+1/3,57+2/3,57+2/3,58,58,58+1/3,58+1/3,58+2/3,58+2/3,59])
        kept,rejected=refine(raw,[c]); self.assertEqual(len(kept),1); self.assertEqual(rejected,[])
    def test_large_single_frame_jump_fails(self):
        raw=arrays(); c=candidate(); paint_path(raw,c,[57]*5+[59]*10)
        kept,rejected=refine(raw,[c]); self.assertEqual(kept,[]); self.assertEqual(len(rejected),1)
    def test_too_few_contour_bins_fails(self):
        raw=arrays(); c=candidate(); paint_path(raw,c,[57]*5+[57+1/3]*5+[57+2/3]*8)
        kept,_=refine(raw,[c]); self.assertEqual(kept,[])
    def test_downward_instability_fails(self):
        raw=arrays(); c=candidate(); paint_path(raw,c,[57,57+1/3,57,57+1/3,57,57+1/3,57,57+2/3,58,58+1/3,58+2/3,59])
        kept,_=refine(raw,[c]); self.assertEqual(kept,[])
    def test_low_salience_frames_do_not_create_fake_path(self):
        raw=arrays(); c=candidate(); paint_path(raw,c,[57,57+1/3,57+2/3,58,58+1/3,58+2/3,59],sal=.1)
        kept,_=refine(raw,[c]); self.assertEqual(kept,[])

if __name__=='__main__': unittest.main()
