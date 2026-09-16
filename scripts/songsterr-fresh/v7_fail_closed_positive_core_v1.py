#!/usr/bin/env python3
"""Fail-closed positive-core composition over frozen V7 diagnostics.

This is a mechanical research composition only. It introduces no new fitted
threshold, rank rule, score, fallback, or real/customer decision.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

import v7_kkt_raw_necessity_diagnostics_v1 as kkt

CONTRACT = "songsterr-fresh-v7-fail-closed-positive-core-v1"
VERSION = 1
EXPECTED_KKT_CONTRACT = "songsterr-fresh-v7-kkt-raw-necessity-diagnostic-v1"
EXPECTED_KKT_VERSION = 1
FROZEN_EVIDENCE_MINIMUM = 0.10

POSITIVE_CORE_CANDIDATE = "POSITIVE_CORE_CANDIDATE"
PROTECTION_REJECTED = "PROTECTION_REJECTED"
UNRESOLVED_SUPPORT_OR_CONTEXT = "UNRESOLVED_SUPPORT_OR_CONTEXT"

REASON_EVIDENCE = "CANDIDATE_EVIDENCE_SIGNIFICANCE_FAILED"
REASON_OWNER = "LOWER_OWNER_VETO_PRESENT"
REASON_KKT = "KKT_STRICT_RAW_NECESSITY_NOT_CERTIFIED"
REASON_ORDER = (REASON_EVIDENCE, REASON_OWNER, REASON_KKT)


class PositiveCoreCompositionError(RuntimeError):
    pass


def _dependency_ok() -> bool:
    return bool(
        getattr(kkt, "CONTRACT", None) == EXPECTED_KKT_CONTRACT
        and getattr(kkt, "VERSION", None) == EXPECTED_KKT_VERSION
    )


def compose_available_flags(
    support_eligible: bool,
    candidate_evidence_pass: bool,
    no_lower_owner_veto: bool,
    kkt_strict_raw_necessity_certified: bool,
) -> dict[str, Any]:
    """Pure prospectively frozen Boolean truth-table composition.

    Inputs represent otherwise available/valid diagnostics. A false support
    precondition routes unresolved regardless of the other Boolean values.
    """

    flags = (
        support_eligible,
        candidate_evidence_pass,
        no_lower_owner_veto,
        kkt_strict_raw_necessity_certified,
    )
    if not all(isinstance(value, bool) for value in flags):
        raise PositiveCoreCompositionError("BOOLEAN_FLAGS_REQUIRED")

    if not support_eligible:
        return {
            "compositionState": UNRESOLVED_SUPPORT_OR_CONTEXT,
            "protectionRejectionReasons": [],
        }

    reasons: list[str] = []
    if not candidate_evidence_pass:
        reasons.append(REASON_EVIDENCE)
    if not no_lower_owner_veto:
        reasons.append(REASON_OWNER)
    if not kkt_strict_raw_necessity_certified:
        reasons.append(REASON_KKT)

    if reasons:
        return {
            "compositionState": PROTECTION_REJECTED,
            "protectionRejectionReasons": reasons,
        }

    return {
        "compositionState": POSITIVE_CORE_CANDIDATE,
        "protectionRejectionReasons": [],
    }


def _base_output(selected_midi: int, dependency: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract": CONTRACT,
        "version": VERSION,
        "selectedMidi": int(selected_midi),
        "positiveCoreDefined": True,
        "customerDecisionDefined": False,
        "realCorrectnessDefined": False,
        "historicalNecessityThresholdApplied": False,
        "rawMagnitudeThresholdDefined": False,
        "rankCutoffDefined": False,
        "scoreDefined": False,
        "reattackFallbackDefined": False,
        "supportEligible": None,
        "candidateEvidencePass": None,
        "noLowerOwnerVeto": None,
        "kktStrictRawNecessityCertified": None,
        "compositionState": UNRESOLVED_SUPPORT_OR_CONTEXT,
        "protectionRejectionReasons": [],
        "dependencyDiagnostic": dependency,
    }


def evaluate_fail_closed_positive_core(
    audio: np.ndarray | list[float],
    onset_sample: int,
    selected_midi: int,
    frequencies: np.ndarray | list[float],
) -> dict[str, Any]:
    """Compose frozen diagnostics without rescue or cross-channel trade-off."""

    if not _dependency_ok():
        raise PositiveCoreCompositionError("FROZEN_KKT_DEPENDENCY_MISMATCH")
    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        raise PositiveCoreCompositionError("SELECTED_MIDI_INTEGER_REQUIRED")
    selected_midi = int(selected_midi)

    dependency = kkt.evaluate_kkt_raw_necessity_diagnostic(
        audio,
        onset_sample,
        selected_midi,
        frequencies,
    )
    if dependency.get("contract") != EXPECTED_KKT_CONTRACT or dependency.get("version") != EXPECTED_KKT_VERSION:
        raise PositiveCoreCompositionError("KKT_PAYLOAD_IDENTITY_MISMATCH")
    if dependency.get("selectedMidi") != selected_midi:
        raise PositiveCoreCompositionError("SELECTED_MIDI_IDENTITY_MISMATCH")
    if dependency.get("finalDecisionDefined") is not False:
        raise PositiveCoreCompositionError("KKT_DEPENDENCY_UNEXPECTED_FINAL_DECISION")
    if dependency.get("historicalNecessityThresholdApplied") is not False:
        raise PositiveCoreCompositionError("KKT_DEPENDENCY_HISTORICAL_THRESHOLD_APPLIED")

    output = _base_output(selected_midi, dependency)

    if dependency.get("onsetAvailable") is not True:
        return output

    support = dependency.get("supportContext")
    certificate = dependency.get("kktCertificate")
    if not isinstance(support, dict) or not isinstance(certificate, dict):
        return output

    support_eligible = support.get("selectedSupportValid")
    if not isinstance(support_eligible, bool):
        return output
    output["supportEligible"] = support_eligible

    if certificate.get("available") is True and certificate.get("consistencyOk") is True:
        kkt_certified = certificate.get("kktCertifiedStrictRawNecessity")
        if isinstance(kkt_certified, bool):
            output["kktStrictRawNecessityCertified"] = kkt_certified

    if not support_eligible:
        return output

    evidence = support.get("selectedCandidateEvidence")
    owners = support.get("selectedOwnerDiagnostics")
    if not isinstance(evidence, dict) or not isinstance(owners, dict):
        return output
    if evidence.get("available") is not True or owners.get("available") is not True:
        return output
    if certificate.get("available") is not True or certificate.get("consistencyOk") is not True:
        return output

    fraction = evidence.get("candidateEvidenceFraction")
    minimum = evidence.get("frozenReferenceMinimum")
    if isinstance(fraction, bool) or not isinstance(fraction, (int, float)):
        return output
    if isinstance(minimum, bool) or not isinstance(minimum, (int, float)):
        return output
    fraction = float(fraction)
    minimum = float(minimum)
    if not math.isfinite(fraction) or not math.isfinite(minimum):
        return output
    if not math.isclose(minimum, FROZEN_EVIDENCE_MINIMUM, rel_tol=0.0, abs_tol=0.0):
        raise PositiveCoreCompositionError("FROZEN_EVIDENCE_MINIMUM_MISMATCH")

    veto_rows = owners.get("vetoOwnerRows")
    if not isinstance(veto_rows, list):
        return output
    kkt_certified = certificate.get("kktCertifiedStrictRawNecessity")
    if not isinstance(kkt_certified, bool):
        return output

    evidence_pass = bool(fraction >= minimum)
    no_owner_veto = bool(len(veto_rows) == 0)

    output["candidateEvidencePass"] = evidence_pass
    output["noLowerOwnerVeto"] = no_owner_veto
    output["kktStrictRawNecessityCertified"] = kkt_certified

    composed = compose_available_flags(
        support_eligible,
        evidence_pass,
        no_owner_veto,
        kkt_certified,
    )
    output["compositionState"] = composed["compositionState"]
    output["protectionRejectionReasons"] = list(composed["protectionRejectionReasons"])
    return output
