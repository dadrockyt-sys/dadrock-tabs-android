from __future__ import annotations

from pathlib import Path
import sys
import unittest

MODAL_DIR = Path(__file__).resolve().parents[1]
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

from v144_rhythm_triple_conjunction_policy import (  # noqa: E402
    apply_triple_prune,
    event_matches_triple,
    rank_fit_triples,
    triple_signatures,
)


def row(measure: int, step: int, midi: int):
    return {
        "measure": measure,
        "step": step,
        "midi": midi,
        "fret": 0,
        "stringIndex": 0,
        "durationSteps": 1,
        "eventIndex": measure * 1000 + step * 10 + midi,
        "techniques": [],
    }


class TripleConjunctionPolicyTests(unittest.TestCase):
    def test_triples_are_deterministic_unique_and_sorted(self):
        triples = triple_signatures(row(1, 0, 71))
        self.assertEqual(triples, triple_signatures(row(1, 0, 71)))
        self.assertEqual(len(triples), len(set(triples)))
        self.assertTrue(all(first < second < third for first, second, third in triples))

    def test_runtime_match_requires_all_three_signatures(self):
        event = row(1, 0, 71)
        self.assertTrue(
            event_matches_triple(
                event,
                ["pitchClass::11", "register::high", "stepParity::0"],
            )
        )
        self.assertFalse(
            event_matches_triple(
                event,
                ["pitchClass::11", "register::high", "stepParity::1"],
            )
        )

    def test_runtime_prune_is_reference_free_event_transform(self):
        events = [row(1, 0, 71), row(1, 1, 71), row(1, 0, 64)]
        kept = apply_triple_prune(
            events,
            ["pitchClass::11", "register::high", "stepParity::0"],
        )
        self.assertEqual(len(kept), 2)
        self.assertEqual([event["midi"] for event in kept], [71, 64])

    def test_rank_accepts_fit_inputs_only_and_is_stable(self):
        fit_generated = [
            row(1, 0, 71),
            row(1, 0, 71),
            row(2, 0, 71),
            row(2, 1, 64),
        ]
        fit_unmatched = fit_generated[:3]
        first = rank_fit_triples(
            fit_unmatched,
            fit_generated,
            minimum_false_positive_support=2,
            maximum_candidates=20,
        )
        second = rank_fit_triples(
            list(fit_unmatched),
            list(fit_generated),
            minimum_false_positive_support=2,
            maximum_candidates=20,
        )
        self.assertEqual(first, second)
        self.assertTrue(first)
        for item in first:
            self.assertEqual(len(item["signatures"]), 3)
            self.assertGreaterEqual(item["fitFalsePositiveSupport"], 2)
            self.assertGreaterEqual(
                item["fitTotalGeneratedSupport"], item["fitFalsePositiveSupport"]
            )

    def test_candidate_cap_and_order_are_deterministic(self):
        fit_generated = [
            row(measure, step, 71 + (step % 2))
            for measure in range(1, 9)
            for step in range(4)
        ]
        ranked = rank_fit_triples(
            fit_generated,
            fit_generated,
            minimum_false_positive_support=1,
            maximum_candidates=7,
        )
        self.assertEqual(len(ranked), 7)
        self.assertEqual(
            ranked,
            sorted(
                ranked,
                key=lambda item: (
                    -float(item["fitFalsePositivePrecision"]),
                    -int(item["fitFalsePositiveSupport"]),
                    int(item["fitTotalGeneratedSupport"]),
                    tuple(item["signatures"]),
                ),
            ),
        )

    def test_invalid_rule_shape_is_rejected(self):
        event = row(1, 0, 71)
        with self.assertRaises(ValueError):
            event_matches_triple(event, ["a", "b"])
        with self.assertRaises(ValueError):
            event_matches_triple(event, ["a", "a", "b"])


if __name__ == "__main__":
    unittest.main()
