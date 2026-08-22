from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = REPO_ROOT / "public" / "gomyway-chorus-soft-evidence-ranking-v1.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-out-chorus-reference-coverage-audit-v1.json"

OUT_CHORUS_START = 103
OUT_CHORUS_END = 110


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing input: {path.relative_to(REPO_ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "measureNumber": int(row["measureNumber"]),
        "candidateStep": int(row["candidateStep"]),
        "classification": row.get("classification"),
        "referenceWithinOneStep": bool(row.get("referenceWithinOneStep")),
        "referenceDistance": row.get("referenceDistance"),
        "score": row.get("score"),
        "softComponents": row.get("softComponents") or {},
    }


def main() -> None:
    payload = load(INPUT_PATH)
    source_rows = payload.get("overallRanking") or []

    rows = [
        compact_row(row)
        for row in source_rows
        if row.get("section") == "Out-Chorus"
        and OUT_CHORUS_START <= int(row.get("measureNumber", 0)) <= OUT_CHORUS_END
    ]

    if not rows:
        raise ValueError("No Out-Chorus rows found for measures 103-110")

    unique: dict[tuple[int, int], dict[str, Any]] = {}
    duplicate_counts: dict[tuple[int, int], int] = defaultdict(int)

    for row in rows:
        key = (row["measureNumber"], row["candidateStep"])
        duplicate_counts[key] += 1
        previous = unique.get(key)
        if previous is None:
            unique[key] = row
            continue

        # Prefer reference-covered evidence if duplicate diagnostic rows disagree.
        if row["referenceWithinOneStep"] and not previous["referenceWithinOneStep"]:
            unique[key] = row

    deduplicated = [unique[key] for key in sorted(unique)]

    by_measure: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in deduplicated:
        by_measure[row["measureNumber"]].append(row)

    measure_reports = []
    for measure in range(OUT_CHORUS_START, OUT_CHORUS_END + 1):
        measure_rows = sorted(by_measure.get(measure, []), key=lambda item: item["candidateStep"])
        covered = [item for item in measure_rows if item["referenceWithinOneStep"]]
        unresolved = [item for item in measure_rows if not item["referenceWithinOneStep"]]

        measure_reports.append({
            "measureNumber": measure,
            "candidateCount": len(measure_rows),
            "coveredCount": len(covered),
            "unresolvedCount": len(unresolved),
            "coverageFraction": round(len(covered) / len(measure_rows), 6) if measure_rows else 0.0,
            "coveredSteps": [item["candidateStep"] for item in covered],
            "unresolvedSteps": [item["candidateStep"] for item in unresolved],
            "coveredEvents": covered,
            "unresolvedEvents": unresolved,
        })

    total = len(deduplicated)
    covered_total = sum(1 for row in deduplicated if row["referenceWithinOneStep"])
    unresolved_total = total - covered_total

    duplicate_keys = [
        {
            "measureNumber": measure,
            "candidateStep": step,
            "rowCount": count,
        }
        for (measure, step), count in sorted(duplicate_counts.items())
        if count > 1
    ]

    unresolved_events = [
        row for row in deduplicated if not row["referenceWithinOneStep"]
    ]

    report = {
        "schemaVersion": 1,
        "auditType": "out-chorus-professional-reference-coverage",
        "input": str(INPUT_PATH.relative_to(REPO_ROOT)),
        "section": "Out-Chorus",
        "measureRange": [OUT_CHORUS_START, OUT_CHORUS_END],
        "rawRowCount": len(rows),
        "deduplicatedCandidateCount": total,
        "duplicateCandidateKeyCount": len(duplicate_keys),
        "coveredCandidateCount": covered_total,
        "unresolvedCandidateCount": unresolved_total,
        "coverageFraction": round(covered_total / total, 6) if total else 0.0,
        "measureReports": measure_reports,
        "duplicateCandidateKeys": duplicate_keys,
        "unresolvedEvents": unresolved_events,
        "auditInterpretation": (
            "Reference-covered candidates are already accounted for and require no change. "
            "Only unresolved candidate steps should proceed to direct listening or professional-reference review."
        ),
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Out-Chorus reference coverage audit V1 complete")
    print("Raw rows:", report["rawRowCount"])
    print("Deduplicated candidates:", report["deduplicatedCandidateCount"])
    print("Duplicate candidate keys:", report["duplicateCandidateKeyCount"])
    print("Covered candidates:", report["coveredCandidateCount"])
    print("Unresolved candidates:", report["unresolvedCandidateCount"])
    print("Coverage fraction:", report["coverageFraction"])
    print()

    for item in measure_reports:
        print(
            f"measure {item['measureNumber']} "
            f"candidates={item['candidateCount']} "
            f"covered={item['coveredCount']} "
            f"unresolved={item['unresolvedCount']} "
            f"unresolvedSteps={item['unresolvedSteps']}"
        )

    print()
    print("Automatic promotion allowed: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
