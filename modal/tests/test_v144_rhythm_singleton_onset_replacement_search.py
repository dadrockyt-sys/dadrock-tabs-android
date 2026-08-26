from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SEARCH_DIR = ROOT / "validation" / "v144_rhythm_calibration"
if str(SEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(SEARCH_DIR))

from search_atomic_singleton_onset_replacements import (  # noqa: E402
    _validate_fixed_search_parameters,
    candidate_name,
    changed_event_count,
)


def event(
    event_index: int,
    *,
    measure: int = 1,
    step: int = 4,
    string_index: int = 5,
    fret: int = 20,
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


def locked_kwargs() -> dict:
    return {
        "expected_context_signature": "stepQuarter::0",
        "expected_source_string_index": 5,
        "expected_source_pitch_class": 0,
        "expected_target_string_index": 2,
        "expected_semitone_shift": 2,
    }


class AtomicSingletonOnsetReplacementSearchInvariantTests(unittest.TestCase):
    def test_candidate_name_is_deterministic_and_all_rule_fields_are_sensitive(self) -> None:
        base = candidate_name("stepQuarter::0", 5, 0, 2, 2)
        self.assertEqual(base, candidate_name("stepQuarter::0", 5, 0, 2, 2))
        self.assertNotEqual(base, candidate_name("stepParity::0", 5, 0, 2, 2))
        self.assertNotEqual(base, candidate_name("stepQuarter::0", 4, 0, 2, 2))
        self.assertNotEqual(base, candidate_name("stepQuarter::0", 5, 1, 2, 2))
        self.assertNotEqual(base, candidate_name("stepQuarter::0", 5, 0, 1, 2))
        self.assertNotEqual(base, candidate_name("stepQuarter::0", 5, 0, 2, 3))
        self.assertTrue(base.startswith("singleton-onset-replace-"))

    def test_valid_nonadjacent_singleton_changes_count_and_preserve_other_onsets(self) -> None:
        baseline = [event(0), event(1, measure=2)]
        candidate = [
            event(0, string_index=2, fret=7, midi=62),
            event(1, measure=2),
        ]
        self.assertEqual(changed_event_count(baseline, candidate, **locked_kwargs()), 1)

        two_changed = [
            event(0, string_index=2, fret=7, midi=62),
            event(1, measure=2, string_index=2, fret=7, midi=62),
        ]
        self.assertEqual(changed_event_count(baseline, two_changed, **locked_kwargs()), 2)

    def test_changed_onset_must_be_exact_singleton(self) -> None:
        baseline = [
            event(0),
            event(1, string_index=4, fret=15, midi=60),
        ]
        candidate = [
            event(0, string_index=2, fret=7, midi=62),
            event(1, string_index=4, fret=15, midi=60),
        ]
        with self.assertRaises(ValueError):
            changed_event_count(baseline, candidate)

    def test_event_count_order_timing_duration_techniques_and_metadata_are_protected(self) -> None:
        baseline = [event(0, sustainTier="short"), event(1, measure=2)]
        with self.assertRaises(ValueError):
            changed_event_count(baseline, baseline + [event(2, measure=3)])
        with self.assertRaises(ValueError):
            changed_event_count(baseline, [baseline[1], baseline[0]])

        variants = [
            [event(0, step=5, string_index=2, fret=7, midi=62, sustainTier="short"), event(1, measure=2)],
            [event(0, duration_steps=2, string_index=2, fret=7, midi=62, sustainTier="short"), event(1, measure=2)],
            [event(0, techniques=["palm-mute"], string_index=2, fret=7, midi=62, sustainTier="short"), event(1, measure=2)],
            [event(0, string_index=2, fret=7, midi=62, sustainTier="long"), event(1, measure=2)],
        ]
        for candidate in variants:
            with self.assertRaises(ValueError):
                changed_event_count(baseline, candidate)

    def test_pitch_only_string_only_and_invalid_tuning_are_rejected(self) -> None:
        baseline = [event(0)]
        pitch_only = [event(0, string_index=5, fret=22, midi=62)]
        string_only = [event(0, string_index=2, fret=5, midi=60)]
        bad_tuning = [event(0, string_index=2, fret=8, midi=62)]
        for candidate in (pitch_only, string_only, bad_tuning):
            with self.assertRaises(ValueError):
                changed_event_count(baseline, candidate)

    def test_locked_context_source_target_and_shift_are_enforced(self) -> None:
        baseline = [event(0)]
        valid = [event(0, string_index=2, fret=7, midi=62)]
        wrong_target = [event(0, string_index=1, fret=3, midi=62)]
        with self.assertRaises(ValueError):
            changed_event_count(
                baseline,
                valid,
                **{**locked_kwargs(), "expected_context_signature": "stepQuarter::1"},
            )
        with self.assertRaises(ValueError):
            changed_event_count(
                baseline,
                valid,
                **{**locked_kwargs(), "expected_source_pitch_class": 1},
            )
        with self.assertRaises(ValueError):
            changed_event_count(baseline, wrong_target, **locked_kwargs())
        with self.assertRaises(ValueError):
            changed_event_count(
                baseline,
                valid,
                **{**locked_kwargs(), "expected_semitone_shift": 3},
            )

    def test_expected_rule_fields_must_be_all_or_none_and_fixed_bounds_cannot_change(self) -> None:
        baseline = [event(0)]
        with self.assertRaises(ValueError):
            changed_event_count(
                baseline,
                baseline,
                expected_context_signature="stepQuarter::0",
            )
        with self.assertRaises(ValueError):
            changed_event_count(
                baseline,
                baseline,
                maximum_abs_semitone_shift=11,
            )
        with self.assertRaises(ValueError):
            candidate_name("stepQuarter::0", 5, 0, 5, 2)
        with self.assertRaises(ValueError):
            candidate_name("stepQuarter::0", 5, 0, 2, 13)

        _validate_fixed_search_parameters(3, 256, 12)
        for values in ((2, 256, 12), (3, 255, 12), (3, 256, 11)):
            with self.assertRaises(ValueError):
                _validate_fixed_search_parameters(*values)


if __name__ == "__main__":
    unittest.main()
