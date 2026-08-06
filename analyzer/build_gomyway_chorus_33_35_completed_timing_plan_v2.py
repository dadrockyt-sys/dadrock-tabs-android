from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
PLAN_V1_PATH = PUBLIC / "gomyway-chorus-33-35-completed-timing-plan-v1.json"
SEMANTICS_PATH = PUBLIC / "gomyway-chorus-33-35-nonstandard-quantized-step-semantics-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-completed-timing-plan-v2.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-completed-timing-plan-v2-manifest.json"

STEPS_PER_MEASURE = 16


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
        return float(value)
    except (TypeError, ValueError):
        return None


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def absolute_step(measure: int, step: int) -> int:
    return (measure - 1) * STEPS_PER_MEASURE + step


def rounded(value: float | None) -> float | None:
    return round(value, 6) if value is not None else None


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    plan_v1 = load(PLAN_V1_PATH)
    semantics = load(SEMANTICS_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if int(plan_v1.get("chorusEventCount", -1)) != 30:
        raise RuntimeError("Completed timing plan V1 must contain 30 chorus events.")
    if semantics.get("passed") is not True:
        raise RuntimeError("Quantized-step semantics diagnostic is not green.")
    if semantics.get("recommendedNextAction") != "rebuild-completed-timing-plan-with-16-step-ordering":
        raise RuntimeError("Semantics diagnostic did not authorize 16-step ordering.")
    if int(semantics.get("withinMeasureConflictCount", -1)) != 0:
        raise RuntimeError("Within-measure timing conflicts remain unresolved.")

    rows: list[dict[str, Any]] = []
    for source_row in plan_v1.get("rows", []):
        if not isinstance(source_row, dict):
            continue
        row = dict(source_row)
        measure = integer(row.get("measureNumber"))
        step = integer(row.get("quantizedStep"))
        if measure is None or step is None:
            continue
        if step < 0 or step >= STEPS_PER_MEASURE:
            raise RuntimeError(
                f"Invalid 16-step position at measure {measure}, step {step}."
            )
        row["absoluteStepV1"] = row.get("absoluteStep")
        row["absoluteStep"] = absolute_step(measure, step)
        row["stepsPerMeasure"] = STEPS_PER_MEASURE
        row["orderingCorrection"] = "recomputed-from-16-step-measure-grid"
        row["readOnly"] = True
        rows.append(row)

    rows.sort(key=lambda row: int(row["absoluteStep"]))

    duplicate_positions = len(rows) - len({int(row["absoluteStep"]) for row in rows})
    conflicts: list[dict[str, Any]] = []
    for left, right in zip(rows, rows[1:]):
        left_time = number(left.get("resolvedStartSeconds"))
        right_time = number(right.get("resolvedStartSeconds"))
        if left_time is None or right_time is None or left_time < right_time:
            continue
        conflicts.append({
            "leftMeasure": left.get("measureNumber"),
            "leftStep": left.get("quantizedStep"),
            "leftTime": rounded(left_time),
            "rightMeasure": right.get("measureNumber"),
            "rightStep": right.get("quantizedStep"),
            "rightTime": rounded(right_time),
            "deltaSeconds": rounded(right_time - left_time),
        })

    for index, row in enumerate(rows):
        start = number(row.get("resolvedStartSeconds"))
        next_start = (
            number(rows[index + 1].get("resolvedStartSeconds"))
            if index + 1 < len(rows)
            else None
        )
        if start is None:
            end = None
        elif next_start is not None and next_start > start:
            end = next_start
        else:
            end = start + 0.45
        row["resolvedEndSeconds"] = rounded(end)
        row["analysisWindowStartSeconds"] = (
            rounded(max(0.0, start - 0.04)) if start is not None else None
        )
        row["analysisWindowEndSeconds"] = (
            rounded(end + 0.12) if end is not None else None
        )

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    resolved_count = sum(row.get("resolvedStartSeconds") is not None for row in rows)
    quality_count = sum(bool(row.get("timingQualityGate")) for row in rows)
    monotonic = len(conflicts) == 0
    ready = bool(
        source_unchanged
        and len(rows) == 30
        and duplicate_positions == 0
        and resolved_count == 30
        and quality_count == 30
        and monotonic
    )

    output = {
        "schemaVersion": 2,
        "planType": "read-only-completed-chorus-audio-technique-timing-16-step-ordering",
        "passed": ready,
        "stepsPerMeasure": STEPS_PER_MEASURE,
        "chorusEventCount": len(rows),
        "duplicateAbsolutePositionCount": duplicate_positions,
        "resolvedTimingCount": resolved_count,
        "timingQualityGatePassedCount": quality_count,
        "monotonicityConflictCount": len(conflicts),
        "strictlyMonotonicTiming": monotonic,
        "conflicts": conflicts,
        "rows": rows,
        "readyForAudioTechniqueFeatureExtraction": ready,
        "audioTimingEvidenceClaimed": True,
        "audioTechniqueSupportClaimed": False,
        "professionalReferenceUsedAsTrainingLabelOnly": True,
        "professionalNotesCopiedIntoProtectedSource": False,
        "protectedSourceEventCount": 949,
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
        "schemaVersion": 2,
        "passed": ready,
        "stepsPerMeasure": STEPS_PER_MEASURE,
        "chorusEventCount": len(rows),
        "duplicateAbsolutePositionCount": duplicate_positions,
        "resolvedTimingCount": resolved_count,
        "timingQualityGatePassedCount": quality_count,
        "monotonicityConflictCount": len(conflicts),
        "strictlyMonotonicTiming": monotonic,
        "readyForAudioTechniqueFeatureExtraction": ready,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 COMPLETED TIMING PLAN V2 COMPLETE")
    print("Passed:", ready)
    print("Steps per measure:", STEPS_PER_MEASURE)
    print("Chorus events:", len(rows))
    print("Duplicate absolute positions:", duplicate_positions)
    print("Resolved timings:", resolved_count)
    print("Timing quality gates passed:", quality_count)
    print("Monotonicity conflicts:", len(conflicts))
    print("Strictly monotonic timing:", monotonic)
    print("Protected source event count: 949")
    print("Protected source hash unchanged:", source_unchanged)
    print("Audio technique support claimed: False")
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for audio technique feature extraction:", ready)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
