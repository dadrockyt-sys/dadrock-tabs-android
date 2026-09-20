import tempfile
import unittest
from pathlib import Path

import numpy as np

from extract_raw_bend_starts import MIDI_OFFSET, build_report, deduplicate, extract, model_frame_times

def prediction(events=None):
    return {"kind":"whole-mix-basic-pitch-development-only","customerDeliveryEligible":False,"events":events or []}

def arrays(n=120):
    return {"note":np.zeros((n,88),dtype=np.float32),"onset":np.zeros((n,88),dtype=np.float32),"contour":np.zeros((n,264),dtype=np.float32)}

def paint_bend(raw, frame, midi, onset=.7, rise=2.0):
    raw["onset"][frame,midi-MIDI_OFFSET]=onset
    times=model_frame_times(raw["onset"].shape[0]); t=times[frame]
    for lo,hi,pitch,sal in [(.035,.085,midi,.35),(.140,.240,midi+rise,.4)]:
        l=np.searchsorted(times,t+lo,"left"); r=np.searchsorted(times,t+hi,"right")
        b=int(round((pitch-MIDI_OFFSET)*3)); raw["contour"][l:r,b]=sal

class BendDetectorTests(unittest.TestCase):
    def test_detects_strong_attacked_rising_contour(self):
        raw=arrays(160); paint_bend(raw,40,57)
        out=extract(raw,prediction())
        self.assertEqual(len(out),1); self.assertEqual(out[0]["midi"],57)
    def test_standard_onset_threshold_is_not_lowered(self):
        raw=arrays(160); paint_bend(raw,40,57,onset=.49)
        self.assertEqual(extract(raw,prediction()),[])
    def test_same_pitch_native_attack_suppresses_candidate(self):
        raw=arrays(160); paint_bend(raw,40,57)
        t=float(model_frame_times(160)[40])
        self.assertEqual(extract(raw,prediction([{"start":t,"end":t+.2,"midi":57}])),[])
    def test_flat_contour_is_not_a_bend(self):
        raw=arrays(160); paint_bend(raw,40,57,rise=0)
        self.assertEqual(extract(raw,prediction()),[])
    def test_requires_normal_frame_level_salience_somewhere(self):
        raw=arrays(160); paint_bend(raw,40,57); raw["contour"]*=.5
        self.assertEqual(extract(raw,prediction()),[])
    def test_neighboring_raw_bins_are_deduplicated_by_onset_strength(self):
        c=[{"time":1.0,"midi":57,"onsetActivation":.7},{"time":1.01,"midi":58,"onsetActivation":.8}]
        out=deduplicate(c)
        self.assertEqual(len(out),1); self.assertEqual(out[0]["midi"],58)
    def test_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); raw=arrays(10); np.savez(root/"r.npz",**raw)
            (root/"p.json").write_text('{"kind":"whole-mix-basic-pitch-development-only","customerDeliveryEligible":false,"events":[]}')
            with self.assertRaisesRegex(ValueError,"SHA256"):
                build_report(root/"r.npz",root/"p.json",expected_raw_sha256="0"*64)

if __name__=="__main__": unittest.main()
