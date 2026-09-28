import unittest
import numpy as np
import torch
from synthetic.s0_pilot_v1 import FAMILIES,BASES_PER_FAMILY,VARIANTS_PER_BASE,build_template,targets_for_template
from synthetic.s6_pilot_v1 import initialize_arm,module_sha
from synthetic.s8_pilot_v1 import build_paired_batch_plans,positive_multiplicity

class S8Tests(unittest.TestCase):
    def targets(self):
        states=[]; onsets=[]; splits=[]; neg=[]
        for fam in FAMILIES:
            for base in range(BASES_PER_FAMILY):
                t=build_template(fam,base); s,o,_=targets_for_template(t,87)
                for _ in range(VARIANTS_PER_BASE):
                    states.append(s); onsets.append(o); splits.append(t["split"]); neg.append(t["hasNegativeStructure"])
        return np.stack(states),np.stack(onsets),np.asarray(splits),np.asarray(neg)

    def test_frozen_positive_accounting(self):
        state,onset,split,neg=self.targets()
        c,w,m,_,a=build_paired_batch_plans(state,onset,split,neg)
        self.assertEqual(a["positiveFrames"],525)
        self.assertEqual(a["positiveStringTokens"],645)
        self.assertEqual(a["sumMultiplicitySquared"],1005)
        self.assertAlmostEqual(a["uniformExpectedPositiveStringsPerFrame"],645/525,places=12)
        self.assertAlmostEqual(a["weightedExpectedPositiveStringsPerFrame"],1005/645,places=12)

    def test_nonpositive_positions_are_pairwise_identical(self):
        state,onset,split,neg=self.targets()
        c,w,m,_,_=build_paired_batch_plans(state,onset,split,neg)
        self.assertEqual(c.shape,(500,128)); self.assertTrue(np.array_equal(c[~m],w[~m]))

    def test_weighted_plan_increases_sampled_multiplicity(self):
        state,onset,split,neg=self.targets()
        c,w,m,_,_=build_paired_batch_plans(state,onset,split,neg)
        mult=positive_multiplicity(onset)
        self.assertGreater(float(mult[w[m]].mean()),float(mult[c[m]].mean()))

    def test_model_initialization_and_logits_identical(self):
        a=initialize_arm(960,True); b=initialize_arm(960,True)
        self.assertEqual(module_sha(a),module_sha(b))
        x=torch.randn((8,960),generator=torch.Generator().manual_seed(8))
        with torch.no_grad():
            asl,aol=a(x); bsl,bol=b(x)
        self.assertTrue(torch.equal(asl,bsl)); self.assertTrue(torch.equal(aol,bol))

if __name__=="__main__": unittest.main()
