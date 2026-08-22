from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

PLAN_PATH = PUBLIC / "gomyway-chorus-33-35-completed-timing-plan-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-timing-monotonicity-diagnostic-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-timing-monotonicity-diagnostic-v1-manifest.json"


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main() -> None:
    plan = load(PLAN_PATH)
    rows = [row for row in plan.get("rows", []) if isinstance(row, dict)]
    if len(rows) != 30:
        raise RuntimeError(f"Expected 30 completed timing rows, found {len(rows)}.")

    rows.sort(key=lambda row: int(row["absoluteStep"]))
    conflicts: list[dict[str, Any]] = []

    for left, right in zip(rows, rows[1:]):
        left_start = number(left.get("resolvedStartSeconds"))
        right_start = number(right.get("resolvedStartSeconds"))
        if left_start is None or right_start is None or left_start < right_start:
            continue

        conflicts.append({
            "left": {
                "measureNumber": left.get("measureNumber"),
                "quantizedStep": left.get("quantizedStep"),
                "absoluteStep": left.get("absoluteStep"),
                "resolvedStartSeconds": left_start,
                "timingSource": left.get("timingSource"),
                "isSingleNoteTechniqueCandidate": left.get(
                    "isSingleNoteTechniqueCandidate"
                ),
            },
            "right": {
                "measureNumber": right.get("measureNumber"),
                "quantizedStep": right.get("quantizedStep"),
                "absoluteStep": right.get("absoluteStep"),
                "resolvedStartSeconds": right_start,
                "timingSource": right.get("timingSource"),
                "isSingleNoteTechniqueCandidate": right.get(
                    "isSingleNoteTechniqueCandidate"
                ),
            },
            "deltaSeconds": round(right_start - left_start, 6),
            "conflictType": (
                "equal-time-collision"
                if left_start == right_start else "time-reversal"
            ),
            "readOnly": True,
        })

    observed_conflicts = sum(
        1
        for conflict in conflicts
        if conflict["left"]["timingSource"] == "observed-measure-step-consensus"
        and conflict["right"]["timingSource"] == "observed-measure-step-consensus"
    )
    derived_conflicts = len(conflicts) - observed_conflicts

    if not conflicts:
        recommended = "recheck-completed-plan-monotonicity-code"
    elif observed_conflicts > 0:
        recommended = "diagnose-conflicting-observed-timing-sources"
    else:
        recommended = "repair-derived-timings-with-bounded-order-constraints"

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-completed-timing-monotonicity",
        "passed": True,
        "chorusEventCount": len(rows),
        "monotonicityConflictCount": len(conflicts),
        "observedOnlyConflictCount": observed_conflicts,
        "derivedTimingConflictCount": derived_conflicts,
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
        "monotonicityConflictCount": len(conflicts),
        "observedOnlyConflictCount": observed_conflicts,
        "derivedTimingConflictCount": derived_conflicts,
        "recommendedNextAction": recommended,
        "timingRepairApplied": False,
        "audioTechniqueSupportClaimed": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 TIMING MONOTONICITY DIAGNOSTIC V1 COMPLETE")
    print("Passed: True")
    print("Chorus events inspected:", len(rows))
    print("Monotonicity conflicts:", len(conflicts))
    print("Observed-only conflicts:", observed_conflicts)
    print("Derived-timing conflicts:", derived_conflicts)
    print("Recommended next action:", recommended)
    for conflict in conflicts:
        left = conflict["left"]
        right = conflict["right"]
        print(
            f"left=m{left['measureNumber']}s{left['quantizedStep']} "
            f"time={left['resolvedStartSeconds']} source={left['timingSource']} "
            f"right=m{right['measureNumber']}s{right['quantizedStep']} "
            f"time={right['resolvedStartSeconds']} source={right['timingSource']} "
            f"delta={conflict['deltaSeconds']} type={conflict['conflictType']}"
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
