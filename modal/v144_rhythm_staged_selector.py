from __future__ import annotations

from typing import Any, Mapping, Sequence

from v144_rhythm_context_split_policy import (
    ContextSplitConfig,
    compare_metric_sets,
    critical_mismatch_count,
    musical_floor,
    musical_mean,
    pdf_event_fidelity,
)

STAGES = ("fit", "validation", "canary")


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def _stage_metrics(candidate: Mapping[str, Any], stage: str) -> Mapping[str, Any]:
    if stage not in STAGES:
        raise ValueError(f"unsupported stage {stage!r}")
    return _require_mapping(candidate.get(stage), f"candidate {stage}")


def _safety_reasons(candidate: Mapping[str, Any], config: ContextSplitConfig) -> list[str]:
    safety = _require_mapping(candidate.get("safety", {}), "candidate safety")
    reasons: list[str] = []
    required_false = (
        ("v5Modified", "v5-modification-not-proven-false"),
        ("productionModified", "production-modification-not-proven-false"),
        ("mainModified", "main-modification-not-proven-false"),
        ("runtimeReferenceInputUsed", "reference-used-as-runtime-input"),
        ("modalGpuInvoked", "modal-gpu-use-not-proven-false"),
    )
    for key, reason in required_false:
        if safety.get(key) is not False:
            reasons.append(reason)
    if safety.get("deterministic") is not True:
        reasons.append("determinism-not-proven")
    if safety.get("baselineGeneratedMeasureSetPreserved") is not True:
        reasons.append("baseline-generated-measure-set-not-preserved")
    if config.holdout_must_remain_closed and candidate.get("holdout") is not None:
        reasons.append("unseen-holdout-opened-before-final-gate")
    return reasons


def _fit_evaluation(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    *,
    config: ContextSplitConfig,
) -> dict[str, Any]:
    baseline_fit = _stage_metrics(baseline, "fit")
    candidate_fit = _stage_metrics(candidate, "fit")
    comparison = compare_metric_sets(
        baseline_fit,
        candidate_fit,
        maximum_regression=config.maximum_per_metric_regression,
    )
    mismatch_delta = critical_mismatch_count(candidate_fit) - critical_mismatch_count(baseline_fit)
    fidelity = pdf_event_fidelity(candidate_fit)
    reasons = _safety_reasons(candidate, config)
    if fidelity != config.required_pdf_event_fidelity:
        reasons.append("fit:pdf-event-fidelity-not-exact")
    if comparison["regressions"]:
        reasons.append("fit:musical-metric-regression")
    if mismatch_delta > config.maximum_critical_mismatch_increase:
        reasons.append("fit:critical-mismatch-regression")
    if comparison["pitchContentGain"] < config.minimum_pitch_content_gain:
        reasons.append("fit:insufficient-pitch-content-gain")
    if comparison["musicalFloorGain"] < config.minimum_musical_floor_gain:
        reasons.append("fit:insufficient-musical-floor-gain")
    return {
        "passed": not reasons,
        "reasons": reasons,
        **comparison,
        "criticalMismatchDelta": mismatch_delta,
        "pdfEventFidelity": fidelity,
        "ranking": {
            "pitchContentGain": comparison["pitchContentGain"],
            "musicalFloorGain": comparison["musicalFloorGain"],
            "musicalMeanGain": comparison["musicalMeanGain"],
            "candidateMusicalFloor": musical_floor(candidate_fit),
            "candidateMusicalMean": musical_mean(candidate_fit),
        },
    }


def lock_fit_candidate(
    candidates: Sequence[Mapping[str, Any]],
    *,
    config: ContextSplitConfig,
    baseline_name: str = "no-prune",
) -> dict[str, Any]:
    """Rank using fit data only; validation/canary are deliberately never read here."""
    if not candidates:
        raise ValueError("at least one candidate is required")
    by_name: dict[str, Mapping[str, Any]] = {}
    for candidate in candidates:
        name = str(candidate.get("name") or "")
        if not name:
            raise ValueError("every candidate requires a name")
        if name in by_name:
            raise ValueError(f"duplicate candidate name {name}")
        by_name[name] = candidate
    if baseline_name not in by_name:
        raise ValueError(f"required baseline {baseline_name!r} is missing")

    baseline = by_name[baseline_name]
    baseline_reasons = _safety_reasons(baseline, config)
    if baseline_reasons:
        raise ValueError("baseline safety contract failed: " + ", ".join(baseline_reasons))
    _stage_metrics(baseline, "fit")

    evaluations: list[dict[str, Any]] = []
    for name in sorted(by_name):
        if name == baseline_name:
            continue
        evaluation = _fit_evaluation(baseline, by_name[name], config=config)
        evaluations.append({"name": name, "policy": str(by_name[name].get("policy") or "unknown"), **evaluation})

    winners = [item for item in evaluations if item["passed"]]
    if winners:
        winners.sort(
            key=lambda item: (
                -float(item["ranking"]["pitchContentGain"]),
                -float(item["ranking"]["musicalFloorGain"]),
                -float(item["ranking"]["musicalMeanGain"]),
                str(item["name"]),
            )
        )
        locked = str(winners[0]["name"])
        reason = "fit-qualified-candidate-locked"
    else:
        locked = baseline_name
        reason = "deterministic-no-prune-fallback"

    return {
        "schemaVersion": 14404,
        "instrument": "rhythm",
        "baseline": baseline_name,
        "locked": locked,
        "lockedReason": reason,
        "fitOnlyRanking": True,
        "validationReadDuringLock": False,
        "canaryReadDuringLock": False,
        "baselineGeneratedMeasureSetPreservationRequired": True,
        "evaluations": evaluations,
    }


def gate_locked_candidate(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    *,
    stage: str,
    config: ContextSplitConfig,
) -> dict[str, Any]:
    """Pass/fail one already-locked candidate; this function never ranks alternatives."""
    if stage not in ("validation", "canary"):
        raise ValueError("gate stage must be validation or canary")
    baseline_metrics = _stage_metrics(baseline, stage)
    candidate_metrics = _stage_metrics(candidate, stage)
    maximum_regression = (
        config.maximum_per_metric_regression
        if stage == "validation"
        else config.maximum_canary_regression
    )
    comparison = compare_metric_sets(
        baseline_metrics,
        candidate_metrics,
        maximum_regression=maximum_regression,
    )
    mismatch_delta = critical_mismatch_count(candidate_metrics) - critical_mismatch_count(baseline_metrics)
    fidelity = pdf_event_fidelity(candidate_metrics)
    reasons = _safety_reasons(candidate, config)
    if fidelity != config.required_pdf_event_fidelity:
        reasons.append(f"{stage}:pdf-event-fidelity-not-exact")
    if comparison["regressions"]:
        reasons.append(f"{stage}:musical-metric-regression")
    if mismatch_delta > config.maximum_critical_mismatch_increase:
        reasons.append(f"{stage}:critical-mismatch-regression")
    return {
        "stage": stage,
        "passed": not reasons,
        "reasons": reasons,
        **comparison,
        "criticalMismatchDelta": mismatch_delta,
        "pdfEventFidelity": fidelity,
        "alternativeCandidatesRead": False,
    }


def staged_select_candidate(
    candidates: Sequence[Mapping[str, Any]],
    *,
    config: ContextSplitConfig,
    baseline_name: str = "no-prune",
) -> dict[str, Any]:
    """Fit-lock exactly one candidate, then gate it once on validation and canary."""
    by_name = {str(item.get("name") or ""): item for item in candidates}
    fit_lock = lock_fit_candidate(candidates, config=config, baseline_name=baseline_name)
    locked_name = str(fit_lock["locked"])
    if locked_name == baseline_name:
        return {
            "schemaVersion": 14404,
            "instrument": "rhythm",
            "baseline": baseline_name,
            "fitLock": fit_lock,
            "selected": baseline_name,
            "selectedReason": "fit-no-qualified-candidate",
            "promotionAllowed": False,
            "validation": None,
            "canary": None,
            "stoppedAt": "fit",
            "alternateAfterGateFailureAllowed": False,
        }

    baseline = by_name[baseline_name]
    locked = by_name[locked_name]
    validation = gate_locked_candidate(
        baseline, locked, stage="validation", config=config
    )
    if not validation["passed"]:
        return {
            "schemaVersion": 14404,
            "instrument": "rhythm",
            "baseline": baseline_name,
            "fitLock": fit_lock,
            "selected": baseline_name,
            "selectedReason": "locked-candidate-failed-validation",
            "promotionAllowed": False,
            "validation": validation,
            "canary": None,
            "stoppedAt": "validation",
            "alternateAfterGateFailureAllowed": False,
        }

    canary = gate_locked_candidate(baseline, locked, stage="canary", config=config)
    if not canary["passed"]:
        return {
            "schemaVersion": 14404,
            "instrument": "rhythm",
            "baseline": baseline_name,
            "fitLock": fit_lock,
            "selected": baseline_name,
            "selectedReason": "locked-candidate-failed-canary",
            "promotionAllowed": False,
            "validation": validation,
            "canary": canary,
            "stoppedAt": "canary",
            "alternateAfterGateFailureAllowed": False,
        }

    return {
        "schemaVersion": 14404,
        "instrument": "rhythm",
        "baseline": baseline_name,
        "fitLock": fit_lock,
        "selected": locked_name,
        "selectedReason": "locked-candidate-passed-validation-and-canary",
        "promotionAllowed": True,
        "validation": validation,
        "canary": canary,
        "stoppedAt": "complete",
        "alternateAfterGateFailureAllowed": False,
    }


__all__ = [
    "STAGES",
    "gate_locked_candidate",
    "lock_fit_candidate",
    "staged_select_candidate",
]
