from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

PLAN_PATH = PUBLIC / "gomyway-chorus-33-35-completed-timing-plan-v1.json"
DUPLICATION_PATH = PUBLIC / "gomyway-chorus-33-35-observed-timing-source-duplication-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-source-balanced-observed-timing-candidate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-source-balanced-observed-timing-candidate-v1-manifest.json"


def load(path: Path) -> dict[str, Any]:
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


def main() -> None:
    plan = load(PLAN_PATH)
    duplication = load(DUPLICATION_PATH)

    if duplication.get("passed") is not True:
        raise RuntimeError("Timing-source duplication diagnostic is not green.")
    if duplication.get("recommendedNextAction") != "build-source-balanced-observed-timing-candidate":
        raise RuntimeError("Duplication diagnostic did not authorize source balancing.")
    if duplication.get("sourcePathDisagreementAbove80ms") is not False:
        raise RuntimeError("Source families disagree above the allowed threshold.")

    balanced = {
        (integer(row.get("measureNumber")), integer(row.get("quantizedStep"))): number(
            row.get("pathBalancedMedianStartSeconds")
        )
        for row in duplication.get("rows", [])
        if isinstance(row, dict)
        and row.get("pathBalancedMedianStartSeconds") is not None
    }

    rows: list[dict[str, Any]] = []
    replaced = 0
    for source_row in plan.get("rows", []):
        if not isinstance(source_row, dict):
            continue
        row = dict(source_row)
        key = (
            integer(row.get("measureNumber")),
            integer(row.get("quantizedStep")),
        )
        candidate = balanced.get(key)
        if candidate is not None:
            row["originalResolvedStartSeconds"] = row.get("resolvedStartSeconds")
            row["resolvedStartSeconds"] = round(candidate, 6)
            row["timingSource"] = "source-path-balanced-observed-median"
            row["sourceBalancedReplacementApplied"] = True
            replaced += 1
        else:
            row["sourceBalancedReplacementApplied"] = False
        rows.append(row)

    rows.sort(key=lambda row: int(row["absoluteStep"]))
    conflicts: list[dict[str, Any]] = []
    for left, right in zip(rows, rows[1:]):
        left_time = number(left.get("resolvedStartSeconds"))
        right_time = number(right.get("resolvedStartSeconds"))
        if left_time is None or right_time is None or left_time < right_time:
            continue
        conflicts.append({
            "leftMeasure": left.get("measureNumber"),
            "leftStep": left.get("quantizedStep"),
            "leftTime": left_time,
            "rightMeasure": right.get("measureNumber"),
            "rightStep": right.get("quantizedStep"),
            "rightTime": right_time,
            "deltaSeconds": round(right_time - left_time, 6),
        })

    monotonic = len(conflicts) == 0
    ready = (
        len(rows) == 30
        and replaced == int(duplication.get("conflictEndpointCount", -1))
        and monotonic
    )

    output = {
        "schemaVersion": 1,
        "candidateType": "read-only-source-path-balanced-observed-timing",
        "passed": len(rows) == 30 and replaced == int(duplication.get("conflictEndpointCount", -1)),
        "chorusEventCount": len(rows),
        "sourceBalancedReplacementCount": replaced,
        "monotonicityConflictCount": len(conflicts),
        "strictlyMonotonicTiming": monotonic,
        "conflicts": conflicts,
        "rows": rows,
        "readyForCompletedTimingPlanV2": ready,
        "timingRepairAppliedToProtectedSource": False,
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
        "sourceBalancedReplacementCount": replaced,
        "monotonicityConflictCount": len(conflicts),
        "strictlyMonotonicTiming": monotonic,
        "readyForCompletedTimingPlanV2": ready,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 SOURCE-BALANCED OBSERVED TIMING CANDIDATE V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Chorus events:", len(rows))
    print("Source-balanced replacements:", replaced)
    print("Monotonicity conflicts:", len(conflicts))
    print("Strictly monotonic timing:", monotonic)
    print("Ready for completed timing plan V2:", ready)
    for conflict in conflicts:
        print(
            f"left=m{conflict['leftMeasure']}s{conflict['leftStep']} "
            f"time={conflict['leftTime']} right=m{conflict['rightMeasure']}s{conflict['rightStep']} "
            f"time={conflict['rightTime']} delta={conflict['deltaSeconds']}"
        )
    print("Timing repair applied to protected source: False")
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
