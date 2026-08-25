from __future__ import annotations

from collections import Counter
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
    _vector_value,
)

POLICY_NAME = "local-or-two-view-extra-harmonic-primary-v3"


@dataclass(frozen=True)
class ContextualHarmonicPrimaryV3Diagnostics:
    inspected_attack_count: int
    corrected_primary_count: int
    local_only_count: int
    two_view_only_count: int
    local_and_two_view_count: int
    removed_upper_harmonic_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "schemaVersion": 1,
            "policy": POLICY_NAME,
            "inspectedAttackCount": int(self.inspected_attack_count),
            "correctedPrimaryCount": int(self.corrected_primary_count),
            "localOnlyCount": int(self.local_only_count),
            "twoViewOnlyCount": int(self.two_view_only_count),
            "localAndTwoViewCount": int(self.local_and_two_view_count),
            "removedUpperHarmonicCount": int(self.removed_upper_harmonic_count),
            "localRadiusSteps": int(LOCAL_RADIUS_STEPS),
            "fundamentalMinRawRatio": float(FUNDAMENTAL_MIN_RAW_RATIO),
            "twoViewConsensusRequired": True,
            "strictHarmonicSupportDominanceRequired": True,
            "additionalHarmonicBeyondCurrentRequired": True,
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
    positive = {midi: _pitch_evidence(row, midi) for midi in _candidate_midis(row)}
    positive = {
        midi: evidence
        for midi, evidence in positive.items()
        if evidence["attack"] > POSITIVE_ATTACK_FLOOR
        and evidence["body"] > POSITIVE_BODY_FLOOR
    }
    if not positive:
        return None
    return int(max(positive, key=lambda midi: (
        positive[midi]["score"], positive[midi]["attack"], -int(midi)
    )))


def _view_evidence(row: Mapping[str, Any], midi: int, view_name: str) -> dict[str, float]:
    raw_view = row.get(view_name)
    view = raw_view if isinstance(raw_view, Mapping) else {}
    attack = float(_vector_value(view.get("attackMax"), midi))
    early = float(_vector_value(view.get("earlyMean"), midi))
    sustain = float(_vector_value(view.get("sustainMean"), midi))
    body = max(early, sustain)
    continuity = min(early, sustain)
    return {
        "attack": attack,
        "early": early,
        "sustain": sustain,
        "body": body,
        "continuity": continuity,
        "score": attack + 0.65 * body + 0.15 * continuity,
    }


def _positive_view(row: Mapping[str, Any], view_name: str) -> dict[int, dict[str, float]]:
    evidence = {midi: _view_evidence(row, midi, view_name) for midi in _candidate_midis(row)}
    return {
        midi: item
        for midi, item in evidence.items()
        if item["attack"] > POSITIVE_ATTACK_FLOOR
        and item["body"] > POSITIVE_BODY_FLOOR
    }


def _harmonic_support_count(midi: int, positive: Mapping[int, Mapping[str, float]]) -> int:
    return sum(
        1 for interval in HARMONIC_INTERVAL_WEIGHTS
        if int(midi) + int(interval) in positive
    )


def _local_supported_lower(
    key: EventKey,
    current: int,
    original_primary: Mapping[EventKey, int],
    positive: Mapping[int, Mapping[str, float]],
) -> tuple[int | None, int]:
    measure, step = int(key[0]), int(key[1])
    support: Counter[int] = Counter()
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
        support[lower] += 1

    if not support:
        return None, 0

    lower = max(
        support,
        key=lambda midi: (
            int(support[midi]),
            _harmonic_family_score(int(midi), positive),
            float(positive[int(midi)]["score"]),
            float(positive[int(midi)]["attack"]),
            -int(midi),
        ),
    )
    return int(lower), int(support[lower])


def _two_view_supported_lower(
    row: Mapping[str, Any],
    current: int,
    positive_consensus: Mapping[int, Mapping[str, float]],
) -> int | None:
    view_a = _positive_view(row, "viewA")
    view_b = _positive_view(row, "viewB")
    if current not in view_a or current not in view_b:
        return None

    strongest_a = max(view_a, key=lambda midi: (
        view_a[midi]["score"], view_a[midi]["attack"], -int(midi)
    ))
    strongest_b = max(view_b, key=lambda midi: (
        view_b[midi]["score"], view_b[midi]["attack"], -int(midi)
    ))
    strongest_a_score = max(1e-6, float(view_a[strongest_a]["score"]))
    strongest_b_score = max(1e-6, float(view_b[strongest_b]["score"]))
    current_a_count = _harmonic_support_count(current, view_a)
    current_b_count = _harmonic_support_count(current, view_b)

    candidates: list[tuple[int, int, int]] = []
    for lower in sorted(set(view_a).intersection(view_b)):
        if lower >= current:
            continue
        if current - lower not in HARMONIC_INTERVAL_WEIGHTS:
            continue
        if lower not in positive_consensus:
            continue
        if float(view_a[lower]["score"]) < FUNDAMENTAL_MIN_RAW_RATIO * strongest_a_score:
            continue
        if float(view_b[lower]["score"]) < FUNDAMENTAL_MIN_RAW_RATIO * strongest_b_score:
            continue

        lower_a_count = _harmonic_support_count(lower, view_a)
        lower_b_count = _harmonic_support_count(lower, view_b)
        additional_a = any(
            lower + interval in view_a and lower + interval != current
            for interval in HARMONIC_INTERVAL_WEIGHTS
        )
        additional_b = any(
            lower + interval in view_b and lower + interval != current
            for interval in HARMONIC_INTERVAL_WEIGHTS
        )
        if not additional_a or not additional_b:
            continue
        if lower_a_count <= current_a_count or lower_b_count <= current_b_count:
            continue
        candidates.append((int(lower), int(lower_a_count), int(lower_b_count)))

    if not candidates:
        return None

    winner = max(
        candidates,
        key=lambda item: (
            min(item[1], item[2]),
            max(item[1], item[2]),
            _harmonic_family_score(item[0], positive_consensus),
            float(positive_consensus[item[0]]["score"]),
            float(positive_consensus[item[0]]["attack"]),
            -item[0],
        ),
    )
    return int(winner[0])


def apply_contextual_harmonic_primary_shadow_v3(
    carrier_rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
    precision: PrecisionShadowResult,
) -> tuple[PrecisionShadowResult, ContextualHarmonicPrimaryV3Diagnostics]:
    """Repair strongest-raw upper-harmonic primaries from source-only context.

    V3 preserves V1's same-measure +/-2-step lower-primary confirmation. When
    that exact local confirmation is absent, it adds one independent fallback:
    a lower observed harmonic-family candidate may replace the current strongest
    raw primary only when the existing 0.55 physical-strength guard passes in
    each source view separately, the lower candidate has at least one additional
    positive harmonic-family member beyond the current upper primary in each
    view, and its harmonic support remains strictly richer than the current
    primary in both views.

    No new numeric confidence threshold, attack, pitch, timing relocation,
    song/key/chord label, or professional reference enters the decision. The
    input primary map is immutable during the pass, so corrections cannot cascade.
    """
    if not isinstance(precision, PrecisionShadowResult):
        raise TypeError("precision must be PrecisionShadowResult")

    rows_by_slot = _best_rows_by_slot(carrier_rows, grid)
    original_primary = {key: int(value) for key, value in precision.primary_midis.items()}
    primary_midis = dict(original_primary)
    pitch_sets = {
        key: tuple(int(value) for value in values)
        for key, values in precision.pitch_sets.items()
    }

    corrected = 0
    removed = 0
    local_only = 0
    two_view_only = 0
    both = 0

    for key in sorted(precision.retained_events):
        row = rows_by_slot.get(key)
        if row is None:
            raise RuntimeError(f"Contextual harmonic v3 has no row for {key}")
        current = int(original_primary[key])
        if _strongest_positive_raw_midi(row) != current:
            continue

        evidence = {midi: _pitch_evidence(row, midi) for midi in _candidate_midis(row)}
        positive = {
            midi: item
            for midi, item in evidence.items()
            if item["attack"] > POSITIVE_ATTACK_FLOOR
            and item["body"] > POSITIVE_BODY_FLOOR
        }
        if current not in positive:
            continue

        local_lower, _local_support_count = _local_supported_lower(
            key, current, original_primary, positive
        )
        two_view_lower = _two_view_supported_lower(row, current, positive)

        if local_lower is not None:
            lower = int(local_lower)
            if two_view_lower == lower:
                both += 1
            else:
                local_only += 1
        elif two_view_lower is not None:
            lower = int(two_view_lower)
            two_view_only += 1
        else:
            continue

        before = set(int(value) for value in pitch_sets[key])
        after = set(before)
        after.add(lower)
        if current in after:
            after.remove(current)
            removed += 1
        after.add(lower)
        if not after:
            raise RuntimeError(f"Contextual harmonic v3 emptied pitch set at {key}")

        primary_midis[key] = lower
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
        raise RuntimeError("Contextual harmonic v3 changed attack identity")
    for key in shadow.retained_events:
        row = rows_by_slot[key]
        observed = set(_candidate_midis(row))
        selected = set(shadow.pitch_sets[key])
        if not selected.issubset(observed):
            raise RuntimeError(f"Contextual harmonic v3 invented pitch at {key}")
        if int(shadow.primary_midis[key]) not in selected:
            raise RuntimeError(f"Contextual harmonic v3 lost primary at {key}")

    diagnostics = ContextualHarmonicPrimaryV3Diagnostics(
        inspected_attack_count=len(precision.retained_events),
        corrected_primary_count=corrected,
        local_only_count=local_only,
        two_view_only_count=two_view_only,
        local_and_two_view_count=both,
        removed_upper_harmonic_count=removed,
    )
    return shadow, diagnostics


__all__ = [
    "POLICY_NAME",
    "ContextualHarmonicPrimaryV3Diagnostics",
    "apply_contextual_harmonic_primary_shadow_v3",
]
