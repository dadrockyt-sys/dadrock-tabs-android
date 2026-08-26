from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SEARCH_DIR = ROOT / "validation" / "v144_rhythm_calibration"
if str(SEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(SEARCH_DIR))

from search_contextual_pitch_shifts import candidate_name, changed_event_count  # noqa: E402


def event(
    event_index: int,
    *,
    measure: int = 1,
    step: int = 0,
    string_index: int = 1,
    fret: int = 1,
    midi: int = 60,
    duration_steps: int = 1,
    techniques: list[str] | None = None,
) -> dict:
    return {
        "eventIndex": event_index,
        "measure": measure,
        "step": step,
        "stringIndex": string_index,
        "fret": fret,
        "midi": midi,
        "durationSteps": duration_steps,
        "techniques": [] if techniques is None else list(techniques),
    }


class PitchShiftSearchInvariantTests(unittest.TestCase):
    def test_candidate_name_is_order_stable_and_shift_sensitive(self) -> None:
        left = candidate_name(["pitchClass::0", "measurePhase::1"], 2)
        right = candidate_name(["measurePhase::1", "pitchClass::0"], 2)
        other_shift = candidate_name(["pitchClass::0", "measurePhase::1"], -2)
        self.assertEqual(left, right)
        self.assertNotEqual(left, other_shift)
        self.assertTrue(left.startswith("pitch-shift-"))

    def test_valid_same_string_pitch_shift_counts_only_changed_events(self) -> None:
        baseline = [event(0), event(1, measure=2)]
        candidate = [event(0, fret=3, midi=62), event(1, measure=2)]
        self.assertEqual(changed_event_count(baseline, candidate), 1)

    def test_event_count_change_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            changed_event_count([event(0)], [event(0), event(1)])

    def test_event_order_change_is_rejected(self) -> None:
        baseline = [event(0), event(1, measure=2)]
        candidate = [event(1), event(0, measure=2)]
        with self.assertRaises(ValueError):
            changed_event_count(baseline, candidate)

    def test_non_pitch_metadata_change_is_rejected(self) -> None:
        baseline = [event(0)]
        with self.assertRaises(ValueError):
            changed_event_count(baseline, [event(0, step=1)])
        with self.assertRaises(ValueError):
            changed_event_count(baseline, [event(0, techniques=["palm-mute"])])

    def test_midi_and_fret_must_move_by_same_delta(self) -> None:
        baseline = [event(0)]
        with self.assertRaises(ValueError):
            changed_event_count(baseline, [event(0, fret=3, midi=61)])


if __name__ == "__main__":
    unittest.main()
