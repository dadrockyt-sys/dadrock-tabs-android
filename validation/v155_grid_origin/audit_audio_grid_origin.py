#!/usr/bin/env python3
"""Reference-blind CPU audit for audio-to-score grid origin.

This script reads only the exact historical audio and the already-consumed,
reference-free V154 generated stream for a latency diagnostic. It never reads
professional reference files and never calls a scorer.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import wave
from pathlib import Path

import numpy as np

TEMPO_BPM = 129.19921875
STEPS_PER_BEAT = 4
STEP_SECONDS = (60.0 / TEMPO_BPM) / STEPS_PER_BEAT
BEAT_SECONDS = 60.0 / TEMPO_BPM
SAMPLE_RATE = 44100
FRAME = 2048
HOP = 256
HOP_SECONDS = HOP / SAMPLE_RATE
ACTIVITY_NOISE_PERCENTILE = 5.0
ACTIVITY_THRESHOLD_DB_ABOVE_NOISE = 12.0
ACTIVITY_WINDOW_SECONDS = 0.5
ACTIVITY_REQUIRED_FRACTION = 0.8
PHASE_ANALYSIS_SECONDS = 60.0
LATENCY_WINDOW_SECONDS = 0.30
EXPECTED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EXPECTED_GENERATED_SHA256 = "1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37"
PREREG_PATH = Path("debug/v155-cpu-autonomous/grid-origin-audit-preregistration.json")
EXPECTED_PREREG_GIT_BLOB = "8760972bc904cc1a062f897d9dc4275f8e09aa11"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_pcm16_mono(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as wf:
        channels = wf.getnchannels()
        width = wf.getsampwidth()
        rate = wf.getframerate()
        frames = wf.getnframes()
        raw = wf.readframes(frames)
    if channels != 1 or width != 2 or rate != SAMPLE_RATE:
        raise RuntimeError(f"unexpected WAV format: channels={channels} width={width} rate={rate}")
    x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    return x, rate


def framed_rms(x: np.ndarray, frame: int = FRAME, hop: int = HOP) -> tuple[np.ndarray, np.ndarray]:
    if len(x) < frame:
        raise RuntimeError("audio shorter than one analysis frame")
    starts = np.arange(0, len(x) - frame + 1, hop, dtype=np.int64)
    sq = x * x
    cs = np.empty(len(sq) + 1, dtype=np.float64)
    cs[0] = 0.0
    np.cumsum(sq, out=cs[1:])
    sums = cs[starts + frame] - cs[starts]
    rms = np.sqrt(np.maximum(0.0, sums / frame))
    times = (starts + frame / 2.0) / SAMPLE_RATE
    return rms, times


def first_activity_time(rms: np.ndarray, times: np.ndarray) -> tuple[float, dict]:
    db = 20.0 * np.log10(rms + 1e-12)
    noise_db = float(np.percentile(db, ACTIVITY_NOISE_PERCENTILE))
    threshold_db = noise_db + ACTIVITY_THRESHOLD_DB_ABOVE_NOISE
    active = db >= threshold_db
    win = max(1, int(round(ACTIVITY_WINDOW_SECONDS / HOP_SECONDS)))
    required = ACTIVITY_REQUIRED_FRACTION
    kernel = np.ones(win, dtype=np.float64) / win
    frac = np.convolve(active.astype(np.float64), kernel, mode="valid")
    hits = np.flatnonzero(frac >= required)
    if len(hits) == 0:
        raw_hits = np.flatnonzero(active)
        idx = int(raw_hits[0]) if len(raw_hits) else 0
        method = "first-threshold-frame-fallback"
    else:
        idx = int(hits[0])
        method = "sustained-active-window"
    return float(times[idx]), {
        "method": method,
        "noiseFloorDb": noise_db,
        "thresholdDb": threshold_db,
        "windowSeconds": ACTIVITY_WINDOW_SECONDS,
        "requiredFraction": required,
        "activeFrameFraction": float(np.mean(active)),
    }


def onset_novelty(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rms, times = framed_rms(x)
    dx = np.diff(x, prepend=x[0])
    drms, dtimes = framed_rms(dx)
    if len(rms) != len(drms) or not np.allclose(times, dtimes):
        raise RuntimeError("analysis frame mismatch")
    lr = np.log1p(1000.0 * rms)
    ld = np.log1p(1000.0 * drms)
    nov = np.maximum(0.0, np.diff(lr, prepend=lr[0])) + np.maximum(0.0, np.diff(ld, prepend=ld[0]))
    nov = np.convolve(nov, np.ones(3, dtype=np.float64) / 3.0, mode="same")
    return nov, rms, times


def sample_series(times: np.ndarray, values: np.ndarray, query: np.ndarray) -> np.ndarray:
    idx = np.rint((query - times[0]) / HOP_SECONDS).astype(np.int64)
    mask = (idx >= 0) & (idx < len(values))
    out = np.zeros(len(query), dtype=np.float64)
    out[mask] = values[idx[mask]]
    return out


def audio_only_origin(nov: np.ndarray, rms: np.ndarray, times: np.ndarray, activity_start: float) -> dict:
    analysis_end = min(float(times[-1]), activity_start + PHASE_ANALYSIS_SECONDS)
    active_mask = (times >= activity_start) & (times <= analysis_end)
    active_nov = nov[active_mask]
    if len(active_nov) < 16:
        raise RuntimeError("insufficient active novelty frames")
    cap = float(np.percentile(active_nov, 95.0))
    capped = np.minimum(nov, cap)

    phase_candidates = np.arange(0.0, BEAT_SECONDS, HOP_SECONDS, dtype=np.float64)
    phase_rows = []
    for phase in phase_candidates:
        k0 = max(0, int(math.ceil((activity_start - phase) / BEAT_SECONDS)))
        k1 = int(math.floor((analysis_end - phase) / BEAT_SECONDS))
        if k1 < k0:
            continue
        ks = np.arange(k0, k1 + 1, dtype=np.int64)
        q = phase + ks * BEAT_SECONDS
        vals = sample_series(times, capped, q)
        score = float(np.mean(vals)) if len(vals) else 0.0
        phase_rows.append((score, float(phase), int(k0), int(k1), len(vals)))
    if not phase_rows:
        raise RuntimeError("beat phase scan produced no candidates")
    phase_rows.sort(reverse=True, key=lambda row: row[0])
    best_score, best_phase, _, _, _ = phase_rows[0]
    second_score = phase_rows[1][0] if len(phase_rows) > 1 else 0.0

    k0 = max(0, int(math.ceil((activity_start - best_phase) / BEAT_SECONDS)))
    k1 = int(math.floor((analysis_end - best_phase) / BEAT_SECONDS))
    ks = np.arange(k0, k1 + 1, dtype=np.int64)
    beat_times = best_phase + ks * BEAT_SECONDS
    beat_vals = sample_series(times, capped, beat_times)

    residue_scores = []
    for residue in range(4):
        vals = beat_vals[(ks % 4) == residue]
        residue_scores.append({
            "residue": residue,
            "score": float(np.mean(vals)) if len(vals) else 0.0,
            "beats": int(len(vals)),
        })
    ranked_residues = sorted(residue_scores, key=lambda row: row["score"], reverse=True)
    best_residue = int(ranked_residues[0]["residue"])
    bar_second = float(ranked_residues[1]["score"]) if len(ranked_residues) > 1 else 0.0

    min_origin = activity_start - BEAT_SECONDS
    origin_candidates = []
    # Include k before k0 so an origin immediately before sustained activity is allowed.
    for k in range(max(0, k0 - 8), k1 + 1):
        if k % 4 != best_residue:
            continue
        t = best_phase + k * BEAT_SECONDS
        if t >= min_origin:
            origin_candidates.append((k, t))
    if not origin_candidates:
        raise RuntimeError("no origin candidate after activity boundary")
    origin_k, origin_seconds = origin_candidates[0]

    return {
        "analysisWindowSeconds": [activity_start, analysis_end],
        "noveltyCap95": cap,
        "beatPeriodSeconds": BEAT_SECONDS,
        "bestBeatPhaseSeconds": best_phase,
        "beatPhaseScore": best_score,
        "beatPhaseSecondScore": float(second_score),
        "beatPhaseRelativeMargin": float((best_score - second_score) / (abs(best_score) + 1e-12)),
        "barResidueScores": residue_scores,
        "bestDownbeatResidue": best_residue,
        "barPhaseRelativeMargin": float((ranked_residues[0]["score"] - bar_second) / (abs(ranked_residues[0]["score"]) + 1e-12)),
        "originBeatIndex": int(origin_k),
        "originSeconds": float(origin_seconds),
        "originSixteenthSteps": float(origin_seconds / STEP_SECONDS),
        "mappingRule": "scoreAbsoluteStep=(audioSeconds-originSeconds)/stepDurationSeconds",
    }


def pick_onset_peaks(nov: np.ndarray, times: np.ndarray) -> tuple[np.ndarray, dict]:
    med = float(np.median(nov))
    mad = float(np.median(np.abs(nov - med)))
    threshold = med + 2.5 * max(mad, 1e-12)
    candidates = np.flatnonzero((nov[1:-1] > nov[:-2]) & (nov[1:-1] >= nov[2:]) & (nov[1:-1] >= threshold)) + 1
    min_sep = max(1, int(round(0.05 / HOP_SECONDS)))
    chosen: list[int] = []
    for idx in candidates:
        idx = int(idx)
        if not chosen or idx - chosen[-1] >= min_sep:
            chosen.append(idx)
        elif nov[idx] > nov[chosen[-1]]:
            chosen[-1] = idx
    peak_times = times[np.asarray(chosen, dtype=np.int64)] if chosen else np.asarray([], dtype=np.float64)
    return peak_times, {
        "threshold": threshold,
        "median": med,
        "mad": mad,
        "peakCount": int(len(peak_times)),
        "minimumSeparationSeconds": min_sep * HOP_SECONDS,
    }


def nearest_peak_delta(start: float, peaks: list[float]) -> float | None:
    if not peaks:
        return None
    i = bisect.bisect_left(peaks, start)
    candidates = []
    if i < len(peaks):
        candidates.append(peaks[i])
    if i > 0:
        candidates.append(peaks[i - 1])
    if not candidates:
        return None
    p = min(candidates, key=lambda t: abs(start - t))
    delta = start - p
    return delta if abs(delta) <= LATENCY_WINDOW_SECONDS else None


def latency_diagnostic(generated: dict, peak_times: np.ndarray) -> dict:
    peaks = [float(x) for x in peak_times.tolist()]
    out = {}
    for stream in ("combinedGuitar", "bass"):
        rows = generated.get("streams", {}).get(stream, [])
        deltas = []
        for row in rows:
            delta = nearest_peak_delta(float(row["startSeconds"]), peaks)
            if delta is not None:
                deltas.append(delta)
        arr = np.asarray(deltas, dtype=np.float64)
        out[stream] = {
            "generatedEvents": int(len(rows)),
            "eventsWithNearbyRawOnset": int(len(arr)),
            "coverage": float(len(arr) / len(rows)) if rows else 0.0,
            "medianGeneratedMinusRawOnsetSeconds": float(np.median(arr)) if len(arr) else None,
            "p10Seconds": float(np.percentile(arr, 10)) if len(arr) else None,
            "p90Seconds": float(np.percentile(arr, 90)) if len(arr) else None,
            "windowSeconds": LATENCY_WINDOW_SECONDS,
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio-m4a", type=Path, required=True)
    ap.add_argument("--decoded-wav", type=Path, required=True)
    ap.add_argument("--generated", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    if args.output.exists():
        raise RuntimeError(f"write-once output already exists: {args.output}")
    if sha256_file(args.audio_m4a) != EXPECTED_AUDIO_SHA256:
        raise RuntimeError("historical audio identity mismatch")
    if sha256_file(args.generated) != EXPECTED_GENERATED_SHA256:
        raise RuntimeError("consumed V154 generated identity mismatch")
    if not PREREG_PATH.is_file() or git_blob_sha(PREREG_PATH) != EXPECTED_PREREG_GIT_BLOB:
        raise RuntimeError("grid-origin audit preregistration identity mismatch")

    x, sr = read_pcm16_mono(args.decoded_wav)
    nov, rms, times = onset_novelty(x)
    activity_start, activity_meta = first_activity_time(rms, times)
    origin = audio_only_origin(nov, rms, times, activity_start)
    peaks, peak_meta = pick_onset_peaks(nov, times)
    generated = json.loads(args.generated.read_text(encoding="utf-8"))
    latency = latency_diagnostic(generated, peaks)

    payload = {
        "schema": "dadrock.tabs.v155.grid-origin-audit.v1",
        "classification": "reference-blind-cpu-audio-grid-origin-diagnostic",
        "validation": "PASS",
        "audio": {
            "m4aSha256": EXPECTED_AUDIO_SHA256,
            "decodedSampleRate": sr,
            "decodedSamples": int(len(x)),
            "decodedDurationSeconds": float(len(x) / sr),
        },
        "controlledGrid": {
            "tempoBpm": TEMPO_BPM,
            "stepsPerBeat": STEPS_PER_BEAT,
            "stepDurationSeconds": STEP_SECONDS,
        },
        "activity": {
            "activityStartSeconds": activity_start,
            **activity_meta,
        },
        "audioOnlyOriginEstimate": origin,
        "rawOnsetPeaks": {
            **peak_meta,
            "firstTenPeakSeconds": [float(x) for x in peaks[:10]],
        },
        "v154TranscriptionLatencyDiagnostic": latency,
        "policy": {
            "professionalReferenceRead": False,
            "officialScorerCalled": False,
            "candidateGenerated": False,
            "candidateModified": False,
            "candidateSelected": False,
            "referenceDerivedOffsetHardcoded": False,
            "cpuOnly": True,
            "gpuCudaModalL4Used": False,
            "mainOrProductionModified": False,
        },
    }
    write_json(args.output, payload)
    print(json.dumps({
        "validation": "PASS",
        "activityStartSeconds": activity_start,
        "originSeconds": origin["originSeconds"],
        "originSixteenthSteps": origin["originSixteenthSteps"],
        "beatPhaseRelativeMargin": origin["beatPhaseRelativeMargin"],
        "barPhaseRelativeMargin": origin["barPhaseRelativeMargin"],
        "output": str(args.output),
        "sha256": sha256_file(args.output),
        "professionalReferenceRead": False,
        "officialScorerCalled": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
