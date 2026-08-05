from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"

RECONCILIATION_PATH = PUBLIC_DIR / "gomyway-full-song-review-evidence-reconciliation-v1.json"
INTRO_AUDIT_PATH = PUBLIC_DIR / "gomyway-intro-review-evidence-audit-v1.json"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-full-song-review-evidence-merge-v1.json"

EXPECTED_START = 1
EXPECTED_END = 113


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path.relative_to(REPO_ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def as_measure_set(value: Any) -> set[int]:
    result: set[int] = set()
    if not isinstance(value, list):
        return result
    for item in value:
        try:
            number = int(item)
        except (TypeError, ValueError):
            continue
        if EXPECTED_START <= number <= EXPECTED_END:
            result.add(number)
    return result


def main() -> None:
    reconciliation = load(RECONCILIATION_PATH)
    intro = load(INTRO_AUDIT_PATH)

    expected = set(range(EXPECTED_START, EXPECTED_END + 1))

    reconciliation_reviewed = expected - as_measure_set(
        reconciliation.get("missingReviewEvidenceMeasures")
    )
    reconciliation_resolved = expected - as_measure_set(
        reconciliation.get("missingResolutionEvidenceMeasures")
    )

    intro_reviewed = as_measure_set(intro.get("reviewedMeasures"))
    intro_resolved = as_measure_set(intro.get("resolvedMeasures"))

    merged_reviewed = reconciliation_reviewed | intro_reviewed
    merged_resolved = reconciliation_resolved | intro_resolved

    missing_review = sorted(expected - merged_reviewed)
    missing_resolution = sorted(expected - merged_resolved)

    intro_complete = bool(
        intro.get("allIntroMeasuresHaveReviewEvidence")
        and intro.get("allIntroMeasuresHaveResolutionEvidence")
        and intro.get("readyToMergeIntoFullSongReconciliation")
    )
    downstream_complete = (
        all(measure in reconciliation_reviewed for measure in range(17, EXPECTED_END + 1))
        and all(measure in reconciliation_resolved for measure in range(17, EXPECTED_END + 1))
    )

    passed = (
        intro_complete
        and downstream_complete
        and not missing_review
        and not missing_resolution
    )

    report = {
        "schemaVersion": 1,
        "auditType": "full-song-review-evidence-merge",
        "measureRange": [EXPECTED_START, EXPECTED_END],
        "reconciliationArtifact": str(RECONCILIATION_PATH.relative_to(REPO_ROOT)),
        "introArtifact": str(INTRO_AUDIT_PATH.relative_to(REPO_ROOT)),
        "introComplete": intro_complete,
        "measures17Through113Complete": downstream_complete,
        "mergedReviewedMeasureCount": len(merged_reviewed),
        "mergedResolvedMeasureCount": len(merged_resolved),
        "missingReviewEvidenceMeasures": missing_review,
        "missingResolutionEvidenceMeasures": missing_resolution,
        "allMeasuresHaveReviewEvidence": not missing_review,
        "allMeasuresHaveResolutionEvidence": not missing_resolution,
        "passed": passed,
        "readyToRepairCompletionAudit": passed,
        "readyForProtectedPdfComparison": passed,
        "interpretation": (
            "Measures 17-113 are covered by the distributed section-review reconciliation. "
            "Measures 1-16 are covered by the dedicated locked-intro evidence audit. "
            "The merged result is the authoritative read-only completion gate for full-song rhythm review."
        ),
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Full-song review-evidence merge V1 complete")
    print("Passed:", report["passed"])
    print("Intro complete:", report["introComplete"])
    print("Measures 17-113 complete:", report["measures17Through113Complete"])
    print("Merged reviewed measures:", report["mergedReviewedMeasureCount"])
    print("Merged resolved measures:", report["mergedResolvedMeasureCount"])
    print("Missing review evidence measures:", report["missingReviewEvidenceMeasures"])
    print("Missing resolution evidence measures:", report["missingResolutionEvidenceMeasures"])
    print("Ready to repair completion audit:", report["readyToRepairCompletionAudit"])
    print("Ready for protected PDF comparison:", report["readyForProtectedPdfComparison"])
    print()
    print("Automatic promotion allowed: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
