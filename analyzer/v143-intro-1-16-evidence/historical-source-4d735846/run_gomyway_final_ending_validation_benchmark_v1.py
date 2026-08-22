from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"

DETAIL_PATH = PUBLIC_DIR / "gomyway-final-ending-event-detail-audit-v1.json"
ADJUDICATION_PATH = PUBLIC_DIR / "gomyway-final-ending-listening-adjudication-v1.json"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-final-ending-validation-benchmark-v1.json"

EXPECTED_PENDING = {111, 112}
EXPECTED_PROTECTED = 113


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required input: {path.relative_to(REPO_ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    detail = load(DETAIL_PATH)
    adjudication = load(ADJUDICATION_PATH)

    detail_pending = {
        int(value)
        for value in detail.get("pendingHumanReviewMeasures") or []
    }
    detail_approved = {
        int(value)
        for value in detail.get("approvedMeasures") or []
    }

    judgments = adjudication.get("judgments") or []
    reviewed = {
        int(item["measureNumber"])
        for item in judgments
        if isinstance(item, dict) and item.get("measureNumber") is not None
    }

    validated_sustains = {
        int(item["measureNumber"])
        for item in judgments
        if isinstance(item, dict)
        and item.get("measureNumber") is not None
        and item.get("isRhythmGuitar") is True
        and item.get("isFullMeasureSustain") is True
        and item.get("tieForwardSupported") is True
        and item.get("humanValidated") is True
    }

    exact_pending_match = detail_pending == EXPECTED_PENDING
    exact_review_match = reviewed == EXPECTED_PENDING
    all_pending_validated = validated_sustains == EXPECTED_PENDING
    protected_measure_preserved = (
        EXPECTED_PROTECTED in detail_approved
        and adjudication.get("protectedApprovedMeasure") == EXPECTED_PROTECTED
    )
    three_measure_ending_validated = (
        exact_pending_match
        and exact_review_match
        and all_pending_validated
        and protected_measure_preserved
    )

    passed = three_measure_ending_validated

    report = {
        "schemaVersion": 1,
        "benchmarkType": "final-ending-human-validation",
        "measureRange": [111, 113],
        "passed": passed,
        "pendingMeasuresFromDetailAudit": sorted(detail_pending),
        "reviewedMeasures": sorted(reviewed),
        "validatedFullMeasureSustainMeasures": sorted(validated_sustains),
        "protectedApprovedMeasure": EXPECTED_PROTECTED,
        "exactPendingMeasureMatch": exact_pending_match,
        "exactReviewedMeasureMatch": exact_review_match,
        "allPendingMeasuresHumanValidated": all_pending_validated,
        "protectedMeasurePreserved": protected_measure_preserved,
        "completeFinalEndingValidationSupported": three_measure_ending_validated,
        "automaticEventMutationAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Final-ending validation benchmark V1 complete")
    print("Passed:", report["passed"])
    print("Pending measures:", report["pendingMeasuresFromDetailAudit"])
    print("Reviewed measures:", report["reviewedMeasures"])
    print("Validated full-measure sustains:", report["validatedFullMeasureSustainMeasures"])
    print("Protected approved measure:", report["protectedApprovedMeasure"])
    print("Exact pending-measure match:", report["exactPendingMeasureMatch"])
    print("Exact reviewed-measure match:", report["exactReviewedMeasureMatch"])
    print("All pending measures human validated:", report["allPendingMeasuresHumanValidated"])
    print("Protected measure preserved:", report["protectedMeasurePreserved"])
    print("Complete final-ending validation supported:", report["completeFinalEndingValidationSupported"])
    print("Automatic event mutation allowed: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
