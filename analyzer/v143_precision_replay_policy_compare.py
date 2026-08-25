from __future__ import annotations

import argparse
import copy
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

EXPECTED_POLICY = "envelope-balanced-secondary-v2"
SECONDARY_RAW_RATIO = 0.80
HARMONIC_SECONDARY_RAW_RATIO = 0.92
FUNDAMENTAL_MIN_RAW_RATIO = 0.55
HARMONIC_INTERVAL_WEIGHTS = {
    12: 0.35,
    19: 0.25,
    24: 0.20,
    28: 0.12,
    31: 0.10,
    36: 0.08,
}
HARMONIC_INTERVALS = frozenset(HARMONIC_INTERVAL_WEIGHTS)
POSITIVE_ATTACK_FLOOR = 0.0
POSITIVE_BODY_FLOOR = -0.25


def _finite(value: Any) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite replay evidence: {value!r}")
    return number


def _candidate_map(attack: Mapping[str, Any]) -> dict[int, Mapping[str, Any]]:
    output: dict[int, Mapping[str, Any]] = {}
    for item in attack.get("candidates") or []:
        midi = int(item["midi"])
        if midi in output:
            raise ValueError(f"duplicate replay MIDI {midi}")
        for field in ("score", "attack", "body"):
            _finite(item[field])
        output[midi] = item
    expected = [int(value) for value in (attack.get("candidateMidis") or [])]
    if expected != list(output):
        raise ValueError("replay candidateMidis do not match candidate records")
    return output


def _stored_primary_midi(candidates: Mapping[int, Mapping[str, Any]]) -> int:
    primaries = [midi for midi, item in candidates.items() if item.get("primary") is True]
    if len(primaries) != 1:
        raise ValueError(f"expected exactly one replay primary, found {len(primaries)}")
    return int(primaries[0])


def _positive(candidates: Mapping[int, Mapping[str, Any]]) -> dict[int, Mapping[str, Any]]:
    return {
        midi: item
        for midi, item in candidates.items()
        if _finite(item["attack"]) > POSITIVE_ATTACK_FLOOR
        and _finite(item["body"]) > POSITIVE_BODY_FLOOR
    }


def _strongest_raw_midi(candidates: Mapping[int, Mapping[str, Any]]) -> int:
    positive = _positive(candidates)
    source = positive or candidates
    if not source:
        raise ValueError("replay attack has no candidates")
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


def _harmonic_family_score(midi: int, positive: Mapping[int, Mapping[str, Any]]) -> float:
    base = positive[midi]
    score = _finite(base["score"])
    for interval, weight in HARMONIC_INTERVAL_WEIGHTS.items():
        upper = positive.get(int(midi) + int(interval))
        if upper is None:
            continue
        if _finite(upper["attack"]) <= POSITIVE_ATTACK_FLOOR:
            continue
        if _finite(upper["body"]) <= POSITIVE_BODY_FLOOR:
            continue
        score += float(weight) * max(
            0.0,
            min(_finite(base["score"]), _finite(upper["score"])),
        )
    return float(score)


def _recomputed_primary_midi(candidates: Mapping[int, Mapping[str, Any]]) -> int:
    if not candidates:
        raise ValueError("cannot recompute primary from empty candidate set")
    positive = _positive(candidates)
    if not positive:
        return _strongest_raw_midi(candidates)

    strongest_raw_midi = _strongest_raw_midi(candidates)
    strongest_score = max(1e-6, _finite(positive[strongest_raw_midi]["score"]))
    family_scores = {midi: _harmonic_family_score(midi, positive) for midi in positive}
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


def _verified_primary_midi(candidates: Mapping[int, Mapping[str, Any]]) -> int:
    stored = _stored_primary_midi(candidates)
    recomputed = _recomputed_primary_midi(candidates)
    if stored != recomputed:
        raise ValueError(
            f"stored replay primary {stored} does not match independently recomputed primary {recomputed}"
        )
    return int(recomputed)


def _ratios(item: Mapping[str, Any], strongest: Mapping[str, Any]) -> dict[str, float]:
    return {
        "score": _finite(item["score"]) / max(1e-6, _finite(strongest["score"])),
        "attack": _finite(item["attack"]) / max(1e-6, _finite(strongest["attack"])),
        "body": _finite(item["body"]) / max(1e-6, _finite(strongest["body"])),
    }


def _select(attack: Mapping[str, Any], *, policy: str) -> tuple[set[int], list[dict[str, Any]]]:
    candidates = _candidate_map(attack)
    if not candidates:
        raise ValueError("replay attack has no candidates")
    primary = _verified_primary_midi(candidates)
    positive = _positive(candidates)
    if not positive:
        return set(candidates), []
    if primary not in positive:
        raise ValueError("replay primary is not physically positive")

    strongest_midi = _strongest_raw_midi(candidates)
    strongest = positive[strongest_midi]
    kept = {primary}
    decisions: list[dict[str, Any]] = []

    for midi, item in positive.items():
        if midi == primary:
            continue
        harmonic = int(midi) - int(primary) in HARMONIC_INTERVALS
        floor = HARMONIC_SECONDARY_RAW_RATIO if harmonic else SECONDARY_RAW_RATIO
        ratios = _ratios(item, strongest)
        passes = {name: value >= floor for name, value in ratios.items()}
        if policy == "legacy":
            accepted = all(passes.values())
        elif policy == "v2":
            accepted = all(passes.values()) if harmonic else sum(passes.values()) >= 2
        else:
            raise ValueError(f"unknown policy: {policy}")
        if accepted:
            kept.add(int(midi))
        decisions.append(
            {
                "midi": int(midi),
                "harmonicAbovePrimary": bool(harmonic),
                "floor": float(floor),
                "ratios": ratios,
                "passes": passes,
                "accepted": bool(accepted),
            }
        )

    # Common promoted-harmonic contradiction guard.
    if strongest_midi != primary and strongest_midi - primary in HARMONIC_INTERVALS:
        kept.discard(strongest_midi)
    if primary not in kept:
        raise RuntimeError("policy compare lost replay primary")
    return kept, decisions


def build_report(replay: Mapping[str, Any]) -> dict[str, Any]:
    if replay.get("schemaVersion") != 2:
        raise ValueError("replay evidence schemaVersion must be 2")
    if replay.get("policy") != EXPECTED_POLICY:
        raise ValueError("replay evidence policy mismatch")
    for field in (
        "fixedRetainedAttackPitchReplayReady",
        "attackPolicyReplayReady",
        "sourceViewEvidenceReady",
        "precisionStrengthRecomputeReady",
        "zeroValuePreservationReady",
    ):
        if replay.get(field) is not True:
            raise ValueError(f"replay evidence is not ready: {field}")
    if replay.get("referenceFree") is not True:
        raise ValueError("replay evidence is not marked reference-free")
    if replay.get("professionalReferenceUsed") is not False:
        raise ValueError("replay evidence indicates forbidden professional reference use")
    if replay.get("runtimeLabelsRequired") is not False:
        raise ValueError("replay evidence indicates runtime labels are required")
    if replay.get("productionModified") is not False:
        raise ValueError("replay evidence indicates production mutation")

    attacks = replay.get("attacks") or []
    if len(attacks) != int(replay.get("retainedAttackCount") or -1):
        raise ValueError("replay attack count mismatch")
    eligible_attack_count = int(replay.get("eligibleAttackCount") or -1)
    eligible_pitch_count = int(replay.get("eligiblePitchHypothesisCount") or -1)
    if eligible_attack_count < len(attacks):
        raise ValueError("eligible attack universe is smaller than retained universe")

    candidate_total = 0
    stored_selected_total = 0
    legacy_total = 0
    v2_total = 0
    added_total = 0
    removed_total = 0
    changed_attacks = 0
    v2_replay_mismatch_count = 0
    failed_dimension_counts: Counter[str] = Counter()
    primary64_attack_count = 0
    primary64_changed_count = 0
    non64_attack_count = 0
    non64_changed_count = 0
    seen_attack_keys: set[tuple[int, int]] = set()
    per_attack: list[dict[str, Any]] = []

    for attack in attacks:
        key = (int(attack["measure"]), int(attack["step"]))
        if key in seen_attack_keys:
            raise ValueError(f"duplicate retained replay attack {key}")
        seen_attack_keys.add(key)
        if attack.get("retained") is not True:
            raise ValueError(f"retained replay attack {key} is not marked retained")

        candidates = _candidate_map(attack)
        primary = _verified_primary_midi(candidates)
        stored = {midi for midi, item in candidates.items() if item.get("selected") is True}
        if primary not in stored:
            raise ValueError(f"replay primary is not stored-selected at {key}")
        legacy, _legacy_decisions = _select(attack, policy="legacy")
        v2, v2_decisions = _select(attack, policy="v2")

        stored_matches_v2 = stored == v2
        v2_replay_mismatch_count += int(not stored_matches_v2)
        additions = sorted(v2 - legacy)
        removals = sorted(legacy - v2)
        changed_attacks += int(bool(additions or removals))
        removed_total += len(removals)

        decision_by_midi = {int(item["midi"]): item for item in v2_decisions}
        for midi in additions:
            failed = sorted(
                name
                for name, passed in decision_by_midi[midi]["passes"].items()
                if not passed
            )
            failed_dimension_counts["+".join(failed) if failed else "none"] += 1

        candidate_total += len(candidates)
        stored_selected_total += len(stored)
        legacy_total += len(legacy)
        v2_total += len(v2)
        added_total += len(additions)

        if primary == 64:
            primary64_attack_count += 1
            primary64_changed_count += int(bool(additions or removals))
        else:
            non64_attack_count += 1
            non64_changed_count += int(bool(additions or removals))

        if additions or removals or not stored_matches_v2:
            per_attack.append(
                {
                    "measure": int(attack["measure"]),
                    "step": int(attack["step"]),
                    "primaryMidi": int(primary),
                    "primaryRecomputed": True,
                    "legacyPitchSet": sorted(legacy),
                    "v2PitchSet": sorted(v2),
                    "storedSelectedPitchSet": sorted(stored),
                    "v2AddedMidis": additions,
                    "v2RemovedMidis": removals,
                    "storedMatchesV2": stored_matches_v2,
                }
            )

    if candidate_total != int(replay.get("originalPitchHypothesisCount") or -1):
        raise ValueError("replay original pitch total mismatch")
    if candidate_total != int(replay.get("retainedOriginalPitchHypothesisCount") or -1):
        raise ValueError("replay retained original pitch total mismatch")
    if eligible_pitch_count < candidate_total:
        raise ValueError("eligible pitch universe is smaller than retained pitch universe")
    if removed_total != 0:
        raise RuntimeError("v2 unexpectedly removed a legacy-supported pitch")
    if v2_replay_mismatch_count != 0:
        raise RuntimeError(
            f"stored v2 selection disagrees with independent CPU replay at {v2_replay_mismatch_count} attacks"
        )

    return {
        "schemaVersion": 2,
        "classification": "reference-free-replay-policy-compare",
        "source": {
            "replayPolicy": str(replay.get("policy") or ""),
            "attackUniverse": "fixed-retained-attacks",
            "retainedAttackCount": len(attacks),
            "eligibleAttackCount": eligible_attack_count,
            "originalPitchHypothesisCount": candidate_total,
            "eligiblePitchHypothesisCount": eligible_pitch_count,
            "fixedRetainedAttackPitchReplayReady": True,
            "attackPolicyReplayReady": True,
            "sourceViewEvidenceReady": True,
            "precisionStrengthRecomputeReady": True,
            "zeroValuePreservationReady": True,
            "primaryRecomputeMatches": True,
            "storedV2ReplayMatches": True,
            "professionalReferenceUsed": False,
            "newInferenceUsed": False,
        },
        "comparison": {
            "storedSelectedPitchCount": stored_selected_total,
            "legacyRecomputedPitchCount": legacy_total,
            "v2RecomputedPitchCount": v2_total,
            "v2AddedPitchCount": added_total,
            "v2RemovedPitchCount": removed_total,
            "changedAttackCount": changed_attacks,
            "v2ReplayMismatchAttackCount": 0,
            "primaryRecomputeMismatchAttackCount": 0,
            "addedPitchFailedDimensionCounts": dict(sorted(failed_dimension_counts.items())),
            "primaryMidi64AttackCount": primary64_attack_count,
            "primaryMidi64ChangedAttackCount": primary64_changed_count,
            "non64AttackCount": non64_attack_count,
            "non64ChangedAttackCount": non64_changed_count,
        },
        "changedAttacks": per_attack,
        "referenceFree": True,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }


def _item(
    midi: int,
    score: float,
    attack: float,
    body: float,
    *,
    primary: bool = False,
    selected: bool = False,
) -> dict[str, Any]:
    return {
        "midi": midi,
        "score": score,
        "attack": attack,
        "body": body,
        "primary": primary,
        "selected": selected,
    }


def _attack(*items: dict[str, Any], measure: int = 1, step: int = 0) -> dict[str, Any]:
    return {
        "measure": measure,
        "step": step,
        "retained": True,
        "candidateMidis": [int(item["midi"]) for item in items],
        "candidates": list(items),
    }


def _replay(attack: Mapping[str, Any]) -> dict[str, Any]:
    pitch_count = len(attack.get("candidates") or [])
    return {
        "schemaVersion": 2,
        "policy": EXPECTED_POLICY,
        "retainedAttackCount": 1,
        "eligibleAttackCount": 2,
        "originalPitchHypothesisCount": pitch_count,
        "retainedOriginalPitchHypothesisCount": pitch_count,
        "eligiblePitchHypothesisCount": pitch_count + 3,
        "fixedRetainedAttackPitchReplayReady": True,
        "attackPolicyReplayReady": True,
        "sourceViewEvidenceReady": True,
        "precisionStrengthRecomputeReady": True,
        "zeroValuePreservationReady": True,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "attacks": [attack],
    }


def _self_test() -> None:
    from v143_contextual_prune_precision_shadow import (
        FUNDAMENTAL_MIN_RAW_RATIO as ACTUAL_FUNDAMENTAL_MIN_RAW_RATIO,
        HARMONIC_INTERVAL_WEIGHTS as ACTUAL_HARMONIC_INTERVAL_WEIGHTS,
        HARMONIC_SECONDARY_RAW_RATIO as ACTUAL_HARMONIC_SECONDARY_RAW_RATIO,
        POSITIVE_ATTACK_FLOOR as ACTUAL_POSITIVE_ATTACK_FLOOR,
        POSITIVE_BODY_FLOOR as ACTUAL_POSITIVE_BODY_FLOOR,
        SECONDARY_RAW_RATIO as ACTUAL_SECONDARY_RAW_RATIO,
    )
    from v143_contextual_prune_precision_shadow_v2 import secondary_gate_decision

    assert SECONDARY_RAW_RATIO == ACTUAL_SECONDARY_RAW_RATIO
    assert HARMONIC_SECONDARY_RAW_RATIO == ACTUAL_HARMONIC_SECONDARY_RAW_RATIO
    assert FUNDAMENTAL_MIN_RAW_RATIO == ACTUAL_FUNDAMENTAL_MIN_RAW_RATIO
    assert HARMONIC_INTERVAL_WEIGHTS == ACTUAL_HARMONIC_INTERVAL_WEIGHTS
    assert POSITIVE_ATTACK_FLOOR == ACTUAL_POSITIVE_ATTACK_FLOOR
    assert POSITIVE_BODY_FLOOR == ACTUAL_POSITIVE_BODY_FLOOR

    cases = [
        (
            "score+attack",
            _attack(
                _item(60, 1.0, 1.0, 1.0, primary=True, selected=True),
                _item(64, 0.86, 0.83, 0.79, selected=True),
            ),
            {60}, {60, 64},
        ),
        (
            "score+body",
            _attack(
                _item(60, 1.0, 1.0, 1.0, primary=True, selected=True),
                _item(64, 0.86, 0.79, 0.83, selected=True),
            ),
            {60}, {60, 64},
        ),
        (
            "attack+body",
            _attack(
                _item(60, 1.0, 1.0, 1.0, primary=True, selected=True),
                _item(64, 0.79, 0.86, 0.86, selected=True),
            ),
            {60}, {60, 64},
        ),
        (
            "one-only",
            _attack(
                _item(60, 1.0, 1.0, 1.0, primary=True, selected=True),
                _item(64, 0.86, 0.79, 0.79, selected=False),
            ),
            {60}, {60},
        ),
        (
            "harmonic-two-of-three",
            _attack(
                _item(60, 1.0, 1.0, 1.0, primary=True, selected=True),
                _item(72, 0.95, 0.95, 0.91, selected=False),
            ),
            {60}, {60},
        ),
        (
            "harmonic-three-of-three",
            _attack(
                _item(60, 1.0, 1.0, 1.0, primary=True, selected=True),
                _item(72, 0.95, 0.95, 0.95, selected=True),
            ),
            {60, 72}, {60, 72},
        ),
        (
            "promoted-harmonic-guard",
            _attack(
                _item(60, 0.80, 0.80, 0.80, primary=True, selected=True),
                _item(72, 1.00, 1.00, 1.00, selected=False),
            ),
            {60}, {60},
        ),
        (
            "no-positive-fallback",
            _attack(
                _item(60, -0.40, -0.10, -0.30, primary=True, selected=True),
                _item(64, -0.50, -0.20, -0.40, selected=True),
            ),
            {60, 64}, {60, 64},
        ),
    ]

    for name, attack, expected_legacy, expected_v2 in cases:
        candidates = _candidate_map(attack)
        assert _verified_primary_midi(candidates) == _stored_primary_midi(candidates), name
        legacy, _ = _select(attack, policy="legacy")
        v2, _ = _select(attack, policy="v2")
        assert legacy == expected_legacy, (name, legacy, expected_legacy)
        assert v2 == expected_v2, (name, v2, expected_v2)

    assert secondary_gate_decision(score_ratio=0.86, attack_ratio=0.83, body_ratio=0.79, harmonic_above_primary=False) is True
    assert secondary_gate_decision(score_ratio=0.86, attack_ratio=0.79, body_ratio=0.79, harmonic_above_primary=False) is False
    assert secondary_gate_decision(score_ratio=0.95, attack_ratio=0.95, body_ratio=0.91, harmonic_above_primary=True) is False
    assert secondary_gate_decision(score_ratio=0.95, attack_ratio=0.95, body_ratio=0.95, harmonic_above_primary=True) is True

    corrupted_primary = _attack(
        _item(60, 0.80, 0.80, 0.80, primary=False, selected=True),
        _item(72, 1.00, 1.00, 1.00, primary=True, selected=True),
    )
    try:
        _verified_primary_midi(_candidate_map(corrupted_primary))
    except ValueError:
        pass
    else:
        raise AssertionError("primary recomputation failed to reject corrupted stored primary")

    good_replay = _replay(cases[0][1])
    report = build_report(good_replay)
    comparison = report["comparison"]
    assert comparison["legacyRecomputedPitchCount"] == 1
    assert comparison["v2RecomputedPitchCount"] == 2
    assert comparison["v2AddedPitchCount"] == 1
    assert comparison["v2RemovedPitchCount"] == 0
    assert comparison["v2ReplayMismatchAttackCount"] == 0
    assert comparison["primaryRecomputeMismatchAttackCount"] == 0
    assert comparison["addedPitchFailedDimensionCounts"] == {"body": 1}
    assert report["source"]["storedV2ReplayMatches"] is True

    corrupted_selection = copy.deepcopy(good_replay)
    corrupted_selection["attacks"][0]["candidates"][1]["selected"] = False
    try:
        build_report(corrupted_selection)
    except RuntimeError:
        pass
    else:
        raise AssertionError("strict replay failed to reject stored-v2 selection mismatch")

    print("PASS precision replay policy compare strict schema2 self-test")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return
    if not args.input or not args.output:
        raise SystemExit("--input and --output are required unless --self-test is used")
    product = json.loads(Path(args.input).read_text())
    replay = product.get("precisionReplayEvidence") or {}
    report = build_report(replay)
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps(report["comparison"], sort_keys=True))


if __name__ == "__main__":
    main()
