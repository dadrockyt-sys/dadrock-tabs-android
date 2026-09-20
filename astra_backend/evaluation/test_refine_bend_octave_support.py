import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from extract_raw_bend_starts import MIDI_OFFSET, model_frame_times
from refine_bend_octave_support import build_report, refine

def arrays(n=160):
    return {"note":np.zeros((n,88),dtype=np.float32),"onset":np.zeros((n,88),dtype=np.float32),"contour":np.zeros((n,264),dtype=np.float32)}

def candidate(frame=40,midi=69):
    times=model_frame_times(160)
    return {"frame":frame,"time":float(times[frame]),"midi":midi,"onsetActivation":.8,
            "earlyPitch":float(midi),"earlyMedianSalience":.4,"earlyMaxSalience":.4,
            "latePitch":float(midi+2),"lateMedianSalience":.4,"lateMaxSalience":.4,
            "riseSemitones":2.0,"technique":"attacked-upward-bend-candidate"}

def paint_lower(raw,frame=40,midi=57,onset=.35,rise=2.0,salience=.4):
    raw["onset"][frame,midi-MIDI_OFFSET]=onset
    times=model_frame_times(raw["onset"].shape[0]); t=times[frame]
    for lo,hi,pitch in [(.035,.085,midi),(.140,.240,midi+rise)]:
        l=np.searchsorted(times,t+lo,"left"); r=np.searchsorted(times,t+hi,"right")
        b=int(round((pitch-MIDI_OFFSET)*3)); raw["contour"][l:r,b]=salience

class OctaveSupportedBendTests(unittest.TestCase):
    def test_reassigns_when_lower_onset_and_contour_support_fundamental(self):
        raw=arrays(); paint_lower(raw)
        out,changes=refine(raw,[candidate()])
        self.assertEqual(out[0]["midi"],57); self.assertTrue(out[0]["octaveSupport"]); self.assertEqual(len(changes),1)
    def test_does_not_lower_without_frame_level_onset_support(self):
        raw=arrays(); paint_lower(raw,onset=.29)
        out,changes=refine(raw,[candidate()])
        self.assertEqual(out[0]["midi"],69); self.assertEqual(changes,[])
    def test_does_not_lower_flat_contour(self):
        raw=arrays(); paint_lower(raw,rise=0)
        out,changes=refine(raw,[candidate()])
        self.assertEqual(out[0]["midi"],69); self.assertEqual(changes,[])
    def test_does_not_lower_when_contour_salience_never_reaches_frame_threshold(self):
        raw=arrays(); paint_lower(raw,salience=.29)
        out,changes=refine(raw,[candidate()])
        self.assertEqual(out[0]["midi"],69); self.assertEqual(changes,[])
    def test_never_moves_more_than_one_frame_for_octave_support(self):
        raw=arrays(); paint_lower(raw,frame=41)
        c=candidate(frame=40); out,_=refine(raw,[c])
        self.assertLessEqual(abs(out[0]["frame"]-c["frame"]),1)
    def test_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); raw=arrays(20); np.savez(root/"r.npz",**raw)
            source={"kind":"basic-pitch-raw-attacked-bend-candidates","customerDeliveryEligible":False,"policy":{"referenceLabelsRead":False},"candidates":[]}
            (root/"c.json").write_text(json.dumps(source))
            with self.assertRaisesRegex(ValueError,"SHA256"):
                build_report(root/"r.npz",root/"c.json",expected_raw_sha256="0"*64)

if __name__=="__main__": unittest.main()
