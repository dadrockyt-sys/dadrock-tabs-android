from __future__ import annotations

import subprocess

from v143_contextual_prune_precision_candidate_events import build_precision_candidate_assembly
from v143_contextual_prune_precision_shadow import apply_reference_free_precision_shadow
from v143_contextual_prune_shadow_correction import ShadowCorrectionResult
from v143_reference_free_timing import ReferenceFreeTimingEstimate


MIDI_MIN = 28
MIDI_MAX = 112
EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"


def _vector(values: dict[int, float], default: float = -2.0) -> list[float]:
    out = [float(default)] * (MIDI_MAX - MIDI_MIN + 1)
    for midi, value in values.items():
        out[int(midi) - MIDI_MIN] = float(value)
    return out


def main() -> int:
    grid = {(1, 0): 0.5}
    view = {
        "attackMax": _vector({52: 1.85, 64: 2.00}),
        "earlyMean": _vector({52: 2.15, 64: 2.30}),
        "sustainMean": _vector({52: 2.15, 64: 2.30}),
    }
    rows = [
        {
            "measure": 1,
            "onsetTime": 0.5,
            "candidateMidis": [52, 64],
            "stemSupportMax": 2,
            "sweepSupportMax": 4,
            "detectionCountSum": 8,
            "viewA": view,
            "viewB": view,
        }
    ]
    correction = ShadowCorrectionResult(
        base_events=frozenset({(1, 0)}),
        corrected_events=frozenset({(1, 0)}),
        rescued_events=frozenset(),
        original_pitch_sets={(1, 0): (52, 64)},
        pitch_sets={(1, 0): (52, 64)},
        suppressed_pitch_count=0,
        observed_slot_count=1,
        strict_slot_count=1,
    )
    precision = apply_reference_free_precision_shadow(rows, grid, correction, {1})
    assert precision.primary_midis[(1, 0)] == 52, precision.primary_midis
    assert 64 in precision.pitch_sets[(1, 0)], precision.pitch_sets

    timing = ReferenceFreeTimingEstimate(
        beat_times=(0.5, 1.0),
        first_beat_in_measure=0,
        downbeat_index_mod4=0,
        tempo_bpm=120.0,
        beat_confidence=1.0,
        bar_confidence=1.0,
        source_sample_rate=22050,
    )
    candidate = build_precision_candidate_assembly(rows, grid, precision, timing)
    emitted = list(candidate.assembly.events)
    assert emitted, "precision adapter emitted no events"
    assert {int(event["midi"]) for event in emitted} == {52, 64}
    assert all(int(event["dominantMidi"]) == 52 for event in emitted), emitted
    assert all(int(event["noteMapping"]["sourceAttackMidi"]) == 52 for event in emitted)
    assert all(event["noteMapping"]["precisionPrimaryPreserved"] is True for event in emitted)
    primaries = [event for event in emitted if event["noteMapping"]["primaryTechniqueNote"] is True]
    assert len(primaries) == 1 and int(primaries[0]["midi"]) == 52, primaries

    protected = subprocess.check_output(
        ["git", "hash-object", "analyzer/v143_reference_free_rhythm_pipeline.py"],
        text=True,
    ).strip()
    assert protected == EXPECTED_PROTECTED_BLOB, protected
    print("V143 precision primary adapter checker: PASS")
    print({
        "precisionPrimary": precision.primary_midis[(1, 0)],
        "retainedPitches": precision.pitch_sets[(1, 0)],
        "emittedDominant": emitted[0]["dominantMidi"],
        "protectedPipelineBlob": protected,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
