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
    _vector_value,
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


def _view_triplet(row: Mapping[str, Any], midi: int) -> dict[str, dict[str, float]]:
    view_a = row.get("viewA") if isinstance(row.get("viewA"), Mapping) else {}
    view_b = row.get("viewB") if isinstance(row.get("viewB"), Mapping) else {}

    def values(view: Mapping[str, Any]) -> dict[str, float]:
        return {
            "attack": float(_vector_value(view.get("attackMax"), midi)),
            "early": float(_vector_value(view.get("earlyMean"), midi)),
            "sustain": float(_vector_value(view.get("sustainMean"), midi)),
        }

    return {"viewA": values(view_a), "viewB": values(view_b)}


def _float_field(row: Mapping[str, Any], key: str, default: float) -> float:
    raw = row.get(key)
    if raw is None:
        return float(default)
    return float(raw)


def _serialize_replay_attack(
    key: EventKey,
    row: Mapping[str, Any],
    precision: PrecisionShadowResult,
    grid_time: float,
) -> dict[str, Any]:
    retained = key in precision.retained_events
    original = _candidate_midis(row)
    selected = set(precision.pitch_sets.get(key) or ()) if retained else set()
    primary = precision.primary_midis.get(key) if retained else None

    if retained:
        if tuple(original) != tuple(precision.original_pitch_sets.get(key) or ()):
            raise RuntimeError(f"Replay evidence candidate identity mismatch at {key}")
        if primary is None or int(primary) not in selected:
            raise RuntimeError(f"Replay evidence retained primary mismatch at {key}")

    candidates: list[dict[str, Any]] = []
    for midi in original:
        evidence = _pitch_evidence(row, midi)
        views = _view_triplet(row, midi)
        candidates.append(
            {
                "midi": int(midi),
                "attack": float(evidence["attack"]),
                "early": float(evidence["early"]),
                "sustain": float(evidence["sustain"]),
                "body": float(evidence["body"]),
                "continuity": float(evidence["continuity"]),
                "score": float(evidence["score"]),
                "viewA": views["viewA"],
                "viewB": views["viewB"],
                "selected": retained and int(midi) in selected,
                "primary": retained and int(midi) == int(primary),
            }
        )

    onset_time = _float_field(row, "onsetTime", grid_time)
    precision_strength = _float_field(row, "_precisionStrength", -99.0)
    precision_grid_error = _float_field(
        row,
        "_precisionGridErrorSeconds",
        abs(onset_time - grid_time),
    )
    candidate_strength = _float_field(row, "_candidateStrength", 0.0)
    return {
        "measure": int(key[0]),
        "step": int(key[1]),
        "gridTime": float(grid_time),
        "onsetTime": onset_time,
        "precisionStrength": precision_strength,
        "precisionGridErrorSeconds": precision_grid_error,
        "candidateStrength": candidate_strength,
        "stemSupportMax": int(row.get("stemSupportMax") or 0),
        "sweepSupportMax": int(row.get("sweepSupportMax") or 0),
        "detectionCountSum": int(row.get("detectionCountSum") or 0),
        "retained": bool(retained),
        "failSafe": key in precision.fail_safe_events,
        "candidateMidis": [int(value) for value in original],
        "candidates": candidates,
    }


def build_precision_replay_evidence(
    carrier_rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
    precision: PrecisionShadowResult,
) -> dict[str, Any]:
    """Serialize the one-shot source universe needed for future CPU-only replay.

    `attacks` preserves the historical retained-attack pitch replay contract.
    `eligibleAttacks` preserves every corrected input attack that has a physical
    carrier row, including row-level strength inputs and per-view pitch evidence.
    This makes fixed-retained pitch experiments and precision-stage attack-policy
    experiments replayable without separator or Basic Pitch inference.
    """
    rows_by_slot = _best_rows_by_slot(carrier_rows, grid)
    input_keys = sorted(precision.input_events)
    retained_keys = set(precision.retained_events)

    eligible_attacks: list[dict[str, Any]] = []
    retained_attacks: list[dict[str, Any]] = []
    missing_input_keys: list[dict[str, int]] = []
    eligible_pitch_count = 0
    retained_pitch_count = 0

    for key in input_keys:
        row = rows_by_slot.get(key)
        if row is None:
            missing_input_keys.append({"measure": int(key[0]), "step": int(key[1])})
            continue
        if key not in grid:
            raise RuntimeError(f"Replay evidence missing grid time for {key}")
        record = _serialize_replay_attack(key, row, precision, float(grid[key]))
        eligible_attacks.append(record)
        eligible_pitch_count += len(record["candidates"])
        if key in retained_keys:
            retained_attacks.append(record)
            retained_pitch_count += len(record["candidates"])

    serialized_retained_keys = {
        (int(item["measure"]), int(item["step"]))
        for item in retained_attacks
    }
    if serialized_retained_keys != retained_keys:
        raise RuntimeError("Replay evidence retained attack universe mismatch")
    if retained_pitch_count != sum(len(value) for value in precision.original_pitch_sets.values()):
        raise RuntimeError("Replay evidence retained candidate count mismatch")
    if any(item.get("retained") is not True for item in retained_attacks):
        raise RuntimeError("Replay evidence retained attack flag mismatch")

    return {
        "schemaVersion": 2,
        "policy": POLICY_NAME,
        "replayCompleteness": "retained-pitch-plus-eligible-attack-source-universe",
        "inputAttackCount": len(input_keys),
        "eligibleAttackCount": len(eligible_attacks),
        "retainedAttackCount": len(retained_attacks),
        "prunedAttackCount": len(precision.pruned_events),
        "originalPitchHypothesisCount": int(retained_pitch_count),
        "retainedOriginalPitchHypothesisCount": int(retained_pitch_count),
        "eligiblePitchHypothesisCount": int(eligible_pitch_count),
        "inputAttackKeys": [
            {"measure": int(key[0]), "step": int(key[1])}
            for key in input_keys
        ],
        "carrierMissingInputAttackKeys": missing_input_keys,
        "attacks": retained_attacks,
        "eligibleAttacks": eligible_attacks,
        "fixedRetainedAttackPitchReplayReady": True,
        "attackPolicyReplayReady": True,
        "sourceViewEvidenceReady": True,
        "precisionStrengthRecomputeReady": True,
        "zeroValuePreservationReady": True,
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
