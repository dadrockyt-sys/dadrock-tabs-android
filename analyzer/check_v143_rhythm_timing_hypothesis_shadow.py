#!/usr/bin/env python3
from __future__ import annotations

from v143_rhythm_timing_hypothesis_shadow import (
    score_four_way_bar_phase,
    summarize_grid_ambiguity,
    summarize_timing_hypothesis_shadow,
)


def main() -> None:
    accents = [0.20, 0.25, 1.00, 0.22] * 4
    phase = score_four_way_bar_phase(
        accents,
        current_downbeat_index_mod4=2,
    )
    assert phase["winnerDownbeatIndexMod4"] == 2
    assert phase["winnerFirstBeatInMeasure"] == 2
    assert phase["currentWinnerMatches"] is True
    assert phase["confidence"] > 0.5
    assert phase["phaseSelectedOrChanged"] is False

    grid = {
        (1, 0): 0.000,
        (1, 1): 0.125,
        (1, 2): 0.250,
        (1, 3): 0.375,
        (2, 0): 2.000,
        (2, 1): 2.125,
        (2, 2): 2.250,
        (2, 3): 2.375,
    }
    rows = [
        {
            "measure": 1,
            "onsetTime": 0.010,
            "stemSupportMax": 2,
            "sweepSupportMax": 4,
            "detectionCountSum": 8,
        },
        {
            "measure": 1,
            "onsetTime": 0.0625,
            "stemSupportMax": 2,
            "sweepSupportMax": 4,
            "detectionCountSum": 8,
        },
        {
            "measure": 2,
            "onsetTime": 2.245,
            "stemSupportMax": 2,
            "sweepSupportMax": 3,
            "detectionCountSum": 6,
        },
        {
            "measure": 2,
            "onsetTime": 2.180,
            "stemSupportMax": 1,
            "sweepSupportMax": 1,
            "detectionCountSum": 1,
        },
    ]
    ambiguity = summarize_grid_ambiguity(rows, grid)
    assert ambiguity["rowCount"] == 4
    assert ambiguity["strictRowCount"] == 3
    assert ambiguity["strictRows"]["ambiguousCount"] == 1
    assert ambiguity["strictRows"]["ambiguousFraction"] == 1.0 / 3.0
    assert ambiguity["mostAmbiguousStrictRows"][0]["nearestRunnerUpMarginSeconds"] == 0.0

    report = summarize_timing_hypothesis_shadow(
        accents,
        rows,
        grid,
        current_downbeat_index_mod4=2,
    )
    invariants = report["invariants"]
    assert invariants["tempoChanged"] is False
    assert invariants["barPhaseChanged"] is False
    assert invariants["attackTimingChanged"] is False
    assert invariants["candidateSelectionChanged"] is False
    assert invariants["pitchChanged"] is False
    assert invariants["professionalReferenceUsed"] is False
    assert invariants["runtimeLabelsRequired"] is False
    assert invariants["productionModified"] is False

    print("V143 rhythm timing hypothesis shadow proof passed")
    print(phase)
    print(ambiguity["strictRows"])


if __name__ == "__main__":
    main()
