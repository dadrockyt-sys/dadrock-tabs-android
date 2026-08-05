from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-out-chorus-reference-coverage-audit-v1.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-out-chorus-unresolved-review-pack-v1.json"
)


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing input: {path.relative_to(REPO_ROOT)}"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def confidence_band(event: dict[str, Any]) -> str:
    components = event.get("softComponents") or {}
    values = [
        float(value)
        for value in components.values()
        if isinstance(value, (int, float))
    ]
    strongest = max(values) if values else 0.0

    if strongest >= 0.75:
        return "strong-diagnostic-evidence"
    if strongest >= 0.40:
        return "moderate-diagnostic-evidence"
    return "weak-diagnostic-evidence"


def main() -> None:
    audit = load(INPUT_PATH)
    unresolved = audit.get("unresolvedEvents") or []

    review_items = []
    for event in unresolved:
        components = event.get("softComponents") or {}
        ranked_components = sorted(
            (
                {
                    "name": name,
                    "value": round(float(value), 6),
                }
                for name, value in components.items()
                if isinstance(value, (int, float))
            ),
            key=lambda item: (-item["value"], item["name"]),
        )

        review_items.append({
            "measureNumber": int(event["measureNumber"]),
            "candidateStep": int(event["candidateStep"]),
            "classification": event.get("classification"),
            "referenceDistance": event.get("referenceDistance"),
            "rankingScore": event.get("score"),
            "confidenceBand": confidence_band(event),
            "strongestComponents": ranked_components[:3],
            "allSoftComponents": components,
            "reviewStatus": "requires-direct-review",
            "automaticDecisionAllowed": False,
            "recommendedReview": (
                "Compare the exact candidate onset against the isolated rhythm stem, "
                "the full mix, and the professional reference for this measure. "
                "Confirm whether it is a real rhythm-guitar articulation, a carried note, "
                "a percussion/transient leak, or an unsupported duplicate."
            ),
        })

    review_items.sort(
        key=lambda item: (
            item["measureNumber"],
            item["candidateStep"],
        )
    )

    report = {
        "schemaVersion": 1,
        "reviewPackType": "out-chorus-unresolved-candidate-review",
        "source": str(INPUT_PATH.relative_to(REPO_ROOT)),
        "section": audit.get("section"),
        "measureRange": audit.get("measureRange"),
        "coverageFraction": audit.get("coverageFraction"),
        "coveredCandidateCount": audit.get("coveredCandidateCount"),
        "unresolvedCandidateCount": len(review_items),
        "unresolvedKeys": [
            [item["measureNumber"], item["candidateStep"]]
            for item in review_items
        ],
        "reviewItems": review_items,
        "reviewOrder": (
            "Review measure 103 steps 2 and 3 first, then measure 104 step 9, "
            "measure 105 step 15, and measure 109 step 15."
        ),
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Out-Chorus unresolved review pack V1 complete")
    print("Coverage fraction:", report["coverageFraction"])
    print("Covered candidates:", report["coveredCandidateCount"])
    print("Unresolved candidates:", report["unresolvedCandidateCount"])
    print("Unresolved keys:", report["unresolvedKeys"])
    print()

    for item in review_items:
        print(
            f"measure {item['measureNumber']} "
            f"step {item['candidateStep']} "
            f"classification={item['classification']} "
            f"referenceDistance={item['referenceDistance']} "
            f"score={item['rankingScore']} "
            f"band={item['confidenceBand']}"
        )
        print("  strongestComponents:", item["strongestComponents"])

    print()
    print("Automatic promotion allowed: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
