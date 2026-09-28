import math
import unittest

from evaluation.evaluation_protocol_v2 import *


class EvaluationProtocolV2Tests(unittest.TestCase):
    def test_boundary_eligibility_is_symmetric_and_reasoned(self):
        ev = crop_source_events([
            ("carryin", -0.2, 0.2, 40),
            ("inside", 0.1, 0.4, 41),
            ("carryout", 0.8, 1.2, 42),
        ], 0.0, 1.0)
        by = {e.id: e for e in ev}
        self.assertTrue(by["carryin"].carry_in)
        self.assertFalse(by["carryin"].onset_eligible)
        self.assertTrue(by["carryout"].onset_eligible)
        self.assertFalse(by["carryout"].offset_eligible)
        s = score_pitch_events_v2(ev, ev)
        self.assertEqual(s["pitchOnset"]["truePositive"], 2)
        self.assertEqual(s["pitchOnsetOffset"]["truePositive"], 1)
        self.assertEqual(s["eligibility"]["predictionOnsetExcludedCarryIn"], 1)
        self.assertEqual(s["eligibility"]["predictionOffsetExcludedCarryOut"], 1)

    def test_greedy_counterexample_gets_maximum_cardinality(self):
        refs = crop_source_events([
            ("r0", 0.00, .2, 60),
            ("r1", 0.05, .25, 60),
        ], 0, 1)
        preds = crop_source_events([
            ("p0", 0.04, .2, 60),
            ("p1", 0.09, .25, 60),
        ], 0, 1)
        s = score_pitch_events_v2(preds, refs)["pitchOnset"]
        self.assertEqual(s["truePositive"], 2)
        self.assertEqual(s["falseNegative"], 0)

    def test_matching_is_permutation_invariant(self):
        refs = crop_source_events([
            ("r0", 0.00, .2, 60),
            ("r1", 0.05, .25, 60),
        ], 0, 1)
        preds = crop_source_events([
            ("p0", 0.04, .2, 60),
            ("p1", 0.09, .25, 60),
        ], 0, 1)
        a = score_pitch_events_v2(preds, refs)["pitchOnset"]
        b = score_pitch_events_v2(
            list(reversed(preds)), list(reversed(refs))
        )["pitchOnset"]
        self.assertEqual(
            (a["truePositive"], a["falsePositive"], a["falseNegative"]), (2, 0, 0)
        )
        self.assertEqual(
            (b["truePositive"], b["falsePositive"], b["falseNegative"]), (2, 0, 0)
        )

    def test_exact_tolerance_boundary_is_inclusive(self):
        refs = crop_source_events([("r", 0.10, .40, 64)], 0, 1)
        preds = crop_source_events([("p", 0.15, .45, 64)], 0, 1)
        s = score_pitch_events_v2(preds, refs)
        self.assertEqual(s["pitchOnset"]["truePositive"], 1)
        self.assertEqual(s["pitchOnsetOffset"]["truePositive"], 1)

    def test_onset_and_offset_ambiguity_policies_are_distinct(self):
        refs = crop_source_events([
            ("a", .1, .4, 45),
            ("b", .1, .6, 45),
        ], 0, 1)
        preds = crop_source_events([("p", .1, .4, 45)], 0, 1)
        s = score_pitch_events_v2(preds, refs)
        self.assertEqual(s["pitchOnset"]["referenceCount"], 1)
        self.assertEqual(s["pitchOnsetOffset"]["referenceCount"], 2)
        self.assertEqual(s["pitchOnsetOffset"]["falseNegative"], 1)

    def test_nonfinite_and_fractional_pitch_are_rejected(self):
        with self.assertRaises(ValueError):
            crop_source_events([(0, math.nan, 40)], 0, 1)
        with self.assertRaises(ValueError):
            crop_source_events([(0, .2, 40.5)], 0, 1)

    def test_manifest_binding_rejects_crop_or_target_drift(self):
        meta = {
            "captureKey": "P1|x",
            "captureView": "directinput",
            "performer": "P1",
            "audioSourceSha256": "a",
            "midiSourceSha256": "m",
            "featureSha256": "f",
            "prepared": {
                "sourceEventSha256": "s",
                "targetSha256": "t",
                "unresolvedLabelCount": 0,
                "crop": {"startFrame": 10, "frames": 200, "hopSeconds": 0.01},
            },
        }
        manifest = {
            "captureKey": "P1|x",
            "captureView": "directinput",
            "performer": "P1",
            "audioSourceSha256": "a",
            "midiSourceSha256": "m",
            "featureSha256": "f",
            "sourceEventSha256": "s",
            "targetSha256": "t",
            "cropStartFrame": 10,
            "cropFrames": 200,
            "cropHopSeconds": 0.01,
            "unresolvedLabelCount": 0,
        }
        self.assertTrue(validate_manifest_binding(meta, manifest))
        bad = dict(manifest)
        bad["targetSha256"] = "changed"
        with self.assertRaises(RuntimeError):
            validate_manifest_binding(meta, bad)
        bad = dict(manifest)
        bad["cropStartFrame"] = 11
        with self.assertRaises(RuntimeError):
            validate_manifest_binding(meta, bad)


if __name__ == "__main__":
    unittest.main()
