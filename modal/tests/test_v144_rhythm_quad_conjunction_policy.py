from __future__ import annotations

from pathlib import Path
import sys
import unittest

MODAL_DIR = Path(__file__).resolve().parents[1]
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

from v144_rhythm_quad_conjunction_policy import (  # noqa: E402
    apply_quad_prune,
    event_matches_quad,
    quad_signatures,
    rank_fit_quads,
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


class QuadConjunctionPolicyTests(unittest.TestCase):
    def test_quads_are_deterministic_unique_and_sorted(self):
        quads = quad_signatures(row(1, 0, 71))
        self.assertEqual(quads, quad_signatures(row(1, 0, 71)))
        self.assertEqual(len(quads), len(set(quads)))
        self.assertTrue(all(a < b < c < d for a, b, c, d in quads))

    def test_runtime_match_requires_all_four_signatures(self):
        event = row(1, 0, 71)
        good = ["pitchClass::11", "register::high", "stepParity::0", "stepQuarter::0"]
        bad = ["pitchClass::11", "register::high", "stepParity::1", "stepQuarter::0"]
        self.assertTrue(event_matches_quad(event, good))
        self.assertFalse(event_matches_quad(event, bad))

    def test_runtime_transform_is_reference_free(self):
        events = [row(1, 0, 71), row(1, 1, 71), row(1, 0, 64)]
        kept = apply_quad_prune(
            events,
            ["pitchClass::11", "register::high", "stepParity::0", "stepQuarter::0"],
        )
        self.assertEqual(len(kept), 2)
        self.assertEqual([event["midi"] for event in kept], [71, 64])

    def test_rank_is_fit_only_stable_and_capped(self):
        fit_generated = [
            row(measure, step, 71 + (step % 2))
            for measure in range(1, 9)
            for step in range(4)
        ]
        ranked = rank_fit_quads(
            fit_generated,
            fit_generated,
            minimum_false_positive_support=1,
            maximum_candidates=9,
        )
        self.assertEqual(len(ranked), 9)
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
        self.assertTrue(all(len(item["signatures"]) == 4 for item in ranked))

    def test_invalid_rule_shape_is_rejected(self):
        event = row(1, 0, 71)
        with self.assertRaises(ValueError):
            event_matches_quad(event, ["a", "b", "c"])
        with self.assertRaises(ValueError):
            event_matches_quad(event, ["a", "a", "b", "c"])


if __name__ == "__main__":
    unittest.main()
