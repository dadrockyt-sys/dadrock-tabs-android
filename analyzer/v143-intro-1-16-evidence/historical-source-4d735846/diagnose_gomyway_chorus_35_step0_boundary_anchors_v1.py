from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

BRIDGE_PATH = PUBLIC / "gomyway-chorus-33-35-measure-step-timing-bridge-v1.json"
GRID_PATH = PUBLIC / "gomyway-chorus-35-step0-global-grid-timing-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-35-step0-boundary-anchor-diagnostic-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-35-step0-boundary-anchor-diagnostic-v1-manifest.json"

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


def median_and_mad(values: list[float]) -> tuple[float | None, float | None]:
    if not values:
        return None, None
    median = statistics.median(values)
    mad = statistics.median(abs(value - median) for value in values)
    return median, mad


def main() -> None:
    bridge = load(BRIDGE_PATH)
    grid = load(GRID_PATH)

    if bridge.get("passed") is not True:
        raise RuntimeError("Timing bridge is not green.")
    if grid.get("passed") is not True:
        raise RuntimeError("Global-grid diagnostic did not complete.")
    if grid.get("qualityGate") is not False:
        raise RuntimeError("This diagnostic is only for the failed two-anchor gate.")

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
    if previous is None or following is None:
        raise RuntimeError("Expected both boundary anchors.")

    # Estimate the outgoing tempo from the tail of measure 34 only.
    previous_measure_rows = [item for item in timed if item[0] == 34]
    previous_intervals: list[float] = []
    for left, right in zip(previous_measure_rows, previous_measure_rows[1:]):
        step_gap = right[1] - left[1]
        time_gap = right[2] - left[2]
        if step_gap > 0 and time_gap > 0:
            previous_intervals.append(time_gap / step_gap)

    # Estimate the incoming tempo from measure 35 only, avoiding the section
    # boundary discontinuity that contaminated the global two-anchor estimate.
    following_measure_rows = [item for item in timed if item[0] == 35]
    following_intervals: list[float] = []
    for left, right in zip(following_measure_rows, following_measure_rows[1:]):
        step_gap = right[1] - left[1]
        time_gap = right[2] - left[2]
        if step_gap > 0 and time_gap > 0:
            following_intervals.append(time_gap / step_gap)

    previous_rate, previous_mad = median_and_mad(previous_intervals)
    following_rate, following_mad = median_and_mad(following_intervals)

    previous_gap = target_abs - absolute_step(previous[0], previous[1])
    following_gap = absolute_step(following[0], following[1]) - target_abs

    previous_estimate = (
        previous[2] + previous_gap * previous_rate
        if previous_rate is not None else None
    )
    following_estimate = (
        following[2] - following_gap * following_rate
        if following_rate is not None else None
    )

    candidates = [
        {
            "direction": "forward-from-measure-34-tail",
            "anchorMeasure": previous[0],
            "anchorStep": previous[1],
            "anchorStartSeconds": previous[2],
            "localIntervalCount": len(previous_intervals),
            "localMedianSecondsPerStep": previous_rate,
            "localMadSeconds": previous_mad,
            "estimatedStartSeconds": previous_estimate,
            "qualityGate": bool(
                previous_estimate is not None
                and len(previous_intervals) >= 2
                and previous_mad is not None
                and previous_mad <= 0.03
            ),
        },
        {
            "direction": "backward-from-measure-35-body",
            "anchorMeasure": following[0],
            "anchorStep": following[1],
            "anchorStartSeconds": following[2],
            "localIntervalCount": len(following_intervals),
            "localMedianSecondsPerStep": following_rate,
            "localMadSeconds": following_mad,
            "estimatedStartSeconds": following_estimate,
            "qualityGate": bool(
                following_estimate is not None
                and len(following_intervals) >= 2
                and following_mad is not None
                and following_mad <= 0.03
            ),
        },
    ]

    passing = [candidate for candidate in candidates if candidate["qualityGate"]]
    recommended = (
        "use-measure-35-local-backward-estimate"
        if candidates[1]["qualityGate"] and not candidates[0]["qualityGate"]
        else "use-measure-34-local-forward-estimate"
        if candidates[0]["qualityGate"] and not candidates[1]["qualityGate"]
        else "compare-local-anchor-estimates"
        if len(passing) == 2
        else "derive-boundary-from-audio-onset"
    )

    local_values = [
        float(candidate["estimatedStartSeconds"])
        for candidate in passing
        if candidate["estimatedStartSeconds"] is not None
    ]
    local_spread = (
        max(local_values) - min(local_values)
        if len(local_values) > 1 else 0.0
    )

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-chorus-boundary-anchor-comparison",
        "passed": True,
        "targetMeasure": TARGET_MEASURE,
        "targetStep": TARGET_STEP,
        "globalEstimateSpreadSeconds": grid.get("estimateSpreadSeconds"),
        "localCandidates": [
            {
                **candidate,
                "localMedianSecondsPerStep": (
                    round(float(candidate["localMedianSecondsPerStep"]), 6)
                    if candidate["localMedianSecondsPerStep"] is not None else None
                ),
                "localMadSeconds": (
                    round(float(candidate["localMadSeconds"]), 6)
                    if candidate["localMadSeconds"] is not None else None
                ),
                "estimatedStartSeconds": (
                    round(float(candidate["estimatedStartSeconds"]), 6)
                    if candidate["estimatedStartSeconds"] is not None else None
                ),
            }
            for candidate in candidates
        ],
        "passingLocalCandidateCount": len(passing),
        "passingLocalEstimateSpreadSeconds": round(local_spread, 6),
        "recommendedNextAction": recommended,
        "boundaryTimingResolved": False,
        "audioTechniqueSupportClaimed": False,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }

    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "passingLocalCandidateCount": len(passing),
        "recommendedNextAction": recommended,
        "boundaryTimingResolved": False,
        "audioTechniqueSupportClaimed": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 35 STEP 0 BOUNDARY ANCHOR DIAGNOSTIC V1 COMPLETE")
    print("Passed: True")
    print("Global estimate spread seconds:", output["globalEstimateSpreadSeconds"])
    for candidate in output["localCandidates"]:
        print(
            f"direction={candidate['direction']} "
            f"intervals={candidate['localIntervalCount']} "
            f"medianStep={candidate['localMedianSecondsPerStep']} "
            f"mad={candidate['localMadSeconds']} "
            f"estimate={candidate['estimatedStartSeconds']} "
            f"qualityGate={candidate['qualityGate']}"
        )
    print("Passing local candidates:", len(passing))
    print("Passing local estimate spread seconds:", output["passingLocalEstimateSpreadSeconds"])
    print("Recommended next action:", recommended)
    print("Boundary timing resolved: False")
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
