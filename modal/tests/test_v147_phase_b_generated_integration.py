from __future__ import annotations

import json

from modal.v147_phase_b_generated_integration import (
    decode_generated_pitch_hypotheses,
    integration_result_to_dict,
    position_identity_violations,
)


def _event(midi: int, onset: float = 0.10) -> dict[str, float | int]:
    return {
        "midi": midi,
        "onset": onset,
        "duration": 0.20,
        "confidence": 0.90,
    }


def _e(fundamental: float, octave: float = 0.0) -> dict[str, float]:
    return {
        "fundamentalDeltaDb": fundamental,
        "octaveDeltaDb": octave,
    }


def _selected(result, source_index: int = 0) -> int:
    row = next(row for row in result.decisions if row["sourceIndex"] == source_index)
    return int(row["selectedMidi"])


def test_control_passthrough_reaches_v145_unchanged() -> None:
    result = decode_generated_pitch_hypotheses(
        [_event(60)],
        {0: {59: _e(1), 60: _e(8), 61: _e(2)}},
        0.25,
    )
    assert _selected(result) == 60
    assert result.decisions[0]["changed"] is False
    assert result.decode_result.decoded_notes[0].midi == 60
    assert position_identity_violations(result) == 0


def test_down_one_recovery_reaches_v145_and_valid_position() -> None:
    result = decode_generated_pitch_hypotheses(
        [_event(60)],
        {0: {59: _e(8), 60: _e(3), 61: _e(1)}},
        0.25,
    )
    assert _selected(result) == 59
    assert result.decisions[0]["semitoneDelta"] == -1
    assert result.corrected_events[0]["midi"] == 59
    assert result.decode_result.decoded_notes[0].midi == 59
    assert position_identity_violations(result) == 0


def test_up_one_recovery_reaches_v145_and_valid_position() -> None:
    result = decode_generated_pitch_hypotheses(
        [_event(60)],
        {0: {59: _e(1), 60: _e(3), 61: _e(8)}},
        0.25,
    )
    assert _selected(result) == 61
    assert result.decisions[0]["semitoneDelta"] == 1
    assert result.corrected_events[0]["midi"] == 61
    assert result.decode_result.decoded_notes[0].midi == 61
    assert position_identity_violations(result) == 0


def test_ambiguous_evidence_fails_closed_end_to_end() -> None:
    result = decode_generated_pitch_hypotheses(
        [_event(60)],
        {0: {59: _e(1), 60: _e(4), 61: _e(6.5)}},
        0.25,
    )
    assert _selected(result) == 60
    assert result.decisions[0]["reason"] == "alternate-score-margin-too-small"
    assert result.decode_result.decoded_notes[0].midi == 60


def test_missing_evidence_fails_closed_end_to_end() -> None:
    result = decode_generated_pitch_hypotheses([_event(60)], {}, 0.25)
    assert _selected(result) == 60
    assert result.decisions[0]["reason"] == "malformed-evidence"
    assert result.decode_result.decoded_notes[0].midi == 60


def test_caller_owned_events_are_not_mutated() -> None:
    events = [_event(60), _event(64, 0.40)]
    before = json.dumps(events, sort_keys=True, separators=(",", ":"))
    result = decode_generated_pitch_hypotheses(
        events,
        {
            0: {59: _e(8), 60: _e(3), 61: _e(1)},
            1: {63: _e(1), 64: _e(8), 65: _e(2)},
        },
        0.25,
    )
    after = json.dumps(events, sort_keys=True, separators=(",", ":"))
    assert before == after
    assert result.corrected_events[0]["midi"] == 59
    assert events[0]["midi"] == 60


def test_valid_source_cardinality_is_preserved() -> None:
    events = [
        _event(60, 0.10),
        _event(62, 0.40),
        _event(64, 0.70),
        _event(65, 1.00),
        _event(67, 1.30),
    ]
    evidence = {
        0: {59: _e(1), 60: _e(8), 61: _e(2)},
        1: {61: _e(8), 62: _e(3), 63: _e(1)},
        2: {63: _e(1), 64: _e(3), 65: _e(8)},
        3: {64: _e(1), 65: _e(8), 66: _e(2)},
        4: {66: _e(1), 67: _e(8), 68: _e(2)},
    }
    result = decode_generated_pitch_hypotheses(events, evidence, 0.25)
    assert result.normalized_evidence_count == len(events)
    assert len(result.decisions) == len(events)
    assert result.decode_result.evidence_count == len(events)
    assert result.decode_result.decoded_evidence_count == len(events)
    assert position_identity_violations(result) == 0


def test_integration_serialization_is_deterministic() -> None:
    events = [_event(60), _event(64, 0.40)]
    evidence = {
        0: {59: _e(8), 60: _e(3), 61: _e(1)},
        1: {63: _e(1), 64: _e(8), 65: _e(2)},
    }
    first = json.dumps(
        integration_result_to_dict(decode_generated_pitch_hypotheses(events, evidence, 0.25)),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    second = json.dumps(
        integration_result_to_dict(decode_generated_pitch_hypotheses(events, evidence, 0.25)),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    assert first == second
