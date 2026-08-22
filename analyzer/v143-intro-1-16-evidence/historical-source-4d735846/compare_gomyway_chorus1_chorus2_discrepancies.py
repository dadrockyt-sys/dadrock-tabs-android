from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHORUS1 = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-populated.json"
CHORUS2A = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-populated.json"
CHORUS2B = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-populated.json"
OUTPUT = ROOT / "public" / "gomyway-chorus1-chorus2-discrepancy-audit.json"
TEXT = ROOT / "public" / "gomyway-chorus1-chorus2-discrepancy-audit.txt"

PAIRS = [(33, 63), (34, 64), (35, 65), (36, 66), (37, 67), (38, 68)]


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def event_signature(event: dict[str, Any]) -> dict[str, Any]:
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
        "confidence": float(event.get("referenceConfidence", 0.0)),
    }


def normalized_measure(measure: dict[str, Any]) -> list[dict[str, Any]]:
    return [event_signature(event) for event in measure.get("events", [])]


def diff_events(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> dict[str, Any]:
    max_len = max(len(left), len(right))
    rows: list[dict[str, Any]] = []
    mismatch_count = 0
    for index in range(max_len):
        l = left[index] if index < len(left) else None
        r = right[index] if index < len(right) else None
        equal = l == r
        if not equal:
            mismatch_count += 1
        rows.append({
            "index": index,
            "chorus1": l,
            "chorus2": r,
            "match": equal,
        })
    return {
        "eventCountChorus1": len(left),
        "eventCountChorus2": len(right),
        "mismatchCount": mismatch_count,
        "exactMatch": mismatch_count == 0,
        "eventRows": rows,
    }


def main() -> None:
    packets = [load(CHORUS1), load(CHORUS2A), load(CHORUS2B)]
    measures: dict[int, dict[str, Any]] = {}
    for packet in packets:
        for measure in packet.get("measures", []):
            number = int(measure["measureNumber"])
            measures[number] = measure

    missing = [number for pair in PAIRS for number in pair if number not in measures]
    if missing:
        raise RuntimeError(f"Missing chorus measures: {sorted(set(missing))}")

    comparisons: list[dict[str, Any]] = []
    exact_pairs = 0
    total_mismatches = 0
    for c1, c2 in PAIRS:
        left = normalized_measure(measures[c1])
        right = normalized_measure(measures[c2])
        diff = diff_events(left, right)
        if diff["exactMatch"]:
            exact_pairs += 1
        total_mismatches += int(diff["mismatchCount"])
        comparisons.append({
            "chorus1Measure": c1,
            "chorus2Measure": c2,
            "chorus1SectionVariant": measures[c1].get("sectionVariant"),
            "chorus2SectionVariant": measures[c2].get("sectionVariant"),
            **diff,
            "decision": None,
            "reviewNotes": "",
        })

    result = {
        "schemaVersion": 1,
        "comparison": "Chorus 1 measures 33-38 vs Chorus 2 measures 63-68",
        "pairs": PAIRS,
        "pairCount": len(PAIRS),
        "exactMatchPairs": exact_pairs,
        "nonMatchingPairs": len(PAIRS) - exact_pairs,
        "totalEventMismatches": total_mismatches,
        "comparisons": comparisons,
        "automaticApprovalApplied": False,
        "readyForTraining": False,
        "nextRequiredStage": "human-resolve-chorus-pair-discrepancies-against-professional-reference-pages-3-and-5",
        "protectedBaselinesChanged": False,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "GOMYWAY CHORUS 1 / CHORUS 2 DISCREPANCY AUDIT",
        f"Pairs compared: {len(PAIRS)}",
        f"Exact-match pairs: {exact_pairs}",
        f"Non-matching pairs: {len(PAIRS) - exact_pairs}",
        f"Total event mismatches: {total_mismatches}",
        "Automatic approval applied: False",
        "Ready for training: False",
        "Protected baselines changed: False",
        "",
    ]
    for item in comparisons:
        lines.append(
            f"PAIR {item['chorus1Measure']} vs {item['chorus2Measure']}: "
            f"events={item['eventCountChorus1']}/{item['eventCountChorus2']} "
            f"mismatches={item['mismatchCount']} exact={item['exactMatch']}"
        )
        for row in item["eventRows"]:
            if not row["match"]:
                lines.append(
                    f"  index {row['index']}: chorus1={row['chorus1']} chorus2={row['chorus2']}"
                )
    TEXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Chorus 1 / Chorus 2 discrepancy audit complete")
    print(f"Pairs compared: {len(PAIRS)}")
    print(f"Exact-match pairs: {exact_pairs}")
    print(f"Non-matching pairs: {len(PAIRS) - exact_pairs}")
    print(f"Total event mismatches: {total_mismatches}")
    print("Automatic approval applied: False")
    print("Ready for training: False")
    print(f"JSON: {OUTPUT.relative_to(ROOT)}")
    print(f"Text: {TEXT.relative_to(ROOT)}")
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
