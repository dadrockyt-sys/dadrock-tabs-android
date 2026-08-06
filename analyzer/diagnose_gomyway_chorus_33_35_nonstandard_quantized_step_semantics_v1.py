from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

CANDIDATE_PATH = PUBLIC / "gomyway-chorus-33-35-identity-separated-onset-candidate-v1.json"
CARDINALITY_PATH = PUBLIC / "gomyway-chorus-33-35-step-grid-cardinality-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-nonstandard-quantized-step-semantics-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-nonstandard-quantized-step-semantics-v1-manifest.json"


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def integer(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def row_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "measureNumber": integer(row.get("measureNumber")),
        "quantizedStep": integer(row.get("quantizedStep")),
        "sourceEventIndex": row.get("sourceEventIndex"),
        "resolvedStartSeconds": number(row.get("resolvedStartSeconds")),
        "timingSource": row.get("timingSource"),
        "noteMultiplicity": row.get("noteMultiplicity"),
        "isSingleNoteTechniqueCandidate": bool(row.get("isSingleNoteTechniqueCandidate")),
        "notes": row.get("notes", []),
    }


def main() -> None:
    candidate = load(CANDIDATE_PATH)
    cardinality = load(CARDINALITY_PATH)

    if candidate.get("passed") is not True:
        raise RuntimeError("Identity-separated timing candidate did not complete.")
    if cardinality.get("passed") is not True:
        raise RuntimeError("Step-grid cardinality diagnostic is not green.")
    if cardinality.get("recommendedNextAction") != "inspect-nonstandard-quantized-step-semantics":
        raise RuntimeError("Cardinality diagnostic did not authorize semantic inspection.")

    rows = [row for row in candidate.get("rows", []) if isinstance(row, dict)]
    if len(rows) != 30:
        raise RuntimeError(f"Expected 30 chorus rows, found {len(rows)}.")

    by_measure: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        measure = integer(row.get("measureNumber"))
        step = integer(row.get("quantizedStep"))
        start = number(row.get("resolvedStartSeconds"))
        if measure is None or step is None or start is None:
            continue
        by_measure.setdefault(measure, []).append(row)

    conflicts: list[dict[str, Any]] = []
    measure_reports: list[dict[str, Any]] = []

    for measure in sorted(by_measure):
        measure_rows = sorted(
            by_measure[measure],
            key=lambda row: int(row["quantizedStep"]),
        )
        local_conflicts: list[dict[str, Any]] = []
        for index, (left, right) in enumerate(zip(measure_rows, measure_rows[1:])):
            left_time = float(left["resolvedStartSeconds"])
            right_time = float(right["resolvedStartSeconds"])
            if left_time < right_time:
                continue

            previous_row = measure_rows[index - 1] if index > 0 else None
            following_row = (
                measure_rows[index + 2]
                if index + 2 < len(measure_rows)
                else None
            )
            conflict = {
                "measureNumber": measure,
                "left": row_summary(left),
                "right": row_summary(right),
                "deltaSeconds": round(right_time - left_time, 6),
                "stepDelta": int(right["quantizedStep"]) - int(left["quantizedStep"]),
                "previousNeighbor": row_summary(previous_row) if previous_row else None,
                "followingNeighbor": row_summary(following_row) if following_row else None,
                "sameTimingSource": left.get("timingSource") == right.get("timingSource"),
                "sourceEventIndexOrderPassed": (
                    integer(left.get("sourceEventIndex")) is not None
                    and integer(right.get("sourceEventIndex")) is not None
                    and int(left["sourceEventIndex"]) < int(right["sourceEventIndex"])
                ),
                "readOnly": True,
            }
            local_conflicts.append(conflict)
            conflicts.append(conflict)

        steps = [int(row["quantizedStep"]) for row in measure_rows]
        times = [float(row["resolvedStartSeconds"]) for row in measure_rows]
        source_indexes = [integer(row.get("sourceEventIndex")) for row in measure_rows]
        measure_reports.append({
            "measureNumber": measure,
            "rowCount": len(measure_rows),
            "stepsInStepOrder": steps,
            "timesInStepOrder": [round(value, 6) for value in times],
            "sourceEventIndexesInStepOrder": source_indexes,
            "withinMeasureConflictCount": len(local_conflicts),
            "strictlyIncreasingByStep": len(local_conflicts) == 0,
            "rows": [row_summary(row) for row in measure_rows],
        })

    conflict_measures = sorted({int(row["measureNumber"]) for row in conflicts})
    same_measure_only = all(
        row["left"]["measureNumber"] == row["right"]["measureNumber"]
        for row in conflicts
    )
    all_conflicts_adjacent_steps = all(int(row["stepDelta"]) == 1 for row in conflicts)
    all_conflicts_same_timing_source = all(bool(row["sameTimingSource"]) for row in conflicts)
    any_source_index_reversal = any(
        not bool(row["sourceEventIndexOrderPassed"])
        for row in conflicts
        if row["left"].get("sourceEventIndex") is not None
        and row["right"].get("sourceEventIndex") is not None
    )

    if len(conflicts) == 1 and same_measure_only:
        recommended = "arbitrate-single-within-measure-step-conflict-with-local-audio-onsets"
    elif conflicts and any_source_index_reversal:
        recommended = "inspect-source-event-index-to-step-assignment"
    elif conflicts:
        recommended = "derive-within-measure-order-from-audio-onset-sequence"
    else:
        recommended = "rebuild-completed-timing-plan-with-16-step-ordering"

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-nonstandard-quantized-step-semantics",
        "passed": True,
        "chorusEventCount": len(rows),
        "minimumRequiredStepsPerMeasure": int(cardinality.get("minimumRequiredStepsPerMeasure", 16)),
        "withinMeasureConflictCount": len(conflicts),
        "conflictMeasureNumbers": conflict_measures,
        "allConflictsWithinSameMeasure": same_measure_only,
        "allConflictsBetweenAdjacentSteps": all_conflicts_adjacent_steps,
        "allConflictsUseSameTimingSource": all_conflicts_same_timing_source,
        "anyConflictReversesSourceEventIndexOrder": any_source_index_reversal,
        "measureReports": measure_reports,
        "conflicts": conflicts,
        "recommendedNextAction": recommended,
        "timingRepairApplied": False,
        "audioTechniqueSupportClaimed": False,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }

    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "withinMeasureConflictCount": len(conflicts),
        "conflictMeasureNumbers": conflict_measures,
        "recommendedNextAction": recommended,
        "timingRepairApplied": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 NONSTANDARD QUANTIZED STEP SEMANTICS V1 COMPLETE")
    print("Passed: True")
    print("Chorus events:", len(rows))
    print("Within-measure conflicts:", len(conflicts))
    print("Conflict measures:", conflict_measures)
    print("All conflicts within same measure:", same_measure_only)
    print("All conflicts between adjacent steps:", all_conflicts_adjacent_steps)
    print("All conflicts use same timing source:", all_conflicts_same_timing_source)
    print("Any conflict reverses source-event-index order:", any_source_index_reversal)
    print("Recommended next action:", recommended)
    for conflict in conflicts:
        left = conflict["left"]
        right = conflict["right"]
        print(
            f"measure={conflict['measureNumber']} "
            f"leftStep={left['quantizedStep']} leftTime={left['resolvedStartSeconds']} "
            f"leftSourceIndex={left['sourceEventIndex']} leftSource={left['timingSource']} "
            f"rightStep={right['quantizedStep']} rightTime={right['resolvedStartSeconds']} "
            f"rightSourceIndex={right['sourceEventIndex']} rightSource={right['timingSource']} "
            f"delta={conflict['deltaSeconds']}"
        )
        if conflict["previousNeighbor"]:
            previous = conflict["previousNeighbor"]
            print(
                f"  previous step={previous['quantizedStep']} "
                f"time={previous['resolvedStartSeconds']} "
                f"sourceIndex={previous['sourceEventIndex']}"
            )
        if conflict["followingNeighbor"]:
            following = conflict["followingNeighbor"]
            print(
                f"  following step={following['quantizedStep']} "
                f"time={following['resolvedStartSeconds']} "
                f"sourceIndex={following['sourceEventIndex']}"
            )
    print("Timing repair applied: False")
    print("Audio technique support claimed: False")
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
