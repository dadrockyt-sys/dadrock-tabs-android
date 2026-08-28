#!/usr/bin/env python3
"""Preregistered V155 reference-blind beat/downbeat grid audit v2."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import wave
from pathlib import Path

import numpy as np

SR = 22050
HOP = 256
EXPECTED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
PREREG = Path("debug/v155-cpu-autonomous/grid-origin-audit-v2-preregistration.json")
EXPECTED_PREREG_BLOB = "b8d04ed211873c7a3966e19c14617b25fd65e52e"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def read_pcm16_mono(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as wf:
        if wf.getframerate() != SR or wf.getnchannels() != 1 or wf.getsampwidth() != 2:
            raise RuntimeError("unexpected decoded WAV format")
        raw = wf.readframes(wf.getnframes())
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0


def robust_positive(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    med = float(np.median(x))
    mad = float(np.median(np.abs(x - med)))
    scale = max(1e-12, 1.4826 * mad)
    z = np.maximum(0.0, (x - med) / scale)
    positive = z[z > 0]
    if len(positive):
        cap = float(np.percentile(positive, 95))
        if cap > 0:
            z = np.minimum(z, cap) / cap
    return z


def find_stable_run(beat_times: np.ndarray) -> tuple[int, int, bool, float, float]:
    if len(beat_times) < 12:
        if len(beat_times) < 2:
            raise RuntimeError("insufficient tracked beats")
        d = np.diff(beat_times)
        return 0, len(beat_times), True, float(np.median(d)), float(np.std(d) / max(np.mean(d), 1e-12))

    for start in range(0, len(beat_times) - 11):
        window = beat_times[start : start + 12]
        d = np.diff(window)
        med = float(np.median(d))
        if med <= 0:
            continue
        if np.all(np.abs(d - med) <= 0.15 * med):
            end = start + 12
            while end < len(beat_times):
                interval = float(beat_times[end] - beat_times[end - 1])
                if abs(interval - med) > 0.15 * med:
                    break
                end += 1
            all_d = np.diff(beat_times[start:end])
            cv = float(np.std(all_d) / max(np.mean(all_d), 1e-12)) if len(all_d) else 0.0
            return start, end, False, med, cv

    d = np.diff(beat_times)
    return 0, len(beat_times), True, float(np.median(d)), float(np.std(d) / max(np.mean(d), 1e-12))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio-m4a", type=Path, required=True)
    ap.add_argument("--decoded-wav", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    if args.output.exists():
        raise RuntimeError(f"write-once output already exists: {args.output}")
    if sha256_file(args.audio_m4a) != EXPECTED_AUDIO_SHA256:
        raise RuntimeError("audio identity mismatch")
    if not PREREG.is_file() or git_blob_sha(PREREG) != EXPECTED_PREREG_BLOB:
        raise RuntimeError("preregistration identity mismatch")

    import librosa
    if librosa.__version__ != "0.11.0":
        raise RuntimeError(f"librosa version mismatch: {librosa.__version__}")

    y = read_pcm16_mono(args.decoded_wav)
    harmonic, percussive = librosa.effects.hpss(y)
    onset = librosa.onset.onset_strength(y=percussive, sr=SR, hop_length=HOP)

    tempo_arr = librosa.feature.tempo(
        onset_envelope=onset,
        sr=SR,
        hop_length=HOP,
        aggregate=np.median,
        max_tempo=200.0,
    )
    tempo = float(np.asarray(tempo_arr).reshape(-1)[0])
    while tempo < 70.0:
        tempo *= 2.0
    while tempo > 200.0:
        tempo /= 2.0

    _, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset,
        sr=SR,
        hop_length=HOP,
        bpm=tempo,
        sparse=True,
    )
    beat_frames = np.asarray(beat_frames, dtype=int)
    beat_times = librosa.frames_to_time(beat_frames, sr=SR, hop_length=HOP)
    if len(beat_times) < 4:
        raise RuntimeError("beat tracker returned fewer than four beats")

    mag = np.abs(librosa.stft(y, n_fft=2048, hop_length=HOP))
    freqs = librosa.fft_frequencies(sr=SR, n_fft=2048)
    low_idx = np.where((freqs >= 30.0) & (freqs <= 220.0))[0]
    if len(low_idx) == 0:
        raise RuntimeError("no low-frequency bins")
    low_energy = np.log1p(np.mean(mag[low_idx, :], axis=0) * 100.0)
    low_flux = np.maximum(0.0, np.diff(low_energy, prepend=low_energy[0]))

    n = min(len(onset), len(low_flux))
    accent = 0.5 * robust_positive(onset[:n]) + 0.5 * robust_positive(low_flux[:n])

    start, end, fallback, interval_med, interval_cv = find_stable_run(beat_times)
    stable_global_indices = np.arange(start, end, dtype=int)
    stable_frames = beat_frames[start:end]
    stable_frames = stable_frames[stable_frames < len(accent)]
    stable_global_indices = stable_global_indices[: len(stable_frames)]
    if len(stable_frames) < 4:
        raise RuntimeError("stable beat run too short after frame alignment")

    rows = []
    for residue in range(4):
        mask = (stable_global_indices % 4) == residue
        vals = accent[stable_frames[mask]]
        if len(vals) == 0:
            score = -1.0
            median = 0.0
            q25 = 0.0
        else:
            median = float(np.median(vals))
            q25 = float(np.percentile(vals, 25))
            score = median + 0.35 * q25
        rows.append({
            "residue": residue,
            "beats": int(len(vals)),
            "medianAccent": median,
            "q25Accent": q25,
            "score": float(score),
        })
    ranked = sorted(rows, key=lambda r: (-r["score"], r["residue"]))
    best = ranked[0]
    second = ranked[1]
    chosen = int(best["residue"])
    margin = float((best["score"] - second["score"]) / max(abs(best["score"]), 1e-12))

    candidates = [i for i in stable_global_indices.tolist() if i % 4 == chosen]
    if not candidates:
        raise RuntimeError("no downbeat candidate in stable run")
    origin_beat_index = int(candidates[0])
    origin_seconds = float(beat_times[origin_beat_index])
    step_seconds = (60.0 / tempo) / 4.0

    mapped = []
    for i, t in enumerate(beat_times[:16]):
        mapped.append({
            "beatIndex": i,
            "timeSeconds": float(t),
            "musicalSixteenth": float((t - origin_seconds) / step_seconds),
        })

    payload = {
        "schema": "dadrock.tabs.v155.grid-origin-audit-v2.v1",
        "classification": "reference-blind-cpu-beat-downbeat-grid-audit",
        "validation": "PASS",
        "audio": {
            "sha256": EXPECTED_AUDIO_SHA256,
            "sampleRate": SR,
            "durationSeconds": float(len(y) / SR),
        },
        "timebase": {
            "tempoBpmAudioDerived": tempo,
            "stepDurationSeconds": step_seconds,
            "trackedBeatCount": int(len(beat_times)),
            "first16BeatTimesSeconds": [float(x) for x in beat_times[:16]],
            "stableRun": {
                "startBeatIndex": int(start),
                "endBeatIndexExclusive": int(end),
                "beatCount": int(end - start),
                "fallbackUsed": bool(fallback),
                "medianIntervalSeconds": interval_med,
                "intervalCv": interval_cv,
            },
            "barResidueScores": rows,
            "chosenDownbeatResidue": chosen,
            "barPhaseRelativeMargin": margin,
            "originBeatIndex": origin_beat_index,
            "originSeconds": origin_seconds,
            "first16MappedBeats": mapped,
            "mappingRule": "musicalAbsoluteStep=(audioSeconds-originSeconds)/(60/tempoBpmAudioDerived/4)",
        },
        "policy": {
            "professionalReferenceRead": False,
            "officialScorerCalled": False,
            "v154PostScoreDiagnosticRead": False,
            "knownReferenceDerivedShiftRead": False,
            "candidateGenerated": False,
            "candidateModified": False,
            "candidateSelected": False,
            "cpuOnly": True,
            "gpuCudaModalL4Used": False,
            "mainOrProductionModified": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "validation": "PASS",
        "tempoBpmAudioDerived": tempo,
        "trackedBeatCount": int(len(beat_times)),
        "stableRunStartBeat": int(start),
        "stableRunFallback": bool(fallback),
        "chosenDownbeatResidue": chosen,
        "barPhaseRelativeMargin": margin,
        "originSeconds": origin_seconds,
        "output": str(args.output),
        "sha256": sha256_file(args.output),
        "professionalReferenceRead": False,
        "officialScorerCalled": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
