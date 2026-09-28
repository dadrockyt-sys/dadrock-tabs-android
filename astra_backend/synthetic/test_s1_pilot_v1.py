import unittest
import numpy as np

from synthetic.s0_pilot_v1 import (
    EXAMPLES, BASES_PER_FAMILY, VARIANTS_PER_BASE, FAMILIES,
    build_template, targets_for_template,
)
from synthetic.s1_pilot_v1 import build_sampling_strata


class S1SamplingTests(unittest.TestCase):
    def synthetic_targets(self):
        frames=87
        states=[]; onsets=[]; splits=[]; negative=[]
        for family in FAMILIES:
            for base in range(BASES_PER_FAMILY):
                t=build_template(family,base)
                state,onset,_=targets_for_template(t,frames)
                for _variant in range(VARIANTS_PER_BASE):
                    states.append(state); onsets.append(onset)
                    splits.append(t["split"])
                    negative.append(t["hasNegativeStructure"])
        return np.stack(states),np.stack(onsets),np.asarray(splits),np.asarray(negative)

    def test_frozen_positive_accounting(self):
        state,onset,split,negative=self.synthetic_targets()
        self.assertEqual(len(state),EXAMPLES)
        train=split=="train"
        self.assertEqual(int(onset[train].sum()),645)
        onset_frames=int((onset[train]==1).any(axis=1).sum())
        self.assertEqual(onset_frames,525)

    def test_strata_exist_and_are_disjoint(self):
        state,onset,split,negative=self.synthetic_targets()
        s=build_sampling_strata(state,onset,split,negative)
        self.assertEqual(set(s),{
            "positiveOnset","activeNonOnset","negativeStructureInactive","otherInactive"
        })
        self.assertTrue(all(len(v)>0 for v in s.values()))
        seen=set()
        for values in s.values():
            ids=set(map(int,values))
            self.assertTrue(seen.isdisjoint(ids))
            seen |= ids

    def test_positive_stratum_matches_attack_frame_count(self):
        state,onset,split,negative=self.synthetic_targets()
        s=build_sampling_strata(state,onset,split,negative)
        self.assertEqual(len(s["positiveOnset"]),525)

    def test_nontrain_frames_never_enter_strata(self):
        state,onset,split,negative=self.synthetic_targets()
        s=build_sampling_strata(state,onset,split,negative)
        frames=state.shape[2]
        for values in s.values():
            clips=np.asarray(values)//frames
            self.assertTrue(np.all(split[clips]=="train"))

    def test_empty_stratum_fails_closed(self):
        state=np.full((1,6,3),-1,dtype=np.int16)
        onset=np.zeros_like(state)
        split=np.asarray(["train"])
        negative=np.asarray([False])
        with self.assertRaises(RuntimeError):
            build_sampling_strata(state,onset,split,negative)


if __name__=="__main__":
    unittest.main()
