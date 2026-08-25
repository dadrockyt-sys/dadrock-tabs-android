from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

from v143_contextual_prune_precision_shadow import (
    FUNDAMENTAL_MIN_RAW_RATIO,
    HARMONIC_INTERVAL_WEIGHTS,
    LOCAL_RADIUS_STEPS,
    POSITIVE_ATTACK_FLOOR,
    POSITIVE_BODY_FLOOR,
    EventKey,
    PrecisionShadowResult,
    _best_rows_by_slot,
    _candidate_midis,
    _harmonic_family_score,
    _pitch_evidence,
)


@dataclass(frozen=True)
class ContextualHarmonicPrimaryDiagnostics:
    inspected_attack_count: int
    corrected_primary_count: int
    removed_upper_harmonic_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "schemaVersion": 1,
            "policy": "same-measure-neighbor-supported-harmonic-primary-v1",
            "inspectedAttackCount": int(self.inspected_attack_count),
            "correctedPrimaryCount": int(self.corrected_primary_count),
            "removedUpperHarmonicCount": int(self.removed_upper_harmonic_count),
            "localRadiusSteps": int(LOCAL_RADIUS_STEPS),
            "attackIdentityChanged": False,
            "addsUnobservedAttack": False,
            "addsUnobservedPitch": False,
            "relocatesAttack": False,
            "referenceFree": True,
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
            "productionModified": False,
        }


def _strongest_positive_raw_midi(row: Mapping[str, Any]) -> int | None:
    positive = {
        midi: _pitch_evidence(row, midi)
        for midi in _candidate_midis(row)
    }
    positive = {
        midi: evidence
        for midi, evidence in positive.items()
        if evidence["attack"] > POSITIVE_ATTACK_FLOOR
        and evidence["body"] > POSITIVE_BODY_FLOOR
    }
    if not positive:
        return None
    return int(
        max(
            positive,
            key=lambda midi: (
                positive[midi]["score"],
                positive[midi]["attack"],
                -int(midi),
            ),
        )
    )


def apply_contextual_harmonic_primary_shadow_v1(
    carrier_rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
    precision: PrecisionShadowResult,
) -> tuple[PrecisionShadowResult, ContextualHarmonicPrimaryDiagnostics]:
    """Repair isolated upper-harmonic primary flips using local physical context.

    This shadow only revisits attacks whose current primary is still the strongest
    positive raw pitch (i.e. the existing harmonic-family selector did not already
    promote a lower fundamental). A lower candidate may replace that primary only
    when all of the following are already true in the frozen source evidence:

    * the lower MIDI is physically observed and positive at this exact attack;
    * the current primary is one of the existing harmonic-family intervals above it;
    * the existing FUNDAMENTAL_MIN_RAW_RATIO physical-strength guard also passes;
    * an already-retained attack in the same measure and existing +/-2-step local
      radius uses that exact lower MIDI as its primary.

    The rule adds no pitch, attack, timing location, song/key/chord label, numeric
    confidence floor, or professional-reference information. It reuses the exact
    harmonic interval family, raw-strength guard, and local radius already present
    in precision-v1/v2. The upper primary being reinterpreted is removed from the
    selected set, matching the existing promoted-harmonic guard's treatment of a
    strongest raw overtone.
    """
    if not isinstance(precision, PrecisionShadowResult):
        raise TypeError("precision must be PrecisionShadowResult")

    rows_by_slot = _best_rows_by_slot(carrier_rows, grid)
    original_primary = {
        key: int(value) for key, value in precision.primary_midis.items()
    }
    primary_midis = dict(original_primary)
    pitch_sets = {
        key: tuple(int(value) for value in values)
        for key, values in precision.pitch_sets.items()
    }

    corrected = 0
    removed = 0

    # Read neighbor primaries from the immutable input map so this pass cannot
    # cascade its own corrections through the song.
    for key in sorted(precision.retained_events):
        row = rows_by_slot.get(key)
        if row is None:
            raise RuntimeError(f"Contextual harmonic shadow has no row for {key}")
        current = int(original_primary[key])
        if _strongest_positive_raw_midi(row) != current:
            continue

        evidence = {
            midi: _pitch_evidence(row, midi)
            for midi in _candidate_midis(row)
        }
        positive = {
            midi: item
            for midi, item in evidence.items()
            if item["attack"] > POSITIVE_ATTACK_FLOOR
            and item["body"] > POSITIVE_BODY_FLOOR
        }

        measure, step = int(key[0]), int(key[1])
        neighbor_support: dict[int, int] = {}
        for other_key, other_primary in original_primary.items():
            if other_key == key or int(other_key[0]) != measure:
                continue
            if abs(int(other_key[1]) - step) > LOCAL_RADIUS_STEPS:
                continue
            lower = int(other_primary)
            if lower not in positive:
                continue
            if current - lower not in HARMONIC_INTERVAL_WEIGHTS:
                continue
            if float(positive[lower]["score"]) < (
                FUNDAMENTAL_MIN_RAW_RATIO * max(1e-6, float(positive[current]["score"]))
            ):
                continue
            neighbor_support[lower] = neighbor_support.get(lower, 0) + 1

        if not neighbor_support:
            continue

        lower = max(
            neighbor_support,
            key=lambda midi: (
                int(neighbor_support[midi]),
                _harmonic_family_score(int(midi), positive),
                positive[int(midi)]["score"],
                positive[int(midi)]["attack"],
                -int(midi),
            ),
        )

        after = set(int(value) for value in pitch_sets[key])
        after.add(int(lower))
        if current in after:
            after.remove(current)
            removed += 1
        after.add(int(lower))
        if not after:
            raise RuntimeError(f"Contextual harmonic shadow emptied pitch set at {key}")

        primary_midis[key] = int(lower)
        pitch_sets[key] = tuple(sorted(after))
        corrected += 1

    shadow = replace(
        precision,
        pitch_sets=pitch_sets,
        primary_midis=primary_midis,
        fundamental_promotions=int(precision.fundamental_promotions) + int(corrected),
        suppressed_pitch_count=int(precision.suppressed_pitch_count) + int(removed),
    )

    if shadow.retained_events != precision.retained_events:
        raise RuntimeError("Contextual harmonic shadow changed attack identity")
    for key in shadow.retained_events:
        row = rows_by_slot[key]
        observed = set(_candidate_midis(row))
        selected = set(shadow.pitch_sets[key])
        if not selected.issubset(observed):
            raise RuntimeError(f"Contextual harmonic shadow invented pitch at {key}")
        if int(shadow.primary_midis[key]) not in selected:
            raise RuntimeError(f"Contextual harmonic shadow lost primary at {key}")

    diagnostics = ContextualHarmonicPrimaryDiagnostics(
        inspected_attack_count=len(precision.retained_events),
        corrected_primary_count=corrected,
        removed_upper_harmonic_count=removed,
    )
    return shadow, diagnostics


__all__ = [
    "ContextualHarmonicPrimaryDiagnostics",
    "apply_contextual_harmonic_primary_shadow_v1",
]
