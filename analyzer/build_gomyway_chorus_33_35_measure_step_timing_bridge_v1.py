from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
WINDOW_PLAN_PATH = PUBLIC / "gomyway-chorus-33-35-audio-technique-window-plan-v1.json"
INVENTORY_PATH = PUBLIC / "gomyway-chorus-33-35-timing-source-inventory-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-measure-step-timing-bridge-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-measure-step-timing-bridge-v1-manifest.json"

CHORUS_MEASURES = {33, 34, 35}
START_KEYS = (
    "startTime", "start_time", "start", "time",
    "onsetTime", "onset_time", "onset",
)
END_KEYS = (
    "endTime", "end_time", "end",
    "offsetTime", "offset_time", "offset",
)
DURATION_KEYS = ("duration", "durationSeconds", "duration_seconds")


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integer(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result >= 0.0 else None


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    # The protected source contains more than one list-valued representation.
    # Select exactly one canonical event collection instead of flattening every
    # list, which would double-count the protected 949 events.
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def evidence_rows(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, list):
        found.extend(item for item in value if isinstance(item, dict))
    elif isinstance(value, dict):
        for nested in value.values():
            if isinstance(nested, list):
                found.extend(item for item in nested if isinstance(item, dict))
    return found


def measure_of(row: dict[str, Any]) -> int | None:
    return integer(row.get("measureNumber", row.get("measure")))


def step_of(row: dict[str, Any]) -> int | None:
    return integer(row.get("quantizedStep", row.get("step")))


def first_number(row: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        value = number(row.get(key))
        if value is not None:
            return value
    return None


def timing_of(row: dict[str, Any]) -> tuple[float | None, float | None]:
    start = first_number(row, START_KEYS)
    end = first_number(row, END_KEYS)
    if end is None and start is not None:
        duration = first_number(row, DURATION_KEYS)
        if duration is not None:
            end = start + duration
    if start is not None and end is not None and end < start:
        end = None
    return start, end


def rounded(value: float | None) -> float | None:
    return round(value, 6) if value is not None else None


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source_payload = load(SOURCE_PATH)
    plan = load(WINDOW_PLAN_PATH)
    inventory = load(INVENTORY_PATH)

    if plan.get("passed") is not True:
        raise RuntimeError("Audio technique window plan is not green.")
    if inventory.get("passed") is not True:
        raise RuntimeError("Timing source inventory is not green.")
    if inventory.get("recommendedNextAction") != "build-read-only-measure-step-timing-bridge":
        raise RuntimeError("Timing inventory did not authorize the measure/step bridge.")
    if int(inventory.get("usableMeasureStepTimingSourceCount", 0)) < 1:
        raise RuntimeError("No usable measure/step timing source was found.")

    protected_rows = source_rows(source_payload)
    if len(protected_rows) != 949:
        raise RuntimeError(
            f"Expected 949 protected source events, found {len(protected_rows)}."
        )

    usable_paths = [
        ROOT / str(candidate["path"])
        for candidate in inventory.get("candidates", [])
        if isinstance(candidate, dict)
        and int(candidate.get("matchingTimedRowCount", 0)) > 0
        and int(candidate.get("rowsWithMeasureAndStep", 0)) > 0
    ]

    observations: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for path in usable_paths:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for row_index, row in enumerate(evidence_rows(payload)):
            measure = measure_of(row)
            step = step_of(row)
            if measure not in CHORUS_MEASURES or step is None:
                continue
            start, end = timing_of(row)
            if start is None:
                continue
            observations.setdefault((measure, step), []).append({
                "path": str(path.relative_to(ROOT)),
                "rowIndex": row_index,
                "startSeconds": start,
                "endSeconds": end,
            })

    bridge_rows: list[dict[str, Any]] = []
    timed_count = 0
    consensus_count = 0

    for plan_row in plan.get("rows", []):
        if not isinstance(plan_row, dict):
            continue
        measure = integer(plan_row.get("measureNumber"))
        step = integer(plan_row.get("quantizedStep"))
        if measure not in CHORUS_MEASURES or step is None:
            continue

        matching = observations.get((measure, step), [])
        starts = [float(item["startSeconds"]) for item in matching]
        ends = [
            float(item["endSeconds"])
            for item in matching
            if item.get("endSeconds") is not None
        ]
        resolved_start = statistics.median(starts) if starts else None
        resolved_end = statistics.median(ends) if ends else None
        if resolved_start is not None and resolved_end is None:
            resolved_end = resolved_start + 0.45

        spread = max(starts) - min(starts) if len(starts) > 1 else 0.0
        consensus = bool(starts and spread <= 0.08)
        if resolved_start is not None:
            timed_count += 1
        if consensus:
            consensus_count += 1

        analysis_start = max(0.0, resolved_start - 0.04) if resolved_start is not None else None
        analysis_end = resolved_end + 0.12 if resolved_end is not None else None

        bridge_rows.append({
            "sourceEventIndex": plan_row.get("sourceEventIndex"),
            "measureNumber": measure,
            "quantizedStep": step,
            "notes": plan_row.get("notes", []),
            "noteMultiplicity": plan_row.get("noteMultiplicity", 0),
            "isSingleNoteTechniqueCandidate": bool(
                plan_row.get("isSingleNoteTechniqueCandidate")
            ),
            "timingObservationCount": len(matching),
            "timingSources": matching,
            "resolvedStartSeconds": rounded(resolved_start),
            "resolvedEndSeconds": rounded(resolved_end),
            "analysisWindowStartSeconds": rounded(analysis_start),
            "analysisWindowEndSeconds": rounded(analysis_end),
            "startTimeSpreadSeconds": rounded(spread),
            "timingConsensusPassed": consensus,
            "audioTechniqueSupportClaimed": False,
            "readOnly": True,
        })

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    expected_rows = int(plan.get("chorusEventCount", -1))
    row_count_matches = len(bridge_rows) == expected_rows == 30
    all_rows_timed = timed_count == len(bridge_rows) == 30
    all_rows_consensus = consensus_count == len(bridge_rows) == 30
    ready = (
        source_unchanged
        and row_count_matches
        and all_rows_timed
        and all_rows_consensus
    )

    output = {
        "schemaVersion": 1,
        "bridgeType": "read-only-chorus-measure-step-to-audio-time",
        "passed": source_unchanged and row_count_matches,
        "usableTimingSourceCount": len(usable_paths),
        "chorusEventCount": len(bridge_rows),
        "timedChorusEventCount": timed_count,
        "consensusPassedEventCount": consensus_count,
        "eventsWithoutTimingCount": len(bridge_rows) - timed_count,
        "eventsWithoutTimingConsensusCount": len(bridge_rows) - consensus_count,
        "rows": bridge_rows,
        "audioTechniqueSupportClaimed": False,
        "professionalReferenceUsedAsTrainingLabelOnly": True,
        "professionalNotesCopiedIntoProtectedSource": False,
        "protectedSourceEventCount": len(protected_rows),
        "protectedSourceHashBefore": source_hash_before,
        "protectedSourceHashAfter": source_hash_after,
        "protectedSourceHashUnchanged": source_unchanged,
        "chorusEventCountMatchesWindowPlan": row_count_matches,
        "readyForAudioTechniqueFeatureExtraction": ready,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }

    manifest = {
        "schemaVersion": 1,
        "passed": output["passed"],
        "usableTimingSourceCount": len(usable_paths),
        "chorusEventCount": len(bridge_rows),
        "timedChorusEventCount": timed_count,
        "consensusPassedEventCount": consensus_count,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "readyForAudioTechniqueFeatureExtraction": ready,
        "sourceEventsModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 MEASURE/STEP TIMING BRIDGE V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Usable timing sources:", len(usable_paths))
    print("Chorus events bridged:", len(bridge_rows))
    print("Timed chorus events:", timed_count)
    print("Timing consensus passed events:", consensus_count)
    print("Events without timing:", len(bridge_rows) - timed_count)
    print("Events without timing consensus:", len(bridge_rows) - consensus_count)
    print("Audio technique support claimed: False")
    print("Protected source event count:", len(protected_rows))
    print("Protected source hash unchanged:", source_unchanged)
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for audio technique feature extraction:", ready)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not output["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
