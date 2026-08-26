from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODAL_DIR = ROOT / "modal"
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

from v144_rhythm_pitch_position_shift_policy import (  # noqa: E402
    apply_pitch_position_rule,
    event_matches_pitch_position_rule,
    rank_fit_pitch_position_rules,
    same_onset_pitch_position_pairs,
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


def ref(
    *,
    measure: int,
    step: int,
    string_index: int,
    fret: int,
    midi: int,
) -> dict:
    return {
        "measure": measure,
        "step": step,
        "stringIndex": string_index,
        "fret": fret,
        "midi": midi,
        "durationSteps": 1,
        "techniques": [],
    }


class JointPitchPositionPolicyTests(unittest.TestCase):
    def test_pairing_requires_wrong_pitch_and_adjacent_string_target(self) -> None:
        generated = [
            event(0, measure=1, step=0, string_index=1, fret=1, midi=60),
            event(1, measure=2, step=0, string_index=1, fret=1, midi=60),
            event(2, measure=3, step=0, string_index=1, fret=1, midi=60),
        ]
        reference = [
            ref(measure=1, step=0, string_index=2, fret=7, midi=62),
            ref(measure=2, step=0, string_index=1, fret=3, midi=62),  # pitch-only: excluded
            ref(measure=3, step=0, string_index=3, fret=12, midi=62),  # two strings away: excluded
        ]
        pairs = same_onset_pitch_position_pairs(generated, reference)
        self.assertEqual(len(pairs), 1)
        generated_row, reference_row = pairs[0]
        self.assertEqual(generated_row["measure"], 1)
        self.assertEqual(reference_row["stringIndex"], 2)
        self.assertEqual(reference_row["fret"], 7)
        self.assertEqual(reference_row["midi"], 62)

    def test_pairing_is_deterministic_under_input_reversal(self) -> None:
        generated = [
            event(0, measure=1, step=0, string_index=1, fret=1, midi=60),
            event(1, measure=1, step=0, string_index=1, fret=5, midi=64),
        ]
        reference = [
            ref(measure=1, step=0, string_index=2, fret=7, midi=62),
            ref(measure=1, step=0, string_index=2, fret=11, midi=66),
        ]
        forward = same_onset_pitch_position_pairs(generated, reference)
        reverse = same_onset_pitch_position_pairs(list(reversed(generated)), list(reversed(reference)))
        compact = lambda rows: [
            (g["midi"], g["stringIndex"], r["midi"], r["stringIndex"], r["fret"])
            for g, r in rows
        ]
        self.assertEqual(compact(forward), compact(reverse))

    def test_ranked_rules_require_nonzero_pitch_and_adjacent_string_shifts(self) -> None:
        generated = [
            event(0, measure=1, step=0, string_index=1, fret=1, midi=60),
            event(1, measure=5, step=0, string_index=1, fret=1, midi=60),
        ]
        reference = [
            ref(measure=1, step=0, string_index=2, fret=7, midi=62),
            ref(measure=5, step=0, string_index=2, fret=7, midi=62),
        ]
        rules = rank_fit_pitch_position_rules(
            generated,
            reference,
            minimum_correction_support=2,
            maximum_candidates=64,
        )
        self.assertTrue(rules)
        for rule in rules:
            self.assertNotEqual(rule["semitoneShift"], 0)
            self.assertIn(rule["stringShift"], (-1, 1))
            self.assertGreaterEqual(rule["fitCorrectionSupport"], 2)
            self.assertGreaterEqual(rule["fitEligibleGeneratedSupport"], rule["fitCorrectionSupport"])
            self.assertGreater(rule["fitCorrectionPrecision"], 0.0)

    def test_runtime_apply_revoices_pitch_and_position_without_changing_timing(self) -> None:
        source = event(
            0,
            measure=1,
            step=0,
            string_index=1,
            fret=1,
            midi=60,
            duration_steps=2,
            techniques=["palm-mute"],
            sustainTier="medium",
        )
        transformed = apply_pitch_position_rule(
            [source],
            ["pitchClass::0", "stepQuarter::0"],
            2,
            1,
        )
        self.assertEqual(len(transformed), 1)
        out = transformed[0]
        self.assertEqual(out["midi"], 62)
        self.assertEqual(out["stringIndex"], 2)
        self.assertEqual(out["fret"], 7)
        self.assertEqual(out["step"], source["step"])
        self.assertEqual(out["eventIndex"], source["eventIndex"])
        self.assertEqual(out["measure"], source["measure"])
        self.assertEqual(out["durationSteps"], source["durationSteps"])
        self.assertEqual(out["techniques"], source["techniques"])
        self.assertEqual(out["sustainTier"], source["sustainTier"])

    def test_target_fret_is_recomputed_from_tuning_not_shifted_naively(self) -> None:
        source = event(0, string_index=1, fret=1, midi=60)
        out = apply_pitch_position_rule(
            [source],
            ["pitchClass::0", "stepQuarter::0"],
            4,
            -1,
        )[0]
        self.assertEqual(out["midi"], 64)
        self.assertEqual(out["stringIndex"], 0)
        self.assertEqual(out["fret"], 0)

    def test_linked_pitch_technique_event_is_skipped(self) -> None:
        linked = event(0, string_index=1, fret=1, midi=60, bendTargetMidi=62)
        out = apply_pitch_position_rule(
            [linked],
            ["pitchClass::0", "stepQuarter::0"],
            2,
            1,
        )
        self.assertEqual(out[0], linked)

    def test_out_of_range_target_string_or_fret_is_skipped_not_clamped(self) -> None:
        high_string = event(0, string_index=0, fret=0, midi=64)
        low_fret_target = event(1, string_index=0, fret=0, midi=64)
        out_string = apply_pitch_position_rule(
            [high_string],
            ["pitchClass::4", "stepQuarter::0"],
            2,
            -1,
        )
        out_fret = apply_pitch_position_rule(
            [low_fret_target],
            ["pitchClass::4", "stepQuarter::0"],
            -12,
            1,
        )
        self.assertEqual(out_string[0], high_string)
        self.assertEqual(out_fret[0], low_fret_target)

    def test_zero_shift_nonadjacent_shift_or_invalid_rule_shape_is_rejected(self) -> None:
        source = event(0)
        with self.assertRaises(ValueError):
            apply_pitch_position_rule([source], ["pitchClass::0", "stepQuarter::0"], 0, 1)
        with self.assertRaises(ValueError):
            apply_pitch_position_rule([source], ["pitchClass::0", "stepQuarter::0"], 2, 0)
        with self.assertRaises(ValueError):
            apply_pitch_position_rule([source], ["pitchClass::0", "stepQuarter::0"], 2, 2)
        with self.assertRaises(ValueError):
            event_matches_pitch_position_rule(source, ["pitchClass::0"])
        with self.assertRaises(ValueError):
            event_matches_pitch_position_rule(source, ["stepParity::0", "stepQuarter::0"])


if __name__ == "__main__":
    unittest.main()
