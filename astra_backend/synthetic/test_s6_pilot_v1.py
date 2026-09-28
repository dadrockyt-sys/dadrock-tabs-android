import unittest
import numpy as np
import torch
from synthetic.s0_pilot_v1 import FAMILIES,BASES_PER_FAMILY,VARIANTS_PER_BASE,build_template,targets_for_template,context5
from synthetic.s6_pilot_v1 import initialize_arm,module_sha,parameter_count,precompute_batches

class S6Tests(unittest.TestCase):
    def test_common_initialization_and_onset_logits_match(self):
        a=initialize_arm(960,False); b=initialize_arm(960,True)
        self.assertEqual(module_sha(a.encoder),module_sha(b.encoder))
        self.assertEqual(module_sha(a.onset_head),module_sha(b.onset_head))
        x=torch.zeros((8,960))
        with torch.no_grad():
            _,ao=a(x); _,bo=b(x)
        self.assertTrue(torch.equal(ao,bo))

    def test_state_head_architecture_and_parameter_counts_differ(self):
        a=initialize_arm(960,False); b=initialize_arm(960,True)
        self.assertLess(parameter_count(a.state_head),parameter_count(b.state_head))
        self.assertEqual(parameter_count(a.onset_head),parameter_count(b.onset_head))
        self.assertEqual(parameter_count(a.encoder),parameter_count(b.encoder))

    def test_batch_plan_deterministic(self):
        states=[]; onsets=[]; splits=[]; neg=[]
        for fam in FAMILIES:
            for base in range(BASES_PER_FAMILY):
                t=build_template(fam,base); s,o,_=targets_for_template(t,87)
                for _ in range(VARIANTS_PER_BASE):
                    states.append(s); onsets.append(o); splits.append(t["split"]); neg.append(t["hasNegativeStructure"])
        a,_=precompute_batches(np.stack(states),np.stack(onsets),np.asarray(splits),np.asarray(neg))
        b,_=precompute_batches(np.stack(states),np.stack(onsets),np.asarray(splits),np.asarray(neg))
        self.assertEqual(a.shape,(500,128)); self.assertTrue(np.array_equal(a,b))

if __name__=="__main__": unittest.main()
