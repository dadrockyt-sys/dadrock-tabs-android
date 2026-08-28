#!/usr/bin/env python3
"""Song-blind synthetic fixtures for sealed V162 event/subdivision logic."""
from __future__ import annotations

import json
import math

import numpy as np

from event_logic_v162 import (
    BASS_GRID_CAP,
    GUITAR_POLYPHONY_CAP,
    active_state_reattack_candidates,
    bass_state_proposals,
    build_subdivision_lattice,
    cap_bass_grid,
    cap_guitar_polyphony,
    choose_sequence_register,
    event_step_score,
    frame_to_seconds,
    median_smooth_midi,
    recovery_score,
    refine_beat_subdivisions,
    segment_guitar_rows,
    select_event_step,
    stable_bass_states,
)


def assert_close(a: float, b: float, tol: float = 1e-9) -> None:
    if not math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=tol):
        raise AssertionError((a, b))


def guitar_segmentation_fixture() -> None:
    env = np.full(220, 0.10, dtype=float)
    # Strong unrelated population peaks establish a stable q60/q95 scale.
    env[[15, 45, 75, 105, 135, 165, 195]] = 1.0

    # Unsupported <=120ms gap merges.
    rows = [
        {"midi": 60, "startSeconds": 0.20, "endSeconds": 0.50, "confidence": 0.70},
        {"midi": 60, "startSeconds": 0.58, "endSeconds": 0.80, "confidence": 0.80},
    ]
    weak_frame = round(0.58 * 22050 / 256)
    env[weak_frame - 3:weak_frame + 4] = 0.10
    merged = segment_guitar_rows(rows, env)
    assert len(merged) == 1
    assert merged[0]["segmentedRawCount"] == 2
    assert_close(merged[0]["endSeconds"], 0.80)

    # Supported reattack inside <=120ms stays distinct.
    strong_env = env.copy()
    strong_frame = round(0.58 * 22050 / 256)
    strong_env[strong_frame] = 1.25
    separated = segment_guitar_rows(rows, strong_env)
    assert len(separated) == 2
    assert separated[1]["reattackEvidence"]["supported"] is True

    # Overlap always merges even if the second onset is strong.
    overlap = [
        {"midi": 62, "startSeconds": 1.00, "endSeconds": 1.30, "confidence": 0.70},
        {"midi": 62, "startSeconds": 1.20, "endSeconds": 1.45, "confidence": 0.75},
    ]
    overlap_merged = segment_guitar_rows(overlap, strong_env)
    assert len(overlap_merged) == 1

    # Gap >120ms remains separate without needing onset evidence.
    distant = [
        {"midi": 64, "startSeconds": 1.60, "endSeconds": 1.80, "confidence": 0.70},
        {"midi": 64, "startSeconds": 1.95, "endSeconds": 2.10, "confidence": 0.75},
    ]
    assert len(segment_guitar_rows(distant, strong_env)) == 2


def active_state_recovery_fixture() -> None:
    env = np.full(200, 0.05, dtype=float)
    env[[20, 50, 80, 110, 140, 170]] = 0.7
    onset_frame = 86
    env[onset_frame] = 1.0
    t = frame_to_seconds(onset_frame)
    raw = [
        {"midi": 60, "startSeconds": t - 0.15, "endSeconds": t + 0.15, "confidence": 0.90},
        {"midi": 64, "startSeconds": t - 0.10, "endSeconds": t + 0.20, "confidence": 0.80},
        {"midi": 67, "startSeconds": t - 0.20, "endSeconds": t + 0.10, "confidence": 0.75},
        {"midi": 71, "startSeconds": t - 0.20, "endSeconds": t + 0.10, "confidence": 0.70},
        # Not active at the onset, therefore must never be recovered.
        {"midi": 72, "startSeconds": t + 0.20, "endSeconds": t + 0.40, "confidence": 0.99},
    ]
    evidence = {
        (onset_frame, 60): {"templateRank": 0.99, "fundamentalPresent": True},
        (onset_frame, 64): {"templateRank": 0.95, "fundamentalPresent": True},
        (onset_frame, 67): {"templateRank": 0.90, "fundamentalPresent": True},
        (onset_frame, 71): {"templateRank": 0.88, "fundamentalPresent": True},
        (onset_frame, 72): {"templateRank": 1.00, "fundamentalPresent": True},
        # Free harmonic pitch not present in Basic Pitch intervals.
        (onset_frame, 76): {"templateRank": 1.00, "fundamentalPresent": True},
    }
    recovered = active_state_reattack_candidates(raw, [], [onset_frame], env, evidence)
    assert len(recovered) == 3
    assert [row["midi"] for row in recovered] == [60, 64, 67]
    assert 72 not in {row["midi"] for row in recovered}
    assert 76 not in {row["midi"] for row in recovered}
    assert all(row["source"] == "basic_pitch_active_state_reattack" for row in recovered)
    assert all(row["recoveryScore"] >= 0.58 for row in recovered)

    # Existing attack exclusion suppresses recovery near an already segmented attack.
    existing = [{"midi": 60, "startSeconds": t}]
    suppressed = active_state_reattack_candidates(raw, existing, [onset_frame], env, evidence)
    assert suppressed == []

    assert_close(recovery_score(0.8, 0.9, 0.7), 0.81)


def register_fixture() -> None:
    # No same-pitch-class context: isolated octave evidence cannot repair.
    rows = [{"midi": 60, "startSeconds": 1.0}, {"midi": 65, "startSeconds": 1.2}]
    chosen, meta = choose_sequence_register(
        rows, 0,
        {48: 1.0, 60: 0.40, 72: 1.0},
        {48: True, 60: True, 72: True},
    )
    assert chosen == 60 and meta["reason"] == "NO_CONTEXT"

    # Same-pitch-class neighbors around 72 support a 60->72 repair when all sealed gates pass.
    contextual = [
        {"midi": 72, "startSeconds": 0.60},
        {"midi": 60, "startSeconds": 1.00},
        {"midi": 72, "startSeconds": 1.40},
    ]
    chosen, meta = choose_sequence_register(
        contextual, 1,
        {48: 0.10, 60: 0.45, 72: 0.85},
        {48: False, 60: True, 72: True},
    )
    assert chosen == 72
    assert meta["repaired"] is True
    assert_close(meta["contextCenter"], 72.0)

    # Rank gain below 0.15 cannot repair even with context.
    chosen, meta = choose_sequence_register(
        contextual, 1,
        {48: 0.10, 60: 0.70, 72: 0.82},
        {48: False, 60: True, 72: True},
    )
    assert chosen == 60 and meta["repaired"] is False


def subdivision_fixture() -> None:
    # A 1-second beat at SR/HOP gives nominal interior frames near 22,43,65.
    env = np.full(120, 0.10, dtype=float)
    env[[10, 35, 58, 90, 105]] = 0.8
    nominal = refine_beat_subdivisions(0.0, 1.0, env)
    assert_close(nominal[0]["seconds"], 0.0)
    assert_close(nominal[-1]["seconds"], 1.0)

    # Force a qualifying peak two frames to the right of first nominal subdivision.
    shifted = env.copy()
    first_nom_frame = round(0.25 * 22050 / 256)
    shifted[first_nom_frame] = 0.15
    shifted[first_nom_frame + 2] = 1.2
    refined = refine_beat_subdivisions(0.0, 1.0, shifted)
    assert refined[1]["moved"] is True
    assert refined[1]["selectedFrame"] == first_nom_frame + 2
    times = [row["seconds"] for row in refined]
    assert all(times[i + 1] > times[i] for i in range(len(times) - 1))

    # Multi-beat lattice retains fixed beat boundaries and strict ordering.
    lattice = build_subdivision_lattice([0.0, 1.0, 2.0], shifted)
    assert_close(lattice[0], 0.0)
    assert_close(lattice[4], 1.0)
    assert_close(lattice[-1], 2.0)
    assert all(lattice[i + 1] > lattice[i] for i in range(len(lattice) - 1))

    # Non-nearest step needs >=0.05 score margin.
    score_nearest = event_step_score(0.25, 0.25, 0.25, 0.20, 0.20)
    score_neighbor = event_step_score(0.25, 0.26, 0.25, 1.00, 1.00)
    assert score_neighbor > score_nearest

    instrument = np.full(160, 0.05, dtype=float)
    shared = np.full(160, 0.05, dtype=float)
    simple_lattice = [0.0, 0.25, 0.50, 0.75, 1.0]
    near_frame = round(0.25 * 22050 / 256)
    neighbor_frame = round(0.50 * 22050 / 256)
    instrument[near_frame] = shared[near_frame] = 0.20
    instrument[neighbor_frame] = shared[neighbor_frame] = 1.00
    # Event remains near 0.25 enough that evidence cannot overcome the margin.
    step, meta = select_event_step(0.27, simple_lattice, instrument, shared)
    assert step == meta["nearestStep"] == 1

    # Event near the midpoint with much stronger neighboring onset evidence can choose one adjacent step only.
    step, meta = select_event_step(0.385, simple_lattice, instrument, shared)
    assert abs(step - meta["nearestStep"]) <= 1


def bass_state_fixture() -> None:
    # Stable 40 sustain, short two-frame gap bridged, then stable 43 state.
    midi = np.asarray([40.0] * 6 + [np.nan, np.nan] + [40.0] * 6 + [43.0] * 6, dtype=float)
    vp = np.asarray([0.90] * len(midi), dtype=float)
    states = stable_bass_states(midi, vp)
    assert len(states) == 2
    assert states[0]["midi"] == 40
    assert states[0]["frameCount"] == 14
    assert states[1]["midi"] == 43
    assert states[1]["frameCount"] == 6

    env = np.full(80, 0.05, dtype=float)
    env[[5, 20, 35, 50, 65]] = 0.8
    # Two strong onsets within first stable state far enough apart => detected + reattack.
    onset1 = 2
    onset2 = 11
    env[onset1] = 1.0
    env[onset2] = 1.1
    proposals = bass_state_proposals(states, [onset1, onset2], env)
    kinds = [row["kind"] for row in proposals]
    assert "detected_onset" in kinds
    assert "same_pitch_reattack" in kinds
    # State change must activate independently of a detected onset at its start.
    assert "state_change" in kinds
    state_change = next(row for row in proposals if row["kind"] == "state_change")
    assert state_change["midi"] == 43

    # Constant stable sustain with one onset emits one detected proposal, no duplicates.
    sustain = stable_bass_states(np.asarray([42.0] * 12), np.asarray([0.9] * 12))
    env2 = np.full(40, 0.05, dtype=float)
    env2[2] = 1.0
    single = bass_state_proposals(sustain, [2], env2)
    assert len(single) == 1 and single[0]["kind"] == "detected_onset"

    # Median smoother is sealed at 7 and removes a single-frame outlier.
    smoothed = median_smooth_midi(np.asarray([40, 40, 40, 52, 40, 40, 40], dtype=float))
    assert_close(smoothed[3], 40.0)


def grid_cap_fixture() -> None:
    guitar = [
        {"absoluteGridStep": 8, "midi": 50 + i, "admissionScore": 0.90 - i * 0.01, "confidence": 0.8}
        for i in range(8)
    ]
    capped_g = cap_guitar_polyphony(guitar)
    assert len(capped_g) == GUITAR_POLYPHONY_CAP == 6
    assert [row["midi"] for row in capped_g] == [50, 51, 52, 53, 54, 55]

    bass = [
        {"absoluteGridStep": 12, "midi": 40, "admissionScore": 0.70, "medianPyinVoicedProbability": 0.8},
        {"absoluteGridStep": 12, "midi": 43, "admissionScore": 0.80, "medianPyinVoicedProbability": 0.7},
    ]
    capped_b = cap_bass_grid(bass)
    assert len(capped_b) == BASS_GRID_CAP == 1
    assert capped_b[0]["midi"] == 43


def main() -> int:
    guitar_segmentation_fixture()
    active_state_recovery_fixture()
    register_fixture()
    subdivision_fixture()
    bass_state_fixture()
    grid_cap_fixture()
    print(json.dumps({
        "schema": "dadrock.tabs.v162.event-logic-static-test.v1",
        "validation": "PASS",
        "guitarSustain": True,
        "guitarSupportedReattack": True,
        "guitarWeakAttackSuppressed": True,
        "activeStateRecoveryOnly": True,
        "activeStateRecoveryCap": True,
        "registerNoContext": True,
        "registerContext": True,
        "subdivisionShift": True,
        "subdivisionOrdering": True,
        "eventStepBounded": True,
        "bassStableSustain": True,
        "bassSamePitchReattack": True,
        "bassStateChange": True,
        "bassGapBridge": True,
        "gridCaps": True,
        "songAudioRead": False,
        "demucsInvoked": False,
        "pitchInferenceInvoked": False,
        "professionalReferenceRead": False,
        "frozenScorerRead": False,
        "V161CandidateRead": False,
        "priorScoreRead": False,
        "gpuUsed": False
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
