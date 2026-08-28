#!/usr/bin/env python3
"""Pure deterministic V164 local-evidence helpers for song-blind synthetic tests.

This module intentionally contains no song I/O, model inference, scorer access, or
professional-reference access. It implements only the local-normalization primitives
sealed by debug/v164-cpu-autonomous/implementation-contract.json.
"""
from __future__ import annotations

import math
from typing import Any, Iterable

import numpy as np

EPS = 1e-12
SR = 22050
HOP = 256
LOCAL_HALF_WINDOW_FRAMES = 32
SUPPORT_SCALE_QUANTILE = 0.95
SUBDIV_SEARCH_RADIUS_FRAMES = 3
SUBDIV_POSITIVE_QUANTILE = 0.55
SUBDIV_MOVE_MIN_RATIO = 1.05
EVENT_NON_NEAREST_MARGIN = 0.05


def _finite_env(env: np.ndarray) -> np.ndarray:
    x = np.asarray(env, dtype=float)
    if x.ndim != 1 or x.size == 0 or not np.all(np.isfinite(x)):
        raise RuntimeError("V164 onset envelope must be finite, one-dimensional, and nonempty")
    return x


def frame_to_seconds(frame: int) -> float:
    return float(int(frame) * HOP / SR)


def seconds_to_nearest_frame(seconds: float, n_frames: int) -> int:
    if n_frames <= 0:
        raise RuntimeError("n_frames must be positive")
    if not math.isfinite(float(seconds)):
        raise RuntimeError("seconds must be finite")
    return int(np.clip(round(float(seconds) * SR / HOP), 0, n_frames - 1))


def local_window_bounds(center_frame: int, n_frames: int, half_window_frames: int = LOCAL_HALF_WINDOW_FRAMES) -> tuple[int, int]:
    if n_frames <= 0:
        raise RuntimeError("n_frames must be positive")
    if half_window_frames != LOCAL_HALF_WINDOW_FRAMES:
        raise RuntimeError("V164 local half-window is sealed at 32 frames")
    center = int(np.clip(int(center_frame), 0, n_frames - 1))
    return max(0, center - half_window_frames), min(n_frames - 1, center + half_window_frames)


def local_positive_population(
    env: np.ndarray,
    center_frame: int,
    half_window_frames: int = LOCAL_HALF_WINDOW_FRAMES,
) -> tuple[np.ndarray, dict[str, int]]:
    x = _finite_env(env)
    lo, hi = local_window_bounds(center_frame, len(x), half_window_frames)
    window = x[lo : hi + 1]
    positive = window[window > 0.0]
    return positive, {"loFrame": int(lo), "hiFrame": int(hi), "positiveCount": int(positive.size)}


def local_positive_quantile(env: np.ndarray, center_frame: int, q: float) -> tuple[float | None, dict[str, int]]:
    if not 0.0 <= float(q) <= 1.0:
        raise RuntimeError("quantile must be in [0,1]")
    positive, provenance = local_positive_population(env, center_frame)
    if positive.size == 0:
        return None, provenance
    return float(np.quantile(positive, float(q))), provenance


def local_support_unit(value: float, env: np.ndarray, center_frame: int) -> tuple[float, dict[str, Any]]:
    if not math.isfinite(float(value)):
        raise RuntimeError("support value must be finite")
    positive, provenance = local_positive_population(env, center_frame)
    if positive.size == 0:
        return 0.0, {**provenance, "supportScale": None}
    scale = float(np.quantile(positive, SUPPORT_SCALE_QUANTILE))
    if not math.isfinite(scale) or scale <= EPS:
        return 0.0, {**provenance, "supportScale": scale}
    support = float(np.clip(float(value) / scale, 0.0, 1.0))
    return support, {**provenance, "supportScale": scale}


def local_peak(env: np.ndarray, center: int, radius: int) -> tuple[int, float]:
    x = _finite_env(env)
    c = int(np.clip(int(center), 0, len(x) - 1))
    lo = max(0, c - int(radius))
    hi = min(len(x) - 1, c + int(radius))
    peak = max(float(x[i]) for i in range(lo, hi + 1))
    frames = [i for i in range(lo, hi + 1) if abs(float(x[i]) - peak) <= EPS]
    frame = min(frames, key=lambda i: (abs(i - c), i))
    return frame, peak


def onset_evidence(
    env: np.ndarray,
    center_frame: int,
    *,
    radius: int,
    positive_q: float,
) -> dict[str, Any]:
    x = _finite_env(env)
    peak_frame, peak = local_peak(x, center_frame, radius)
    threshold, threshold_provenance = local_positive_quantile(x, center_frame, positive_q)
    support, support_provenance = local_support_unit(peak, x, center_frame)
    if threshold_provenance != {k: support_provenance[k] for k in ("loFrame", "hiFrame", "positiveCount")}:
        raise RuntimeError("local normalization provenance mismatch")
    return {
        "centerFrame": int(np.clip(int(center_frame), 0, len(x) - 1)),
        "peakFrame": int(peak_frame),
        "peakStrength": float(peak),
        "positiveThreshold": threshold,
        "normalizedSupport": float(support),
        "normalizationLoFrame": int(support_provenance["loFrame"]),
        "normalizationHiFrame": int(support_provenance["hiFrame"]),
        "normalizationPositiveCount": int(support_provenance["positiveCount"]),
        "normalizationSupportScale": support_provenance["supportScale"],
    }


def supported_attack(
    env: np.ndarray,
    center_frame: int,
    *,
    radius: int,
    positive_q: float,
    minimum_support: float,
) -> tuple[bool, dict[str, Any]]:
    evidence = onset_evidence(env, center_frame, radius=radius, positive_q=positive_q)
    threshold = evidence["positiveThreshold"]
    supported = bool(
        threshold is not None
        and float(evidence["peakStrength"]) + EPS >= float(threshold)
        and float(evidence["normalizedSupport"]) + EPS >= float(minimum_support)
    )
    evidence["supported"] = supported
    return supported, evidence


def beat_frame_bounds(beat_start: float, beat_end: float, n_frames: int) -> tuple[int, int]:
    if n_frames <= 0:
        raise RuntimeError("n_frames must be positive")
    if not math.isfinite(float(beat_start)) or not math.isfinite(float(beat_end)) or float(beat_end) <= float(beat_start):
        raise RuntimeError("invalid beat interval")
    lo = seconds_to_nearest_frame(float(beat_start), n_frames)
    hi = seconds_to_nearest_frame(float(beat_end), n_frames)
    if hi < lo:
        raise RuntimeError("beat frame bounds reversed")
    return int(lo), int(hi)


def beat_positive_population(env: np.ndarray, beat_start: float, beat_end: float) -> tuple[np.ndarray, dict[str, int]]:
    x = _finite_env(env)
    lo, hi = beat_frame_bounds(beat_start, beat_end, len(x))
    population = x[lo : hi + 1]
    positive = population[population > 0.0]
    return positive, {"loFrame": lo, "hiFrame": hi, "positiveCount": int(positive.size)}


def beat_positive_quantile(env: np.ndarray, beat_start: float, beat_end: float, q: float) -> tuple[float | None, dict[str, int]]:
    if not 0.0 <= float(q) <= 1.0:
        raise RuntimeError("quantile must be in [0,1]")
    positive, provenance = beat_positive_population(env, beat_start, beat_end)
    if positive.size == 0:
        return None, provenance
    return float(np.quantile(positive, float(q))), provenance


def beat_support_unit(value: float, env: np.ndarray, beat_start: float, beat_end: float) -> tuple[float, dict[str, Any]]:
    if not math.isfinite(float(value)):
        raise RuntimeError("support value must be finite")
    positive, provenance = beat_positive_population(env, beat_start, beat_end)
    if positive.size == 0:
        return 0.0, {**provenance, "supportScale": None}
    scale = float(np.quantile(positive, SUPPORT_SCALE_QUANTILE))
    if not math.isfinite(scale) or scale <= EPS:
        return 0.0, {**provenance, "supportScale": scale}
    return float(np.clip(float(value) / scale, 0.0, 1.0)), {**provenance, "supportScale": scale}


def refine_beat_subdivisions(beat_start: float, beat_end: float, shared_env: np.ndarray) -> list[dict[str, Any]]:
    x = _finite_env(shared_env)
    if not math.isfinite(float(beat_start)) or not math.isfinite(float(beat_end)) or beat_end <= beat_start:
        raise RuntimeError("invalid beat interval")
    period = float(beat_end - beat_start)
    nominal = [float(beat_start + j * period / 4.0) for j in range(5)]
    threshold, provenance = beat_positive_quantile(x, beat_start, beat_end, SUBDIV_POSITIVE_QUANTILE)
    out: list[dict[str, Any]] = [{
        "subdivision": 0,
        "nominalSeconds": nominal[0],
        "seconds": nominal[0],
        "moved": False,
        "normalizationLoFrame": provenance["loFrame"],
        "normalizationHiFrame": provenance["hiFrame"],
        "normalizationPositiveCount": provenance["positiveCount"],
    }]
    for j in (1, 2, 3):
        nominal_frame = seconds_to_nearest_frame(nominal[j], len(x))
        lo = max(0, nominal_frame - SUBDIV_SEARCH_RADIUS_FRAMES)
        hi = min(len(x) - 1, nominal_frame + SUBDIV_SEARCH_RADIUS_FRAMES)
        left_mid = 0.5 * (nominal[j - 1] + nominal[j])
        right_mid = 0.5 * (nominal[j] + nominal[j + 1])
        candidates = [f for f in range(lo, hi + 1) if left_mid - EPS <= frame_to_seconds(f) <= right_mid + EPS]
        if not candidates:
            out.append({
                "subdivision": j,
                "nominalSeconds": nominal[j],
                "seconds": nominal[j],
                "moved": False,
                "normalizationLoFrame": provenance["loFrame"],
                "normalizationHiFrame": provenance["hiFrame"],
                "normalizationPositiveCount": provenance["positiveCount"],
            })
            continue
        peak = max(float(x[f]) for f in candidates)
        peak_frames = [f for f in candidates if abs(float(x[f]) - peak) <= EPS]
        selected = min(peak_frames, key=lambda f: (abs(f - nominal_frame), f))
        nominal_strength = float(x[nominal_frame])
        moved = bool(
            threshold is not None
            and peak + EPS >= float(threshold)
            and peak + EPS >= SUBDIV_MOVE_MIN_RATIO * nominal_strength
            and selected != nominal_frame
        )
        seconds = frame_to_seconds(selected) if moved else nominal[j]
        out.append({
            "subdivision": j,
            "nominalSeconds": nominal[j],
            "seconds": float(seconds),
            "moved": moved,
            "nominalFrame": nominal_frame,
            "selectedFrame": int(selected),
            "peakStrength": float(peak),
            "nominalStrength": nominal_strength,
            "positiveThreshold": threshold,
            "normalizationLoFrame": provenance["loFrame"],
            "normalizationHiFrame": provenance["hiFrame"],
            "normalizationPositiveCount": provenance["positiveCount"],
        })
    out.append({
        "subdivision": 4,
        "nominalSeconds": nominal[4],
        "seconds": nominal[4],
        "moved": False,
        "normalizationLoFrame": provenance["loFrame"],
        "normalizationHiFrame": provenance["hiFrame"],
        "normalizationPositiveCount": provenance["positiveCount"],
    })
    times = [float(row["seconds"]) for row in out]
    if not all(times[i + 1] > times[i] + EPS for i in range(len(times) - 1)):
        raise RuntimeError("refined subdivision interval is not strictly increasing")
    return out


def extrapolated_final_beat(beat_times: Iterable[float]) -> float:
    beats = np.asarray([float(x) for x in beat_times], dtype=float)
    if len(beats) < 2 or not np.all(np.isfinite(beats)) or not np.all(np.diff(beats) > 0.0):
        raise RuntimeError("invalid beat times for final extrapolation")
    ibis = np.diff(beats)
    period = float(np.median(ibis[-min(8, len(ibis)) :]))
    if not math.isfinite(period) or period <= 0.0:
        raise RuntimeError("invalid final beat extrapolation period")
    return float(beats[-1] + period)


def build_subdivision_lattice(beat_times: Iterable[float], shared_env: np.ndarray) -> list[float]:
    beats = [float(x) for x in beat_times]
    if len(beats) < 2 or not all(math.isfinite(x) for x in beats) or not all(beats[i + 1] > beats[i] for i in range(len(beats) - 1)):
        raise RuntimeError("invalid beat times")
    extended = beats + [extrapolated_final_beat(beats)]
    lattice: list[float] = []
    for i in range(len(extended) - 1):
        interval = refine_beat_subdivisions(extended[i], extended[i + 1], shared_env)
        lattice.extend(float(row["seconds"]) for row in interval[:4])
    lattice.append(float(extended[-1]))
    if not all(lattice[i + 1] > lattice[i] + EPS for i in range(len(lattice) - 1)):
        raise RuntimeError("subdivision lattice not strictly increasing")
    return lattice


def event_step_score(event_time: float, step_time: float, nominal_substep: float, instrument_support: float, shared_support: float) -> float:
    temporal = float(np.clip(1.0 - abs(float(event_time) - float(step_time)) / (0.75 * float(nominal_substep)), 0.0, 1.0))
    return float(np.clip(0.70 * temporal + 0.20 * float(instrument_support) + 0.10 * float(shared_support), 0.0, 1.0))


def _candidate_beat_bounds(lattice: list[float], step: int) -> tuple[int, float, float]:
    if len(lattice) < 5 or (len(lattice) - 1) % 4 != 0:
        raise RuntimeError("V164 lattice must contain complete four-subdivision beats plus terminal endpoint")
    beat_count = (len(lattice) - 1) // 4
    beat = min(int(step) // 4, beat_count - 1)
    return beat, float(lattice[4 * beat]), float(lattice[4 * (beat + 1)])


def select_event_step(event_time: float, lattice: list[float], instrument_env: np.ndarray, shared_env: np.ndarray) -> tuple[int, dict[str, Any]]:
    inst_env = _finite_env(instrument_env)
    shr_env = _finite_env(shared_env)
    times = np.asarray(lattice, dtype=float)
    if len(times) < 5 or (len(times) - 1) % 4 != 0 or not np.all(np.isfinite(times)) or not np.all(np.diff(times) > 0.0):
        raise RuntimeError("invalid V164 lattice")
    nearest = int(np.argmin(np.abs(times - float(event_time))))
    candidates = [k for k in (nearest - 1, nearest, nearest + 1) if 0 <= k < len(times)]
    rows: list[dict[str, Any]] = []
    for k in candidates:
        if k == 0:
            nominal_sub = float(times[1] - times[0])
        elif k == len(times) - 1:
            nominal_sub = float(times[-1] - times[-2])
        else:
            nominal_sub = 0.5 * float(times[k + 1] - times[k - 1])
        beat_index, beat_start, beat_end = _candidate_beat_bounds(list(times), k)
        inst_frame = seconds_to_nearest_frame(float(times[k]), len(inst_env))
        shared_frame = seconds_to_nearest_frame(float(times[k]), len(shr_env))
        inst_support, inst_prov = beat_support_unit(float(inst_env[inst_frame]), inst_env, beat_start, beat_end)
        shared_support, shared_prov = beat_support_unit(float(shr_env[shared_frame]), shr_env, beat_start, beat_end)
        score = event_step_score(event_time, float(times[k]), nominal_sub, inst_support, shared_support)
        rows.append({
            "step": int(k),
            "score": float(score),
            "instrumentSupport": float(inst_support),
            "sharedSupport": float(shared_support),
            "time": float(times[k]),
            "normalizationBeatIndex": int(beat_index),
            "instrumentNormalizationLoFrame": int(inst_prov["loFrame"]),
            "instrumentNormalizationHiFrame": int(inst_prov["hiFrame"]),
            "sharedNormalizationLoFrame": int(shared_prov["loFrame"]),
            "sharedNormalizationHiFrame": int(shared_prov["hiFrame"]),
        })
    nearest_row = next(row for row in rows if int(row["step"]) == nearest)
    winner = sorted(rows, key=lambda r: (-float(r["score"]), abs(int(r["step"]) - nearest), int(r["step"])))[0]
    if int(winner["step"]) != nearest and float(winner["score"]) + EPS < float(nearest_row["score"]) + EVENT_NON_NEAREST_MARGIN:
        winner = nearest_row
    return int(winner["step"]), {"nearestStep": nearest, "winner": dict(winner), "candidates": rows}
