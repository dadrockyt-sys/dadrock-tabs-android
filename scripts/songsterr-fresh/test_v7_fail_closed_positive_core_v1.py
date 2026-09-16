#!/usr/bin/env python3
"""Prospectively frozen mechanical gate for V7 fail-closed composition."""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as v6
import v7_fail_closed_positive_core_v1 as composer
import v7_kkt_raw_necessity_diagnostics_v1 as kkt

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "v6_onset_birth_synthetic_fixtures.json"
REPETITIONS = 3
EXPECTED_FIXTURE_CONTRACT = "songsterr-fresh-v6-onset-birth-synthetic-fixtures-v1"


class MechanicalCompositionError(RuntimeError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _check_finite(value: Any, path: str = "root") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise MechanicalCompositionError(f"NONFINITE:{path}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _check_finite(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _check_finite(item, f"{path}.{key}")
        return
    raise MechanicalCompositionError(f"UNEXPECTED_TYPE:{path}:{type(value).__name__}")


def _expected_available_flags(
    support_eligible: bool,
    evidence_pass: bool,
    no_owner_veto: bool,
    kkt_certified: bool,
) -> tuple[str, list[str]]:
    if not support_eligible:
        return composer.UNRESOLVED_SUPPORT_OR_CONTEXT, []
    if evidence_pass and no_owner_veto and kkt_certified:
        return composer.POSITIVE_CORE_CANDIDATE, []
    reasons: list[str] = []
    if not evidence_pass:
        reasons.append(composer.REASON_EVIDENCE)
    if not no_owner_veto:
        reasons.append(composer.REASON_OWNER)
    if not kkt_certified:
        reasons.append(composer.REASON_KKT)
    return composer.PROTECTION_REJECTED, reasons


def _truth_table_once() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for support, evidence, no_owner, kkt_certified in itertools.product(
        (False, True), repeat=4
    ):
        observed = composer.compose_available_flags(
            support,
            evidence,
            no_owner,
            kkt_certified,
        )
        expected_state, expected_reasons = _expected_available_flags(
            support,
            evidence,
            no_owner,
            kkt_certified,
        )
        if observed.get("compositionState") != expected_state:
            raise MechanicalCompositionError(
                f"TRUTH_TABLE_STATE:{support}:{evidence}:{no_owner}:{kkt_certified}"
            )
        if observed.get("protectionRejectionReasons") != expected_reasons:
            raise MechanicalCompositionError(
                f"TRUTH_TABLE_REASONS:{support}:{evidence}:{no_owner}:{kkt_certified}"
            )
        rows.append(
            {
                "supportEligible": support,
                "candidateEvidencePass": evidence,
                "noLowerOwnerVeto": no_owner,
                "kktStrictRawNecessityCertified": kkt_certified,
                "expectedState": expected_state,
                "expectedReasons": expected_reasons,
                "observed": observed,
            }
        )
    return rows


def _independent_expected_from_dependency(
    dependency: dict[str, Any],
) -> tuple[str, list[str], dict[str, Any]]:
    flags = {
        "supportEligible": None,
        "candidateEvidencePass": None,
        "noLowerOwnerVeto": None,
        "kktStrictRawNecessityCertified": None,
    }
    if dependency.get("onsetAvailable") is not True:
        return composer.UNRESOLVED_SUPPORT_OR_CONTEXT, [], flags

    support = dependency.get("supportContext")
    certificate = dependency.get("kktCertificate")
    if not isinstance(support, dict) or not isinstance(certificate, dict):
        return composer.UNRESOLVED_SUPPORT_OR_CONTEXT, [], flags

    selected_support = support.get("selectedSupportValid")
    if not isinstance(selected_support, bool):
        return composer.UNRESOLVED_SUPPORT_OR_CONTEXT, [], flags
    flags["supportEligible"] = selected_support

    if certificate.get("available") is True and certificate.get("consistencyOk") is True:
        cert_value = certificate.get("kktCertifiedStrictRawNecessity")
        if isinstance(cert_value, bool):
            flags["kktStrictRawNecessityCertified"] = cert_value

    if not selected_support:
        return composer.UNRESOLVED_SUPPORT_OR_CONTEXT, [], flags

    evidence = support.get("selectedCandidateEvidence")
    owners = support.get("selectedOwnerDiagnostics")
    if not isinstance(evidence, dict) or not isinstance(owners, dict):
        return composer.UNRESOLVED_SUPPORT_OR_CONTEXT, [], flags
    if evidence.get("available") is not True or owners.get("available") is not True:
        return composer.UNRESOLVED_SUPPORT_OR_CONTEXT, [], flags
    if certificate.get("available") is not True or certificate.get("consistencyOk") is not True:
        return composer.UNRESOLVED_SUPPORT_OR_CONTEXT, [], flags

    fraction = evidence.get("candidateEvidenceFraction")
    minimum = evidence.get("frozenReferenceMinimum")
    veto_rows = owners.get("vetoOwnerRows")
    cert_value = certificate.get("kktCertifiedStrictRawNecessity")
    if (
        isinstance(fraction, bool)
        or not isinstance(fraction, (int, float))
        or isinstance(minimum, bool)
        or not isinstance(minimum, (int, float))
        or not isinstance(veto_rows, list)
        or not isinstance(cert_value, bool)
    ):
        return composer.UNRESOLVED_SUPPORT_OR_CONTEXT, [], flags
    fraction = float(fraction)
    minimum = float(minimum)
    if not math.isfinite(fraction) or not math.isfinite(minimum):
        return composer.UNRESOLVED_SUPPORT_OR_CONTEXT, [], flags
    if not math.isclose(minimum, 0.10, rel_tol=0.0, abs_tol=0.0):
        raise MechanicalCompositionError("FROZEN_EVIDENCE_MINIMUM_CHANGED")

    evidence_pass = bool(fraction >= minimum)
    no_owner = bool(len(veto_rows) == 0)
    flags["candidateEvidencePass"] = evidence_pass
    flags["noLowerOwnerVeto"] = no_owner
    flags["kktStrictRawNecessityCertified"] = cert_value

    state, reasons = _expected_available_flags(
        selected_support,
        evidence_pass,
        no_owner,
        cert_value,
    )
    return state, reasons, flags


def _evaluate_fixture(fixture: dict[str, Any], frequencies: np.ndarray) -> dict[str, Any]:
    fixture_id = str(fixture["id"])
    selected_midi = int(fixture["selectedMidi"])
    audio = v6._fixture_audio(fixture)
    onset_sample = int(round(float(fixture["onsetSeconds"]) * v6.SAMPLE_RATE))

    composed = composer.evaluate_fail_closed_positive_core(
        audio,
        onset_sample,
        selected_midi,
        frequencies,
    )
    dependency = kkt.evaluate_kkt_raw_necessity_diagnostic(
        audio,
        onset_sample,
        selected_midi,
        frequencies,
    )

    if composed.get("contract") != composer.CONTRACT or composed.get("version") != composer.VERSION:
        raise MechanicalCompositionError(f"COMPOSER_IDENTITY:{fixture_id}")
    if composed.get("selectedMidi") != selected_midi:
        raise MechanicalCompositionError(f"MIDI_IDENTITY:{fixture_id}")
    if _canonical(composed.get("dependencyDiagnostic")) != _canonical(dependency):
        raise MechanicalCompositionError(f"DEPENDENCY_PAYLOAD_MISMATCH:{fixture_id}")

    expected_state, expected_reasons, expected_flags = _independent_expected_from_dependency(
        dependency
    )
    if composed.get("compositionState") != expected_state:
        raise MechanicalCompositionError(
            f"COMPOSITION_STATE:{fixture_id}:{composed.get('compositionState')}!={expected_state}"
        )
    if composed.get("protectionRejectionReasons") != expected_reasons:
        raise MechanicalCompositionError(f"COMPOSITION_REASONS:{fixture_id}")
    for key, expected in expected_flags.items():
        if composed.get(key) != expected:
            raise MechanicalCompositionError(
                f"COMPOSITION_FLAG:{fixture_id}:{key}:{composed.get(key)}!={expected}"
            )

    fixed_false = (
        "customerDecisionDefined",
        "realCorrectnessDefined",
        "historicalNecessityThresholdApplied",
        "rawMagnitudeThresholdDefined",
        "rankCutoffDefined",
        "scoreDefined",
        "reattackFallbackDefined",
    )
    for key in fixed_false:
        if composed.get(key) is not False:
            raise MechanicalCompositionError(f"FORBIDDEN_AUTHORITY:{fixture_id}:{key}")
    if composed.get("positiveCoreDefined") is not True:
        raise MechanicalCompositionError(f"POSITIVE_CORE_NOT_DEFINED:{fixture_id}")

    if composed.get("compositionState") == composer.POSITIVE_CORE_CANDIDATE:
        if not all(
            composed.get(key) is True
            for key in (
                "supportEligible",
                "candidateEvidencePass",
                "noLowerOwnerVeto",
                "kktStrictRawNecessityCertified",
            )
        ):
            raise MechanicalCompositionError(f"ILLEGAL_POSITIVE_RESCUE:{fixture_id}")
    if composed.get("supportEligible") is False:
        if composed.get("compositionState") != composer.UNRESOLVED_SUPPORT_OR_CONTEXT:
            raise MechanicalCompositionError(f"SUPPORT_FAILURE_RESCUED:{fixture_id}")

    for forbidden in (
        "expectedClassification",
        "historicalExpectedClassification",
        "correctnessPass",
        "customerEligible",
        "rawNecessityPassed",
        "rankPassed",
        "compositeScore",
    ):
        if forbidden in composed:
            raise MechanicalCompositionError(f"FORBIDDEN_FIELD:{fixture_id}:{forbidden}")

    _check_finite(composed, fixture_id)
    return {
        "fixtureId": fixture_id,
        "selectedMidi": selected_midi,
        "historicalExpectedUsedForComputation": False,
        "composition": composed,
    }


def main() -> int:
    if composer.CONTRACT != "songsterr-fresh-v7-fail-closed-positive-core-v1" or composer.VERSION != 1:
        raise MechanicalCompositionError("COMPOSER_CONTRACT_CHANGED")
    if kkt.CONTRACT != "songsterr-fresh-v7-kkt-raw-necessity-diagnostic-v1" or kkt.VERSION != 1:
        raise MechanicalCompositionError("KKT_CONTRACT_CHANGED")
    if not math.isclose(composer.FROZEN_EVIDENCE_MINIMUM, 0.10, rel_tol=0.0, abs_tol=0.0):
        raise MechanicalCompositionError("COMPOSER_EVIDENCE_MINIMUM_CHANGED")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("contract") != EXPECTED_FIXTURE_CONTRACT:
        raise MechanicalCompositionError("FIXTURE_CONTRACT_MISMATCH")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 23:
        raise MechanicalCompositionError("EXPECTED_23_FIXTURES")

    frequencies = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))

    truth_repetitions = [_truth_table_once() for _ in range(REPETITIONS)]
    if any(len(rows) != 16 for rows in truth_repetitions):
        raise MechanicalCompositionError("EXPECTED_16_TRUTH_TABLE_ROWS")
    truth_serialized = [_canonical(rows) for rows in truth_repetitions]
    truth_deterministic = len(set(truth_serialized)) == 1
    if not truth_deterministic:
        raise MechanicalCompositionError("TRUTH_TABLE_NONDETERMINISTIC")

    audio_repetitions: list[list[dict[str, Any]]] = []
    for _ in range(REPETITIONS):
        audio_repetitions.append(
            [_evaluate_fixture(fixture, frequencies) for fixture in fixtures]
        )
    audio_serialized = [_canonical(rows) for rows in audio_repetitions]
    audio_deterministic = len(set(audio_serialized)) == 1
    if not audio_deterministic:
        raise MechanicalCompositionError("AUDIO_COMPOSITION_NONDETERMINISTIC")

    rows = audio_repetitions[0]
    if [row["fixtureId"] for row in rows] != [str(fixture["id"]) for fixture in fixtures]:
        raise MechanicalCompositionError("FIXTURE_ORDER_CHANGED")

    descriptive_counts = {
        state: sum(
            1
            for row in rows
            if row["composition"].get("compositionState") == state
        )
        for state in (
            composer.POSITIVE_CORE_CANDIDATE,
            composer.PROTECTION_REJECTED,
            composer.UNRESOLVED_SUPPORT_OR_CONTEXT,
        )
    }
    if sum(descriptive_counts.values()) != 23:
        raise MechanicalCompositionError("DESCRIPTIVE_STATE_COUNT_MISMATCH")

    output = {
        "contract": "songsterr-fresh-v7-fail-closed-positive-core-synthetic-test-v1",
        "compositionContract": composer.CONTRACT,
        "kktContract": kkt.CONTRACT,
        "fixtureContract": manifest["contract"],
        "truthTableRowCount": 16,
        "fixtureCount": 23,
        "repetitions": REPETITIONS,
        "truthTableDeterministic": truth_deterministic,
        "audioDeterministic": audio_deterministic,
        "historicalExpectedUsedForComputation": False,
        "classCountExpectationFrozen": False,
        "descriptiveCompositionCounts": descriptive_counts,
        "positiveCoreDefined": True,
        "customerDecisionDefined": False,
        "realCorrectnessDefined": False,
        "historicalNecessityThresholdApplied": False,
        "rawMagnitudeThresholdDefined": False,
        "rankCutoffDefined": False,
        "scoreDefined": False,
        "reattackFallbackDefined": False,
        "temporalDiagnosticReconstructed": False,
        "realCorpusEvaluated": False,
        "modelInferenceInvoked": False,
        "basicPitchInvoked": False,
        "networkInvoked": False,
        "customerEligibleEvents": 0,
        "mayAdvanceDelivery": False,
        "mechanicalCompositionStatus": "COMPLETE",
        "truthTable": truth_repetitions[0],
        "rows": rows,
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
