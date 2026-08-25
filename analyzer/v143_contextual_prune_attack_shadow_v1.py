#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

ATTACK_TRANSIENT_RATIO_FLOOR = 0.70
ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR = 0.60
LOCAL_STRENGTH_MARGIN = 0.20
LOCAL_RADIUS_STEPS = 2
POSITIVE_ATTACK_FLOOR = 0.0
POSITIVE_BODY_FLOOR = -0.25
EXPECTED_POLICY = "envelope-balanced-secondary-v2"


def _finite(v: Any) -> float:
    x = float(v)
    if not math.isfinite(x):
        raise ValueError(f"non-finite value: {v!r}")
    return x


def _key(a: Mapping[str, Any]) -> tuple[int, int]:
    return int(a["measure"]), int(a["step"])


def _candidate_map(a: Mapping[str, Any]) -> dict[int, Mapping[str, Any]]:
    return {int(c["midi"]): c for c in (a.get("candidates") or [])}


def _best_candidate(a: Mapping[str, Any]) -> Mapping[str, Any] | None:
    cs = _candidate_map(a)
    if not cs:
        return None
    midi = max(cs, key=lambda m: (_finite(cs[m]["score"]), _finite(cs[m]["attack"]), -int(m)))
    return cs[midi]


def _transient_ratio(a: Mapping[str, Any]) -> float:
    c = _best_candidate(a)
    if c is None:
        return 0.0
    return max(0.0, _finite(c["attack"])) / max(1e-6, _finite(c["body"]))


def _legacy_strength(a: Mapping[str, Any]) -> float:
    x = _finite(a["precisionStrength"])
    return x if x else -99.0


def _positive_best(a: Mapping[str, Any]) -> bool:
    c = _best_candidate(a)
    return bool(
        c is not None
        and _finite(c["attack"]) > POSITIVE_ATTACK_FLOOR
        and _finite(c["body"]) > POSITIVE_BODY_FLOOR
    )


def _legacy_precise(
    k: tuple[int, int],
    a: Mapping[str, Any],
    eligible: Mapping[tuple[int, int], Mapping[str, Any]],
) -> bool:
    c = _best_candidate(a)
    if c is None:
        return False
    if _finite(c["attack"]) <= POSITIVE_ATTACK_FLOOR or _finite(c["body"]) <= POSITIVE_BODY_FLOOR:
        return False
    ratio = _transient_ratio(a)
    if ratio >= ATTACK_TRANSIENT_RATIO_FLOOR:
        return True
    if ratio < ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR:
        return False
    neighbors = [
        _legacy_strength(o)
        for ok, o in eligible.items()
        if ok != k
        and ok[0] == k[0]
        and abs(ok[1] - k[1]) <= LOCAL_RADIUS_STEPS
    ]
    if not neighbors:
        return True
    return _legacy_strength(a) >= max(neighbors) + LOCAL_STRENGTH_MARGIN


def _attack_peak_rescue(
    k: tuple[int, int],
    a: Mapping[str, Any],
    eligible: Mapping[tuple[int, int], Mapping[str, Any]],
) -> bool:
    """Reuse the existing local margin/radius on the transient dimension itself."""
    if not _positive_best(a):
        return False
    c = _best_candidate(a)
    assert c is not None
    attack = _finite(c["attack"])
    neighbors: list[float] = []
    for ok, o in eligible.items():
        if ok == k or ok[0] != k[0] or abs(ok[1] - k[1]) > LOCAL_RADIUS_STEPS:
            continue
        oc = _best_candidate(o)
        if oc is not None:
            neighbors.append(_finite(oc["attack"]))
    if not neighbors:
        return True
    return attack >= max(neighbors) + LOCAL_STRENGTH_MARGIN


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
    eligible = {_key(a): a for a in attacks}
    if len(eligible) != int(replay.get("eligibleAttackCount")):
        raise ValueError("eligible attack count mismatch")

    baseline = {k for k, a in eligible.items() if a.get("retained") is True}
    recomputed = {k for k, a in eligible.items() if _legacy_precise(k, a, eligible)}
    if baseline != recomputed:
        missing = sorted(baseline - recomputed)
        extra = sorted(recomputed - baseline)
        raise ValueError(
            f"baseline replay mismatch missing={missing[:5]} extra={extra[:5]}"
        )

    rescued = {
        k
        for k, a in eligible.items()
        if k not in baseline and _attack_peak_rescue(k, a, eligible)
    }
    shadow = baseline | rescued

    reason_counts: Counter[str] = Counter()
    rescued_rows: list[dict[str, Any]] = []
    for k in sorted(rescued):
        a = eligible[k]
        c = _best_candidate(a)
        assert c is not None
        ratio = _transient_ratio(a)
        if ratio < ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR:
            reason = "below-legacy-ratio-floor-but-local-attack-peak"
        elif ratio < ATTACK_TRANSIENT_RATIO_FLOOR:
            reason = "legacy-borderline-not-composite-max-but-local-attack-peak"
        else:
            reason = "unexpected"
        reason_counts[reason] += 1
        rescued_rows.append(
            {
                "measure": k[0],
                "step": k[1],
                "reason": reason,
                "transientRatio": ratio,
                "bestMidi": int(c["midi"]),
                "bestAttack": _finite(c["attack"]),
                "bestBody": _finite(c["body"]),
                "bestScore": _finite(c["score"]),
                "precisionStrength": _finite(a["precisionStrength"]),
                "precisionGridErrorSeconds": _finite(a["precisionGridErrorSeconds"]),
                "stemSupportMax": int(a["stemSupportMax"]),
                "sweepSupportMax": int(a["sweepSupportMax"]),
                "detectionCountSum": int(a["detectionCountSum"]),
            }
        )

    return {
        "schemaVersion": 1,
        "classification": "v143-reference-free-attack-local-peak-shadow-v1",
        "policy": "legacy-attack-policy-plus-local-transient-peak-rescue",
        "sourcePolicy": EXPECTED_POLICY,
        "baselineRetainedAttackCount": len(baseline),
        "eligibleAttackCount": len(eligible),
        "baselinePrunedAttackCount": len(eligible) - len(baseline),
        "rescuedAttackCount": len(rescued),
        "shadowRetainedAttackCount": len(shadow),
        "removedBaselineAttackCount": len(baseline - shadow),
        "reasonCounts": dict(sorted(reason_counts.items())),
        "rescuedAttacks": rescued_rows,
        "constantsReusedWithoutChange": {
            "positiveAttackFloor": POSITIVE_ATTACK_FLOOR,
            "positiveBodyFloor": POSITIVE_BODY_FLOOR,
            "localMargin": LOCAL_STRENGTH_MARGIN,
            "localRadiusSteps": LOCAL_RADIUS_STEPS,
            "legacyRatioFloor": ATTACK_TRANSIENT_RATIO_FLOOR,
            "legacyRatioExceptionFloor": ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR,
        },
        "referenceFree": True,
        "newInferenceUsed": False,
        "professionalReferenceUsed": False,
        "productionModified": False,
    }


def _self_test() -> None:
    def cand(midi: int, score: float, attack: float, body: float) -> dict[str, Any]:
        return {"midi": midi, "score": score, "attack": attack, "body": body}

    def attack(
        measure: int,
        step: int,
        score: float,
        transient: float,
        body: float,
        retained: bool = False,
    ) -> dict[str, Any]:
        return {
            "measure": measure,
            "step": step,
            "precisionStrength": score,
            "retained": retained,
            "candidates": [cand(60, score, transient, body)],
            "candidateMidis": [60],
        }

    low_ratio_peak = {
        (1, 0): attack(1, 0, 3.0, 1.0, 2.0),
        (1, 1): attack(1, 1, 3.5, 0.7, 1.0),
    }
    assert not _legacy_precise((1, 0), low_ratio_peak[(1, 0)], low_ratio_peak)
    assert _attack_peak_rescue((1, 0), low_ratio_peak[(1, 0)], low_ratio_peak)

    sustained_nonpeak = {
        (1, 0): attack(1, 0, 3.0, 0.7, 2.0),
        (1, 1): attack(1, 1, 3.5, 1.0, 1.5),
    }
    assert not _attack_peak_rescue(
        (1, 0), sustained_nonpeak[(1, 0)], sustained_nonpeak
    )

    negative_attack = {(1, 0): attack(1, 0, 1.0, -0.1, 1.0)}
    assert not _attack_peak_rescue((1, 0), negative_attack[(1, 0)], negative_attack)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("product")
    parser.add_argument("--output")
    args = parser.parse_args()
    _self_test()
    product = json.loads(Path(args.product).read_text())
    report = build_report(product)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
