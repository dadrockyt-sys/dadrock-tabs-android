from __future__ import annotations

import json
import math

import numpy as np

from modal.v147_pitch_hypothesis import (
    choose_pitch_hypothesis,
    choose_pitch_hypothesis_from_cqt,
    extract_candidate_evidence_from_cqt,
)


def _e(fundamental: float, octave: float = 0.0) -> dict[str, float]:
    return {
        "fundamentalDeltaDb": fundamental,
        "octaveDeltaDb": octave,
    }


def test_correct_control_keeps_original_pitch() -> None:
    result = choose_pitch_hypothesis(60, {59: _e(1), 60: _e(7), 61: _e(2)})
    assert result["selectedMidi"] == 60
    assert result["changed"] is False
    assert result["reason"] == "original-best"


def test_strong_down_one_evidence_recovers_pitch() -> None:
    result = choose_pitch_hypothesis(60, {59: _e(8), 60: _e(3), 61: _e(1)})
    assert result["selectedMidi"] == 59
    assert result["semitoneDelta"] == -1
    assert result["reason"] == "alternate-supported"


def test_strong_up_one_evidence_recovers_pitch() -> None:
    result = choose_pitch_hypothesis(60, {59: _e(1), 60: _e(3), 61: _e(8)})
    assert result["selectedMidi"] == 61
    assert result["semitoneDelta"] == 1
    assert result["reason"] == "alternate-supported"


def test_ambiguous_neighbor_fails_closed() -> None:
    result = choose_pitch_hypothesis(60, {59: _e(1), 60: _e(4), 61: _e(6.5)})
    assert result["selectedMidi"] == 60
    assert result["reason"] == "alternate-score-margin-too-small"


def test_weak_alternate_fails_closed() -> None:
    result = choose_pitch_hypothesis(60, {59: _e(0), 60: _e(0), 61: _e(2.9)})
    assert result["selectedMidi"] == 60
    assert result["reason"] == "alternate-fundamental-too-weak"


def test_tied_best_candidates_fail_closed() -> None:
    result = choose_pitch_hypothesis(60, {59: _e(7), 60: _e(2), 61: _e(7)})
    assert result["selectedMidi"] == 60
    assert result["reason"] == "tied-best-score"


def test_low_boundary_never_emits_below_guitar_range() -> None:
    result = choose_pitch_hypothesis(40, {40: _e(2), 41: _e(7)})
    assert result["selectedMidi"] == 41
    assert 40 <= result["selectedMidi"] <= 88


def test_high_boundary_never_emits_above_guitar_range() -> None:
    result = choose_pitch_hypothesis(88, {87: _e(7), 88: _e(2)})
    assert result["selectedMidi"] == 87
    assert 40 <= result["selectedMidi"] <= 88


def test_missing_candidate_evidence_fails_closed() -> None:
    result = choose_pitch_hypothesis(60, {59: _e(8), 60: _e(2)})
    assert result["selectedMidi"] == 60
    assert result["reason"] == "missing-or-malformed-candidate"


def test_nonfinite_evidence_fails_closed() -> None:
    result = choose_pitch_hypothesis(
        60,
        {59: _e(8), 60: _e(2), 61: _e(math.inf)},
    )
    assert result["selectedMidi"] == 60
    assert result["reason"] == "non-finite-evidence"


def test_decision_is_deterministic() -> None:
    evidence = {59: _e(1.25, 2.5), 60: _e(3.0, 1.0), 61: _e(8.25, 4.0)}
    first = json.dumps(
        choose_pitch_hypothesis(60, evidence),
        sort_keys=True,
        separators=(",", ":"),
    )
    second = json.dumps(
        choose_pitch_hypothesis(60, evidence),
        sort_keys=True,
        separators=(",", ":"),
    )
    assert first == second


def test_generated_cqt_adapter_supports_strong_neighbor() -> None:
    midi_bins = np.arange(56.0, 76.0001, 0.25)
    cqt = np.ones((midi_bins.size, 4), dtype=float)
    frames = [0, 1, 2, 3]

    target_mask = np.abs(midi_bins - 61.0) <= 0.30
    cqt[target_mask, :] = 10.0

    evidence = extract_candidate_evidence_from_cqt(cqt, midi_bins, frames, 60)
    assert evidence is not None
    assert evidence[61]["fundamentalDeltaDb"] > evidence[60]["fundamentalDeltaDb"] + 2.0

    result = choose_pitch_hypothesis_from_cqt(60, cqt, midi_bins, frames)
    assert result["selectedMidi"] == 61
    assert result["reason"] == "alternate-supported"


def test_generated_cqt_adapter_shape_error_fails_closed() -> None:
    midi_bins = np.arange(56.0, 76.0001, 0.25)
    bad_cqt = np.ones((midi_bins.size - 1, 4), dtype=float)
    result = choose_pitch_hypothesis_from_cqt(60, bad_cqt, midi_bins, [0, 1])
    assert result["selectedMidi"] == 60
    assert result["reason"] == "cqt-evidence-unavailable"
