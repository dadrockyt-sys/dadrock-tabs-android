from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

from v143_contextual_prune_precision_shadow import (
    FUNDAMENTAL_MIN_RAW_RATIO,
    HARMONIC_INTERVAL_WEIGHTS,
    HARMONIC_SECONDARY_RAW_RATIO,
    POSITIVE_ATTACK_FLOOR,
    POSITIVE_BODY_FLOOR,
    SECONDARY_RAW_RATIO,
    EventKey,
    PrecisionShadowResult,
    _attack_is_precise,
    _best_evidence,
    _best_rows_by_slot,
    _candidate_midis,
    _harmonic_family_score,
    _pitch_evidence,
    _transient_ratio,
)
from v143_contextual_prune_shadow_correction import ShadowCorrectionResult


POLICY_NAME = "envelope-balanced-secondary-v2"


def secondary_gate_decision(
    *,
    score_ratio: float,
    attack_ratio: float,
    body_ratio: float,
    harmonic_above_primary: bool,
) -> bool:
    """Return whether an observed secondary has sufficient physical support.

    The legacy precision rule required score, attack, and body to *all* clear
    the same high relative floor. That treats an attack-dominant guitar note
    and a sustain/body-dominant guitar note as failures even when the combined
    physical score plus one independent envelope view is strong.

    V2 keeps the historical harmonic-above-primary protection unchanged: known
    overtone-family candidates must still clear all three 0.92 gates. For every
    other observed secondary, V2 requires any two of score/attack/body to clear
    the historical 0.80 floor. It introduces no new numeric threshold, pitch,
    attack, key/chord/song rule, or reference-derived information.
    """
    floor = HARMONIC_SECONDARY_RAW_RATIO if harmonic_above_primary else SECONDARY_RAW_RATIO
    passes = (
        float(score_ratio) >= floor,
        float(attack_ratio) >= floor,
        float(body_ratio) >= floor,
    )
    required = 3 if harmonic_above_primary else 2
    return sum(bool(value) for value in passes) >= required


def _precision_pitch_set_v2(row: Mapping[str, Any]) -> tuple[tuple[int, ...], bool, int]:
    original = _candidate_midis(row)
    if not original:
        raise ValueError("Precision pitch selection requires an observed candidate pitch")

    evidence = {midi: _pitch_evidence(row, midi) for midi in original}
    positive = {
        midi: item
        for midi, item in evidence.items()
        if item["attack"] > POSITIVE_ATTACK_FLOOR and item["body"] > POSITIVE_BODY_FLOOR
    }
    if not positive:
        strongest = max(
            original,
            key=lambda midi: (evidence[midi]["score"], evidence[midi]["attack"], -midi),
        )
        return original, False, int(strongest)

    strongest_raw_midi = max(
        positive,
        key=lambda midi: (positive[midi]["score"], positive[midi]["attack"], -midi),
    )
    strongest_raw = positive[strongest_raw_midi]
    strongest_score = max(1e-6, float(strongest_raw["score"]))
    strongest_attack = max(1e-6, float(strongest_raw["attack"]))
    strongest_body = max(1e-6, float(strongest_raw["body"]))

    family_scores = {midi: _harmonic_family_score(midi, positive) for midi in positive}
    primary = max(
        family_scores,
        key=lambda midi: (family_scores[midi], positive[midi]["attack"], -midi),
    )
    if float(positive[primary]["score"]) < FUNDAMENTAL_MIN_RAW_RATIO * strongest_score:
        primary = strongest_raw_midi

    kept = {int(primary)}
    for midi, item in sorted(
        positive.items(),
        key=lambda pair: (pair[1]["score"], pair[1]["attack"], -pair[0]),
        reverse=True,
    ):
        if midi == primary:
            continue

        harmonic_above_primary = int(midi) - int(primary) in HARMONIC_INTERVAL_WEIGHTS
        if secondary_gate_decision(
            score_ratio=float(item["score"]) / strongest_score,
            attack_ratio=float(item["attack"]) / strongest_attack,
            body_ratio=float(item["body"]) / strongest_body,
            harmonic_above_primary=harmonic_above_primary,
        ):
            kept.add(int(midi))

    promoted = int(primary) != int(strongest_raw_midi)
    return tuple(sorted(kept)), promoted, int(primary)


def apply_reference_free_precision_shadow_v2(
    carrier_rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
    correction: ShadowCorrectionResult,
    target_measures: Iterable[int],
) -> PrecisionShadowResult:
    """Reference-free precision shadow with envelope-balanced secondary support.

    Attack selection, local-prominence logic, measure fail-safe behavior,
    harmonic-family primary promotion, and all no-invention invariants are the
    historical precision implementation. Only the non-harmonic secondary gate
    changes from a three-way conjunction to a two-of-three physical consensus.
    """
    if not isinstance(correction, ShadowCorrectionResult):
        raise TypeError("correction must be ShadowCorrectionResult")
    input_events = set(correction.corrected_events)
    if not input_events:
        raise ValueError("correction contains no events")
    targets = {int(value) for value in target_measures}
    if not targets:
        raise ValueError("target_measures cannot be empty")

    rows_by_slot = _best_rows_by_slot(carrier_rows, grid)
    eligible = {key for key in input_events if key in rows_by_slot and key[0] in targets}
    retained = {
        key
        for key in eligible
        if _attack_is_precise(key, rows_by_slot[key], rows_by_slot, eligible)
    }

    fail_safe: set[EventKey] = set()
    for measure in sorted(targets):
        measure_inputs = sorted(key for key in eligible if key[0] == measure)
        if not measure_inputs or any(key in retained for key in measure_inputs):
            continue
        winner = max(
            measure_inputs,
            key=lambda key: (
                _transient_ratio(_best_evidence(rows_by_slot[key])[1]),
                float(rows_by_slot[key].get("_precisionStrength") or -99.0),
                -int(key[1]),
            ),
        )
        retained.add(winner)
        fail_safe.add(winner)

    original_pitch_sets: dict[EventKey, tuple[int, ...]] = {}
    pitch_sets: dict[EventKey, tuple[int, ...]] = {}
    primary_midis: dict[EventKey, int] = {}
    promoted_count = 0
    suppressed = 0

    for key in sorted(retained):
        row = rows_by_slot[key]
        original = _candidate_midis(row)
        if not original:
            retained.remove(key)
            fail_safe.discard(key)
            continue
        selected, promoted, primary = _precision_pitch_set_v2(row)
        if not selected:
            selected = original
        if int(primary) not in set(selected):
            raise RuntimeError(f"Precision v2 primary escaped retained pitch set at {key}")
        original_pitch_sets[key] = original
        pitch_sets[key] = selected
        primary_midis[key] = int(primary)
        promoted_count += int(promoted)
        suppressed += max(0, len(original) - len(selected))

    retained_measures = {measure for measure, _step in retained}
    missing = targets - retained_measures
    if missing:
        for measure in sorted(missing):
            candidates = [
                key
                for key in eligible
                if key[0] == measure and _candidate_midis(rows_by_slot[key])
            ]
            if not candidates:
                raise RuntimeError(f"No observed pitched corrected event can preserve measure {measure}")
            winner = max(
                candidates,
                key=lambda key: (
                    _transient_ratio(_best_evidence(rows_by_slot[key])[1]),
                    float(rows_by_slot[key].get("_precisionStrength") or -99.0),
                    -int(key[1]),
                ),
            )
            retained.add(winner)
            fail_safe.add(winner)
            original = _candidate_midis(rows_by_slot[winner])
            selected, promoted, primary = _precision_pitch_set_v2(rows_by_slot[winner])
            selected = selected or original
            if int(primary) not in set(selected):
                raise RuntimeError(f"Precision v2 fail-safe primary escaped pitch set at {winner}")
            original_pitch_sets[winner] = original
            pitch_sets[winner] = selected
            primary_midis[winner] = int(primary)
            promoted_count += int(promoted)
            suppressed += max(0, len(original) - len(selected))

    pruned = input_events - retained
    if not retained.issubset(input_events):
        raise RuntimeError("Precision v2 added an attack")
    if set(primary_midis) != set(retained):
        raise RuntimeError("Precision v2 did not preserve one explicit primary per retained attack")
    for key, selected in pitch_sets.items():
        observed = set(_candidate_midis(rows_by_slot[key]))
        if not set(selected).issubset(observed):
            raise RuntimeError(f"Precision v2 invented pitch at {key}")
        if int(primary_midis[key]) not in set(selected):
            raise RuntimeError(f"Precision v2 primary is not retained at {key}")

    return PrecisionShadowResult(
        input_events=frozenset(input_events),
        retained_events=frozenset(retained),
        pruned_events=frozenset(pruned),
        original_pitch_sets=original_pitch_sets,
        pitch_sets=pitch_sets,
        primary_midis=primary_midis,
        fail_safe_events=frozenset(fail_safe),
        fundamental_promotions=int(promoted_count),
        suppressed_pitch_count=int(suppressed),
    )


def build_precision_replay_evidence(
    carrier_rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
    precision: PrecisionShadowResult,
) -> dict[str, Any]:
    """Serialize compact source evidence needed for future CPU-only replay.

    This intentionally stores only observed candidate pitches and their derived
    two-view physical evidence for retained attacks. It avoids stems/CQT arrays,
    professional labels, runtime labels, or any invented pitch. A single future
    carrier capture can therefore support many later policy experiments without
    repeating separator or Basic Pitch inference.
    """
    rows_by_slot = _best_rows_by_slot(carrier_rows, grid)
    attacks: list[dict[str, Any]] = []
    candidate_count = 0

    for key in sorted(precision.retained_events):
        row = rows_by_slot.get(key)
        if row is None:
            raise RuntimeError(f"Replay evidence missing carrier row at {key}")
        original = _candidate_midis(row)
        if tuple(original) != tuple(precision.original_pitch_sets.get(key) or ()):
            raise RuntimeError(f"Replay evidence candidate identity mismatch at {key}")

        candidates: list[dict[str, Any]] = []
        for midi in original:
            evidence = _pitch_evidence(row, midi)
            candidates.append(
                {
                    "midi": int(midi),
                    "attack": float(evidence["attack"]),
                    "early": float(evidence["early"]),
                    "sustain": float(evidence["sustain"]),
                    "body": float(evidence["body"]),
                    "continuity": float(evidence["continuity"]),
                    "score": float(evidence["score"]),
                    "selected": int(midi) in set(precision.pitch_sets[key]),
                    "primary": int(midi) == int(precision.primary_midis[key]),
                }
            )
        candidate_count += len(candidates)
        attacks.append(
            {
                "measure": int(key[0]),
                "step": int(key[1]),
                "onsetTime": float(row.get("onsetTime") or 0.0),
                "candidateMidis": [int(value) for value in original],
                "candidates": candidates,
            }
        )

    if candidate_count != sum(len(value) for value in precision.original_pitch_sets.values()):
        raise RuntimeError("Replay evidence candidate count mismatch")

    return {
        "schemaVersion": 1,
        "policy": POLICY_NAME,
        "retainedAttackCount": len(attacks),
        "originalPitchHypothesisCount": int(candidate_count),
        "attacks": attacks,
        "candidateAddsUnobservedAttack": False,
        "candidateAddsUnobservedPitch": False,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }


__all__ = [
    "POLICY_NAME",
    "secondary_gate_decision",
    "apply_reference_free_precision_shadow_v2",
    "build_precision_replay_evidence",
]
