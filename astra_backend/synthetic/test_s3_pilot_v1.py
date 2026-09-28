import unittest
import numpy as np
import torch

from synthetic.s0_pilot_v1 import (
    FAMILIES, BASES_PER_FAMILY, VARIANTS_PER_BASE,
    build_template, targets_for_template,
)
from synthetic.s3_pilot_v1 import (
    CONTROL_POS_WEIGHT, INTERVENTION_POS_WEIGHT,
    s3_loss, precompute_batches,
)


class S3Tests(unittest.TestCase):
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

    def test_exact_positive_onset_accounting(self):
        state,onset,split,negative=self.synthetic_targets()
        train=split=="train"
        self.assertEqual(int(onset[train].sum()),645)
        self.assertEqual(int((onset[train]==1).any(axis=1).sum()),525)

    def test_batch_plan_is_identical_and_deterministic(self):
        state,onset,split,negative=self.synthetic_targets()
        a,strata=precompute_batches(state,onset,split,negative)
        b,_=precompute_batches(state,onset,split,negative)
        self.assertEqual(a.shape,(500,128))
        self.assertTrue(np.array_equal(a,b))
        self.assertEqual(set(strata),{
            "positiveOnset","activeNonOnset","negativeStructureInactive","otherInactive"
        })

    def test_only_frozen_onset_weights_are_accepted(self):
        state_logits=torch.zeros((2,6*21))
        onset_logits=torch.zeros((2,6))
        state=torch.full((2,6),20,dtype=torch.long)
        onset=torch.zeros((2,6),dtype=torch.long)
        onset[0,0]=1
        for weight in (CONTROL_POS_WEIGHT,INTERVENTION_POS_WEIGHT):
            total,sl,ol=s3_loss(state_logits,onset_logits,state,onset,weight)
            self.assertTrue(torch.isfinite(total))
            self.assertTrue(torch.isfinite(sl))
            self.assertTrue(torch.isfinite(ol))
        with self.assertRaises(ValueError):
            s3_loss(state_logits,onset_logits,state,onset,12.0)

    def test_weight16_increases_positive_onset_bce(self):
        state_logits=torch.zeros((1,6*21))
        onset_logits=torch.zeros((1,6))
        state=torch.full((1,6),20,dtype=torch.long)
        onset=torch.zeros((1,6),dtype=torch.long)
        onset[0,0]=1
        _,_,c=s3_loss(state_logits,onset_logits,state,onset,CONTROL_POS_WEIGHT)
        _,_,w=s3_loss(state_logits,onset_logits,state,onset,INTERVENTION_POS_WEIGHT)
        self.assertGreater(float(w),float(c))

    def test_repeated_family_has_repeated_reference_attacks(self):
        t=build_template("repeated",12)
        _,onset,refs=targets_for_template(t,87)
        self.assertEqual(len(refs),4)
        self.assertEqual(int(onset.sum()),4)


if __name__=="__main__":
    unittest.main()
