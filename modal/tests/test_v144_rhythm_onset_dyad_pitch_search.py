from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SEARCH_DIR = ROOT / "validation" / "v144_rhythm_calibration"
if str(SEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(SEARCH_DIR))

from search_atomic_onset_dyad_pitch_rewrites import candidate_name, changed_event_count  # noqa: E402


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


def rules(shift1: int = 2, shift2: int = 2) -> list[dict]:
    return [
        {"stringIndex": 1, "sourcePitchClass": 0, "semitoneShift": shift1},
        {"stringIndex": 2, "sourcePitchClass": 0, "semitoneShift": shift2},
    ]


class AtomicOnsetDyadPitchSearchInvariantTests(unittest.TestCase):
    def test_candidate_name_is_note_order_stable_and_rule_sensitive(self) -> None:
        base_rules = rules(2, 3)
        left = candidate_name("stepQuarter::0", base_rules)
        right = candidate_name("stepQuarter::0", list(reversed(base_rules)))
        other_context = candidate_name("stepParity::0", base_rules)
        other_shift = candidate_name("stepQuarter::0", rules(2, 4))
        self.assertEqual(left, right)
        self.assertNotEqual(left, other_context)
        self.assertNotEqual(left, other_shift)
        self.assertTrue(left.startswith("onset-dyad-pitch-"))

    def test_valid_atomic_two_event_change_counts_both_events(self) -> None:
        baseline = [
            event(0, string_index=1, fret=1, midi=60),
            event(1, string_index=2, fret=5, midi=60),
            event(2, measure=2, string_index=1, fret=1, midi=60),
        ]
        candidate = [
            event(0, string_index=1, fret=3, midi=62),
            event(1, string_index=2, fret=7, midi=62),
            event(2, measure=2, string_index=1, fret=1, midi=60),
        ]
        self.assertEqual(
            changed_event_count(
                baseline,
                candidate,
                expected_context_signature="stepQuarter::0",
                expected_note_rules=rules(),
            ),
            2,
        )

    def test_partial_single_event_change_is_rejected(self) -> None:
        baseline = [
            event(0, string_index=1, fret=1, midi=60),
            event(1, string_index=2, fret=5, midi=60),
        ]
        candidate = [
            event(0, string_index=1, fret=3, midi=62),
            event(1, string_index=2, fret=5, midi=60),
        ]
        with self.assertRaises(ValueError):
            changed_event_count(baseline, candidate)

    def test_changed_onset_must_have_exactly_two_baseline_events(self) -> None:
        baseline = [
            event(0, string_index=1, fret=1, midi=60),
            event(1, string_index=2, fret=5, midi=60),
            event(2, string_index=3, fret=10, midi=60),
        ]
        candidate = [
            event(0, string_index=1, fret=3, midi=62),
            event(1, string_index=2, fret=7, midi=62),
            event(2, string_index=3, fret=10, midi=60),
        ]
        with self.assertRaises(ValueError):
            changed_event_count(baseline, candidate)

    def test_event_count_order_and_protected_metadata_are_enforced(self) -> None:
        baseline = [
            event(0, string_index=1, fret=1, midi=60, sustainTier="short"),
            event(1, string_index=2, fret=5, midi=60),
        ]
        with self.assertRaises(ValueError):
            changed_event_count(baseline, baseline + [event(2)])
        with self.assertRaises(ValueError):
            changed_event_count(baseline, [event(1), event(0, string_index=2, fret=5, midi=60)])

        variants = [
            [event(0, string_index=1, fret=3, midi=62, step=5, sustainTier="short"), event(1, string_index=2, fret=7, midi=62)],
            [event(0, string_index=2, fret=7, midi=62, sustainTier="short"), event(1, string_index=1, fret=3, midi=62)],
            [event(0, string_index=1, fret=3, midi=62, duration_steps=2, sustainTier="short"), event(1, string_index=2, fret=7, midi=62)],
            [event(0, string_index=1, fret=3, midi=62, techniques=["palm-mute"], sustainTier="short"), event(1, string_index=2, fret=7, midi=62)],
            [event(0, string_index=1, fret=3, midi=62, sustainTier="long"), event(1, string_index=2, fret=7, midi=62)],
        ]
        for candidate in variants:
            with self.assertRaises(ValueError):
                changed_event_count(baseline, candidate)

    def test_tuning_identity_and_midi_fret_delta_are_required(self) -> None:
        baseline = [
            event(0, string_index=1, fret=1, midi=60),
            event(1, string_index=2, fret=5, midi=60),
        ]
        bad_tuning = [
            event(0, string_index=1, fret=2, midi=62),
            event(1, string_index=2, fret=7, midi=62),
        ]
        with self.assertRaises(ValueError):
            changed_event_count(baseline, bad_tuning)

    def test_locked_context_source_pitch_classes_and_deltas_are_enforced(self) -> None:
        baseline = [
            event(0, string_index=1, fret=1, midi=60),
            event(1, string_index=2, fret=5, midi=60),
        ]
        candidate = [
            event(0, string_index=1, fret=3, midi=62),
            event(1, string_index=2, fret=7, midi=62),
        ]
        with self.assertRaises(ValueError):
            changed_event_count(
                baseline,
                candidate,
                expected_context_signature="stepQuarter::1",
                expected_note_rules=rules(),
            )
        wrong_pc = [
            {"stringIndex": 1, "sourcePitchClass": 1, "semitoneShift": 2},
            {"stringIndex": 2, "sourcePitchClass": 0, "semitoneShift": 2},
        ]
        with self.assertRaises(ValueError):
            changed_event_count(
                baseline,
                candidate,
                expected_context_signature="stepQuarter::0",
                expected_note_rules=wrong_pc,
            )
        with self.assertRaises(ValueError):
            changed_event_count(
                baseline,
                candidate,
                expected_context_signature="stepQuarter::0",
                expected_note_rules=rules(2, 3),
            )

    def test_expected_context_and_rules_must_be_supplied_together_and_bounded(self) -> None:
        baseline = [
            event(0, string_index=1, fret=1, midi=60),
            event(1, string_index=2, fret=5, midi=60),
        ]
        with self.assertRaises(ValueError):
            changed_event_count(baseline, baseline, expected_context_signature="stepQuarter::0")
        with self.assertRaises(ValueError):
            changed_event_count(baseline, baseline, expected_note_rules=rules())
        with self.assertRaises(ValueError):
            changed_event_count(
                baseline,
                baseline,
                expected_context_signature="stepQuarter::0",
                expected_note_rules=rules(13, 2),
            )


if __name__ == "__main__":
    unittest.main()
