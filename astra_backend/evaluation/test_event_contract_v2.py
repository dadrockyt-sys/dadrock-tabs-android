import unittest

from event_contract_v2 import Event, delivery_counts, frame_targets, score_events, validate_events, from_string_notes
from diagnostic_histogram_v2 import finalize_hist


def note(id, start, end, string=0, fret=5):
    return Event(id, string, fret, start, end)


class EventTests(unittest.TestCase):
    def test_source_adapter_preserves_reattacks_and_frozen_lag(self):
        events = from_string_notes({"E": [(.1, .2, 45), (.2, .3, 45)]},
                                   capture_id="synthetic", lag_ms=10)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].fret, 5)
        self.assertAlmostEqual(events[1].start, .21)
        self.assertEqual(events[1].id, "synthetic:E:1")

    def test_source_adapter_rejects_unresolved_input(self):
        for notes, lag in [({"X": [(0, .1, 45)]}, 0), ({"E": [(0, .1, 39)]}, 0),
                           ({"E": [(0, .1, 45)]}, -10), ({"E": [(0, .1, 45.1)]}, 0)]:
            with self.assertRaises(ValueError):
                from_string_notes(notes, capture_id="synthetic", lag_ms=lag)

    def test_repeated_fret_retains_two_attacks_and_ids(self):
        events = [note("a", .1, .2), note("b", .2, .3)]
        target = frame_targets(events, frames=40, hop_seconds=.01)
        self.assertTrue(target["onset"][0][10])
        self.assertTrue(target["onset"][0][20])
        self.assertEqual(sum(target["onset"][0]), 2)
        self.assertEqual(target["state"][0][19:21], [5, 5])
        self.assertEqual(target["eventId"][0][19:21], ["a", "b"])
        result = score_events([note("merged", .1, .3)], events)
        self.assertEqual((result["truePositive"], result["falseNegative"]), (1, 1))
        self.assertAlmostEqual(result["f1"], 2/3)

    def test_tie_is_one_extended_event(self):
        events = [note("tied", .1, .4)]
        target = frame_targets(events, frames=50, hop_seconds=.01)
        self.assertEqual(sum(target["onset"][0]), 1)
        self.assertEqual(score_events(events, events)["referenceCount"], 1)

    def test_repeated_chord(self):
        events = [note(f"{s}-{k}", .1 + k * .2, .3 + k * .2, s, 3)
                  for s in (0, 1, 2) for k in (0, 1)]
        self.assertEqual(score_events(events, events)["truePositive"], 6)

    def test_silence_does_not_mean_abstained(self):
        out = score_events([], [])
        self.assertEqual(out["predictionCount"], 0)
        self.assertTrue(out["emptyReference"])
        self.assertIsNone(out["abstentionRate"])
        self.assertFalse(out["customerDeliveryEligible"])

    def test_empty_prediction_is_failure_to_recall(self):
        self.assertEqual(score_events([], [note("r", 0, .1)])["recall"], 0)

    def test_no_reference_with_prediction_is_false_positive(self):
        self.assertEqual(score_events([note("p", 0, .1)], [])["falsePositive"], 1)

    def test_onset_tolerance_boundary(self):
        r = [note("r", .1, .2)]
        self.assertEqual(score_events([note("p", .15, .25)], r)["truePositive"], 1)
        self.assertEqual(score_events([note("p", .15001, .25)], r)["truePositive"], 0)

    def test_offsets_reported_separately(self):
        out = score_events([note("p", .1, .9)], [note("r", .1, .2)])
        self.assertEqual(out["f1"], 1)
        self.assertEqual(out["matchedOffsetWithinTolerance"], 0)
        self.assertAlmostEqual(out["matchedOffsetMAESeconds"], .7)

    def test_wrong_string_not_exact_identity(self):
        out = score_events([note("p", .1, .2, 1, 0)], [note("r", .1, .2, 0, 5)])
        self.assertEqual(out["truePositive"], 0)

    def test_matching_maximizes_count_not_nearest_first(self):
        pred = [note("p1", .10, .11), note("p2", .16, .17)]
        ref = [note("r1", .06, .07), note("r2", .12, .13)]
        self.assertEqual(score_events(pred, ref)["truePositive"], 2)

    def test_matching_minimizes_total_error(self):
        out = score_events([note("p", .13, .14)],
                           [note("r1", .10, .11), note("r2", .15, .16)])
        self.assertAlmostEqual(out["matchedOnsetMAESeconds"], .02)

    def test_order_invariant(self):
        events = [note("a", .1, .2), note("b", .2, .3)]
        self.assertEqual(score_events(events, events), score_events(events[::-1], events[::-1]))

    def test_mask_excludes_whole_events_without_new_attacks(self):
        r = [note("r", .1, .4), note("r2", .5, .6)]
        out = score_events(r, r, excluded_intervals=[(0, .2, .3)])
        self.assertEqual(out["excludedReferenceCount"], 1)
        self.assertEqual(out["excludedPredictionCount"], 1)
        self.assertEqual(out["referenceCount"], 1)

    def test_mask_end_is_half_open(self):
        events = [note("r", .3, .4)]
        self.assertEqual(score_events(events, events, excluded_intervals=[(0, .2, .3)])
                         ["excludedReferenceCount"], 0)

    def test_invalid_events_fail(self):
        for e in [note("x", .2, .1), note("x", float("nan"), .2),
                  note("x", 0, .1, string=True), note("x", 0, .1, fret=20)]:
            with self.subTest(event=e), self.assertRaises(ValueError):
                validate_events([e])

    def test_duplicates_and_overlap_fail(self):
        for events in [[note("x", 0, .1), note("x", .2, .3)],
                       [note("a", 0, .2), note("b", .1, .3)]]:
            with self.assertRaises(ValueError):
                validate_events(events)

    def test_subframe_attack_not_silently_dropped(self):
        with self.assertRaises(ValueError):
            frame_targets([note("x", .001, .002)], frames=20, hop_seconds=.01)

    def test_beyond_coverage_fails(self):
        with self.assertRaises(ValueError):
            frame_targets([note("x", 0, .3)], frames=20, hop_seconds=.01)

    def test_status_counts_are_observed(self):
        result = delivery_counts(["complete", "partial", "abstained", "failed"])
        self.assertEqual(result["abstentionRate"], .25)
        self.assertEqual(result["failed"], 1)
        self.assertIsNone(delivery_counts([])["abstentionRate"])
        with self.assertRaises(ValueError):
            delivery_counts(["unknown"])


class HistogramTests(unittest.TestCase):
    def test_perfect_ranking(self):
        out = finalize_hist({"pos": [0, 3], "neg": [4, 0]})
        self.assertEqual(out["approxAUROC"], 1)
        self.assertEqual(out["approxAUPRCTrapezoid"], 1)
        self.assertEqual(out["approxAveragePrecision"], 1)

    def test_reversed_ranking_still_nonnegative(self):
        out = finalize_hist({"pos": [2, 0], "neg": [0, 2]})
        self.assertEqual(out["approxAUROC"], 0)
        self.assertEqual(out["approxAUPRCTrapezoid"], .25)
        self.assertEqual(out["approxAveragePrecision"], .5)

    def test_tied_ranking_uses_whole_bin(self):
        out = finalize_hist({"pos": [2], "neg": [2]})
        self.assertEqual(out["approxAUROC"], .5)
        self.assertEqual(out["approxAveragePrecision"], .5)
        self.assertEqual(out["approxAUPRCTrapezoid"], .75)

    def test_empty_and_single_class(self):
        out = finalize_hist({"pos": [0, 0], "neg": [1, 2]})
        self.assertIsNone(out["approxAUROC"])
        self.assertIsNone(out["approxAUPRCTrapezoid"])
        out = finalize_hist({"pos": [1, 2], "neg": [0, 0]})
        self.assertIsNone(out["approxAUROC"])
        self.assertEqual(out["approxAUPRCTrapezoid"], 1)
        self.assertIsNone(finalize_hist({"pos": [0], "neg": [0]})["approxAveragePrecision"])

    def test_invalid_histograms_fail(self):
        for p, n in [([], []), ([1], [1, 2]), ([-1], [1]), ([.1], [1]), ([float("nan")], [1])]:
            with self.subTest(p=p, n=n), self.assertRaises(ValueError):
                finalize_hist({"pos": p, "neg": n})


if __name__ == "__main__":
    unittest.main()
