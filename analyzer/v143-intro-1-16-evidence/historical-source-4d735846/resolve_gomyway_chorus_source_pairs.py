from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
C1_PATH = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-populated.json"
C2A_PATH = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-populated.json"
C2B_PATH = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-populated.json"
OUT_C1 = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-source-resolved.json"
OUT_C2A = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-source-resolved.json"
OUT_C2B = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-source-resolved.json"
AUDIT = ROOT / "public" / "gomyway-chorus-source-resolution-audit.json"

SOURCE_EQUIVALENT_PAIRS = [(33, 63), (34, 64), (35, 65), (36, 66), (37, 67)]
SOURCE_INTENTIONAL_DIFFERENCE = (38, 68)


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def by_number(packet: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {int(item["measureNumber"]): item for item in packet.get("measures", [])}


def approve_measure(measure: dict[str, Any], note: str) -> None:
    for event in measure.get("events", []):
        event["humanValidated"] = True
        event["referenceConfidence"] = max(float(event.get("referenceConfidence", 0.0)), 0.95)
    measure["humanReview"] = {
        "status": "approved",
        "reviewedBy": "human-source-review",
        "reviewedAt": None,
        "notes": note,
    }


def main() -> None:
    c1 = load(C1_PATH)
    c2a = load(C2A_PATH)
    c2b = load(C2B_PATH)
    m1 = by_number(c1)
    m2a = by_number(c2a)
    m2b = by_number(c2b)

    resolved_pairs: list[dict[str, Any]] = []

    for left, right in SOURCE_EQUIVALENT_PAIRS:
        right_packet = m2a if right <= 64 else m2b
        if left not in m1 or right not in right_packet:
            raise RuntimeError(f"Missing source pair {left}/{right}")

        # Pages 3 and 5 show the same notated guitar part for these five pairs.
        # Use the Chorus 1 source-derived semantic form as the canonical event set,
        # preserving the Chorus 2 section metadata and measure number.
        right_packet[right]["events"] = deepcopy(m1[left]["events"])
        right_packet[right]["sectionVariant"] = m1[left].get("sectionVariant")

        approve_measure(
            m1[left],
            f"Approved against professional reference page 3; source-equivalent to measure {right} on page 5.",
        )
        approve_measure(
            right_packet[right],
            f"Approved against professional reference page 5; source-equivalent to measure {left} on page 3.",
        )
        resolved_pairs.append({
            "chorus1Measure": left,
            "chorus2Measure": right,
            "decision": "same-notated-part",
            "canonicalSource": left,
        })

    left, right = SOURCE_INTENTIONAL_DIFFERENCE
    if left not in m1 or right not in m2b:
        raise RuntimeError("Missing intentional-difference pair 38/68")

    approve_measure(
        m1[left],
        "Approved against professional reference page 3: A(add2) held figure closes Chorus 1.",
    )
    approve_measure(
        m2b[right],
        "Approved against professional reference page 5: empty/rest continuation closes Chorus 2 before Bridge.",
    )
    resolved_pairs.append({
        "chorus1Measure": left,
        "chorus2Measure": right,
        "decision": "intentionally-different",
        "chorus1Meaning": "A(add2) held figure",
        "chorus2Meaning": "empty/rest continuation",
    })

    c1["sourceResolvedMeasures"] = list(range(33, 39))
    c2a["sourceResolvedMeasures"] = [63, 64]
    c2b["sourceResolvedMeasures"] = [65, 66, 67, 68]
    for packet in (c1, c2a, c2b):
        packet["readyForTraining"] = False
        packet["trainingMayStartFromThisChunk"] = False
        packet["professionalReferenceUsedForScoringOnly"] = True

    OUT_C1.write_text(json.dumps(c1, indent=2) + "\n", encoding="utf-8")
    OUT_C2A.write_text(json.dumps(c2a, indent=2) + "\n", encoding="utf-8")
    OUT_C2B.write_text(json.dumps(c2b, indent=2) + "\n", encoding="utf-8")

    audit = {
        "sourcePages": [3, 5],
        "pairsReviewed": 6,
        "sourceEquivalentPairs": SOURCE_EQUIVALENT_PAIRS,
        "intentionalDifferencePair": list(SOURCE_INTENTIONAL_DIFFERENCE),
        "measuresApproved": [33, 34, 35, 36, 37, 38, 63, 64, 65, 66, 67, 68],
        "resolvedPairs": resolved_pairs,
        "automaticApprovalApplied": False,
        "humanSourceReviewApplied": True,
        "readyForTraining": False,
        "nextRequiredStage": "rebuild-full-review-with-source-resolved-chorus-chunks",
        "protectedBaselinesChanged": False,
    }
    AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print("Chorus source resolution complete")
    print("Pairs reviewed: 6")
    print("Source-equivalent pairs: 5")
    print("Intentional-difference pairs: 1")
    print("Measures approved: 12")
    print("Pair 38/68 intentionally different: True")
    print("Ready for training: False")
    print("Output Chorus 1:", OUT_C1.relative_to(ROOT))
    print("Output Chorus 2A:", OUT_C2A.relative_to(ROOT))
    print("Output Chorus 2B:", OUT_C2B.relative_to(ROOT))
    print("Audit:", AUDIT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
