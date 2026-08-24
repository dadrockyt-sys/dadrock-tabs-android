from __future__ import annotations

import subprocess
from pathlib import Path

from v143_contextual_prune_precision_shadow import PrecisionShadowResult
from v143_precision_promoted_harmonic_guard import apply_reference_free_promoted_harmonic_guard


EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"
MIDI_MIN = 28
MIDI_MAX = 112


def _vector(values: dict[int, float], default: float = -2.0) -> list[float]:
    result = [float(default)] * (MIDI_MAX - MIDI_MIN + 1)
    for midi, value in values.items():
        result[int(midi) - MIDI_MIN] = float(value)
    return result


def _row(measure: int, onset: float, values: dict[int, float], candidates: list[int]) -> dict:
    vector = _vector(values)
    view = {
        "attackMax": vector,
        "earlyMean": vector,
        "sustainMean": vector,
    }
    return {
        "measure": int(measure),
        "onsetTime": float(onset),
        "candidateMidis": list(candidates),
        "stemSupportMax": 2,
        "sweepSupportMax": 4,
        "detectionCountSum": 8,
        "viewA": view,
        "viewB": view,
    }


def main() -> int:
    grid = {
        (1, 0): 0.0,
        (1, 4): 0.5,
        (1, 8): 1.0,
    }
    rows = [
        # The strongest raw 52 is +12 above promoted primary 40. This is the
        # contradictory case: if 52 is reinterpreted as harmonic support for 40,
        # it must not also be emitted as an independent secondary note.
        _row(1, 0.0, {40: 0.78, 52: 0.90}, [40, 52]),
        # Minimality: strongest raw is +7, not one of the harmonic-family
        # intervals used by the fundamental promotion model, so keep it.
        _row(1, 0.5, {45: 0.78, 52: 0.90}, [45, 52]),
        # No promotion: primary already equals strongest raw, so keep the lower
        # secondary untouched.
        _row(1, 1.0, {40: 0.82, 52: 0.90}, [40, 52]),
    ]
    precision = PrecisionShadowResult(
        input_events=frozenset(grid),
        retained_events=frozenset(grid),
        pruned_events=frozenset(),
        original_pitch_sets={
            (1, 0): (40, 52),
            (1, 4): (45, 52),
            (1, 8): (40, 52),
        },
        pitch_sets={
            (1, 0): (40, 52),
            (1, 4): (45, 52),
            (1, 8): (40, 52),
        },
        primary_midis={
            (1, 0): 40,
            (1, 4): 45,
            (1, 8): 52,
        },
        fail_safe_events=frozenset(),
        fundamental_promotions=2,
        suppressed_pitch_count=0,
    )

    guarded, diagnostics = apply_reference_free_promoted_harmonic_guard(rows, grid, precision)

    assert guarded.retained_events == precision.retained_events
    assert guarded.primary_midis == precision.primary_midis
    assert guarded.pitch_sets[(1, 0)] == (40,), guarded.pitch_sets
    assert guarded.pitch_sets[(1, 4)] == (45, 52), guarded.pitch_sets
    assert guarded.pitch_sets[(1, 8)] == (40, 52), guarded.pitch_sets
    assert guarded.suppressed_pitch_count == 1

    diag = diagnostics.to_dict()
    assert diag["inspectedAttackCount"] == 3
    assert diag["promotedPrimaryCount"] == 2
    assert diag["harmonicStrongestAbovePromotedPrimaryCount"] == 1
    assert diag["suppressedStrongestHarmonicCount"] == 1
    assert diag["attackIdentityChanged"] is False
    assert diag["primaryMidiChanged"] is False
    assert diag["addsUnobservedAttack"] is False
    assert diag["addsUnobservedPitch"] is False
    assert diag["relocatesAttack"] is False
    assert diag["referenceFree"] is True
    assert diag["professionalReferenceUsed"] is False
    assert diag["runtimeLabelsRequired"] is False
    assert diag["productionModified"] is False

    protected = subprocess.check_output(
        ["git", "hash-object", "analyzer/v143_reference_free_rhythm_pipeline.py"],
        text=True,
    ).strip()
    assert protected == EXPECTED_PROTECTED_BLOB, protected

    source = Path("analyzer/v143_precision_promoted_harmonic_guard.py").read_text(encoding="utf-8").lower()
    forbidden = [
        "professional-rhythm-complete",
        "reference.json",
        "songsterr",
        "are you gonna go my way",
        "lenny kravitz",
        "craig ross",
    ]
    assert not any(token in source for token in forbidden)

    print("V143 precision promoted harmonic guard checker: PASS")
    print(diag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
