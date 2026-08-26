from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODAL_DIR = ROOT / "modal"
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

from v144_rhythm_pitch_shift_policy import (  # noqa: E402
    apply_pitch_shift_rule,
    event_matches_pitch_shift_rule,
    has_pitch_linkage,
    rank_fit_pitch_shift_rules,
    same_onset_substitution_pairs,
)


def generated_note(measure: int, step: int, midi: int, string_index: int, fret: int, **extra) -> dict:
    payload = {
        "measure": measure,
        "step": step,
        "midi": midi,
        "stringIndex": string_index,
        "fret": fret,
        "durationSteps": 1,
        "techniques": [],
    }
    payload.update(extra)
    return payload


def reference_note(measure: int, step: int, midi: int) -> dict:
    return {"measure": measure, "step": step, "midi": midi}


class PitchShiftPolicyTests(unittest.TestCase):
    def test_same_onset_pairing_removes_exact_pitch_before_substitution(self) -> None:
        generated = [
            generated_note(1, 0, 60, 1, 1),
            generated_note(1, 0, 62, 1, 3),
        ]
        reference = [reference_note(1, 0, 60), reference_note(1, 0, 64)]
        pairs = same_onset_substitution_pairs(generated, reference)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0][0]["midi"], 62)
        self.assertEqual(pairs[0][1]["midi"], 64)

    def test_rank_uses_pitch_class_plus_context_and_fit_support(self) -> None:
        generated = [
            generated_note(1, 0, 60, 1, 1),
            generated_note(5, 0, 60, 1, 1),
            generated_note(9, 0, 60, 1, 1),
        ]
        reference = [
            reference_note(1, 0, 62),
            reference_note(5, 0, 62),
            reference_note(9, 0, 62),
        ]
        candidates = rank_fit_pitch_shift_rules(generated, reference)
        self.assertTrue(candidates)
        target = next(
            item
            for item in candidates
            if set(item["signatures"]) == {"pitchClass::0", "measurePhase::1"}
            and item["semitoneShift"] == 2
        )
        self.assertEqual(target["fitCorrectionSupport"], 3)
        self.assertEqual(target["fitEligibleGeneratedSupport"], 3)
        self.assertEqual(target["fitCorrectionPrecision"], 1.0)

    def test_runtime_apply_is_reference_free_count_preserving_and_position_consistent(self) -> None:
        events = [
            generated_note(1, 0, 60, 1, 1),
            generated_note(2, 0, 60, 1, 1),
            generated_note(5, 0, 60, 1, 1),
        ]
        transformed = apply_pitch_shift_rule(
            events,
            ["pitchClass::0", "measurePhase::1"],
            2,
        )
        self.assertEqual(len(transformed), len(events))
        self.assertEqual(
            [(row["measure"], row["step"]) for row in transformed],
            [(row["measure"], row["step"]) for row in events],
        )
        self.assertEqual((transformed[0]["midi"], transformed[0]["fret"]), (62, 3))
        self.assertEqual((transformed[1]["midi"], transformed[1]["fret"]), (60, 1))
        self.assertEqual((transformed[2]["midi"], transformed[2]["fret"]), (62, 3))
        for row in transformed:
            self.assertEqual(row["midi"], {0: 64, 1: 59, 2: 55, 3: 50, 4: 45, 5: 40}[row["stringIndex"]] + row["fret"])

    def test_linked_bend_legato_and_slide_events_are_never_shifted(self) -> None:
        bend = generated_note(
            1, 0, 60, 1, 1,
            bendSemitones=2.0,
            bendTargetFret=3,
            bendTargetMidi=62,
        )
        legato = generated_note(
            1, 0, 60, 1, 1,
            legatoTargetEventIndex=99,
            legatoTargetFret=3,
            legatoTargetMidi=62,
        )
        slide = generated_note(1, 0, 60, 1, 1)
        slide["techniques"] = ["slide"]
        plain = generated_note(1, 0, 60, 1, 1)
        transformed = apply_pitch_shift_rule(
            [bend, legato, slide, plain],
            ["pitchClass::0", "measurePhase::1"],
            2,
        )
        self.assertEqual(transformed[0], bend)
        self.assertEqual(transformed[1], legato)
        self.assertEqual(transformed[2], slide)
        self.assertEqual((transformed[3]["midi"], transformed[3]["fret"]), (62, 3))
        self.assertTrue(has_pitch_linkage(bend))
        self.assertTrue(has_pitch_linkage(legato))
        self.assertTrue(has_pitch_linkage(slide))
        self.assertFalse(has_pitch_linkage(plain))

    def test_out_of_range_fret_shift_leaves_matching_event_unchanged(self) -> None:
        event = generated_note(1, 0, 99, 0, 35)
        transformed = apply_pitch_shift_rule(
            [event],
            ["pitchClass::3", "measurePhase::1"],
            2,
        )
        self.assertEqual(transformed, [event])

    def test_rule_shape_and_shift_bounds_are_enforced(self) -> None:
        event = generated_note(1, 0, 60, 1, 1)
        with self.assertRaises(ValueError):
            event_matches_pitch_shift_rule(event, ["measurePhase::1", "stepParity::0"])
        with self.assertRaises(ValueError):
            event_matches_pitch_shift_rule(event, ["pitchClass::0"])
        with self.assertRaises(ValueError):
            apply_pitch_shift_rule([event], ["pitchClass::0", "measurePhase::1"], 0)
        with self.assertRaises(ValueError):
            apply_pitch_shift_rule([event], ["pitchClass::0", "measurePhase::1"], 13)


if __name__ == "__main__":
    unittest.main()
