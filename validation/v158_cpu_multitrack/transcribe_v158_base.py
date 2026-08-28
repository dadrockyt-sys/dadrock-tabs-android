#!/usr/bin/env python3
"""Canonical V158 reference-blind CPU transcriber.

Implements the preregistered V158 sequential bar-state, onset-first Bass, and
persistent harmonic-template Guitar architecture. This module has no professional
reference/scorer/prior-candidate inputs and writes exactly one candidate + receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

SR = 22050
HOP = 256
BPO = 36
HARMONICS = (1, 2, 3, 4, 5)
HWEIGHTS = (1.0, 0.5, 0.3333333333, 0.25, 0.2)
BASS_RANGE = (28, 67)
GUITAR_RANGE = (40, 88)
EPS = 1e-12

CANDIDATE_SCHEMA = "dadrock.tabs.v158.cpu-sequential-onset-first-generated.v1"
RECEIPT_SCHEMA = "dadrock.tabs.v158.cpu-generation-receipt.v1"
PREREG_BLOB = "728cf28646db225f3c266a4bb73a6112b1f60330"
CONTRACT_BLOB = "68f01df155cd27077cea3de5a0cd048ddcb7bd76"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def robust_z(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    med = float(np.median(x)) if x.size else 0.0
    mad = float(np.median(np.abs(x - med))) * 1.4826 if x.size else 0.0
    if not math.isfinite(mad) or mad < 1e-9:
        std = float(np.std(x)) if x.size else 0.0
        mad = std if math.isfinite(std) and std >= 1e-9 else 1.0
    return (x - med) / mad


def z_across_candidates(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    std = float(np.std(x))
    if not math.isfinite(std) or std < 1e-9:
        return np.zeros_like(x)
    return (x - float(np.mean(x))) / std


def load_mono(path: Path) -> tuple[np.ndarray, int]:
    import librosa
    y, sr = librosa.load(str(path), sr=SR, mono=True)
    if sr != SR or not np.all(np.isfinite(y)):
        raise RuntimeError(f"invalid audio load: {path}")
    return np.asarray(y, dtype=np.float32), sr


def onset_env(y: np.ndarray) -> np.ndarray:
    import librosa
    return np.asarray(librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP), dtype=float)


def first_onset_seconds(env: np.ndarray) -> float | None:
    import librosa
    frames = librosa.onset.onset_detect(onset_envelope=env, sr=SR, hop_length=HOP, units="frames")
    if len(frames) == 0:
        return None
    return float(librosa.frames_to_time(int(frames[0]), sr=SR, hop_length=HOP))


def low_frequency_flux(y: np.ndarray) -> np.ndarray:
    import librosa
    s = np.abs(librosa.stft(y, n_fft=2048, hop_length=HOP))
    freqs = librosa.fft_frequencies(sr=SR, n_fft=2048)
    band = s[freqs <= 200.0]
    if band.shape[1] < 2:
        return np.zeros(s.shape[1], dtype=float)
    diff = np.diff(band, axis=1, prepend=band[:, :1])
    return np.sum(np.maximum(diff, 0.0), axis=0)


def chroma_change(y: np.ndarray) -> np.ndarray:
    import librosa
    chroma = librosa.feature.chroma_cqt(y=y, sr=SR, hop_length=HOP, n_chroma=12)
    if chroma.shape[1] < 2:
        return np.zeros(chroma.shape[1], dtype=float)
    diff = np.diff(chroma, axis=1, prepend=chroma[:, :1])
    return np.linalg.norm(diff, axis=0)


def sample_feature(feature: np.ndarray, frames: np.ndarray) -> np.ndarray:
    if len(feature) == 0:
        return np.zeros(len(frames), dtype=float)
    idx = np.clip(frames.astype(int), 0, len(feature) - 1)
    return np.asarray(feature[idx], dtype=float)


def viterbi_states(emission0: np.ndarray) -> list[int]:
    n = len(emission0)
    if n == 0:
        return []
    log_start = -1.3862943611198906
    logp = {
        1: math.log(0.985),
        0: math.log(0.0075),
        2: math.log(0.0075),
    }
    dp = np.full((n, 4), -np.inf, dtype=float)
    prev = np.full((n, 4), -1, dtype=int)
    for s in range(4):
        dp[0, s] = log_start + (float(emission0[0]) if s == 0 else 0.0)
    for i in range(1, n):
        for s in range(4):
            best_score = -np.inf
            best_prev = 0
            for ps in range(4):
                delta = (s - ps) % 4
                if delta not in logp:
                    continue
                score = dp[i - 1, ps] + logp[delta]
                if score > best_score + EPS or (abs(score - best_score) <= EPS and ps < best_prev):
                    best_score = score
                    best_prev = ps
            dp[i, s] = best_score + (float(emission0[i]) if s == 0 else 0.0)
            prev[i, s] = best_prev
    final = 0
    best = dp[-1, 0]
    for s in range(1, 4):
        if dp[-1, s] > best + EPS:
            best = dp[-1, s]
            final = s
    path = [0] * n
    path[-1] = final
    for i in range(n - 1, 0, -1):
        path[i - 1] = int(prev[i, path[i]])
    return path


@dataclass
class BeatGrid:
    beat_times: np.ndarray
    beat_steps: np.ndarray
    states: list[int]
    tempo_bpm: float
    first_period: float
    last_period: float
    earliest_activity: float
    leading_bars: int
    feature_summary: dict[str, Any]

    def raw_step(self, seconds: float) -> float:
        t = float(seconds)
        if t <= self.beat_times[0]:
            return float(self.beat_steps[0] + 4.0 * (t - self.beat_times[0]) / self.first_period)
        if t >= self.beat_times[-1]:
            return float(self.beat_steps[-1] + 4.0 * (t - self.beat_times[-1]) / self.last_period)
        hi = int(np.searchsorted(self.beat_times, t, side="right"))
        lo = hi - 1
        dt = max(1e-9, float(self.beat_times[hi] - self.beat_times[lo]))
        frac = (t - float(self.beat_times[lo])) / dt
        return float(self.beat_steps[lo] + frac * (self.beat_steps[hi] - self.beat_steps[lo]))


def build_timebase(mix_path: Path, drums_path: Path, bass_path: Path, guitar_path: Path) -> BeatGrid:
    import librosa
    mix, _ = load_mono(mix_path)
    drums, _ = load_mono(drums_path)
    bass, _ = load_mono(bass_path)
    guitar, _ = load_mono(guitar_path)
    env_mix = onset_env(mix)
    env_drums = onset_env(drums)
    env_bass = onset_env(bass)
    env_guitar = onset_env(guitar)
    n = min(len(env_mix), len(env_drums))
    fused = 0.5 * (robust_z(env_mix[:n]) + robust_z(env_drums[:n]))
    tempo, beat_frames = librosa.beat.beat_track(
        onset_envelope=fused, sr=SR, hop_length=HOP, start_bpm=120.0, tightness=100.0, sparse=True
    )
    beat_frames = np.asarray(beat_frames, dtype=int)
    if len(beat_frames) < 8:
        raise RuntimeError(f"V158 insufficient beat count: {len(beat_frames)}")
    beat_times = librosa.frames_to_time(beat_frames, sr=SR, hop_length=HOP).astype(float)
    if not np.all(np.diff(beat_times) > 0):
        raise RuntimeError("V158 beat times not strictly increasing")

    low_flux = low_frequency_flux(mix)
    harm_change = chroma_change(mix)
    features = {
        "drums": sample_feature(robust_z(env_drums), beat_frames),
        "mix": sample_feature(robust_z(env_mix), beat_frames),
        "bass": sample_feature(robust_z(env_bass), beat_frames),
        "lowFlux": sample_feature(robust_z(low_flux), beat_frames),
        "harmonicChange": sample_feature(robust_z(harm_change), beat_frames),
    }
    emission0 = (
        1.0 * features["drums"] + 0.5 * features["mix"] + 0.5 * features["bass"]
        + 0.75 * features["lowFlux"] + 0.75 * features["harmonicChange"]
    )
    states = viterbi_states(emission0)
    if len(states) != len(beat_times) or any(s not in {0, 1, 2, 3} for s in states):
        raise RuntimeError("V158 invalid Viterbi state path")

    ordinal = np.zeros(len(states), dtype=float)
    ordinal[0] = float(states[0])
    for i in range(1, len(states)):
        delta = (states[i] - states[i - 1]) % 4
        if delta not in {0, 1, 2}:
            raise RuntimeError("V158 impossible Viterbi transition")
        ordinal[i] = ordinal[i - 1] + float(delta)
    beat_steps = ordinal * 4.0
    ibis = np.diff(beat_times)
    first_period = float(np.median(ibis[: min(8, len(ibis))]))
    last_period = float(np.median(ibis[max(0, len(ibis) - 8):]))
    activity = [x for x in (
        first_onset_seconds(env_mix), first_onset_seconds(env_drums), first_onset_seconds(env_bass), first_onset_seconds(env_guitar)
    ) if x is not None]
    earliest = min(activity) if activity else 0.0
    temp = BeatGrid(beat_times, beat_steps, states, float(np.asarray(tempo).reshape(-1)[0]), first_period, last_period, earliest, 0, {})
    raw_earliest = temp.raw_step(earliest)
    leading_bars = max(0, int(math.ceil(max(0.0, -raw_earliest) / 16.0)))
    beat_steps = beat_steps + leading_bars * 16.0
    summary = {
        "stateCounts": {str(s): int(states.count(s)) for s in range(4)},
        "emission0Mean": float(np.mean(emission0)),
        "emission0Std": float(np.std(emission0)),
        "transitionCounts": {
            "same": sum(1 for a, b in zip(states, states[1:]) if (b - a) % 4 == 0),
            "next": sum(1 for a, b in zip(states, states[1:]) if (b - a) % 4 == 1),
            "skipOne": sum(1 for a, b in zip(states, states[1:]) if (b - a) % 4 == 2),
        },
    }
    return BeatGrid(beat_times, beat_steps, states, float(np.asarray(tempo).reshape(-1)[0]), first_period, last_period, earliest, leading_bars, summary)


def harmonic_cqt(y: np.ndarray, midi_min: int, midi_max: int) -> tuple[np.ndarray, np.ndarray]:
    import librosa
    harmonic, _ = librosa.effects.hpss(y)
    top = midi_max + 30
    fmin = librosa.midi_to_hz(midi_min - 1)
    n_bins = int(math.ceil((top - (midi_min - 1)) * BPO / 12.0)) + 1
    cqt = np.log1p(np.abs(librosa.cqt(harmonic, sr=SR, hop_length=HOP, fmin=fmin, n_bins=n_bins, bins_per_octave=BPO)))
    freqs = librosa.cqt_frequencies(n_bins, fmin=fmin, bins_per_octave=BPO)
    return cqt, freqs


def frequency_bin(freqs: np.ndarray, hz: float) -> int:
    return int(np.argmin(np.abs(freqs - hz)))


def template_scores(cqt: np.ndarray, freqs: np.ndarray, frames: list[int], midi_min: int, midi_max: int) -> tuple[np.ndarray, np.ndarray]:
    import librosa
    safe_frames = [int(np.clip(f, 0, cqt.shape[1] - 1)) for f in frames]
    scores = []
    fundamentals = []
    for midi in range(midi_min, midi_max + 1):
        f0 = float(librosa.midi_to_hz(midi))
        fundamental = frequency_bin(freqs, f0)
        lo = max(0, fundamental - 1); hi = min(cqt.shape[0], fundamental + 2)
        fund_mean = float(np.mean(cqt[lo:hi, safe_frames]))
        score = 0.75 * fund_mean
        for harmonic, weight in zip(HARMONICS, HWEIGHTS):
            hz = f0 * harmonic
            if hz > freqs[-1]:
                continue
            center = frequency_bin(freqs, hz)
            hlo = max(0, center - 1); hhi = min(cqt.shape[0], center + 2)
            score += float(weight) * float(np.mean(cqt[hlo:hhi, safe_frames]))
        scores.append(score)
        fundamentals.append(fund_mean)
    return np.asarray(scores, dtype=float), np.asarray(fundamentals, dtype=float)


def collapse_onsets(frames: np.ndarray, min_ms: float) -> list[int]:
    min_frames = max(1, int(math.ceil((min_ms / 1000.0) * SR / HOP)))
    out: list[int] = []
    for f in sorted(set(int(x) for x in frames)):
        if not out or f - out[-1] >= min_frames:
            out.append(f)
    return out


def bass_events(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    import librosa
    y, _ = load_mono(path)
    env = onset_env(y)
    onset_frames = librosa.onset.onset_detect(onset_envelope=env, sr=SR, hop_length=HOP, backtrack=True, units="frames")
    retained = collapse_onsets(np.asarray(onset_frames, dtype=int), 35.0)
    harmonic, _ = librosa.effects.hpss(y)
    f0, voiced_flag, voiced_prob = librosa.pyin(
        harmonic, fmin=librosa.midi_to_hz(BASS_RANGE[0]), fmax=librosa.midi_to_hz(BASS_RANGE[1]),
        sr=SR, frame_length=2048, hop_length=256
    )
    pyin_midi = librosa.hz_to_midi(np.asarray(f0, dtype=float))
    voiced_prob = np.asarray(voiced_prob, dtype=float)
    cqt, freqs = harmonic_cqt(y, BASS_RANGE[0], BASS_RANGE[1])
    half_frames = max(1, int(round((0.180 / 2.0) * SR / HOP)))
    rows: list[dict[str, Any]] = []
    for idx, frame in enumerate(retained):
        lo = max(0, frame - half_frames); hi = min(cqt.shape[1], frame + half_frames + 1)
        frames = list(range(lo, hi)) or [frame]
        hscores, fundamentals = template_scores(cqt, freqs, frames, BASS_RANGE[0], BASS_RANGE[1])
        hz = z_across_candidates(hscores)
        p_lo = max(0, lo); p_hi = min(len(pyin_midi), hi)
        finite = np.isfinite(pyin_midi[p_lo:p_hi])
        if np.any(finite):
            pm = float(np.median(pyin_midi[p_lo:p_hi][finite]))
            vp = float(np.nanmedian(voiced_prob[p_lo:p_hi][finite]))
            vp = 0.0 if not math.isfinite(vp) else vp
            midi_candidates = np.arange(BASS_RANGE[0], BASS_RANGE[1] + 1, dtype=float)
            prox = np.exp(-0.5 * ((midi_candidates - pm) / 0.75) ** 2)
            combined = hz + 0.75 * vp * prox
        else:
            pm = None; vp = 0.0; combined = hz
        best_value = float(np.max(combined))
        best_offsets = np.where(np.abs(combined - best_value) <= EPS)[0]
        best_offset = int(best_offsets[0])
        midi = BASS_RANGE[0] + best_offset
        start = float(librosa.frames_to_time(frame, sr=SR, hop_length=HOP))
        if idx + 1 < len(retained):
            next_start = float(librosa.frames_to_time(retained[idx + 1], sr=SR, hop_length=HOP))
            end = min(next_start, start + 0.5)
        else:
            end = start + 0.5
        rows.append({
            "midi": int(midi), "startSeconds": start, "endSeconds": end,
            "durationSeconds": max(0.0, end - start), "source": "onset_harmonic_pyin",
            "onsetProposalIndex": idx, "onsetFrame": int(frame),
            "harmonicTemplateScore": float(hscores[best_offset]),
            "fundamentalMeanMagnitude": float(fundamentals[best_offset]),
            "fundamentalPresent": bool(fundamentals[best_offset] > float(np.median(fundamentals))),
            "medianPyinMidi": pm, "medianPyinVoicedProbability": vp,
            "combinedPitchScore": best_value,
        })
    return rows, {
        "detectedOnsetCount": int(len(onset_frames)), "retainedOnsetCount": int(len(retained)),
        "eventCountBeforeGridDedupe": len(rows), "inputSha256": sha256_file(path),
    }


def top_template_midi_per_frame(cqt: np.ndarray, freqs: np.ndarray, frame: int, midi_min: int, midi_max: int, topn: int) -> list[tuple[int, float, bool]]:
    scores, fundamentals = template_scores(cqt, freqs, [frame], midi_min, midi_max)
    med_fund = float(np.median(fundamentals))
    ranked = sorted(
        [(midi_min + i, float(scores[i]), bool(fundamentals[i] > med_fund)) for i in range(len(scores))],
        key=lambda x: (-x[1], x[0])
    )
    return ranked[:topn]


def three_frame_template(cqt: np.ndarray, freqs: np.ndarray, frame: int, midi_min: int, midi_max: int) -> tuple[np.ndarray, np.ndarray]:
    frames = [int(np.clip(frame + d, 0, cqt.shape[1] - 1)) for d in (-1, 0, 1)]
    return template_scores(cqt, freqs, frames, midi_min, midi_max)


def guitar_events(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    import librosa
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import predict
    y, _ = load_mono(path)
    cqt, freqs = harmonic_cqt(y, GUITAR_RANGE[0], GUITAR_RANGE[1])
    _, _, notes = predict(
        path, model_or_model_path=Path(ICASSP_2022_MODEL_PATH), onset_threshold=0.50,
        frame_threshold=0.30, minimum_note_length=90.0,
        minimum_frequency=librosa.midi_to_hz(GUITAR_RANGE[0]), maximum_frequency=librosa.midi_to_hz(GUITAR_RANGE[1]),
        multiple_pitch_bends=False, melodia_trick=True
    )
    rows: list[dict[str, Any]] = []
    raw_bp = 0
    repairs = 0
    for note in notes:
        if len(note) < 4:
            continue
        start, end, raw_midi, amp = float(note[0]), float(note[1]), int(round(float(note[2]))), float(note[3])
        if not GUITAR_RANGE[0] <= raw_midi <= GUITAR_RANGE[1]:
            continue
        raw_bp += 1
        frame = int(np.clip(round(start * SR / HOP), 0, cqt.shape[1] - 1))
        scores, fundamentals = three_frame_template(cqt, freqs, frame, GUITAR_RANGE[0], GUITAR_RANGE[1])
        med_fund = float(np.median(fundamentals))
        candidates = [raw_midi] + [m for m in (raw_midi - 12, raw_midi + 12) if GUITAR_RANGE[0] <= m <= GUITAR_RANGE[1]]
        chosen = raw_midi
        base_score = float(scores[raw_midi - GUITAR_RANGE[0]])
        chosen_score = base_score
        for m in sorted(candidates):
            i = m - GUITAR_RANGE[0]
            score = float(scores[i])
            fund_present = bool(fundamentals[i] > med_fund)
            if m != raw_midi and fund_present and score > chosen_score + EPS:
                chosen, chosen_score = m, score
        if chosen != raw_midi:
            repairs += 1
        rows.append({
            "midi": int(chosen), "startSeconds": start, "endSeconds": end,
            "durationSeconds": max(0.0, end - start), "confidence": amp,
            "source": "basic_pitch", "basicPitchOriginalMidi": int(raw_midi),
            "registerRepaired": bool(chosen != raw_midi), "templateScore": chosen_score,
        })

    env = onset_env(y)
    onset_frames = np.asarray(librosa.onset.onset_detect(onset_envelope=env, sr=SR, hop_length=HOP, backtrack=False, units="frames"), dtype=int)
    added = 0
    for onset_index, frame in enumerate(onset_frames):
        frame = int(np.clip(frame, 1, cqt.shape[1] - 2))
        frame_sets = []
        frame_scores: dict[int, list[float]] = {}
        frame_fund: dict[int, list[bool]] = {}
        for f in (frame - 1, frame, frame + 1):
            ranked = top_template_midi_per_frame(cqt, freqs, f, GUITAR_RANGE[0], GUITAR_RANGE[1], 6)
            frame_sets.append({m for m, _, _ in ranked})
            for m, score, fund in ranked:
                frame_scores.setdefault(m, []).append(score)
                frame_fund.setdefault(m, []).append(fund)
        persistent = set.intersection(*frame_sets) if frame_sets else set()
        candidates = []
        for midi in persistent:
            vals = frame_scores.get(midi, [])
            if len(vals) != 3:
                continue
            candidates.append((midi, float(np.mean(vals)), any(frame_fund.get(midi, []))))
        candidates.sort(key=lambda x: (-x[1], x[0]))
        t = float(librosa.frames_to_time(frame, sr=SR, hop_length=HOP))
        for midi, score, fund_present in candidates[:6]:
            if any(int(r["midi"]) == midi and abs(float(r["startSeconds"]) - t) <= 0.060 for r in rows):
                continue
            rows.append({
                "midi": int(midi), "startSeconds": t, "endSeconds": t + 0.07,
                "durationSeconds": 0.07, "confidence": score, "source": "harmonic_track",
                "onsetProposalIndex": onset_index, "onsetFrame": frame,
                "persistentTrackFrames": 3, "templateScore": score,
                "fundamentalPresent": bool(fund_present),
            })
            added += 1
    return rows, {
        "inputSha256": sha256_file(path), "basicPitchVersion": importlib.metadata.version("basic-pitch"),
        "basicPitchModelSha256": sha256_file(Path(ICASSP_2022_MODEL_PATH)),
        "basicPitchRawEventCount": raw_bp, "registerRepairCount": repairs,
        "independentOnsetCount": int(len(onset_frames)), "harmonicTrackAddedCount": added,
        "eventCountBeforeGridDedupe": len(rows),
    }


def map_and_dedupe(events: list[dict[str, Any]], grid: BeatGrid, stream: str) -> tuple[list[dict[str, Any]], int]:
    precedence = {"basic_pitch": 0, "harmonic_track": 1, "onset_harmonic_pyin": 2}
    mapped: dict[tuple[int, int], dict[str, Any]] = {}
    pregrid = 0
    for row in events:
        raw = grid.raw_step(float(row["startSeconds"]))
        snapped = int(round(raw))
        if snapped < 0:
            pregrid += 1
            continue
        item = dict(row)
        item.update({
            "rawGridStep": float(raw), "absoluteGridStep": snapped,
            "measure": snapped // 16 + 1, "step": snapped % 16, "stream": stream,
        })
        key = (snapped, int(item["midi"]))
        old = mapped.get(key)
        if old is None:
            mapped[key] = item
        else:
            a = precedence.get(str(item.get("source")), 99)
            b = precedence.get(str(old.get("source")), 99)
            if a < b or (a == b and float(item.get("confidence", item.get("combinedPitchScore", 0.0))) > float(old.get("confidence", old.get("combinedPitchScore", 0.0)))):
                mapped[key] = item
    return sorted(mapped.values(), key=lambda r: (int(r["absoluteGridStep"]), int(r["midi"]), str(r["source"]))), pregrid


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mix", type=Path, required=True)
    ap.add_argument("--guitar", type=Path, required=True)
    ap.add_argument("--bass", type=Path, required=True)
    ap.add_argument("--drums", type=Path, required=True)
    ap.add_argument("--preregistration", type=Path, required=True)
    ap.add_argument("--implementation-contract", type=Path, required=True)
    ap.add_argument("--environment-receipt", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists() or args.receipt.exists():
        raise RuntimeError("V158 candidate/receipt is write-once")
    if git_blob_sha(args.preregistration) != PREREG_BLOB or git_blob_sha(args.implementation_contract) != CONTRACT_BLOB:
        raise RuntimeError("V158 sealed preregistration/contract identity drift")
    prereg = json.loads(args.preregistration.read_text())
    contract = json.loads(args.implementation_contract.read_text())
    env = json.loads(args.environment_receipt.read_text())
    if prereg.get("status") != "PREREGISTERED_BEFORE_GENERATION" or contract.get("status") != "SEALED_BEFORE_GENERATION_CODE":
        raise RuntimeError("V158 sealed setup status invalid")
    if env.get("validation") != "PASS" or env.get("device") != "cpu":
        raise RuntimeError("V158 environment receipt invalid")

    grid = build_timebase(args.mix, args.drums, args.bass, args.guitar)
    bass_raw, bass_meta = bass_events(args.bass)
    guitar_raw, guitar_meta = guitar_events(args.guitar)
    guitar, guitar_pre = map_and_dedupe(guitar_raw, grid, "combinedGuitar")
    bass, bass_pre = map_and_dedupe(bass_raw, grid, "bass")
    if not guitar or not bass:
        raise RuntimeError("V158 generated empty stream")

    safety = {
        "referenceRead": False, "professionalReferencePathsOpened": 0,
        "referenceFacingScoreCalls": 0, "priorGeneratedCandidateRead": False,
        "priorScoreOrDiagnosticRead": False, "referenceGuidedFiltering": False,
        "thresholdSweep": False, "variantSelection": False, "humanCorrection": False,
        "cudaGpuUsed": False, "modalUsed": False, "mainOrProductionModified": False,
    }
    candidate = {
        "schema": CANDIDATE_SCHEMA,
        "song": {"artist": "Lenny Kravitz", "title": "Are You Gonna Go My Way"},
        "classification": "single-preregistered-reference-blind-v158-cpu-candidate",
        "streams": {"combinedGuitar": guitar, "bass": bass},
        "timebase": {
            "method": "dynamic-beat-grid-four-state-viterbi-bar-position",
            "trackerTempoBpm": grid.tempo_bpm,
            "beatTimesSeconds": [float(x) for x in grid.beat_times],
            "beatGridSteps": [float(x) for x in grid.beat_steps],
            "viterbiBarStates": [int(x) for x in grid.states],
            "earliestActivitySeconds": grid.earliest_activity,
            "leadingExtensionBars": grid.leading_bars,
            "featureSummary": grid.feature_summary,
            "qc": {"beatCount": len(grid.beat_times), "strictlyIncreasingBeatTimes": True, "statePathLength": len(grid.states)},
        },
        "streamMetadata": {"combinedGuitar": guitar_meta, "bass": bass_meta},
        "sealedInputs": {"preregistrationGitBlob": PREREG_BLOB, "implementationContractGitBlob": CONTRACT_BLOB},
        "safety": safety,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": RECEIPT_SCHEMA, "validation": "PENDING_INDEPENDENT_STRUCTURAL_QC",
        "candidatePath": str(args.output), "candidateSha256": sha256_file(args.output),
        "preregistrationSha256": sha256_file(args.preregistration),
        "implementationContractSha256": sha256_file(args.implementation_contract),
        "environmentReceiptSha256": sha256_file(args.environment_receipt),
        "counts": {"combinedGuitar": len(guitar), "bass": len(bass)},
        "preGridExcluded": {"combinedGuitar": guitar_pre, "bass": bass_pre},
        "inputIdentities": {
            "mixSha256": sha256_file(args.mix), "guitarStemSha256": sha256_file(args.guitar),
            "bassStemSha256": sha256_file(args.bass), "drumsStemSha256": sha256_file(args.drums),
        },
        "environment": env, "safety": safety,
    }
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"candidateSha256": receipt["candidateSha256"], "counts": receipt["counts"], "referenceRead": False, "scoreCalls": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
