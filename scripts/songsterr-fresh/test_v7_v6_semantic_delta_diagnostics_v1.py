#!/usr/bin/env python3
"""First-run synthetic-only test for frozen-V6 semantic-delta diagnostics V1.

The frozen expected classifications are carried as reference metadata only.
They never influence diagnostic computation, branching, exit status, or any
new verdict. This test defines no successor classifier.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as v6
import physical_template_plausibility_v3 as v3_base
import v7_v6_semantic_delta_diagnostics_v1 as diagnostic

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "v6_onset_birth_synthetic_fixtures.json"
REPETITIONS = 3
EXPECTED_FIXTURE_CONTRACT = "songsterr-fresh-v6-onset-birth-synthetic-fixtures-v1"


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _assert_finite_numbers(value: Any, path: str = "root") -> None:
    if value is None or isinstance(value, (str, bool, int)):
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


def _support_necessity(dual_payload: dict[str, Any]) -> float | None:
    support = dual_payload.get("supportView")
    if not isinstance(support, dict):
        return None
    composite = support.get("frozenComposite")
    if not isinstance(composite, dict):
        return None
    iteration2 = composite.get("iteration2Composite")
    if not isinstance(iteration2, dict):
        return None
    base = iteration2.get("baseComposite")
    if not isinstance(base, dict):
        return None
    value = base.get("necessityFraction")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _summarize(payload: dict[str, Any]) -> dict[str, Any]:
    historical = payload.get("frozenV6HistoricalComponent")
    historical = historical if isinstance(historical, dict) else {}
    fit = payload.get("frozenV6FitComponent")
    fit = fit if isinstance(fit, dict) else {}
    raw_template = payload.get("frozenV6SelectedRawTemplate")
    raw_template = raw_template if isinstance(raw_template, dict) else {}
    dual_payload = payload.get("dualViewDiagnostic")
    dual_payload = dual_payload if isinstance(dual_payload, dict) else {}
    support = dual_payload.get("supportView")
    support = support if isinstance(support, dict) else {}
    support_template = support.get("selectedTemplate")
    support_template = support_template if isinstance(support_template, dict) else {}
    support_composite = support.get("frozenComposite")
    support_composite = support_composite if isinstance(support_composite, dict) else {}
    evidence = support.get("candidateEvidence")
    evidence = evidence if isinstance(evidence, dict) else {}
    owners = support.get("ownerDiagnostics")
    owners = owners if isinstance(owners, dict) else {}
    dual_fit = dual_payload.get("dualViewFit")
    dual_fit = dual_fit if isinstance(dual_fit, dict) else {}

    return {
        "onsetAvailable": payload.get("onsetAvailable") is True,
        "onsetStatus": payload.get("onsetStatus"),
        "analysisRms": payload.get("analysisRms"),
        "innovationEnergy": payload.get("innovationEnergy"),
        "frozenV6HistoricalClassification": historical.get("classification"),
        "frozenV6HistoricalReason": historical.get("reason"),
        "frozenV6FitStatus": fit.get("status"),
        "frozenV6FitPassed": fit.get("passed") is True,
        "frozenV6ValidCandidateCount": fit.get("validCandidateCount"),
        "frozenV6FeatureEnergy": fit.get("featureEnergy"),
        "frozenV6SelectedCoefficient": fit.get("selectedCoefficient"),
        "frozenV6NecessityFraction": fit.get("necessityFraction"),
        "frozenV6FitFundamentalRatio": fit.get("fundamentalToMaxHarmonicInnovationRatio"),
        "frozenV6RawTemplateValid": raw_template.get("valid") is True,
        "frozenV6RawTemplateReason": raw_template.get("reason"),
        "frozenV6RawTemplateFundamentalBin": raw_template.get("fundamentalBin"),
        "frozenV6RawTemplateFundamentalHz": raw_template.get("fundamentalHz"),
        "frozenV6RawTemplateBins": raw_template.get("bins"),
        "frozenV6RawTemplateObservedHarmonics": raw_template.get("observedHarmonicInnovation"),
        "frozenV6RawTemplateFundamentalRatio": raw_template.get(
            "fundamentalToMaxHarmonicInnovationRatio"
        ),
        "supportSelectedTemplateValid": support_template.get("valid") is True,
        "supportSelectedTemplateStatus": support_template.get("status"),
        "supportSelectedCents": support_template.get("cents"),
        "supportSupportedHarmonicCount": support_template.get("supportedHarmonicCount"),
        "supportWeightedHarmonicCoverage": support_template.get("weightedHarmonicCoverage"),
        "supportValidCandidateCount": support.get("validCandidateCount"),
        "supportFrozenCompositePassed": support_composite.get("passed") is True,
        "supportFrozenCompositeStatus": support_composite.get("status"),
        "supportFrozenNecessityFraction": _support_necessity(dual_payload),
        "supportCandidateEvidenceAvailable": evidence.get("available") is True,
        "supportCandidateEvidenceFraction": evidence.get("candidateEvidenceFraction"),
        "supportCredibleOwnerMidis": [
            int(row["ownerMidi"])
            for row in owners.get("credibleOwnerRows", [])
            if isinstance(row, dict) and isinstance(row.get("ownerMidi"), int)
        ],
        "supportVetoOwnerMidis": [
            int(row["ownerMidi"])
            for row in owners.get("vetoOwnerRows", [])
            if isinstance(row, dict) and isinstance(row.get("ownerMidi"), int)
        ],
        "dualViewFitAvailable": dual_fit.get("available") is True,
        "dualViewFitStatus": dual_fit.get("availabilityStatus"),
        "dualViewRawFeatureEnergy": dual_fit.get("rawFeatureEnergy"),
        "dualViewSelectedCoefficient": dual_fit.get("selectedCoefficient"),
        "dualViewRawNecessityFraction": dual_fit.get("rawNecessityFraction"),
        "historicalV6FundamentalRatioThresholdReferenceOnly": payload.get(
            "historicalV6FundamentalRatioThresholdReferenceOnly"
        ),
        "historicalV6NecessityThresholdReferenceOnly": payload.get(
            "historicalV6NecessityThresholdReferenceOnly"
        ),
    }


def _evaluate_fixture(fixture: dict[str, Any], frequencies: np.ndarray) -> dict[str, Any]:
    fixture_id = str(fixture["id"])
    selected_midi = int(fixture["selectedMidi"])
    reference_expected = str(fixture["expectedClassification"])
    audio = v6._fixture_audio(fixture)
    onset_sample = int(round(float(fixture["onsetSeconds"]) * v6.SAMPLE_RATE))

    payload = diagnostic.evaluate_semantic_delta(
        audio,
        onset_sample,
        selected_midi,
        frequencies,
    )
    if payload.get("contract") != diagnostic.CONTRACT or payload.get("version") != diagnostic.VERSION:
        raise AssertionError(f"{fixture_id}: diagnostic contract mismatch")
    if payload.get("finalDecisionDefined") is not False:
        raise AssertionError(f"{fixture_id}: diagnostic unexpectedly defined a final decision")
    if "finalDecision" in payload or "successorClassification" in payload:
        raise AssertionError(f"{fixture_id}: forbidden successor verdict field present")
    _assert_finite_numbers(payload, fixture_id)

    return {
        "fixtureId": fixture_id,
        "selectedMidi": selected_midi,
        "referenceExpectedClassification": reference_expected,
        "referenceExpectedUsedForComputation": False,
        "finalDecisionDefined": False,
        "diagnostic": _summarize(payload),
        "fullDiagnosticCanonical": _canonical(payload),
    }


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("contract") != EXPECTED_FIXTURE_CONTRACT:
        raise AssertionError("fixture contract mismatch")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 23:
        raise AssertionError("expected exactly 23 frozen V6 fixtures")

    if diagnostic.CONTRACT != "songsterr-fresh-v7-v6-semantic-delta-diagnostic-v1":
        raise AssertionError("diagnostic contract changed")
    if diagnostic.VERSION != 1:
        raise AssertionError("diagnostic version changed")

    frequencies = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))
    if not np.allclose(frequencies, v3_base.expected_frequencies(), rtol=0.0, atol=1e-12):
        raise AssertionError("V6/V3 frequency grid mismatch")

    repetitions: list[list[dict[str, Any]]] = []
    for _ in range(REPETITIONS):
        repetitions.append([_evaluate_fixture(fixture, frequencies) for fixture in fixtures])

    canonical_runs = [_canonical(rows) for rows in repetitions]
    deterministic = len(set(canonical_runs)) == 1
    if not deterministic:
        raise AssertionError("semantic-delta diagnostics were not deterministic")

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

    onset_ok_count = sum(
        1 for row in rows if row["diagnostic"].get("onsetStatus") == "OK"
    )
    raw_template_valid_count = sum(
        1 for row in rows if row["diagnostic"].get("frozenV6RawTemplateValid") is True
    )
    support_template_valid_count = sum(
        1 for row in rows if row["diagnostic"].get("supportSelectedTemplateValid") is True
    )
    dual_fit_available_count = sum(
        1 for row in rows if row["diagnostic"].get("dualViewFitAvailable") is True
    )

    output = {
        "contract": "songsterr-fresh-v7-v6-semantic-delta-synthetic-test-v1",
        "diagnosticContract": diagnostic.CONTRACT,
        "fixtureContract": manifest["contract"],
        "fixtureCount": len(rows),
        "repetitions": REPETITIONS,
        "deterministic": deterministic,
        "onsetOkCount": onset_ok_count,
        "frozenV6RawTemplateValidCount": raw_template_valid_count,
        "supportTemplateValidCount": support_template_valid_count,
        "dualViewFitAvailableCount": dual_fit_available_count,
        "finalDecisionDefined": False,
        "referenceExpectedUsedForComputation": False,
        "historicalV6ThresholdAdoptedAsSuccessorRule": False,
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
