from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

PLAN_PATH = PUBLIC / "gomyway-chorus-33-35-completed-timing-plan-v1.json"
IDENTITY_PATH = PUBLIC / "gomyway-chorus-33-35-measure-step-row-identity-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-identity-separated-onset-candidate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-identity-separated-onset-candidate-v1-manifest.json"


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
    plan = load(PLAN_PATH)
    identity = load(IDENTITY_PATH)

    if identity.get("passed") is not True:
        raise RuntimeError("Row-identity diagnostic is not green.")
    if identity.get("recommendedNextAction") != "separate-note-row-identities-before-timing-consensus":
        raise RuntimeError("Row-identity diagnostic did not authorize identity separation.")
    if int(identity.get("endpointsWithMultipleDistinctRowIdentities", 0)) < 1:
        raise RuntimeError("No multiple-identity endpoints were found.")

    plan_rows = [row for row in plan.get("rows", []) if isinstance(row, dict)]
    if len(plan_rows) != 30:
        raise RuntimeError("Expected 30 completed timing rows.")

    endpoint_candidates: dict[tuple[int | None, int | None], dict[str, Any]] = {}
    for endpoint in identity.get("rows", []):
        if not isinstance(endpoint, dict):
            continue
        key = (
            integer(endpoint.get("measureNumber")),
            integer(endpoint.get("quantizedStep")),
        )
        observations = [
            row for row in endpoint.get("observations", [])
            if isinstance(row, dict)
            and row.get("rowResolved") is True
            and row.get("measureStepMatchesEndpoint") is True
            and number(row.get("actualStartSeconds")) is not None
        ]
        if not observations:
            continue

        by_identity: dict[str, list[float]] = {}
        identity_payloads: dict[str, dict[str, Any]] = {}
        for observation in observations:
            signature = str(observation.get("identitySignature", ""))
            if not signature:
                signature = json.dumps(
                    observation.get("identity", {}),
                    sort_keys=True,
                    separators=(",", ":"),
                    default=str,
                )
            start = float(observation["actualStartSeconds"])
            by_identity.setdefault(signature, []).append(start)
            identity_payloads[signature] = observation.get("identity", {})

        identity_rows: list[dict[str, Any]] = []
        identity_medians: list[float] = []
        for signature, values in sorted(by_identity.items()):
            unique_values = sorted(set(round(value, 6) for value in values))
            median_start = statistics.median(unique_values)
            identity_medians.append(median_start)
            identity_rows.append({
                "identity": identity_payloads.get(signature, {}),
                "rawObservationCount": len(values),
                "uniqueTimestampCount": len(unique_values),
                "uniqueStartSeconds": unique_values,
                "identityMedianStartSeconds": round(median_start, 6),
            })

        # A measure/step denotes a rhythmic onset bucket. When distinct note rows
        # occupy that bucket, the event onset is the earliest identity onset;
        # later identities are retained as read-only strum/arpeggiation spread.
        selected_onset = min(identity_medians)
        spread = max(identity_medians) - min(identity_medians) if len(identity_medians) > 1 else 0.0
        endpoint_candidates[key] = {
            "measureNumber": key[0],
            "quantizedStep": key[1],
            "identityCount": len(identity_rows),
            "identityRows": identity_rows,
            "selectedOnsetSeconds": round(selected_onset, 6),
            "identityOnsetSpreadSeconds": round(spread, 6),
            "selectionRule": "earliest-distinct-identity-onset-for-rhythmic-step",
            "timingRepairAppliedToProtectedSource": False,
            "readOnly": True,
        }

    rows: list[dict[str, Any]] = []
    replacement_count = 0
    multiple_identity_replacement_count = 0
    for source_row in plan_rows:
        row = dict(source_row)
        key = (
            integer(row.get("measureNumber")),
            integer(row.get("quantizedStep")),
        )
        candidate = endpoint_candidates.get(key)
        if candidate is not None:
            row["originalResolvedStartSeconds"] = row.get("resolvedStartSeconds")
            row["resolvedStartSeconds"] = candidate["selectedOnsetSeconds"]
            row["timingSource"] = "identity-separated-earliest-onset"
            row["identitySeparatedReplacementApplied"] = True
            row["identityCount"] = candidate["identityCount"]
            row["identityOnsetSpreadSeconds"] = candidate["identityOnsetSpreadSeconds"]
            replacement_count += 1
            if int(candidate["identityCount"]) > 1:
                multiple_identity_replacement_count += 1
        else:
            row["identitySeparatedReplacementApplied"] = False
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
            "leftSource": left.get("timingSource"),
            "rightMeasure": right.get("measureNumber"),
            "rightStep": right.get("quantizedStep"),
            "rightTime": right_time,
            "rightSource": right.get("timingSource"),
            "deltaSeconds": round(right_time - left_time, 6),
        })

    monotonic = len(conflicts) == 0
    passed = len(rows) == 30 and replacement_count == int(identity.get("conflictEndpointCount", -1))
    ready = passed and monotonic

    output = {
        "schemaVersion": 1,
        "candidateType": "read-only-identity-separated-rhythmic-onset",
        "passed": passed,
        "chorusEventCount": len(rows),
        "identitySeparatedReplacementCount": replacement_count,
        "multipleIdentityReplacementCount": multiple_identity_replacement_count,
        "monotonicityConflictCount": len(conflicts),
        "strictlyMonotonicTiming": monotonic,
        "endpointCandidates": list(endpoint_candidates.values()),
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
        "passed": passed,
        "identitySeparatedReplacementCount": replacement_count,
        "multipleIdentityReplacementCount": multiple_identity_replacement_count,
        "monotonicityConflictCount": len(conflicts),
        "strictlyMonotonicTiming": monotonic,
        "readyForCompletedTimingPlanV2": ready,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 IDENTITY-SEPARATED ONSET CANDIDATE V1 COMPLETE")
    print("Passed:", passed)
    print("Chorus events:", len(rows))
    print("Identity-separated replacements:", replacement_count)
    print("Multiple-identity replacements:", multiple_identity_replacement_count)
    print("Monotonicity conflicts:", len(conflicts))
    print("Strictly monotonic timing:", monotonic)
    print("Ready for completed timing plan V2:", ready)
    for candidate in endpoint_candidates.values():
        print(
            f"measure={candidate['measureNumber']} step={candidate['quantizedStep']} "
            f"identities={candidate['identityCount']} "
            f"selectedOnset={candidate['selectedOnsetSeconds']} "
            f"spread={candidate['identityOnsetSpreadSeconds']}"
        )
    for conflict in conflicts:
        print(
            f"left=m{conflict['leftMeasure']}s{conflict['leftStep']} "
            f"time={conflict['leftTime']} source={conflict['leftSource']} "
            f"right=m{conflict['rightMeasure']}s{conflict['rightStep']} "
            f"time={conflict['rightTime']} source={conflict['rightSource']} "
            f"delta={conflict['deltaSeconds']}"
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

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
