#!/usr/bin/env python3
"""Song-blind V161 event-logic contract fixtures. No song audio or reference data."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from event_logic_v161 import (  # noqa: E402
    BASS_ONSET_RADIUS_FRAMES,
    GUITAR_ONSET_RADIUS_FRAMES,
    bass_admission_score,
    bass_transition_frames,
    cap_bass_grid,
    cap_guitar_polyphony,
    guitar_admission_score,
    median_smooth_midi,
    merge_bass_proposals,
    merge_same_pitch_rows,
    refine_onset_frame,
    support_unit,
    suppress_same_pitch_refractory,
    template_rank,
)


def test_same_pitch_merge() -> None:
    rows = [
        {"midi": 64, "startSeconds": 0.00, "endSeconds": 0.10, "durationSeconds": 0.10, "confidence": 0.5},
        {"midi": 64, "startSeconds": 0.18, "endSeconds": 0.25, "durationSeconds": 0.07, "confidence": 0.7},
        {"midi": 64, "startSeconds": 0.331, "endSeconds": 0.40, "durationSeconds": 0.069, "confidence": 0.6},
        {"midi": 67, "startSeconds": 0.05, "endSeconds": 0.15, "durationSeconds": 0.10, "confidence": 0.8},
    ]
    merged = merge_same_pitch_rows(rows)
    pitch64 = [r for r in merged if r["midi"] == 64]
    assert len(pitch64) == 2
    assert math.isclose(pitch64[0]["startSeconds"], 0.0)
    assert math.isclose(pitch64[0]["endSeconds"], 0.25)
    assert math.isclose(pitch64[0]["confidence"], 0.7)
    assert pitch64[0]["mergedRawCount"] == 2


def test_onset_refinement() -> None:
    env = np.zeros(30, dtype=float)
    env[10] = 0.20
    env[13] = 1.00
    refined, meta = refine_onset_frame(env, 10, GUITAR_ONSET_RADIUS_FRAMES)
    assert refined == 13 and meta["moved"] is True

    weak = np.zeros(30, dtype=float)
    weak[10] = 0.50
    weak[13] = 0.54
    weak[25] = 2.00
    refined, meta = refine_onset_frame(weak, 10, GUITAR_ONSET_RADIUS_FRAMES)
    assert refined == 10 and meta["moved"] is False

    tied = np.zeros(30, dtype=float)
    tied[8] = 1.0
    tied[12] = 1.0
    tied[10] = 0.1
    refined, meta = refine_onset_frame(tied, 10, GUITAR_ONSET_RADIUS_FRAMES)
    assert meta["selectedPeakFrame"] == 8
    assert refined == 8

    bass = np.zeros(40, dtype=float)
    bass[20] = 0.1
    bass[28] = 1.0
    refined, _ = refine_onset_frame(bass, 20, BASS_ONSET_RADIUS_FRAMES)
    assert refined == 28


def test_support_and_rank() -> None:
    pop = np.asarray([0.0, 1.0, 2.0, 4.0, 8.0])
    assert 0.0 < support_unit(2.0, pop) < 1.0
    assert support_unit(100.0, pop) == 1.0
    scores = np.asarray([1.0, 2.0, 3.0, 4.0])
    assert template_rank(scores, 0) == 0.25
    assert template_rank(scores, 3) == 1.0


def test_bass_transition_boundary() -> None:
    midi = np.asarray([40.0] * 8 + [41.49] * 8 + [43.0] * 8)
    vp = np.asarray([0.8] * len(midi))
    smooth = median_smooth_midi(midi)
    proposals = bass_transition_frames(smooth, vp)
    assert all(abs(smooth[i] - smooth[i - 1]) >= 1.5 - 1e-12 for i in proposals)
    assert proposals, proposals

    low_vp = vp.copy()
    low_vp[:] = 0.54
    assert bass_transition_frames(smooth, low_vp) == []


def test_bass_proposal_merge() -> None:
    env = np.zeros(100, dtype=float)
    env[10] = 1.0
    env[12] = 2.0
    env[50] = 0.5
    proposals = merge_bass_proposals([10], [12, 50], env)
    assert proposals[0]["kind"] == "detected_onset"
    assert proposals[0]["frame"] == 10
    assert proposals[-1]["kind"] == "pitch_transition"


def test_refractory() -> None:
    rows = [
        {"midi": 40, "startSeconds": 0.00, "admissionScore": 0.4},
        {"midi": 40, "startSeconds": 0.05, "admissionScore": 0.7},
        {"midi": 40, "startSeconds": 0.20, "admissionScore": 0.5},
    ]
    out = suppress_same_pitch_refractory(rows)
    assert len(out) == 2
    assert math.isclose(out[0]["startSeconds"], 0.05)


def test_polyphony_caps() -> None:
    guitar = [
        {"absoluteGridStep": 10, "midi": 40 + i, "admissionScore": 0.9 - i * 0.01, "confidence": 0.8}
        for i in range(8)
    ]
    capped = cap_guitar_polyphony(guitar)
    assert len(capped) == 6
    assert {r["midi"] for r in capped} == {40, 41, 42, 43, 44, 45}

    bass = [
        {"absoluteGridStep": 4, "midi": 40, "admissionScore": 0.4, "medianPyinVoicedProbability": 0.9},
        {"absoluteGridStep": 4, "midi": 43, "admissionScore": 0.7, "medianPyinVoicedProbability": 0.6},
    ]
    capped_bass = cap_bass_grid(bass)
    assert len(capped_bass) == 1 and capped_bass[0]["midi"] == 43


def test_admission_scores() -> None:
    guitar = guitar_admission_score(1.0, 1.0, 1.0, 1.0, 1.0)
    bass = bass_admission_score(1.0, 1.0, 1.0, 1.0)
    assert math.isclose(guitar, 1.0)
    assert math.isclose(bass, 1.0)
    assert 0.0 <= guitar_admission_score(0.2, 0.4, 0.1, 0.5, 0.1) <= 1.0
    assert 0.0 <= bass_admission_score(0.2, 0.4, 0.1, 0.1) <= 1.0


def main() -> int:
    test_same_pitch_merge()
    test_onset_refinement()
    test_support_and_rank()
    test_bass_transition_boundary()
    test_bass_proposal_merge()
    test_refractory()
    test_polyphony_caps()
    test_admission_scores()
    print("V161 song-blind event logic fixtures: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
