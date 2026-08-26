from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODAL_DIR = ROOT / "modal"
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

from v144_rhythm_generated_only_dyad_prune_policy import (  # noqa: E402
    apply_generated_only_dyad_prune_rule,
    generated_only_dyad_corrections,
    onset_matches_generated_only_dyad_prune_rule,
    rank_fit_generated_only_dyad_prune_rules,
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


def dyad(start_index: int, *, measure: int, step: int = 4, **extra) -> list[dict]:
    return [
        event(start_index, measure=measure, step=step, string_index=1, fret=1, midi=60, **extra),
        event(start_index + 1, measure=measure, step=step, string_index=2, fret=7, midi=62),
    ]


def reference(*, measure: int, step: int, string_index: int = 1, fret: int = 1, midi: int = 60) -> dict:
    return {
        "measure": measure,
        "step": step,
        "stringIndex": string_index,
        "fret": fret,
        "midi": midi,
        "durationSteps": 1,
        "techniques": [],
    }


class GeneratedOnlyDyadPrunePolicyTests(unittest.TestCase):
    def test_construction_requires_generated_only_exact_dyad_onset(self) -> None:
        generated = [
            *dyad(0, measure=1),
            *dyad(2, measure=2),
            event(4, measure=3, step=4),
            *dyad(5, measure=4, bendTargetMidi=64),
            *dyad(7, measure=5),
            event(9, measure=5, step=4, string_index=3, fret=5, midi=60),
        ]
        refs = [reference(measure=2, step=4)]
        corrections = generated_only_dyad_corrections(generated, refs)
        self.assertEqual([[row["eventIndex"] for row in onset] for onset in corrections], [[0, 1]])

    def test_construction_and_ranking_are_deterministic_under_reversal(self) -> None:
        generated = [*dyad(0, measure=1), *dyad(2, measure=5), *dyad(4, measure=9)]
        forward = rank_fit_generated_only_dyad_prune_rules(
            generated, [], minimum_false_positive_support=3
        )
        reverse = rank_fit_generated_only_dyad_prune_rules(
            list(reversed(generated)), [], minimum_false_positive_support=3
        )
        self.assertEqual(forward, reverse)
        self.assertTrue(forward)
        self.assertGreaterEqual(forward[0]["fitFalsePositiveSupport"], 3)
        identities = {
            (forward[0]["firstSourceStringIndex"], forward[0]["firstSourcePitchClass"]),
            (forward[0]["secondSourceStringIndex"], forward[0]["secondSourcePitchClass"]),
        }
        self.assertEqual(identities, {(1, 0), (2, 2)})

    def test_rank_support_cap_and_rule_shape_are_fixed(self) -> None:
        generated = [*dyad(0, measure=1), *dyad(2, measure=5), *dyad(4, measure=9)]
        rules = rank_fit_generated_only_dyad_prune_rules(
            generated,
            [],
            minimum_false_positive_support=3,
            maximum_candidates=2,
        )
        self.assertTrue(rules)
        self.assertLessEqual(len(rules), 2)
        for rule in rules:
            self.assertGreaterEqual(rule["fitFalsePositiveSupport"], 3)
            self.assertIn("contextSignature", rule)
            self.assertIn("firstSourceStringIndex", rule)
            self.assertIn("firstSourcePitchClass", rule)
            self.assertIn("secondSourceStringIndex", rule)
            self.assertIn("secondSourcePitchClass", rule)
            self.assertNotIn("semitoneShift", rule)
            self.assertNotIn("targetStringIndex", rule)

    def test_runtime_match_requires_exact_dyad_context_and_both_source_identities(self) -> None:
        source = dyad(0, measure=1)
        self.assertTrue(
            onset_matches_generated_only_dyad_prune_rule(source, "stepQuarter::0", 2, 2, 1, 0)
        )
        self.assertFalse(
            onset_matches_generated_only_dyad_prune_rule(source, "stepQuarter::1", 1, 0, 2, 2)
        )
        self.assertFalse(
            onset_matches_generated_only_dyad_prune_rule(source, "stepQuarter::0", 1, 0, 2, 3)
        )
        self.assertFalse(
            onset_matches_generated_only_dyad_prune_rule(source[:1], "stepQuarter::0", 1, 0, 2, 2)
        )
        triad = source + [event(2, measure=1, step=4, string_index=3, fret=5, midi=60)]
        self.assertFalse(
            onset_matches_generated_only_dyad_prune_rule(triad, "stepQuarter::0", 1, 0, 2, 2)
        )

    def test_runtime_prunes_both_dyad_events_atomically_and_preserves_survivors(self) -> None:
        source = [
            *dyad(0, measure=1),
            event(2, measure=1, step=8, string_index=3, fret=5, midi=60, custom="keep-a"),
            event(3, measure=2, step=4, string_index=2, fret=5, midi=60, custom="keep-b"),
            event(4, measure=2, step=8, string_index=2, fret=7, midi=62, custom="keep-c"),
        ]
        out = apply_generated_only_dyad_prune_rule(source, "stepQuarter::0", 1, 0, 2, 2)
        self.assertEqual([row["eventIndex"] for row in out], [2, 3, 4])
        self.assertEqual([row["custom"] for row in out], ["keep-a", "keep-b", "keep-c"])
        self.assertEqual(out[0]["step"], 8)
        self.assertEqual(out[0]["midi"], 60)
        self.assertEqual(out[0]["stringIndex"], 3)

    def test_runtime_refuses_measure_erasure_linked_and_referenced_dyads(self) -> None:
        last_in_measure = [
            *dyad(0, measure=1),
            event(2, measure=2, step=8, string_index=2, fret=5, midi=60),
        ]
        self.assertEqual(
            apply_generated_only_dyad_prune_rule(last_in_measure, "stepQuarter::0", 1, 0, 2, 2),
            last_in_measure,
        )

        linked = [
            *dyad(0, measure=1, bendTargetMidi=64),
            event(2, measure=1, step=8, string_index=3, fret=5, midi=60),
        ]
        self.assertEqual(
            apply_generated_only_dyad_prune_rule(linked, "stepQuarter::0", 1, 0, 2, 2),
            linked,
        )

        referenced = [
            *dyad(0, measure=1),
            event(2, measure=1, step=8, string_index=3, fret=5, midi=60, legatoTargetEventIndex=0),
        ]
        self.assertEqual(
            apply_generated_only_dyad_prune_rule(referenced, "stepQuarter::0", 1, 0, 2, 2),
            referenced,
        )

    def test_invalid_context_string_or_pitch_class_is_rejected(self) -> None:
        source = [*dyad(0, measure=1), event(2, measure=1, step=8, string_index=3, fret=5, midi=60)]
        with self.assertRaises(ValueError):
            apply_generated_only_dyad_prune_rule(source, "pitchClass::0", 1, 0, 2, 2)
        with self.assertRaises(ValueError):
            apply_generated_only_dyad_prune_rule(source, "stepQuarter::0", 9, 0, 2, 2)
        with self.assertRaises(ValueError):
            apply_generated_only_dyad_prune_rule(source, "stepQuarter::0", 1, 12, 2, 2)


if __name__ == "__main__":
    unittest.main()
