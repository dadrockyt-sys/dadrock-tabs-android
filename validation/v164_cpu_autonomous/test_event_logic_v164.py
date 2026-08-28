#!/usr/bin/env python3
"""Song-blind regression + invariance fixtures for sealed V164 local-evidence logic."""
from __future__ import annotations

import json
import math

import numpy as np

from event_logic_v164 import (
    BASS_GRID_CAP,
    GUITAR_POLYPHONY_CAP,
    LOCAL_HALF_WINDOW_FRAMES,
    active_state_reattack_candidates,
    bass_state_proposals,
    beat_frame_bounds,
    beat_support_unit,
    build_subdivision_lattice,
    cap_bass_grid,
    cap_guitar_polyphony,
    choose_sequence_register,
    event_step_score,
    frame_to_seconds,
    local_positive_quantile,
    local_support_unit,
    local_window_bounds,
    median_smooth_midi,
    onset_evidence,
    recovery_score,
    refine_beat_subdivisions,
    refine_onset_frame,
    segment_guitar_rows,
    select_event_step,
    stable_bass_states,
    supported_attack,
)

REL_TOL = 1e-12
ABS_TOL = 1e-12
REMOTE_SCALE = 1_000_000.0
LOCAL_SCALES = (0.1, 10.0)


def assert_close(a: float, b: float) -> None:
    if not math.isclose(float(a), float(b), rel_tol=REL_TOL, abs_tol=ABS_TOL):
        raise AssertionError((a, b))


def local_population_and_boundary_fixture() -> None:
    env = np.zeros(100, dtype=float)
    assert local_window_bounds(0, len(env)) == (0, 32)
    assert local_window_bounds(99, len(env)) == (67, 99)
    assert local_window_bounds(50, len(env)) == (18, 82)
    threshold, provenance = local_positive_quantile(env, 50, 0.60)
    support, support_provenance = local_support_unit(0.0, env, 50)
    assert threshold is None and support == 0.0
    assert provenance["positiveCount"] == 0
    assert support_provenance["supportScale"] is None
    bad = env.copy()
    bad[10] = np.nan
    try:
        local_support_unit(1.0, bad, 50)
    except RuntimeError:
        pass
    else:
        raise AssertionError("nonfinite envelope must be rejected")


def guitar_segmentation_regression_fixture() -> None:
    env = np.zeros(220, dtype=float)
    env[[15, 45, 75, 105, 135, 165, 195]] = 1.0
    rows = [
        {"midi": 60, "startSeconds": 0.20, "endSeconds": 0.50, "confidence": 0.70},
        {"midi": 60, "startSeconds": 0.58, "endSeconds": 0.80, "confidence": 0.80},
    ]
    weak_frame = round(0.58 * 22050 / 256)
    env[weak_frame - 3 : weak_frame + 4] = 0.10
    merged = segment_guitar_rows(rows, env)
    assert len(merged) == 1
    assert merged[0]["segmentedRawCount"] == 2
    assert_close(merged[0]["endSeconds"], 0.80)

    strong = env.copy()
    strong[weak_frame] = 1.25
    separated = segment_guitar_rows(rows, strong)
    assert len(separated) == 2
    assert separated[1]["reattackEvidence"]["supported"] is True

    overlap = [
        {"midi": 62, "startSeconds": 1.00, "endSeconds": 1.30, "confidence": 0.70},
        {"midi": 62, "startSeconds": 1.20, "endSeconds": 1.45, "confidence": 0.75},
    ]
    assert len(segment_guitar_rows(overlap, strong)) == 1
    distant = [
        {"midi": 64, "startSeconds": 1.60, "endSeconds": 1.80, "confidence": 0.70},
        {"midi": 64, "startSeconds": 1.95, "endSeconds": 2.10, "confidence": 0.75},
    ]
    assert len(segment_guitar_rows(distant, strong)) == 2


def active_state_recovery_regression_fixture() -> None:
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
    assert all(row["source"] == "basic_pitch_active_state_reattack" for row in recovered)
    assert all(row["recoveryScore"] >= 0.58 for row in recovered)
    existing = [{"midi": 60, "startSeconds": t}]
    assert active_state_reattack_candidates(raw, existing, [onset_frame], env, evidence) == []
    assert_close(recovery_score(0.8, 0.9, 0.7), 0.81)


def register_regression_fixture() -> None:
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


def bass_state_regression_fixture() -> None:
    midi = np.asarray([40.0] * 6 + [np.nan, np.nan] + [40.0] * 12 + [43.0] * 6, dtype=float)
    vp = np.asarray([0.90] * len(midi), dtype=float)
    states = stable_bass_states(midi, vp)
    assert len(states) == 2
    assert states[0]["midi"] == 40 and states[0]["frameCount"] == 20
    assert states[1]["midi"] == 43 and states[1]["frameCount"] == 6
    env = np.full(80, 0.05, dtype=float)
    env[[5, 20, 35, 50, 65]] = 0.8
    env[2] = 1.0
    env[11] = 1.1
    proposals = bass_state_proposals(states, [2, 11], env)
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


def grid_cap_regression_fixture() -> None:
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


def supported_attack_remote_invariance_fixture() -> None:
    env = np.full(220, 0.02, dtype=float)
    center = 90
    env[center - 2] = 0.20
    env[center] = 0.35
    env[center + 2] = 1.00
    baseline, meta = supported_attack(env, center, radius=3, positive_q=0.60, minimum_support=0.30)
    assert baseline is True
    lo, hi = meta["normalizationLoFrame"], meta["normalizationHiFrame"]
    remote = env.copy()
    remote[:lo] *= REMOTE_SCALE
    remote[hi + 1 :] *= REMOTE_SCALE
    changed, changed_meta = supported_attack(remote, center, radius=3, positive_q=0.60, minimum_support=0.30)
    assert changed == baseline and changed_meta["peakFrame"] == meta["peakFrame"]
    assert_close(changed_meta["normalizedSupport"], meta["normalizedSupport"])
    assert_close(changed_meta["positiveThreshold"], meta["positiveThreshold"])
    for factor in LOCAL_SCALES:
        scaled = env.copy()
        scaled[lo : hi + 1] *= factor
        decision, scaled_meta = supported_attack(scaled, center, radius=3, positive_q=0.60, minimum_support=0.30)
        assert decision == baseline and scaled_meta["peakFrame"] == meta["peakFrame"]
        assert_close(scaled_meta["normalizedSupport"], meta["normalizedSupport"])
        assert_close(float(scaled_meta["positiveThreshold"]) / factor, meta["positiveThreshold"])


def onset_refinement_remote_invariance_fixture() -> None:
    env = np.full(220, 0.04, dtype=float)
    center = 100
    env[center] = 0.20
    env[center + 2] = 0.90
    refined, meta = refine_onset_frame(env, center, 6)
    assert refined == center + 2 and meta["moved"] is True
    lo, hi = meta["normalizationLoFrame"], meta["normalizationHiFrame"]
    remote = env.copy()
    remote[:lo] *= REMOTE_SCALE
    remote[hi + 1 :] *= REMOTE_SCALE
    refined2, meta2 = refine_onset_frame(remote, center, 6)
    assert refined2 == refined and meta2["moved"] == meta["moved"]
    assert_close(meta2["positiveQ60"], meta["positiveQ60"])


def bass_onset_remote_invariance_fixture() -> None:
    env = np.full(260, 0.03, dtype=float)
    center = 120
    env[center - 1] = 0.5
    env[center + 1] = 1.1
    baseline = onset_evidence(env, center, radius=3, positive_q=0.60)
    lo, hi = baseline["normalizationLoFrame"], baseline["normalizationHiFrame"]
    remote = env.copy()
    remote[:lo] = np.maximum(remote[:lo], 2.0) * REMOTE_SCALE
    remote[hi + 1 :] = np.maximum(remote[hi + 1 :], 2.0) * REMOTE_SCALE
    changed = onset_evidence(remote, center, radius=3, positive_q=0.60)
    assert changed["peakFrame"] == baseline["peakFrame"]
    assert_close(changed["normalizedSupport"], baseline["normalizedSupport"])
    assert_close(changed["positiveThreshold"], baseline["positiveThreshold"])


def bass_proposal_remote_invariance_fixture() -> None:
    states = [{"midi": 40, "startFrame": 70, "endFrameExclusive": 150, "frameCount": 80, "medianVoicedProbability": 0.9}]
    env = np.full(240, 0.04, dtype=float)
    env[80] = 1.0
    env[100] = 1.1
    baseline = bass_state_proposals(states, [80, 100], env)
    assert [row["kind"] for row in baseline] == ["detected_onset", "same_pitch_reattack"]
    lo = min(row["normalizationLoFrame"] for row in baseline)
    hi = max(row["normalizationHiFrame"] for row in baseline)
    remote = env.copy()
    remote[:lo] *= REMOTE_SCALE
    remote[hi + 1 :] *= REMOTE_SCALE
    changed = bass_state_proposals(states, [80, 100], remote)
    assert [(r["frame"], r["kind"], r["midi"]) for r in changed] == [(r["frame"], r["kind"], r["midi"]) for r in baseline]
    for a, b in zip(changed, baseline):
        assert_close(a["onsetSupport"], b["onsetSupport"])


def subdivision_remote_and_scale_invariance_fixture() -> None:
    env = np.full(320, 0.05, dtype=float)
    beat_start, beat_end = 0.0, 1.0
    lo, hi = beat_frame_bounds(beat_start, beat_end, len(env))
    first_nominal = round(0.25 * 22050 / 256)
    env[first_nominal] = 0.10
    env[first_nominal + 2] = 1.20
    env[40] = 0.30
    baseline = refine_beat_subdivisions(beat_start, beat_end, env)
    assert baseline[1]["moved"] is True and baseline[1]["selectedFrame"] == first_nominal + 2
    remote = env.copy()
    remote[hi + 1 :] *= REMOTE_SCALE
    changed = refine_beat_subdivisions(beat_start, beat_end, remote)
    assert changed[1]["moved"] == baseline[1]["moved"]
    assert changed[1]["selectedFrame"] == baseline[1]["selectedFrame"]
    assert_close(changed[1]["seconds"], baseline[1]["seconds"])
    for factor in LOCAL_SCALES:
        scaled = env.copy()
        scaled[lo : hi + 1] *= factor
        got = refine_beat_subdivisions(beat_start, beat_end, scaled)
        assert got[1]["moved"] == baseline[1]["moved"]
        assert got[1]["selectedFrame"] == baseline[1]["selectedFrame"]
        assert_close(got[1]["seconds"], baseline[1]["seconds"])
    lattice = build_subdivision_lattice([0.0, 1.0, 2.0], env)
    assert len(lattice) == 13 and all(lattice[i + 1] > lattice[i] for i in range(len(lattice) - 1))


def event_step_remote_and_scale_invariance_fixture() -> None:
    lattice = [0.0, 0.25, 0.50, 0.75, 1.0]
    instrument = np.full(240, 0.05, dtype=float)
    shared = np.full(240, 0.05, dtype=float)
    near_frame = round(0.25 * 22050 / 256)
    neighbor_frame = round(0.50 * 22050 / 256)
    instrument[near_frame] = shared[near_frame] = 0.25
    instrument[neighbor_frame] = shared[neighbor_frame] = 1.00
    event_time = 0.385
    baseline_step, baseline_meta = select_event_step(event_time, lattice, instrument, shared)
    beat_lo, beat_hi = beat_frame_bounds(0.0, 1.0, len(instrument))
    remote_i, remote_s = instrument.copy(), shared.copy()
    remote_i[beat_hi + 1 :] *= REMOTE_SCALE
    remote_s[beat_hi + 1 :] *= REMOTE_SCALE
    remote_step, remote_meta = select_event_step(event_time, lattice, remote_i, remote_s)
    assert remote_step == baseline_step
    assert remote_meta["winner"]["step"] == baseline_meta["winner"]["step"]
    assert_close(remote_meta["winner"]["instrumentSupport"], baseline_meta["winner"]["instrumentSupport"])
    assert_close(remote_meta["winner"]["sharedSupport"], baseline_meta["winner"]["sharedSupport"])
    for factor in LOCAL_SCALES:
        scaled_i, scaled_s = instrument.copy(), shared.copy()
        scaled_i[beat_lo : beat_hi + 1] *= factor
        scaled_s[beat_lo : beat_hi + 1] *= factor
        step, meta = select_event_step(event_time, lattice, scaled_i, scaled_s)
        assert step == baseline_step and meta["winner"]["step"] == baseline_meta["winner"]["step"]
        assert_close(meta["winner"]["instrumentSupport"], baseline_meta["winner"]["instrumentSupport"])
        assert_close(meta["winner"]["sharedSupport"], baseline_meta["winner"]["sharedSupport"])
    score_nearest = event_step_score(0.25, 0.25, 0.25, 0.20, 0.20)
    score_neighbor = event_step_score(0.25, 0.26, 0.25, 1.00, 1.00)
    assert score_neighbor > score_nearest


def beat_support_zero_fixture() -> None:
    env = np.zeros(120, dtype=float)
    support, provenance = beat_support_unit(0.0, env, 0.0, 0.5)
    assert support == 0.0 and provenance["positiveCount"] == 0 and provenance["supportScale"] is None


def main() -> int:
    assert LOCAL_HALF_WINDOW_FRAMES == 32
    local_population_and_boundary_fixture()
    guitar_segmentation_regression_fixture()
    active_state_recovery_regression_fixture()
    register_regression_fixture()
    bass_state_regression_fixture()
    grid_cap_regression_fixture()
    supported_attack_remote_invariance_fixture()
    onset_refinement_remote_invariance_fixture()
    bass_onset_remote_invariance_fixture()
    bass_proposal_remote_invariance_fixture()
    subdivision_remote_and_scale_invariance_fixture()
    event_step_remote_and_scale_invariance_fixture()
    beat_support_zero_fixture()
    print(json.dumps({
        "schema": "dadrock.tabs.v164.local-evidence-static-test.v2",
        "validation": "PASS",
        "localHalfWindowFrames": 32,
        "remoteScaleFactor": REMOTE_SCALE,
        "localScaleFactors": list(LOCAL_SCALES),
        "v162GuitarSegmentationRegression": True,
        "v162ActiveStateRecoveryRegression": True,
        "v162RegisterRegression": True,
        "v162BassStateRegression": True,
        "v162GridCapRegression": True,
        "eventRemoteInvariant": True,
        "onsetRefinementRemoteInvariant": True,
        "bassOnsetRemoteInvariant": True,
        "bassProposalRemoteInvariant": True,
        "subdivisionRemoteInvariant": True,
        "eventStepRemoteInvariant": True,
        "localScaleInvariant": True,
        "zeroFallbackDeterministic": True,
        "boundaryClippingDeterministic": True,
        "nonfiniteRejected": True,
        "songAudioRead": False,
        "professionalReferenceRead": False,
        "frozenScorerRead": False,
        "V163CandidateRead": False,
        "V163ScoreRead": False,
        "gpuUsed": False
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
