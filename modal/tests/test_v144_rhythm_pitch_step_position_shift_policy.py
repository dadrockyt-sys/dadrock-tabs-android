from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODAL_DIR = ROOT / "modal"
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

from v144_rhythm_pitch_step_position_shift_policy import (  # noqa: E402
    apply_pitch_step_position_rule,
    event_matches_pitch_step_position_rule,
    rank_fit_pitch_step_position_rules,
    same_measure_pitch_step_position_pairs,
)


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


def ref(*, measure: int, step: int, string_index: int, fret: int, midi: int) -> dict:
    return {
        "measure": measure,
        "step": step,
        "stringIndex": string_index,
        "fret": fret,
        "midi": midi,
        "durationSteps": 1,
        "techniques": [],
    }


class PitchStepPositionPolicyTests(unittest.TestCase):
    def test_pairing_requires_all_three_nonzero_deltas(self) -> None:
        generated = [
            event(0, measure=1, step=4, string_index=1, fret=1, midi=60),
            event(1, measure=2, step=4, string_index=1, fret=1, midi=60),
            event(2, measure=3, step=4, string_index=1, fret=1, midi=60),
            event(3, measure=4, step=4, string_index=1, fret=1, midi=60),
        ]
        reference = [
            ref(measure=1, step=5, string_index=2, fret=7, midi=62),
            ref(measure=2, step=5, string_index=1, fret=3, midi=62),  # no string delta
            ref(measure=3, step=4, string_index=2, fret=7, midi=62),  # no step delta
            ref(measure=4, step=5, string_index=2, fret=5, midi=60),  # no pitch delta
        ]
        pairs = same_measure_pitch_step_position_pairs(generated, reference)
        self.assertEqual(len(pairs), 1)
        generated_row, reference_row = pairs[0]
        self.assertEqual(generated_row["measure"], 1)
        self.assertEqual(reference_row["step"], 5)
        self.assertEqual(reference_row["stringIndex"], 2)
        self.assertEqual(reference_row["midi"], 62)

    def test_pairing_is_deterministic_under_reversal(self) -> None:
        generated = [
            event(0, measure=1, step=2, string_index=1, fret=1, midi=60),
            event(1, measure=1, step=8, string_index=1, fret=5, midi=64),
        ]
        reference = [
            ref(measure=1, step=3, string_index=2, fret=7, midi=62),
            ref(measure=1, step=9, string_index=2, fret=11, midi=66),
        ]
        forward = same_measure_pitch_step_position_pairs(generated, reference)
        reverse = same_measure_pitch_step_position_pairs(list(reversed(generated)), list(reversed(reference)))
        compact = lambda rows: [
            (g["step"], g["midi"], r["step"], r["midi"], r["stringIndex"])
            for g, r in rows
        ]
        self.assertEqual(compact(forward), compact(reverse))

    def test_ranked_rules_require_all_three_nonzero_deltas(self) -> None:
        generated = [
            event(0, measure=1, step=4, string_index=1, fret=1, midi=60),
            event(1, measure=5, step=4, string_index=1, fret=1, midi=60),
        ]
        reference = [
            ref(measure=1, step=5, string_index=2, fret=7, midi=62),
            ref(measure=5, step=5, string_index=2, fret=7, midi=62),
        ]
        rules = rank_fit_pitch_step_position_rules(
            generated,
            reference,
            minimum_correction_support=2,
            maximum_candidates=64,
        )
        self.assertTrue(rules)
        for rule in rules:
            self.assertNotEqual(rule["semitoneShift"], 0)
            self.assertNotEqual(rule["stepShift"], 0)
            self.assertIn(rule["stringShift"], (-1, 1))
            self.assertGreaterEqual(rule["fitCorrectionSupport"], 2)

    def test_runtime_apply_changes_pitch_step_and_adjacent_string_together(self) -> None:
        source = event(
            0,
            measure=1,
            step=4,
            string_index=1,
            fret=1,
            midi=60,
            duration_steps=2,
            techniques=["palm-mute"],
            sustainTier="medium",
        )
        out = apply_pitch_step_position_rule(
            [source],
            ["pitchClass::0", "stepQuarter::0"],
            2,
            1,
            1,
        )[0]
        self.assertEqual(out["midi"], 62)
        self.assertEqual(out["step"], 5)
        self.assertEqual(out["stringIndex"], 2)
        self.assertEqual(out["fret"], 7)
        self.assertEqual(out["eventIndex"], source["eventIndex"])
        self.assertEqual(out["measure"], source["measure"])
        self.assertEqual(out["durationSteps"], source["durationSteps"])
        self.assertEqual(out["techniques"], source["techniques"])
        self.assertEqual(out["sustainTier"], source["sustainTier"])

    def test_linked_event_and_invalid_target_are_skipped_not_clamped(self) -> None:
        linked = event(0, step=4, string_index=1, fret=1, midi=60, bendTargetMidi=62)
        boundary = event(1, step=15, string_index=1, fret=1, midi=60)
        out_linked = apply_pitch_step_position_rule(
            [linked], ["pitchClass::0", "stepQuarter::0"], 2, 1, 1
        )
        out_boundary = apply_pitch_step_position_rule(
            [boundary], ["pitchClass::0", "stepQuarter::3"], 2, 1, 1
        )
        self.assertEqual(out_linked[0], linked)
        self.assertEqual(out_boundary[0], boundary)

    def test_zero_or_out_of_bound_shift_is_rejected(self) -> None:
        source = event(0, step=4)
        signatures = ["pitchClass::0", "stepQuarter::0"]
        cases = [
            (0, 1, 1),
            (2, 0, 1),
            (2, 1, 0),
            (13, 1, 1),
            (2, 3, 1),
            (2, 1, 2),
        ]
        for pitch_shift, step_shift, string_shift in cases:
            with self.assertRaises(ValueError):
                apply_pitch_step_position_rule(
                    [source], signatures, pitch_shift, step_shift, string_shift
                )

    def test_invalid_rule_shape_is_rejected(self) -> None:
        source = event(0)
        with self.assertRaises(ValueError):
            event_matches_pitch_step_position_rule(source, ["pitchClass::0"])
        with self.assertRaises(ValueError):
            event_matches_pitch_step_position_rule(source, ["stepParity::0", "stepQuarter::0"])


if __name__ == "__main__":
    unittest.main()
