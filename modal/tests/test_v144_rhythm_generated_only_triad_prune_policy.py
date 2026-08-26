from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODAL_DIR = ROOT / "modal"
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

from v144_rhythm_generated_only_triad_prune_policy import (  # noqa: E402
    DEFAULT_MAX_CANDIDATES,
    DEFAULT_MIN_FALSE_POSITIVE_SUPPORT,
    apply_generated_only_triad_prune_rule,
    generated_only_triad_corrections,
    onset_matches_generated_only_triad_prune_rule,
    rank_fit_generated_only_triad_prune_rules,
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


def triad(start: int, *, measure: int, step: int = 4, **extra) -> list[dict]:
    return [
        event(start, measure=measure, step=step, string_index=1, fret=1, midi=60, **extra),
        event(start + 1, measure=measure, step=step, string_index=2, fret=7, midi=62),
        event(start + 2, measure=measure, step=step, string_index=3, fret=10, midi=60),
    ]


def reference(*, measure: int, step: int) -> dict:
    return {
        "measure": measure,
        "step": step,
        "stringIndex": 1,
        "fret": 1,
        "midi": 60,
        "durationSteps": 1,
        "techniques": [],
    }


class GeneratedOnlyTriadPrunePolicyTests(unittest.TestCase):
    def test_family_defaults_are_frozen(self) -> None:
        self.assertEqual(DEFAULT_MIN_FALSE_POSITIVE_SUPPORT, 3)
        self.assertEqual(DEFAULT_MAX_CANDIDATES, 256)

    def test_construction_requires_generated_only_exact_triad_onset(self) -> None:
        generated = [
            *triad(0, measure=1),
            *triad(3, measure=2),
            event(6, measure=3, step=4),
            *triad(7, measure=4, bendTargetMidi=64),
            *triad(10, measure=5),
            event(13, measure=5, step=4, string_index=4, fret=15, midi=60),
        ]
        corrections = generated_only_triad_corrections(
            generated,
            [reference(measure=2, step=4)],
        )
        self.assertEqual(
            [[row["eventIndex"] for row in onset] for onset in corrections],
            [[0, 1, 2]],
        )

    def test_construction_and_ranking_are_deterministic_under_reversal(self) -> None:
        generated = [*triad(0, measure=1), *triad(3, measure=5), *triad(6, measure=9)]
        forward = rank_fit_generated_only_triad_prune_rules(
            generated,
            [],
            minimum_false_positive_support=DEFAULT_MIN_FALSE_POSITIVE_SUPPORT,
            maximum_candidates=DEFAULT_MAX_CANDIDATES,
        )
        reverse = rank_fit_generated_only_triad_prune_rules(
            list(reversed(generated)),
            [],
            minimum_false_positive_support=DEFAULT_MIN_FALSE_POSITIVE_SUPPORT,
            maximum_candidates=DEFAULT_MAX_CANDIDATES,
        )
        self.assertEqual(forward, reverse)
        self.assertTrue(forward)
        identities = {
            (forward[0]["firstSourceStringIndex"], forward[0]["firstSourcePitchClass"]),
            (forward[0]["secondSourceStringIndex"], forward[0]["secondSourcePitchClass"]),
            (forward[0]["thirdSourceStringIndex"], forward[0]["thirdSourcePitchClass"]),
        }
        self.assertEqual(identities, {(1, 0), (2, 2), (3, 0)})

    def test_rank_support_cap_and_rule_shape_are_fixed(self) -> None:
        generated = [*triad(0, measure=1), *triad(3, measure=5), *triad(6, measure=9)]
        rules = rank_fit_generated_only_triad_prune_rules(
            generated,
            [],
            minimum_false_positive_support=DEFAULT_MIN_FALSE_POSITIVE_SUPPORT,
            maximum_candidates=DEFAULT_MAX_CANDIDATES,
        )
        self.assertTrue(rules)
        self.assertLessEqual(len(rules), DEFAULT_MAX_CANDIDATES)
        for rule in rules:
            self.assertGreaterEqual(rule["fitFalsePositiveSupport"], DEFAULT_MIN_FALSE_POSITIVE_SUPPORT)
            self.assertIn("thirdSourceStringIndex", rule)
            self.assertIn("thirdSourcePitchClass", rule)
            self.assertNotIn("semitoneShift", rule)

    def test_runtime_match_requires_exact_triad_context_and_all_three_identities(self) -> None:
        source = triad(0, measure=1)
        self.assertTrue(
            onset_matches_generated_only_triad_prune_rule(
                source,
                "stepQuarter::0",
                3,
                0,
                1,
                0,
                2,
                2,
            )
        )
        self.assertFalse(
            onset_matches_generated_only_triad_prune_rule(
                source,
                "stepQuarter::1",
                1,
                0,
                2,
                2,
                3,
                0,
            )
        )
        self.assertFalse(
            onset_matches_generated_only_triad_prune_rule(
                source,
                "stepQuarter::0",
                1,
                0,
                2,
                2,
                3,
                1,
            )
        )
        self.assertFalse(
            onset_matches_generated_only_triad_prune_rule(
                source[:2],
                "stepQuarter::0",
                1,
                0,
                2,
                2,
                3,
                0,
            )
        )
        four = source + [
            event(3, measure=1, step=4, string_index=4, fret=15, midi=60)
        ]
        self.assertFalse(
            onset_matches_generated_only_triad_prune_rule(
                four,
                "stepQuarter::0",
                1,
                0,
                2,
                2,
                3,
                0,
            )
        )

    def test_runtime_prunes_three_events_atomically_and_preserves_survivors(self) -> None:
        source = [
            *triad(0, measure=1),
            event(
                3,
                measure=1,
                step=8,
                string_index=4,
                fret=15,
                midi=60,
                custom="keep-a",
            ),
            event(
                4,
                measure=2,
                step=8,
                string_index=2,
                fret=5,
                midi=60,
                custom="keep-b",
            ),
        ]
        out = apply_generated_only_triad_prune_rule(
            source,
            "stepQuarter::0",
            1,
            0,
            2,
            2,
            3,
            0,
        )
        self.assertEqual([row["eventIndex"] for row in out], [3, 4])
        self.assertEqual([row["custom"] for row in out], ["keep-a", "keep-b"])
        self.assertEqual(out[0]["durationSteps"], 1)

    def test_runtime_refuses_measure_erasure_linked_and_referenced_triads(self) -> None:
        last_measure = [
            *triad(0, measure=1),
            event(3, measure=2, step=8, string_index=2, fret=5, midi=60),
        ]
        self.assertEqual(
            apply_generated_only_triad_prune_rule(
                last_measure,
                "stepQuarter::0",
                1,
                0,
                2,
                2,
                3,
                0,
            ),
            last_measure,
        )

        linked = [
            *triad(0, measure=1, bendTargetMidi=64),
            event(3, measure=1, step=8, string_index=4, fret=15, midi=60),
        ]
        self.assertEqual(
            apply_generated_only_triad_prune_rule(
                linked,
                "stepQuarter::0",
                1,
                0,
                2,
                2,
                3,
                0,
            ),
            linked,
        )

        referenced = [
            *triad(0, measure=1),
            event(
                3,
                measure=1,
                step=8,
                string_index=4,
                fret=15,
                midi=60,
                legatoTargetEventIndex=0,
            ),
        ]
        self.assertEqual(
            apply_generated_only_triad_prune_rule(
                referenced,
                "stepQuarter::0",
                1,
                0,
                2,
                2,
                3,
                0,
            ),
            referenced,
        )

    def test_invalid_context_string_or_pitch_class_is_rejected(self) -> None:
        source = [
            *triad(0, measure=1),
            event(3, measure=1, step=8, string_index=4, fret=15, midi=60),
        ]
        with self.assertRaises(ValueError):
            apply_generated_only_triad_prune_rule(
                source,
                "pitchClass::0",
                1,
                0,
                2,
                2,
                3,
                0,
            )
        with self.assertRaises(ValueError):
            apply_generated_only_triad_prune_rule(
                source,
                "stepQuarter::0",
                9,
                0,
                2,
                2,
                3,
                0,
            )
        with self.assertRaises(ValueError):
            apply_generated_only_triad_prune_rule(
                source,
                "stepQuarter::0",
                1,
                0,
                2,
                12,
                3,
                0,
            )


if __name__ == "__main__":
    unittest.main()
