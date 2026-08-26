from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODAL_DIR = ROOT / "modal"
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

from v144_rhythm_pitch_step_shift_policy import (  # noqa: E402
    apply_pitch_step_rule,
    event_matches_pitch_step_rule,
    rank_fit_pitch_step_rules,
    same_measure_joint_correction_pairs,
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


def ref(*, measure: int, step: int, midi: int) -> dict:
    return {
        "measure": measure,
        "step": step,
        "stringIndex": 1,
        "fret": midi - 59,
        "midi": midi,
        "durationSteps": 1,
        "techniques": [],
    }


class JointPitchStepPolicyTests(unittest.TestCase):
    def test_pairing_removes_exact_and_requires_both_nonzero_shifts(self) -> None:
        generated = [
            event(0, measure=1, step=0, fret=1, midi=60),
            event(1, measure=1, step=4, fret=3, midi=62),
            event(2, measure=2, step=0, fret=1, midi=60),
            event(3, measure=3, step=0, fret=1, midi=60),
        ]
        reference = [
            ref(measure=1, step=0, midi=60),
            ref(measure=1, step=5, midi=64),
            ref(measure=2, step=0, midi=62),  # pitch-only: excluded
            ref(measure=3, step=1, midi=60),  # timing-only: excluded
        ]
        pairs = same_measure_joint_correction_pairs(generated, reference)
        self.assertEqual(len(pairs), 1)
        generated_row, reference_row = pairs[0]
        self.assertEqual((generated_row["measure"], generated_row["step"], generated_row["midi"]), (1, 4, 62))
        self.assertEqual((reference_row["measure"], reference_row["step"], reference_row["midi"]), (1, 5, 64))

    def test_pairing_is_deterministic_under_input_reversal(self) -> None:
        generated = [
            event(0, measure=1, step=1, fret=1, midi=60),
            event(1, measure=1, step=5, fret=5, midi=64),
        ]
        reference = [
            ref(measure=1, step=2, midi=62),
            ref(measure=1, step=6, midi=66),
        ]
        forward = same_measure_joint_correction_pairs(generated, reference)
        reverse = same_measure_joint_correction_pairs(list(reversed(generated)), list(reversed(reference)))
        compact = lambda rows: [
            (g["step"], g["midi"], r["step"], r["midi"])
            for g, r in rows
        ]
        self.assertEqual(compact(forward), compact(reverse))

    def test_ranked_rules_require_nonzero_pitch_and_step_shifts(self) -> None:
        generated = [
            event(0, measure=1, step=0, fret=1, midi=60),
            event(1, measure=5, step=0, fret=1, midi=60),
        ]
        reference = [
            ref(measure=1, step=1, midi=62),
            ref(measure=5, step=1, midi=62),
        ]
        rules = rank_fit_pitch_step_rules(
            generated,
            reference,
            minimum_correction_support=2,
            maximum_candidates=64,
        )
        self.assertTrue(rules)
        for rule in rules:
            self.assertNotEqual(rule["semitoneShift"], 0)
            self.assertNotEqual(rule["stepShift"], 0)
            self.assertGreaterEqual(rule["fitCorrectionSupport"], 2)
            self.assertGreaterEqual(rule["fitEligibleGeneratedSupport"], rule["fitCorrectionSupport"])
            self.assertGreater(rule["fitCorrectionPrecision"], 0.0)

    def test_runtime_apply_shifts_pitch_fret_and_step_only(self) -> None:
        source = event(
            0,
            measure=1,
            step=0,
            fret=1,
            midi=60,
            duration_steps=2,
            techniques=["palm-mute"],
            sustainTier="medium",
        )
        transformed = apply_pitch_step_rule(
            [source],
            ["pitchClass::0", "stepQuarter::0"],
            2,
            1,
        )
        self.assertEqual(len(transformed), 1)
        out = transformed[0]
        self.assertEqual(out["midi"], 62)
        self.assertEqual(out["fret"], 3)
        self.assertEqual(out["step"], 1)
        self.assertEqual(out["eventIndex"], source["eventIndex"])
        self.assertEqual(out["measure"], source["measure"])
        self.assertEqual(out["stringIndex"], source["stringIndex"])
        self.assertEqual(out["durationSteps"], source["durationSteps"])
        self.assertEqual(out["techniques"], source["techniques"])
        self.assertEqual(out["sustainTier"], source["sustainTier"])

    def test_linked_pitch_technique_event_is_skipped(self) -> None:
        linked = event(0, step=0, fret=1, midi=60, bendTargetMidi=62)
        out = apply_pitch_step_rule(
            [linked],
            ["pitchClass::0", "stepQuarter::0"],
            2,
            1,
        )
        self.assertEqual(out[0], linked)

    def test_out_of_range_step_or_fret_is_skipped_not_clamped(self) -> None:
        step_edge = event(0, step=15, fret=1, midi=60)
        fret_edge = event(1, step=0, fret=36, midi=95)
        out_step = apply_pitch_step_rule(
            [step_edge],
            ["pitchClass::0", "measurePhase::1"],
            2,
            1,
        )
        out_fret = apply_pitch_step_rule(
            [fret_edge],
            ["pitchClass::11", "measurePhase::1"],
            1,
            1,
        )
        self.assertEqual(out_step[0], step_edge)
        self.assertEqual(out_fret[0], fret_edge)

    def test_zero_shift_or_invalid_rule_shape_is_rejected(self) -> None:
        source = event(0)
        with self.assertRaises(ValueError):
            apply_pitch_step_rule([source], ["pitchClass::0", "stepQuarter::0"], 0, 1)
        with self.assertRaises(ValueError):
            apply_pitch_step_rule([source], ["pitchClass::0", "stepQuarter::0"], 2, 0)
        with self.assertRaises(ValueError):
            event_matches_pitch_step_rule(source, ["pitchClass::0"])
        with self.assertRaises(ValueError):
            event_matches_pitch_step_rule(source, ["stepParity::0", "stepQuarter::0"])


if __name__ == "__main__":
    unittest.main()
