#!/usr/bin/env python3
from __future__ import annotations

from v143_contextual_prune_candidate_events import build_corrected_candidate_assembly
from v143_contextual_prune_shadow_correction import ShadowCorrectionResult
from v143_reference_free_timing import ReferenceFreeTimingEstimate


MIDI_MIN = 28
MIDI_MAX = 112


def _vector(default: float = -1.0) -> list[float]:
    return [float(default)] * (MIDI_MAX - MIDI_MIN + 1)


def _row(measure: int, onset: float, midis: list[int]) -> dict[str, object]:
    view_a = {name: _vector() for name in ("attackMax", "earlyMean", "sustainMean")}
    view_b = {name: _vector() for name in ("attackMax", "earlyMean", "sustainMean")}
    for strength_rank, midi in enumerate(midis):
        index = midi - MIDI_MIN
        strength = 2.4 - 0.08 * strength_rank
        view_a["attackMax"][index] = strength
        view_b["attackMax"][index] = strength - 0.1
        view_a["earlyMean"][index] = 1.4 - 0.03 * strength_rank
        view_b["earlyMean"][index] = 1.3 - 0.03 * strength_rank
        view_a["sustainMean"][index] = 1.0 - 0.02 * strength_rank
        view_b["sustainMean"][index] = 0.9 - 0.02 * strength_rank
    return {
        "measure": measure,
        "onsetTime": onset,
        "candidateMidis": list(midis),
        "stemSupportMax": 2,
        "sweepSupportMax": 4,
        "detectionCountSum": 12,
        "viewA": view_a,
        "viewB": view_b,
    }


def main() -> None:
    grid = {
        (1, 0): 0.00,
        (1, 4): 0.50,
        (2, 0): 2.00,
    }
    rows = [
        _row(1, 0.01, [40, 45, 52]),
        # Seven supported pitches force the adapter to honor the six-string
        # physical ceiling without inventing or relocating anything.
        _row(1, 0.49, [40, 45, 50, 55, 59, 64, 67]),
        _row(2, 2.01, [43]),
    ]
    correction = ShadowCorrectionResult(
        base_events=frozenset({(1, 0), (1, 4)}),
        corrected_events=frozenset({(1, 0), (1, 4), (2, 0)}),
        rescued_events=frozenset({(2, 0)}),
        original_pitch_sets={
            (1, 0): (40, 45, 52),
            (1, 4): (40, 45, 50, 55, 59, 64, 67),
            (2, 0): (43,),
        },
        pitch_sets={
            (1, 0): (40, 45, 52),
            (1, 4): (40, 45, 50, 55, 59, 64, 67),
            (2, 0): (43,),
        },
        suppressed_pitch_count=0,
        observed_slot_count=3,
        strict_slot_count=3,
    )
    timing = ReferenceFreeTimingEstimate(
        beat_times=(0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5),
        first_beat_in_measure=0,
        downbeat_index_mod4=0,
        tempo_bpm=120.0,
        beat_confidence=0.9,
        bar_confidence=0.8,
        source_sample_rate=22050,
    )

    result = build_corrected_candidate_assembly(rows, grid, correction, timing)
    diagnostics = result.diagnostics()
    assert diagnostics["correctedAttackCount"] == 3
    assert diagnostics["everyCorrectedAttackRendered"] is True
    assert diagnostics["candidateAddsUnobservedPitch"] is False
    assert diagnostics["candidateRelocatesEvents"] is False
    assert diagnostics["referenceFree"] is True
    assert diagnostics["productionModified"] is False
    assert result.source.selected_count == 3

    emitted_by_key: dict[tuple[int, int], list[dict[str, object]]] = {}
    for event in result.assembly.events:
        key = (int(event["measure"]), int(event["step"]))
        emitted_by_key.setdefault(key, []).append(event)
        assert int(event["midi"]) in correction.pitch_sets[key]
        assert event["noteMapping"]["professionalReferenceUsed"] is False
        assert event["noteMapping"]["runtimeLabelsRequired"] is False

    assert set(emitted_by_key) == set(correction.corrected_events)
    assert len(emitted_by_key[(1, 4)]) <= 6
    for events in emitted_by_key.values():
        strings = [int(event["stringIndex"]) for event in events]
        assert len(strings) == len(set(strings))

    print("V143 corrected Rhythm candidate event proof passed")
    print(diagnostics)


if __name__ == "__main__":
    main()
