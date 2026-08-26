from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SEARCH_DIR = ROOT / "validation" / "v144_rhythm_calibration"
MODAL_DIR = ROOT / "modal"
for entry in (SEARCH_DIR, MODAL_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from search_atomic_generated_only_triad_prunes import (  # noqa: E402
    BASELINE_EVENT_COUNT,
    BASELINE_EVENT_SHA256,
    BASELINE_MEASURE_COUNT,
    BASELINE_NAME,
    _validate_fixed_search_parameters,
    candidate_name,
    removed_event_count,
    safety_payload,
)
from v144_rhythm_generated_only_triad_prune_policy import (  # noqa: E402
    DEFAULT_MAX_CANDIDATES,
    DEFAULT_MIN_FALSE_POSITIVE_SUPPORT,
    apply_generated_only_triad_prune_rule,
)


def event(
    event_index: int,
    *,
    measure: int = 1,
    step: int = 4,
    string_index: int = 1,
    fret: int = 1,
    midi: int = 60,
    techniques: list[str] | None = None,
    **extra,
) -> dict:
    row = {
        "eventIndex": event_index,
        "measure": measure,
        "step": step,
        "stringIndex": string_index,
        "fret": fret,
        "midi": midi,
        "durationSteps": 1,
        "techniques": [] if techniques is None else list(techniques),
    }
    row.update(extra)
    return row


def baseline() -> list[dict]:
    return [
        event(0, measure=1, step=4, string_index=1, fret=1, midi=60),
        event(1, measure=1, step=4, string_index=2, fret=7, midi=62),
        event(2, measure=1, step=4, string_index=3, fret=10, midi=60),
        event(3, measure=1, step=8, string_index=4, fret=15, midi=60, custom="keep-a"),
        event(4, measure=2, step=4, string_index=1, fret=1, midi=60),
        event(5, measure=2, step=4, string_index=2, fret=7, midi=62),
        event(6, measure=2, step=4, string_index=3, fret=10, midi=60),
        event(7, measure=2, step=8, string_index=4, fret=17, midi=62, custom="keep-b"),
    ]


class AtomicGeneratedOnlyTriadPruneSearchInvariantTests(unittest.TestCase):
    def test_candidate_name_is_note_order_stable_and_all_rule_fields_sensitive(self) -> None:
        first = candidate_name("stepQuarter::0", 1, 0, 2, 2, 3, 0)
        reversed_notes = candidate_name("stepQuarter::0", 3, 0, 2, 2, 1, 0)
        rotated_notes = candidate_name("stepQuarter::0", 2, 2, 3, 0, 1, 0)
        self.assertEqual(first, reversed_notes)
        self.assertEqual(first, rotated_notes)
        self.assertNotEqual(first, candidate_name("stepQuarter::1", 1, 0, 2, 2, 3, 0))
        self.assertNotEqual(first, candidate_name("stepQuarter::0", 1, 0, 2, 2, 3, 1))

    def test_valid_prune_is_deletion_only_subsequence_and_counts_three_per_onset(self) -> None:
        source = baseline()
        candidate = apply_generated_only_triad_prune_rule(
            source,
            "stepQuarter::0",
            1,
            0,
            2,
            2,
            3,
            0,
        )
        removed = removed_event_count(
            source,
            candidate,
            expected_context_signature="stepQuarter::0",
            expected_first_string_index=3,
            expected_first_pitch_class=0,
            expected_second_string_index=1,
            expected_second_pitch_class=0,
            expected_third_string_index=2,
            expected_third_pitch_class=2,
        )
        self.assertEqual(removed, 6)
        self.assertEqual([row["eventIndex"] for row in candidate], [3, 7])
        self.assertEqual([row["custom"] for row in candidate], ["keep-a", "keep-b"])

    def test_partial_or_non_triad_deletion_is_rejected(self) -> None:
        source = baseline()
        with self.assertRaises(ValueError):
            removed_event_count(source, source[1:])
        partial = [row for row in source if row["eventIndex"] != 0]
        with self.assertRaises(ValueError):
            removed_event_count(
                source,
                partial,
                expected_context_signature="stepQuarter::0",
                expected_first_string_index=1,
                expected_first_pitch_class=0,
                expected_second_string_index=2,
                expected_second_pitch_class=2,
                expected_third_string_index=3,
                expected_third_pitch_class=0,
            )

    def test_survivor_mutation_reordering_and_added_events_are_rejected(self) -> None:
        source = baseline()
        valid = apply_generated_only_triad_prune_rule(source, "stepQuarter::0", 1, 0, 2, 2, 3, 0)

        mutated = [dict(row) for row in valid]
        mutated[0]["durationSteps"] = 2
        with self.assertRaises(ValueError):
            removed_event_count(source, mutated)

        with self.assertRaises(ValueError):
            removed_event_count(source, list(reversed(valid)))

        added = [dict(row) for row in source] + [event(99, measure=3, step=4)]
        with self.assertRaises(ValueError):
            removed_event_count(source, added)

    def test_locked_rule_mismatch_is_rejected(self) -> None:
        source = baseline()
        candidate = apply_generated_only_triad_prune_rule(source, "stepQuarter::0", 1, 0, 2, 2, 3, 0)
        with self.assertRaises(ValueError):
            removed_event_count(
                source,
                candidate,
                expected_context_signature="stepQuarter::1",
                expected_first_string_index=1,
                expected_first_pitch_class=0,
                expected_second_string_index=2,
                expected_second_pitch_class=2,
                expected_third_string_index=3,
                expected_third_pitch_class=0,
            )

    def test_fixed_search_parameters_cannot_be_relaxed(self) -> None:
        self.assertEqual(DEFAULT_MIN_FALSE_POSITIVE_SUPPORT, 3)
        self.assertEqual(DEFAULT_MAX_CANDIDATES, 256)
        _validate_fixed_search_parameters(3, 256)
        with self.assertRaises(ValueError):
            _validate_fixed_search_parameters(2, 256)
        with self.assertRaises(ValueError):
            _validate_fixed_search_parameters(3, 512)

    def test_search_locks_current_accepted_baseline_and_count_changing_safety(self) -> None:
        self.assertEqual(BASELINE_NAME, "singleton-onset-replace-be9e9aa7a734e3cd")
        self.assertEqual(BASELINE_EVENT_COUNT, 1144)
        self.assertEqual(BASELINE_MEASURE_COUNT, 113)
        self.assertEqual(
            BASELINE_EVENT_SHA256,
            "4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881",
        )
        safety = safety_payload(measure_preserved=True, event_count_preserved=False)
        self.assertTrue(safety["baselineGeneratedMeasureSetPreserved"])
        self.assertFalse(safety["baselineEventCountPreserved"])
        self.assertFalse(safety["runtimeReferenceInputUsed"])
        self.assertFalse(safety["modalGpuInvoked"])
        self.assertFalse(safety["mainModified"])
        self.assertFalse(safety["productionModified"])
        self.assertFalse(safety["v5Modified"])


if __name__ == "__main__":
    unittest.main()
