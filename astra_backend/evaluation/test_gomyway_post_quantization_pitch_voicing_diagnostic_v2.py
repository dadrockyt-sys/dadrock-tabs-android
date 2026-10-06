import math
import tempfile
import unittest
from pathlib import Path

import gomyway_post_quantization_pitch_voicing_diagnostic_v2 as d


def pred(i, start, midi):
    return {"id": f"p{i}", "start": start, "end": start + 0.2, "midi": midi}


def targ(i, start, midi, measure=1):
    return {"id": f"t{i}", "start": start, "midi": midi, "measure": measure, "step": 0.0}


class DiagnosticV2Tests(unittest.TestCase):
    def test_permuted_chord_ordering_does_not_change_group_overlap(self):
        preds_a = [pred(0, 1.0, 60), pred(1, 1.0, 64)]
        preds_b = [pred(1, 1.0, 64), pred(0, 1.0, 60)]
        targets = [targ(0, 1.0, 64), targ(1, 1.0, 60)]
        self.assertEqual(len(d.max_cardinality_min_time_match(preds_a, targets)), 2)
        self.assertEqual(len(d.max_cardinality_min_time_match(preds_b, targets)), 2)
        comps_a, _ = d.matching_components(preds_a, targets)
        comps_b, _ = d.matching_components(preds_b, targets)
        self.assertEqual(comps_a[0]["pairingInvariantPitchMultisetExactOverlap"], 2)
        self.assertEqual(comps_b[0]["pairingInvariantPitchMultisetExactOverlap"], 2)
        self.assertTrue(comps_a[0]["ambiguous"])

    def test_duplicate_notes_are_one_to_one(self):
        preds = [pred(0, 0.0, 60), pred(1, 0.0, 60)]
        targets = [targ(0, 0.0, 60)]
        rows = d.max_cardinality_min_time_match(preds, targets)
        self.assertEqual(len(rows), 1)
        self.assertEqual(len({r["predictionIndex"] for r in rows}), 1)
        self.assertEqual(len({r["targetIndex"] for r in rows}), 1)

    def test_greedy_cardinality_counterexample(self):
        preds = [pred(0, 0.00, 60), pred(1, 0.03, 62)]
        targets = [targ(0, 0.04, 60), targ(1, 0.08, 62)]
        self.assertEqual(len(d.legacy_greedy_match(preds, targets, 0.05)), 1)
        self.assertEqual(len(d.max_cardinality_min_time_match(preds, targets, 0.05)), 2)

    def test_exact_50ms_boundary_is_inclusive(self):
        rows = d.max_cardinality_min_time_match([pred(0, 0.0, 60)], [targ(0, 0.05, 60)], 0.05)
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0]["onsetErrorSeconds"], 0.05)

    def test_octave_and_other_buckets_are_disjoint(self):
        rows = [{"midiDelta": x} for x in (0, 12, -12, 24, -24, 1, -2, 4, 7)]
        s = d.delta_summary(rows)
        self.assertEqual(s["buckets"], {"exact": 1, "abs1": 1, "abs2": 1, "abs3to5": 1, "abs12": 2, "other": 3})
        self.assertEqual(s["pitchClassCorrectNonzeroOctaveError"], 4)

    def test_exclusions_and_final_endpoint(self):
        timing = {"measureBoundaries": [
            {"measureNumber": 1, "startSeconds": 0.0, "endSeconds": 1.0, "durationSeconds": 1.0},
            {"measureNumber": 2, "startSeconds": 1.0, "endSeconds": 2.0, "durationSeconds": 1.0},
        ]}
        self.assertEqual(d.classify_event_for_role({"start": 0.5}, timing, {1})["reason"], "excludedMeasure")
        self.assertEqual(d.classify_event_for_role({"start": 1.5}, timing, {1})["reason"], "eligible")
        self.assertEqual(d.classify_event_for_role({"start": 2.0}, timing, {1})["reason"], "atOrAfterFinalEndpoint")

    def test_empty_input(self):
        rows = d.max_cardinality_min_time_match([], [], 0.05)
        self.assertEqual(rows, [])
        self.assertIsNone(d.delta_summary(rows)["exactMidiRate"])

    def test_invalid_nonfinite_event_rejected(self):
        with self.assertRaises(RuntimeError):
            d.validate_events([{"id": "bad", "start": math.nan, "end": 1.0, "midi": 60}], "bad")

    def test_hash_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x"
            p.write_text("abc")
            with self.assertRaises(RuntimeError):
                d.verify_sha(p, "0" * 64, "fixture")

    def test_mutation_guard_rejects_midi_change(self):
        old_count = d.EXPECTED_EVENT_COUNT
        try:
            d.EXPECTED_EVENT_COUNT = 1
            old = [pred(0, 1.0, 60)]
            new = [dict(old[0], midi=61, originalStart=1.0)]
            with self.assertRaises(RuntimeError):
                d.validate_frozen_pair(old, new)
        finally:
            d.EXPECTED_EVENT_COUNT = old_count


if __name__ == "__main__":
    unittest.main()
