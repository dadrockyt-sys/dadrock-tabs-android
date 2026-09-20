"""Reference-blind attacked-bend candidate extraction from Basic Pitch raw activations."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ONSET_THRESHOLD = 0.5
FRAME_SALIENCE_THRESHOLD = 0.3
MIDI_OFFSET = 21
CONTOUR_BINS_PER_SEMITONE = 3
MIN_MIDI = 40
MAX_MIDI = 88
EARLY_WINDOW_SECONDS = (0.035, 0.085)
LATE_WINDOW_SECONDS = (0.140, 0.240)
EARLY_PITCH_TOLERANCE_SEMITONES = 1.0
MIN_RISE_SEMITONES = 1.0
MAX_RISE_SEMITONES = 3.0
NATIVE_MATCH_TOLERANCE_SECONDS = 0.060
CANDIDATE_CLUSTER_SECONDS = 0.060
CANDIDATE_CLUSTER_SEMITONES = 2
FFT_HOP = 256
SAMPLE_RATE = 22050
ANNOTATIONS_N_FRAMES = (SAMPLE_RATE // FFT_HOP) * 2
AUDIO_N_SAMPLES = SAMPLE_RATE * 2 - FFT_HOP
WINDOW_OFFSET_SECONDS = ((FFT_HOP / SAMPLE_RATE) * (ANNOTATIONS_N_FRAMES - (AUDIO_N_SAMPLES / FFT_HOP)) + 0.0018)

def require(ok, message):
    if not ok:
        raise ValueError(message)

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)

def model_frame_times(n_frames: int) -> np.ndarray:
    idx = np.arange(n_frames, dtype=np.float64)
    times = idx * FFT_HOP / SAMPLE_RATE
    window_numbers = np.floor(idx / ANNOTATIONS_N_FRAMES)
    return times - WINDOW_OFFSET_SECONDS * window_numbers

def load_prediction(path):
    doc = json.loads(Path(path).read_text())
    require(doc.get("kind") == "whole-mix-basic-pitch-development-only", "unexpected prediction kind")
    require(doc.get("customerDeliveryEligible") is False, "prediction cannot authorize delivery")
    events = doc.get("events")
    require(isinstance(events, list), "prediction events missing")
    for row in events:
        require(isinstance(row, dict), "prediction event must be an object")
        require(finite(row.get("start")) and finite(row.get("end")) and 0 <= row["start"] < row["end"], "invalid prediction time")
        require(isinstance(row.get("midi"), int) and not isinstance(row.get("midi"), bool), "invalid prediction midi")
    return doc

def validate_raw(raw):
    require(set(raw) >= {"note", "onset", "contour"}, "raw arrays missing")
    note, onset, contour = raw["note"], raw["onset"], raw["contour"]
    require(note.ndim == 2 and onset.ndim == 2 and contour.ndim == 2, "raw arrays must be matrices")
    require(note.shape == onset.shape and note.shape[1] == 88, "unexpected Basic Pitch note/onset shape")
    require(contour.shape[0] == note.shape[0] and contour.shape[1] == 264, "unexpected Basic Pitch contour shape")
    require(np.isfinite(note).all() and np.isfinite(onset).all() and np.isfinite(contour).all(), "raw activations contain non-finite values")

def has_native_same_pitch(native_times, midi, time):
    arr = native_times.get(midi)
    if arr is None or not len(arr):
        return False
    j = int(np.searchsorted(arr, time))
    return ((j < len(arr) and abs(arr[j] - time) <= NATIVE_MATCH_TOLERANCE_SECONDS)
            or (j > 0 and abs(arr[j - 1] - time) <= NATIVE_MATCH_TOLERANCE_SECONDS))

def contour_summary(contour, times, time, midi, window):
    left = int(np.searchsorted(times, time + window[0], side="left"))
    right = int(np.searchsorted(times, time + window[1], side="right"))
    if right <= left:
        return None
    low_pitch = midi - 1.0
    high_pitch = midi + MAX_RISE_SEMITONES + 0.5
    low_bin = max(0, int(math.floor((low_pitch - MIDI_OFFSET) * CONTOUR_BINS_PER_SEMITONE)))
    high_bin = min(contour.shape[1], int(math.ceil((high_pitch - MIDI_OFFSET) * CONTOUR_BINS_PER_SEMITONE)) + 1)
    if high_bin <= low_bin:
        return None
    block = contour[left:right, low_bin:high_bin]
    maxima = np.argmax(block, axis=1)
    pitches = MIDI_OFFSET + (low_bin + maxima) / CONTOUR_BINS_PER_SEMITONE
    salience = block[np.arange(len(maxima)), maxima]
    return {
        "medianPitch": float(np.median(pitches)),
        "medianSalience": float(np.median(salience)),
        "maxSalience": float(np.max(salience)),
    }

def local_onset_peaks(column):
    if len(column) < 3:
        return np.array([], dtype=np.int64)
    return np.where((column[1:-1] >= ONSET_THRESHOLD) & (column[1:-1] >= column[:-2]) & (column[1:-1] > column[2:]))[0] + 1

def deduplicate(candidates):
    ranked = sorted(candidates, key=lambda c: (-c["onsetActivation"], c["time"], c["midi"]))
    kept = []
    for cand in ranked:
        if any(abs(cand["time"] - other["time"]) <= CANDIDATE_CLUSTER_SECONDS
               and abs(cand["midi"] - other["midi"]) <= CANDIDATE_CLUSTER_SEMITONES for other in kept):
            continue
        kept.append(cand)
    return sorted(kept, key=lambda c: (c["time"], c["midi"]))

def extract(raw, prediction):
    validate_raw(raw)
    onset = raw["onset"]
    contour = raw["contour"]
    times = model_frame_times(onset.shape[0])
    native_times = {midi: np.array(sorted(row["start"] for row in prediction["events"] if row["midi"] == midi), dtype=np.float64) for midi in range(128)}
    candidates = []
    for midi in range(MIN_MIDI, MAX_MIDI + 1):
        note_bin = midi - MIDI_OFFSET
        if not 0 <= note_bin < onset.shape[1]:
            continue
        column = onset[:, note_bin]
        for frame in local_onset_peaks(column):
            time = float(times[frame])
            if has_native_same_pitch(native_times, midi, time):
                continue
            early = contour_summary(contour, times, time, midi, EARLY_WINDOW_SECONDS)
            late = contour_summary(contour, times, time, midi, LATE_WINDOW_SECONDS)
            if early is None or late is None:
                continue
            rise = late["medianPitch"] - early["medianPitch"]
            if abs(early["medianPitch"] - midi) > EARLY_PITCH_TOLERANCE_SEMITONES:
                continue
            if not MIN_RISE_SEMITONES <= rise <= MAX_RISE_SEMITONES:
                continue
            if max(early["maxSalience"], late["maxSalience"]) < FRAME_SALIENCE_THRESHOLD:
                continue
            candidates.append({
                "frame": int(frame), "time": time, "midi": midi, "onsetActivation": float(column[frame]),
                "earlyPitch": early["medianPitch"], "earlyMedianSalience": early["medianSalience"], "earlyMaxSalience": early["maxSalience"],
                "latePitch": late["medianPitch"], "lateMedianSalience": late["medianSalience"], "lateMaxSalience": late["maxSalience"],
                "riseSemitones": rise, "technique": "attacked-upward-bend-candidate",
            })
    return deduplicate(candidates)

def build_report(raw_path, prediction_path, *, expected_raw_sha256=None, expected_prediction_sha256=None):
    if expected_raw_sha256 is not None:
        require(sha256(raw_path) == expected_raw_sha256, "raw activation SHA256 mismatch")
    if expected_prediction_sha256 is not None:
        require(sha256(prediction_path) == expected_prediction_sha256, "prediction SHA256 mismatch")
    z = np.load(raw_path)
    raw = {k: z[k] for k in z.files}
    prediction = load_prediction(prediction_path)
    candidates = extract(raw, prediction)
    return {
        "kind": "basic-pitch-raw-attacked-bend-candidates",
        "version": 1,
        "rawActivationSha256": sha256(raw_path),
        "predictionSha256": sha256(prediction_path),
        "candidateCount": len(candidates),
        "candidates": candidates,
        "policy": {
            "referenceLabelsRead": False,
            "onsetThreshold": ONSET_THRESHOLD,
            "frameSalienceThreshold": FRAME_SALIENCE_THRESHOLD,
            "earlyWindowSeconds": list(EARLY_WINDOW_SECONDS),
            "lateWindowSeconds": list(LATE_WINDOW_SECONDS),
            "earlyPitchToleranceSemitones": EARLY_PITCH_TOLERANCE_SEMITONES,
            "minRiseSemitones": MIN_RISE_SEMITONES,
            "maxRiseSemitones": MAX_RISE_SEMITONES,
            "nativeMatchToleranceSeconds": NATIVE_MATCH_TOLERANCE_SECONDS,
            "candidateClusterSeconds": CANDIDATE_CLUSTER_SECONDS,
            "candidateClusterSemitones": CANDIDATE_CLUSTER_SEMITONES,
        },
        "customerDeliveryEligible": False,
        "limitations": [
            "Candidates are technique evidence from a generic guitar oracle, not rhythm-versus-lead role assignments.",
            "The detector does not read reviewed labels or optimize thresholds against score matches.",
            "Candidate extraction alone does not authorize insertion into customer tablature.",
        ],
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw", required=True)
    p.add_argument("--prediction", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--raw-sha256")
    p.add_argument("--prediction-sha256")
    a = p.parse_args()
    output = Path(a.output)
    require(not output.exists(), "refusing to overwrite output")
    report = build_report(a.raw, a.prediction, expected_raw_sha256=a.raw_sha256, expected_prediction_sha256=a.prediction_sha256)
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"candidateCount": report["candidateCount"]}, sort_keys=True))

if __name__ == "__main__":
    main()
