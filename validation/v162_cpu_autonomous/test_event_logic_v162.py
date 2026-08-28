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
    env[[15, 45, 75, 105, 135, 165, 195]] = 1.0
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

    strong_env = env.copy()
    strong_frame = round(0.58 * 22050 / 256)
    strong_env[strong_frame] = 1.25
    separated = segment_guitar_rows(rows, strong_env)
    assert len(separated) == 2
    assert separated[1]["reattackEvidence"]["supported"] is True

    overlap = [
        {"midi": 62, "startSeconds": 1.00, "endSeconds": 1.30, "confidence": 0.70},
        {"midi": 62, "startSeconds": 1.20, "endSeconds": 1.45, "confidence": 0.75},
    ]
    assert len(segment_guitar_rows(overlap, strong_env)) == 1

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
        {"midi": 72, "startSeconds": t + 0.20, "endSeconds": t + 0.40, "confidence": 0.99},
    ]
    evidence = {
        (onset_frame, 60): {"templateRank": 0.99, "fundamentalPresent": True},
        (onset_frame, 64): {"templateRank": 0.95, "fundamentalPresent": True},
        (onset_frame, 67): {"templateRank": 0.90, "fundamentalPresent": True},
        (onset_frame, 71): {"templateRank": 0.88, "fundamentalPresent": True},
        (onset_frame, 72): {"templateRank": 1.00, "fundamentalPresent": True},
        (onset_frame, 76): {"templateRank": 1.00, "fundamentalPresent": True},
    }
    recovered = active_state_reattack_candidates(raw, [], [onset_frame], env, evidence)
    assert len(recovered) == 3
    assert [row["midi"] for row in recovered] == [60, 64, 67]
    assert 72 not in {row["midi"] for row in recovered}
    assert 76 not in {row["midi"] for row in recovered}
    assert all(row["source"] == "basic_pitch_active_state_reattack" for row in recovered)
    assert all(row["recoveryScore"] >= 0.58 for row in recovered)

    existing = [{"midi": 60, "startSeconds": t}]
    assert active_state_reattack_candidates(raw, existing, [onset_frame], env, evidence) == []
    assert_close(recovery_score(0.8, 0.9, 0.7), 0.81)


def register_fixture() -> None:
    rows = [{"midi": 60, "startSeconds": 1.0}, {"midi": 65, "startSeconds": 1.2}]
    chosen, meta = choose_sequence_register(rows, 0, {48: 1.0, 60: 0.40, 72: 1.0}, {48: True, 60: True, 72: True})
    assert chosen == 60 and meta["reason"] == "NO_CONTEXT"

    contextual = [
        {"midi": 72, "startSeconds": 0.60},
        {"midi": 60, "startSeconds": 1.00},
        {"midi": 72, "startSeconds": 1.40},
    ]
    chosen, meta = choose_sequence_register(contextual, 1, {48: 0.10, 60: 0.45, 72: 0.85}, {48: False, 60: True, 72: True})
    assert chosen == 72 and meta["repaired"] is True
    assert_close(meta["contextCenter"], 72.0)

    chosen, meta = choose_sequence_register(contextual, 1, {48: 0.10, 60: 0.70, 72: 0.82}, {48: False, 60: True, 72: True})
    assert chosen == 60 and meta["repaired"] is False


def subdivision_fixture() -> None:
    env = np.full(320, 0.10, dtype=float)
    env[[10, 35, 58, 90, 105, 145, 175, 210, 250, 285]] = 0.8
    nominal = refine_beat_subdivisions(0.0, 1.0, env)
    assert_close(nominal[0]["seconds"], 0.0)
    assert_close(nominal[-1]["seconds"], 1.0)

    shifted = env.copy()
    first_nom_frame = round(0.25 * 22050 / 256)
    shifted[first_nom_frame] = 0.15
    shifted[first_nom_frame + 2] = 1.2
    refined = refine_beat_subdivisions(0.0, 1.0, shifted)
    assert refined[1]["moved"] is True
    assert refined[1]["selectedFrame"] == first_nom_frame + 2
    times = [row["seconds"] for row in refined]
    assert all(times[i + 1] > times[i] for i in range(len(times) - 1))

    # [0,1,2] must include one sealed extrapolated interval ending at 3.0.
    lattice = build_subdivision_lattice([0.0, 1.0, 2.0], shifted)
    assert len(lattice) == 13
    assert_close(lattice[0], 0.0)
    assert_close(lattice[4], 1.0)
    assert_close(lattice[8], 2.0)
    assert_close(lattice[-1], 3.0)
    assert all(lattice[i + 1] > lattice[i] for i in range(len(lattice) - 1))

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
    step, meta = select_event_step(0.27, simple_lattice, instrument, shared)
    assert step == meta["nearestStep"] == 1
    step, meta = select_event_step(0.385, simple_lattice, instrument, shared)
    assert abs(step - meta["nearestStep"]) <= 1


def bass_state_fixture() -> None:
    midi = np.asarray([40.0] * 6 + [np.nan, np.nan] + [40.0] * 6 + [43.0] * 6, dtype=float)
    vp = np.asarray([0.90] * len(midi), dtype=float)
    states = stable_bass_states(midi, vp)
    assert len(states) == 2
    assert states[0]["midi"] == 40 and states[0]["frameCount"] == 14
    assert states[1]["midi"] == 43 and states[1]["frameCount"] == 6

    env = np.full(80, 0.05, dtype=float)
    env[[5, 20, 35, 50, 65]] = 0.8
    onset1, onset2 = 2, 11
    env[onset1] = 1.0
    env[onset2] = 1.1
    proposals = bass_state_proposals(states, [onset1, onset2], env)
    kinds = [row["kind"] for row in proposals]
    assert "detected_onset" in kinds
    assert "same_pitch_reattack" in kinds
    assert "state_change" in kinds
    assert next(row for row in proposals if row["kind"] == "state_change")["midi"] == 43

    sustain = stable_bass_states(np.asarray([42.0] * 12), np.asarray([0.9] * 12))
    env2 = np.full(40, 0.05, dtype=float)
    env2[2] = 1.0
    single = bass_state_proposals(sustain, [2], env2)
    assert len(single) == 1 and single[0]["kind"] == "detected_onset"

    smoothed = median_smooth_midi(np.asarray([40, 40, 40, 52, 40, 40, 40], dtype=float))
    assert_close(smoothed[3], 40.0)


def grid_cap_fixture() -> None:
    guitar = [{"absoluteGridStep": 8, "midi": 50 + i, "admissionScore": 0.90 - i * 0.01, "confidence": 0.8} for i in range(8)]
    capped_g = cap_guitar_polyphony(guitar)
    assert len(capped_g) == GUITAR_POLYPHONY_CAP == 6
    assert [row["midi"] for row in capped_g] == [50, 51, 52, 53, 54, 55]

    bass = [
        {"absoluteGridStep": 12, "midi": 40, "admissionScore": 0.70, "medianPyinVoicedProbability": 0.8},
        {"absoluteGridStep": 12, "midi": 43, "admissionScore": 0.80, "medianPyinVoicedProbability": 0.7},
    ]
    capped_b = cap_bass_grid(bass)
    assert len(capped_b) == BASS_GRID_CAP == 1 and capped_b[0]["midi"] == 43


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
        "finalBeatExtrapolation": True,
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
