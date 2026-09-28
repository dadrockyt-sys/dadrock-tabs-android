import unittest
import numpy as np
import torch
from synthetic.s0_pilot_v1 import FAMILIES,BASES_PER_FAMILY,VARIANTS_PER_BASE,build_template,targets_for_template
from synthetic.s7_pilot_v1 import initialize_arm,module_sha,residual_output_zero,precompute_batches

class S7Tests(unittest.TestCase):
    def test_exact_preupdate_identity(self):
        c=initialize_arm(960,False); r=initialize_arm(960,True)
        self.assertEqual(module_sha(c.encoder),module_sha(r.encoder))
        self.assertEqual(module_sha(c.onset_head),module_sha(r.onset_head))
        self.assertEqual(module_sha(c.base_state_head),module_sha(r.base_state_head))
        self.assertTrue(residual_output_zero(r))
        x=torch.randn((8,960),generator=torch.Generator().manual_seed(7))
        with torch.no_grad():
            cs,co=c(x); rs,ro=r(x)
        self.assertTrue(torch.equal(cs,rs))
        self.assertTrue(torch.equal(co,ro))

    def test_residual_branch_has_extra_parameters_but_zero_output_layer(self):
        c=initialize_arm(960,False); r=initialize_arm(960,True)
        self.assertGreater(sum(p.numel() for p in r.parameters()),sum(p.numel() for p in c.parameters()))
        self.assertTrue(residual_output_zero(r))
        self.assertGreater(torch.count_nonzero(r.residual_hidden.weight).item(),0)

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
