from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODAL_DIR = ROOT / "modal"
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

from v144_rhythm_onset_dyad_pitch_policy import (  # noqa: E402
    apply_onset_dyad_pitch_rule,
    exact_two_note_onset_dyad_corrections,
    onset_matches_dyad_rule,
    rank_fit_onset_dyad_pitch_rules,
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


def reference(
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


class OnsetDyadPitchPolicyTests(unittest.TestCase):
    def test_construction_requires_exactly_two_notes_same_strings_and_two_nonzero_shifts(self) -> None:
        generated = [
            event(0, measure=1, step=4, string_index=1, fret=1, midi=60),
            event(1, measure=1, step=4, string_index=2, fret=5, midi=60),
            event(2, measure=2, step=4, string_index=1, fret=1, midi=60),
            event(3, measure=2, step=4, string_index=2, fret=5, midi=60),
            event(4, measure=3, step=4, string_index=1, fret=1, midi=60),
            event(5, measure=3, step=4, string_index=2, fret=5, midi=60),
        ]
        refs = [
            reference(measure=1, step=4, string_index=1, fret=3, midi=62),
            reference(measure=1, step=4, string_index=2, fret=7, midi=62),
            reference(measure=2, step=4, string_index=1, fret=1, midi=60),
            reference(measure=2, step=4, string_index=2, fret=7, midi=62),
            reference(measure=3, step=4, string_index=1, fret=3, midi=62),
            reference(measure=3, step=4, string_index=3, fret=12, midi=62),
        ]
        corrections = exact_two_note_onset_dyad_corrections(generated, refs)
        self.assertEqual(len(corrections), 1)
        self.assertEqual(corrections[0]["measure"], 1)
        self.assertEqual(
            corrections[0]["noteRules"],
            [
                {"stringIndex": 1, "sourcePitchClass": 0, "semitoneShift": 2},
                {"stringIndex": 2, "sourcePitchClass": 0, "semitoneShift": 2},
            ],
        )

    def test_construction_is_deterministic_under_input_reversal(self) -> None:
        generated = [
            event(0, string_index=1, fret=1, midi=60),
            event(1, string_index=2, fret=5, midi=60),
        ]
        refs = [
            reference(measure=1, step=4, string_index=1, fret=3, midi=62),
            reference(measure=1, step=4, string_index=2, fret=8, midi=63),
        ]
        forward = exact_two_note_onset_dyad_corrections(generated, refs)
        reverse = exact_two_note_onset_dyad_corrections(list(reversed(generated)), list(reversed(refs)))
        self.assertEqual(forward, reverse)

    def test_ranked_rules_are_fit_only_stable_supported_and_capped(self) -> None:
        generated = []
        refs = []
        for offset, measure in enumerate((1, 5, 9)):
            generated.extend(
                [
                    event(offset * 2, measure=measure, string_index=1, fret=1, midi=60),
                    event(offset * 2 + 1, measure=measure, string_index=2, fret=5, midi=60),
                ]
            )
            refs.extend(
                [
                    reference(measure=measure, step=4, string_index=1, fret=3, midi=62),
                    reference(measure=measure, step=4, string_index=2, fret=7, midi=62),
                ]
            )
        rules = rank_fit_onset_dyad_pitch_rules(
            generated,
            refs,
            minimum_correction_support=3,
            maximum_candidates=2,
        )
        self.assertTrue(rules)
        self.assertLessEqual(len(rules), 2)
        for rule in rules:
            self.assertGreaterEqual(rule["fitCorrectionSupport"], 3)
            self.assertEqual(len(rule["noteRules"]), 2)
            self.assertNotEqual(rule["noteRules"][0]["semitoneShift"], 0)
            self.assertNotEqual(rule["noteRules"][1]["semitoneShift"], 0)

    def test_runtime_match_requires_exact_two_note_source_dyad_and_context(self) -> None:
        notes = [
            event(0, string_index=1, fret=1, midi=60),
            event(1, string_index=2, fret=5, midi=60),
        ]
        rules = [
            {"stringIndex": 1, "sourcePitchClass": 0, "semitoneShift": 2},
            {"stringIndex": 2, "sourcePitchClass": 0, "semitoneShift": 3},
        ]
        self.assertTrue(onset_matches_dyad_rule(notes, "stepQuarter::0", rules))
        self.assertFalse(onset_matches_dyad_rule(notes, "stepQuarter::1", rules))
        self.assertFalse(onset_matches_dyad_rule(notes + [event(2, string_index=3, fret=10, midi=60)], "stepQuarter::0", rules))

    def test_runtime_rewrites_both_notes_atomically_and_preserves_metadata(self) -> None:
        source = [
            event(0, string_index=1, fret=1, midi=60, duration_steps=2, sustainTier="medium"),
            event(1, string_index=2, fret=5, midi=60, duration_steps=3, accent=True),
        ]
        rules = [
            {"stringIndex": 1, "sourcePitchClass": 0, "semitoneShift": 2},
            {"stringIndex": 2, "sourcePitchClass": 0, "semitoneShift": 3},
        ]
        out = apply_onset_dyad_pitch_rule(source, "stepQuarter::0", rules)
        self.assertEqual(out[0]["midi"], 62)
        self.assertEqual(out[0]["fret"], 3)
        self.assertEqual(out[1]["midi"], 63)
        self.assertEqual(out[1]["fret"], 8)
        for index in (0, 1):
            self.assertEqual(out[index]["eventIndex"], source[index]["eventIndex"])
            self.assertEqual(out[index]["measure"], source[index]["measure"])
            self.assertEqual(out[index]["step"], source[index]["step"])
            self.assertEqual(out[index]["stringIndex"], source[index]["stringIndex"])
            self.assertEqual(out[index]["durationSteps"], source[index]["durationSteps"])
            self.assertEqual(out[index]["techniques"], source[index]["techniques"])
        self.assertEqual(out[0]["sustainTier"], "medium")
        self.assertTrue(out[1]["accent"])

    def test_linked_or_invalid_target_skips_whole_dyad(self) -> None:
        rules = [
            {"stringIndex": 1, "sourcePitchClass": 0, "semitoneShift": 2},
            {"stringIndex": 2, "sourcePitchClass": 0, "semitoneShift": 3},
        ]
        linked = [
            event(0, string_index=1, fret=1, midi=60, bendTargetMidi=62),
            event(1, string_index=2, fret=5, midi=60),
        ]
        self.assertEqual(apply_onset_dyad_pitch_rule(linked, "stepQuarter::0", rules), linked)

        boundary = [
            event(0, string_index=1, fret=35, midi=94),
            event(1, string_index=2, fret=5, midi=60),
        ]
        boundary_rules = [
            {"stringIndex": 1, "sourcePitchClass": 10, "semitoneShift": 2},
            {"stringIndex": 2, "sourcePitchClass": 0, "semitoneShift": 3},
        ]
        self.assertEqual(
            apply_onset_dyad_pitch_rule(boundary, "stepQuarter::0", boundary_rules),
            boundary,
        )

    def test_invalid_rule_shape_shift_or_context_is_rejected(self) -> None:
        notes = [
            event(0, string_index=1, fret=1, midi=60),
            event(1, string_index=2, fret=5, midi=60),
        ]
        valid = [
            {"stringIndex": 1, "sourcePitchClass": 0, "semitoneShift": 2},
            {"stringIndex": 2, "sourcePitchClass": 0, "semitoneShift": 3},
        ]
        invalid_rules = [
            [valid[0]],
            [valid[0], {"stringIndex": 1, "sourcePitchClass": 0, "semitoneShift": 3}],
            [valid[0], {"stringIndex": 2, "sourcePitchClass": 0, "semitoneShift": 0}],
            [valid[0], {"stringIndex": 2, "sourcePitchClass": 0, "semitoneShift": 13}],
        ]
        for rules in invalid_rules:
            with self.assertRaises(ValueError):
                apply_onset_dyad_pitch_rule(notes, "stepQuarter::0", rules)
        with self.assertRaises(ValueError):
            apply_onset_dyad_pitch_rule(notes, "pitchClass::0", valid)


if __name__ == "__main__":
    unittest.main()
