from __future__ import annotations

from pathlib import Path
import sys
import unittest

MODAL_DIR = Path(__file__).resolve().parents[1]
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

from v144_rhythm_measure_set_guard import (  # noqa: E402
    generated_measure_ids,
    measure_set_evidence,
)


def event(measure: int, step: int = 0):
    return {"measure": measure, "step": step}


class MeasureSetGuardTests(unittest.TestCase):
    def test_generated_measure_ids_are_sorted_and_unique(self):
        self.assertEqual(
            generated_measure_ids([event(3), event(1), event(3, 4), event(2)]),
            (1, 2, 3),
        )

    def test_exact_measure_set_is_preserved_even_when_event_count_changes(self):
        baseline = [event(1), event(1, 1), event(2), event(3)]
        candidate = [event(1), event(2), event(3), event(3, 2)]
        evidence = measure_set_evidence(baseline, candidate)
        self.assertTrue(evidence["baselineGeneratedMeasureSetPreserved"])
        self.assertEqual(evidence["missingBaselineGeneratedMeasures"], [])
        self.assertEqual(evidence["extraCandidateGeneratedMeasures"], [])
        self.assertFalse(evidence["professionalReferenceUsed"])

    def test_dropping_last_event_of_measure_fails_preservation(self):
        baseline = [event(1), event(2), event(3)]
        candidate = [event(1), event(3)]
        evidence = measure_set_evidence(baseline, candidate)
        self.assertFalse(evidence["baselineGeneratedMeasureSetPreserved"])
        self.assertEqual(evidence["missingBaselineGeneratedMeasures"], [2])
        self.assertEqual(evidence["candidateGeneratedMeasureCount"], 2)

    def test_extra_measure_also_fails_exact_set_preservation(self):
        baseline = [event(1), event(2)]
        candidate = [event(1), event(2), event(3)]
        evidence = measure_set_evidence(baseline, candidate)
        self.assertFalse(evidence["baselineGeneratedMeasureSetPreserved"])
        self.assertEqual(evidence["extraCandidateGeneratedMeasures"], [3])

    def test_invalid_or_empty_stream_is_rejected(self):
        with self.assertRaises(ValueError):
            generated_measure_ids([])
        with self.assertRaises(ValueError):
            generated_measure_ids([event(0)])


if __name__ == "__main__":
    unittest.main()
