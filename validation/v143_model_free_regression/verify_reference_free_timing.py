#!/usr/bin/env python3
"""Deterministic, model-free regression checks for V143 bar-phase selection."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyzer.v143_candidate_timing_adapter import build_subdivision_grid
from analyzer.v143_reference_free_timing import _bar_phase_from_accents


def _assert_phase(
    name: str,
    accents: list[float],
    *,
    expected_first_beat: int,
    expected_downbeat_phase: int,
    expected_first_step: int,
    expect_zero_confidence: bool = False,
) -> None:
    first_beat, downbeat_phase, confidence = _bar_phase_from_accents(
        np.asarray(accents, dtype=np.float64)
    )
    assert first_beat == expected_first_beat, (
        name,
        first_beat,
        expected_first_beat,
    )
    assert downbeat_phase == expected_downbeat_phase, (
        name,
        downbeat_phase,
        expected_downbeat_phase,
    )
    if expect_zero_confidence:
        assert confidence == 0.0, (name, confidence)

    grid = build_subdivision_grid(
        [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
        first_beat_in_measure=first_beat,
    )
    assert grid[0].measure == 1, (name, grid[0])
    assert grid[0].step == expected_first_step, (name, grid[0])


def main() -> int:
    # A tiny, inconsistent advantage for phase 1 must not rotate the entire
    # downstream grid. The old argmax-only behavior selected phase 1 here.
    _assert_phase(
        "ambiguous_nonzero_falls_back_to_phase_zero",
        [1.00, 1.02, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00],
        expected_first_beat=0,
        expected_downbeat_phase=0,
        expected_first_step=0,
        expect_zero_confidence=True,
    )

    # Strong, repeatable nonzero downbeat evidence is still honored.
    _assert_phase(
        "clear_phase_one_is_preserved",
        [1.0, 3.0, 1.0, 1.0] * 4,
        expected_first_beat=3,
        expected_downbeat_phase=1,
        expected_first_step=12,
    )
    _assert_phase(
        "clear_phase_two_is_preserved",
        [1.0, 1.0, 2.5, 1.0] * 4,
        expected_first_beat=2,
        expected_downbeat_phase=2,
        expected_first_step=8,
    )
    _assert_phase(
        "clear_phase_zero_stays_step_zero",
        [3.0, 1.0, 1.0, 1.0] * 4,
        expected_first_beat=0,
        expected_downbeat_phase=0,
        expected_first_step=0,
    )

    try:
        _bar_phase_from_accents(np.ones(7, dtype=np.float64))
    except ValueError:
        pass
    else:
        raise AssertionError("short beat sequences must still be rejected")

    print("PASS: V143 reference-free timing regressions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
