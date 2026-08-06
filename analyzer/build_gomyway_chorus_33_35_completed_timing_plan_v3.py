from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
PLAN_V2_PATH = PUBLIC / "gomyway-chorus-33-35-completed-timing-plan-v2.json"
ADAPTIVE_PATH = PUBLIC / "gomyway-chorus-35-step0-adaptive-boundary-onset-v3.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-completed-timing-plan-v3.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-completed-timing-plan-v3-manifest.json"

STEPS_PER_MEASURE = 16
TARGET_MEASURE = 35
TARGET_STEP = 0


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


def rounded(value: float | None) -> float | None:
    return round(value, 6) if value is not None else None


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    plan_v2 = load(PLAN_V2_PATH)
    adaptive = load(ADAPTIVE_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if int(plan_v2.get("chorusEventCount", -1)) != 30:
        raise RuntimeError("Completed timing plan V2 must contain 30 chorus events.")
    if int(plan_v2.get("stepsPerMeasure", -1)) != STEPS_PER_MEASURE:
        raise RuntimeError("Completed timing plan V2 must use 16-step ordering.")
    if adaptive.get("passed") is not True:
        raise RuntimeError("Adaptive boundary onset V3 did not complete.")
    if adaptive.get("qualityGate") is not True:
        raise RuntimeError("Adaptive boundary onset V3 quality gate is not green.")
    if adaptive.get("readyForCompletedTimingPlanV3") is not True:
        raise RuntimeError("Adaptive boundary onset V3 did not authorize plan V3.")

    replacement_time = number(adaptive.get("resolvedStartSeconds"))
    left_boundary = number(adaptive.get("leftBoundaryStartSeconds"))
    following_boundary = number(adaptive.get("followingBoundaryStartSeconds"))
    if replacement_time is None or left_boundary is None or following_boundary is None:
        raise RuntimeError("Adaptive boundary onset output is missing required timing values.")
    if not left_boundary < replacement_time < following_boundary:
        raise RuntimeError("Adaptive boundary onset does not preserve chronological order.")

    rows: list[dict[str, Any]] = []
    replacement_count = 0
    for source_row in plan_v2.get("rows", []):
        if not isinstance(source_row, dict):
            continue
        row = dict(source_row)
        measure = integer(row.get("measureNumber"))
        step = integer(row.get("quantizedStep"))
        if measure == TARGET_MEASURE and step == TARGET_STEP:
            row["completedTimingPlanV2StartSeconds"] = row.get("resolvedStartSeconds")
            row["resolvedStartSeconds"] = rounded(replacement_time)
            row["timingSource"] = "adaptive-boundary-audio-onset-v3"
            row["timingQualityGate"] = True
            row["adaptiveBoundaryReplacementApplied"] = True
            replacement_count += 1
        else:
            row["adaptiveBoundaryReplacementApplied"] = False
        row["readOnly"] = True
        rows.append(row)

    if replacement_count != 1:
        raise RuntimeError(
            f"Expected exactly one m35s0 replacement, found {replacement_count}."
        )

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
            "leftSource": left.get("timingSource"),
            "rightMeasure": right.get("measureNumber"),
            "rightStep": right.get("quantizedStep"),
            "rightTime": rounded(right_time),
            "rightSource": right.get("timingSource"),
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
    resolved_count = sum(number(row.get("resolvedStartSeconds")) is not None for row in rows)
    quality_count = sum(bool(row.get("timingQualityGate")) for row in rows)
    monotonic = len(conflicts) == 0
    target_row = next(
        (
            row for row in rows
            if integer(row.get("measureNumber")) == TARGET_MEASURE
            and integer(row.get("quantizedStep")) == TARGET_STEP
        ),
        None,
    )
    target_matches = bool(
        target_row
        and abs(float(target_row["resolvedStartSeconds"]) - replacement_time) <= 0.000001
    )

    ready = bool(
        source_unchanged
        and len(rows) == 30
        and duplicate_positions == 0
        and resolved_count == 30
        and quality_count == 30
        and replacement_count == 1
        and target_matches
        and monotonic
    )

    output = {
        "schemaVersion": 3,
        "planType": "read-only-completed-chorus-audio-technique-timing-with-adaptive-boundary",
        "passed": ready,
        "stepsPerMeasure": STEPS_PER_MEASURE,
        "chorusEventCount": len(rows),
        "adaptiveBoundaryReplacementCount": replacement_count,
        "adaptiveBoundaryResolvedStartSeconds": rounded(replacement_time),
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
        "schemaVersion": 3,
        "passed": ready,
        "stepsPerMeasure": STEPS_PER_MEASURE,
        "chorusEventCount": len(rows),
        "adaptiveBoundaryReplacementCount": replacement_count,
        "adaptiveBoundaryResolvedStartSeconds": rounded(replacement_time),
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

    print("GOMYWAY CHORUS 33-35 COMPLETED TIMING PLAN V3 COMPLETE")
    print("Passed:", ready)
    print("Steps per measure:", STEPS_PER_MEASURE)
    print("Chorus events:", len(rows))
    print("Adaptive boundary replacements:", replacement_count)
    print("Resolved measure 35 step 0 start:", rounded(replacement_time))
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
