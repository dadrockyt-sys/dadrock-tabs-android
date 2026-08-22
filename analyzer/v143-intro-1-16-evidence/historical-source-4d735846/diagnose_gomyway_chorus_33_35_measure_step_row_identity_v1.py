from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

ORDER_PATH = PUBLIC / "gomyway-chorus-33-35-source-family-local-order-v1.json"
PROVENANCE_PATH = PUBLIC / "gomyway-chorus-33-35-conflicting-observed-timing-sources-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-measure-step-row-identity-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-measure-step-row-identity-v1-manifest.json"

IDENTITY_KEYS = (
    "id",
    "eventId",
    "event_id",
    "sourceEventIndex",
    "sourceIndex",
    "candidateIndex",
    "noteIndex",
    "string",
    "stringIndex",
    "fret",
    "midi",
    "midiPitch",
    "pitch",
    "pitchClass",
    "voice",
    "track",
    "part",
)
START_KEYS = (
    "startTime",
    "start_time",
    "start",
    "time",
    "onsetTime",
    "onset_time",
    "onset",
)


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


def evidence_rows(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, list):
        found.extend(item for item in value if isinstance(item, dict))
    elif isinstance(value, dict):
        for nested in value.values():
            if isinstance(nested, list):
                found.extend(item for item in nested if isinstance(item, dict))
    return found


def first_number(row: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        value = number(row.get(key))
        if value is not None:
            return value
    return None


def compact_identity(row: dict[str, Any]) -> dict[str, Any]:
    identity = {
        key: row[key]
        for key in IDENTITY_KEYS
        if key in row and row[key] is not None
    }
    notes = row.get("notes")
    if isinstance(notes, list):
        identity["notes"] = notes
    return identity


def identity_signature(identity: dict[str, Any]) -> str:
    return json.dumps(identity, sort_keys=True, separators=(",", ":"), default=str)


def main() -> None:
    order = load(ORDER_PATH)
    provenance = load(PROVENANCE_PATH)

    if order.get("passed") is not True:
        raise RuntimeError("Source-family local-order diagnostic is not green.")
    if order.get("recommendedNextAction") != "inspect-measure-step-row-identity-mapping":
        raise RuntimeError("Local-order diagnostic did not authorize row-identity inspection.")
    if provenance.get("passed") is not True:
        raise RuntimeError("Observed timing provenance diagnostic is not green.")

    endpoint_rows = [
        row for row in provenance.get("rows", [])
        if isinstance(row, dict)
    ]
    expected_endpoint_count = int(provenance.get("conflictEndpointCount", -1))
    if len(endpoint_rows) != expected_endpoint_count or expected_endpoint_count < 1:
        raise RuntimeError("Conflict endpoint provenance count is inconsistent.")

    file_cache: dict[str, list[dict[str, Any]]] = {}
    results: list[dict[str, Any]] = []
    endpoints_with_multiple_identities = 0
    endpoints_with_same_identity_multiple_times = 0
    unresolved_observations = 0

    for endpoint in endpoint_rows:
        measure = integer(endpoint.get("measureNumber"))
        step = integer(endpoint.get("quantizedStep"))
        observation_results: list[dict[str, Any]] = []

        for observation in endpoint.get("observations", []):
            if not isinstance(observation, dict):
                continue
            path_text = str(observation.get("path", ""))
            row_index = integer(observation.get("rowIndex"))
            expected_start = number(observation.get("startSeconds"))
            path = ROOT / path_text

            if path_text not in file_cache:
                if not path.exists():
                    file_cache[path_text] = []
                else:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    file_cache[path_text] = evidence_rows(payload)

            rows = file_cache[path_text]
            source_row = (
                rows[row_index]
                if row_index is not None and 0 <= row_index < len(rows)
                else None
            )
            if source_row is None:
                unresolved_observations += 1
                observation_results.append({
                    "path": path_text,
                    "rowIndex": row_index,
                    "expectedStartSeconds": expected_start,
                    "rowResolved": False,
                })
                continue

            source_measure = integer(
                source_row.get("measureNumber", source_row.get("measure"))
            )
            source_step = integer(
                source_row.get("quantizedStep", source_row.get("step"))
            )
            actual_start = first_number(source_row, START_KEYS)
            identity = compact_identity(source_row)
            observation_results.append({
                "path": path_text,
                "rowIndex": row_index,
                "expectedStartSeconds": expected_start,
                "actualStartSeconds": actual_start,
                "sourceMeasureNumber": source_measure,
                "sourceQuantizedStep": source_step,
                "measureStepMatchesEndpoint": (
                    source_measure == measure and source_step == step
                ),
                "startMatchesObservation": (
                    actual_start is not None
                    and expected_start is not None
                    and abs(actual_start - expected_start) <= 0.000001
                ),
                "identity": identity,
                "identitySignature": identity_signature(identity),
                "rowResolved": True,
            })

        resolved = [row for row in observation_results if row.get("rowResolved")]
        signatures = {
            str(row.get("identitySignature"))
            for row in resolved
        }
        unique_times = {
            round(float(row["actualStartSeconds"]), 6)
            for row in resolved
            if row.get("actualStartSeconds") is not None
        }
        multiple_identities = len(signatures) > 1
        same_identity_multiple_times = len(signatures) == 1 and len(unique_times) > 1
        if multiple_identities:
            endpoints_with_multiple_identities += 1
        if same_identity_multiple_times:
            endpoints_with_same_identity_multiple_times += 1

        results.append({
            "measureNumber": measure,
            "quantizedStep": step,
            "observationCount": len(observation_results),
            "resolvedObservationCount": len(resolved),
            "uniqueIdentityCount": len(signatures),
            "uniqueTimestampCount": len(unique_times),
            "multipleDistinctRowIdentities": multiple_identities,
            "sameIdentityMappedToMultipleTimes": same_identity_multiple_times,
            "allRowsMatchEndpointMeasureStep": bool(resolved) and all(
                row.get("measureStepMatchesEndpoint") is True for row in resolved
            ),
            "allStartsMatchProvenance": bool(resolved) and all(
                row.get("startMatchesObservation") is True for row in resolved
            ),
            "observations": observation_results,
            "timingRepairApplied": False,
            "readOnly": True,
        })

    all_rows_resolved = unresolved_observations == 0
    all_measure_steps_match = all(
        row["allRowsMatchEndpointMeasureStep"] for row in results
    )
    recommended = (
        "separate-note-row-identities-before-timing-consensus"
        if endpoints_with_multiple_identities > 0
        else "deduplicate-same-identity-timing-observations"
        if endpoints_with_same_identity_multiple_times > 0
        else "inspect-timing-source-row-index-flattening"
        if not all_rows_resolved or not all_measure_steps_match
        else "derive-conflict-endpoints-from-local-monotonic-grid"
    )

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-measure-step-row-identity-mapping",
        "passed": len(results) == expected_endpoint_count,
        "conflictEndpointCount": len(results),
        "unresolvedObservationCount": unresolved_observations,
        "endpointsWithMultipleDistinctRowIdentities": endpoints_with_multiple_identities,
        "endpointsWithSameIdentityMappedToMultipleTimes": endpoints_with_same_identity_multiple_times,
        "allRowsResolved": all_rows_resolved,
        "allRowsMatchEndpointMeasureStep": all_measure_steps_match,
        "rows": results,
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
        "conflictEndpointCount": len(results),
        "unresolvedObservationCount": unresolved_observations,
        "endpointsWithMultipleDistinctRowIdentities": endpoints_with_multiple_identities,
        "endpointsWithSameIdentityMappedToMultipleTimes": endpoints_with_same_identity_multiple_times,
        "recommendedNextAction": recommended,
        "timingRepairApplied": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 MEASURE/STEP ROW IDENTITY V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Conflict endpoints:", len(results))
    print("Unresolved observations:", unresolved_observations)
    print("Endpoints with multiple distinct row identities:", endpoints_with_multiple_identities)
    print("Endpoints with same identity mapped to multiple times:", endpoints_with_same_identity_multiple_times)
    print("All rows resolved:", all_rows_resolved)
    print("All rows match endpoint measure/step:", all_measure_steps_match)
    print("Recommended next action:", recommended)
    for row in results:
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"observations={row['observationCount']} "
            f"identities={row['uniqueIdentityCount']} "
            f"times={row['uniqueTimestampCount']} "
            f"multipleIdentities={row['multipleDistinctRowIdentities']} "
            f"sameIdentityMultipleTimes={row['sameIdentityMappedToMultipleTimes']}"
        )
        for observation in row["observations"]:
            print(
                f"  path={observation.get('path')} row={observation.get('rowIndex')} "
                f"resolved={observation.get('rowResolved')} "
                f"start={observation.get('actualStartSeconds')} "
                f"measureStepMatch={observation.get('measureStepMatchesEndpoint')} "
                f"identity={observation.get('identity')}"
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
