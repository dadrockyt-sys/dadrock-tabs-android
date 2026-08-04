from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = REPO_ROOT / "public" / "gomyway-chorus2-prototype-refinement-v1.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-chorus2-prototype-refinement-conclusion-v1.json"


def main() -> None:
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))

    report = {
        "schemaVersion": 1,
        "conclusionType": "chorus2-prototype-refinement-diagnostic",
        "source": str(INPUT_PATH.relative_to(REPO_ROOT)),
        "prototypeSection": data.get("prototypeSection"),
        "refinementSection": data.get("refinementSection"),
        "chorus1BaselineAccuracy": data.get("chorus1BaselineScore", {}).get("pairwiseAccuracy"),
        "chorus2PrototypeOnlyAccuracy": data.get("chorus2PrototypeOnlyScore", {}).get("pairwiseAccuracy"),
        "chorus1Preserved": data.get("chorus1Preserved"),
        "chorus2Improved": data.get("chorus2Improved"),
        "refinementFeasible": data.get("refinementFeasible"),
        "bestRefinement": data.get("bestRefinement"),
        "interpretation": (
            "The Chorus 1 prototype already ranks Chorus 2 candidates at 0.875 pairwise accuracy. "
            "All Chorus 1-safe refinements produced zero Chorus 2 gain, so a separate additive Chorus 2 "
            "refinement is not supported by this evidence."
        ),
        "recommendedUse": (
            "Retain the Chorus 1 prototype as read-only soft evidence for Chorus 1 and Chorus 2. "
            "Do not add a Chorus 2-specific refinement and do not use the ranking as a hard rejection gate."
        ),
        "refinementPromoted": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Chorus 2 prototype refinement conclusion V1 complete")
    print("Chorus 1 baseline accuracy:", report["chorus1BaselineAccuracy"])
    print("Chorus 2 prototype-only accuracy:", report["chorus2PrototypeOnlyAccuracy"])
    print("Chorus 1 preserved:", report["chorus1Preserved"])
    print("Chorus 2 improved:", report["chorus2Improved"])
    print("Refinement feasible:", report["refinementFeasible"])
    print("Refinement promoted: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
