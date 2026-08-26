from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODAL_DIR = ROOT / "modal"
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

from v144_rhythm_singleton_onset_prune_policy import (  # noqa: E402
    apply_singleton_onset_prune_rule,
    onset_matches_singleton_prune_rule,
    rank_fit_singleton_onset_prune_rules,
    singleton_generated_only_corrections,
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


class SingletonOnsetPrunePolicyTests(unittest.TestCase):
    def test_construction_requires_generated_only_exact_singleton_onset(self) -> None:
        generated = [
            event(0, measure=1, step=4),
            event(1, measure=2, step=4),
            event(2, measure=3, step=4),
            event(3, measure=3, step=4, string_index=2, fret=5, midi=60),
            event(4, measure=4, step=4, bendTargetMidi=62),
        ]
        refs = [reference(measure=2, step=4)]
        corrections = singleton_generated_only_corrections(generated, refs)
        self.assertEqual([row["eventIndex"] for row in corrections], [0])

    def test_construction_and_ranking_are_deterministic_under_reversal(self) -> None:
        generated = [
            event(0, measure=1, step=4),
            event(1, measure=5, step=4),
            event(2, measure=9, step=4),
            event(3, measure=13, step=4, string_index=2, fret=5, midi=60),
        ]
        forward = rank_fit_singleton_onset_prune_rules(generated, [], minimum_false_positive_support=3)
        reverse = rank_fit_singleton_onset_prune_rules(list(reversed(generated)), [], minimum_false_positive_support=3)
        self.assertEqual(forward, reverse)
        self.assertTrue(forward)
        self.assertGreaterEqual(forward[0]["fitFalsePositiveSupport"], 3)
        self.assertEqual(forward[0]["sourceStringIndex"], 1)
        self.assertEqual(forward[0]["sourcePitchClass"], 0)

    def test_rank_support_cap_and_rule_shape_are_fixed(self) -> None:
        generated = []
        for offset, measure in enumerate((1, 5, 9)):
            generated.append(event(offset, measure=measure, step=4))
        rules = rank_fit_singleton_onset_prune_rules(
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
            self.assertIn("sourceStringIndex", rule)
            self.assertIn("sourcePitchClass", rule)
            self.assertNotIn("semitoneShift", rule)
            self.assertNotIn("targetStringIndex", rule)

    def test_runtime_match_requires_exact_singleton_context_and_source_identity(self) -> None:
        source = [event(0, measure=1, step=4)]
        self.assertTrue(onset_matches_singleton_prune_rule(source, "stepQuarter::0", 1, 0))
        self.assertFalse(onset_matches_singleton_prune_rule(source, "stepQuarter::1", 1, 0))
        self.assertFalse(onset_matches_singleton_prune_rule(source, "stepQuarter::0", 2, 0))
        self.assertFalse(onset_matches_singleton_prune_rule(source, "stepQuarter::0", 1, 1))
        self.assertFalse(
            onset_matches_singleton_prune_rule(
                source + [event(1, measure=1, step=4, string_index=2, fret=5, midi=60)],
                "stepQuarter::0",
                1,
                0,
            )
        )

    def test_runtime_prunes_matching_singleton_only_and_preserves_survivor_order_metadata(self) -> None:
        source = [
            event(0, measure=1, step=4, custom="drop"),
            event(1, measure=1, step=8, string_index=2, fret=5, midi=60, custom="keep-a"),
            event(2, measure=2, step=4, string_index=2, fret=5, midi=60, custom="keep-b"),
            event(3, measure=2, step=8, string_index=2, fret=7, midi=62, custom="keep-c"),
        ]
        out = apply_singleton_onset_prune_rule(source, "stepQuarter::0", 1, 0)
        self.assertEqual([row["eventIndex"] for row in out], [1, 2, 3])
        self.assertEqual([row["custom"] for row in out], ["keep-a", "keep-b", "keep-c"])
        self.assertEqual(out[0]["step"], 8)
        self.assertEqual(out[0]["midi"], 60)
        self.assertEqual(out[0]["stringIndex"], 2)

    def test_runtime_refuses_last_event_in_measure_linked_and_dangling_reference_targets(self) -> None:
        last_in_measure = [
            event(0, measure=1, step=4),
            event(1, measure=2, step=8, string_index=2, fret=5, midi=60),
        ]
        self.assertEqual(
            apply_singleton_onset_prune_rule(last_in_measure, "stepQuarter::0", 1, 0),
            last_in_measure,
        )

        linked = [
            event(0, measure=1, step=4, bendTargetMidi=62),
            event(1, measure=1, step=8, string_index=2, fret=5, midi=60),
        ]
        self.assertEqual(apply_singleton_onset_prune_rule(linked, "stepQuarter::0", 1, 0), linked)

        referenced = [
            event(0, measure=1, step=4),
            event(1, measure=1, step=8, string_index=2, fret=5, midi=60, legatoTargetEventIndex=0),
        ]
        self.assertEqual(apply_singleton_onset_prune_rule(referenced, "stepQuarter::0", 1, 0), referenced)

    def test_invalid_context_string_or_pitch_class_is_rejected(self) -> None:
        source = [
            event(0, measure=1, step=4),
            event(1, measure=1, step=8, string_index=2, fret=5, midi=60),
        ]
        with self.assertRaises(ValueError):
            apply_singleton_onset_prune_rule(source, "pitchClass::0", 1, 0)
        with self.assertRaises(ValueError):
            apply_singleton_onset_prune_rule(source, "stepQuarter::0", 9, 0)
        with self.assertRaises(ValueError):
            apply_singleton_onset_prune_rule(source, "stepQuarter::0", 1, 12)


if __name__ == "__main__":
    unittest.main()
