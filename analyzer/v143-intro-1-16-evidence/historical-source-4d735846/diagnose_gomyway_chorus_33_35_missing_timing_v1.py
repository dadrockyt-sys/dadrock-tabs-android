from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

BRIDGE_PATH = PUBLIC / "gomyway-chorus-33-35-measure-step-timing-bridge-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-missing-timing-diagnostic-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-missing-timing-diagnostic-v1-manifest.json"


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
    if bridge.get("passed") is not True:
        raise RuntimeError("Timing bridge is not green.")
    if int(bridge.get("chorusEventCount", -1)) != 30:
        raise RuntimeError("Expected 30 chorus bridge rows.")

    rows = [row for row in bridge.get("rows", []) if isinstance(row, dict)]
    timed_by_measure: dict[int, list[tuple[int, float]]] = {}
    for row in rows:
        measure = integer(row.get("measureNumber"))
        step = integer(row.get("quantizedStep"))
        start = number(row.get("resolvedStartSeconds"))
        if measure is None or step is None or start is None:
            continue
        timed_by_measure.setdefault(measure, []).append((step, start))

    for measure in timed_by_measure:
        timed_by_measure[measure].sort()

    missing_rows: list[dict[str, Any]] = []
    recoverable_count = 0

    for row in rows:
        if row.get("resolvedStartSeconds") is not None:
            continue

        measure = integer(row.get("measureNumber"))
        step = integer(row.get("quantizedStep"))
        neighbors = timed_by_measure.get(measure or -1, [])

        previous = None
        following = None
        if step is not None:
            for candidate_step, candidate_time in neighbors:
                if candidate_step < step:
                    previous = (candidate_step, candidate_time)
                elif candidate_step > step and following is None:
                    following = (candidate_step, candidate_time)

        interpolation = None
        interpolation_reason = "insufficient-neighbor-timing"
        if previous is not None and following is not None and step is not None:
            previous_step, previous_time = previous
            following_step, following_time = following
            step_span = following_step - previous_step
            if step_span > 0:
                fraction = (step - previous_step) / step_span
                estimate = previous_time + fraction * (following_time - previous_time)
                interpolation = round(estimate, 6)
                interpolation_reason = "bounded-linear-interpolation"
                recoverable_count += 1

        missing_rows.append({
            "sourceEventIndex": row.get("sourceEventIndex"),
            "measureNumber": measure,
            "quantizedStep": step,
            "notes": row.get("notes", []),
            "noteMultiplicity": row.get("noteMultiplicity", 0),
            "isSingleNoteTechniqueCandidate": bool(
                row.get("isSingleNoteTechniqueCandidate")
            ),
            "previousTimedNeighbor": (
                {"quantizedStep": previous[0], "startSeconds": previous[1]}
                if previous is not None else None
            ),
            "followingTimedNeighbor": (
                {"quantizedStep": following[0], "startSeconds": following[1]}
                if following is not None else None
            ),
            "interpolatedStartSeconds": interpolation,
            "interpolationReason": interpolation_reason,
            "interpolationApplied": False,
            "audioTechniqueSupportClaimed": False,
            "readOnly": True,
        })

    missing_count = len(missing_rows)
    unresolved_count = missing_count - recoverable_count
    ready_for_interpolation_bridge = missing_count > 0 and unresolved_count == 0

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-missing-chorus-timing-diagnostic",
        "passed": missing_count == int(bridge.get("eventsWithoutTimingCount", -1)),
        "missingTimingEventCount": missing_count,
        "boundedInterpolationCandidateCount": recoverable_count,
        "unresolvedTimingEventCount": unresolved_count,
        "rows": missing_rows,
        "recommendedNextAction": (
            "build-read-only-bounded-interpolation-bridge"
            if ready_for_interpolation_bridge
            else "derive-missing-boundary-timing-from-global-grid"
        ),
        "readyForBoundedInterpolationBridge": ready_for_interpolation_bridge,
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
        "missingTimingEventCount": missing_count,
        "boundedInterpolationCandidateCount": recoverable_count,
        "unresolvedTimingEventCount": unresolved_count,
        "recommendedNextAction": output["recommendedNextAction"],
        "audioTechniqueSupportClaimed": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 MISSING TIMING DIAGNOSTIC V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Missing timing events:", missing_count)
    print("Bounded interpolation candidates:", recoverable_count)
    print("Unresolved timing events:", unresolved_count)
    print("Recommended next action:", output["recommendedNextAction"])
    for row in missing_rows:
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"singleNote={row['isSingleNoteTechniqueCandidate']} "
            f"interpolatedStart={row['interpolatedStartSeconds']} "
            f"reason={row['interpolationReason']}"
        )
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
