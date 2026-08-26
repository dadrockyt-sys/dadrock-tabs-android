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

from search_atomic_singleton_onset_prunes import (  # noqa: E402
    BASELINE_EVENT_COUNT,
    BASELINE_EVENT_SHA256,
    BASELINE_MEASURE_COUNT,
    BASELINE_NAME,
    _validate_fixed_search_parameters,
    candidate_name,
    make_candidate,
    removed_event_count,
)
from v144_rhythm_singleton_onset_prune_policy import apply_singleton_onset_prune_rule  # noqa: E402


def event(
    event_index: int,
    *,
    measure: int = 1,
    step: int = 4,
    string_index: int = 1,
    fret: int = 1,
    midi: int = 60,
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
        "techniques": [],
    }
    row.update(extra)
    return row


class AtomicSingletonOnsetPruneSearchInvariantTests(unittest.TestCase):
    def test_candidate_name_is_deterministic_and_all_rule_fields_are_sensitive(self) -> None:
        base = candidate_name("stepQuarter::0", 1, 0)
        self.assertEqual(base, candidate_name("stepQuarter::0", 1, 0))
        self.assertNotEqual(base, candidate_name("stepQuarter::1", 1, 0))
        self.assertNotEqual(base, candidate_name("stepQuarter::0", 2, 0))
        self.assertNotEqual(base, candidate_name("stepQuarter::0", 1, 1))

    def test_fixed_search_parameters_cannot_be_relaxed(self) -> None:
        _validate_fixed_search_parameters(3, 256)
        for support, maximum in ((2, 256), (4, 256), (3, 255), (3, 257)):
            with self.assertRaises(ValueError):
                _validate_fixed_search_parameters(support, maximum)

    def test_valid_prune_is_deletion_only_subsequence_and_counts_removed_event(self) -> None:
        baseline = [
            event(0, measure=1, step=4, custom="remove"),
            event(1, measure=1, step=8, string_index=2, fret=5, midi=60, custom="keep"),
            event(2, measure=2, step=8, string_index=2, fret=7, midi=62, custom="keep2"),
        ]
        candidate = apply_singleton_onset_prune_rule(baseline, "stepQuarter::0", 1, 0)
        self.assertEqual([row["eventIndex"] for row in candidate], [1, 2])
        self.assertEqual(
            removed_event_count(
                baseline,
                candidate,
                expected_context_signature="stepQuarter::0",
                expected_source_string_index=1,
                expected_source_pitch_class=0,
            ),
            1,
        )
        self.assertEqual(candidate[0]["custom"], "keep")
        self.assertEqual(candidate[1]["custom"], "keep2")

    def test_survivor_mutation_reordering_and_added_events_are_rejected(self) -> None:
        baseline = [
            event(0, measure=1, step=4),
            event(1, measure=1, step=8, string_index=2, fret=5, midi=60),
            event(2, measure=2, step=8, string_index=2, fret=7, midi=62),
        ]
        valid = apply_singleton_onset_prune_rule(baseline, "stepQuarter::0", 1, 0)

        mutated = [dict(row) for row in valid]
        mutated[0]["durationSteps"] = 2
        with self.assertRaises(ValueError):
            removed_event_count(baseline, mutated)

        with self.assertRaises(ValueError):
            removed_event_count(baseline, list(reversed(valid)))

        with self.assertRaises(ValueError):
            removed_event_count(valid, baseline)

    def test_locked_rule_mismatch_is_rejected(self) -> None:
        baseline = [
            event(0, measure=1, step=4),
            event(1, measure=1, step=8, string_index=2, fret=5, midi=60),
        ]
        candidate = apply_singleton_onset_prune_rule(baseline, "stepQuarter::0", 1, 0)
        with self.assertRaises(ValueError):
            removed_event_count(
                baseline,
                candidate,
                expected_context_signature="stepQuarter::0",
                expected_source_string_index=2,
                expected_source_pitch_class=0,
            )

    def test_count_changing_candidate_safety_keeps_measure_guard_required(self) -> None:
        candidate = make_candidate(
            "x",
            "atomic-singleton-onset-prune",
            {"pitchContentF1": 0.0},
            measure_preserved=True,
            event_count_preserved=False,
        )
        safety = candidate["safety"]
        self.assertTrue(safety["baselineGeneratedMeasureSetPreserved"])
        self.assertFalse(safety["baselineEventCountPreserved"])
        self.assertFalse(safety["runtimeReferenceInputUsed"])
        self.assertFalse(safety["v5Modified"])
        self.assertFalse(safety["mainModified"])
        self.assertFalse(safety["productionModified"])
        self.assertFalse(safety["modalGpuInvoked"])
        self.assertTrue(safety["deterministic"])

    def test_search_locks_current_accepted_baseline_identity_constants(self) -> None:
        self.assertEqual(BASELINE_NAME, "singleton-onset-replace-be9e9aa7a734e3cd")
        self.assertEqual(BASELINE_EVENT_COUNT, 1144)
        self.assertEqual(BASELINE_MEASURE_COUNT, 113)
        self.assertEqual(
            BASELINE_EVENT_SHA256,
            "4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881",
        )


if __name__ == "__main__":
    unittest.main()
