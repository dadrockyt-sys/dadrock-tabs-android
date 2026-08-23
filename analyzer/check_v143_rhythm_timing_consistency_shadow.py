#!/usr/bin/env python3
from __future__ import annotations

from v143_rhythm_timing_consistency_shadow import (
    summarize_reference_free_timing_consistency,
)


def main() -> None:
    grid = {
        (1, 0): 0.00,
        (1, 4): 0.50,
        (1, 8): 1.00,
        (2, 0): 2.00,
        (2, 4): 2.50,
        (2, 8): 3.00,
        (3, 0): 4.00,
        (3, 4): 4.50,
        (3, 8): 5.00,
    }
    rows = [
        {"measure": 1, "onsetTime": 0.012, "stemSupportMax": 2, "sweepSupportMax": 4, "detectionCountSum": 8},
        {"measure": 1, "onsetTime": 0.492, "stemSupportMax": 2, "sweepSupportMax": 4, "detectionCountSum": 7},
        {"measure": 2, "onsetTime": 2.016, "stemSupportMax": 2, "sweepSupportMax": 4, "detectionCountSum": 9},
        {"measure": 2, "onsetTime": 2.488, "stemSupportMax": 2, "sweepSupportMax": 3, "detectionCountSum": 6},
        {"measure": 3, "onsetTime": 4.020, "stemSupportMax": 2, "sweepSupportMax": 4, "detectionCountSum": 8},
        # A weak row is retained in all-row diagnostics but excluded from strict structure.
        {"measure": 3, "onsetTime": 4.580, "stemSupportMax": 1, "sweepSupportMax": 1, "detectionCountSum": 1},
    ]
    report = summarize_reference_free_timing_consistency(
        rows,
        grid,
        tempo_bpm=120.0,
        first_beat_in_measure=0,
        downbeat_index_mod4=0,
        beat_confidence=0.82,
        bar_confidence=0.61,
    )

    assert report["rowCount"] == 6
    assert report["strictRowCount"] == 5
    assert report["strictRowsResidual"]["absoluteP95Seconds"] < 0.03
    assert report["strictRowsResidual"]["within30ms"] == 1.0
    assert report["strictPatternConsistency"]["lag1"]["pairCount"] == 2
    assert report["strictPatternConsistency"]["lag1"]["meanJaccard"] > 0.5

    invariants = report["invariants"]
    assert invariants["tempoChanged"] is False
    assert invariants["barPhaseChanged"] is False
    assert invariants["attackTimingChanged"] is False
    assert invariants["candidateSelectionChanged"] is False
    assert invariants["pitchChanged"] is False
    assert invariants["professionalReferenceUsed"] is False
    assert invariants["runtimeLabelsRequired"] is False
    assert invariants["productionModified"] is False

    print("V143 rhythm timing consistency shadow proof passed")
    print(report["strictRowsResidual"])
    print(report["strictPatternConsistency"])


if __name__ == "__main__":
    main()
