from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

PLAN_PATH = PUBLIC / "gomyway-chorus-33-35-completed-timing-plan-v2.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-remaining-v2-timing-conflict-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-remaining-v2-timing-conflict-v1-manifest.json"


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


def summary(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(row, dict):
        return None
    return {
        "measureNumber": integer(row.get("measureNumber")),
        "quantizedStep": integer(row.get("quantizedStep")),
        "absoluteStep": integer(row.get("absoluteStep")),
        "resolvedStartSeconds": number(row.get("resolvedStartSeconds")),
        "timingSource": row.get("timingSource"),
        "sourceEventIndex": row.get("sourceEventIndex"),
        "noteMultiplicity": row.get("noteMultiplicity"),
        "isSingleNoteTechniqueCandidate": bool(row.get("isSingleNoteTechniqueCandidate")),
        "notes": row.get("notes", []),
    }


def main() -> None:
    plan = load(PLAN_PATH)
    if int(plan.get("stepsPerMeasure", -1)) != 16:
        raise RuntimeError("Completed timing plan V2 is not using the 16-step grid.")
    if int(plan.get("chorusEventCount", -1)) != 30:
        raise RuntimeError("Completed timing plan V2 must contain 30 chorus events.")
    if int(plan.get("monotonicityConflictCount", 0)) < 1:
        raise RuntimeError("No remaining V2 timing conflict is available to diagnose.")

    rows = [row for row in plan.get("rows", []) if isinstance(row, dict)]
    rows.sort(key=lambda row: int(row["absoluteStep"]))

    conflicts: list[dict[str, Any]] = []
    for index, (left, right) in enumerate(zip(rows, rows[1:])):
        left_time = number(left.get("resolvedStartSeconds"))
        right_time = number(right.get("resolvedStartSeconds"))
        if left_time is None or right_time is None or left_time < right_time:
            continue
        left_measure = integer(left.get("measureNumber"))
        right_measure = integer(right.get("measureNumber"))
        conflict = {
            "left": summary(left),
            "right": summary(right),
            "previousNeighbor": summary(rows[index - 1]) if index > 0 else None,
            "followingNeighbor": summary(rows[index + 2]) if index + 2 < len(rows) else None,
            "deltaSeconds": round(right_time - left_time, 6),
            "crossMeasure": left_measure != right_measure,
            "sameMeasure": left_measure == right_measure,
            "sameTimingSource": left.get("timingSource") == right.get("timingSource"),
            "leftDerived": left.get("timingSource") not in ("observed-measure-step-consensus", None),
            "rightDerived": right.get("timingSource") not in ("observed-measure-step-consensus", None),
            "readOnly": True,
        }
        conflicts.append(conflict)

    all_cross_measure = bool(conflicts) and all(row["crossMeasure"] for row in conflicts)
    all_same_measure = bool(conflicts) and all(row["sameMeasure"] for row in conflicts)
    any_derived_endpoint = any(row["leftDerived"] or row["rightDerived"] for row in conflicts)

    if len(conflicts) == 1 and all_cross_measure:
        recommended = "arbitrate-single-cross-measure-boundary-with-local-audio-onsets"
    elif all_same_measure:
        recommended = "inspect-within-measure-candidate-version-mismatch"
    elif any_derived_endpoint:
        recommended = "inspect-derived-timing-boundary-assignment"
    else:
        recommended = "inspect-observed-cross-measure-timing-provenance"

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-remaining-completed-timing-plan-v2-conflict",
        "passed": len(conflicts) == int(plan.get("monotonicityConflictCount", -1)),
        "conflictCount": len(conflicts),
        "allConflictsCrossMeasure": all_cross_measure,
        "allConflictsWithinMeasure": all_same_measure,
        "anyDerivedEndpoint": any_derived_endpoint,
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
        "passed": output["passed"],
        "conflictCount": len(conflicts),
        "allConflictsCrossMeasure": all_cross_measure,
        "anyDerivedEndpoint": any_derived_endpoint,
        "recommendedNextAction": recommended,
        "timingRepairApplied": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 REMAINING V2 TIMING CONFLICT V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Remaining conflicts:", len(conflicts))
    print("All conflicts cross measure:", all_cross_measure)
    print("All conflicts within measure:", all_same_measure)
    print("Any derived endpoint:", any_derived_endpoint)
    print("Recommended next action:", recommended)
    for conflict in conflicts:
        left = conflict["left"]
        right = conflict["right"]
        print(
            f"left=m{left['measureNumber']}s{left['quantizedStep']} "
            f"time={left['resolvedStartSeconds']} source={left['timingSource']} "
            f"right=m{right['measureNumber']}s{right['quantizedStep']} "
            f"time={right['resolvedStartSeconds']} source={right['timingSource']} "
            f"delta={conflict['deltaSeconds']} crossMeasure={conflict['crossMeasure']}"
        )
        if conflict["previousNeighbor"]:
            previous = conflict["previousNeighbor"]
            print(
                f"  previous=m{previous['measureNumber']}s{previous['quantizedStep']} "
                f"time={previous['resolvedStartSeconds']} source={previous['timingSource']}"
            )
        if conflict["followingNeighbor"]:
            following = conflict["followingNeighbor"]
            print(
                f"  following=m{following['measureNumber']}s{following['quantizedStep']} "
                f"time={following['resolvedStartSeconds']} source={following['timingSource']}"
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

    if not output["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
