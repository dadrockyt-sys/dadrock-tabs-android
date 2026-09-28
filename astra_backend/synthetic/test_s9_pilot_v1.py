import unittest
import numpy as np
import torch

from synthetic.s0_pilot_v1 import build_template, ROOT_SEED, _seed
from synthetic.s6_pilot_v1 import initialize_arm, module_sha
from synthetic.s9_pilot_v1 import intervention_chord_template, chord_signature

class S9Tests(unittest.TestCase):
    def test_control_has_ten_unique_train_chord_signatures(self):
        sig=[chord_signature(build_template("chords",i)) for i in range(10)]
        self.assertEqual(len(set(sig)),10)

    def test_intervention_has_thirty_unique_voicings(self):
        sig=[chord_signature(intervention_chord_template(i)) for i in range(30)]
        self.assertEqual(len(set(sig)),30)
        for t in [intervention_chord_template(i) for i in range(30)]:
            self.assertEqual(len(t["segments"]),6)
            self.assertEqual(sorted(set(round(x["start"],2) for x in t["segments"])),[0.32,1.08])
            self.assertEqual(len(set(x["string"] for x in t["segments"][:3])),3)

    def test_paired_timbre_keys_repeat_exact_control_slot_pattern(self):
        keys=[]
        variants=[]
        for slot in range(30):
            base=slot//3; variant=slot%3
            keys.append(_seed(ROOT_SEED,"timbre",f"chords:{base:02d}",variant))
            variants.append(variant)
        self.assertEqual(variants.count(0),10); self.assertEqual(variants.count(1),10); self.assertEqual(variants.count(2),10)
        self.assertEqual(len(set(keys)),30)

    def test_model_initialization_identical(self):
        a=initialize_arm(960,True); b=initialize_arm(960,True)
        self.assertEqual(module_sha(a),module_sha(b))
        x=torch.randn((8,960),generator=torch.Generator().manual_seed(9))
        with torch.no_grad():
            asl,aol=a(x); bsl,bol=b(x)
        self.assertTrue(torch.equal(asl,bsl)); self.assertTrue(torch.equal(aol,bol))

if __name__=="__main__": unittest.main()
