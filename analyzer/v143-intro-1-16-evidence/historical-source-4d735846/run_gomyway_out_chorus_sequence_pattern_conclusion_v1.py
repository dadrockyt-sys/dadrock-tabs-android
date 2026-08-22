from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-out-chorus-sequence-pattern-benchmark-v1.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-out-chorus-sequence-pattern-conclusion-v1.json"
)


def main() -> None:
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    holdouts = (
        data.get("leaveOneSequenceOutReports")
        or data.get("holdoutReports")
        or data.get("holdouts")
        or []
    )

    correct_count = sum(
        1
        for item in holdouts
        if bool(item.get("correct"))
    )
    holdout_count = len(holdouts)

    report = {
        "schemaVersion": 1,
        "conclusionType": "out-chorus-sequence-pattern-diagnostic",
        "source": str(INPUT_PATH.relative_to(REPO_ROOT)),
        "measureCount": len(data.get("measurePatterns") or []),
        "adjacentSequenceCount": len(data.get("adjacentSequences") or []),
        "holdoutCount": holdout_count,
        "correctHoldoutCount": correct_count,
        "holdoutAccuracy": data.get("holdoutAccuracy"),
        "medianNearestSimilarity": data.get("medianNearestSimilarity"),
        "sequencePatternStable": data.get("sequencePatternStable"),
        "interpretation": (
            "Adjacent two-measure similarity is high in several cases, but the nearest "
            "sequence usually does not preserve the professionally validated rhythm role. "
            "Only two of seven holdouts were classified correctly, so raw sequence shape "
            "is not a reliable transferable signal for this Out-Chorus."
        ),
        "recommendedUse": (
            "Do not promote whole-measure or adjacent-sequence similarity as a ranking "
            "model, automatic correction rule, or rejection gate. Treat measures 103-110 "
            "as a section-specific ending passage and proceed with direct professional-reference "
            "coverage and unresolved-event auditing instead of further fitting on seven sequences."
        ),
        "patternFamilyPromoted": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Out-Chorus sequence-pattern conclusion V1 complete")
    print("Measures:", report["measureCount"])
    print("Adjacent sequences:", report["adjacentSequenceCount"])
    print("Holdouts:", report["holdoutCount"])
    print("Correct holdouts:", report["correctHoldoutCount"])
    print("Holdout accuracy:", report["holdoutAccuracy"])
    print("Median nearest similarity:", report["medianNearestSimilarity"])
    print("Sequence pattern stable:", report["sequencePatternStable"])
    print("Pattern family promoted: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
