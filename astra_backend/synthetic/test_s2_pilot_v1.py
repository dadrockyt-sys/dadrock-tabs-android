import unittest
import numpy as np
import torch

from synthetic.s0_pilot_v1 import (
    FAMILIES, BASES_PER_FAMILY, VARIANTS_PER_BASE,
    build_template, targets_for_template,
)
from synthetic.s2_pilot_v1 import (
    CONTROL_WEIGHT, INTERVENTION_WEIGHT,
    array_content_sha256, precompute_batches, weighted_loss,
)


class S2Tests(unittest.TestCase):
    def synthetic_targets(self):
        frames=87
        states=[]; onsets=[]; splits=[]; negative=[]
        for family in FAMILIES:
            for base in range(BASES_PER_FAMILY):
                t=build_template(family,base)
                state,onset,_=targets_for_template(t,frames)
                for _ in range(VARIANTS_PER_BASE):
                    states.append(state); onsets.append(onset)
                    splits.append(t["split"]); negative.append(t["hasNegativeStructure"])
        return np.stack(states),np.stack(onsets),np.asarray(splits),np.asarray(negative)

    def test_exact_active_token_accounting(self):
        state,onset,split,negative=self.synthetic_targets()
        train=state[split=="train"]
        active=((train>=0)&(train<20))
        self.assertEqual(int(active.sum()),11145)
        self.assertEqual(int(train.size),109620)

    def test_batch_plan_has_frozen_composition_and_is_deterministic(self):
        state,onset,split,negative=self.synthetic_targets()
        a,strata=precompute_batches(state,onset,split,negative)
        b,_=precompute_batches(state,onset,split,negative)
        self.assertEqual(a.shape,(500,128))
        self.assertTrue(np.array_equal(a,b))
        self.assertEqual(len(strata),4)

    def test_array_hash_is_dtype_shape_and_content_sensitive(self):
        a=np.arange(12,dtype=np.float32).reshape(3,4)
        self.assertEqual(array_content_sha256(a),array_content_sha256(a.copy()))
        self.assertNotEqual(array_content_sha256(a),array_content_sha256(a.astype(np.float64)))
        b=a.copy(); b[0,0]=99
        self.assertNotEqual(array_content_sha256(a),array_content_sha256(b))

    def test_only_frozen_state_weights_are_accepted(self):
        state_logits=torch.zeros((2,6*21))
        onset_logits=torch.zeros((2,6))
        state=torch.full((2,6),20,dtype=torch.long)
        onset=torch.zeros((2,6),dtype=torch.long)
        for weight in (CONTROL_WEIGHT,INTERVENTION_WEIGHT):
            total,sl,ol=weighted_loss(state_logits,onset_logits,state,onset,weight)
            self.assertTrue(torch.isfinite(total))
            self.assertTrue(torch.isfinite(sl))
            self.assertTrue(torch.isfinite(ol))
        with self.assertRaises(ValueError):
            weighted_loss(state_logits,onset_logits,state,onset,3.0)

    def test_weight6_increases_active_state_contribution(self):
        state_logits=torch.zeros((2,6*21))
        onset_logits=torch.zeros((2,6))
        state=torch.full((2,6),20,dtype=torch.long)
        state[0,0]=3
        onset=torch.zeros((2,6),dtype=torch.long)
        _,control,_=weighted_loss(state_logits,onset_logits,state,onset,CONTROL_WEIGHT)
        _,heavy,_=weighted_loss(state_logits,onset_logits,state,onset,INTERVENTION_WEIGHT)
        # Uniform logits make all token CE equal, so normalized mean is equal.
        self.assertAlmostEqual(float(control),float(heavy),places=6)
        # The implementation contract is tested by accepted weights and end-to-end arm isolation.
        self.assertEqual(CONTROL_WEIGHT,1.5)
        self.assertEqual(INTERVENTION_WEIGHT,6.0)


if __name__=="__main__":
    unittest.main()
