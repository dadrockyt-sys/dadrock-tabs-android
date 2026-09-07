from __future__ import annotations

import unittest

from v143_precision_polyphony_boundary import resolve_precision_polyphony


HARMONIC_INTERVALS = (12, 19, 24, 28, 31, 36)


def _evidence(
    score: float,
    *,
    attack: float | None = None,
    body: float | None = None,
) -> dict[str, float]:
    return {
        "score": float(score),
        "attack": float(score if attack is None else attack),
        "body": float(score if body is None else body),
    }


def _resolve(
    *,
    primary: int,
    precision: list[int],
    observed: list[int],
    evidence: dict[int, dict[str, float]],
):
    return resolve_precision_polyphony(
        primary_midi=primary,
        precision_midis=precision,
        observed_midis=observed,
        evidence=evidence,
        positive_attack_floor=0.0,
        positive_body_floor=-0.25,
        harmonic_intervals=HARMONIC_INTERVALS,
    )


class PrecisionPolyphonyBoundaryTest(unittest.TestCase):
    def test_recovers_weaker_observed_tone_when_joint_voicing_is_legal(self) -> None:
        decision = _resolve(
            primary=40,
            precision=[40],
            observed=[40, 47],
            evidence={40: _evidence(1.0), 47: _evidence(0.50)},
        )

        self.assertEqual(set(decision.selected_midis), {40, 47})
        self.assertEqual(decision.recovered_midis, frozenset({47}))
        self.assertEqual(decision.protected_harmonic_midi, None)
        self.assertEqual(
            len({position["stringIndex"] for position in decision.voicing.values()}),
            2,
        )

    def test_rejects_weaker_observed_tone_when_joint_voicing_is_impossible(self) -> None:
        # MIDI 87 and 88 are each playable only on the high-e string within
        # the mapper's 0-24-fret limit, so they cannot sound simultaneously.
        decision = _resolve(
            primary=87,
            precision=[87],
            observed=[87, 88],
            evidence={87: _evidence(1.0), 88: _evidence(0.60)},
        )

        self.assertEqual(decision.selected_midis, (87,))
        self.assertFalse(decision.recovered_midis)
        self.assertIn(88, decision.dropped_midis)

    def test_does_not_reintroduce_promoted_strongest_harmonic(self) -> None:
        decision = _resolve(
            primary=40,
            precision=[40],
            observed=[40, 52],
            evidence={40: _evidence(0.70), 52: _evidence(1.0)},
        )

        self.assertEqual(decision.selected_midis, (40,))
        self.assertEqual(decision.protected_harmonic_midi, 52)
        self.assertFalse(decision.recovered_midis)

    def test_does_not_recover_nonpositive_or_unobserved_pitch(self) -> None:
        decision = _resolve(
            primary=40,
            precision=[40],
            observed=[40, 47],
            evidence={
                40: _evidence(1.0),
                47: _evidence(-0.50, attack=-0.10, body=-0.50),
            },
        )

        self.assertEqual(decision.selected_midis, (40,))
        self.assertTrue(set(decision.selected_midis).issubset({40, 47}))
        self.assertNotIn(52, decision.selected_midis)

    def test_primary_is_immutable_and_simultaneous_strings_are_unique(self) -> None:
        decision = _resolve(
            primary=45,
            precision=[45, 52],
            observed=[45, 52, 57],
            evidence={
                45: _evidence(0.95),
                52: _evidence(0.90),
                57: _evidence(0.55),
            },
        )

        self.assertIn(45, decision.selected_midis)
        strings = [
            int(decision.voicing[midi]["stringIndex"])
            for midi in decision.selected_midis
        ]
        self.assertEqual(len(strings), len(set(strings)))
        self.assertTrue(set(decision.selected_midis).issubset({45, 52, 57}))


if __name__ == "__main__":
    unittest.main()
