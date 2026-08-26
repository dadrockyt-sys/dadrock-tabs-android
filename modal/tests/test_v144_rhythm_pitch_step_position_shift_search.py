from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SEARCH_DIR = ROOT / "validation" / "v144_rhythm_calibration"
if str(SEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(SEARCH_DIR))

from search_contextual_pitch_step_position_shifts import (  # noqa: E402
    candidate_name,
    changed_event_count,
)


def event(
    event_index: int,
    *,
    measure: int = 1,
    step: int = 4,
    string_index: int = 1,
    fret: int = 1,
    midi: int = 60,
    duration_steps: int = 1,
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
        "durationSteps": duration_steps,
        "techniques": [] if techniques is None else list(techniques),
    }
    row.update(extra)
    return row


class PitchStepPositionSearchInvariantTests(unittest.TestCase):
    def test_candidate_name_is_order_stable_and_all_shift_sensitive(self) -> None:
        left = candidate_name(["pitchClass::0", "measurePhase::1"], 2, 1, 1)
        right = candidate_name(["measurePhase::1", "pitchClass::0"], 2, 1, 1)
        other_pitch = candidate_name(["pitchClass::0", "measurePhase::1"], -2, 1, 1)
        other_step = candidate_name(["pitchClass::0", "measurePhase::1"], 2, -1, 1)
        other_string = candidate_name(["pitchClass::0", "measurePhase::1"], 2, 1, -1)
        self.assertEqual(left, right)
        self.assertNotEqual(left, other_pitch)
        self.assertNotEqual(left, other_step)
        self.assertNotEqual(left, other_string)
        self.assertTrue(left.startswith("pitch-step-position-shift-"))

    def test_valid_three_way_correction_counts_changed_event(self) -> None:
        baseline = [event(0), event(1, measure=2)]
        candidate = [
            event(0, step=5, string_index=2, fret=7, midi=62),
            event(1, measure=2),
        ]
        self.assertEqual(
            changed_event_count(
                baseline,
                candidate,
                expected_semitone_shift=2,
                expected_step_shift=1,
                expected_string_shift=1,
            ),
            1,
        )

    def test_unchanged_events_count_zero(self) -> None:
        baseline = [event(0), event(1, measure=2)]
        self.assertEqual(changed_event_count(baseline, [dict(row) for row in baseline]), 0)

    def test_event_count_or_order_change_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            changed_event_count([event(0)], [event(0), event(1)])
        baseline = [event(0), event(1, measure=2)]
        candidate = [event(1), event(0, measure=2)]
        with self.assertRaises(ValueError):
            changed_event_count(baseline, candidate)

    def test_measure_duration_techniques_and_other_metadata_are_protected(self) -> None:
        baseline = [event(0, sustainTier="short")]
        variants = [
            event(0, measure=2, step=5, string_index=2, fret=7, midi=62, sustainTier="short"),
            event(0, step=5, string_index=2, fret=7, midi=62, duration_steps=2, sustainTier="short"),
            event(0, step=5, string_index=2, fret=7, midi=62, techniques=["palm-mute"], sustainTier="short"),
            event(0, step=5, string_index=2, fret=7, midi=62, sustainTier="long"),
        ]
        for candidate in variants:
            with self.assertRaises(ValueError):
                changed_event_count(baseline, [candidate])

    def test_partial_dimension_changes_are_rejected(self) -> None:
        baseline = [event(0)]
        variants = [
            event(0, fret=3, midi=62),
            event(0, step=5),
            event(0, string_index=2, fret=5, midi=60),
            event(0, step=5, fret=3, midi=62),
            event(0, string_index=2, fret=7, midi=62),
            event(0, step=5, string_index=2, fret=5, midi=60),
        ]
        for candidate in variants:
            with self.assertRaises(ValueError):
                changed_event_count(baseline, [candidate])

    def test_tuning_derived_fret_identity_is_required(self) -> None:
        baseline = [event(0)]
        bad = [event(0, step=5, string_index=2, fret=6, midi=62)]
        with self.assertRaises(ValueError):
            changed_event_count(baseline, bad)

    def test_pitch_step_and_adjacent_string_bounds_are_enforced(self) -> None:
        baseline = [event(0, string_index=1, fret=1, midi=60)]
        with self.assertRaises(ValueError):
            changed_event_count(
                baseline,
                [event(0, step=5, string_index=3, fret=12, midi=62)],
            )
        with self.assertRaises(ValueError):
            changed_event_count(
                baseline,
                [event(0, step=5, string_index=2, fret=18, midi=73)],
                maximum_abs_semitone_shift=12,
            )
        with self.assertRaises(ValueError):
            changed_event_count(
                baseline,
                [event(0, step=7, string_index=2, fret=7, midi=62)],
                maximum_abs_step_shift=2,
            )

    def test_candidate_step_must_remain_inside_measure(self) -> None:
        baseline = [event(0, step=15)]
        candidate = [event(0, step=16, string_index=2, fret=7, midi=62)]
        with self.assertRaises(ValueError):
            changed_event_count(
                baseline,
                candidate,
                maximum_abs_step_shift=2,
            )

    def test_fixed_locked_deltas_are_enforced(self) -> None:
        baseline = [event(0)]
        candidate = [event(0, step=5, string_index=2, fret=7, midi=62)]
        mismatches = [
            {"expected_semitone_shift": -2, "expected_step_shift": 1, "expected_string_shift": 1},
            {"expected_semitone_shift": 2, "expected_step_shift": -1, "expected_string_shift": 1},
            {"expected_semitone_shift": 2, "expected_step_shift": 1, "expected_string_shift": -1},
        ]
        for kwargs in mismatches:
            with self.assertRaises(ValueError):
                changed_event_count(baseline, candidate, **kwargs)

    def test_expected_shifts_must_be_supplied_together_and_valid(self) -> None:
        baseline = [event(0)]
        partials = [
            {"expected_semitone_shift": 2},
            {"expected_step_shift": 1},
            {"expected_string_shift": 1},
            {"expected_semitone_shift": 2, "expected_step_shift": 1},
        ]
        for kwargs in partials:
            with self.assertRaises(ValueError):
                changed_event_count(baseline, baseline, **kwargs)

        invalid = [
            {"expected_semitone_shift": 0, "expected_step_shift": 1, "expected_string_shift": 1},
            {"expected_semitone_shift": 2, "expected_step_shift": 0, "expected_string_shift": 1},
            {"expected_semitone_shift": 2, "expected_step_shift": 1, "expected_string_shift": 0},
            {"expected_semitone_shift": 13, "expected_step_shift": 1, "expected_string_shift": 1},
            {"expected_semitone_shift": 2, "expected_step_shift": 3, "expected_string_shift": 1},
            {"expected_semitone_shift": 2, "expected_step_shift": 1, "expected_string_shift": 2},
        ]
        for kwargs in invalid:
            with self.assertRaises(ValueError):
                changed_event_count(baseline, baseline, **kwargs)


if __name__ == "__main__":
    unittest.main()
