from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODAL_DIR = ROOT / "modal"
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

from v144_rhythm_singleton_onset_replacement_policy import (  # noqa: E402
    apply_singleton_onset_replacement_rule,
    exact_singleton_onset_replacements,
    onset_matches_singleton_replacement_rule,
    rank_fit_singleton_onset_replacement_rules,
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


def reference(
    *,
    measure: int,
    step: int = 4,
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


class SingletonOnsetReplacementPolicyTests(unittest.TestCase):
    def test_construction_requires_shared_singletons_with_both_pitch_and_string_change(self) -> None:
        generated = [
            event(0, measure=1),
            event(1, measure=2),
            event(2, measure=3),
            event(3, measure=4),
            event(4, measure=4, string_index=4, fret=15, midi=60),
            event(5, measure=5, bendTargetMidi=62),
        ]
        refs = [
            reference(measure=1, string_index=2, fret=7, midi=62),
            reference(measure=2, string_index=5, fret=22, midi=62),
            reference(measure=3, string_index=2, fret=5, midi=60),
            reference(measure=4, string_index=2, fret=7, midi=62),
            reference(measure=5, string_index=2, fret=7, midi=62),
        ]
        corrections = exact_singleton_onset_replacements(generated, refs)
        self.assertEqual(
            corrections,
            [
                {
                    "measure": 1,
                    "step": 4,
                    "sourceStringIndex": 5,
                    "sourcePitchClass": 0,
                    "targetStringIndex": 2,
                    "semitoneShift": 2,
                }
            ],
        )

    def test_construction_is_deterministic_under_input_reversal(self) -> None:
        generated = [event(0, measure=1), event(1, measure=5)]
        refs = [
            reference(measure=1, string_index=2, fret=7, midi=62),
            reference(measure=5, string_index=2, fret=7, midi=62),
        ]
        forward = exact_singleton_onset_replacements(generated, refs)
        reverse = exact_singleton_onset_replacements(
            list(reversed(generated)), list(reversed(refs))
        )
        self.assertEqual(forward, reverse)

    def test_ranked_rules_are_supported_capped_and_store_explicit_nonadjacent_target(self) -> None:
        generated = [event(index, measure=measure) for index, measure in enumerate((1, 5, 9))]
        refs = [
            reference(measure=measure, string_index=2, fret=7, midi=62)
            for measure in (1, 5, 9)
        ]
        rules = rank_fit_singleton_onset_replacement_rules(
            generated,
            refs,
            minimum_correction_support=3,
            maximum_candidates=2,
        )
        self.assertTrue(rules)
        self.assertLessEqual(len(rules), 2)
        for rule in rules:
            self.assertGreaterEqual(rule["fitCorrectionSupport"], 3)
            self.assertEqual(rule["sourceStringIndex"], 5)
            self.assertEqual(rule["targetStringIndex"], 2)
            self.assertEqual(rule["semitoneShift"], 2)
            self.assertGreater(abs(rule["targetStringIndex"] - rule["sourceStringIndex"]), 1)

    def test_runtime_match_requires_exact_singleton_source_identity_and_context(self) -> None:
        note = event(0)
        self.assertTrue(
            onset_matches_singleton_replacement_rule(
                [note], "stepQuarter::0", 5, 0, 2, 2
            )
        )
        self.assertFalse(
            onset_matches_singleton_replacement_rule(
                [note], "stepQuarter::1", 5, 0, 2, 2
            )
        )
        self.assertFalse(
            onset_matches_singleton_replacement_rule(
                [note, event(1, string_index=4, fret=15, midi=60)],
                "stepQuarter::0",
                5,
                0,
                2,
                2,
            )
        )
        self.assertFalse(
            onset_matches_singleton_replacement_rule(
                [note], "stepQuarter::0", 4, 0, 2, 2
            )
        )

    def test_runtime_rewrites_nonadjacent_position_atomically_and_preserves_metadata(self) -> None:
        source = [
            event(
                0,
                duration_steps=3,
                techniques=["accent"],
                sustainTier="medium",
                confidence=0.91,
            )
        ]
        out = apply_singleton_onset_replacement_rule(
            source, "stepQuarter::0", 5, 0, 2, 2
        )
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["stringIndex"], 2)
        self.assertEqual(out[0]["midi"], 62)
        self.assertEqual(out[0]["fret"], 7)
        self.assertEqual(out[0]["eventIndex"], source[0]["eventIndex"])
        self.assertEqual(out[0]["measure"], source[0]["measure"])
        self.assertEqual(out[0]["step"], source[0]["step"])
        self.assertEqual(out[0]["durationSteps"], source[0]["durationSteps"])
        self.assertEqual(out[0]["techniques"], source[0]["techniques"])
        self.assertEqual(out[0]["sustainTier"], "medium")
        self.assertEqual(out[0]["confidence"], 0.91)

    def test_linked_or_invalid_target_is_not_rewritten(self) -> None:
        linked = [event(0, bendTargetMidi=62)]
        self.assertEqual(
            apply_singleton_onset_replacement_rule(
                linked, "stepQuarter::0", 5, 0, 2, 2
            ),
            linked,
        )

        boundary = [event(0, string_index=0, fret=36, midi=100)]
        self.assertEqual(
            apply_singleton_onset_replacement_rule(
                boundary, "stepQuarter::0", 0, 4, 5, 12
            ),
            boundary,
        )

    def test_invalid_rule_shape_shift_or_context_is_rejected(self) -> None:
        note = [event(0)]
        invalid = [
            (5, 0, 5, 2),
            (5, 0, 2, 0),
            (5, 0, 2, 13),
            (6, 0, 2, 2),
            (5, 12, 2, 2),
        ]
        for source_string, source_pitch, target_string, shift in invalid:
            with self.assertRaises(ValueError):
                apply_singleton_onset_replacement_rule(
                    note,
                    "stepQuarter::0",
                    source_string,
                    source_pitch,
                    target_string,
                    shift,
                )
        with self.assertRaises(ValueError):
            apply_singleton_onset_replacement_rule(
                note, "pitchClass::0", 5, 0, 2, 2
            )


if __name__ == "__main__":
    unittest.main()
