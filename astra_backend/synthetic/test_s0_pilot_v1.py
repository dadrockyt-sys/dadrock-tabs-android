import unittest
import numpy as np

from synthetic.s0_pilot_v1 import (
    FAMILIES, BASES_PER_FAMILY, VARIANTS_PER_BASE, EXAMPLES, AUDIO_SECONDS,
    MAX_EXAMPLES, MAX_AUDIO_SECONDS, build_template, split_for_base,
    render_waveform, targets_for_template, context5, OUTPUT_SR,
)


class S0PilotTests(unittest.TestCase):
    def test_frozen_ceiling_and_grouped_split(self):
        self.assertEqual(EXAMPLES,294)
        self.assertEqual(AUDIO_SECONDS,588.0)
        self.assertLessEqual(EXAMPLES,MAX_EXAMPLES)
        self.assertLessEqual(AUDIO_SECONDS,MAX_AUDIO_SECONDS)
        self.assertEqual([split_for_base(i) for i in (0,9,10,11,12,13)],
                         ["train","train","validation","validation","test","test"])

    def test_all_variants_of_template_share_split(self):
        for family in FAMILIES:
            for base in range(BASES_PER_FAMILY):
                t=build_template(family,base)
                self.assertEqual(t["split"],split_for_base(base))
                self.assertTrue(all(build_template(family,base)["templateId"]==t["templateId"]
                                    for _ in range(VARIANTS_PER_BASE)))

    def test_waveform_is_finite_and_exact_length(self):
        t=build_template("repeated",0)
        y=render_waveform(t,0)
        self.assertEqual(len(y),int(round(2.0*OUTPUT_SR)))
        self.assertTrue(np.isfinite(y).all())
        self.assertGreater(float(np.max(np.abs(y))),0)

    def test_repeated_targets_have_multiple_attacks(self):
        t=build_template("repeated",1)
        state,onset,refs=targets_for_template(t,87)
        self.assertEqual(len(refs),4)
        self.assertEqual(int(onset.sum()),4)
        self.assertEqual(state.shape,(6,87))

    def test_negative_only_mixed_has_no_pitch_reference(self):
        t=build_template("mixed",12)
        self.assertTrue(t["negativeOnly"])
        state,onset,refs=targets_for_template(t,87)
        self.assertEqual(refs,[])
        self.assertEqual(int(onset.sum()),0)
        self.assertTrue(np.all(state==-1))

    def test_context_shape(self):
        x=np.zeros((2,7,192),dtype=np.float32)
        self.assertEqual(context5(x).shape,(2,7,960))


if __name__=="__main__":
    unittest.main()
