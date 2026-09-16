#!/usr/bin/env python3
"""First-run synthetic-only test for V7 dual-view diagnostics V1.

This test checks deterministic/mechanical diagnostic integrity only. It does not
define or score a new classifier against the frozen expected classifications.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as v6
import physical_template_plausibility_v3 as base
import v7_dual_view_diagnostics_v1 as diagnostic

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "v6_onset_birth_synthetic_fixtures.json"
REPETITIONS = 3
EXPECTED_FIXTURE_CONTRACT = "songsterr-fresh-v6-onset-birth-synthetic-fixtures-v1"


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _assert_finite_numbers(value: Any, path: str = "root") -> None:
    if isinstance(value, bool) or value is None or isinstance(value, (str, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise AssertionError(f"nonfinite diagnostic at {path}: {value}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _assert_finite_numbers(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _assert_finite_numbers(item, f"{path}.{key}")
        return
    raise AssertionError(f"unexpected diagnostic type at {path}: {type(value).__name__}")


def _nested_support_necessity(support_composite: dict[str, Any]) -> float | None:
    iteration2 = support_composite.get("iteration2Composite")
    if not isinstance(iteration2, dict):
        return None
    base_composite = iteration2.get("baseComposite")
    if not isinstance(base_composite, dict):
        return None
    value = base_composite.get("necessityFraction")
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _summarize_diag(payload: dict[str, Any]) -> dict[str, Any]:
    support = payload["supportView"]
    template = support["selectedTemplate"]
    composite = support["frozenComposite"]
    evidence = support["candidateEvidence"]
    owners = support["ownerDiagnostics"]
    dual_fit = payload["dualViewFit"]
    return {
        "selectedMidi": payload["selectedMidi"],
        "finalDecisionDefined": payload["finalDecisionDefined"],
        "rawNorm": payload["rawView"]["norm"],
        "rawPositiveBinCount": payload["rawView"]["positiveBinCount"],
        "supportNorm": support["norm"],
        "supportPositiveBinCount": support["positiveBinCount"],
        "retainedCenterCount": support["retainedCenterCount"],
        "supportSelectedTemplateValid": template.get("valid") is True,
        "supportSelectedTemplateStatus": template.get("status"),
        "supportSelectedCents": template.get("cents"),
        "supportSupportedHarmonicCount": template.get("supportedHarmonicCount"),
        "supportWeightedHarmonicCoverage": template.get("weightedHarmonicCoverage"),
        "supportValidCandidateCount": support["validCandidateCount"],
        "supportFrozenCompositePassed": composite.get("passed") is True,
        "supportFrozenCompositeStatus": composite.get("status"),
        "supportFrozenNecessityFraction": _nested_support_necessity(composite),
        "supportCandidateEvidenceAvailable": evidence.get("available") is True,
        "supportCandidateEvidenceStatus": evidence.get("availabilityStatus"),
        "supportCandidateEvidenceFraction": evidence.get("candidateEvidenceFraction"),
        "credibleLowerOwnerMidis": [
            row["ownerMidi"] for row in owners.get("credibleOwnerRows", [])
        ],
        "vetoLowerOwnerMidis": [
            row["ownerMidi"] for row in owners.get("vetoOwnerRows", [])
        ],
        "dualViewFitAvailable": dual_fit.get("available") is True,
        "dualViewFitStatus": dual_fit.get("availabilityStatus"),
        "dualViewValidCandidateCount": dual_fit.get("validCandidateCount"),
        "dualViewFeatureBinCount": dual_fit.get("featureBinCount"),
        "dualViewSelectedCoefficient": dual_fit.get("selectedCoefficient"),
        "dualViewRawFeatureEnergy": dual_fit.get("rawFeatureEnergy"),
        "dualViewRawNecessityFraction": dual_fit.get("rawNecessityFraction"),
    }


def _evaluate_fixture(fixture: dict[str, Any], frequencies: np.ndarray) -> dict[str, Any]:
    fixture_id = str(fixture["id"])
    selected_midi = int(fixture["selectedMidi"])
    reference_expected = str(fixture["expectedClassification"])
    audio = v6._fixture_audio(fixture)
    onset_sample = int(round(float(fixture["onsetSeconds"]) * v6.SAMPLE_RATE))

    try:
        onset = v6._onset_innovation_spectrum(audio, onset_sample)
    except v6.CorroborationError as exc:
        return {
            "fixtureId": fixture_id,
            "selectedMidi": selected_midi,
            "referenceExpectedClassification": reference_expected,
            "referenceExpectedUsedForComputation": False,
            "onsetStatus": "CONTEXT_ERROR",
            "onsetReason": str(exc),
            "diagnosticAvailable": False,
            "finalDecisionDefined": False,
        }

    onset_status = str(onset.get("status", "UNKNOWN"))
    if onset_status != "OK":
        return {
            "fixtureId": fixture_id,
            "selectedMidi": selected_midi,
            "referenceExpectedClassification": reference_expected,
            "referenceExpectedUsedForComputation": False,
            "onsetStatus": onset_status,
            "onsetReason": onset_status,
            "analysisRms": onset.get("analysisRms"),
            "innovationEnergy": onset.get("innovationEnergy"),
            "diagnosticAvailable": False,
            "finalDecisionDefined": False,
        }

    raw = np.asarray(onset["innovation"], dtype=np.float64)
    payload = diagnostic.evaluate_dual_view_diagnostics(selected_midi, raw, frequencies)
    if payload.get("contract") != diagnostic.CONTRACT or payload.get("version") != diagnostic.VERSION:
        raise AssertionError(f"{fixture_id}: diagnostic contract mismatch")
    if payload.get("finalDecisionDefined") is not False:
        raise AssertionError(f"{fixture_id}: diagnostic unexpectedly defined a final decision")
    if "finalDecision" in payload or "classification" in payload:
        raise AssertionError(f"{fixture_id}: forbidden final verdict field present")
    _assert_finite_numbers(payload, fixture_id)

    support = payload["supportView"]
    raw_view = payload["rawView"]
    if support["positiveBinCount"] > raw_view["positiveBinCount"]:
        raise AssertionError(f"{fixture_id}: support created positive bins")

    summary = _summarize_diag(payload)
    return {
        "fixtureId": fixture_id,
        "selectedMidi": selected_midi,
        "referenceExpectedClassification": reference_expected,
        "referenceExpectedUsedForComputation": False,
        "onsetStatus": onset_status,
        "analysisRms": float(onset["analysisRms"]),
        "innovationEnergy": float(onset["innovationEnergy"]),
        "diagnosticAvailable": True,
        "finalDecisionDefined": False,
        "diagnostic": summary,
        "fullDiagnosticCanonical": _canonical(payload),
    }


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("contract") != EXPECTED_FIXTURE_CONTRACT:
        raise AssertionError("fixture contract mismatch")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 23:
        raise AssertionError("expected exactly 23 frozen V6 fixtures")

    if diagnostic.CONTRACT != "songsterr-fresh-v7-dual-view-representation-diagnostic-v1":
        raise AssertionError("diagnostic contract changed")
    if diagnostic.VERSION != 1:
        raise AssertionError("diagnostic version changed")

    frequencies = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))
    if not np.allclose(frequencies, base.expected_frequencies(), rtol=0.0, atol=1e-12):
        raise AssertionError("frozen frequency grid mismatch")

    repetitions: list[list[dict[str, Any]]] = []
    for _ in range(REPETITIONS):
        repetitions.append([_evaluate_fixture(fixture, frequencies) for fixture in fixtures])

    canonical_runs = [_canonical(rows) for rows in repetitions]
    deterministic = len(set(canonical_runs)) == 1
    if not deterministic:
        raise AssertionError("dual-view diagnostics were not deterministic")

    rows = repetitions[0]
    expected_ids = [str(fixture["id"]) for fixture in fixtures]
    observed_ids = [str(row["fixtureId"]) for row in rows]
    if observed_ids != expected_ids:
        raise AssertionError("fixture order changed")

    printable_rows: list[dict[str, Any]] = []
    for row in rows:
        printable = dict(row)
        printable.pop("fullDiagnosticCanonical", None)
        printable_rows.append(printable)

    available_rows = [row for row in rows if row["diagnosticAvailable"] is True]
    fit_available_rows = [
        row
        for row in available_rows
        if row["diagnostic"]["dualViewFitAvailable"] is True
    ]
    selected_template_available_rows = [
        row
        for row in available_rows
        if row["diagnostic"]["supportSelectedTemplateValid"] is True
    ]

    output = {
        "contract": "songsterr-fresh-v7-dual-view-diagnostic-synthetic-test-v1",
        "diagnosticContract": diagnostic.CONTRACT,
        "fixtureContract": manifest["contract"],
        "fixtureCount": len(rows),
        "repetitions": REPETITIONS,
        "deterministic": deterministic,
        "diagnosticAvailableCount": len(available_rows),
        "supportSelectedTemplateAvailableCount": len(selected_template_available_rows),
        "dualViewFitAvailableCount": len(fit_available_rows),
        "finalDecisionDefined": False,
        "referenceExpectedUsedForComputation": False,
        "realCorpusEvaluated": False,
        "modelInferenceInvoked": False,
        "basicPitchInvoked": False,
        "networkInvoked": False,
        "customerEligibleEvents": 0,
        "mayAdvanceDelivery": False,
        "mechanicalDiagnosticStatus": "COMPLETE",
        "rows": printable_rows,
    }
    print(json.dumps(output, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
