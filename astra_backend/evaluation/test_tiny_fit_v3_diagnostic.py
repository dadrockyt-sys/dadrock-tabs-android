import unittest

from event_contract_v2 import Event
from tiny_fit_v3_diagnostic import boundary_exclusions, detailed_score


class TinyFitV3DiagnosticTests(unittest.TestCase):
    def test_boundary_exclusion_removes_boundary_prediction_but_not_real_extra(self):
        event_id = [[None] * 10 for _ in range(6)]
        for i in range(6, 10):
            event_id[0][i] = "carry"
        prepared = {
            "crop": {"hopSeconds": 0.01, "frames": 10},
            "eventId": event_id,
            "carryInEventIds": [],
            "carryOutEventIds": ["carry"],
        }
        intervals, records = boundary_exclusions(prepared)
        self.assertEqual(intervals, [(0, 0.06, 0.10)])
        self.assertEqual(records[0]["kind"], ["carry_out"])

        ref = [Event("r", 0, 5, 0.01, 0.04)]
        pred = [
            Event("p-match", 0, 5, 0.01, 0.04),
            Event("p-boundary", 0, 7, 0.07, 0.09),
            Event("p-extra", 1, 3, 0.02, 0.03),
        ]
        out = detailed_score(pred, ref, excluded_intervals=intervals)
        self.assertEqual([x["id"] for x in out["excludedPredictions"]], ["p-boundary"])
        self.assertEqual([x["id"] for x in out["falsePositives"]], ["p-extra"])
        self.assertEqual(out["falseNegatives"], [])

    def test_carry_in_boundary_uses_frame_grid_occupancy(self):
        event_id = [[None] * 8 for _ in range(6)]
        for i in range(0, 3):
            event_id[4][i] = "carry-in"
        prepared = {
            "crop": {"hopSeconds": 0.02, "frames": 8},
            "eventId": event_id,
            "carryInEventIds": ["carry-in"],
            "carryOutEventIds": [],
        }
        intervals, records = boundary_exclusions(prepared)
        self.assertEqual(intervals, [(4, 0.0, 0.06)])
        self.assertEqual(records[0]["frameEndExclusive"], 3)


if __name__ == "__main__":
    unittest.main()
