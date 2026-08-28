#!/usr/bin/env python3
"""Diagnostic-only V154 audio/grid-origin audit.

This reads the already-consumed frozen generated candidate and the exact historical
audio. It does not read professional references, call the official scorer, or emit
any corrected candidate. The reference-derived -13.25-step shift is used only as a
frozen diagnostic comparator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
import imageio_ffmpeg

TEMPO_BPM = 129.19921875
STEPS_PER_BEAT = 4
STEP_SECONDS = (60.0 / TEMPO_BPM) / STEPS_PER_BEAT
FROZEN_DIAGNOSTIC_SHIFT_STEPS = -13.25
EXPECTED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EXPECTED_GENERATED_SHA256 = "1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def first_sustained(mask: np.ndarray, needed: int) -> int | None:
    if needed <= 1:
        idx = np.flatnonzero(mask)
        return int(idx[0]) if len(idx) else None
    run = np.convolve(mask.astype(np.int16), np.ones(needed, dtype=np.int16), mode="valid")
    idx = np.flatnonzero(run >= needed)
    return int(idx[0]) if len(idx) else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", type=Path, required=True)
    ap.add_argument("--generated", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    if args.output.exists():
        raise RuntimeError(f"diagnostic output already exists: {args.output}")
    audio_sha = sha256_file(args.audio)
    generated_sha = sha256_file(args.generated)
    if audio_sha != EXPECTED_AUDIO_SHA256:
        raise RuntimeError(f"audio identity drift: {audio_sha}")
    if generated_sha != EXPECTED_GENERATED_SHA256:
        raise RuntimeError(f"generated identity drift: {generated_sha}")

    generated = json.loads(args.generated.read_text())
    earliest = {}
    for name in ("combinedGuitar", "bass"):
        rows = generated["streams"][name]
        starts = sorted(float(r["startSeconds"]) for r in rows)
        earliest[name] = {
            "firstStartSeconds": starts[0],
            "firstStartAsGridStepsFromAudioZero": starts[0] / STEP_SECONDS,
            "firstFiveStartSeconds": starts[:5],
        }

    with tempfile.TemporaryDirectory() as td:
        wav_path = Path(td) / "mono.wav"
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.check_call([
            ffmpeg, "-v", "error", "-i", str(args.audio), "-vn",
            "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", str(wav_path),
        ])
        with wave.open(str(wav_path), "rb") as wf:
            if wf.getsampwidth() != 2 or wf.getnchannels() != 1:
                raise RuntimeError("unexpected decoded WAV format")
            sr = wf.getframerate()
            raw = wf.readframes(wf.getnframes())
        samples = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0

    frame_ms = 20.0
    hop_ms = 5.0
    frame_n = max(1, int(round(sr * frame_ms / 1000.0)))
    hop_n = max(1, int(round(sr * hop_ms / 1000.0)))
    # Analyze only the opening 6 seconds; this is an origin audit, not a song-wide tuner.
    max_n = min(len(samples), int(sr * 6.0))
    x = samples[:max_n]
    starts = np.arange(0, max(1, len(x) - frame_n + 1), hop_n, dtype=np.int64)
    rms = np.array([math.sqrt(float(np.mean(x[s:s + frame_n] ** 2))) for s in starts])
    dbfs = 20.0 * np.log10(np.maximum(rms, 1e-12))
    peak_dbfs = float(np.max(dbfs))

    # Multiple fixed relative thresholds make the finding auditable rather than
    # dependent on one hand-picked activity threshold.
    activity = {}
    sustain_frames = max(1, int(round(100.0 / hop_ms)))
    for below_peak in (40.0, 35.0, 30.0, 25.0, 20.0):
        threshold = peak_dbfs - below_peak
        idx = first_sustained(dbfs >= threshold, sustain_frames)
        seconds = None if idx is None else float(starts[idx] / sr)
        activity[f"peakMinus{int(below_peak)}Db"] = {
            "thresholdDbfs": threshold,
            "firstSustained100msSeconds": seconds,
            "gridStepsFromAudioZero": None if seconds is None else seconds / STEP_SECONDS,
        }

    # Also expose the strongest envelope rises in the opening 3 s, without using
    # any reference alignment. 50-ms smoothing suppresses AAC/sample noise.
    smooth_frames = max(1, int(round(50.0 / hop_ms)))
    kernel = np.ones(smooth_frames) / smooth_frames
    smoothed = np.convolve(rms, kernel, mode="same")
    delta = np.diff(smoothed, prepend=smoothed[0])
    opening_mask = (starts / sr) <= 3.0
    candidate_indices = np.flatnonzero(opening_mask)
    ranked = candidate_indices[np.argsort(delta[candidate_indices])[::-1]]
    selected = []
    min_sep_seconds = 0.12
    for idx in ranked:
        t = float(starts[idx] / sr)
        if all(abs(t - old["seconds"]) >= min_sep_seconds for old in selected):
            selected.append({"seconds": t, "gridStepsFromAudioZero": t / STEP_SECONDS, "rise": float(delta[idx])})
        if len(selected) >= 10:
            break
    selected.sort(key=lambda z: z["seconds"])

    implied_seconds = abs(FROZEN_DIAGNOSTIC_SHIFT_STEPS) * STEP_SECONDS
    comparisons = {}
    for key, item in activity.items():
        t = item["firstSustained100msSeconds"]
        if t is not None:
            comparisons[key] = {
                "activityMinusImpliedShiftSeconds": t - implied_seconds,
                "absoluteDifferenceSeconds": abs(t - implied_seconds),
                "absoluteDifferenceGridSteps": abs(t - implied_seconds) / STEP_SECONDS,
            }

    output = {
        "schema": "dadrock.tabs.v154.audio-grid-origin-diagnostic.v1",
        "classification": "post-score-diagnostic-only-no-candidate-correction",
        "validation": "PASS",
        "frozenIdentities": {"audioSha256": audio_sha, "generatedSha256": generated_sha},
        "grid": {
            "tempoBpm": TEMPO_BPM,
            "stepsPerBeat": STEPS_PER_BEAT,
            "stepDurationSeconds": STEP_SECONDS,
            "historicalTranscriberOrigin": "audio_time_zero_equals_measure_1_step_0",
        },
        "frozenPostScoreComparator": {
            "bestDiagnosticGeneratedShiftSteps": FROZEN_DIAGNOSTIC_SHIFT_STEPS,
            "equivalentPositiveAudioLeadSeconds": implied_seconds,
            "note": "Comparator was frozen by prior consumed-candidate diagnostic; this script does not search offsets.",
        },
        "audioOpening": {
            "sampleRate": sr,
            "analysisSeconds": max_n / sr,
            "frameMs": frame_ms,
            "hopMs": hop_ms,
            "peakFrameDbfs": peak_dbfs,
            "firstSustainedActivity": activity,
            "strongEnvelopeRisesFirst3Seconds": selected,
        },
        "generatedOpening": earliest,
        "comparisonToFrozenShift": comparisons,
        "policy": {
            "professionalReferenceRead": False,
            "officialScorerCalled": False,
            "candidateModified": False,
            "correctedCandidateWritten": False,
            "thresholdSweepForGeneration": False,
            "gpuUsed": False,
            "mainOrProductionModified": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
