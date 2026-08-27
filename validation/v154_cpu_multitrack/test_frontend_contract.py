#!/usr/bin/env python3
from __future__ import annotations

import unittest

from validation.v154_cpu_multitrack import score_frontend_reference as scorer
from validation.v154_cpu_multitrack import transcribe_broad_other as transcriber


class FrontendScorerTests(unittest.TestCase):
    def test_combined_guitar_ignores_rhythm_lead_role_labels(self) -> None:
        generated = [
            {"measure": 1, "step": 0.0, "midi": 64},
            {"measure": 1, "step": 4.25, "midi": 67},
        ]
        # The scorer receives the professional Rhythm+Lead union at this stage;
        # role identity is intentionally absent from the primary acoustic gate.
        reference_union = [
            {"measure": 1, "step": 0.2, "midi": 64},
            {"measure": 1, "step": 4.0, "midi": 67},
        ]
        report = scorer.score_stream(generated, reference_union)
        self.assertEqual(report["primaryTimingAwarePitch"]["matched"], 2)
        self.assertAlmostEqual(report["primaryTimingAwarePitch"]["f1"], 1.0)

    def test_primary_and_gross_tolerances_are_distinct(self) -> None:
        generated = [{"measure": 3, "step": 8.0, "midi": 52}]
        reference = [{"measure": 3, "step": 9.25, "midi": 52}]
        report = scorer.score_stream(generated, reference)
        self.assertEqual(report["primaryTimingAwarePitch"]["matched"], 0)
        self.assertEqual(report["grossTimingAwarePitch"]["matched"], 1)

    def test_uncertain_reference_event_can_be_excluded_without_repair(self) -> None:
        notes = [
            {"measure": 88, "step": 4.0, "midi": 40, "excludeFromScoring": True},
            {"measure": 88, "step": 8.0, "midi": 43},
        ]
        normalized = scorer.normalize_notes(notes, label="reference.bass")
        self.assertEqual(normalized, [{"measure": 88, "step": 8.0, "midi": 43}])

    def test_pitch_mismatch_never_matches_even_with_timing_tolerance(self) -> None:
        generated = [{"measure": 1, "step": 0.0, "midi": 60}]
        reference = [{"measure": 1, "step": 0.0, "midi": 61}]
        report = scorer.score_stream(generated, reference)
        self.assertEqual(report["grossTimingAwarePitch"]["matched"], 0)


class BroadOtherTranscriberHelperTests(unittest.TestCase):
    def test_stream_ranges_keep_bass_low_e(self) -> None:
        self.assertEqual(transcriber.STREAM_RANGES["combinedGuitar"], (40, 88))
        self.assertEqual(transcriber.STREAM_RANGES["bass"], (28, 67))

    def test_grid_location_preserves_continuous_step(self) -> None:
        measure, step, nearest = transcriber.grid_location(transcriber.STEP_SECONDS * 16.25)
        self.assertEqual(measure, 2)
        self.assertAlmostEqual(step, 0.25, places=9)
        self.assertEqual(nearest, 16)

    def test_json_safe_recurses_native_containers(self) -> None:
        value = {"a": [1, 2.5, {"b": True}], "c": None}
        self.assertEqual(transcriber.json_safe(value), value)


if __name__ == "__main__":
    unittest.main()
