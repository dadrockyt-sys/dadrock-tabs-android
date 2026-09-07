from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from v143_rhythm_guitar_note_mapper import (
    MAX_CHORD_NOTES,
    resolve_joint_chord_voicing,
)


@dataclass(frozen=True)
class PrecisionPolyphonyDecision:
    selected_midis: tuple[int, ...]
    candidate_midis: tuple[int, ...]
    recovered_midis: frozenset[int]
    dropped_midis: frozenset[int]
    protected_harmonic_midi: int | None
    voicing: dict[int, dict[str, Any]]


def _ranked_midis(
    midis: Sequence[int],
    evidence: Mapping[int, Mapping[str, float]],
) -> list[int]:
    return sorted(
        {int(midi) for midi in midis},
        key=lambda midi: (
            -float(evidence[int(midi)]["score"]),
            -float(evidence[int(midi)]["attack"]),
            -float(evidence[int(midi)]["body"]),
            int(midi),
        ),
    )


def resolve_precision_polyphony(
    *,
    primary_midi: int,
    precision_midis: Sequence[int],
    observed_midis: Sequence[int],
    evidence: Mapping[int, Mapping[str, float]],
    positive_attack_floor: float,
    positive_body_floor: float,
    harmonic_intervals: Sequence[int],
) -> PrecisionPolyphonyDecision:
    """Resolve a playable voicing without treating confidence as feasibility.

    Precision-retained pitches keep priority. A weaker pitch may be recovered only
    when it was already observed at the same attack, has positive two-view physical
    evidence, and the whole selected set remains a legal six-string voicing.

    One deterministic contradiction remains protected: when the explicit primary
    was promoted below the strongest positive raw pitch and that strongest pitch is
    an upper harmonic-family interval, the strongest upper is not reintroduced as
    an independent chord tone. This mirrors the promoted-harmonic guard.
    """
    primary = int(primary_midi)
    precision = tuple(sorted({int(value) for value in precision_midis}))
    observed = tuple(sorted({int(value) for value in observed_midis}))
    precision_set = set(precision)
    observed_set = set(observed)

    if primary not in precision_set:
        raise ValueError("Primary MIDI must remain in the precision pitch set")
    if not precision_set.issubset(observed_set):
        raise ValueError("Precision pitch set must be a subset of observed pitches")

    missing_evidence = [midi for midi in observed if int(midi) not in evidence]
    if missing_evidence:
        raise ValueError(
            f"Missing physical evidence for observed pitches: {missing_evidence}"
        )

    positive = [
        midi
        for midi in observed
        if float(evidence[midi]["attack"]) > float(positive_attack_floor)
        and float(evidence[midi]["body"]) > float(positive_body_floor)
    ]
    strongest_positive = _ranked_midis(positive, evidence)[0] if positive else None

    harmonic_set = {int(value) for value in harmonic_intervals}
    protected_harmonic: int | None = None
    if (
        strongest_positive is not None
        and int(strongest_positive) != primary
        and int(strongest_positive) - primary in harmonic_set
    ):
        protected_harmonic = int(strongest_positive)

    recovery_candidates = [
        midi
        for midi in positive
        if midi not in precision_set and midi != protected_harmonic
    ]

    retained_others = _ranked_midis(
        [midi for midi in precision if midi != primary],
        evidence,
    )
    recovery_others = _ranked_midis(recovery_candidates, evidence)
    ordered = [primary] + retained_others + recovery_others

    selected = [primary]
    voicing = resolve_joint_chord_voicing(selected)
    if voicing is None:
        raise RuntimeError(
            f"Precision primary MIDI {primary} has no legal guitar position"
        )

    for midi in ordered[1:]:
        if len(selected) >= MAX_CHORD_NOTES:
            break
        trial = selected + [int(midi)]
        trial_voicing = resolve_joint_chord_voicing(trial)
        if trial_voicing is None:
            continue
        selected = trial
        voicing = trial_voicing

    candidate_set = precision_set.union(recovery_candidates)
    selected_set = set(selected)
    recovered = selected_set.difference(precision_set)
    dropped = candidate_set.difference(selected_set)

    if not selected_set.issubset(observed_set):
        raise RuntimeError("Polyphony boundary invented an unobserved pitch")
    if primary not in selected_set:
        raise RuntimeError("Polyphony boundary dropped the precision primary")
    if protected_harmonic is not None and protected_harmonic in recovered:
        raise RuntimeError(
            "Polyphony boundary reintroduced a protected promoted harmonic"
        )

    return PrecisionPolyphonyDecision(
        selected_midis=tuple(int(value) for value in selected),
        candidate_midis=tuple(sorted(int(value) for value in candidate_set)),
        recovered_midis=frozenset(int(value) for value in recovered),
        dropped_midis=frozenset(int(value) for value in dropped),
        protected_harmonic_midi=protected_harmonic,
        voicing={
            int(midi): dict(position)
            for midi, position in voicing.items()
        },
    )


__all__ = [
    "PrecisionPolyphonyDecision",
    "resolve_precision_polyphony",
]
