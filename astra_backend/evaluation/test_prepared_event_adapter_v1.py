import unittest

from evaluation.prepared_event_adapter_v1 import (
    MASK,
    prepare_event_crop,
    select_training_crop,
    source_events_from_notes,
)


HOP = 0.01


class PreparedEventAdapterTests(unittest.TestCase):
    def test_preserves_repeated_same_fret_attacks(self):
        notes = {"E": [(0.10, 0.20, 45), (0.20, 0.30, 45)]}
        out = prepare_event_crop(
            notes,
            capture_id="P1|singlenotes|x|directinput",
            lag_ms=10,
            allowlist_lag_ms=10,
            crop_start_frame=0,
            frames=40,
            hop_seconds=HOP,
        )
        self.assertTrue(out["launchReady"])
        self.assertEqual(len(out["scorableEvents"]), 2)
        self.assertEqual(sum(v == 1 for v in out["onset"][0]), 2)
        self.assertNotEqual(out["scorableEvents"][0]["id"], out["scorableEvents"][1]["id"])

    def test_carry_in_keeps_state_without_false_onset(self):
        notes = {"E": [(0.05, 0.25, 45)]}
        out = prepare_event_crop(
            notes,
            capture_id="cap",
            lag_ms=0,
            allowlist_lag_ms=0,
            crop_start_frame=10,
            frames=20,
            hop_seconds=HOP,
        )
        self.assertEqual(out["carryInEventIds"], ["cap:E:0"])
        self.assertEqual(out["state"][0][0], 5)
        self.assertEqual(out["onset"][0][0], 0)
        self.assertEqual(out["scorableEvents"], [])
        self.assertIn(
            {"eventId": "cap:E:0", "reason": "crop_boundary"},
            out["excludedEvents"],
        )

    def test_carry_out_retains_real_onset_but_is_not_offset_scored(self):
        notes = {"E": [(0.15, 0.50, 45)]}
        out = prepare_event_crop(
            notes,
            capture_id="cap",
            lag_ms=0,
            allowlist_lag_ms=0,
            crop_start_frame=10,
            frames=20,
            hop_seconds=HOP,
        )
        self.assertEqual(out["carryOutEventIds"], ["cap:E:0"])
        self.assertEqual(sum(v == 1 for v in out["onset"][0]), 1)
        self.assertEqual(out["scorableEvents"], [])

    def test_registered_mask_excludes_whole_event_and_masks_occupancy(self):
        notes = {"E": [(0.10, 0.30, 45)]}
        out = prepare_event_crop(
            notes,
            capture_id="cap",
            lag_ms=0,
            allowlist_lag_ms=0,
            crop_start_frame=0,
            frames=40,
            hop_seconds=HOP,
            excluded_intervals=[(0, 0.15, 0.16)],
        )
        self.assertTrue(out["launchReady"])
        self.assertEqual(out["scorableEvents"], [])
        self.assertTrue(all(out["state"][0][i] == MASK for i in range(10, 30)))
        self.assertIn(
            {"eventId": "cap:E:0", "reason": "registered_mask_intersection"},
            out["excludedEvents"],
        )

    def test_allowlist_mismatch_fails_closed(self):
        with self.assertRaises(ValueError):
            prepare_event_crop(
                {"E": [(0.1, 0.2, 45)]},
                capture_id="cap",
                lag_ms=-19,
                allowlist_lag_ms=-20,
                crop_start_frame=0,
                frames=40,
                hop_seconds=HOP,
            )

    def test_unsupported_fret_is_reported_not_dropped(self):
        out = prepare_event_crop(
            {"E": [(0.10, 0.20, 39)]},
            capture_id="cap",
            lag_ms=0,
            allowlist_lag_ms=0,
            crop_start_frame=0,
            frames=40,
            hop_seconds=HOP,
        )
        self.assertFalse(out["launchReady"])
        self.assertEqual(out["unresolvedLabelCount"], 1)
        self.assertIn("unsupported_fret", {r["code"] for r in out["unresolved"]})

    def test_same_string_overlap_is_reported(self):
        out = prepare_event_crop(
            {"E": [(0.10, 0.25, 45), (0.20, 0.30, 47)]},
            capture_id="cap",
            lag_ms=0,
            allowlist_lag_ms=0,
            crop_start_frame=0,
            frames=40,
            hop_seconds=HOP,
        )
        self.assertFalse(out["launchReady"])
        self.assertIn("same_string_overlap", {r["code"] for r in out["unresolved"]})

    def test_subframe_attack_is_reported(self):
        out = prepare_event_crop(
            {"E": [(0.101, 0.102, 45)]},
            capture_id="cap",
            lag_ms=0,
            allowlist_lag_ms=0,
            crop_start_frame=0,
            frames=40,
            hop_seconds=HOP,
        )
        self.assertFalse(out["launchReady"])
        self.assertIn("subframe_attack", {r["code"] for r in out["unresolved"]})

    def test_negative_lag_is_preserved_when_aligned_time_stays_valid(self):
        out = prepare_event_crop(
            {"E": [(0.10, 0.20, 45)]},
            capture_id="cap",
            lag_ms=-20,
            allowlist_lag_ms=-20,
            crop_start_frame=0,
            frames=40,
            hop_seconds=HOP,
        )
        self.assertTrue(out["launchReady"])
        self.assertAlmostEqual(out["scorableEvents"][0]["start"], 0.08)

    def test_crop_selection_prefers_earliest_repeated_attack(self):
        events, issues, _ = source_events_from_notes(
            {"E": [(0.20, 0.30, 45), (0.50, 0.60, 47), (1.00, 1.10, 45)]},
            capture_id="cap",
            lag_ms=0,
        )
        self.assertEqual(issues, [])
        selection = select_training_crop(
            events, total_frames=300, frames=100, hop_seconds=HOP
        )
        self.assertEqual(selection["reason"], "earliest_repeated_same_fret_attack")
        start = selection["startFrame"]
        self.assertLessEqual(start, 20)
        self.assertGreater(start + 100, 100)

    def test_out_of_crop_source_issue_is_reported_without_blocking_crop(self):
        notes = {"E": [(0.10, 0.20, 45), (5.00, 5.10, 39)]}
        out = prepare_event_crop(
            notes, capture_id="cap", lag_ms=0, allowlist_lag_ms=0,
            crop_start_frame=0, frames=40, hop_seconds=HOP,
        )
        self.assertTrue(out["launchReady"])
        self.assertGreater(out["outOfCropSourceIssueCount"], 0)
        self.assertIn("unsupported_fret", {r["code"] for r in out["sourceIssues"]})

    def test_crop_selection_does_not_claim_unfit_distant_repeat(self):
        events, issues, _ = source_events_from_notes(
            {"E": [(0.20, 0.30, 45), (5.00, 5.10, 45)]},
            capture_id="cap", lag_ms=0,
        )
        self.assertEqual(issues, [])
        selection = select_training_crop(
            events, total_frames=600, frames=100, hop_seconds=HOP
        )
        self.assertEqual(selection["reason"], "earliest_source_attack")

    def test_hashes_are_stable_and_capture_scoped(self):
        kwargs = dict(
            notes={"E": [(0.10, 0.20, 45)]},
            lag_ms=0,
            allowlist_lag_ms=0,
            crop_start_frame=0,
            frames=40,
            hop_seconds=HOP,
        )
        a = prepare_event_crop(capture_id="a", **kwargs)
        b = prepare_event_crop(capture_id="a", **kwargs)
        c = prepare_event_crop(capture_id="b", **kwargs)
        self.assertEqual(a["sourceEventSha256"], b["sourceEventSha256"])
        self.assertNotEqual(a["sourceEventSha256"], c["sourceEventSha256"])
        self.assertEqual(a["targetSha256"], b["targetSha256"])


if __name__ == "__main__":
    unittest.main()
