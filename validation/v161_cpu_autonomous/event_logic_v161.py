#!/usr/bin/env python3
"""Pure deterministic V161 event logic; safe for song-blind static fixtures."""
from __future__ import annotations

import math
from typing import Any, Iterable

import numpy as np

EPS = 1e-12
SR = 22050
HOP = 256

GUITAR_MERGE_GAP_SECONDS = 0.080
GUITAR_ONSET_RADIUS_FRAMES = 6
BASS_ONSET_RADIUS_FRAMES = 8
ONSET_MOVE_POSITIVE_QUANTILE = 0.60
ONSET_MOVE_MIN_RATIO = 1.10
BASS_TRANSITION_SEMITONES = 1.50
BASS_TRANSITION_MIN_VOICED = 0.55
BASS_TRANSITION_MIN_IOI_SECONDS = 0.060
BASS_PROPOSAL_MERGE_SECONDS = 0.045
BASS_RAW_REFRACTORY_SECONDS = 0.060
GUITAR_POLYPHONY_CAP = 6
BASS_GRID_CAP = 1


def seconds_to_frames(seconds: float) -> int:
    return max(1, int(math.ceil(float(seconds) * SR / HOP)))


def positive_quantile(values: np.ndarray, q: float) -> float | None:
    x = np.asarray(values, dtype=float)
    positive = x[np.isfinite(x) & (x > 0.0)]
    if positive.size == 0:
        return None
    return float(np.quantile(positive, q))


def support_unit(value: float, population: np.ndarray) -> float:
    x = np.asarray(population, dtype=float)
    positive = x[np.isfinite(x) & (x > 0.0)]
    if positive.size == 0:
        return 0.0
    scale = float(np.quantile(positive, 0.95))
    if not math.isfinite(scale) or scale <= EPS:
        return 0.0
    return float(np.clip(float(value) / scale, 0.0, 1.0))


def template_rank(scores: np.ndarray, selected_index: int) -> float:
    x = np.asarray(scores, dtype=float)
    if x.size == 0 or not np.all(np.isfinite(x)):
        raise RuntimeError("template_rank requires finite nonempty scores")
    idx = int(selected_index)
    if idx < 0 or idx >= x.size:
        raise RuntimeError("template_rank selected index out of range")
    selected = float(x[idx])
    return float(np.count_nonzero(x <= selected + EPS) / x.size)


def refine_onset_frame(env: np.ndarray, original_frame: int, radius: int) -> tuple[int, dict[str, Any]]:
    x = np.asarray(env, dtype=float)
    if x.size == 0 or not np.all(np.isfinite(x)):
        raise RuntimeError("refine_onset_frame requires finite nonempty envelope")
    original = int(np.clip(int(original_frame), 0, len(x) - 1))
    lo = max(0, original - int(radius))
    hi = min(len(x) - 1, original + int(radius))
    threshold = positive_quantile(x, ONSET_MOVE_POSITIVE_QUANTILE)
    current = float(x[original])
    candidates = list(range(lo, hi + 1))
    peak = max(float(x[i]) for i in candidates)
    peak_frames = [i for i in candidates if abs(float(x[i]) - peak) <= EPS]
    selected = min(peak_frames, key=lambda i: (abs(i - original), i))
    moved = bool(
        threshold is not None
        and peak >= threshold - EPS
        and peak >= ONSET_MOVE_MIN_RATIO * current - EPS
        and selected != original
    )
    refined = selected if moved else original
    return refined, {
        "originalFrame": original,
        "selectedPeakFrame": selected,
        "refinedFrame": refined,
        "searchRadiusFrames": int(radius),
        "currentOnsetStrength": current,
        "peakOnsetStrength": peak,
        "positiveQ60": threshold,
        "moved": moved,
    }


def merge_same_pitch_rows(rows: Iterable[dict[str, Any]], gap_seconds: float = GUITAR_MERGE_GAP_SECONDS) -> list[dict[str, Any]]:
    ordered = sorted((dict(r) for r in rows), key=lambda r: (int(r["midi"]), float(r["startSeconds"]), float(r["endSeconds"])))
    merged: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for row in ordered:
        if current is None:
            current = row
            continue
        same_pitch = int(row["midi"]) == int(current["midi"])
        gap = float(row["startSeconds"]) - float(current["endSeconds"])
        if same_pitch and gap <= float(gap_seconds) + EPS:
            current["startSeconds"] = min(float(current["startSeconds"]), float(row["startSeconds"]))
            current["endSeconds"] = max(float(current["endSeconds"]), float(row["endSeconds"]))
            current["durationSeconds"] = max(0.0, float(current["endSeconds"]) - float(current["startSeconds"]))
            current["confidence"] = max(float(current.get("confidence", 0.0)), float(row.get("confidence", 0.0)))
            current["mergedRawCount"] = int(current.get("mergedRawCount", 1)) + int(row.get("mergedRawCount", 1))
        else:
            current.setdefault("mergedRawCount", 1)
            merged.append(current)
            current = row
    if current is not None:
        current.setdefault("mergedRawCount", 1)
        merged.append(current)
    return sorted(merged, key=lambda r: (float(r["startSeconds"]), int(r["midi"]), float(r["endSeconds"])))


def median_smooth_midi(midi: np.ndarray, window: int = 5) -> np.ndarray:
    x = np.asarray(midi, dtype=float)
    if window != 5:
        raise RuntimeError("V161 median smoothing window is sealed at 5")
    out = np.full_like(x, np.nan, dtype=float)
    radius = window // 2
    for i in range(len(x)):
        lo = max(0, i - radius)
        hi = min(len(x), i + radius + 1)
        finite = x[lo:hi][np.isfinite(x[lo:hi])]
        if finite.size:
            out[i] = float(np.median(finite))
    return out


def bass_transition_frames(smoothed_midi: np.ndarray, voiced_prob: np.ndarray) -> list[int]:
    midi = np.asarray(smoothed_midi, dtype=float)
    vp = np.asarray(voiced_prob, dtype=float)
    if midi.shape != vp.shape:
        raise RuntimeError("bass transition MIDI/voiced arrays must align")
    proposals: list[int] = []
    min_frames = seconds_to_frames(BASS_TRANSITION_MIN_IOI_SECONDS)
    for frame in range(1, len(midi)):
        if not (math.isfinite(float(midi[frame - 1])) and math.isfinite(float(midi[frame]))):
            continue
        left_vp = float(vp[frame - 1]) if math.isfinite(float(vp[frame - 1])) else 0.0
        right_vp = float(vp[frame]) if math.isfinite(float(vp[frame])) else 0.0
        if min(left_vp, right_vp) + EPS < BASS_TRANSITION_MIN_VOICED:
            continue
        if abs(float(midi[frame]) - float(midi[frame - 1])) + EPS < BASS_TRANSITION_SEMITONES:
            continue
        if proposals and frame - proposals[-1] < min_frames:
            continue
        proposals.append(frame)
    return proposals


def merge_bass_proposals(onsets: Iterable[int], transitions: Iterable[int], onset_env: np.ndarray) -> list[dict[str, Any]]:
    env = np.asarray(onset_env, dtype=float)
    if env.size == 0 or not np.all(np.isfinite(env)):
        raise RuntimeError("merge_bass_proposals requires finite onset envelope")
    merge_frames = seconds_to_frames(BASS_PROPOSAL_MERGE_SECONDS)
    candidates: list[dict[str, Any]] = []
    for frame in onsets:
        f = int(np.clip(int(frame), 0, len(env) - 1))
        candidates.append({"frame": f, "kind": "detected_onset", "priority": 0, "onsetStrength": float(env[f])})
    for frame in transitions:
        f = int(np.clip(int(frame), 0, len(env) - 1))
        candidates.append({"frame": f, "kind": "pitch_transition", "priority": 1, "onsetStrength": float(env[f])})
    candidates.sort(key=lambda r: (int(r["frame"]), int(r["priority"]), -float(r["onsetStrength"])))
    groups: list[list[dict[str, Any]]] = []
    for row in candidates:
        if not groups or int(row["frame"]) - max(int(x["frame"]) for x in groups[-1]) > merge_frames:
            groups.append([row])
        else:
            groups[-1].append(row)
    out: list[dict[str, Any]] = []
    for group in groups:
        winner = min(group, key=lambda r: (int(r["priority"]), -float(r["onsetStrength"]), int(r["frame"])))
        item = dict(winner)
        item["mergedProposalCount"] = len(group)
        out.append(item)
    return sorted(out, key=lambda r: int(r["frame"]))


def suppress_same_pitch_refractory(rows: Iterable[dict[str, Any]], seconds: float = BASS_RAW_REFRACTORY_SECONDS) -> list[dict[str, Any]]:
    ordered = sorted((dict(r) for r in rows), key=lambda r: (int(r["midi"]), float(r["startSeconds"]), -float(r.get("admissionScore", 0.0))))
    by_midi: dict[int, list[dict[str, Any]]] = {}
    for row in ordered:
        midi = int(row["midi"])
        bucket = by_midi.setdefault(midi, [])
        if bucket and float(row["startSeconds"]) - float(bucket[-1]["startSeconds"]) <= seconds + EPS:
            old = bucket[-1]
            old_key = (-float(old.get("admissionScore", 0.0)), float(old["startSeconds"]))
            new_key = (-float(row.get("admissionScore", 0.0)), float(row["startSeconds"]))
            if new_key < old_key:
                bucket[-1] = row
        else:
            bucket.append(row)
    result = [row for bucket in by_midi.values() for row in bucket]
    return sorted(result, key=lambda r: (float(r["startSeconds"]), int(r["midi"])))


def cap_guitar_polyphony(rows: Iterable[dict[str, Any]], cap: int = GUITAR_POLYPHONY_CAP) -> list[dict[str, Any]]:
    by_step: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        by_step.setdefault(int(row["absoluteGridStep"]), []).append(dict(row))
    out: list[dict[str, Any]] = []
    for step in sorted(by_step):
        ranked = sorted(
            by_step[step],
            key=lambda r: (-float(r.get("admissionScore", 0.0)), -float(r.get("confidence", 0.0)), int(r["midi"])),
        )
        out.extend(ranked[:cap])
    return sorted(out, key=lambda r: (int(r["absoluteGridStep"]), int(r["midi"])))


def cap_bass_grid(rows: Iterable[dict[str, Any]], cap: int = BASS_GRID_CAP) -> list[dict[str, Any]]:
    by_step: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        by_step.setdefault(int(row["absoluteGridStep"]), []).append(dict(row))
    out: list[dict[str, Any]] = []
    for step in sorted(by_step):
        ranked = sorted(
            by_step[step],
            key=lambda r: (-float(r.get("admissionScore", 0.0)), -float(r.get("medianPyinVoicedProbability", 0.0)), int(r["midi"])),
        )
        out.extend(ranked[:cap])
    return sorted(out, key=lambda r: (int(r["absoluteGridStep"]), int(r["midi"])))


def guitar_admission_score(confidence: float, rank: float, onset: float, persistence: float, activity: float) -> float:
    values = [confidence, rank, onset, persistence, activity]
    if not all(math.isfinite(float(x)) for x in values):
        raise RuntimeError("nonfinite Guitar admission input")
    score = 0.45 * confidence + 0.25 * rank + 0.15 * onset + 0.10 * persistence + 0.05 * activity
    return float(np.clip(score, 0.0, 1.0))


def bass_admission_score(voiced: float, rank: float, onset: float, activity: float) -> float:
    values = [voiced, rank, onset, activity]
    if not all(math.isfinite(float(x)) for x in values):
        raise RuntimeError("nonfinite Bass admission input")
    score = 0.40 * voiced + 0.35 * rank + 0.15 * onset + 0.10 * activity
    return float(np.clip(score, 0.0, 1.0))
