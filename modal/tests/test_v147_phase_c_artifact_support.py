from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from modal.v147_phase_c_artifact_support import (
    EXPECTED_ACCEPTED_EVENT_COUNT,
    EXPECTED_ACCEPTED_EVENT_SHA256,
    apply_fixed_time_pitch_decisions,
    decide_event_from_prepared_cqt,
    event_onset_seconds,
    materialize_accepted_family,
    select_frame_indices,
    timing_and_metadata_violations,
    verify_raw_audio_identity,
    verify_sha256,
)


ROOT = Path(__file__).resolve().parents[2]
V5_PATH = ROOT / "debug" / "v143-contextual-prune" / "v5-professional-pdf" / "v5-render-stream.json"
OPEN_MIDI_BY_STRING_INDEX = {0: 64, 1: 59, 2: 55, 3: 50, 4: 45, 5: 40}


def _event(
    *,
    event_index: int = 0,
    midi: int = 60,
    string_index: int = 1,
    fret: int = 1,
    measure: int = 1,
    step: int = 0,
    duration: float = 0.20,
) -> dict[str, object]:
    return {
        "eventIndex": event_index,
        "midi": midi,
        "stringIndex": string_index,
        "fret": fret,
        "measure": measure,
        "step": step,
        "durationSeconds": duration,
        "durationSteps": 2,
        "techniques": [],
        "metadataSource": "generated-test",
    }


def _prepared_cqt(strong_midi: int) -> tuple[np.ndarray, np.ndarray, list[float]]:
    bins = np.arange(38.0, 103.01, 0.25, dtype=float)
    frame_times = [0.02, 0.04, 0.06, 0.08, 0.10]
    cqt = np.ones((len(bins), len(frame_times)), dtype=float)
    strong = np.abs(bins - float(strong_midi)) <= 0.30
    original = np.abs(bins - 60.0) <= 0.30
    cqt[original, :] = 2.0
    cqt[strong, :] = 20.0
    return cqt, bins, frame_times


def test_materializes_exact_accepted_family_without_reference() -> None:
    stream = json.loads(V5_PATH.read_text(encoding="utf-8"))
    events = materialize_accepted_family(stream)
    assert len(events) == EXPECTED_ACCEPTED_EVENT_COUNT == 1144

    # The materializer itself verifies the canonical hash after every selected stage.
    from modal.v147_phase_c_artifact_support import sha256_json, canonical_events

    assert sha256_json(canonical_events(events)) == EXPECTED_ACCEPTED_EVENT_SHA256
    assert {int(row["measure"]) for row in events} == set(range(1, 114))


def test_materializer_fails_closed_if_v5_source_changes() -> None:
    stream = json.loads(V5_PATH.read_text(encoding="utf-8"))
    mutated = copy.deepcopy(stream)
    mutated["events"][0]["midi"] = int(mutated["events"][0]["midi"]) + 1
    mutated["events"][0]["fret"] = int(mutated["events"][0]["fret"]) + 1
    with pytest.raises(ValueError, match="V5 source identity mismatch"):
        materialize_accepted_family(mutated)


def test_generic_sha_guard_accepts_exact_and_rejects_mismatch() -> None:
    payload = b"phase-c-generated-sha-fixture"
    expected = hashlib.sha256(payload).hexdigest()
    assert verify_sha256(payload, expected) == expected
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        verify_sha256(payload + b"x", expected)


def test_real_audio_guard_rejects_noncanonical_bytes_without_decoding() -> None:
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        verify_raw_audio_identity(b"not-the-historical-source-audio")


def test_frozen_event_time_and_frame_selection() -> None:
    event = _event(measure=1, step=0, duration=0.20)
    assert event_onset_seconds(event) == 0.0
    frame_times = [0.00, 0.019, 0.020, 0.040, 0.080, 0.120, 0.149, 0.151]
    indices = select_frame_indices(frame_times, event)
    assert indices == (2, 3, 4, 5, 6)


def test_frozen_cqt_delegation_recovers_strong_up_one() -> None:
    event = _event(midi=60, string_index=1, fret=1)
    cqt, bins, times = _prepared_cqt(61)
    decision = decide_event_from_prepared_cqt(event, cqt, bins, times)
    assert decision["changed"] is True
    assert decision["selectedMidi"] == 61
    assert decision["semitoneDelta"] == 1
    assert decision["reason"] == "alternate-supported"
    assert len(decision["frameIndices"]) == 5


def test_insufficient_frames_fail_closed_before_cqt_evidence() -> None:
    event = _event()
    cqt, bins, _ = _prepared_cqt(61)
    decision = decide_event_from_prepared_cqt(
        event,
        cqt[:, :2],
        bins,
        [0.02, 0.04],
    )
    assert decision["changed"] is False
    assert decision["selectedMidi"] == 60
    assert decision["reason"] == "insufficient-frames"


def test_fixed_time_pitch_change_preserves_all_non_position_fields() -> None:
    before = [_event(midi=60, string_index=1, fret=1, step=4)]
    snapshot = copy.deepcopy(before)
    result = apply_fixed_time_pitch_decisions(before, {0: 61})
    after = result["events"]

    assert before == snapshot
    assert result["changedEventCount"] == 1
    assert result["onsetGroupFailClosedCount"] == 0
    assert after[0]["midi"] == 61
    assert after[0]["measure"] == before[0]["measure"]
    assert after[0]["step"] == before[0]["step"]
    assert after[0]["durationSeconds"] == before[0]["durationSeconds"]
    assert timing_and_metadata_violations(before, after) == []

    string_index = int(after[0]["stringIndex"])
    fret = int(after[0]["fret"])
    assert 0 <= string_index <= 5
    assert 0 <= fret <= 24
    assert OPEN_MIDI_BY_STRING_INDEX[string_index] + fret == 61


def test_fixed_time_invalid_delta_fails_closed_for_entire_group() -> None:
    before = [
        _event(event_index=0, midi=60, string_index=1, fret=1),
        _event(event_index=1, midi=64, string_index=0, fret=0),
    ]
    result = apply_fixed_time_pitch_decisions(before, {0: 62, 1: 65})
    assert result["events"] == before
    assert result["changedEventCount"] == 0
    assert result["onsetGroupFailClosedCount"] == 1


def test_timing_metadata_checker_detects_forbidden_mutation() -> None:
    before = [_event()]
    after = copy.deepcopy(before)
    after[0]["step"] = 1
    violations = timing_and_metadata_violations(before, after)
    assert len(violations) == 1
    assert violations[0]["forbiddenFields"] == ["step"]


def test_support_is_deterministic_for_identical_generated_inputs() -> None:
    event = _event(midi=60, string_index=1, fret=1)
    cqt, bins, times = _prepared_cqt(59)
    first = decide_event_from_prepared_cqt(event, cqt, bins, times)
    second = decide_event_from_prepared_cqt(event, cqt, bins, times)
    assert json.dumps(first, sort_keys=True, separators=(",", ":")) == json.dumps(
        second, sort_keys=True, separators=(",", ":")
    )
