from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
WINDOW_PLAN_PATH = PUBLIC / "gomyway-chorus-33-35-audio-technique-window-plan-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-timing-source-inventory-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-timing-source-inventory-v1-manifest.json"

CHORUS_MEASURES = {33, 34, 35}
TIME_KEYS = (
    "startTime", "start_time", "start", "time", "onsetTime", "onset_time", "onset",
    "endTime", "end_time", "end", "offsetTime", "offset_time", "offset",
    "duration", "durationSeconds", "duration_seconds",
)
MEASURE_KEYS = ("measureNumber", "measure")
STEP_KEYS = ("quantizedStep", "step")


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


def rows_from(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, list):
        found.extend(item for item in value if isinstance(item, dict))
    elif isinstance(value, dict):
        for nested in value.values():
            if isinstance(nested, list):
                found.extend(item for item in nested if isinstance(item, dict))
    return found


def measure_of(row: dict[str, Any]) -> int | None:
    for key in MEASURE_KEYS:
        value = integer(row.get(key))
        if value is not None:
            return value
    return None


def step_of(row: dict[str, Any]) -> int | None:
    for key in STEP_KEYS:
        value = integer(row.get(key))
        if value is not None:
            return value
    return None


def timing_values(row: dict[str, Any]) -> dict[str, Any]:
    return {key: row[key] for key in TIME_KEYS if key in row and row[key] is not None}


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    plan = load(WINDOW_PLAN_PATH)

    if plan.get("passed") is not True:
        raise RuntimeError("Audio technique window plan is not green.")
    if int(plan.get("timedChorusEventCount", -1)) != 0:
        raise RuntimeError("This inventory is only for the zero-timed-event recovery path.")

    protected_paths = {SOURCE_PATH.resolve(), WINDOW_PLAN_PATH.resolve()}
    candidates: list[dict[str, Any]] = []

    for path in sorted(PUBLIC.glob("gomyway*.json")):
        if path.resolve() in protected_paths or path in {OUTPUT_PATH, MANIFEST_PATH}:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        rows = rows_from(payload)
        matching_rows: list[dict[str, Any]] = []
        for row_index, row in enumerate(rows):
            measure = measure_of(row)
            if measure not in CHORUS_MEASURES:
                continue
            values = timing_values(row)
            if not values:
                continue
            matching_rows.append({
                "rowIndex": row_index,
                "measureNumber": measure,
                "quantizedStep": step_of(row),
                "timing": values,
            })

        top_level_timing = {
            key: payload[key]
            for key in TIME_KEYS
            if isinstance(payload, dict) and key in payload and payload[key] is not None
        }
        if matching_rows or top_level_timing:
            candidates.append({
                "path": str(path.relative_to(ROOT)),
                "matchingTimedRowCount": len(matching_rows),
                "rowsWithMeasureAndStep": sum(
                    1 for row in matching_rows if row["quantizedStep"] is not None
                ),
                "topLevelTiming": top_level_timing,
                "sampleRows": matching_rows[:12],
                "readOnly": True,
            })

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    usable = [
        item for item in candidates
        if item["matchingTimedRowCount"] > 0 and item["rowsWithMeasureAndStep"] > 0
    ]

    output = {
        "schemaVersion": 1,
        "inventoryType": "read-only-chorus-timing-source-inventory",
        "passed": source_unchanged,
        "chorusMeasures": sorted(CHORUS_MEASURES),
        "candidateFileCount": len(candidates),
        "usableMeasureStepTimingSourceCount": len(usable),
        "candidates": candidates,
        "recommendedNextAction": (
            "build-read-only-measure-step-timing-bridge"
            if usable else
            "derive-section-timing-from-audio-or-existing-global-grid"
        ),
        "audioTechniqueSupportClaimed": False,
        "protectedSourceEventCount": int(plan.get("protectedSourceEventCount", -1)),
        "protectedSourceHashBefore": source_hash_before,
        "protectedSourceHashAfter": source_hash_after,
        "protectedSourceHashUnchanged": source_unchanged,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }

    manifest = {
        "schemaVersion": 1,
        "passed": output["passed"],
        "candidateFileCount": len(candidates),
        "usableMeasureStepTimingSourceCount": len(usable),
        "recommendedNextAction": output["recommendedNextAction"],
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "sourceEventsModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 TIMING SOURCE INVENTORY V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Candidate timing files:", len(candidates))
    print("Usable measure/step timing sources:", len(usable))
    print("Recommended next action:", output["recommendedNextAction"])
    print("Audio technique support claimed: False")
    print("Protected source event count:", output["protectedSourceEventCount"])
    print("Protected source hash unchanged:", source_unchanged)
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
