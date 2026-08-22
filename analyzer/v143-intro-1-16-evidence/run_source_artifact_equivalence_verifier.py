#!/usr/bin/env python3
"""Run the static V143 equivalence verifier with audit-safe corrections.

The first verifier revision had two verifier-only assumptions that do not match the
historical producer contract:

1. ``value or -1`` maps the valid integer grid step 0 to -1.
2. It assumed measures 1-16 must always contain 16 complete steps each. Historical
   ``build_subdivision_grid`` preserves the detected bar phase, so a take whose
   first beat is late in measure 1 legitimately has a partial opening measure.

Keep the original evidence verifier immutable for audit history. Patch only those
verifier assumptions in memory, then execute the corrected verifier. No preserved
artifact, historical source, model, threshold, or production file is modified.
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
VERIFIER = HERE / "verify_source_artifact_equivalence.py"

source = VERIFIER.read_text(encoding="utf-8")

old_zero_step = 'int(row.get("step") or -1)'
new_zero_step = 'int(row.get("step")) if row.get("step") is not None else -1'
if source.count(old_zero_step) != 1:
    raise RuntimeError(
        f"Expected exactly one zero-step parser to patch, found {source.count(old_zero_step)}"
    )
source = source.replace(old_zero_step, new_zero_step)

old_grid_contract = '''    expected_grid_keys = {(measure, step) for measure in range(1, 17) for step in range(16)}
    grid_keys: set[tuple[int, int]] = set()
    global_steps: set[int] = set()
    for index, row in enumerate(grid):
        require(isinstance(row, dict), f"grid row {index} is not an object")
        key = (int(row.get("measure") or 0), int(row.get("step")) if row.get("step") is not None else -1)
        require(key not in grid_keys, f"duplicate grid key {key}")
        grid_keys.add(key)
        global_steps.add(int(row.get("globalStep")))
        as_finite_float(row.get("timeSeconds"), f"grid[{index}].timeSeconds")
    require(grid_keys == expected_grid_keys, f"raw grid keys differ from exact 16x16 contract; missing={sorted(expected_grid_keys-grid_keys)[:8]} extra={sorted(grid_keys-expected_grid_keys)[:8]}")
    require(len(global_steps) == 256, "raw grid globalStep values are not unique")
'''

new_grid_contract = '''    # Reconstruct the exact grid written by the historical producer from the
    # cache's own reference-free timing payload. The source does not synthesize a
    # complete opening measure: firstBeatInMeasure preserves detected bar phase.
    timing = raw.get("timing") or {}
    beat_values = timing.get("beatTimes") or []
    require(isinstance(beat_values, list) and len(beat_values) >= 2, "raw timing beatTimes missing/too short")
    beats = [
        as_finite_float(value, f"timing.beatTimes[{index}]")
        for index, value in enumerate(beat_values)
    ]
    for left, right in zip(beats[:-1], beats[1:]):
        require(right > left, "raw timing beatTimes are not strictly increasing")
    first_beat = int(timing.get("firstBeatInMeasure"))
    require(0 <= first_beat < 4, f"raw firstBeatInMeasure outside 4/4 bar: {first_beat}")

    intervals = [right - left for left, right in zip(beats[:-1], beats[1:])]
    tail_interval = float(median(intervals[-min(4, len(intervals)) :]))
    expected_grid: list[dict[str, Any]] = []
    global_step = 0
    for beat_index, beat_time in enumerate(beats):
        interval = intervals[beat_index] if beat_index < len(intervals) else tail_interval
        absolute_beat = first_beat + beat_index
        measure = 1 + absolute_beat // 4
        beat_in_measure = absolute_beat % 4
        for subdivision in range(4):
            step = beat_in_measure * 4 + subdivision
            time_seconds = beat_time + interval * subdivision / 4.0
            if 1 <= measure <= 16:
                expected_grid.append(
                    {
                        "globalStep": global_step,
                        "measure": measure,
                        "step": step,
                        "timeSeconds": float(time_seconds),
                    }
                )
            global_step += 1

    require(
        len(grid) == len(expected_grid),
        f"raw grid row count {len(grid)} != historical timing reconstruction {len(expected_grid)}",
    )
    grid_keys: set[tuple[int, int]] = set()
    global_steps: set[int] = set()
    for index, (row, expected) in enumerate(zip(grid, expected_grid)):
        require(isinstance(row, dict), f"grid row {index} is not an object")
        measure = int(row.get("measure")) if row.get("measure") is not None else 0
        step = int(row.get("step")) if row.get("step") is not None else -1
        key = (measure, step)
        require(key not in grid_keys, f"duplicate grid key {key}")
        grid_keys.add(key)
        actual_global = int(row.get("globalStep"))
        require(actual_global not in global_steps, f"duplicate grid globalStep {actual_global}")
        global_steps.add(actual_global)
        actual_time = as_finite_float(row.get("timeSeconds"), f"grid[{index}].timeSeconds")
        require(measure == int(expected["measure"]), f"grid row {index} measure differs from historical timing reconstruction")
        require(step == int(expected["step"]), f"grid row {index} step differs from historical timing reconstruction")
        require(actual_global == int(expected["globalStep"]), f"grid row {index} globalStep differs from historical timing reconstruction")
        require(
            math.isclose(actual_time, float(expected["timeSeconds"]), abs_tol=1e-12),
            f"grid row {index} timeSeconds differs from historical timing reconstruction",
        )
    require(len(global_steps) == len(grid), "raw grid globalStep values are not unique")
'''

if source.count(old_grid_contract) != 1:
    raise RuntimeError(
        "Expected exactly one full-grid verifier assumption to patch, "
        f"found {source.count(old_grid_contract)}"
    )
source = source.replace(old_grid_contract, new_grid_contract)

namespace = {
    "__file__": str(VERIFIER),
    "__name__": "__main__",
}
exec(compile(source, str(VERIFIER), "exec"), namespace, namespace)
