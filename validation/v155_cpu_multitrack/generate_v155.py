#!/usr/bin/env python3
"""V155 reference-blind CPU generator.

Implements the architecture sealed in debug/v155-cpu-autonomous/preregistration.json.
This module must never import/read professional scoring references and writes exactly
one candidate plus one generation receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
from typing import Any, Iterable

import numpy as np

MIDI_GUITAR = (40, 88)
MIDI_BASS = (28, 67)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sha256_path(path: Path) -> str:
    if path.is_file():
        return sha256_file(path)
    h = hashlib.sha256()
    for child in sorted(p for p in path.rglob("*") if p.is_file()):
        rel = child.relative_to(path).as_posix().encode("utf-8")
        payload_hash = bytes.fromhex(sha256_file(child))
        h.update(len(rel).to_bytes(8, "big"))
        h.update(rel)
        h.update(payload_hash)
    return h.hexdigest()


def robust_z(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    med = float(np.median(values))
    mad = float(np.median(np.abs(values - med)))
    scale = 1.4826 * mad + 1e-9
    return np.maximum(0.0, (values - med) / scale)


def robust_threshold(values: np.ndarray, multiplier: float) -> np.ndarray:
    med = np.median(values, axis=0)
    mad = np.median(np.abs(values - med[None, :]), axis=0)
    return med + multiplier * (1.4826 * mad + 1e-9)


def hz_for_midi(midi: int) -> float:
    return 440.0 * (2.0 ** ((float(midi) - 69.0) / 12.0))


def package_version(name: str) -> str:
    return importlib.metadata.version(name)


def load_audio(path: Path, sr: int = 22050) -> tuple[np.ndarray, int]:
    import librosa

    y, actual_sr = librosa.load(str(path), sr=sr, mono=True)
    if y.size == 0 or not np.all(np.isfinite(y)):
        raise RuntimeError(f"invalid/empty audio: {path}")
    return y.astype(np.float32, copy=False), int(actual_sr)


def derive_timebase(mix_path: Path, drums_path: Path, bass_path: Path) -> dict[str, Any]:
    import librosa

    hop = 512
    mix, sr = load_audio(mix_path, 22050)
    drums, _ = load_audio(drums_path, 22050)
    bass, _ = load_audio(bass_path, 22050)
    n = min(len(mix), len(drums), len(bass))
    mix = mix[:n]
    drums = drums[:n]
    bass = bass[:n]

    mix_env = librosa.onset.onset_strength(y=mix, sr=sr, hop_length=hop)
    drum_env = librosa.onset.onset_strength(y=drums, sr=sr, hop_length=hop)
    bass_env = librosa.onset.onset_strength(y=bass, sr=sr, hop_length=hop)
    env_n = min(len(mix_env), len(drum_env), len(bass_env))
    mix_env = mix_env[:env_n]
    drum_env = drum_env[:env_n]
    bass_env = bass_env[:env_n]
    combined = 0.45 * robust_z(mix_env) + 0.55 * robust_z(drum_env)

    tempo_raw, beat_frames = librosa.beat.beat_track(
        onset_envelope=combined,
        sr=sr,
        hop_length=hop,
        trim=False,
    )
    beat_frames = np.asarray(beat_frames, dtype=int)
    if beat_frames.size < 24:
        raise RuntimeError(f"insufficient detected beats: {beat_frames.size}")
    beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop).astype(float)
    periods = np.diff(beat_times)
    positive_periods = periods[(periods > 0.20) & (periods < 1.20)]
    if positive_periods.size < 12:
        raise RuntimeError("insufficient valid beat periods")
    robust_period = float(np.median(positive_periods))
    robust_bpm = 60.0 / robust_period

    mix_z = robust_z(mix_env)
    drum_z = robust_z(drum_env)
    bass_z = robust_z(bass_env)
    accents: list[float] = []
    for frame in beat_frames:
        idx = int(np.clip(frame, 0, env_n - 1))
        accents.append(float(0.30 * mix_z[idx] + 0.50 * drum_z[idx] + 0.20 * bass_z[idx]))

    phase_scores: list[dict[str, Any]] = []
    for phase in range(4):
        selected = [accents[i] for i in range(phase, len(accents), 4)]
        others = [accents[i] for i in range(len(accents)) if i % 4 != phase]
        selected_mean = float(np.mean(selected)) if selected else 0.0
        other_mean = float(np.mean(others)) if others else 0.0
        score = selected_mean - 0.20 * other_mean
        phase_scores.append({
            "phase": phase,
            "score": score,
            "selectedMeanAccent": selected_mean,
            "otherMeanAccent": other_mean,
        })
    phase_scores.sort(key=lambda x: (-float(x["score"]), int(x["phase"])))
    phase = int(phase_scores[0]["phase"])

    onset_frames = librosa.onset.onset_detect(
        onset_envelope=combined,
        sr=sr,
        hop_length=hop,
        backtrack=True,
        units="frames",
    )
    onset_frames = np.asarray(onset_frames, dtype=int)
    if onset_frames.size:
        first_onset_time = float(librosa.frames_to_time(onset_frames[0], sr=sr, hop_length=hop))
    else:
        first_onset_time = float(beat_times[0])

    phase_indices = [i for i in range(len(beat_times)) if i % 4 == phase]
    before = [i for i in phase_indices if beat_times[i] <= first_onset_time + 0.10]
    if before:
        origin_index = max(before)
    else:
        first_phase = phase_indices[0]
        measures_back = max(1, int(math.ceil((beat_times[first_phase] - first_onset_time) / max(4.0 * robust_period, 1e-9))))
        origin_index = first_phase - 4 * measures_back

    tempo_scalar = float(np.asarray(tempo_raw).reshape(-1)[0])
    return {
        "sampleRate": sr,
        "hopLength": hop,
        "beatFrames": [int(x) for x in beat_frames.tolist()],
        "beatTimesSeconds": [float(x) for x in beat_times.tolist()],
        "beatTrackerTempoBpm": tempo_scalar,
        "robustMedianBeatPeriodSeconds": robust_period,
        "robustMedianTempoBpm": robust_bpm,
        "downbeatPhase": phase,
        "phaseScores": sorted(phase_scores, key=lambda x: int(x["phase"])),
        "firstDetectedOnsetSeconds": first_onset_time,
        "originBeatIndex": int(origin_index),
        "originDefinition": "latest selected-phase tracked beat at/before first detected onset, or one-or-more full 4-beat periods extrapolated backward",
    }


def raw_grid_step(seconds: float, timebase: dict[str, Any]) -> float:
    beats = np.asarray(timebase["beatTimesSeconds"], dtype=float)
    origin_index = int(timebase["originBeatIndex"])
    if beats.size < 2:
        raise RuntimeError("timebase missing beats")
    if seconds <= beats[0]:
        period = beats[1] - beats[0]
        beat_pos = (0 - origin_index) + (seconds - beats[0]) / period
    elif seconds >= beats[-1]:
        period = beats[-1] - beats[-2]
        beat_pos = (len(beats) - 1 - origin_index) + (seconds - beats[-1]) / period
    else:
        right = int(np.searchsorted(beats, seconds, side="right"))
        left = right - 1
        period = beats[right] - beats[left]
        frac = 0.0 if period <= 1e-9 else (seconds - beats[left]) / period
        beat_pos = (left - origin_index) + frac
    return float(beat_pos * 4.0)


def map_event(seconds: float, midi: int, source: str, evidence: float, end_seconds: float, timebase: dict[str, Any], extra: dict[str, Any] | None = None) -> dict[str, Any] | None:
    rg = raw_grid_step(seconds, timebase)
    snapped = int(round(rg))
    if snapped < 0:
        return None
    measure = snapped // 16 + 1
    step = snapped % 16
    event: dict[str, Any] = {
        "measure": int(measure),
        "step": int(step),
        "midi": int(midi),
        "startSeconds": float(seconds),
        "endSeconds": float(max(seconds, end_seconds)),
        "rawGridStep": float(rg),
        "snappedAbsoluteGridStep": int(snapped),
        "source": source,
        "evidence": float(evidence),
    }
    if extra:
        event.update(extra)
    return event


def bass_events(bass_path: Path, timebase: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    import librosa

    y, sr = load_audio(bass_path, 22050)
    harmonic, _ = librosa.effects.hpss(y)
    hop = 256
    f0, voiced_flag, voiced_prob = librosa.pyin(
        harmonic,
        fmin=hz_for_midi(MIDI_BASS[0]),
        fmax=hz_for_midi(MIDI_BASS[1]),
        sr=sr,
        frame_length=2048,
        hop_length=hop,
        fill_na=np.nan,
    )
    if f0 is None or voiced_prob is None:
        raise RuntimeError("pYIN returned no F0")
    f0 = np.asarray(f0, dtype=float)
    voiced_prob = np.asarray(voiced_prob, dtype=float)
    midi = librosa.hz_to_midi(f0)
    valid = np.isfinite(midi) & np.isfinite(voiced_prob) & (voiced_prob >= 0.70) & (midi >= MIDI_BASS[0] - 0.5) & (midi <= MIDI_BASS[1] + 0.5)

    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    onset_frames = set(int(x) for x in np.asarray(librosa.onset.onset_detect(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=hop,
        backtrack=True,
        units="frames",
    ), dtype=int).tolist())

    boundaries = {0, len(midi)} | {x for x in onset_frames if 0 < x < len(midi)}
    for i in range(1, len(midi)):
        if bool(valid[i]) != bool(valid[i - 1]):
            boundaries.add(i)
    i = 3
    while i + 3 < len(midi):
        if valid[i-3:i].all() and valid[i:i+3].all():
            before = midi[i-3:i]
            after = midi[i:i+3]
            if float(np.std(before)) <= 0.40 and float(np.std(after)) <= 0.40 and abs(float(np.median(after) - np.median(before))) >= 0.70:
                boundaries.add(i)
                i += 3
                continue
        i += 1

    bounds = sorted(boundaries)
    events: list[dict[str, Any]] = []
    dropped_short = 0
    dropped_unvoiced = 0
    for a, b in zip(bounds, bounds[1:]):
        if b <= a:
            continue
        duration = (b - a) * hop / sr
        if duration < 0.070:
            dropped_short += 1
            continue
        mask = valid[a:b]
        if int(mask.sum()) < max(2, int(math.ceil((b - a) * 0.40))):
            dropped_unvoiced += 1
            continue
        vals = midi[a:b][mask]
        probs = voiced_prob[a:b][mask]
        pitch = int(round(float(np.median(vals))))
        if not MIDI_BASS[0] <= pitch <= MIDI_BASS[1]:
            continue
        start = float(a * hop / sr)
        end = float(b * hop / sr)
        event = map_event(
            start,
            pitch,
            "pyin-bass",
            float(np.median(probs)),
            end,
            timebase,
            {"voicedProbabilityMedian": float(np.median(probs)), "rawMidiMedian": float(np.median(vals))},
        )
        if event is not None:
            events.append(event)
    return events, {
        "pyinFrameCount": int(len(midi)),
        "voicedFrameCount": int(valid.sum()),
        "onsetFrameCount": int(len(onset_frames)),
        "segmentCountBeforeDedup": int(len(events)),
        "droppedShortSegments": int(dropped_short),
        "droppedLowVoicingSegments": int(dropped_unvoiced),
    }


def guitar_cqt(guitar_path: Path) -> dict[str, Any]:
    import librosa

    y, sr = load_audio(guitar_path, 22050)
    harmonic, _ = librosa.effects.hpss(y)
    hop = 256
    bins_per_octave = 36
    midi_min, midi_max = MIDI_GUITAR
    fmin = hz_for_midi(midi_min)
    n_bins = (midi_max - midi_min) * 3 + 3
    cqt = np.abs(librosa.cqt(
        harmonic,
        sr=sr,
        hop_length=hop,
        fmin=fmin,
        n_bins=n_bins,
        bins_per_octave=bins_per_octave,
    ))
    salience = np.zeros((midi_max - midi_min + 1, cqt.shape[1]), dtype=np.float32)
    for midi_value in range(midi_min, midi_max + 1):
        center = (midi_value - midi_min) * 3
        lo = max(0, center - 1)
        hi = min(cqt.shape[0], center + 2)
        salience[midi_value - midi_min] = np.max(cqt[lo:hi], axis=0)
    salience = np.log1p(salience * 100.0)
    frame_med = np.median(salience, axis=0)
    frame_mad = np.median(np.abs(salience - frame_med[None, :]), axis=0) * 1.4826 + 1e-9
    high_threshold = frame_med + 3.0 * frame_mad
    support_threshold = frame_med + 1.5 * frame_mad
    sustain_threshold = frame_med + 1.0 * frame_mad
    flux = np.maximum(0.0, np.diff(salience, axis=1, prepend=salience[:, :1]))
    flux_med = np.median(flux, axis=0)
    flux_mad = np.median(np.abs(flux - flux_med[None, :]), axis=0) * 1.4826 + 1e-9
    flux_threshold = flux_med + 2.0 * flux_mad
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    onset_frames = np.asarray(librosa.onset.onset_detect(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=hop,
        backtrack=True,
        units="frames",
    ), dtype=int)
    return {
        "y": y,
        "sr": sr,
        "hop": hop,
        "salience": salience,
        "highThreshold": high_threshold,
        "supportThreshold": support_threshold,
        "sustainThreshold": sustain_threshold,
        "flux": flux,
        "fluxThreshold": flux_threshold,
        "onsetFrames": onset_frames,
    }


def cqt_support(cqt: dict[str, Any], midi: int, start: float, window_seconds: float = 0.120) -> tuple[bool, float, float]:
    sal = cqt["salience"]
    sr = int(cqt["sr"])
    hop = int(cqt["hop"])
    row = midi - MIDI_GUITAR[0]
    frame = int(round(start * sr / hop))
    frame = int(np.clip(frame, 0, sal.shape[1] - 1))
    count = max(1, int(round(window_seconds * sr / hop)))
    hi = min(sal.shape[1], frame + count)
    vals = sal[row, frame:hi]
    thresholds = cqt["supportThreshold"][frame:hi]
    fraction = float(np.mean(vals >= thresholds)) if vals.size else 0.0
    onset_supported = bool(sal[row, frame] >= cqt["supportThreshold"][frame])
    ratio = float(sal[row, frame] / max(cqt["supportThreshold"][frame], 1e-9))
    return onset_supported or fraction >= 0.35, fraction, ratio


def basic_pitch_guitar(guitar_path: Path, cqt: dict[str, Any], timebase: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import predict

    model_path = Path(ICASSP_2022_MODEL_PATH)
    _model_output, _midi_data, note_events = predict(
        guitar_path,
        model_or_model_path=model_path,
        onset_threshold=0.50,
        frame_threshold=0.30,
        minimum_note_length=90.0,
        minimum_frequency=hz_for_midi(MIDI_GUITAR[0]),
        maximum_frequency=hz_for_midi(MIDI_GUITAR[1]),
        multiple_pitch_bends=False,
        melodia_trick=True,
    )
    events: list[dict[str, Any]] = []
    rejected = 0
    for source_index, note in enumerate(note_events):
        if len(note) < 4:
            continue
        start = float(note[0]); end = float(note[1]); midi = int(round(float(note[2]))); amp = float(note[3])
        if not MIDI_GUITAR[0] <= midi <= MIDI_GUITAR[1]:
            continue
        supported, fraction, ratio = cqt_support(cqt, midi, start)
        strong = amp >= 0.80
        if not supported and not strong:
            rejected += 1
            continue
        source = "basic-pitch+cqt" if supported else "basic-pitch-strong"
        evidence = amp + min(1.0, fraction) * 0.5 + min(2.0, ratio) * 0.1
        event = map_event(start, midi, source, evidence, end, timebase, {
            "basicPitchAmplitude": amp,
            "cqtSupportFractionFirst120ms": fraction,
            "cqtOnsetSupportRatio": ratio,
            "basicPitchSourceIndex": source_index,
        })
        if event is not None:
            events.append(event)
    return events, {
        "basicPitchRawEventCount": len(note_events),
        "basicPitchRetainedCount": len(events),
        "basicPitchRejectedByCqtCount": rejected,
        "basicPitchModelPath": str(model_path),
        "basicPitchModelSha256": sha256_path(model_path),
    }


def cqt_completions(cqt: dict[str, Any], existing: list[dict[str, Any]], timebase: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sal = cqt["salience"]
    flux = cqt["flux"]
    high = cqt["highThreshold"]
    flux_thr = cqt["fluxThreshold"]
    sustain = cqt["sustainThreshold"]
    sr = int(cqt["sr"]); hop = int(cqt["hop"])
    existing_by_midi: dict[int, list[float]] = {}
    for e in existing:
        existing_by_midi.setdefault(int(e["midi"]), []).append(float(e["startSeconds"]))
    added: list[dict[str, Any]] = []
    considered = 0
    harmonic_rejected = 0
    duplicate_rejected = 0
    for frame in cqt["onsetFrames"]:
        frame = int(frame)
        if not 0 <= frame < sal.shape[1]:
            continue
        candidates: list[tuple[float, int]] = []
        for row in range(sal.shape[0]):
            midi = MIDI_GUITAR[0] + row
            value = float(sal[row, frame])
            if value < float(high[frame]) or float(flux[row, frame]) < float(flux_thr[frame]):
                continue
            left = float(sal[row - 1, frame]) if row > 0 else -math.inf
            right = float(sal[row + 1, frame]) if row + 1 < sal.shape[0] else -math.inf
            if value < left or value < right:
                continue
            considered += 1
            harmonic = False
            for interval in (12, 19, 24):
                lower = midi - interval
                if lower < MIDI_GUITAR[0]:
                    continue
                lower_value = float(sal[lower - MIDI_GUITAR[0], frame])
                if lower_value > value * 1.15:
                    harmonic = True
                    break
            if harmonic:
                harmonic_rejected += 1
                continue
            candidates.append((value, midi))
        candidates.sort(reverse=True)
        for value, midi in candidates[:6]:
            start = frame * hop / sr
            if any(abs(start - old) <= 0.060 for old in existing_by_midi.get(midi, [])):
                duplicate_rejected += 1
                continue
            row = midi - MIDI_GUITAR[0]
            end_frame = frame + 1
            max_frames = int(round(2.0 * sr / hop))
            while end_frame < sal.shape[1] and end_frame - frame < max_frames:
                if float(sal[row, end_frame]) < float(sustain[end_frame]):
                    break
                end_frame += 1
            end = end_frame * hop / sr
            if end - start < 0.070:
                continue
            ratio = value / max(float(high[frame]), 1e-9)
            event = map_event(start, midi, "cqt-onset-completion", ratio, end, timebase, {
                "cqtHighThresholdRatio": float(ratio),
                "cqtFlux": float(flux[row, frame]),
                "cqtFluxThreshold": float(flux_thr[frame]),
            })
            if event is None:
                continue
            added.append(event)
            existing_by_midi.setdefault(midi, []).append(start)
    return added, {
        "cqtOnsetFrameCount": int(len(cqt["onsetFrames"])),
        "cqtPeakCandidatesConsidered": considered,
        "cqtHarmonicRejected": harmonic_rejected,
        "cqtNearDuplicateRejected": duplicate_rejected,
        "cqtCompletionCount": len(added),
    }


def deduplicate(events: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[tuple[int, int], dict[str, Any]] = {}
    for event in events:
        key = (int(event["snappedAbsoluteGridStep"]), int(event["midi"]))
        old = best.get(key)
        if old is None or (float(event.get("evidence", 0.0)), -float(event["startSeconds"]), str(event["source"])) > (float(old.get("evidence", 0.0)), -float(old["startSeconds"]), str(old["source"])):
            best[key] = event
    return sorted(best.values(), key=lambda e: (int(e["snappedAbsoluteGridStep"]), int(e["midi"]), str(e["source"])))


def structural_qc(guitar: list[dict[str, Any]], bass: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    if not guitar: errors.append("empty combinedGuitar")
    if not bass: errors.append("empty bass")
    for label, rows, limits in (("combinedGuitar", guitar, MIDI_GUITAR), ("bass", bass, MIDI_BASS)):
        seen = set()
        for i, e in enumerate(rows):
            required = ("measure", "step", "midi", "startSeconds", "rawGridStep", "source")
            if any(k not in e for k in required):
                errors.append(f"{label}[{i}] missing required field")
                continue
            if not isinstance(e["step"], int) or not 0 <= e["step"] <= 15:
                errors.append(f"{label}[{i}] invalid snapped step")
            if int(e["measure"]) < 1:
                errors.append(f"{label}[{i}] invalid measure")
            if not limits[0] <= int(e["midi"]) <= limits[1]:
                errors.append(f"{label}[{i}] MIDI out of range")
            for key in ("startSeconds", "endSeconds", "rawGridStep", "evidence"):
                if not math.isfinite(float(e[key])):
                    errors.append(f"{label}[{i}] nonfinite {key}")
            if float(e["endSeconds"]) < float(e["startSeconds"]):
                errors.append(f"{label}[{i}] negative duration")
            key = (int(e["snappedAbsoluteGridStep"]), int(e["midi"]))
            if key in seen:
                errors.append(f"{label}[{i}] duplicate snapped MIDI/grid row")
            seen.add(key)
    if errors:
        raise RuntimeError("structural QC failed: " + "; ".join(errors[:20]))
    return {
        "validation": "PASS",
        "combinedGuitarCount": len(guitar),
        "bassCount": len(bass),
        "combinedGuitarUniqueRows": len({(e["snappedAbsoluteGridStep"], e["midi"]) for e in guitar}),
        "bassUniqueRows": len({(e["snappedAbsoluteGridStep"], e["midi"]) for e in bass}),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mix", type=Path, required=True)
    ap.add_argument("--guitar", type=Path, required=True)
    ap.add_argument("--bass", type=Path, required=True)
    ap.add_argument("--drums", type=Path, required=True)
    ap.add_argument("--preregistration", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists() or args.receipt.exists():
        raise RuntimeError("V155 output/receipt already exists; one-candidate policy")
    for p in (args.mix, args.guitar, args.bass, args.drums, args.preregistration):
        if not p.is_file(): raise FileNotFoundError(p)

    versions = {
        "numpy": np.__version__,
        "librosa": package_version("librosa"),
        "demucs": package_version("demucs"),
        "basic-pitch": package_version("basic-pitch"),
        "imageio-ffmpeg": package_version("imageio-ffmpeg"),
        "torch": package_version("torch"),
    }
    expected = {
        "numpy": "1.26.4",
        "librosa": "0.11.0",
        "demucs": "4.1.0",
        "basic-pitch": "0.4.0",
        "imageio-ffmpeg": "0.6.0",
    }
    for k, v in expected.items():
        if versions[k] != v:
            raise RuntimeError(f"dependency drift {k}: {versions[k]} != {v}")
    if not versions["torch"].startswith("2.8.0"):
        raise RuntimeError(f"torch drift: {versions['torch']}")

    timebase = derive_timebase(args.mix, args.drums, args.bass)
    bass_raw, bass_diag = bass_events(args.bass, timebase)
    cqt = guitar_cqt(args.guitar)
    guitar_bp, bp_diag = basic_pitch_guitar(args.guitar, cqt, timebase)
    guitar_cqt_added, cqt_diag = cqt_completions(cqt, guitar_bp, timebase)
    guitar = deduplicate(guitar_bp + guitar_cqt_added)
    bass = deduplicate(bass_raw)
    qc = structural_qc(guitar, bass)

    safety = {
        "referenceRead": False,
        "humanCorrection": False,
        "referenceGuidedFiltering": False,
        "thresholdSweep": False,
        "candidateVariantSelection": False,
        "modalUsed": False,
        "cudaGpuUsed": False,
        "mainOrProductionModified": False,
    }
    payload = {
        "schema": "dadrock.tabs.v155.reference-blind-generated.v1",
        "song": {"artist": "Lenny Kravitz", "title": "Are You Gonna Go My Way"},
        "classification": "single-preregistered-reference-blind-cpu-candidate",
        "preregistrationSha256": sha256_file(args.preregistration),
        "generatorGitBlob": os.environ.get("V155_GENERATOR_GIT_BLOB"),
        "timebase": timebase,
        "streams": {"combinedGuitar": guitar, "bass": bass},
        "diagnostics": {"bass": bass_diag, "guitarBasicPitch": bp_diag, "guitarCqt": cqt_diag, "structuralQc": qc},
        "safety": safety,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cache = Path.home() / ".cache/torch/hub/checkpoints"
    checkpoints = []
    if cache.exists():
        for f in sorted(x for x in cache.iterdir() if x.is_file()):
            checkpoints.append({"name": f.name, "bytes": f.stat().st_size, "sha256": sha256_file(f)})
    receipt = {
        "schema": "dadrock.tabs.v155.reference-blind-generation-receipt.v1",
        "validation": "PASS",
        "outputPath": str(args.output),
        "outputSha256": sha256_file(args.output),
        "counts": {"combinedGuitar": len(guitar), "bass": len(bass)},
        "identities": {
            "mixSha256": sha256_file(args.mix),
            "guitarStemSha256": sha256_file(args.guitar),
            "bassStemSha256": sha256_file(args.bass),
            "drumsStemSha256": sha256_file(args.drums),
            "preregistrationSha256": sha256_file(args.preregistration),
            "generatorGitBlob": os.environ.get("V155_GENERATOR_GIT_BLOB"),
            "demucsCheckpointFiles": checkpoints,
            "packages": versions,
        },
        "timebaseSummary": {
            "beatCount": len(timebase["beatTimesSeconds"]),
            "beatTrackerTempoBpm": timebase["beatTrackerTempoBpm"],
            "robustMedianTempoBpm": timebase["robustMedianTempoBpm"],
            "downbeatPhase": timebase["downbeatPhase"],
            "originBeatIndex": timebase["originBeatIndex"],
            "firstDetectedOnsetSeconds": timebase["firstDetectedOnsetSeconds"],
        },
        "structuralQc": qc,
        "safety": {**safety, "professionalReferencePathsOpened": 0, "referenceFacingScoreCalls": 0},
    }
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "validation": "PASS",
        "combinedGuitar": len(guitar),
        "bass": len(bass),
        "candidateSha256": receipt["outputSha256"],
        "beatCount": len(timebase["beatTimesSeconds"]),
        "robustMedianTempoBpm": timebase["robustMedianTempoBpm"],
        "downbeatPhase": timebase["downbeatPhase"],
        "originBeatIndex": timebase["originBeatIndex"],
        "referenceRead": False,
        "scoreCalls": 0,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
