#!/usr/bin/env python3
"""Song-blind synthetic invariance fixtures for sealed V164 local-evidence logic."""
from __future__ import annotations

import json
import math

import numpy as np

from event_logic_v164 import (
    LOCAL_HALF_WINDOW_FRAMES,
    beat_frame_bounds,
    beat_support_unit,
    local_positive_quantile,
    local_support_unit,
    local_window_bounds,
    onset_evidence,
    refine_beat_subdivisions,
    select_event_step,
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
    assert threshold is None
    assert support == 0.0
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
    assert changed == baseline
    assert changed_meta["peakFrame"] == meta["peakFrame"]
    assert_close(changed_meta["normalizedSupport"], meta["normalizedSupport"])
    assert_close(changed_meta["positiveThreshold"], meta["positiveThreshold"])

    for factor in LOCAL_SCALES:
        scaled = env.copy()
        scaled[lo : hi + 1] *= factor
        decision, scaled_meta = supported_attack(scaled, center, radius=3, positive_q=0.60, minimum_support=0.30)
        assert decision == baseline
        assert scaled_meta["peakFrame"] == meta["peakFrame"]
        assert_close(scaled_meta["normalizedSupport"], meta["normalizedSupport"])
        assert_close(float(scaled_meta["positiveThreshold"]) / factor, meta["positiveThreshold"])


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


def subdivision_remote_and_scale_invariance_fixture() -> None:
    env = np.full(320, 0.05, dtype=float)
    beat_start, beat_end = 0.0, 1.0
    lo, hi = beat_frame_bounds(beat_start, beat_end, len(env))
    first_nominal = round(0.25 * 22050 / 256)
    env[first_nominal] = 0.10
    env[first_nominal + 2] = 1.20
    env[40] = 0.30
    baseline = refine_beat_subdivisions(beat_start, beat_end, env)
    assert baseline[1]["moved"] is True
    assert baseline[1]["selectedFrame"] == first_nominal + 2

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

    remote_i = instrument.copy()
    remote_s = shared.copy()
    remote_i[beat_hi + 1 :] *= REMOTE_SCALE
    remote_s[beat_hi + 1 :] *= REMOTE_SCALE
    remote_step, remote_meta = select_event_step(event_time, lattice, remote_i, remote_s)
    assert remote_step == baseline_step
    assert remote_meta["winner"]["step"] == baseline_meta["winner"]["step"]
    assert_close(remote_meta["winner"]["instrumentSupport"], baseline_meta["winner"]["instrumentSupport"])
    assert_close(remote_meta["winner"]["sharedSupport"], baseline_meta["winner"]["sharedSupport"])

    for factor in LOCAL_SCALES:
        scaled_i = instrument.copy()
        scaled_s = shared.copy()
        scaled_i[beat_lo : beat_hi + 1] *= factor
        scaled_s[beat_lo : beat_hi + 1] *= factor
        step, meta = select_event_step(event_time, lattice, scaled_i, scaled_s)
        assert step == baseline_step
        assert meta["winner"]["step"] == baseline_meta["winner"]["step"]
        assert_close(meta["winner"]["instrumentSupport"], baseline_meta["winner"]["instrumentSupport"])
        assert_close(meta["winner"]["sharedSupport"], baseline_meta["winner"]["sharedSupport"])


def beat_support_zero_fixture() -> None:
    env = np.zeros(120, dtype=float)
    support, provenance = beat_support_unit(0.0, env, 0.0, 0.5)
    assert support == 0.0
    assert provenance["positiveCount"] == 0
    assert provenance["supportScale"] is None


def main() -> int:
    assert LOCAL_HALF_WINDOW_FRAMES == 32
    local_population_and_boundary_fixture()
    supported_attack_remote_invariance_fixture()
    bass_onset_remote_invariance_fixture()
    subdivision_remote_and_scale_invariance_fixture()
    event_step_remote_and_scale_invariance_fixture()
    beat_support_zero_fixture()
    print(json.dumps({
        "schema": "dadrock.tabs.v164.local-evidence-static-test.v1",
        "validation": "PASS",
        "localHalfWindowFrames": 32,
        "remoteScaleFactor": REMOTE_SCALE,
        "localScaleFactors": list(LOCAL_SCALES),
        "eventRemoteInvariant": True,
        "bassOnsetRemoteInvariant": True,
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
