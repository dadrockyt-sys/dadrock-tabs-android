#!/usr/bin/env python3
"""Build sealed V162 reference-blind beat + shared 16th subdivision timebase before pitch."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import warnings
from pathlib import Path
from typing import Any

import numpy as np

from event_logic_v162 import build_subdivision_lattice

SR = 22050
HOP = 256
EPS = 1e-12
SCHEMA = "dadrock.tabs.v162.reference-blind-subdivision-timebase.v1"
TARGET_ARTIST = "Lenny Kravitz"
TARGET_TITLE = "Are You Gonna Go My Way"
PHASES = (0, 1, 2, 3)
WEIGHTS = {
    "drumsAccent": 1.0,
    "mixAccent": 0.5,
    "bassAccent": 0.5,
    "lowFrequencyFlux": 0.75,
    "harmonicChangeNovelty": 0.75,
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def load_mono(path: Path) -> np.ndarray:
    import librosa
    y, sr = librosa.load(str(path), sr=SR, mono=True)
    y = np.asarray(y, dtype=np.float32)
    if sr != SR or y.size == 0 or not np.all(np.isfinite(y)):
        raise RuntimeError(f"invalid finite mono analysis load: {path}")
    return y


def onset_strength(y: np.ndarray) -> np.ndarray:
    import librosa
    x = np.asarray(librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP), dtype=float)
    if x.size == 0 or not np.all(np.isfinite(x)):
        raise RuntimeError("nonfinite or empty onset-strength feature")
    return x


def positive_unit_scale(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.size == 0 or not np.all(np.isfinite(x)):
        raise RuntimeError("positiveUnitScale received empty/nonfinite input")
    x = np.maximum(x, 0.0)
    peak = float(np.max(x))
    if not math.isfinite(peak) or peak <= EPS:
        raise RuntimeError("positiveUnitScale input has no strictly positive value")
    return x / peak


def robust_z(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.size == 0 or not np.all(np.isfinite(x)):
        raise RuntimeError("robust-z received empty/nonfinite input")
    med = float(np.median(x))
    scale = float(np.median(np.abs(x - med))) * 1.4826
    if not math.isfinite(scale) or scale < 1e-9:
        std = float(np.std(x))
        if not math.isfinite(std) or std < 1e-9:
            return np.zeros_like(x)
        scale = std
    return (x - med) / scale


def low_frequency_flux(y: np.ndarray) -> np.ndarray:
    import librosa
    magnitude = np.abs(librosa.stft(y, n_fft=2048, hop_length=HOP))
    if magnitude.size == 0 or not np.all(np.isfinite(magnitude)):
        raise RuntimeError("invalid low-frequency STFT magnitude")
    freqs = librosa.fft_frequencies(sr=SR, n_fft=2048)
    band = magnitude[freqs <= 200.0]
    if band.shape[1] == 0:
        return np.zeros(0, dtype=float)
    diff = np.diff(band, axis=1, prepend=band[:, :1])
    return np.sum(np.maximum(diff, 0.0), axis=0)


def chroma_change(y: np.ndarray) -> np.ndarray:
    import librosa
    chroma = np.asarray(librosa.feature.chroma_cqt(y=y, sr=SR, hop_length=HOP, n_chroma=12), dtype=float)
    if chroma.size == 0 or not np.all(np.isfinite(chroma)):
        raise RuntimeError("invalid harmonic chroma feature")
    diff = np.diff(chroma, axis=1, prepend=chroma[:, :1])
    return np.linalg.norm(diff, axis=0)


def sample_feature(feature: np.ndarray, frames: np.ndarray) -> np.ndarray:
    if feature.size == 0:
        return np.zeros(len(frames), dtype=float)
    idx = np.clip(np.asarray(frames, dtype=int), 0, len(feature) - 1)
    return np.asarray(feature[idx], dtype=float)


def select_phase(weighted_accent: np.ndarray) -> tuple[int, dict[str, float]]:
    if weighted_accent.size == 0 or not np.all(np.isfinite(weighted_accent)):
        raise RuntimeError("invalid phase accent evidence")
    scores: dict[int, float] = {}
    indices = np.arange(len(weighted_accent), dtype=int)
    for phase in PHASES:
        down = weighted_accent[indices % 4 == phase]
        other = weighted_accent[indices % 4 != phase]
        if down.size == 0 or other.size == 0:
            raise RuntimeError("insufficient accepted beats for four-phase scoring")
        scores[phase] = float(np.mean(down) - np.mean(other))
    best = 0
    best_score = scores[0]
    for phase in PHASES[1:]:
        score = scores[phase]
        if score > best_score + 1e-12:
            best, best_score = phase, score
    return best, {str(p): scores[p] for p in PHASES}


def identity(path: Path) -> dict[str, Any]:
    return {"path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-audio", type=Path, required=True)
    parser.add_argument("--mix", type=Path, required=True)
    parser.add_argument("--drums", type=Path, required=True)
    parser.add_argument("--bass", type=Path, required=True)
    parser.add_argument("--guitar", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--implementation-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.output.exists():
        raise RuntimeError("V162 timebase is write-once")
    for path in (args.source_audio, args.mix, args.drums, args.bass, args.guitar, args.preregistration, args.implementation_contract):
        if not path.is_file():
            raise RuntimeError(f"missing required V162 timebase input: {path}")

    prereg = load_json(args.preregistration)
    contract = load_json(args.implementation_contract)
    if prereg.get("version") != "V162" or prereg.get("status") != "PREREGISTERED_BEFORE_IMPLEMENTATION_CODE":
        raise RuntimeError("invalid V162 preregistration state")
    if contract.get("version") != "V162" or contract.get("status") != "SEALED_BEFORE_IMPLEMENTATION_CODE":
        raise RuntimeError("invalid V162 implementation-contract state")
    if contract.get("canonicalSchemas", {}).get("timebase") != SCHEMA:
        raise RuntimeError("V162 timebase schema contract drift")
    geometry = contract.get("analysisGeometry") or {}
    if geometry.get("sampleRate") != SR or geometry.get("hopLength") != HOP:
        raise RuntimeError("V162 analysis geometry contract drift")

    source_contract = contract.get("sourceAndSeparation") or {}
    source_identity = identity(args.source_audio)
    mix_identity = identity(args.mix)
    if source_identity["sha256"] != source_contract.get("sourceSha256") or source_identity["bytes"] != source_contract.get("sourceBytes"):
        raise RuntimeError("V162 historical source-audio identity mismatch")
    if mix_identity["sha256"] != source_contract.get("normalizedWavSha256"):
        raise RuntimeError("V162 normalized-mix identity mismatch")

    captured: list[warnings.WarningMessage]
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        mix = load_mono(args.mix)
        drums = load_mono(args.drums)
        bass = load_mono(args.bass)
        env_mix = onset_strength(mix)
        env_drums = onset_strength(drums)
        env_bass = onset_strength(bass)
        n = min(len(env_mix), len(env_drums))
        if n == 0:
            raise RuntimeError("empty V162 fused/shared onset envelope")
        unit_mix = positive_unit_scale(env_mix[:n])
        unit_drums = positive_unit_scale(env_drums[:n])
        fused = 0.5 * unit_mix + 0.5 * unit_drums
        shared = 0.65 * unit_drums + 0.35 * unit_mix
        if not np.all(np.isfinite(fused)) or np.any(fused < 0.0) or not np.any(fused > 0.0):
            raise RuntimeError("V162 fused beat envelope domain failure")
        if not np.all(np.isfinite(shared)) or np.any(shared < 0.0) or not np.any(shared > 0.0):
            raise RuntimeError("V162 shared subdivision envelope domain failure")

        import librosa
        tempo, beat_frames = librosa.beat.beat_track(
            onset_envelope=fused,
            sr=SR,
            hop_length=HOP,
            start_bpm=120.0,
            tightness=100.0,
            sparse=True,
        )
        beat_frames = np.asarray(beat_frames, dtype=int)
        tempo_raw = np.asarray(tempo, dtype=float).reshape(-1)
        if tempo_raw.size != 1 or not math.isfinite(float(tempo_raw[0])) or float(tempo_raw[0]) <= 0.0:
            raise RuntimeError("V162 tracker tempo is not one finite positive scalar")
        tracker_tempo = float(tempo_raw[0])
        if len(beat_frames) < 8:
            raise RuntimeError(f"V162 insufficient accepted beats: {len(beat_frames)}")
        detected = np.asarray(librosa.frames_to_time(beat_frames, sr=SR, hop_length=HOP), dtype=float)
        if not np.all(np.isfinite(detected)) or not np.all(np.diff(detected) > 0.0):
            raise RuntimeError("V162 detected beat times are not finite/strictly increasing")
        features = {
            "drumsAccent": sample_feature(robust_z(env_drums), beat_frames),
            "mixAccent": sample_feature(robust_z(env_mix), beat_frames),
            "bassAccent": sample_feature(robust_z(env_bass), beat_frames),
            "lowFrequencyFlux": sample_feature(robust_z(low_frequency_flux(mix)), beat_frames),
            "harmonicChangeNovelty": sample_feature(robust_z(chroma_change(mix)), beat_frames),
        }
        weighted = sum(WEIGHTS[name] * features[name] for name in WEIGHTS)
        selected_phase, phase_scores = select_phase(np.asarray(weighted, dtype=float))

    warning_rows = [{"category": item.category.__name__, "message": str(item.message)} for item in captured]
    runtime_warnings = [item for item in captured if issubclass(item.category, RuntimeWarning)]
    if runtime_warnings:
        raise RuntimeError("V162 RuntimeWarning captured during timebase construction: " + "; ".join(str(x.message) for x in runtime_warnings))

    ibis = np.diff(detected)
    positive_early = ibis[: min(8, len(ibis))]
    positive_early = positive_early[positive_early > 0.0]
    if positive_early.size == 0:
        raise RuntimeError("V162 has no positive early inter-beat interval")
    early_period = float(np.median(positive_early))
    leading = int((-selected_phase) % 4)
    prefix = np.asarray([float(detected[0] - early_period * k) for k in range(leading, 0, -1)], dtype=float)
    grid_times = np.concatenate((prefix, detected)) if leading else detected.copy()
    grid_steps = 4.0 * np.arange(len(grid_times), dtype=float)
    detected_ordinals = leading + np.arange(len(detected), dtype=int)
    if not np.all(np.diff(grid_times) > 0.0):
        raise RuntimeError("V162 beat grid is not strictly increasing")

    subdivision_times = build_subdivision_lattice([float(x) for x in grid_times], shared)
    subdivision_steps = list(range(len(subdivision_times)))
    if len(subdivision_times) != 4 * len(grid_times) + 1:
        raise RuntimeError("V162 subdivision lattice length invariant failure")
    for beat_index, beat_time in enumerate(grid_times):
        if abs(float(subdivision_times[4 * beat_index]) - float(beat_time)) > 1e-12:
            raise RuntimeError("V162 beat anchor moved inside subdivision lattice")

    duration = float(len(mix) / SR)
    mean_ibi = float(np.mean(ibis))
    median_ibi = float(np.median(ibis))
    mean_bpm = float(60.0 / mean_ibi)
    median_bpm = float(60.0 / median_ibi)
    count_bpm = float(60.0 * len(detected) / duration)
    consistency = float(median_bpm / tracker_tempo)
    moved_interior = sum(
        1 for i, t in enumerate(subdivision_times[:-1])
        if i % 4 != 0 and abs(float(t) - (float(grid_times[i // 4]) + (i % 4) * (float((grid_times.tolist() + [subdivision_times[-1]])[i // 4 + 1]) - float(grid_times[i // 4])) / 4.0)) > (0.5 * HOP / SR)
    )

    safety = {
        "referenceRead": False,
        "professionalReferencePathsOpened": 0,
        "priorGeneratedCandidateRead": False,
        "priorScoreRead": False,
        "priorDiagnosticReadByRuntime": False,
        "V161CandidateRead": False,
        "gpu": False,
    }
    artifact = {
        "schema": SCHEMA,
        "song": {"artist": TARGET_ARTIST, "title": TARGET_TITLE},
        "audioIdentity": {"source": source_identity, "normalizedMix": mix_identity},
        "stemIdentities": {"drums": identity(args.drums), "bass": identity(args.bass), "guitar": identity(args.guitar)},
        "analysisSampleRate": SR,
        "hopLength": HOP,
        "audioDurationSeconds": duration,
        "trackerTempoBpm": tracker_tempo,
        "detectedBeatTimesSeconds": [float(x) for x in detected],
        "detectedBeatOrdinals": [int(x) for x in detected_ordinals],
        "gridBeatTimesSeconds": [float(x) for x in grid_times],
        "gridBeatSteps": [float(x) for x in grid_steps],
        "subdivisionTimesSeconds": [float(x) for x in subdivision_times],
        "subdivisionAbsoluteSteps": [int(x) for x in subdivision_steps],
        "selectedPhase": selected_phase,
        "phaseScores": phase_scores,
        "leadingBeatCount": leading,
        "earlyPeriodSeconds": early_period,
        "sharedSubdivisionEnvelope": {
            "formula": "0.65*unitDrums + 0.35*unitMix",
            "frameCount": int(len(shared)),
            "finite": bool(np.all(np.isfinite(shared))),
            "nonnegative": bool(np.all(shared >= 0.0)),
            "hasPositive": bool(np.any(shared > 0.0)),
        },
        "diagnostics": {
            "audioDurationSeconds": duration,
            "detectedBeatCount": int(len(detected)),
            "trackerTempoBpm": tracker_tempo,
            "meanInterBeatIntervalSeconds": mean_ibi,
            "medianInterBeatIntervalSeconds": median_ibi,
            "meanIbiImpliedBpm": mean_bpm,
            "medianIbiImpliedBpm": median_bpm,
            "beatCountDurationBpm": count_bpm,
            "tempoConsistencyRatio": consistency,
            "selectedPhase": selected_phase,
            "phaseScores": phase_scores,
            "leadingBeatCount": leading,
            "earlyPeriodSeconds": early_period,
            "firstGridTimeSeconds": float(grid_times[0]),
            "lastGridTimeSeconds": float(grid_times[-1]),
            "subdivisionCount": len(subdivision_times),
            "firstSubdivisionTimeSeconds": float(subdivision_times[0]),
            "lastSubdivisionTimeSeconds": float(subdivision_times[-1]),
            "movedInteriorSubdivisionCount": int(moved_interior),
            "fusedEnvelopeFinite": bool(np.all(np.isfinite(fused))),
            "fusedEnvelopeNonnegative": bool(np.all(fused >= 0.0)),
            "fusedEnvelopeHasPositive": bool(np.any(fused > 0.0)),
            "warningCount": len(warning_rows),
            "warningMessages": [row["message"] for row in warning_rows],
        },
        "warnings": warning_rows,
        "safety": safety,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({
        "timebase": str(args.output),
        "detectedBeats": len(detected),
        "selectedPhase": selected_phase,
        "subdivisionCount": len(subdivision_times),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
