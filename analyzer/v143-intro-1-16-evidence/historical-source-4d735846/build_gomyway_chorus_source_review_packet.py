from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "public" / "gomyway-chorus1-chorus2-musical-consensus.json"
CHORUS1 = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-populated.json"
CHORUS2A = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-populated.json"
CHORUS2B = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-populated.json"
OUTPUT = ROOT / "public" / "gomyway-chorus-source-review-packet.json"
TEXT = ROOT / "public" / "gomyway-chorus-source-review-packet.txt"

PAIRS = [(33, 63), (34, 64), (35, 65), (36, 66), (37, 67), (38, 68)]


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def compact_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "step": int(event.get("quantizedStep", -1)),
        "duration": int(event.get("durationSteps", -1)),
        "notes": [
            {
                "string": int(note.get("string", -99)),
                "fret": int(note.get("fret", -99)),
            }
            for note in event.get("notes", [])
        ],
        "techniques": list(event.get("techniques", [])),
        "confidence": float(event.get("referenceConfidence", 0.0)),
    }


def main() -> None:
    consensus = load(CONSENSUS)
    packets = [load(CHORUS1), load(CHORUS2A), load(CHORUS2B)]
    measures: dict[int, dict[str, Any]] = {}
    for packet in packets:
        for measure in packet.get("measures", []):
            number = int(measure["measureNumber"])
            measures[number] = measure

    missing = [number for pair in PAIRS for number in pair if number not in measures]
    if missing:
        raise RuntimeError(f"Missing chorus measures: {sorted(set(missing))}")

    comparisons_by_pair = {
        (int(item["chorus1Measure"]), int(item["chorus2Measure"])): item
        for item in consensus.get("comparisons", [])
    }

    review_pairs: list[dict[str, Any]] = []
    for chorus1_measure, chorus2_measure in PAIRS:
        comparison = comparisons_by_pair.get((chorus1_measure, chorus2_measure), {})
        review_pairs.append({
            "chorus1Measure": chorus1_measure,
            "chorus2Measure": chorus2_measure,
            "chorus1SourcePage": 3,
            "chorus2SourcePage": 5,
            "chorus1Events": [compact_event(event) for event in measures[chorus1_measure].get("events", [])],
            "chorus2Events": [compact_event(event) for event in measures[chorus2_measure].get("events", [])],
            "musicalMismatchCount": int(comparison.get("musicalMismatchCount", comparison.get("mismatchCount", 0))),
            "mismatchCategories": comparison.get("mismatchCategories", []),
            "reviewQuestions": [
                "Does the professional source show the same rhythm in both choruses?",
                "Are different voicings intentional or a draft transcription error?",
                "Are missing attacks/rests intentional in one chorus?",
                "Do techniques differ in the source, or only in the draft?",
            ],
            "decision": None,
            "correctedChorus1Events": None,
            "correctedChorus2Events": None,
            "reviewNotes": "",
        })

    result = {
        "schemaVersion": 1,
        "reviewType": "source-grounded-chorus-pair-review",
        "professionalReferencePages": [3, 5],
        "pairCount": len(review_pairs),
        "musicalExactMatchPairs": int(consensus.get("musicalExactMatchPairs", 0)),
        "musicalNonMatchingPairs": int(consensus.get("musicalNonMatchingPairs", len(review_pairs))),
        "totalMusicalEventMismatches": int(consensus.get("totalMusicalEventMismatches", 0)),
        "totalConfidenceDifferences": int(consensus.get("totalConfidenceDifferences", 0)),
        "policy": {
            "doNotForceChorusesToMatch": True,
            "sourceNotationOutranksRepeatedSectionAssumption": True,
            "confidenceIsNotMusicalContent": True,
            "automaticApprovalApplied": False,
        },
        "pairs": review_pairs,
        "readyForTraining": False,
        "nextRequiredStage": "review-each-pair-against-professional-pages-3-and-5-and-enter-corrections",
        "protectedBaselinesChanged": False,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "GOMYWAY CHORUS SOURCE REVIEW PACKET",
        "Professional reference pages: 3 and 5",
        f"Pairs: {len(review_pairs)}",
        f"Musical exact-match pairs: {result['musicalExactMatchPairs']}",
        f"Musical non-matching pairs: {result['musicalNonMatchingPairs']}",
        f"Total musical event mismatches: {result['totalMusicalEventMismatches']}",
        f"Confidence-only differences: {result['totalConfidenceDifferences']}",
        "Do not force choruses to match: True",
        "Automatic approval applied: False",
        "Ready for training: False",
        "Protected baselines changed: False",
        "",
    ]
    for item in review_pairs:
        lines.append(
            f"PAIR {item['chorus1Measure']} vs {item['chorus2Measure']} "
            f"mismatches={item['musicalMismatchCount']}"
        )
        lines.append(f"  Chorus 1 page 3 events: {item['chorus1Events']}")
        lines.append(f"  Chorus 2 page 5 events: {item['chorus2Events']}")
        lines.append("  Decision: [ ] same [ ] intentionally different [ ] correct chorus 1 [ ] correct chorus 2 [ ] correct both")
        lines.append("  Notes:")
        lines.append("")
    TEXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Chorus source review packet complete")
    print(f"Pairs prepared: {len(review_pairs)}")
    print(f"Musical exact-match pairs: {result['musicalExactMatchPairs']}")
    print(f"Musical non-matching pairs: {result['musicalNonMatchingPairs']}")
    print(f"Total musical event mismatches: {result['totalMusicalEventMismatches']}")
    print(f"Confidence-only differences: {result['totalConfidenceDifferences']}")
    print("Do not force choruses to match: True")
    print("Automatic approval applied: False")
    print("Ready for training: False")
    print(f"JSON: {OUTPUT.relative_to(ROOT)}")
    print(f"Text: {TEXT.relative_to(ROOT)}")
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
