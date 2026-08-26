from __future__ import annotations

from pathlib import Path
import copy
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODAL_DIR = ROOT / "modal"
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

from v144_rhythm_shared_dyad_surplus_prune_policy import (  # noqa: E402
    apply_shared_dyad_surplus_prune_rule,
    onset_matches_shared_dyad_surplus_prune_rule,
    rank_fit_shared_dyad_surplus_prune_rules,
    shared_dyad_surplus_corrections,
)


def event(
    event_index: int,
    *,
    measure: int = 1,
    step: int = 4,
    string_index: int = 1,
    fret: int = 1,
    midi: int = 60,
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
        "durationSteps": 1,
        "techniques": [] if techniques is None else list(techniques),
    }
    row.update(extra)
    return row


def dyad(start_index: int, *, measure: int, step: int = 4, **first_extra) -> list[dict]:
    return [
        event(start_index, measure=measure, step=step, string_index=1, fret=1, midi=60, **first_extra),
        event(start_index + 1, measure=measure, step=step, string_index=2, fret=7, midi=62),
    ]


def reference(*, measure: int, step: int = 4, midi: int = 60) -> dict:
    return {
        "measure": measure,
        "step": step,
        "stringIndex": 1,
        "fret": 1,
        "midi": midi,
        "durationSteps": 1,
        "techniques": [],
    }


class SharedDyadSurplusPrunePolicyTests(unittest.TestCase):
    def test_construction_requires_exact_g2_r1_with_one_exact_midi_survivor(self) -> None:
        generated = [
            *dyad(0, measure=1),
            *dyad(2, measure=2),
            *dyad(4, measure=3),
            *dyad(6, measure=4),
            event(8, measure=5, step=4, string_index=1, fret=1, midi=60),
            *dyad(9, measure=6, bendTargetMidi=64),
            *dyad(11, measure=7),
            event(13, measure=7, step=8, string_index=3, fret=5, midi=60, legatoTargetEventIndex=12),
        ]
        refs = [
            reference(measure=1, midi=60),
            reference(measure=2, midi=61),
            reference(measure=3, midi=60),
            reference(measure=3, midi=62),
            reference(measure=4, midi=60),
            reference(measure=4, midi=60),
            reference(measure=5, midi=60),
            reference(measure=6, midi=60),
            reference(measure=7, midi=60),
        ]
        corrections = shared_dyad_surplus_corrections(generated, refs)
        self.assertEqual(len(corrections), 1)
        self.assertEqual(corrections[0]["survivorEvent"]["eventIndex"], 0)
        self.assertEqual(corrections[0]["pruneEvent"]["eventIndex"], 1)

    def test_duplicate_source_identity_is_excluded_as_ambiguous(self) -> None:
        generated = [
            event(0, measure=1, string_index=1, fret=1, midi=60),
            event(1, measure=1, string_index=1, fret=13, midi=72),
        ]
        refs = [reference(measure=1, midi=60)]
        self.assertEqual(shared_dyad_surplus_corrections(generated, refs), [])

    def test_construction_and_ranking_are_deterministic_under_reversal(self) -> None:
        generated = [*dyad(0, measure=1), *dyad(2, measure=5), *dyad(4, measure=9)]
        refs = [reference(measure=1), reference(measure=5), reference(measure=9)]
        forward = rank_fit_shared_dyad_surplus_prune_rules(
            generated, refs, minimum_correction_support=3
        )
        reverse = rank_fit_shared_dyad_surplus_prune_rules(
            list(reversed(generated)), list(reversed(refs)), minimum_correction_support=3
        )
        self.assertEqual(forward, reverse)
        self.assertTrue(forward)
        self.assertGreaterEqual(forward[0]["fitCorrectionSupport"], 3)
        self.assertEqual(
            (forward[0]["pruneSourceStringIndex"], forward[0]["pruneSourcePitchClass"]),
            (2, 2),
        )

    def test_rank_support_cap_and_rule_shape_are_fixed(self) -> None:
        generated = [*dyad(0, measure=1), *dyad(2, measure=5), *dyad(4, measure=9)]
        refs = [reference(measure=1), reference(measure=5), reference(measure=9)]
        rules = rank_fit_shared_dyad_surplus_prune_rules(
            generated,
            refs,
            minimum_correction_support=3,
            maximum_candidates=2,
        )
        self.assertTrue(rules)
        self.assertLessEqual(len(rules), 2)
        for rule in rules:
            self.assertGreaterEqual(rule["fitCorrectionSupport"], 3)
            self.assertIn("contextSignature", rule)
            self.assertIn("firstSourceStringIndex", rule)
            self.assertIn("firstSourcePitchClass", rule)
            self.assertIn("secondSourceStringIndex", rule)
            self.assertIn("secondSourcePitchClass", rule)
            self.assertIn("pruneSourceStringIndex", rule)
            self.assertIn("pruneSourcePitchClass", rule)
            self.assertNotIn("targetMidi", rule)
            self.assertNotIn("referenceMidi", rule)
            self.assertNotIn("semitoneShift", rule)

    def test_runtime_match_requires_exact_dyad_context_complete_identity_and_unique_prune_member(self) -> None:
        source = dyad(0, measure=1)
        self.assertTrue(
            onset_matches_shared_dyad_surplus_prune_rule(
                source, "stepQuarter::0", 2, 2, 1, 0, 2, 2
            )
        )
        self.assertFalse(
            onset_matches_shared_dyad_surplus_prune_rule(
                source, "stepQuarter::1", 1, 0, 2, 2, 2, 2
            )
        )
        self.assertFalse(
            onset_matches_shared_dyad_surplus_prune_rule(
                source, "stepQuarter::0", 1, 0, 2, 3, 2, 3
            )
        )
        self.assertFalse(
            onset_matches_shared_dyad_surplus_prune_rule(
                source[:1], "stepQuarter::0", 1, 0, 2, 2, 2, 2
            )
        )

    def test_runtime_prunes_only_surplus_member_and_preserves_survivor_and_order(self) -> None:
        source = [
            event(0, measure=1, step=4, string_index=1, fret=1, midi=60, custom="survivor"),
            event(1, measure=1, step=4, string_index=2, fret=7, midi=62, custom="prune"),
            event(2, measure=1, step=8, string_index=3, fret=5, midi=60, custom="keep-a"),
            event(3, measure=2, step=4, string_index=2, fret=5, midi=60, custom="keep-b"),
        ]
        expected_survivor = copy.deepcopy(source[0])
        out = apply_shared_dyad_surplus_prune_rule(
            source, "stepQuarter::0", 1, 0, 2, 2, 2, 2
        )
        self.assertEqual([row["eventIndex"] for row in out], [0, 2, 3])
        self.assertEqual(out[0], expected_survivor)
        self.assertEqual([row["custom"] for row in out], ["survivor", "keep-a", "keep-b"])

    def test_runtime_refuses_linked_referenced_or_invalid_dyad(self) -> None:
        linked = [
            *dyad(0, measure=1, bendTargetMidi=64),
            event(2, measure=1, step=8, string_index=3, fret=5, midi=60),
        ]
        self.assertEqual(
            apply_shared_dyad_surplus_prune_rule(
                linked, "stepQuarter::0", 1, 0, 2, 2, 2, 2
            ),
            linked,
        )

        referenced = [
            *dyad(0, measure=1),
            event(2, measure=1, step=8, string_index=3, fret=5, midi=60, legatoTargetEventIndex=1),
        ]
        self.assertEqual(
            apply_shared_dyad_surplus_prune_rule(
                referenced, "stepQuarter::0", 1, 0, 2, 2, 2, 2
            ),
            referenced,
        )

        invalid = [
            event(0, measure=1, step=4, string_index=1, fret=2, midi=60),
            event(1, measure=1, step=4, string_index=2, fret=7, midi=62),
            event(2, measure=1, step=8, string_index=3, fret=5, midi=60),
        ]
        self.assertEqual(
            apply_shared_dyad_surplus_prune_rule(
                invalid, "stepQuarter::0", 1, 0, 2, 2, 2, 2
            ),
            invalid,
        )

    def test_invalid_context_pitch_class_or_prune_identity_is_rejected(self) -> None:
        source = [*dyad(0, measure=1), event(2, measure=1, step=8, string_index=3, fret=5, midi=60)]
        with self.assertRaises(ValueError):
            apply_shared_dyad_surplus_prune_rule(
                source, "pitchClass::0", 1, 0, 2, 2, 2, 2
            )
        with self.assertRaises(ValueError):
            apply_shared_dyad_surplus_prune_rule(
                source, "stepQuarter::0", 1, 0, 2, 12, 2, 2
            )
        with self.assertRaises(ValueError):
            apply_shared_dyad_surplus_prune_rule(
                source, "stepQuarter::0", 1, 0, 2, 2, 3, 0
            )
        with self.assertRaises(ValueError):
            apply_shared_dyad_surplus_prune_rule(
                source, "stepQuarter::0", 1, 0, 1, 0, 1, 0
            )

    def test_policy_does_not_mutate_fit_inputs(self) -> None:
        generated = [*dyad(0, measure=1), *dyad(2, measure=5), *dyad(4, measure=9)]
        refs = [reference(measure=1), reference(measure=5), reference(measure=9)]
        generated_before = copy.deepcopy(generated)
        refs_before = copy.deepcopy(refs)
        rank_fit_shared_dyad_surplus_prune_rules(generated, refs, minimum_correction_support=3)
        self.assertEqual(generated, generated_before)
        self.assertEqual(refs, refs_before)


if __name__ == "__main__":
    unittest.main()
