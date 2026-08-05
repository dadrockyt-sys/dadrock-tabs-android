from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-out-chorus-transition-ranking-v1.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-out-chorus-transition-conclusion-v1.json"
)


def main() -> None:
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    holdouts = data.get("holdoutReports") or []
    accuracies = [
        float((item.get("holdoutScore") or {}).get("pairwiseAccuracy") or 0.0)
        for item in holdouts
    ]

    report = {
        "schemaVersion": 1,
        "conclusionType": "out-chorus-transition-ranking-diagnostic",
        "source": str(INPUT_PATH.relative_to(REPO_ROOT)),
        "section": data.get("section"),
        "measureRange": data.get("measureRange"),
        "candidateCount": data.get("candidateCount"),
        "positiveCount": data.get("positiveCount"),
        "negativeCount": data.get("negativeCount"),
        "eligibleTwoMeasureHoldoutCount": data.get(
            "eligibleTwoMeasureHoldoutCount"
        ),
        "medianHoldoutAccuracy": data.get("medianHoldoutAccuracy"),
        "holdoutsAtOrAbove065": data.get("holdoutsAtOrAbove065"),
        "minimumHoldoutAccuracy": min(accuracies) if accuracies else None,
        "maximumHoldoutAccuracy": max(accuracies) if accuracies else None,
        "transitionRankingStable": data.get("transitionRankingStable"),
        "interpretation": (
            "The transition and ending-position feature family overfits the available "
            "Out-Chorus labels. Training accuracy reaches 1.0 while held-out accuracy "
            "varies sharply, including weak results. The feature family therefore does "
            "not define a transferable candidate-ranking boundary."
        ),
        "recommendedUse": (
            "Do not promote transition position, ending proximity, pulse affinity, or "
            "edge placement as a ranking model or rejection gate. Preserve them only as "
            "descriptive diagnostics. The next investigation should compare complete "
            "multi-event measure patterns and adjacent-measure sequences rather than "
            "scoring isolated candidates."
        ),
        "featureFamilyPromoted": False,
        "rankingPromoted": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Out-Chorus transition conclusion V1 complete")
    print("Eligible holdouts:", report["eligibleTwoMeasureHoldoutCount"])
    print("Median holdout accuracy:", report["medianHoldoutAccuracy"])
    print("Minimum holdout accuracy:", report["minimumHoldoutAccuracy"])
    print("Maximum holdout accuracy:", report["maximumHoldoutAccuracy"])
    print("Transition ranking stable:", report["transitionRankingStable"])
    print("Feature family promoted: False")
    print("Ranking promoted: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
