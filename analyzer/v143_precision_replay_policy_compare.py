from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

SECONDARY_RAW_RATIO = 0.80
HARMONIC_SECONDARY_RAW_RATIO = 0.92
HARMONIC_INTERVALS = frozenset({12, 19, 24, 28, 31, 36})
POSITIVE_ATTACK_FLOOR = 0.0
POSITIVE_BODY_FLOOR = -0.25


def _finite(value: Any) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite replay evidence: {value!r}")
    return number


def _candidate_map(attack: Mapping[str, Any]) -> dict[int, Mapping[str, Any]]:
    candidates = attack.get("candidates") or []
    output: dict[int, Mapping[str, Any]] = {}
    for item in candidates:
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


def _primary_midi(candidates: Mapping[int, Mapping[str, Any]]) -> int:
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


def _ratios(
    item: Mapping[str, Any],
    strongest: Mapping[str, Any],
) -> dict[str, float]:
    return {
        "score": _finite(item["score"]) / max(1e-6, _finite(strongest["score"])),
        "attack": _finite(item["attack"]) / max(1e-6, _finite(strongest["attack"])),
        "body": _finite(item["body"]) / max(1e-6, _finite(strongest["body"])),
    }


def _select(
    attack: Mapping[str, Any],
    *,
    policy: str,
) -> tuple[set[int], list[dict[str, Any]]]:
    candidates = _candidate_map(attack)
    if not candidates:
        raise ValueError("replay attack has no candidates")
    primary = _primary_midi(candidates)
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

    # Existing promoted-harmonic guard is common to both policies.
    if strongest_midi != primary and strongest_midi - primary in HARMONIC_INTERVALS:
        kept.discard(strongest_midi)
    if primary not in kept:
        raise RuntimeError("policy compare lost replay primary")
    return kept, decisions


def build_report(replay: Mapping[str, Any]) -> dict[str, Any]:
    if replay.get("referenceFree") is not True:
        raise ValueError("replay evidence is not marked reference-free")
    if replay.get("professionalReferenceUsed") is not False:
        raise ValueError("replay evidence indicates forbidden professional reference use")

    attacks = replay.get("attacks") or []
    if len(attacks) != int(replay.get("retainedAttackCount") or -1):
        raise ValueError("replay attack count mismatch")

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

    per_attack: list[dict[str, Any]] = []
    for attack in attacks:
        candidates = _candidate_map(attack)
        primary = _primary_midi(candidates)
        stored = {midi for midi, item in candidates.items() if item.get("selected") is True}
        legacy, legacy_decisions = _select(attack, policy="legacy")
        v2, v2_decisions = _select(attack, policy="v2")

        if stored != v2:
            v2_replay_mismatch_count += 1
        additions = sorted(v2 - legacy)
        removals = sorted(legacy - v2)
        if additions or removals:
            changed_attacks += 1
        if removals:
            removed_total += len(removals)

        decision_by_midi = {int(item["midi"]): item for item in v2_decisions}
        for midi in additions:
            decision = decision_by_midi[midi]
            failed = sorted(name for name, passed in decision["passes"].items() if not passed)
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

        if additions or removals or stored != v2:
            per_attack.append(
                {
                    "measure": int(attack["measure"]),
                    "step": int(attack["step"]),
                    "primaryMidi": int(primary),
                    "legacyPitchSet": sorted(legacy),
                    "v2PitchSet": sorted(v2),
                    "storedSelectedPitchSet": sorted(stored),
                    "v2AddedMidis": additions,
                    "v2RemovedMidis": removals,
                    "storedMatchesV2": stored == v2,
                }
            )

    if candidate_total != int(replay.get("originalPitchHypothesisCount") or -1):
        raise ValueError("replay original pitch total mismatch")
    if removed_total != 0:
        raise RuntimeError("v2 unexpectedly removed a legacy-supported pitch")

    return {
        "schemaVersion": 1,
        "classification": "reference-free-replay-policy-compare",
        "source": {
            "replayPolicy": str(replay.get("policy") or ""),
            "retainedAttackCount": len(attacks),
            "originalPitchHypothesisCount": candidate_total,
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
            "v2ReplayMismatchAttackCount": v2_replay_mismatch_count,
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


def _self_test() -> None:
    replay = {
        "policy": "envelope-balanced-secondary-v2",
        "retainedAttackCount": 1,
        "originalPitchHypothesisCount": 3,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "attacks": [
            {
                "measure": 1,
                "step": 0,
                "candidateMidis": [60, 64, 72],
                "candidates": [
                    {"midi": 60, "score": 1.0, "attack": 1.0, "body": 1.0, "primary": True, "selected": True},
                    {"midi": 64, "score": 0.86, "attack": 0.83, "body": 0.79, "primary": False, "selected": True},
                    {"midi": 72, "score": 0.95, "attack": 0.95, "body": 0.91, "primary": False, "selected": False},
                ],
            }
        ],
    }
    report = build_report(replay)
    comparison = report["comparison"]
    assert comparison["legacyRecomputedPitchCount"] == 1
    assert comparison["v2RecomputedPitchCount"] == 2
    assert comparison["v2AddedPitchCount"] == 1
    assert comparison["v2RemovedPitchCount"] == 0
    assert comparison["v2ReplayMismatchAttackCount"] == 0
    assert comparison["addedPitchFailedDimensionCounts"] == {"body": 1}
    print("PASS precision replay policy compare self-test")


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
