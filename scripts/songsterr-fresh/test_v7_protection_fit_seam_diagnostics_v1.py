#!/usr/bin/env python3
"""First-run synthetic-only gate for the V7 protection/raw-fit seam diagnostic."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as v6
import onset_birth_corroboration_v7 as historical_v7
import v7_dual_view_diagnostics_v1 as dual
import v7_fixed_feature_competition_diagnostics_v1 as fixed
import v7_protection_fit_seam_diagnostics_v1 as diagnostic

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "v6_onset_birth_synthetic_fixtures.json"
REPETITIONS = 3
EXPECTED_FIXTURE_CONTRACT = "songsterr-fresh-v6-onset-birth-synthetic-fixtures-v1"


class MechanicalInvariantError(RuntimeError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _check_finite(value: Any, path: str = "root") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise MechanicalInvariantError(f"NONFINITE:{path}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _check_finite(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _check_finite(item, f"{path}.{key}")
        return
    raise MechanicalInvariantError(f"UNEXPECTED_TYPE:{path}:{type(value).__name__}")


def _evaluate_fixture(fixture: dict[str, Any], frequencies: np.ndarray) -> dict[str, Any]:
    fixture_id = str(fixture["id"])
    selected_midi = int(fixture["selectedMidi"])
    audio = v6._fixture_audio(fixture)
    onset_sample = int(round(float(fixture["onsetSeconds"]) * v6.SAMPLE_RATE))

    payload = diagnostic.evaluate_protection_fit_seam(
        audio,
        onset_sample,
        selected_midi,
        frequencies,
    )
    if payload.get("contract") != diagnostic.CONTRACT or payload.get("version") != diagnostic.VERSION:
        raise MechanicalInvariantError(f"CONTRACT:{fixture_id}")
    if payload.get("selectedMidi") != selected_midi:
        raise MechanicalInvariantError(f"MIDI_IDENTITY:{fixture_id}")
    if payload.get("finalDecisionDefined") is not False:
        raise MechanicalInvariantError(f"FINAL_DECISION_DEFINED:{fixture_id}")
    for forbidden in (
        "finalDecision",
        "successorClassification",
        "rawNecessityPassed",
        "passed",
        "classification",
    ):
        if forbidden in payload:
            raise MechanicalInvariantError(f"FORBIDDEN_TOP_LEVEL_VERDICT:{fixture_id}:{forbidden}")

    _check_finite(payload, fixture_id)

    if payload.get("onsetAvailable") is True:
        onset = v6._onset_innovation_spectrum(audio, onset_sample)
        if onset.get("status") != "OK":
            raise MechanicalInvariantError(f"ONSET_RECONSTRUCTION:{fixture_id}")
        raw = np.asarray(onset["innovation"], dtype=np.float64)

        expected_dual = dual.evaluate_dual_view_diagnostics(
            selected_midi,
            raw,
            frequencies,
        )
        expected_fixed = fixed.evaluate_fixed_feature_competition_diagnostic(
            audio,
            onset_sample,
            selected_midi,
            frequencies,
        )
        expected_historical_v7 = historical_v7.evaluate_in_memory_innovation(
            selected_midi,
            raw,
            frequencies,
        )

        references = payload.get("historicalReferences")
        if not isinstance(references, dict):
            raise MechanicalInvariantError(f"HISTORICAL_REFERENCES_MISSING:{fixture_id}")
        if _canonical(references.get("dualViewPayload")) != _canonical(expected_dual):
            raise MechanicalInvariantError(f"DUAL_REFERENCE_MISMATCH:{fixture_id}")
        if _canonical(references.get("fixedFeaturePayload")) != _canonical(expected_fixed):
            raise MechanicalInvariantError(f"FIXED_REFERENCE_MISMATCH:{fixture_id}")
        if _canonical(references.get("historicalV7RawComposite")) != _canonical(expected_historical_v7):
            raise MechanicalInvariantError(f"HISTORICAL_V7_REFERENCE_MISMATCH:{fixture_id}")

        support_view = expected_dual.get("supportView")
        if not isinstance(support_view, dict):
            raise MechanicalInvariantError(f"EXPECTED_SUPPORT_VIEW_MISSING:{fixture_id}")
        expected_support = {
            "rawView": expected_dual.get("rawView"),
            "supportNorm": support_view.get("norm"),
            "supportPositiveBinCount": support_view.get("positiveBinCount"),
            "retainedCenterCount": support_view.get("retainedCenterCount"),
            "retainedCenters": list(support_view.get("retainedCenters", [])),
            "selectedTemplate": dict(support_view.get("selectedTemplate", {})),
            "validCandidateCount": support_view.get("validCandidateCount"),
            "validCandidateMidis": list(support_view.get("validCandidateMidis", [])),
            "ownerDiagnostics": support_view.get("ownerDiagnostics"),
            "candidateEvidence": support_view.get("candidateEvidence"),
        }
        if _canonical(payload.get("supportMeasurements")) != _canonical(expected_support):
            raise MechanicalInvariantError(f"SUPPORT_MEASUREMENT_MISMATCH:{fixture_id}")

        fixed_fits = expected_fixed.get("fixedFeatureFits")
        if not isinstance(fixed_fits, dict):
            raise MechanicalInvariantError(f"EXPECTED_FIXED_FITS_MISSING:{fixture_id}")
        if _canonical(payload.get("rawFixedFit")) != _canonical(fixed_fits.get("gateFree49FixedFit")):
            raise MechanicalInvariantError(f"RAW_FIXED_FIT_MISMATCH:{fixture_id}")

        selected_template = support_view.get("selectedTemplate")
        selected_template = selected_template if isinstance(selected_template, dict) else {}
        owner = support_view.get("ownerDiagnostics")
        evidence = support_view.get("candidateEvidence")
        owner = owner if isinstance(owner, dict) else {}
        evidence = evidence if isinstance(evidence, dict) else {}
        if selected_template.get("valid") is True:
            if owner.get("available") is not True:
                raise MechanicalInvariantError(f"ELIGIBLE_WITHOUT_OWNER_DIAGNOSTIC:{fixture_id}")
            if evidence.get("available") is not True:
                raise MechanicalInvariantError(f"ELIGIBLE_WITHOUT_EVIDENCE_DIAGNOSTIC:{fixture_id}")
        else:
            if owner.get("available") is True or evidence.get("available") is True:
                raise MechanicalInvariantError(f"INELIGIBLE_WITH_AVAILABLE_SUPPORT_GUARD:{fixture_id}")

        raw_fit = payload.get("rawFixedFit")
        if not isinstance(raw_fit, dict) or raw_fit.get("available") is not True:
            raise MechanicalInvariantError(f"ALL49_FIXED_FIT_UNAVAILABLE:{fixture_id}")
        if int(raw_fit.get("candidateCount", -1)) != 49:
            raise MechanicalInvariantError(f"ALL49_FIXED_CANDIDATE_COUNT:{fixture_id}")
    else:
        if payload.get("supportMeasurements") is not None:
            raise MechanicalInvariantError(f"FABRICATED_SUPPORT:{fixture_id}")
        if payload.get("rawFixedFit") is not None:
            raise MechanicalInvariantError(f"FABRICATED_RAW_FIT:{fixture_id}")
        if payload.get("historicalReferences") is not None:
            raise MechanicalInvariantError(f"FABRICATED_HISTORICAL_REFERENCE:{fixture_id}")

    return {
        "fixtureId": fixture_id,
        "selectedMidi": selected_midi,
        "referenceExpectedClassification": str(fixture["expectedClassification"]),
        "referenceExpectedUsedForComputation": False,
        "diagnostic": payload,
    }


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("contract") != EXPECTED_FIXTURE_CONTRACT:
        raise MechanicalInvariantError("FIXTURE_CONTRACT_MISMATCH")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 23:
        raise MechanicalInvariantError("EXPECTED_23_FIXTURES")

    if diagnostic.CONTRACT != "songsterr-fresh-v7-protection-fit-seam-diagnostic-v1":
        raise MechanicalInvariantError("DIAGNOSTIC_CONTRACT_CHANGED")
    if diagnostic.VERSION != 1:
        raise MechanicalInvariantError("DIAGNOSTIC_VERSION_CHANGED")

    frequencies = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))

    repetitions: list[list[dict[str, Any]]] = []
    for _ in range(REPETITIONS):
        repetitions.append([_evaluate_fixture(fixture, frequencies) for fixture in fixtures])

    canonical_runs = [_canonical(rows) for rows in repetitions]
    deterministic = len(set(canonical_runs)) == 1
    if not deterministic:
        raise MechanicalInvariantError("NONDETERMINISTIC_OUTPUT")

    rows = repetitions[0]
    expected_ids = [str(fixture["id"]) for fixture in fixtures]
    observed_ids = [str(row["fixtureId"]) for row in rows]
    if observed_ids != expected_ids:
        raise MechanicalInvariantError("FIXTURE_ORDER_CHANGED")

    onset_available_count = sum(
        1 for row in rows if row["diagnostic"].get("onsetAvailable") is True
    )
    support_selected_eligible_count = 0
    evidence_available_count = 0
    owner_available_count = 0
    support_eligible_historical_composite_fail_count = 0
    raw_fixed_fit_available_count = 0

    for row in rows:
        payload = row["diagnostic"]
        support = payload.get("supportMeasurements")
        references = payload.get("historicalReferences")
        if isinstance(support, dict):
            template = support.get("selectedTemplate")
            owner = support.get("ownerDiagnostics")
            evidence = support.get("candidateEvidence")
            if isinstance(template, dict) and template.get("valid") is True:
                support_selected_eligible_count += 1
                if isinstance(references, dict):
                    dual_ref = references.get("dualViewPayload")
                    dual_ref = dual_ref if isinstance(dual_ref, dict) else {}
                    support_ref = dual_ref.get("supportView")
                    support_ref = support_ref if isinstance(support_ref, dict) else {}
                    frozen_composite = support_ref.get("frozenComposite")
                    if isinstance(frozen_composite, dict) and frozen_composite.get("passed") is not True:
                        support_eligible_historical_composite_fail_count += 1
            if isinstance(owner, dict) and owner.get("available") is True:
                owner_available_count += 1
            if isinstance(evidence, dict) and evidence.get("available") is True:
                evidence_available_count += 1
        raw_fit = payload.get("rawFixedFit")
        if isinstance(raw_fit, dict) and raw_fit.get("available") is True:
            raw_fixed_fit_available_count += 1

    output = {
        "contract": "songsterr-fresh-v7-protection-fit-seam-diagnostic-synthetic-test-v1",
        "diagnosticContract": diagnostic.CONTRACT,
        "fixtureContract": manifest["contract"],
        "fixtureCount": len(rows),
        "repetitions": REPETITIONS,
        "deterministic": deterministic,
        "onsetAvailableCount": onset_available_count,
        "supportSelectedEligibleCount": support_selected_eligible_count,
        "ownerDiagnosticAvailableCount": owner_available_count,
        "candidateEvidenceAvailableCount": evidence_available_count,
        "supportEligibleHistoricalCompositeFailCount": support_eligible_historical_composite_fail_count,
        "rawFixedFitAvailableCount": raw_fixed_fit_available_count,
        "finalDecisionDefined": False,
        "referenceExpectedUsedForComputation": False,
        "rawNecessityThresholdDefined": False,
        "temporalDiagnosticReconstructed": False,
        "realCorpusEvaluated": False,
        "modelInferenceInvoked": False,
        "basicPitchInvoked": False,
        "networkInvoked": False,
        "customerEligibleEvents": 0,
        "mayAdvanceDelivery": False,
        "mechanicalDiagnosticStatus": "COMPLETE",
        "rows": rows,
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
