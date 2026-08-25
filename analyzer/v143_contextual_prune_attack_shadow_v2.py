#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from v143_contextual_prune_attack_shadow_v1 import (
    ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR,
    ATTACK_TRANSIENT_RATIO_FLOOR,
    EXPECTED_POLICY,
    LOCAL_RADIUS_STEPS,
    LOCAL_STRENGTH_MARGIN,
    POSITIVE_ATTACK_FLOOR,
    POSITIVE_BODY_FLOOR,
    _attack_peak_rescue,
    _key,
    _legacy_precise,
    _positive_best,
    _transient_ratio,
)


def build_report(product: Mapping[str, Any]) -> dict[str, Any]:
    replay = product.get("precisionReplayEvidence") or {}
    if replay.get("schemaVersion") != 2 or replay.get("policy") != EXPECTED_POLICY:
        raise ValueError("unexpected replay schema/policy")
    for field in (
        "attackPolicyReplayReady",
        "sourceViewEvidenceReady",
        "precisionStrengthRecomputeReady",
        "zeroValuePreservationReady",
    ):
        if replay.get(field) is not True:
            raise ValueError(f"replay not ready: {field}")
    if replay.get("referenceFree") is not True or replay.get("professionalReferenceUsed") is not False:
        raise ValueError("invalid provenance flags")

    attacks = replay.get("eligibleAttacks") or []
    eligible = {_key(attack): attack for attack in attacks}
    if len(eligible) != int(replay.get("eligibleAttackCount")):
        raise ValueError("eligible attack count mismatch")

    baseline = {key for key, attack in eligible.items() if attack.get("retained") is True}
    recomputed = {
        key
        for key, attack in eligible.items()
        if _legacy_precise(key, attack, eligible)
    }
    if baseline != recomputed:
        missing = sorted(baseline - recomputed)
        extra = sorted(recomputed - baseline)
        raise ValueError(
            f"baseline replay mismatch missing={missing[:5]} extra={extra[:5]}"
        )

    rescued: set[tuple[int, int]] = set()
    reason_by_key: dict[tuple[int, int], str] = {}
    for key, attack in eligible.items():
        if key in baseline or not _positive_best(attack):
            continue
        ratio = _transient_ratio(attack)

        # The 0.60 floor already exists in the legacy attack policy as the
        # lower edge of its exception band. V2 removes only the requirement
        # that a physically positive attack in that existing band must also
        # beat a body-heavy local composite-strength maximum by +0.20.
        if ratio >= ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR:
            rescued.add(key)
            reason_by_key[key] = "existing-exception-band-without-composite-local-max"
            continue

        # Below the existing exception floor, retain only the conservative V1
        # transient-local-peak rescue. This reuses the existing local radius
        # and margin on the actual attack dimension and introduces no new
        # numeric threshold.
        if _attack_peak_rescue(key, attack, eligible):
            rescued.add(key)
            reason_by_key[key] = "subfloor-local-transient-peak"

    shadow = baseline | rescued
    reason_counts = Counter(reason_by_key.values())
    remaining = set(eligible) - shadow

    return {
        "schemaVersion": 2,
        "classification": "v143-reference-free-attack-exception-band-shadow-v2",
        "policy": "existing-exception-band-plus-local-transient-peak-v2",
        "sourcePolicy": EXPECTED_POLICY,
        "eligibleAttackCount": len(eligible),
        "baselineRetainedAttackCount": len(baseline),
        "baselinePrunedAttackCount": len(eligible) - len(baseline),
        "rescuedAttackCount": len(rescued),
        "shadowRetainedAttackCount": len(shadow),
        "remainingPrunedAttackCount": len(remaining),
        "removedBaselineAttackCount": len(baseline - shadow),
        "reasonCounts": dict(sorted(reason_counts.items())),
        "rescuedAttackKeys": [
            {
                "measure": key[0],
                "step": key[1],
                "reason": reason_by_key[key],
                "transientRatio": _transient_ratio(eligible[key]),
            }
            for key in sorted(rescued)
        ],
        "remainingPrunedAttackKeys": [
            {"measure": key[0], "step": key[1]}
            for key in sorted(remaining)
        ],
        "constantsReusedWithoutChange": {
            "positiveAttackFloor": POSITIVE_ATTACK_FLOOR,
            "positiveBodyFloor": POSITIVE_BODY_FLOOR,
            "legacyRatioFloor": ATTACK_TRANSIENT_RATIO_FLOOR,
            "legacyRatioExceptionFloor": ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR,
            "localMargin": LOCAL_STRENGTH_MARGIN,
            "localRadiusSteps": LOCAL_RADIUS_STEPS,
        },
        "thresholdsAdded": 0,
        "referenceFree": True,
        "newInferenceUsed": False,
        "professionalReferenceUsed": False,
        "modalInvoked": False,
        "productionModified": False,
    }


def _self_test() -> None:
    # Helper-level behavior is already covered by V1; V2 specifically proves
    # that an exception-band attack no longer depends on composite dominance.
    from v143_contextual_prune_attack_shadow_v1 import _best_candidate

    def candidate(score: float, attack: float, body: float) -> dict[str, Any]:
        return {
            "midi": 60,
            "score": score,
            "attack": attack,
            "early": body,
            "sustain": body,
            "body": body,
            "continuity": body,
            "viewA": {"attack": attack, "early": body, "sustain": body},
            "viewB": {"attack": attack, "early": body, "sustain": body},
        }

    exception = {
        "measure": 1,
        "step": 0,
        "precisionStrength": 2.0,
        "candidates": [candidate(2.0, 0.65, 1.0)],
        "candidateMidis": [60],
    }
    neighbor = {
        "measure": 1,
        "step": 1,
        "precisionStrength": 5.0,
        "candidates": [candidate(5.0, 1.0, 1.0)],
        "candidateMidis": [60],
    }
    universe = {(1, 0): exception, (1, 1): neighbor}
    assert _best_candidate(exception) is not None
    assert not _legacy_precise((1, 0), exception, universe)
    assert _positive_best(exception)
    assert ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR <= _transient_ratio(exception) < ATTACK_TRANSIENT_RATIO_FLOOR
    print("PASS v143 attack-shadow v2 exception-band helper self-test")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", nargs="?")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return 0
    if not args.product:
        raise SystemExit("product is required unless --self-test is used")
    product = json.loads(Path(args.product).read_text())
    report = build_report(product)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
