from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

CANDIDATE_PATH = PUBLIC / "gomyway-chorus-33-35-source-balanced-observed-timing-candidate-v1.json"
DUPLICATION_PATH = PUBLIC / "gomyway-chorus-33-35-observed-timing-source-duplication-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-source-family-local-order-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-source-family-local-order-v1-manifest.json"


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


def main() -> None:
    candidate = load(CANDIDATE_PATH)
    duplication = load(DUPLICATION_PATH)

    if candidate.get("passed") is not True:
        raise RuntimeError("Source-balanced timing candidate did not complete.")
    if int(candidate.get("monotonicityConflictCount", 0)) < 1:
        raise RuntimeError("This diagnostic requires remaining monotonicity conflicts.")
    if duplication.get("passed") is not True:
        raise RuntimeError("Timing duplication diagnostic is not green.")

    endpoint_rows = {
        (integer(row.get("measureNumber")), integer(row.get("quantizedStep"))): row
        for row in duplication.get("rows", [])
        if isinstance(row, dict)
    }

    conflict_rows: list[dict[str, Any]] = []
    path_order_failure_count = 0
    path_order_pass_count = 0
    missing_path_pair_count = 0

    for conflict in candidate.get("conflicts", []):
        if not isinstance(conflict, dict):
            continue
        left_key = (
            integer(conflict.get("leftMeasure")),
            integer(conflict.get("leftStep")),
        )
        right_key = (
            integer(conflict.get("rightMeasure")),
            integer(conflict.get("rightStep")),
        )
        left_endpoint = endpoint_rows.get(left_key, {})
        right_endpoint = endpoint_rows.get(right_key, {})

        left_paths = {
            str(row.get("path")): number(row.get("pathMedianStartSeconds"))
            for row in left_endpoint.get("pathRows", [])
            if isinstance(row, dict)
        }
        right_paths = {
            str(row.get("path")): number(row.get("pathMedianStartSeconds"))
            for row in right_endpoint.get("pathRows", [])
            if isinstance(row, dict)
        }

        shared_paths = sorted(set(left_paths) & set(right_paths))
        path_results: list[dict[str, Any]] = []
        for path in shared_paths:
            left_time = left_paths[path]
            right_time = right_paths[path]
            if left_time is None or right_time is None:
                continue
            delta = right_time - left_time
            order_passed = delta > 0.0
            if order_passed:
                path_order_pass_count += 1
            else:
                path_order_failure_count += 1
            path_results.append({
                "path": path,
                "leftTimeSeconds": round(left_time, 6),
                "rightTimeSeconds": round(right_time, 6),
                "deltaSeconds": round(delta, 6),
                "localOrderPassed": order_passed,
            })

        if not path_results:
            missing_path_pair_count += 1

        conflict_rows.append({
            "leftMeasure": left_key[0],
            "leftStep": left_key[1],
            "rightMeasure": right_key[0],
            "rightStep": right_key[1],
            "candidateDeltaSeconds": conflict.get("deltaSeconds"),
            "sharedSourcePathCount": len(path_results),
            "pathResults": path_results,
            "allSharedPathsPreserveOrder": bool(path_results) and all(
                row["localOrderPassed"] for row in path_results
            ),
            "anySharedPathReversesOrder": any(
                not row["localOrderPassed"] for row in path_results
            ),
            "timingRepairApplied": False,
            "readOnly": True,
        })

    all_conflicts_explained_by_source_order = bool(conflict_rows) and all(
        row["anySharedPathReversesOrder"] for row in conflict_rows
    )
    any_path_preserves_all_conflicts = False
    all_paths = sorted({
        result["path"]
        for row in conflict_rows
        for result in row["pathResults"]
    })
    path_summaries: list[dict[str, Any]] = []
    for path in all_paths:
        relevant = [
            result
            for row in conflict_rows
            for result in row["pathResults"]
            if result["path"] == path
        ]
        passed = sum(bool(row["localOrderPassed"]) for row in relevant)
        failed = len(relevant) - passed
        preserves_all = bool(relevant) and failed == 0
        any_path_preserves_all_conflicts = any_path_preserves_all_conflicts or preserves_all
        path_summaries.append({
            "path": path,
            "conflictPairCount": len(relevant),
            "orderPassedCount": passed,
            "orderFailedCount": failed,
            "preservesAllConflictPairOrder": preserves_all,
        })

    recommended = (
        "select-order-preserving-source-family-candidate"
        if any_path_preserves_all_conflicts
        else "derive-conflict-endpoints-from-local-monotonic-grid"
        if all_conflicts_explained_by_source_order
        else "inspect-measure-step-row-identity-mapping"
    )

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-source-family-local-order",
        "passed": len(conflict_rows) == int(candidate.get("monotonicityConflictCount", -1)),
        "conflictPairCount": len(conflict_rows),
        "sourcePathOrderPassedCount": path_order_pass_count,
        "sourcePathOrderFailedCount": path_order_failure_count,
        "conflictsWithoutSharedSourcePathCount": missing_path_pair_count,
        "allConflictsExplainedBySourceOrder": all_conflicts_explained_by_source_order,
        "anySourcePathPreservesAllConflictOrder": any_path_preserves_all_conflicts,
        "pathSummaries": path_summaries,
        "conflicts": conflict_rows,
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
        "conflictPairCount": len(conflict_rows),
        "sourcePathOrderPassedCount": path_order_pass_count,
        "sourcePathOrderFailedCount": path_order_failure_count,
        "recommendedNextAction": recommended,
        "timingRepairApplied": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 SOURCE FAMILY LOCAL ORDER V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Conflict pairs:", len(conflict_rows))
    print("Source-path order passes:", path_order_pass_count)
    print("Source-path order failures:", path_order_failure_count)
    print("Conflicts without shared source path:", missing_path_pair_count)
    print("Any source path preserves all conflict order:", any_path_preserves_all_conflicts)
    print("Recommended next action:", recommended)
    for summary in path_summaries:
        print(
            f"path={summary['path']} pairs={summary['conflictPairCount']} "
            f"passed={summary['orderPassedCount']} failed={summary['orderFailedCount']} "
            f"preservesAll={summary['preservesAllConflictPairOrder']}"
        )
    for row in conflict_rows:
        print(
            f"pair=m{row['leftMeasure']}s{row['leftStep']}->"
            f"m{row['rightMeasure']}s{row['rightStep']} "
            f"sharedPaths={row['sharedSourcePathCount']}"
        )
        for result in row["pathResults"]:
            print(
                f"  path={result['path']} left={result['leftTimeSeconds']} "
                f"right={result['rightTimeSeconds']} delta={result['deltaSeconds']} "
                f"orderPassed={result['localOrderPassed']}"
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
