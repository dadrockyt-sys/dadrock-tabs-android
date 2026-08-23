#!/usr/bin/env python3
from __future__ import annotations

from v143_contextual_prune_reference_free_carrier import _validate_section_grid


def _row(measure: int, step: int, index: int) -> dict[str, object]:
    return {
        "globalStep": index,
        "measure": measure,
        "step": step,
        "timeSeconds": index * 0.1,
    }


def _approved_shape() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    index = 0
    for measure in range(1, 114):
        if measure == 1:
            steps = range(12, 16)
        elif measure == 113:
            steps = range(0, 8)
        else:
            steps = range(16)
        for step in steps:
            rows.append(_row(measure, step, index))
            index += 1
    return rows


def _must_fail(rows: list[dict[str, object]], label: str) -> None:
    try:
        _validate_section_grid(rows, 1, 113)
    except RuntimeError:
        return
    raise AssertionError(f"Malformed boundary grid unexpectedly passed: {label}")


def main() -> None:
    rows = _approved_shape()
    assert len(rows) == 1788
    diagnostic = _validate_section_grid(rows, 1, 113)
    assert diagnostic["gridCount"] == 1788
    assert diagnostic["measureCount"] == 113
    assert diagnostic["firstMeasureStepStart"] == 12
    assert diagnostic["firstMeasureStepEnd"] == 15
    assert diagnostic["firstMeasureStepCount"] == 4
    assert diagnostic["lastMeasureStepStart"] == 0
    assert diagnostic["lastMeasureStepEnd"] == 7
    assert diagnostic["lastMeasureStepCount"] == 8
    assert diagnostic["interiorMeasuresFull"] is True
    assert diagnostic["boundaryPartialMeasuresAllowed"] is True
    assert diagnostic["syntheticBoundarySlotsAdded"] is False
    assert diagnostic["referenceFree"] is True

    broken_interior = [
        row for row in rows if not (row["measure"] == 50 and row["step"] == 7)
    ]
    _must_fail(broken_interior, "interior gap")

    broken_first = [
        row for row in rows if row["measure"] != 1
    ]
    broken_first.extend(
        _row(1, step, len(broken_first) + offset)
        for offset, step in enumerate(range(8, 12))
    )
    _must_fail(broken_first, "first boundary is not suffix")

    broken_last = [
        row for row in rows if row["measure"] != 113
    ]
    broken_last.extend(
        _row(113, step, len(broken_last) + offset)
        for offset, step in enumerate(range(4, 8))
    )
    _must_fail(broken_last, "last boundary is not prefix")

    duplicate = list(rows) + [dict(rows[0])]
    _must_fail(duplicate, "duplicate slot")

    one_measure = [_row(4, step, step) for step in range(5, 11)]
    one = _validate_section_grid(one_measure, 4, 4)
    assert one["gridCount"] == 6
    assert one["syntheticBoundarySlotsAdded"] is False

    print("V143 contextual-prune boundary grid proof passed")
    print(diagnostic)


if __name__ == "__main__":
    main()
