from __future__ import annotations

import subprocess
from pathlib import Path

from v143_contextual_prune_precision_shadow import apply_reference_free_precision_shadow
from v143_contextual_prune_shadow_correction import ShadowCorrectionResult


EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"
MIDI_MIN = 28
MIDI_MAX = 112


def _vector(values: dict[int, float], default: float = -2.0) -> list[float]:
    result = [float(default)] * (MIDI_MAX - MIDI_MIN + 1)
    for midi, value in values.items():
        result[int(midi) - MIDI_MIN] = float(value)
    return result


def _row(measure: int, onset: float, *, attack: dict[int, float], body: dict[int, float], candidates: list[int], sweep: int = 4, detections: int = 8) -> dict:
    view = {
        "attackMax": _vector(attack),
        "earlyMean": _vector(body),
        "sustainMean": _vector(body),
    }
    return {
        "measure": measure,
        "onsetTime": onset,
        "candidateMidis": candidates,
        "stemSupportMax": 2,
        "sweepSupportMax": sweep,
        "detectionCountSum": detections,
        "viewA": view,
        "viewB": view,
    }


def main() -> int:
    grid = {(1, 0): 0.0, (1, 4): 0.5, (2, 0): 2.0}
    rows = [
        # Strong transient. 64 is the strongest raw bin, but 52 has physically
        # present octave-family support and should be promoted as fundamental.
        _row(
            1,
            0.0,
            attack={52: 1.85, 64: 2.00, 67: 1.70},
            body={52: 2.15, 64: 2.30, 67: 1.95},
            candidates=[52, 64, 67],
        ),
        _row(
            1,
            0.5,
            attack={59: 0.70, 71: 0.72},
            body={59: 1.80, 71: 1.85},
            candidates=[59, 71],
        ),
        _row(
            2,
            2.0,
            attack={57: 0.80, 69: 0.82},
            body={57: 1.70, 69: 1.75},
            candidates=[57, 69],
        ),
    ]
    correction = ShadowCorrectionResult(
        base_events=frozenset({(1, 0), (1, 4), (2, 0)}),
        corrected_events=frozenset({(1, 0), (1, 4), (2, 0)}),
        rescued_events=frozenset(),
        original_pitch_sets={(1, 0): (52, 64, 67), (1, 4): (59, 71), (2, 0): (57, 69)},
        pitch_sets={(1, 0): (52, 64, 67), (1, 4): (59, 71), (2, 0): (57, 69)},
        suppressed_pitch_count=0,
        observed_slot_count=3,
        strict_slot_count=3,
    )

    result = apply_reference_free_precision_shadow(rows, grid, correction, {1, 2})
    assert result.retained_events.issubset(correction.corrected_events)
    assert (1, 0) in result.retained_events
    assert (1, 4) in result.pruned_events
    assert (2, 0) in result.retained_events
    assert (2, 0) in result.fail_safe_events
    assert {measure for measure, _step in result.retained_events} == {1, 2}
    assert result.fundamental_promotions >= 1
    assert result.primary_midis[(1, 0)] == 52, result.primary_midis
    assert set(result.primary_midis) == set(result.retained_events)
    for key, midis in result.pitch_sets.items():
        observed = set(next(row["candidateMidis"] for row in rows if row["measure"] == key[0] and abs(row["onsetTime"] - grid[key]) < 1e-9))
        assert set(midis).issubset(observed)
        assert int(result.primary_midis[key]) in set(midis)

    protected = subprocess.check_output(
        ["git", "hash-object", "analyzer/v143_reference_free_rhythm_pipeline.py"],
        text=True,
    ).strip()
    assert protected == EXPECTED_PROTECTED_BLOB, protected

    source = Path("analyzer/v143_contextual_prune_precision_shadow.py").read_text(encoding="utf-8").lower()
    forbidden = ["professional-rhythm-complete", "reference.json", "songsterr", "are you gonna go my way", "lenny kravitz", "craig ross"]
    assert not any(token in source for token in forbidden)

    diag = result.diagnostics()
    assert diag["explicitPrimaryMidiComplete"] is True
    assert diag["candidateAddsUnobservedAttack"] is False
    assert diag["candidateRelocatesEvents"] is False
    assert diag["candidateAddsUnobservedPitch"] is False
    assert diag["referenceFree"] is True
    assert diag["productionModified"] is False
    print("V143 contextual-prune precision shadow checker: PASS")
    print(diag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
