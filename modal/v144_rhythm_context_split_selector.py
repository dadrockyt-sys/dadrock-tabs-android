from __future__ import annotations

from typing import Any, Mapping, Sequence

from v144_rhythm_context_split_policy import (
    ContextSplitConfig,
    evaluate_candidate_pair,
    musical_floor,
    musical_mean,
)


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def _safety_reasons(candidate: Mapping[str, Any], config: ContextSplitConfig) -> list[str]:
    reasons: list[str] = []
    safety = _require_mapping(candidate.get("safety", {}), "candidate safety")

    if safety.get("v5Modified") is not False:
        reasons.append("v5-modification-not-proven-false")
    if safety.get("productionModified") is not False:
        reasons.append("production-modification-not-proven-false")
    if safety.get("runtimeReferenceInputUsed") is not False:
        reasons.append("reference-used-as-runtime-input")
    if safety.get("deterministic") is not True:
        reasons.append("determinism-not-proven")

    if config.holdout_must_remain_closed and candidate.get("holdout") is not None:
        reasons.append("holdout-opened-before-promotion-gate")
    return reasons


def evaluate_candidate(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    *,
    config: ContextSplitConfig,
) -> dict[str, Any]:
    baseline_calibration = _require_mapping(baseline.get("calibration"), "baseline calibration")
    candidate_calibration = _require_mapping(candidate.get("calibration"), "candidate calibration")
    baseline_canary = _require_mapping(baseline.get("canary"), "baseline canary")
    candidate_canary = _require_mapping(candidate.get("canary"), "candidate canary")

    calibration = evaluate_candidate_pair(
        baseline_calibration,
        candidate_calibration,
        config=config,
        canary=False,
    )
    canary = evaluate_candidate_pair(
        baseline_canary,
        candidate_canary,
        config=config,
        canary=True,
    )
    reasons = _safety_reasons(candidate, config)
    reasons.extend(f"calibration:{reason}" for reason in calibration["reasons"])
    reasons.extend(f"canary:{reason}" for reason in canary["reasons"])

    return {
        "name": str(candidate.get("name") or "unnamed"),
        "policy": str(candidate.get("policy") or "unknown"),
        "passed": not reasons,
        "reasons": reasons,
        "calibration": calibration,
        "canary": canary,
        "ranking": {
            "pitchContentGain": float(calibration["pitchContentGain"]),
            "musicalFloorGain": float(calibration["musicalFloorGain"]),
            "musicalMeanGain": float(calibration["musicalMeanGain"]),
            "candidateMusicalFloor": musical_floor(candidate_calibration),
            "candidateMusicalMean": musical_mean(candidate_calibration),
        },
    }


def select_candidate(
    candidates: Sequence[Mapping[str, Any]],
    *,
    config: ContextSplitConfig,
    baseline_name: str = "no-prune",
) -> dict[str, Any]:
    if not candidates:
        raise ValueError("at least one candidate is required")

    by_name: dict[str, Mapping[str, Any]] = {}
    for item in candidates:
        name = str(item.get("name") or "")
        if not name:
            raise ValueError("every candidate requires a name")
        if name in by_name:
            raise ValueError(f"duplicate candidate name {name}")
        by_name[name] = item

    if baseline_name not in by_name:
        raise ValueError(f"required baseline {baseline_name!r} is missing")
    baseline = by_name[baseline_name]

    baseline_safety = _safety_reasons(baseline, config)
    if baseline_safety:
        raise ValueError(
            "baseline safety contract failed: " + ", ".join(baseline_safety)
        )

    evaluated: list[dict[str, Any]] = []
    for name in sorted(by_name):
        if name == baseline_name:
            continue
        evaluated.append(
            evaluate_candidate(baseline, by_name[name], config=config)
        )

    winners = [item for item in evaluated if item["passed"]]
    if winners:
        winners.sort(
            key=lambda item: (
                -float(item["ranking"]["pitchContentGain"]),
                -float(item["ranking"]["musicalFloorGain"]),
                -float(item["ranking"]["musicalMeanGain"]),
                str(item["name"]),
            )
        )
        selected_name = str(winners[0]["name"])
        selected_reason = "qualified-v144-candidate"
    else:
        selected_name = baseline_name
        selected_reason = "deterministic-no-prune-fallback"

    return {
        "schemaVersion": 14401,
        "instrument": "rhythm",
        "baseline": baseline_name,
        "selected": selected_name,
        "selectedReason": selected_reason,
        "promotionAllowed": selected_name != baseline_name,
        "holdoutOpened": False,
        "v5Modified": False,
        "productionModified": False,
        "evaluations": evaluated,
    }


__all__ = ["evaluate_candidate", "select_candidate"]
