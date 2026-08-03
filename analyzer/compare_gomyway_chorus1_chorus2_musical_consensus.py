from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHORUS1 = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-populated.json"
CHORUS2A = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-populated.json"
CHORUS2B = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-populated.json"
OUTPUT = ROOT / "public" / "gomyway-chorus1-chorus2-musical-consensus.json"
TEXT = ROOT / "public" / "gomyway-chorus1-chorus2-musical-consensus.txt"

PAIRS = [(33, 63), (34, 64), (35, 65), (36, 66), (37, 67), (38, 68)]


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def musical_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "step": int(event.get("quantizedStep", -1)),
        "duration": int(event.get("durationSteps", -1)),
        "notes": sorted(
            [
                {
                    "string": int(note.get("string", -99)),
                    "fret": int(note.get("fret", -99)),
                }
                for note in event.get("notes", [])
            ],
            key=lambda item: (item["string"], item["fret"]),
        ),
        "techniques": sorted(str(item) for item in event.get("techniques", [])),
    }


def confidence(event: dict[str, Any] | None) -> float | None:
    if event is None:
        return None
    return float(event.get("referenceConfidence", 0.0))


def classify(left: dict[str, Any] | None, right: dict[str, Any] | None) -> list[str]:
    if left is None or right is None:
        return ["missing-event"]
    categories: list[str] = []
    if left["step"] != right["step"]:
        categories.append("timing-step")
    if left["duration"] != right["duration"]:
        categories.append("duration")
    if left["notes"] != right["notes"]:
        categories.append("notes-or-voicing")
    if left["techniques"] != right["techniques"]:
        categories.append("techniques")
    return categories


def main() -> None:
    packets = [load(CHORUS1), load(CHORUS2A), load(CHORUS2B)]
    measures: dict[int, dict[str, Any]] = {}
    for packet in packets:
        for measure in packet.get("measures", []):
            measures[int(measure["measureNumber"])] = measure

    missing = sorted({number for pair in PAIRS for number in pair if number not in measures})
    if missing:
        raise RuntimeError(f"Missing chorus measures: {missing}")

    comparisons: list[dict[str, Any]] = []
    musical_match_pairs = 0
    category_counts: dict[str, int] = {}
    total_musical_mismatches = 0
    total_confidence_differences = 0

    for c1, c2 in PAIRS:
        raw_left = measures[c1].get("events", [])
        raw_right = measures[c2].get("events", [])
        left = [musical_event(event) for event in raw_left]
        right = [musical_event(event) for event in raw_right]
        max_len = max(len(left), len(right))
        rows: list[dict[str, Any]] = []
        pair_mismatches = 0
        pair_confidence_differences = 0

        for index in range(max_len):
            l = left[index] if index < len(left) else None
            r = right[index] if index < len(right) else None
            l_raw = raw_left[index] if index < len(raw_left) else None
            r_raw = raw_right[index] if index < len(raw_right) else None
            categories = classify(l, r)
            musical_match = not categories
            if not musical_match:
                pair_mismatches += 1
                total_musical_mismatches += 1
                for category in categories:
                    category_counts[category] = category_counts.get(category, 0) + 1
            left_conf = confidence(l_raw)
            right_conf = confidence(r_raw)
            confidence_differs = left_conf != right_conf
            if confidence_differs:
                pair_confidence_differences += 1
                total_confidence_differences += 1
            rows.append({
                "index": index,
                "chorus1": l,
                "chorus2": r,
                "musicalMatch": musical_match,
                "mismatchCategories": categories,
                "chorus1Confidence": left_conf,
                "chorus2Confidence": right_conf,
                "confidenceDiffers": confidence_differs,
            })

        pair_exact = pair_mismatches == 0
        if pair_exact:
            musical_match_pairs += 1
        comparisons.append({
            "chorus1Measure": c1,
            "chorus2Measure": c2,
            "musicalExactMatch": pair_exact,
            "musicalMismatchCount": pair_mismatches,
            "confidenceDifferenceCount": pair_confidence_differences,
            "eventRows": rows,
            "humanDecision": None,
            "reviewNotes": "",
        })

    result = {
        "schemaVersion": 1,
        "comparison": "Chorus 1 measures 33-38 vs Chorus 2 measures 63-68",
        "comparisonRule": "musical events compared without referenceConfidence",
        "pairsCompared": len(PAIRS),
        "musicalExactMatchPairs": musical_match_pairs,
        "musicalNonMatchingPairs": len(PAIRS) - musical_match_pairs,
        "totalMusicalEventMismatches": total_musical_mismatches,
        "totalConfidenceDifferences": total_confidence_differences,
        "mismatchCategoryCounts": category_counts,
        "comparisons": comparisons,
        "automaticApprovalApplied": False,
        "readyForTraining": False,
        "nextRequiredStage": "review-only-genuine-musical-differences",
        "protectedBaselinesChanged": False,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "GOMYWAY CHORUS 1 / CHORUS 2 MUSICAL CONSENSUS",
        "Comparison ignores referenceConfidence and compares only timing, duration, notes, and techniques.",
        f"Pairs compared: {len(PAIRS)}",
        f"Musical exact-match pairs: {musical_match_pairs}",
        f"Musical non-matching pairs: {len(PAIRS) - musical_match_pairs}",
        f"Total musical event mismatches: {total_musical_mismatches}",
        f"Total confidence differences: {total_confidence_differences}",
        f"Mismatch categories: {category_counts}",
        "Automatic approval applied: False",
        "Ready for training: False",
        "Protected baselines changed: False",
        "",
    ]
    for item in comparisons:
        lines.append(
            f"PAIR {item['chorus1Measure']} vs {item['chorus2Measure']}: "
            f"musicalExact={item['musicalExactMatch']} "
            f"musicalMismatches={item['musicalMismatchCount']} "
            f"confidenceDifferences={item['confidenceDifferenceCount']}"
        )
        for row in item["eventRows"]:
            if not row["musicalMatch"]:
                lines.append(
                    f"  index {row['index']} categories={row['mismatchCategories']} "
                    f"chorus1={row['chorus1']} chorus2={row['chorus2']}"
                )
    TEXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Chorus 1 / Chorus 2 musical consensus audit complete")
    print(f"Pairs compared: {len(PAIRS)}")
    print(f"Musical exact-match pairs: {musical_match_pairs}")
    print(f"Musical non-matching pairs: {len(PAIRS) - musical_match_pairs}")
    print(f"Total musical event mismatches: {total_musical_mismatches}")
    print(f"Total confidence differences: {total_confidence_differences}")
    print(f"Mismatch categories: {category_counts}")
    print("Automatic approval applied: False")
    print("Ready for training: False")
    print(f"JSON: {OUTPUT.relative_to(ROOT)}")
    print(f"Text: {TEXT.relative_to(ROOT)}")
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
