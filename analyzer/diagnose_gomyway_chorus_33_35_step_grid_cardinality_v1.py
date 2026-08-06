from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

CANDIDATE_PATH = PUBLIC / "gomyway-chorus-33-35-identity-separated-onset-candidate-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-step-grid-cardinality-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-step-grid-cardinality-v1-manifest.json"

GRID_CANDIDATES = (12, 16, 24, 32)


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


def absolute_step(measure: int, step: int, steps_per_measure: int) -> int:
    return (measure - 1) * steps_per_measure + step


def evaluate_grid(rows: list[dict[str, Any]], steps_per_measure: int) -> dict[str, Any]:
    ordered = sorted(
        rows,
        key=lambda row: absolute_step(
            int(row["measureNumber"]),
            int(row["quantizedStep"]),
            steps_per_measure,
        ),
    )
    conflicts: list[dict[str, Any]] = []
    duplicate_positions: list[dict[str, Any]] = []
    previous_position: int | None = None

    for row in ordered:
        position = absolute_step(
            int(row["measureNumber"]),
            int(row["quantizedStep"]),
            steps_per_measure,
        )
        if previous_position is not None and position == previous_position:
            duplicate_positions.append({
                "measureNumber": row["measureNumber"],
                "quantizedStep": row["quantizedStep"],
                "absoluteStep": position,
            })
        previous_position = position

    for left, right in zip(ordered, ordered[1:]):
        left_time = number(left.get("resolvedStartSeconds"))
        right_time = number(right.get("resolvedStartSeconds"))
        if left_time is None or right_time is None or left_time < right_time:
            continue
        conflicts.append({
            "leftMeasure": left["measureNumber"],
            "leftStep": left["quantizedStep"],
            "leftTime": left_time,
            "rightMeasure": right["measureNumber"],
            "rightStep": right["quantizedStep"],
            "rightTime": right_time,
            "deltaSeconds": round(right_time - left_time, 6),
        })

    return {
        "stepsPerMeasure": steps_per_measure,
        "monotonicityConflictCount": len(conflicts),
        "duplicateAbsolutePositionCount": len(duplicate_positions),
        "strictlyMonotonicTiming": len(conflicts) == 0,
        "conflicts": conflicts,
        "duplicatePositions": duplicate_positions,
    }


def main() -> None:
    candidate = load(CANDIDATE_PATH)
    if candidate.get("passed") is not True:
        raise RuntimeError("Identity-separated onset candidate did not complete.")
    if int(candidate.get("monotonicityConflictCount", 0)) < 1:
        raise RuntimeError("This diagnostic requires remaining timing conflicts.")

    rows = [row for row in candidate.get("rows", []) if isinstance(row, dict)]
    if len(rows) != 30:
        raise RuntimeError(f"Expected 30 chorus rows, found {len(rows)}.")

    steps = [
        integer(row.get("quantizedStep"))
        for row in rows
        if integer(row.get("quantizedStep")) is not None
    ]
    maximum_step = max(int(step) for step in steps)
    minimum_required_cardinality = maximum_step + 1

    evaluations = [evaluate_grid(rows, grid) for grid in GRID_CANDIDATES]
    valid = [
        row for row in evaluations
        if int(row["stepsPerMeasure"]) >= minimum_required_cardinality
        and int(row["duplicateAbsolutePositionCount"]) == 0
        and bool(row["strictlyMonotonicTiming"])
    ]
    selected = min(valid, key=lambda row: int(row["stepsPerMeasure"]), default=None)

    twelve = next(row for row in evaluations if row["stepsPerMeasure"] == 12)
    sixteen = next(row for row in evaluations if row["stepsPerMeasure"] == 16)
    twelve_invalid = maximum_step >= 12
    quality_gate = bool(
        twelve_invalid
        and selected is not None
        and int(selected["stepsPerMeasure"]) == 16
        and int(sixteen["monotonicityConflictCount"]) == 0
    )

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-chorus-step-grid-cardinality",
        "passed": True,
        "chorusEventCount": len(rows),
        "minimumQuantizedStep": min(int(step) for step in steps),
        "maximumQuantizedStep": maximum_step,
        "minimumRequiredStepsPerMeasure": minimum_required_cardinality,
        "twelveStepGridInvalidForObservedSteps": twelve_invalid,
        "evaluations": evaluations,
        "selectedStepsPerMeasure": (
            selected["stepsPerMeasure"] if selected is not None else None
        ),
        "qualityGate": quality_gate,
        "recommendedNextAction": (
            "rebuild-completed-timing-plan-with-16-step-ordering"
            if quality_gate
            else "inspect-nonstandard-quantized-step-semantics"
        ),
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
        "maximumQuantizedStep": maximum_step,
        "minimumRequiredStepsPerMeasure": minimum_required_cardinality,
        "selectedStepsPerMeasure": output["selectedStepsPerMeasure"],
        "qualityGate": quality_gate,
        "recommendedNextAction": output["recommendedNextAction"],
        "timingRepairApplied": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 STEP GRID CARDINALITY V1 COMPLETE")
    print("Passed: True")
    print("Chorus events:", len(rows))
    print("Minimum quantized step:", output["minimumQuantizedStep"])
    print("Maximum quantized step:", maximum_step)
    print("Minimum required steps per measure:", minimum_required_cardinality)
    print("12-step grid invalid for observed steps:", twelve_invalid)
    for evaluation in evaluations:
        print(
            f"stepsPerMeasure={evaluation['stepsPerMeasure']} "
            f"conflicts={evaluation['monotonicityConflictCount']} "
            f"duplicatePositions={evaluation['duplicateAbsolutePositionCount']} "
            f"strictlyMonotonic={evaluation['strictlyMonotonicTiming']}"
        )
    print("Selected steps per measure:", output["selectedStepsPerMeasure"])
    print("Quality gate:", quality_gate)
    print("Recommended next action:", output["recommendedNextAction"])
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
