from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

BRIDGE_PATH = PUBLIC / "gomyway-chorus-33-35-measure-step-timing-bridge-v1.json"
DIAGNOSTIC_PATH = PUBLIC / "gomyway-chorus-33-35-missing-timing-diagnostic-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-35-step0-global-grid-timing-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-35-step0-global-grid-timing-v1-manifest.json"

TARGET_MEASURE = 35
TARGET_STEP = 0
STEPS_PER_MEASURE = 12


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


def absolute_step(measure: int, step: int) -> int:
    return (measure - 1) * STEPS_PER_MEASURE + step


def main() -> None:
    bridge = load(BRIDGE_PATH)
    diagnostic = load(DIAGNOSTIC_PATH)

    if bridge.get("passed") is not True:
        raise RuntimeError("Timing bridge is not green.")
    if diagnostic.get("passed") is not True:
        raise RuntimeError("Missing timing diagnostic is not green.")
    if diagnostic.get("recommendedNextAction") != "derive-missing-boundary-timing-from-global-grid":
        raise RuntimeError("Diagnostic did not authorize global-grid boundary recovery.")

    target_rows = [
        row for row in diagnostic.get("rows", [])
        if isinstance(row, dict)
        and integer(row.get("measureNumber")) == TARGET_MEASURE
        and integer(row.get("quantizedStep")) == TARGET_STEP
    ]
    if len(target_rows) != 1:
        raise RuntimeError("Expected exactly one unresolved measure 35 step 0 target.")
    if target_rows[0].get("interpolatedStartSeconds") is not None:
        raise RuntimeError("Measure 35 step 0 is no longer unresolved.")

    timed: list[tuple[int, int, float]] = []
    for row in bridge.get("rows", []):
        if not isinstance(row, dict):
            continue
        measure = integer(row.get("measureNumber"))
        step = integer(row.get("quantizedStep"))
        start = number(row.get("resolvedStartSeconds"))
        if measure is None or step is None or start is None:
            continue
        timed.append((measure, step, start))

    timed.sort(key=lambda item: absolute_step(item[0], item[1]))

    per_step_intervals: list[float] = []
    interval_rows: list[dict[str, Any]] = []
    for left, right in zip(timed, timed[1:]):
        left_abs = absolute_step(left[0], left[1])
        right_abs = absolute_step(right[0], right[1])
        step_gap = right_abs - left_abs
        time_gap = right[2] - left[2]
        if step_gap <= 0 or time_gap <= 0:
            continue
        per_step = time_gap / step_gap
        if 0.02 <= per_step <= 0.5:
            per_step_intervals.append(per_step)
            interval_rows.append({
                "fromMeasure": left[0],
                "fromStep": left[1],
                "toMeasure": right[0],
                "toStep": right[1],
                "stepGap": step_gap,
                "timeGapSeconds": round(time_gap, 6),
                "secondsPerStep": round(per_step, 6),
            })

    if len(per_step_intervals) < 3:
        raise RuntimeError("Insufficient global-grid intervals for boundary recovery.")

    median_step_seconds = statistics.median(per_step_intervals)
    mad = statistics.median(
        abs(value - median_step_seconds) for value in per_step_intervals
    )

    target_abs = absolute_step(TARGET_MEASURE, TARGET_STEP)
    previous = max(
        (item for item in timed if absolute_step(item[0], item[1]) < target_abs),
        key=lambda item: absolute_step(item[0], item[1]),
        default=None,
    )
    following = min(
        (item for item in timed if absolute_step(item[0], item[1]) > target_abs),
        key=lambda item: absolute_step(item[0], item[1]),
        default=None,
    )

    estimates: list[dict[str, Any]] = []
    if previous is not None:
        gap = target_abs - absolute_step(previous[0], previous[1])
        estimates.append({
            "direction": "forward-from-previous",
            "anchorMeasure": previous[0],
            "anchorStep": previous[1],
            "anchorStartSeconds": previous[2],
            "stepGap": gap,
            "estimatedStartSeconds": previous[2] + gap * median_step_seconds,
        })
    if following is not None:
        gap = absolute_step(following[0], following[1]) - target_abs
        estimates.append({
            "direction": "backward-from-following",
            "anchorMeasure": following[0],
            "anchorStep": following[1],
            "anchorStartSeconds": following[2],
            "stepGap": gap,
            "estimatedStartSeconds": following[2] - gap * median_step_seconds,
        })

    estimate_values = [float(item["estimatedStartSeconds"]) for item in estimates]
    resolved = statistics.median(estimate_values) if estimate_values else None
    estimate_spread = (
        max(estimate_values) - min(estimate_values)
        if len(estimate_values) > 1 else 0.0
    )

    quality_gate = bool(
        resolved is not None
        and len(estimates) >= 1
        and median_step_seconds > 0
        and mad <= 0.03
        and estimate_spread <= 0.08
    )

    output = {
        "schemaVersion": 1,
        "derivationType": "read-only-global-grid-boundary-timing",
        "passed": True,
        "targetMeasure": TARGET_MEASURE,
        "targetStep": TARGET_STEP,
        "usableIntervalCount": len(per_step_intervals),
        "medianSecondsPerStep": round(median_step_seconds, 6),
        "medianAbsoluteDeviationSeconds": round(mad, 6),
        "anchorEstimates": [
            {
                **item,
                "estimatedStartSeconds": round(float(item["estimatedStartSeconds"]), 6),
            }
            for item in estimates
        ],
        "estimateSpreadSeconds": round(estimate_spread, 6),
        "resolvedStartSeconds": round(resolved, 6) if resolved is not None else None,
        "qualityGate": quality_gate,
        "readyForReadOnlyTimingCompletion": quality_gate,
        "intervalRows": interval_rows,
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
        "targetMeasure": TARGET_MEASURE,
        "targetStep": TARGET_STEP,
        "qualityGate": quality_gate,
        "readyForReadOnlyTimingCompletion": quality_gate,
        "audioTechniqueSupportClaimed": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 35 STEP 0 GLOBAL GRID TIMING V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Usable grid intervals:", len(per_step_intervals))
    print("Median seconds per step:", output["medianSecondsPerStep"])
    print("Median absolute deviation:", output["medianAbsoluteDeviationSeconds"])
    print("Boundary anchor estimates:", len(estimates))
    print("Estimate spread seconds:", output["estimateSpreadSeconds"])
    print("Resolved measure 35 step 0 start:", output["resolvedStartSeconds"])
    print("Quality gate:", quality_gate)
    print("Ready for read-only timing completion:", quality_gate)
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
