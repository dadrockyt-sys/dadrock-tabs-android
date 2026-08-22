#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

import v143_reserve_contextual_prune_predict as predictor


def merge_reference_free_context_partial_tail() -> tuple[dict[int, list[dict[str, Any]]], dict[tuple[int, int], float]]:
    """Merge the sealed 81-113 reference-free context.

    Measures 81-112 must retain a complete 16-step grid. The captured source
    audio ends halfway through measure 113, so the only accepted partial tail
    is measure 113 steps 0-7. No missing interior grid slots are tolerated.
    """
    rows_by_measure: dict[int, list[dict[str, Any]]] = {}
    grid: dict[tuple[int, int], float] = {}
    group_offset = 0

    for path in (predictor.SECTION5_CACHE_PATH, predictor.RESERVE_CACHE_PATH):
        cache = predictor.load_json(path)
        if cache.get("referenceFree") is not True:
            raise RuntimeError(f"Cache is not referenceFree=true: {path}")
        if cache.get("professionalReferenceUsedByAnalyzer") is not False:
            raise RuntimeError(f"Cache does not assert professionalReferenceUsedByAnalyzer=false: {path}")
        if cache.get("professionalReferenceRequiredAtRuntime") is not False:
            raise RuntimeError(f"Cache unexpectedly requires professional reference at runtime: {path}")
        if cache.get("productionModified") is not False:
            raise RuntimeError(f"Cache unexpectedly marks productionModified=true: {path}")

        for raw in cache.get("rows", []) or []:
            if not isinstance(raw, dict):
                continue
            measure = int(raw.get("measure") or raw.get("nearestMeasure") or 0)
            if measure not in predictor.CONTEXT_MEASURES:
                continue
            row = dict(raw)
            row["measure"] = measure
            if row.get("onsetGroupId") is not None:
                row["onsetGroupId"] = int(row.get("onsetGroupId") or 0) + group_offset
            rows_by_measure.setdefault(measure, []).append(row)

        for raw in cache.get("grid", []) or []:
            if not isinstance(raw, dict):
                continue
            measure = int(raw.get("measure") or 0)
            step = int(raw.get("step") or 0)
            if measure not in predictor.CONTEXT_MEASURES or not 0 <= step < 16:
                continue
            key = (measure, step)
            time_seconds = float(raw.get("timeSeconds") or 0.0)
            if key in grid and abs(grid[key] - time_seconds) > 1e-6:
                raise RuntimeError(f"Conflicting grid time for {key}: {grid[key]} vs {time_seconds}")
            grid[key] = time_seconds

        group_offset += 1_000_000

    for values in rows_by_measure.values():
        values.sort(
            key=lambda row: (
                float(row.get("onsetTime") or 0.0),
                int(row.get("onsetGroupId") or 0),
            )
        )

    # Strictly require every grid slot through the last complete measure.
    missing_complete = [
        (measure, step)
        for measure in range(81, 113)
        for step in range(16)
        if (measure, step) not in grid
    ]
    if missing_complete:
        raise RuntimeError(f"81-112 context grid has unexpected holes: {missing_complete[:12]}")

    final_steps = sorted(step for measure, step in grid if measure == 113)
    expected_final_steps = list(range(8))
    if final_steps != expected_final_steps:
        raise RuntimeError(
            "Measure 113 partial-tail invariant changed: "
            f"actual={final_steps} expected={expected_final_steps}"
        )

    expected_grid_count = (32 * 16) + len(expected_final_steps)
    if len(grid) != expected_grid_count:
        raise RuntimeError(
            f"81-113 context grid count changed: {len(grid)} != {expected_grid_count}"
        )

    if set(rows_by_measure) != predictor.CONTEXT_MEASURES:
        missing_measures = sorted(predictor.CONTEXT_MEASURES - set(rows_by_measure))
        raise RuntimeError(f"81-113 reference-free rows missing measures: {missing_measures}")

    print("PARTIAL_FINAL_MEASURE_113_STEPS", final_steps)
    print("REFERENCE_FREE_CONTEXT_GRID_COUNT", len(grid))
    return rows_by_measure, grid


def main() -> None:
    predictor.merge_reference_free_context = merge_reference_free_context_partial_tail
    predictor.main()


if __name__ == "__main__":
    main()
