#!/usr/bin/env python3
"""V155 reference-blind CPU hybrid front-end.

Implements the sealed V155 preregistration only. This module has no professional
reference/scorer imports and writes exactly one candidate plus generation receipt.
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

MIX_SR = 22050
HOP = 256
GUITAR_MIN_MIDI = 40
GUITAR_MAX_MIDI = 88
BASS_MIN_MIDI = 28
BASS_MAX_MIDI = 67


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_path(path: Path) -> str:
    if path.is_file():
        return sha256_file(path)
    h = hashlib.sha256()
    for child in sorted(p for p in path.rglob("*") if p.is_file()):
        rel = child.relative_to(path).as_posix().encode()
        payload = child.read_bytes()
        h.update(len(rel).to_bytes(8, "big")); h.update(rel)
        h.update(len(payload).to_bytes(8, "big")); h.update(payload)
    return h.hexdigest()


def robust_z(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        return x.copy()
    med = float(np.median(x))
    mad = float(np.median(np.abs(x - med))) * 1.4826
    if not math.isfinite(mad) or mad < 1e-9:
        std = float(np.std(x))
        mad = std if math.isfinite(std) and std >= 1e-9 else 1.0
    return (x - med) / mad


def trimmed_mean(vals: list[float]) -> float:
    if not vals:
        return float("-inf")
    s = sorted(float(v) for v in vals)
    if len(s) >= 5:
        trim = max(1, int(math.floor(len(s) * 0.10)))
        if len(s) > 2 * trim:
            s = s[trim:-trim]
    return float(np.mean(s))


@dataclass
class BeatGrid:
    beat_times: np.ndarray
    beat_steps: np.ndarray
    selected_phase: int
    phase_scores: list[float]
    earliest_activity_seconds: float
    extension_bars: int
    tempo_bpm: float
    first_local_period: float
    last_local_period: float
    qc: dict[str, Any]

    def raw_step(self, seconds: float) -> float:
        t = float(seconds)
        bt = self.beat_times
        bs = self.beat_steps
        if len(bt) < 2:
            raise RuntimeError("insufficient beat grid")
        if t <= bt[0]:
            period = max(1e-6, self.first_local_period)
            return float(bs[0] + 4.0 * (t - bt[0]) / period)
        if t >= bt[-1]:
            period = max(1e-6, self.last_local_period)
            return float(bs[-1] + 4.0 * (t - bt[-1]) / period)
        hi = int(np.searchsorted(bt, t, side="right"))
        lo = hi - 1
        span = max(1e-6, float(bt[hi] - bt[lo]))
        frac = (t - float(bt[lo])) / span
        return float(bs[lo] + frac * (bs[hi] - bs[lo]))


def load_mono(path: Path, sr: int = MIX_SR) -> tuple[np.ndarray, int]:
    import librosa
    y, got_sr = librosa.load(str(path), sr=sr, mono=True)
    if got_sr != sr:
        raise RuntimeError(f"unexpected sample rate {got_sr}")
    if not np.all(np.isfinite(y)):
        raise RuntimeError(f"non-finite audio samples: {path}")
    return np.asarray(y, dtype=np.float32), got_sr


def onset_env(y: np.ndarray, sr: int) -> np.ndarray:
    import librosa
    return np.asarray(librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP), dtype=float)


def first_onset_seconds(env: np.ndarray, sr: int) -> float | None:
    import librosa
    frames = librosa.onset.onset_detect(onset_envelope=env, sr=sr, hop_length=HOP, units="frames")
    if len(frames) == 0:
        return None
    return float(librosa.frames_to_time(int(frames[0]), sr=sr, hop_length=HOP))


def build_timebase(mix_path: Path, drums_path: Path, bass_path: Path, guitar_path: Path) -> BeatGrid:
    import librosa

    mix, sr = load_mono(mix_path)
    drums, _ = load_mono(drums_path)
    bass, _ = load_mono(bass_path)
    guitar, _ = load_mono(guitar_path)
    env_mix = onset_env(mix, sr)
    env_drums = onset_env(drums, sr)
    env_bass = onset_env(bass, sr)
    env_guitar = onset_env(guitar, sr)
    n = min(len(env_mix), len(env_drums))
    fused = (np.maximum(robust_z(env_mix[:n]), 0.0) + np.maximum(robust_z(env_drums[:n]), 0.0)) / 2.0

    tempo, beat_frames = librosa.beat.beat_track(
        onset_envelope=fused,
        sr=sr,
        hop_length=HOP,
        start_bpm=120.0,
        tightness=100.0,
        sparse=True,
    )
    beat_frames = np.asarray(beat_frames, dtype=int)
    if len(beat_frames) < 8:
        raise RuntimeError(f"V155 timebase structural failure: only {len(beat_frames)} tracked beats")
    beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=HOP).astype(float)
    if not np.all(np.diff(beat_times) > 0):
        raise RuntimeError("V155 timebase structural failure: beat times not strictly increasing")

    z_mix = robust_z(env_mix)
    z_drums = robust_z(env_drums)
    z_bass = robust_z(env_bass)
    accents = []
    for frame in beat_frames:
        f = int(np.clip(frame, 0, min(len(z_mix), len(z_drums), len(z_bass)) - 1))
        accents.append(float((z_mix[f] + z_drums[f] + z_bass[f]) / 3.0))
    eligible = list(range(len(beat_frames)))
    if len(eligible) > 2:
        eligible = eligible[1:-1]
    phase_scores = []
    for phase in range(4):
        phase_scores.append(trimmed_mean([accents[i] for i in eligible if i % 4 == phase]))
    selected_phase = max(range(4), key=lambda p: (phase_scores[p], -p))
    phase_indices = [i for i in range(len(beat_frames)) if i % 4 == selected_phase]
    if not phase_indices:
        raise RuntimeError("no downbeat phase index")
    first_phase_index = phase_indices[0]

    activity = [v for v in (
        first_onset_seconds(env_mix, sr),
        first_onset_seconds(env_drums, sr),
        first_onset_seconds(env_bass, sr),
        first_onset_seconds(env_guitar, sr),
    ) if v is not None]
    earliest_activity = min(activity) if activity else 0.0

    ibis = np.diff(beat_times)
    local_period = float(np.median(ibis[: min(8, len(ibis))]))
    last_local_period = float(np.median(ibis[max(0, len(ibis)-8):]))
    if local_period <= 0 or not math.isfinite(local_period) or last_local_period <= 0 or not math.isfinite(last_local_period):
        raise RuntimeError("invalid local beat period")
    selected_origin_time = float(beat_times[first_phase_index])
    extension_bars = 0
    extended_origin_time = selected_origin_time
    while earliest_activity < extended_origin_time and extension_bars < 64:
        extended_origin_time -= 4.0 * local_period
        extension_bars += 1
    beat_steps = np.array([
        (i - first_phase_index) * 4.0 + extension_bars * 16.0
        for i in range(len(beat_times))
    ], dtype=float)

    median_ibi = float(np.median(ibis))
    cv = float(np.std(ibis) / max(1e-9, np.mean(ibis)))
    fraction_band = float(np.mean((ibis >= 0.5 * median_ibi) & (ibis <= 1.5 * median_ibi)))
    median_bpm = 60.0 / median_ibi
    tempo_scalar = float(np.asarray(tempo).reshape(-1)[0])
    qc = {
        "trackedBeatCount": int(len(beat_times)),
        "trackerTempoBpm": tempo_scalar,
        "medianInterBeatBpm": median_bpm,
        "interBeatIntervalCoefficientOfVariation": cv,
        "fractionIntervalsWithinHalfToOnePointFiveMedian": fraction_band,
        "strictlyIncreasingBeatTimes": True,
    }
    if not (70.0 <= median_bpm <= 180.0):
        raise RuntimeError(f"V155 timebase structural failure: median beat BPM {median_bpm}")
    if cv > 0.20:
        raise RuntimeError(f"V155 timebase structural failure: beat interval CV {cv}")
    if fraction_band < 0.90:
        raise RuntimeError(f"V155 timebase structural failure: interval consistency {fraction_band}")

    return BeatGrid(
        beat_times=beat_times,
        beat_steps=beat_steps,
        selected_phase=selected_phase,
        phase_scores=phase_scores,
        earliest_activity_seconds=float(earliest_activity),
        extension_bars=extension_bars,
        tempo_bpm=tempo_scalar,
        first_local_period=local_period,
        last_local_period=last_local_period,
        qc=qc,
    )


def collapse_boundaries(boundaries: list[int], minimum_gap: int = 2) -> list[int]:
    out: list[int] = []
    for b in sorted(set(int(x) for x in boundaries)):
        if not out or b - out[-1] >= minimum_gap:
            out.append(b)
    return out


def bass_events(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    import librosa
    y, sr = load_mono(path)
    harmonic, _ = librosa.effects.hpss(y)
    f0, voiced_flag, voiced_prob = librosa.pyin(
        harmonic,
        fmin=librosa.midi_to_hz(BASS_MIN_MIDI),
        fmax=librosa.midi_to_hz(BASS_MAX_MIDI),
        sr=sr,
        frame_length=2048,
        hop_length=HOP,
    )
    f0 = np.asarray(f0, dtype=float)
    voiced_flag = np.asarray(voiced_flag, dtype=bool)
    voiced_prob = np.asarray(voiced_prob, dtype=float)
    midi = librosa.hz_to_midi(f0)
    env = onset_env(y, sr)
    onset_frames = librosa.onset.onset_detect(
        onset_envelope=env, sr=sr, hop_length=HOP, backtrack=True, units="frames"
    )
    n = len(f0)
    boundaries = [0, n]
    boundaries.extend(int(x) for x in onset_frames if 0 < int(x) < n)
    for i in range(1, n):
        if bool(voiced_flag[i]) != bool(voiced_flag[i - 1]):
            boundaries.append(i)
    for i in range(3, max(3, n - 3)):
        prev = midi[i - 3:i]; nxt = midi[i:i + 3]
        pp = voiced_prob[i - 3:i]; npb = voiced_prob[i:i + 3]
        if np.all(np.isfinite(prev)) and np.all(np.isfinite(nxt)) and np.all(pp >= 0.70) and np.all(npb >= 0.70):
            if abs(float(np.median(nxt)) - float(np.median(prev))) >= 0.70:
                boundaries.append(i)
    boundaries = collapse_boundaries(boundaries, minimum_gap=2)
    if boundaries[-1] != n:
        boundaries.append(n)

    rows: list[dict[str, Any]] = []
    min_frames = max(1, int(math.ceil((0.070 * sr) / HOP)))
    for a, b in zip(boundaries, boundaries[1:]):
        if b - a < min_frames:
            continue
        idx = np.arange(a, b)
        good = idx[(voiced_prob[a:b] >= 0.70) & np.isfinite(midi[a:b])]
        if len(good) < min_frames:
            continue
        pitch = int(round(float(np.median(midi[good]))))
        if not BASS_MIN_MIDI <= pitch <= BASS_MAX_MIDI:
            continue
        first_good = int(good[0]); last_good = int(good[-1])
        start = float(librosa.frames_to_time(first_good, sr=sr, hop_length=HOP))
        end = float(librosa.frames_to_time(last_good + 1, sr=sr, hop_length=HOP))
        if (end - start) * 1000.0 < 70.0:
            continue
        rows.append({
            "midi": pitch,
            "startSeconds": start,
            "endSeconds": end,
            "durationSeconds": end - start,
            "confidence": float(np.median(voiced_prob[good])),
            "source": "pyin",
        })
    return rows, {
        "inputSha256": sha256_file(path),
        "rawFrameCount": int(n),
        "detectedOnsetCount": int(len(onset_frames)),
        "eventCountBeforeGridDedupe": int(len(rows)),
    }


def guitar_cqt(path: Path):
    import librosa
    y, sr = load_mono(path)
    harmonic, _ = librosa.effects.hpss(y)
    base_midi = 39.0
    bins_per_octave = 36
    n_bins = int(round((89.0 - base_midi) * bins_per_octave / 12.0)) + 1
    cqt = np.abs(librosa.cqt(
        harmonic, sr=sr, hop_length=HOP, fmin=librosa.midi_to_hz(base_midi),
        n_bins=n_bins, bins_per_octave=bins_per_octave,
    ))
    logmag = np.log1p(cqt)
    pitches = np.arange(GUITAR_MIN_MIDI, GUITAR_MAX_MIDI + 1, dtype=int)
    sal = np.zeros((len(pitches), logmag.shape[1]), dtype=float)
    for pi, m in enumerate(pitches):
        center = int(round((float(m) - base_midi) * bins_per_octave / 12.0))
        lo = max(0, center - 1); hi = min(logmag.shape[0], center + 2)
        sal[pi] = np.sum(logmag[lo:hi], axis=0)
    med = np.median(sal, axis=0)
    mad = np.median(np.abs(sal - med[None, :]), axis=0) * 1.4826
    mad = np.where(mad < 1e-9, 1.0, mad)
    z = (sal - med[None, :]) / mad[None, :]
    env = onset_env(y, sr)
    onset_frames = librosa.onset.onset_detect(onset_envelope=env, sr=sr, hop_length=HOP, units="frames")
    return sr, pitches, sal, z, np.asarray(onset_frames, dtype=int)


def is_local_pitch_peak(sal: np.ndarray, pi: int, frame: int) -> bool:
    value = float(sal[pi, frame])
    if pi > 0 and value < float(sal[pi - 1, frame]):
        return False
    if pi + 1 < sal.shape[0] and value < float(sal[pi + 1, frame]):
        return False
    return True


def likely_harmonic_duplicate(midi: int, salience: float, candidates: list[tuple[int, float]]) -> bool:
    for lower_midi, lower_sal in candidates:
        if lower_midi >= midi or lower_sal <= salience:
            continue
        d = midi - lower_midi
        if any(abs(d - h) <= 1 for h in (12, 19, 24, 28, 31, 34, 36)):
            return True
    return False


def guitar_events(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    import librosa
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import predict

    version = importlib.metadata.version("basic-pitch")
    if version != "0.4.0":
        raise RuntimeError(f"Basic Pitch version drift: {version}")
    model_path = Path(ICASSP_2022_MODEL_PATH)
    _model_output, _midi_data, notes = predict(
        path,
        model_or_model_path=model_path,
        onset_threshold=0.50,
        frame_threshold=0.30,
        minimum_note_length=90.0,
        minimum_frequency=librosa.midi_to_hz(GUITAR_MIN_MIDI),
        maximum_frequency=librosa.midi_to_hz(GUITAR_MAX_MIDI),
        multiple_pitch_bends=False,
        melodia_trick=True,
    )
    sr, pitches, sal, z, onset_frames = guitar_cqt(path)
    first120 = max(1, int(math.ceil(0.120 / (HOP / sr))))
    parsed = []
    for idx, note in enumerate(notes):
        if len(note) < 4:
            continue
        start, end = float(note[0]), float(note[1])
        midi_raw, amp = int(round(float(note[2]))), float(note[3])
        if GUITAR_MIN_MIDI <= midi_raw <= GUITAR_MAX_MIDI and end >= start:
            parsed.append((idx, start, end, midi_raw, amp))

    rows: list[dict[str, Any]] = []
    for idx, start, end, midi_raw, amp in parsed:
        pi = midi_raw - GUITAR_MIN_MIDI
        frame = int(np.clip(round(start * sr / HOP), 0, z.shape[1] - 1))
        stop = min(z.shape[1], frame + first120)
        onset_support = float(z[pi, frame]) >= 1.5
        sustained_fraction = float(np.mean(z[pi, frame:stop] >= 1.5)) if stop > frame else 0.0
        if not (onset_support or sustained_fraction >= 0.35 or amp >= 0.80):
            continue
        rows.append({
            "midi": midi_raw,
            "startSeconds": start,
            "endSeconds": end,
            "durationSeconds": end - start,
            "confidence": amp,
            "source": "basic_pitch",
            "basicPitchAmplitude": amp,
            "cqtOnsetZ": float(z[pi, frame]),
            "cqtFirst120msSupportFraction": sustained_fraction,
        })

    for frame in onset_frames:
        if frame < 0 or frame >= sal.shape[1]:
            continue
        high: list[tuple[int, float, float]] = []
        for pi, midi_val in enumerate(pitches):
            if float(z[pi, frame]) < 3.0 or not is_local_pitch_peak(sal, pi, frame):
                continue
            flux = float(sal[pi, frame] - sal[pi, max(0, frame - 1)])
            if flux > 0.0:
                high.append((int(midi_val), float(sal[pi, frame]), float(z[pi, frame])))
        simple = [(m, s) for m, s, _ in high]
        filtered = [(m, s, zz) for m, s, zz in high if not likely_harmonic_duplicate(m, s, simple)]
        filtered.sort(key=lambda x: (-x[1], x[0]))
        t = float(librosa.frames_to_time(int(frame), sr=sr, hop_length=HOP))
        existing = [r for r in rows if abs(float(r["startSeconds"]) - t) <= 0.060]
        capacity = max(0, 6 - len({int(r["midi"]) for r in existing}))
        added = 0
        for midi_val, s, zz in filtered:
            if added >= capacity:
                break
            if any(int(r["midi"]) == midi_val and abs(float(r["startSeconds"]) - t) <= 0.060 for r in rows):
                continue
            rows.append({
                "midi": midi_val,
                "startSeconds": t,
                "endSeconds": t + 0.070,
                "durationSeconds": 0.070,
                "confidence": zz,
                "source": "cqt",
                "cqtSalience": s,
                "cqtOnsetZ": zz,
            })
            added += 1

    return rows, {
        "inputSha256": sha256_file(path),
        "basicPitchVersion": version,
        "basicPitchModelPath": str(model_path),
        "basicPitchModelSha256": sha256_path(model_path),
        "basicPitchRawEventCount": int(len(parsed)),
        "independentOnsetCount": int(len(onset_frames)),
        "eventCountBeforeGridDedupe": int(len(rows)),
    }


def map_and_dedupe(events: list[dict[str, Any]], grid: BeatGrid, stream: str) -> tuple[list[dict[str, Any]], int]:
    out: dict[tuple[int, int], dict[str, Any]] = {}
    pregrid = 0
    for row in events:
        start = float(row["startSeconds"])
        raw = grid.raw_step(start)
        snapped = int(round(raw))
        if snapped < 0:
            pregrid += 1
            continue
        item = dict(row)
        item.update({
            "absoluteGridStep": snapped,
            "measure": snapped // 16 + 1,
            "step": snapped % 16,
            "rawGridStep": raw,
            "stream": stream,
        })
        key = (snapped, int(row["midi"]))
        prev = out.get(key)
        if prev is None:
            out[key] = item
        else:
            psrc, nsrc = str(prev.get("source")), str(item.get("source"))
            replace = False
            if stream == "combinedGuitar" and nsrc == "basic_pitch" and psrc != "basic_pitch":
                replace = True
            elif not (stream == "combinedGuitar" and psrc == "basic_pitch" and nsrc != "basic_pitch"):
                replace = float(item.get("confidence", 0.0)) > float(prev.get("confidence", 0.0))
            if replace:
                item["mergedProvenance"] = sorted(set([psrc, nsrc])); out[key] = item
            else:
                prev["mergedProvenance"] = sorted(set(list(prev.get("mergedProvenance", [psrc])) + [nsrc]))
    return sorted(out.values(), key=lambda r: (int(r["absoluteGridStep"]), int(r["midi"]), str(r["source"]))), pregrid


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mix", type=Path, required=True)
    ap.add_argument("--guitar", type=Path, required=True)
    ap.add_argument("--bass", type=Path, required=True)
    ap.add_argument("--drums", type=Path, required=True)
    ap.add_argument("--preregistration", type=Path, required=True)
    ap.add_argument("--environment-receipt", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists() or args.receipt.exists():
        raise RuntimeError("V155 candidate/receipt is write-once")
    prereg = json.loads(args.preregistration.read_text())
    if prereg.get("version") != "V155" or prereg.get("status") != "PREREGISTERED_BEFORE_GENERATION":
        raise RuntimeError("invalid V155 preregistration")
    env_receipt = json.loads(args.environment_receipt.read_text())

    grid = build_timebase(args.mix, args.drums, args.bass, args.guitar)
    bass_raw, bass_meta = bass_events(args.bass)
    guitar_raw, guitar_meta = guitar_events(args.guitar)
    guitar, guitar_pre = map_and_dedupe(guitar_raw, grid, "combinedGuitar")
    bass, bass_pre = map_and_dedupe(bass_raw, grid, "bass")
    if not guitar or not bass:
        raise RuntimeError("V155 generated an empty stream")

    safety = {
        "referenceRead": False,
        "humanCorrection": False,
        "referenceGuidedFiltering": False,
        "thresholdSweep": False,
        "modalUsed": False,
        "cudaGpuUsed": False,
    }
    candidate = {
        "schema": "dadrock.tabs.v155.cpu-hybrid-generated.v1",
        "song": {"artist": "Lenny Kravitz", "title": "Are You Gonna Go My Way"},
        "classification": "reference-blind-single-candidate-cpu-hybrid-transcription",
        "streams": {"combinedGuitar": guitar, "bass": bass},
        "timebase": {
            "method": "audio-derived-piecewise-linear-beat-grid",
            "trackerTempoBpm": grid.tempo_bpm,
            "selectedDownbeatPhase": grid.selected_phase,
            "phaseScores": grid.phase_scores,
            "earliestActivitySeconds": grid.earliest_activity_seconds,
            "leadingExtensionBars": grid.extension_bars,
            "beatTimesSeconds": [float(x) for x in grid.beat_times],
            "beatGridSteps": [float(x) for x in grid.beat_steps],
            "qc": grid.qc,
        },
        "streamMetadata": {"combinedGuitar": guitar_meta, "bass": bass_meta},
        "safety": safety,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "dadrock.tabs.v155.cpu-hybrid-generation-receipt.v1",
        "validation": "PENDING_STRUCTURAL_QC",
        "preregistrationSha256": sha256_file(args.preregistration),
        "environmentReceiptSha256": sha256_file(args.environment_receipt),
        "candidatePath": str(args.output),
        "candidateSha256": sha256_file(args.output),
        "counts": {"combinedGuitar": len(guitar), "bass": len(bass)},
        "preGridExcluded": {"combinedGuitar": guitar_pre, "bass": bass_pre},
        "inputIdentities": {
            "mixSha256": sha256_file(args.mix),
            "guitarStemSha256": sha256_file(args.guitar),
            "bassStemSha256": sha256_file(args.bass),
            "drumsStemSha256": sha256_file(args.drums),
        },
        "environment": env_receipt,
        "safety": {**safety, "variantSelection": False, "mainOrProductionModified": False},
    }
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "candidateSha256": receipt["candidateSha256"],
        "counts": receipt["counts"],
        "preGridExcluded": receipt["preGridExcluded"],
        "timebaseQc": grid.qc,
        "referenceRead": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
