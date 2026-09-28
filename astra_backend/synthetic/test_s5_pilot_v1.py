import unittest
import numpy as np
import torch

from synthetic.s0_pilot_v1 import (
    FAMILIES, BASES_PER_FAMILY, VARIANTS_PER_BASE,
    build_template, targets_for_template, context5, FrameModel,
)
from synthetic.s5_pilot_v1 import (
    CONTROL_STATE_WEIGHT, INTERVENTION_STATE_WEIGHT,
    weighted_loss, precompute_batches, _set_determinism,
)


class S5Tests(unittest.TestCase):
    def synthetic_targets(self):
        states=[]; onsets=[]; splits=[]; neg=[]
        for fam in FAMILIES:
            for base in range(BASES_PER_FAMILY):
                t=build_template(fam,base)
                s,o,_=targets_for_template(t,87)
                for _ in range(VARIANTS_PER_BASE):
                    states.append(s); onsets.append(o); splits.append(t["split"]); neg.append(t["hasNegativeStructure"])
        return np.stack(states),np.stack(onsets),np.asarray(splits),np.asarray(neg)

    def test_only_frozen_state_weights_are_accepted(self):
        sl=torch.zeros((2,6*21)); ol=torch.zeros((2,6))
        st=torch.full((2,6),20,dtype=torch.long); st[0,0]=3
        ot=torch.zeros((2,6),dtype=torch.long); ot[0,0]=1
        for w in (CONTROL_STATE_WEIGHT,INTERVENTION_STATE_WEIGHT):
            total,state_loss,onset_loss=weighted_loss(sl,ol,st,ot,w)
            self.assertTrue(torch.isfinite(total))
            self.assertTrue(torch.isfinite(state_loss))
            self.assertTrue(torch.isfinite(onset_loss))
        with self.assertRaises(ValueError):
            weighted_loss(sl,ol,st,ot,7.5)

    def test_weight9_increases_active_state_gradient_pressure(self):
        sl6=torch.zeros((1,6*21),requires_grad=True)
        sl9=torch.zeros((1,6*21),requires_grad=True)
        ol=torch.zeros((1,6),requires_grad=True)
        st=torch.full((1,6),20,dtype=torch.long); st[0,0]=3
        ot=torch.zeros((1,6),dtype=torch.long)
        _,s6,_=weighted_loss(sl6,ol,st,ot,CONTROL_STATE_WEIGHT)
        _,s9,_=weighted_loss(sl9,ol,st,ot,INTERVENTION_STATE_WEIGHT)
        s6.backward(retain_graph=True); s9.backward()
        g6=float(sl6.grad[0,3].abs()); g9=float(sl9.grad[0,3].abs())
        self.assertGreater(g9,g6)

    def test_batch_plan_is_deterministic(self):
        state,onset,split,neg=self.synthetic_targets()
        a,_=precompute_batches(state,onset,split,neg)
        b,_=precompute_batches(state,onset,split,neg)
        self.assertEqual(a.shape,(500,128))
        self.assertTrue(np.array_equal(a,b))

    def test_identical_initialization_and_forward(self):
        _set_determinism(); a=FrameModel(960)
        _set_determinism(); b=FrameModel(960)
        x=torch.zeros((4,960))
        with torch.no_grad():
            asl,aol=a(x); bsl,bol=b(x)
        self.assertTrue(torch.equal(asl,bsl))
        self.assertTrue(torch.equal(aol,bol))


if __name__=="__main__":
    unittest.main()
