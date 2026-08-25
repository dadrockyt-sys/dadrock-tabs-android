from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from v143_contextual_prune_attack_shadow_v1 import build_report as build_attack_shadow_report
from v143_precision_replay_artifact_validator import validate_product
from v143_rhythm_guitar_note_mapper import resolve_joint_chord_voicing

SECONDARY_RAW_RATIO = 0.80
HARMONIC_SECONDARY_RAW_RATIO = 0.92
FUNDAMENTAL_MIN_RAW_RATIO = 0.55
HARMONIC_INTERVAL_WEIGHTS = {12: 0.35, 19: 0.25, 24: 0.20, 28: 0.12, 31: 0.10, 36: 0.08}
HARMONIC_INTERVALS = frozenset(HARMONIC_INTERVAL_WEIGHTS)
POSITIVE_ATTACK_FLOOR = 0.0
POSITIVE_BODY_FLOOR = -0.25
MAX_GUITAR_STRINGS = 6


class AttackShadowReplayValidationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AttackShadowReplayValidationError(message)


def _finite(value: Any) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise AttackShadowReplayValidationError(f"non-finite replay evidence: {value!r}")
    return number


def _candidate_map(attack: Mapping[str, Any]) -> dict[int, Mapping[str, Any]]:
    output: dict[int, Mapping[str, Any]] = {}
    for item in attack.get("candidates") or []:
        midi = int(item["midi"])
        _require(midi not in output, f"duplicate replay MIDI {midi}")
        for field in ("score", "attack", "body"):
            _finite(item[field])
        output[midi] = item
    expected = [int(value) for value in (attack.get("candidateMidis") or [])]
    _require(expected == list(output), "replay candidateMidis do not match candidate records")
    return output


def _positive(candidates: Mapping[int, Mapping[str, Any]]) -> dict[int, Mapping[str, Any]]:
    return {
        midi: item
        for midi, item in candidates.items()
        if _finite(item["attack"]) > POSITIVE_ATTACK_FLOOR
        and _finite(item["body"]) > POSITIVE_BODY_FLOOR
    }


def _strongest_raw_midi(candidates: Mapping[int, Mapping[str, Any]]) -> int:
    source = _positive(candidates) or candidates
    _require(bool(source), "replay attack has no candidates")
    return int(
        max(
            source,
            key=lambda midi: (
                _finite(source[midi]["score"]),
                _finite(source[midi]["attack"]),
                -int(midi),
            ),
        )
    )


def _harmonic_family_score(
    midi: int,
    positive: Mapping[int, Mapping[str, Any]],
) -> float:
    base = positive[midi]
    score = _finite(base["score"])
    for interval, weight in HARMONIC_INTERVAL_WEIGHTS.items():
        upper = positive.get(int(midi) + int(interval))
        if upper is None:
            continue
        score += float(weight) * max(
            0.0,
            min(_finite(base["score"]), _finite(upper["score"])),
        )
    return float(score)


def _recomputed_primary_midi(candidates: Mapping[int, Mapping[str, Any]]) -> int:
    _require(bool(candidates), "cannot recompute primary from empty candidate set")
    positive = _positive(candidates)
    if not positive:
        return _strongest_raw_midi(candidates)
    strongest_raw_midi = _strongest_raw_midi(candidates)
    strongest_score = max(1e-6, _finite(positive[strongest_raw_midi]["score"]))
    family_scores = {
        midi: _harmonic_family_score(midi, positive)
        for midi in positive
    }
    primary = max(
        family_scores,
        key=lambda midi: (
            family_scores[midi],
            _finite(positive[midi]["attack"]),
            -int(midi),
        ),
    )
    if _finite(positive[primary]["score"]) < FUNDAMENTAL_MIN_RAW_RATIO * strongest_score:
        primary = strongest_raw_midi
    return int(primary)


def _select_v2(
    attack: Mapping[str, Any],
) -> tuple[set[int], int]:
    candidates = _candidate_map(attack)
    _require(bool(candidates), "replay attack has no pitch hypotheses")
    primary = _recomputed_primary_midi(candidates)
    positive = _positive(candidates)
    if not positive:
        return set(candidates), primary
    _require(primary in positive, "recomputed primary is not physically positive")

    strongest_midi = _strongest_raw_midi(candidates)
    strongest = positive[strongest_midi]
    kept = {primary}
    for midi, item in positive.items():
        if midi == primary:
            continue
        harmonic = int(midi) - int(primary) in HARMONIC_INTERVALS
        floor = HARMONIC_SECONDARY_RAW_RATIO if harmonic else SECONDARY_RAW_RATIO
        ratios = {
            name: _finite(item[name]) / max(1e-6, _finite(strongest[name]))
            for name in ("score", "attack", "body")
        }
        passes = [value >= floor for value in ratios.values()]
        accepted = all(passes) if harmonic else sum(passes) >= 2
        if accepted:
            kept.add(int(midi))

    if strongest_midi != primary and strongest_midi - primary in HARMONIC_INTERVALS:
        kept.discard(strongest_midi)
    _require(primary in kept, "v2 replay lost recomputed primary")
    return kept, primary


def _expected_voicing(
    attack: Mapping[str, Any],
    selected: set[int],
    primary: int,
) -> tuple[list[int], dict[int, dict[str, Any]]]:
    candidates = _candidate_map(attack)
    _require(primary in selected, "primary is not selected")
    others = sorted(
        (midi for midi in selected if midi != primary),
        key=lambda midi: (
            -_finite(candidates[midi]["score"]),
            -_finite(candidates[midi]["attack"]),
            -_finite(candidates[midi]["body"]),
            int(midi),
        ),
    )

    kept = [primary]
    voicing = resolve_joint_chord_voicing(kept)
    _require(voicing is not None, f"primary MIDI {primary} has no legal guitar position")
    for midi in others:
        if len(kept) >= MAX_GUITAR_STRINGS:
            break
        trial = kept + [int(midi)]
        trial_voicing = resolve_joint_chord_voicing(trial)
        if trial_voicing is None:
            continue
        kept = trial
        voicing = trial_voicing
    _require(voicing is not None, "deterministic voicing unexpectedly missing")
    return kept, voicing


def build_report(product: Mapping[str, Any]) -> dict[str, Any]:
    base_validation = validate_product(product)
    _require(base_validation.get("passed") is True, "base replay validator did not pass")

    shadow = build_attack_shadow_report(product)
    _require(shadow.get("referenceFree") is True, "attack shadow is not reference-free")
    _require(int(shadow.get("removedBaselineAttackCount") or 0) == 0, "attack shadow removed baseline attacks")

    replay = product.get("precisionReplayEvidence") or {}
    eligible_rows = replay.get("eligibleAttacks") or []
    eligible = {
        (int(attack["measure"]), int(attack["step"])): attack
        for attack in eligible_rows
    }
    _require(len(eligible) == int(replay.get("eligibleAttackCount") or -1), "eligible attack count mismatch")

    baseline_keys = {
        key for key, attack in eligible.items()
        if attack.get("retained") is True
    }
    baseline_grid_times = {
        round(_finite(eligible[key]["gridTime"]), 12)
        for key in baseline_keys
    }
    rescued_keys = {
        (int(item["measure"]), int(item["step"]))
        for item in shadow.get("rescuedAttacks") or []
    }
    _require(not (rescued_keys & baseline_keys), "rescued attack overlaps baseline retained attack")

    selected_total = 0
    rendered_total = 0
    voicing_dropped_total = 0
    grid_collision_count = 0
    unobserved_pitch_count = 0
    unplayable_primary_count = 0
    pitch_count_distribution: Counter[int] = Counter()
    per_attack: list[dict[str, Any]] = []

    for key in sorted(rescued_keys):
        attack = eligible[key]
        selected, primary = _select_v2(attack)
        observed = set(int(value) for value in (attack.get("candidateMidis") or []))
        unobserved = selected - observed
        unobserved_pitch_count += len(unobserved)
        _require(not unobserved, f"rescued attack {key} selected unobserved pitches")

        try:
            kept, voicing = _expected_voicing(attack, selected, primary)
        except AttackShadowReplayValidationError:
            unplayable_primary_count += 1
            raise
        kept_set = set(kept)
        _require(kept_set.issubset(selected), f"voicing escaped selected pitch set at {key}")
        for midi in kept:
            position = voicing[int(midi)]
            _require(0 <= int(position["stringIndex"]) < 6, f"invalid string at {key} MIDI {midi}")
            _require(0 <= int(position["fret"]) <= 24, f"invalid fret at {key} MIDI {midi}")

        grid_time = round(_finite(attack["gridTime"]), 12)
        if grid_time in baseline_grid_times:
            grid_collision_count += 1

        selected_total += len(selected)
        rendered_total += len(kept_set)
        voicing_dropped_total += len(selected - kept_set)
        pitch_count_distribution[len(selected)] += 1
        per_attack.append(
            {
                "measure": key[0],
                "step": key[1],
                "primaryMidi": int(primary),
                "selectedPitchSet": sorted(selected),
                "renderedPitchSet": sorted(kept_set),
                "voicingDroppedPitchSet": sorted(selected - kept_set),
                "gridTime": _finite(attack["gridTime"]),
                "onsetTime": _finite(attack["onsetTime"]),
            }
        )

    return {
        "schemaVersion": 1,
        "classification": "v143-reference-free-attack-shadow-v1-pitch-voicing-replay",
        "attackPolicy": {
            "eligibleAttackCount": int(shadow["eligibleAttackCount"]),
            "baselineRetainedAttackCount": int(shadow["baselineRetainedAttackCount"]),
            "baselinePrunedAttackCount": int(shadow["baselinePrunedAttackCount"]),
            "rescuedAttackCount": len(rescued_keys),
            "shadowRetainedAttackCount": int(shadow["shadowRetainedAttackCount"]),
            "removedBaselineAttackCount": int(shadow["removedBaselineAttackCount"]),
        },
        "pitchReplay": {
            "rescuedSelectedPitchCount": selected_total,
            "pitchCountDistribution": {
                str(count): attacks
                for count, attacks in sorted(pitch_count_distribution.items())
            },
            "unobservedPitchCount": unobserved_pitch_count,
        },
        "voicingReplay": {
            "renderedPitchCount": rendered_total,
            "voicingDroppedPitchCount": voicing_dropped_total,
            "unplayablePrimaryCount": unplayable_primary_count,
            "gridTimeCollisionWithBaselineCount": grid_collision_count,
            "standardTuning": True,
            "maxFret": 24,
        },
        "rescuedAttacks": per_attack,
        "downstreamBoundary": {
            "techniqueSustainReplayAvailableForNewlyRescuedAttacks": False,
            "freezeReady": False,
            "reason": "schema-2 intentionally does not persist the full downstream CQT/stem universe for hypothetical newly retained attacks",
        },
        "referenceFree": True,
        "newInferenceUsed": False,
        "professionalReferenceUsed": False,
        "modalInvoked": False,
        "productionModified": False,
    }


def _self_test() -> None:
    from v143_precision_replay_policy_compare import (
        FUNDAMENTAL_MIN_RAW_RATIO as ACTUAL_FUNDAMENTAL_MIN_RAW_RATIO,
        HARMONIC_INTERVAL_WEIGHTS as ACTUAL_HARMONIC_INTERVAL_WEIGHTS,
        HARMONIC_SECONDARY_RAW_RATIO as ACTUAL_HARMONIC_SECONDARY_RAW_RATIO,
        POSITIVE_ATTACK_FLOOR as ACTUAL_POSITIVE_ATTACK_FLOOR,
        POSITIVE_BODY_FLOOR as ACTUAL_POSITIVE_BODY_FLOOR,
        SECONDARY_RAW_RATIO as ACTUAL_SECONDARY_RAW_RATIO,
    )

    assert SECONDARY_RAW_RATIO == ACTUAL_SECONDARY_RAW_RATIO
    assert HARMONIC_SECONDARY_RAW_RATIO == ACTUAL_HARMONIC_SECONDARY_RAW_RATIO
    assert FUNDAMENTAL_MIN_RAW_RATIO == ACTUAL_FUNDAMENTAL_MIN_RAW_RATIO
    assert HARMONIC_INTERVAL_WEIGHTS == ACTUAL_HARMONIC_INTERVAL_WEIGHTS
    assert POSITIVE_ATTACK_FLOOR == ACTUAL_POSITIVE_ATTACK_FLOOR
    assert POSITIVE_BODY_FLOOR == ACTUAL_POSITIVE_BODY_FLOOR

    attack = {
        "candidateMidis": [60, 64, 67],
        "candidates": [
            {"midi": 60, "score": 1.0, "attack": 1.0, "body": 1.0},
            {"midi": 64, "score": 0.86, "attack": 0.83, "body": 0.79},
            {"midi": 67, "score": 0.82, "attack": 0.81, "body": 0.84},
        ],
    }
    selected, primary = _select_v2(attack)
    assert primary == 60
    assert selected == {60, 64, 67}
    kept, voicing = _expected_voicing(attack, selected, primary)
    assert set(kept) == selected
    assert set(voicing) == selected
    print("PASS v143 attack-shadow v1 replay helper self-test")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return
    if not args.input:
        raise SystemExit("--input is required unless --self-test is used")
    product = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = build_report(product)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
