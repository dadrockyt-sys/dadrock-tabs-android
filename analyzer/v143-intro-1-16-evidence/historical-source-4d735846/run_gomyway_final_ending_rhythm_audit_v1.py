from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
RANKING_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-chorus-soft-evidence-ranking-v1.json"
)
TIMING_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-professional-timing-map-v2.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-final-ending-rhythm-audit-v1.json"
)

ENDING_START = 111
ENDING_END = 113


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing required input: {path.relative_to(REPO_ROOT)}"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    measure = int(row.get("measureNumber") or row.get("measure") or 0)
    step = int(row.get("candidateStep") or row.get("step") or 0)
    return {
        "measureNumber": measure,
        "candidateStep": step,
        "section": row.get("section") or "unknown",
        "classification": row.get("classification"),
        "referenceWithinOneStep": bool(row.get("referenceWithinOneStep")),
        "referenceDistance": row.get("referenceDistance"),
        "score": row.get("score"),
        "softComponents": row.get("softComponents") or {},
    }


def meter_for_measure(
    timing: dict[str, Any],
    measure: int,
) -> dict[str, Any] | None:
    regions = timing.get("meterRegions") or []
    for region in regions:
        start = int(region.get("startMeasure") or 0)
        end = int(region.get("endMeasure") or 0)
        if start <= measure <= end:
            return {
                "numerator": int(region.get("numerator") or 4),
                "denominator": int(region.get("denominator") or 4),
            }
    return None


def main() -> None:
    ranking = load(RANKING_PATH)
    timing = load(TIMING_PATH)

    source_rows = ranking.get("overallRanking") or []
    raw_rows = [
        compact_row(row)
        for row in source_rows
        if ENDING_START
        <= int(row.get("measureNumber") or row.get("measure") or 0)
        <= ENDING_END
    ]

    unique: dict[tuple[int, int], dict[str, Any]] = {}
    duplicate_counts: dict[tuple[int, int], int] = defaultdict(int)

    for row in raw_rows:
        key = (row["measureNumber"], row["candidateStep"])
        duplicate_counts[key] += 1
        previous = unique.get(key)
        if previous is None:
            unique[key] = row
            continue
        if row["referenceWithinOneStep"] and not previous["referenceWithinOneStep"]:
            unique[key] = row
        elif (
            row["referenceWithinOneStep"] == previous["referenceWithinOneStep"]
            and float(row.get("score") or 0.0)
            > float(previous.get("score") or 0.0)
        ):
            unique[key] = row

    deduplicated = [unique[key] for key in sorted(unique)]
    by_measure: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in deduplicated:
        by_measure[row["measureNumber"]].append(row)

    reports = []
    unresolved_events = []
    for measure in range(ENDING_START, ENDING_END + 1):
        rows = sorted(
            by_measure.get(measure, []),
            key=lambda item: item["candidateStep"],
        )
        covered = [row for row in rows if row["referenceWithinOneStep"]]
        unresolved = [row for row in rows if not row["referenceWithinOneStep"]]
        unresolved_events.extend(unresolved)
        reports.append({
            "measureNumber": measure,
            "meter": meter_for_measure(timing, measure),
            "sectionLabels": sorted({row["section"] for row in rows}),
            "candidateCount": len(rows),
            "coveredCount": len(covered),
            "unresolvedCount": len(unresolved),
            "coveredSteps": [row["candidateStep"] for row in covered],
            "unresolvedSteps": [row["candidateStep"] for row in unresolved],
            "events": rows,
        })

    covered_count = sum(
        1 for row in deduplicated if row["referenceWithinOneStep"]
    )
    total = len(deduplicated)

    report = {
        "schemaVersion": 1,
        "auditType": "final-ending-read-only-rhythm-audit",
        "measureRange": [ENDING_START, ENDING_END],
        "rankingSource": str(RANKING_PATH.relative_to(REPO_ROOT)),
        "timingSource": str(TIMING_PATH.relative_to(REPO_ROOT)),
        "rawRowCount": len(raw_rows),
        "deduplicatedCandidateCount": total,
        "duplicateCandidateKeyCount": sum(
            1 for count in duplicate_counts.values() if count > 1
        ),
        "professionallyCoveredCandidateCount": covered_count,
        "unresolvedCandidateCount": total - covered_count,
        "coverageFraction": (
            round(covered_count / total, 6) if total else 0.0
        ),
        "measureReports": reports,
        "unresolvedEvents": unresolved_events,
        "interpretation": (
            "This is a read-only inventory of the final ending after the locked "
            "Out-Chorus. Reference-covered events require no action. Any unresolved "
            "events must be reviewed directly before retention or rejection."
        ),
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Final-ending rhythm audit V1 complete")
    print("Measure range:", report["measureRange"])
    print("Raw rows:", report["rawRowCount"])
    print("Deduplicated candidates:", report["deduplicatedCandidateCount"])
    print("Duplicate candidate keys:", report["duplicateCandidateKeyCount"])
    print("Professionally covered candidates:", report["professionallyCoveredCandidateCount"])
    print("Unresolved candidates:", report["unresolvedCandidateCount"])
    print("Coverage fraction:", report["coverageFraction"])
    print()

    for item in reports:
        print(
            f"measure {item['measureNumber']} "
            f"meter={item['meter']} "
            f"sections={item['sectionLabels']} "
            f"candidates={item['candidateCount']} "
            f"covered={item['coveredCount']} "
            f"unresolved={item['unresolvedCount']} "
            f"unresolvedSteps={item['unresolvedSteps']}"
        )

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
