#!/usr/bin/env python3
"""Synthetic-only evidence-significance guard for V3 research iteration 3.

Frozen iteration 2 remains the source of candidate eligibility, NNLS necessity,
and lower-owner protection. This wrapper can only reject an iteration-2 PASS;
it can never promote an iteration-2 failure.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

import physical_template_plausibility_v3_iteration2 as iteration2

CONTRACT = "songsterr-fresh-v3-physical-template-evidence-significance-synthetic-research-v3"
VERSION = 3
MIN_CANDIDATE_EVIDENCE_FRACTION = 0.10

EXPECTED_ITERATION2_CONTRACT = "songsterr-fresh-v3-physical-template-owner-aware-synthetic-research-v2"
EXPECTED_ITERATION2_VERSION = 2


def _iteration2_contract_ok() -> bool:
    return bool(
        getattr(iteration2, "CONTRACT", None) == EXPECTED_ITERATION2_CONTRACT
        and getattr(iteration2, "VERSION", None) == EXPECTED_ITERATION2_VERSION
    )


def _passthrough_failure(result: dict[str, Any]) -> dict[str, Any]:
    row = dict(result)
    row["iteration2Composite"] = result
    row["promotedFromIteration2Failure"] = False
    return row


def evaluate_evidence_significance_composite(
    selected_midi: int,
    innovation: np.ndarray | list[float],
    frequencies: np.ndarray | list[float],
) -> dict[str, Any]:
    """Apply frozen iteration 2, then the prospective evidence-significance guard."""

    if not _iteration2_contract_ok():
        return {
            "passed": False,
            "status": "ITERATION2_CONTRACT_MISMATCH",
            "selectedMidi": int(selected_midi) if isinstance(selected_midi, (int, np.integer)) else selected_midi,
            "promotedFromIteration2Failure": False,
        }

    iteration2_result = iteration2.evaluate_owner_aware_composite(
        selected_midi,
        innovation,
        frequencies,
    )
    if iteration2_result.get("passed") is not True:
        return _passthrough_failure(iteration2_result)

    base_composite = iteration2_result.get("baseComposite")
    selected_template = (
        base_composite.get("selectedTemplate")
        if isinstance(base_composite, dict)
        else None
    )
    if not isinstance(selected_template, dict) or selected_template.get("valid") is not True:
        return {
            "passed": False,
            "status": "ITERATION2_PASS_WITHOUT_VALID_SELECTED_TEMPLATE",
            "selectedMidi": iteration2_result.get("selectedMidi", selected_midi),
            "iteration2Composite": iteration2_result,
            "promotedFromIteration2Failure": False,
        }

    peaks = list(selected_template.get("observedHarmonicInnovation", []))
    thresholds = list(selected_template.get("supportThresholds", []))
    supported = list(selected_template.get("supported", []))
    if not peaks or len(peaks) != len(thresholds) or len(peaks) != len(supported):
        return {
            "passed": False,
            "status": "MALFORMED_SELECTED_TEMPLATE_DIAGNOSTICS",
            "selectedMidi": iteration2_result.get("selectedMidi", selected_midi),
            "iteration2Composite": iteration2_result,
            "promotedFromIteration2Failure": False,
        }

    try:
        values = np.asarray(innovation, dtype=np.float64)
        peak_values = [float(value) for value in peaks]
        threshold_values = [float(value) for value in thresholds]
    except Exception as exc:
        return {
            "passed": False,
            "status": "ITERATION3_DIAGNOSTIC_COERCION_FAILED",
            "selectedMidi": iteration2_result.get("selectedMidi", selected_midi),
            "errorType": type(exc).__name__,
            "iteration2Composite": iteration2_result,
            "promotedFromIteration2Failure": False,
        }

    innovation_norm = float(np.linalg.norm(values))
    excess: list[float] = []
    for peak, threshold, is_supported in zip(peak_values, threshold_values, supported):
        value = max(0.0, peak - threshold) if is_supported is True else 0.0
        excess.append(float(value))

    supported_excess_norm = float(np.linalg.norm(np.asarray(excess, dtype=np.float64)))
    if not (
        math.isfinite(innovation_norm)
        and innovation_norm > 0.0
        and math.isfinite(supported_excess_norm)
        and all(math.isfinite(value) and value >= 0.0 for value in excess)
    ):
        return {
            "passed": False,
            "status": "INVALID_EVIDENCE_SIGNIFICANCE_DIAGNOSTICS",
            "selectedMidi": iteration2_result.get("selectedMidi", selected_midi),
            "innovationNorm": innovation_norm,
            "supportedExcessNorm": supported_excess_norm,
            "supportedExcess": excess,
            "iteration2Composite": iteration2_result,
            "promotedFromIteration2Failure": False,
        }

    candidate_evidence_fraction = float(supported_excess_norm / innovation_norm)
    if not math.isfinite(candidate_evidence_fraction) or candidate_evidence_fraction < 0.0:
        return {
            "passed": False,
            "status": "INVALID_CANDIDATE_EVIDENCE_FRACTION",
            "selectedMidi": iteration2_result.get("selectedMidi", selected_midi),
            "candidateEvidenceFraction": candidate_evidence_fraction,
            "iteration2Composite": iteration2_result,
            "promotedFromIteration2Failure": False,
        }

    diagnostics = {
        "iteration2Composite": iteration2_result,
        "promotedFromIteration2Failure": False,
        "innovationNorm": innovation_norm,
        "supportedExcess": excess,
        "supportedExcessNorm": supported_excess_norm,
        "candidateEvidenceFraction": candidate_evidence_fraction,
        "minimumCandidateEvidenceFraction": MIN_CANDIDATE_EVIDENCE_FRACTION,
    }

    if candidate_evidence_fraction < MIN_CANDIDATE_EVIDENCE_FRACTION:
        return {
            "passed": False,
            "status": "INSUFFICIENT_CANDIDATE_EVIDENCE_SIGNIFICANCE",
            "selectedMidi": iteration2_result.get("selectedMidi", selected_midi),
            "credibleLowerOwners": iteration2_result.get("credibleLowerOwners", []),
            "vetoingOwners": iteration2_result.get("vetoingOwners", []),
            **diagnostics,
        }

    return {
        "passed": True,
        "status": "PASS",
        "selectedMidi": iteration2_result.get("selectedMidi", selected_midi),
        "credibleLowerOwners": iteration2_result.get("credibleLowerOwners", []),
        "vetoingOwners": iteration2_result.get("vetoingOwners", []),
        **diagnostics,
    }
