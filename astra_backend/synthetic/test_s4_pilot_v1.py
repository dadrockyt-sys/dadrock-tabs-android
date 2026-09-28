import unittest
import numpy as np
import torch
from synthetic.s0_pilot_v1 import build_template, targets_for_template, context5, FrameModel
from synthetic.s4_pilot_v1 import (
    _set_determinism, forward_arm, gradient_contract, precompute_batches
)

class S4Tests(unittest.TestCase):
    def fixture(self):
        t=build_template("repeated",0)
        state,onset,_=targets_for_template(t,87)
        features=np.zeros((1,87,192),dtype=np.float32)
        return features,state[None],onset[None]

    def test_forward_identity_before_update(self):
        features,state,onset=self.fixture()
        x=torch.from_numpy(context5(features).reshape(-1,960)).float()
        _set_determinism(); a=FrameModel(960)
        _set_determinism(); b=FrameModel(960)
        with torch.no_grad():
            asl,aol=forward_arm(a,x,False); bsl,bol=forward_arm(b,x,True)
        self.assertTrue(torch.equal(asl,bsl))
        self.assertTrue(torch.equal(aol,bol))

    def test_gradient_contract(self):
        features,state,onset=self.fixture()
        x=torch.from_numpy(context5(features).reshape(-1,960)).float()
        s=torch.from_numpy(state.transpose(0,2,1).reshape(-1,6)).long()
        o=torch.from_numpy(onset.transpose(0,2,1).reshape(-1,6)).long()
        _set_determinism(); a=FrameModel(960)
        _set_determinism(); b=FrameModel(960)
        ga=gradient_contract(a,x,s,o,False); gb=gradient_contract(b,x,s,o,True)
        self.assertGreater(ga["onsetEncoderGradNorm"],0)
        self.assertGreater(ga["onsetHeadGradNorm"],0)
        self.assertEqual(gb["onsetEncoderGradNorm"],0)
        self.assertGreater(gb["onsetHeadGradNorm"],0)
        self.assertAlmostEqual(ga["stateEncoderGradNorm"],gb["stateEncoderGradNorm"],places=12)

    def test_batch_plan_deterministic(self):
        states=[]; onsets=[]; splits=[]; neg=[]
        for fam in ("isolated","scales","chords","repeated","legato","palmmute","mixed"):
            for base in range(14):
                t=build_template(fam,base); s,o,_=targets_for_template(t,87)
                for _ in range(3):
                    states.append(s); onsets.append(o); splits.append(t["split"]); neg.append(t["hasNegativeStructure"])
        a,_=precompute_batches(np.stack(states),np.stack(onsets),np.asarray(splits),np.asarray(neg))
        b,_=precompute_batches(np.stack(states),np.stack(onsets),np.asarray(splits),np.asarray(neg))
        self.assertEqual(a.shape,(500,128)); self.assertTrue(np.array_equal(a,b))

if __name__=="__main__": unittest.main()
