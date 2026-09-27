import unittest
from evaluation.pretrained_note_front_end_v1 import *

def meta(key,events=None):
    perf=key.split("|")[0]
    return {"captureKey":key,"captureView":"directinput","performer":perf,
            "prepared":{"unresolvedLabelCount":0,"crop":{"frames":200},
                        "scorableEvents":events or []}}

class FrontEndSyntheticTests(unittest.TestCase):
    def test_standard_tuning_mapping(self):
        self.assertEqual([string_fret_to_midi(i,0) for i in range(6)],[40,45,50,55,59,64])
        self.assertEqual(string_fret_to_midi(0,12),52)
    def test_wrong_identity_rejected(self):
        m=meta(P1_KEYS[0]); m["captureKey"]=P1_KEYS[1]
        with self.assertRaises(RuntimeError): validate_meta(m,P1_KEYS[0])
    def test_duplicate_pitch_ambiguity_retained(self):
        m=meta(P1_KEYS[0],[
          {"id":"a","string":0,"fret":5,"start":0.1,"end":0.4},
          {"id":"b","string":1,"fret":0,"start":0.1,"end":0.4}])
        refs,amb=reference_pitch_events(m)
        self.assertEqual([e.pitch for e in refs],[45,45])
        self.assertEqual(amb,[["a","b"]])
    def test_duplicate_pitch_is_collapsed_for_pitch_only_score(self):
        refs=[PitchEvent("a",45,.1,.4),PitchEvent("b",45,.1,.4)]
        preds=[PitchEvent("p",45,.1,.4)]
        s=score_pitch_events(preds,refs)
        self.assertEqual(s["rawReferenceCount"],2)
        self.assertEqual(s["ambiguityCollapsedReferenceCount"],1)
        self.assertEqual(s["pitchOnset"]["truePositive"],1)
        self.assertEqual(s["pitchOnset"]["f1"],1.0)
    def test_crop_boundary_clips_without_favorable_window(self):
        notes=[(-1.0,0.2,40,1,None),(0.95,1.2,45,1,None),(1.2,1.4,50,1,None)]
        got=basic_pitch_to_crop_events(notes,0.0,1.0)
        self.assertEqual(len(got),2)
        self.assertEqual((got[0].start,got[0].end),(0.0,0.2))
        self.assertEqual((got[1].start,got[1].end),(0.95,1.0))
    def test_pitch_onset_scorer_one_to_one(self):
        refs=[PitchEvent("r1",40,.10,.30),PitchEvent("r2",45,.50,.80)]
        preds=[PitchEvent("p1",40,.12,.31),PitchEvent("p2",45,.70,.80)]
        s=score_pitch_events(preds,refs)
        self.assertEqual(s["pitchOnset"]["truePositive"],1)
        self.assertEqual(s["pitchOnsetOffset"]["truePositive"],1)
    def test_zero_optimizer_constants_are_frozen(self):
        self.assertEqual((ONSET_THRESHOLD,FRAME_THRESHOLD,MIN_NOTE_LENGTH_MS),(.5,.3,127.70))

if __name__=="__main__": unittest.main()
