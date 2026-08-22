from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

BRIDGE_PATH = PUBLIC / "gomyway-chorus-33-35-measure-step-timing-bridge-v1.json"
MONOTONICITY_PATH = PUBLIC / "gomyway-chorus-33-35-timing-monotonicity-diagnostic-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-conflicting-observed-timing-sources-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-conflicting-observed-timing-sources-v1-manifest.json"


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
    bridge = load(BRIDGE_PATH)
    diagnostic = load(MONOTONICITY_PATH)

    if bridge.get("passed") is not True:
        raise RuntimeError("Measure/step timing bridge is not green.")
    if diagnostic.get("passed") is not True:
        raise RuntimeError("Monotonicity diagnostic is not green.")
    if diagnostic.get("recommendedNextAction") != "diagnose-conflicting-observed-timing-sources":
        raise RuntimeError("Monotonicity diagnostic did not authorize observed-source analysis.")

    bridge_by_key = {
        (integer(row.get("measureNumber")), integer(row.get("quantizedStep"))): row
        for row in bridge.get("rows", [])
        if isinstance(row, dict)
    }

    conflict_keys: set[tuple[int | None, int | None]] = set()
    for conflict in diagnostic.get("conflicts", []):
        if not isinstance(conflict, dict):
            continue
        for side in ("left", "right"):
            row = conflict.get(side)
            if isinstance(row, dict):
                conflict_keys.add((
                    integer(row.get("measureNumber")),
                    integer(row.get("quantizedStep")),
                ))

    rows: list[dict[str, Any]] = []
    source_path_counts: dict[str, int] = {}
    multi_source_count = 0
    single_source_count = 0

    for key in sorted(conflict_keys, key=lambda item: ((item[0] or 0), (item[1] or 0))):
        bridge_row = bridge_by_key.get(key)
        if bridge_row is None:
            continue

        observations: list[dict[str, Any]] = []
        starts: list[float] = []
        for observation in bridge_row.get("timingSources", []):
            if not isinstance(observation, dict):
                continue
            start = number(observation.get("startSeconds"))
            path = str(observation.get("path", "unknown"))
            if start is None:
                continue
            starts.append(start)
            source_path_counts[path] = source_path_counts.get(path, 0) + 1
            observations.append({
                "path": path,
                "rowIndex": observation.get("rowIndex"),
                "startSeconds": round(start, 6),
                "endSeconds": observation.get("endSeconds"),
            })

        if len(observations) > 1:
            multi_source_count += 1
        else:
            single_source_count += 1

        median_start = statistics.median(starts) if starts else None
        spread = max(starts) - min(starts) if len(starts) > 1 else 0.0
        rows.append({
            "measureNumber": key[0],
            "quantizedStep": key[1],
            "resolvedStartSeconds": bridge_row.get("resolvedStartSeconds"),
            "timingObservationCount": len(observations),
            "timingObservationSpreadSeconds": round(spread, 6),
            "medianObservationStartSeconds": (
                round(median_start, 6) if median_start is not None else None
            ),
            "observations": observations,
            "timingConsensusPassed": bridge_row.get("timingConsensusPassed"),
            "readOnly": True,
        })

    unique_paths = sorted(source_path_counts)
    all_single_source = bool(rows) and all(row["timingObservationCount"] == 1 for row in rows)
    any_multi_source = any(row["timingObservationCount"] > 1 for row in rows)
    recommended = (
        "derive-conflicting-events-from-local-monotonic-grid"
        if all_single_source
        else "score-observed-source-paths-against-local-order"
        if any_multi_source
        else "inspect-missing-observation-provenance"
    )

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-conflicting-observed-timing-source-provenance",
        "passed": len(rows) == len(conflict_keys) and len(rows) > 0,
        "conflictEndpointCount": len(rows),
        "singleSourceEndpointCount": single_source_count,
        "multiSourceEndpointCount": multi_source_count,
        "uniqueTimingSourcePathCount": len(unique_paths),
        "uniqueTimingSourcePaths": unique_paths,
        "sourcePathObservationCounts": source_path_counts,
        "rows": rows,
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
        "conflictEndpointCount": len(rows),
        "singleSourceEndpointCount": single_source_count,
        "multiSourceEndpointCount": multi_source_count,
        "uniqueTimingSourcePathCount": len(unique_paths),
        "recommendedNextAction": recommended,
        "timingRepairApplied": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 CONFLICTING OBSERVED TIMING SOURCES V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Conflict endpoints:", len(rows))
    print("Single-source endpoints:", single_source_count)
    print("Multi-source endpoints:", multi_source_count)
    print("Unique timing source paths:", len(unique_paths))
    print("Recommended next action:", recommended)
    for row in rows:
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"resolved={row['resolvedStartSeconds']} "
            f"observations={row['timingObservationCount']} "
            f"spread={row['timingObservationSpreadSeconds']}"
        )
        for observation in row["observations"]:
            print(
                f"  path={observation['path']} row={observation['rowIndex']} "
                f"start={observation['startSeconds']}"
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
