import copy
import unittest

from filter_structure_grid import FLOAT_EPSILON_SECONDS, filter_events, transform


def alignment():
    return {
        "reviewStatus": "complete",
        "independentOfPredictions": True,
        "windowSeconds": [0.0, 2.0],
        "segments": [
            {"beatStart": 0.0, "beatEnd": 4.0, "timeStart": 0.0, "timeEnd": 2.0},
        ],
    }


def event(identity, start, midi=60):
    return {"id": identity, "start": start, "end": start + .1, "midi": midi, "amplitude": .5}


class StructureGridFilterTests(unittest.TestCase):
    def test_keeps_exact_grid_event(self):
        kept, removed, _ = filter_events([event("e", .5)], alignment(), tolerance_seconds=.05)
        self.assertEqual(len(kept), 1)
        self.assertEqual(removed, [])

    def test_keeps_inside_tolerance(self):
        kept, removed, _ = filter_events([event("e", .549)], alignment(), tolerance_seconds=.05)
        self.assertEqual(len(kept), 1)
        self.assertEqual(removed, [])

    def test_inclusive_boundary_survives_binary_float_noise(self):
        kept, removed, _ = filter_events(
            [event("e", .30)], alignment(), subdivision_beats=.5, tolerance_seconds=.05
        )
        self.assertLessEqual(abs(.30 - .25), .05 + FLOAT_EPSILON_SECONDS)
        self.assertEqual(len(kept), 1)
        self.assertEqual(removed, [])

    def test_rejects_just_outside_tolerance(self):
        kept, removed, _ = filter_events([event("e", .551)], alignment(), tolerance_seconds=.05)
        self.assertEqual(kept, [])
        self.assertEqual(len(removed), 1)

    def test_filter_never_changes_kept_time_or_midi_and_never_adds_events(self):
        rows = [event("a", .5, 50), event("b", .62, 62)]
        kept, removed, _ = filter_events(rows, alignment(), tolerance_seconds=.05)
        by_id = {row["id"]: row for row in rows}
        self.assertLessEqual(len(kept), len(rows))
        for row in kept:
            self.assertEqual(row["start"], by_id[row["id"]]["start"])
            self.assertEqual(row["midi"], by_id[row["id"]]["midi"])
        self.assertEqual(len(kept) + len(removed), len(rows))

    def test_requires_complete_prediction_independent_alignment(self):
        for field, value in [("reviewStatus", "draft"), ("independentOfPredictions", False)]:
            a = alignment()
            a[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                filter_events([event("e", .5)], a)

    def test_transform_is_reference_blind_and_delivery_false(self):
        doc = {"kind": "x", "events": [event("e", .5)], "customerDeliveryEligible": False}
        before = copy.deepcopy(doc)
        out = transform(doc, alignment(), source_sha256="a"*64, alignment_sha256="b"*64)
        self.assertEqual(doc, before)
        self.assertFalse(out["structureGridFilter"]["referenceLabelsRead"])
        self.assertFalse(out["customerDeliveryEligible"])


if __name__ == "__main__":
    unittest.main()
