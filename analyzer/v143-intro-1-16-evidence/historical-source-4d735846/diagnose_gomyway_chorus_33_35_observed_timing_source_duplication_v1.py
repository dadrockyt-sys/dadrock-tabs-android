from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

PROVENANCE_PATH = PUBLIC / "gomyway-chorus-33-35-conflicting-observed-timing-sources-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-observed-timing-source-duplication-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-observed-timing-source-duplication-v1-manifest.json"


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


def integer(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def observation_rows(endpoint: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("observations", "timingSources", "sources"):
        rows = endpoint.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def provenance_rows(provenance: dict[str, Any]) -> list[dict[str, Any]]:
    # The provenance diagnostic currently writes endpoint records under
    # top-level "rows". Keep compatibility with earlier candidate names.
    for key in ("rows", "endpoints", "conflictEndpoints"):
        rows = provenance.get(key)
        if isinstance(rows, list):
            selected = [row for row in rows if isinstance(row, dict)]
            if selected:
                return selected
    return []


def main() -> None:
    provenance = load(PROVENANCE_PATH)
    if provenance.get("passed") is not True:
        raise RuntimeError("Observed timing provenance diagnostic is not green.")

    endpoints = provenance_rows(provenance)
    expected_count = integer(provenance.get("conflictEndpointCount"))
    if not endpoints:
        raise RuntimeError("No conflict endpoints were found in provenance output.")
    if expected_count is not None and len(endpoints) != expected_count:
        raise RuntimeError(
            f"Expected {expected_count} provenance endpoints, found {len(endpoints)}."
        )

    rows: list[dict[str, Any]] = []
    duplicate_observation_count = 0
    path_imbalanced_count = 0

    for endpoint in endpoints:
        measure = integer(endpoint.get("measureNumber"))
        step = integer(endpoint.get("quantizedStep"))
        observations = observation_rows(endpoint)

        grouped: dict[str, list[float]] = {}
        for observation in observations:
            path = str(observation.get("path", "unknown"))
            start = number(
                observation.get(
                    "startSeconds",
                    observation.get("resolvedStartSeconds"),
                )
            )
            if start is None:
                continue
            grouped.setdefault(path, []).append(start)

        path_rows: list[dict[str, Any]] = []
        raw_count = sum(len(values) for values in grouped.values())
        unique_path_time_count = 0
        max_path_count = 0
        min_path_count = min((len(values) for values in grouped.values()), default=0)

        for path, values in sorted(grouped.items()):
            unique_values = sorted(set(values))
            unique_path_time_count += len(unique_values)
            max_path_count = max(max_path_count, len(values))
            path_rows.append({
                "path": path,
                "rawObservationCount": len(values),
                "uniqueTimestampCount": len(unique_values),
                "duplicateObservationCount": len(values) - len(unique_values),
                "pathMedianStartSeconds": round(statistics.median(values), 6),
                "uniqueStartSeconds": [round(value, 6) for value in unique_values],
            })

        duplicates = raw_count - unique_path_time_count
        duplicate_observation_count += duplicates
        path_imbalanced = bool(
            len(grouped) > 1
            and min_path_count > 0
            and max_path_count / min_path_count >= 2.0
        )
        if path_imbalanced:
            path_imbalanced_count += 1

        per_path_medians = [
            float(row["pathMedianStartSeconds"])
            for row in path_rows
        ]
        path_balanced_median = (
            statistics.median(per_path_medians)
            if per_path_medians else None
        )
        path_spread = (
            max(per_path_medians) - min(per_path_medians)
            if len(per_path_medians) > 1 else 0.0
        )

        rows.append({
            "measureNumber": measure,
            "quantizedStep": step,
            "rawObservationCount": raw_count,
            "uniqueSourcePathCount": len(grouped),
            "duplicateObservationCount": duplicates,
            "pathObservationCountsImbalanced": path_imbalanced,
            "pathBalancedMedianStartSeconds": (
                round(path_balanced_median, 6)
                if path_balanced_median is not None else None
            ),
            "pathMedianSpreadSeconds": round(path_spread, 6),
            "pathRows": path_rows,
            "timingRepairApplied": False,
            "readOnly": True,
        })

    all_endpoints_have_duplicates = all(
        int(row["duplicateObservationCount"]) > 0 for row in rows
    )
    any_path_disagreement = any(
        float(row["pathMedianSpreadSeconds"]) > 0.08 for row in rows
    )
    recommended = (
        "build-source-balanced-observed-timing-candidate"
        if duplicate_observation_count > 0 and not any_path_disagreement
        else "arbitrate-observed-timing-source-families-with-audio-onsets"
        if duplicate_observation_count > 0 and any_path_disagreement
        else "diagnose-observed-row-identity-mapping"
    )

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-observed-timing-source-duplication",
        "passed": len(rows) == len(endpoints) and len(rows) > 0,
        "conflictEndpointCount": len(rows),
        "duplicateObservationCount": duplicate_observation_count,
        "pathImbalancedEndpointCount": path_imbalanced_count,
        "allConflictEndpointsContainDuplicates": all_endpoints_have_duplicates,
        "sourcePathDisagreementAbove80ms": any_path_disagreement,
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
        "duplicateObservationCount": duplicate_observation_count,
        "pathImbalancedEndpointCount": path_imbalanced_count,
        "recommendedNextAction": recommended,
        "timingRepairApplied": False,
        "audioTechniqueSupportClaimed": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 OBSERVED TIMING SOURCE DUPLICATION V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Conflict endpoints:", len(rows))
    print("Duplicate observations:", duplicate_observation_count)
    print("Path-imbalanced endpoints:", path_imbalanced_count)
    print("All conflict endpoints contain duplicates:", all_endpoints_have_duplicates)
    print("Source path disagreement above 80 ms:", any_path_disagreement)
    print("Recommended next action:", recommended)
    for row in rows:
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"raw={row['rawObservationCount']} paths={row['uniqueSourcePathCount']} "
            f"duplicates={row['duplicateObservationCount']} "
            f"pathBalancedMedian={row['pathBalancedMedianStartSeconds']} "
            f"pathSpread={row['pathMedianSpreadSeconds']}"
        )
        for source in row["pathRows"]:
            print(
                f"  path={source['path']} raw={source['rawObservationCount']} "
                f"uniqueTimes={source['uniqueTimestampCount']} "
                f"median={source['pathMedianStartSeconds']}"
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
