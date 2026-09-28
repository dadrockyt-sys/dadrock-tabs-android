import unittest
import numpy as np
import torch
from synthetic.s0_pilot_v1 import FAMILIES,BASES_PER_FAMILY,VARIANTS_PER_BASE,build_template,targets_for_template
from synthetic.s11_pilot_v1 import RUN_SEEDS,initialize_model,module_sha,paired_batches

class S11Tests(unittest.TestCase):
    def targets(self):
        states=[]; onsets=[]; splits=[]; neg=[]
        for fam in FAMILIES:
            for base in range(BASES_PER_FAMILY):
                t=build_template(fam,base); s,o,_=targets_for_template(t,87)
                for _ in range(VARIANTS_PER_BASE):
                    states.append(s); onsets.append(o); splits.append(t["split"]); neg.append(t["hasNegativeStructure"])
        return np.stack(states),np.stack(onsets),np.asarray(splits),np.asarray(neg)

    def test_three_frozen_seeds(self):
        self.assertEqual(RUN_SEEDS,(20260927,20260928,20260929))

    def test_pair_init_same_within_seed_distinct_across_seeds(self):
        hashes=[]
        for s in RUN_SEEDS:
            a=initialize_model(s,960); b=initialize_model(s,960)
            self.assertEqual(module_sha(a),module_sha(b))
            hashes.append(module_sha(a))
        self.assertEqual(len(set(hashes)),3)

    def test_batches_same_within_seed_distinct_across_seeds(self):
        state,onset,split,neg=self.targets()
        hashes=[]
        for s in RUN_SEEDS:
            a,_=paired_batches(state,onset,split,neg,s)
            b,_=paired_batches(state,onset,split,neg,s)
            self.assertTrue(np.array_equal(a,b)); self.assertEqual(a.shape,(500,128))
            hashes.append(a.tobytes())
        self.assertEqual(len(set(hashes)),3)

if __name__=="__main__": unittest.main()
