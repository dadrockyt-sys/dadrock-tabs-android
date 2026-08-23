#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

from v143_contextual_prune_shadow_correction import (
    SPECTRUM_MIDI_MAX,
    SPECTRUM_MIDI_MIN,
    apply_reference_free_shadow_correction,
)


def _vector(default: float = -1.0) -> list[float]:
    return [float(default)] * (SPECTRUM_MIDI_MAX - SPECTRUM_MIDI_MIN + 1)


def _row(
    measure: int,
    onset: float,
    midis: list[int],
    *,
    strong: list[int],
    weak_cross_view: list[int] | None = None,
    stem_support: int = 2,
    sweep_support: int = 4,
    detections: int = 8,
) -> dict[str, Any]:
    weak = set(weak_cross_view or [])
    view_a = {name: _vector() for name in ("attackMax", "earlyMean", "sustainMean")}
    view_b = {name: _vector() for name in ("attackMax", "earlyMean", "sustainMean")}
    for midi in midis:
        index = midi - SPECTRUM_MIDI_MIN
        if midi in strong:
            view_a["attackMax"][index] = 2.4
            view_b["attackMax"][index] = 2.2
            view_a["earlyMean"][index] = 1.5
            view_b["earlyMean"][index] = 1.4
            view_a["sustainMean"][index] = 1.0
            view_b["sustainMean"][index] = 0.9
        elif midi in weak:
            view_a["attackMax"][index] = 2.8
            view_b["attackMax"][index] = -0.8
            view_a["earlyMean"][index] = 1.5
            view_b["earlyMean"][index] = -0.9
            view_a["sustainMean"][index] = 1.0
            view_b["sustainMean"][index] = -1.0
        else:
            view_a["attackMax"][index] = 0.15
            view_b["attackMax"][index] = 0.10
            view_a["earlyMean"][index] = -0.15
            view_b["earlyMean"][index] = -0.20
            view_a["sustainMean"][index] = -0.20
            view_b["sustainMean"][index] = -0.25
    return {
        "measure": measure,
        "onsetTime": onset,
        "candidateMidis": midis,
        "stemSupportMax": stem_support,
        "sweepSupportMax": sweep_support,
        "detectionCountSum": detections,
        "viewA": view_a,
        "viewB": view_b,
    }


def main() -> None:
    grid = {
        (1, 0): 0.00,
        (1, 4): 0.50,
        (2, 0): 2.00,
        (2, 4): 2.50,
        (3, 0): 4.00,
        (4, 0): 6.00,
    }
    rows = [
        _row(1, 0.01, [40], strong=[40]),
        # Measure 1 is already populated by the base selector. This strict,
        # separated local peak proves the new rescue is not empty-measure-only.
        _row(1, 0.49, [45], strong=[45]),
        _row(2, 2.02, [40, 52, 64, 76, 88], strong=[40, 52, 64, 76], weak_cross_view=[88]),
        _row(2, 2.49, [43], strong=[43], stem_support=1),
        _row(3, 4.01, [45], strong=[45], stem_support=1),
        # A base-selected event with no independently supported pitch must not be
        # collapsed to a single arbitrary winner merely because one candidate is
        # relatively less weak than another.
        _row(4, 6.01, [48, 60], strong=[], weak_cross_view=[48, 60]),
    ]
    result = apply_reference_free_shadow_correction(
        rows,
        grid,
        base_events={(1, 0), (4, 0)},
        target_measures={1, 2, 3, 4},
    )

    assert (1, 0) in result.corrected_events
    assert (4, 0) in result.corrected_events
    assert (1, 4) in result.rescued_events
    assert (2, 0) in result.rescued_events
    assert all(key[0] != 3 for key in result.rescued_events)
    assert result.pitch_sets[(2, 0)] == (40, 52, 64, 76)
    assert 88 not in result.pitch_sets[(2, 0)]
    assert result.pitch_sets[(4, 0)] == (48, 60)
    assert result.original_pitch_sets[(4, 0)] == result.pitch_sets[(4, 0)]
    assert result.suppressed_pitch_count == 1
    assert result.diagnostics()["baseEventsPreserved"] is True
    assert result.diagnostics()["rescuesAreObservedSlots"] is True
    assert result.diagnostics()["localPeakRescueEnabled"] is True
    assert result.diagnostics()["emptyMeasureFailSafeEnabled"] is True
    assert result.diagnostics()["candidateRelocatesEvents"] is False
    assert result.diagnostics()["referenceFree"] is True
    assert result.diagnostics()["runtimeLabelsRequired"] is False
    assert result.diagnostics()["productionModified"] is False

    print("V143 contextual-prune shadow correction CPU proof passed")
    print(result.diagnostics())


if __name__ == "__main__":
    main()
