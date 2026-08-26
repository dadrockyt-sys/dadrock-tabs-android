from __future__ import annotations

from pathlib import Path
import sys
import unittest

MODAL_DIR = Path(__file__).resolve().parents[1]
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

from v144_rhythm_conjunction_prune_policy import (  # noqa: E402
    apply_conjunction_prune,
    conjunction_pairs,
    event_matches_conjunction,
    rank_fit_conjunctions,
)


def row(measure: int, step: int, midi: int, *, fret: int = 0, string_index: int = 0):
    return {
        "measure": measure,
        "step": step,
        "midi": midi,
        "fret": fret,
        "stringIndex": string_index,
        "durationSteps": 1,
        "eventIndex": measure * 100 + step + midi,
        "techniques": [],
    }


class ConjunctionPrunePolicyTests(unittest.TestCase):
    def test_pairs_are_deterministic_and_unique(self):
        pairs = conjunction_pairs(row(1, 0, 71))
        self.assertEqual(pairs, conjunction_pairs(row(1, 0, 71)))
        self.assertEqual(len(pairs), len(set(pairs)))
        self.assertTrue(all(left < right for left, right in pairs))

    def test_runtime_match_needs_both_signatures(self):
        event = row(1, 0, 71)
        self.assertTrue(
            event_matches_conjunction(event, ["pitchClass::11", "register::high"])
        )
        self.assertFalse(
            event_matches_conjunction(event, ["pitchClass::11", "stepParity::1"])
        )

    def test_runtime_prune_is_reference_free_event_transform(self):
        events = [row(1, 0, 71), row(1, 1, 71), row(1, 0, 64)]
        kept = apply_conjunction_prune(
            events, ["pitchClass::11", "stepParity::0"]
        )
        self.assertEqual(len(kept), 2)
        self.assertEqual([event["midi"] for event in kept], [71, 64])

    def test_rank_uses_only_rows_supplied_as_fit_inputs(self):
        fit_generated = [
            row(1, 0, 71),
            row(1, 0, 71),
            row(2, 0, 71),
            row(2, 1, 64),
        ]
        fit_unmatched = [fit_generated[0], fit_generated[1], fit_generated[2]]
        ranked = rank_fit_conjunctions(
            fit_unmatched,
            fit_generated,
            minimum_false_positive_support=2,
            maximum_candidates=20,
        )
        self.assertTrue(ranked)
        for item in ranked:
            self.assertGreaterEqual(item["fitFalsePositiveSupport"], 2)
            self.assertGreaterEqual(
                item["fitTotalGeneratedSupport"], item["fitFalsePositiveSupport"]
            )
            self.assertGreaterEqual(item["fitFalsePositivePrecision"], 0.0)
            self.assertLessEqual(item["fitFalsePositivePrecision"], 1.0)

    def test_rank_is_independent_of_unprovided_later_stage_data(self):
        fit_generated = [row(1, 0, 71), row(1, 0, 71), row(2, 0, 71)]
        fit_unmatched = list(fit_generated)
        first = rank_fit_conjunctions(
            fit_unmatched,
            fit_generated,
            minimum_false_positive_support=2,
            maximum_candidates=10,
        )
        # There is intentionally no API parameter for validation/canary rows.
        second = rank_fit_conjunctions(
            list(fit_unmatched),
            list(fit_generated),
            minimum_false_positive_support=2,
            maximum_candidates=10,
        )
        self.assertEqual(first, second)

    def test_candidate_cap_and_order_are_stable(self):
        fit_generated = [row(measure, step, 71 + (step % 2)) for measure in range(1, 8) for step in range(4)]
        ranked = rank_fit_conjunctions(
            fit_generated,
            fit_generated,
            minimum_false_positive_support=1,
            maximum_candidates=5,
        )
        self.assertEqual(len(ranked), 5)
        ordered = sorted(
            ranked,
            key=lambda item: (
                -float(item["fitFalsePositivePrecision"]),
                -int(item["fitFalsePositiveSupport"]),
                int(item["fitTotalGeneratedSupport"]),
                tuple(item["signatures"]),
            ),
        )
        self.assertEqual(ranked, ordered)

    def test_invalid_duplicate_rule_is_rejected(self):
        with self.assertRaises(ValueError):
            event_matches_conjunction(row(1, 0, 71), ["pitchClass::11", "pitchClass::11"])


if __name__ == "__main__":
    unittest.main()
