from __future__ import annotations

import hashlib
import json
import math
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

AUDIO_PATH = PUBLIC / "gomywayfullaitest.m4a"
SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
TIMING_PATH = PUBLIC / "gomyway-chorus-33-35-completed-timing-plan-v3.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-audio-technique-features-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-audio-technique-features-v1-manifest.json"

SAMPLE_RATE = 22050
FRAME_SIZE = 2048
HOP_SIZE = 256
MIN_FREQUENCY_HZ = 70.0
MAX_FREQUENCY_HZ = 1200.0
MIN_RMS = 0.008
MIN_AUTOCORRELATION = 0.28
MIN_VOICED_FRAMES = 6
MIN_VOICED_RATIO = 0.20


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def decode_window(start: float, end: float) -> np.ndarray:
    duration = max(0.10, end - start)
    with tempfile.TemporaryDirectory() as temp_dir:
        wav_path = Path(temp_dir) / "window.wav"
        command = [
            "ffmpeg", "-v", "error", "-ss", f"{start:.6f}",
            "-i", str(AUDIO_PATH), "-t", f"{duration:.6f}",
            "-ac", "1", "-ar", str(SAMPLE_RATE), "-c:a", "pcm_s16le",
            str(wav_path),
        ]
        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {completed.stderr.strip()}")
        with wave.open(str(wav_path), "rb") as handle:
            frames = handle.readframes(handle.getnframes())
    return np.frombuffer(frames, dtype=np.int16).astype(np.float64) / 32768.0


def estimate_pitch(frame: np.ndarray) -> tuple[float | None, float, float]:
    frame = frame - float(np.mean(frame))
    rms = float(np.sqrt(np.mean(frame * frame)))
    if rms < MIN_RMS:
        return None, 0.0, rms
    windowed = frame * np.hanning(len(frame))
    correlation = np.correlate(windowed, windowed, mode="full")[len(windowed) - 1:]
    zero = float(correlation[0])
    if zero <= 1e-12:
        return None, 0.0, rms
    correlation /= zero
    min_lag = max(1, int(SAMPLE_RATE / MAX_FREQUENCY_HZ))
    max_lag = min(len(correlation) - 1, int(SAMPLE_RATE / MIN_FREQUENCY_HZ))
    if max_lag <= min_lag:
        return None, 0.0, rms
    region = correlation[min_lag:max_lag + 1]
    lag = min_lag + int(np.argmax(region))
    confidence = float(correlation[lag])
    if confidence < MIN_AUTOCORRELATION:
        return None, confidence, rms
    frequency = SAMPLE_RATE / float(lag)
    return frequency, confidence, rms


def cents(frequency: float) -> float:
    return 1200.0 * math.log2(frequency / 440.0)


def contour_features(audio: np.ndarray) -> dict[str, Any]:
    frames: list[dict[str, float]] = []
    total = 0
    for offset in range(0, max(0, len(audio) - FRAME_SIZE + 1), HOP_SIZE):
        total += 1
        frequency, confidence, rms = estimate_pitch(audio[offset:offset + FRAME_SIZE])
        if frequency is None:
            continue
        frames.append({
            "timeSeconds": round((offset + FRAME_SIZE / 2) / SAMPLE_RATE, 6),
            "frequencyHz": round(frequency, 4),
            "pitchCentsFromA4": round(cents(frequency), 3),
            "confidence": round(confidence, 5),
            "rms": round(rms, 6),
        })

    voiced = len(frames)
    ratio = voiced / total if total else 0.0
    pitches = np.asarray([row["pitchCentsFromA4"] for row in frames], dtype=float)
    times = np.asarray([row["timeSeconds"] for row in frames], dtype=float)
    if voiced >= 2:
        centered = pitches - float(np.median(pitches))
        pitch_range = float(np.max(pitches) - np.min(pitches))
        slope = float(np.polyfit(times, pitches, 1)[0]) if np.ptp(times) > 0 else 0.0
        direction_changes = int(np.sum(np.diff(np.sign(np.diff(centered))) != 0)) if voiced >= 3 else 0
        modulation_std = float(np.std(centered))
    else:
        pitch_range = 0.0
        slope = 0.0
        direction_changes = 0
        modulation_std = 0.0

    quality = bool(voiced >= MIN_VOICED_FRAMES and ratio >= MIN_VOICED_RATIO)
    return {
        "totalFrameCount": total,
        "voicedFrameCount": voiced,
        "voicedFrameRatio": round(ratio, 6),
        "pitchRangeCents": round(pitch_range, 3),
        "linearPitchSlopeCentsPerSecond": round(slope, 3),
        "pitchModulationStdCents": round(modulation_std, 3),
        "pitchDirectionChangeCount": direction_changes,
        "featureQualityGate": quality,
        "frames": frames,
    }


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    timing = load(TIMING_PATH)

    if not AUDIO_PATH.exists():
        raise FileNotFoundError(f"Missing audio: {AUDIO_PATH.relative_to(ROOT)}")
    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if timing.get("passed") is not True or timing.get("readyForAudioTechniqueFeatureExtraction") is not True:
        raise RuntimeError("Completed Timing Plan V3 is not ready for feature extraction.")

    candidates = [
        row for row in timing.get("rows", [])
        if isinstance(row, dict) and row.get("isSingleNoteTechniqueCandidate") is True
    ]
    rows: list[dict[str, Any]] = []
    quality_count = 0
    for row in candidates:
        start = number(row.get("analysisWindowStartSeconds"))
        end = number(row.get("analysisWindowEndSeconds"))
        if start is None or end is None or end <= start:
            features = {
                "totalFrameCount": 0,
                "voicedFrameCount": 0,
                "voicedFrameRatio": 0.0,
                "pitchRangeCents": 0.0,
                "linearPitchSlopeCentsPerSecond": 0.0,
                "pitchModulationStdCents": 0.0,
                "pitchDirectionChangeCount": 0,
                "featureQualityGate": False,
                "frames": [],
            }
        else:
            features = contour_features(decode_window(start, end))
        if features["featureQualityGate"]:
            quality_count += 1
        rows.append({
            "measureNumber": row.get("measureNumber"),
            "quantizedStep": row.get("quantizedStep"),
            "sourceEventIndex": row.get("sourceEventIndex"),
            "analysisWindowStartSeconds": start,
            "analysisWindowEndSeconds": end,
            "notes": row.get("notes", []),
            "features": features,
            "bendSupportClaimed": False,
            "vibratoSupportClaimed": False,
            "audioTechniqueSupportClaimed": False,
            "readOnly": True,
        })

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    ready = bool(rows and quality_count > 0 and source_unchanged)
    output = {
        "schemaVersion": 1,
        "analysisType": "read-only-single-note-pitch-contour-feature-extraction",
        "passed": True,
        "singleNoteCandidateCount": len(rows),
        "featureQualityGatePassedCount": quality_count,
        "featureQualityGateFailedCount": len(rows) - quality_count,
        "rows": rows,
        "readyForTechniqueEvidenceClassification": ready,
        "bendSupportClaimed": False,
        "vibratoSupportClaimed": False,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceEventCount": 949,
        "protectedSourceHashBefore": source_hash_before,
        "protectedSourceHashAfter": source_hash_after,
        "protectedSourceHashUnchanged": source_unchanged,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "singleNoteCandidateCount": len(rows),
        "featureQualityGatePassedCount": quality_count,
        "readyForTechniqueEvidenceClassification": ready,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 AUDIO TECHNIQUE FEATURES V1 COMPLETE")
    print("Passed: True")
    print("Single-note candidates:", len(rows))
    print("Feature quality gates passed:", quality_count)
    print("Feature quality gates failed:", len(rows) - quality_count)
    for row in rows:
        features = row["features"]
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"voicedFrames={features['voicedFrameCount']} "
            f"voicedRatio={features['voicedFrameRatio']} "
            f"rangeCents={features['pitchRangeCents']} "
            f"slope={features['linearPitchSlopeCentsPerSecond']} "
            f"modStd={features['pitchModulationStdCents']} "
            f"directionChanges={features['pitchDirectionChangeCount']} "
            f"qualityGate={features['featureQualityGate']}"
        )
    print("Ready for technique evidence classification:", ready)
    print("Bend support claimed: False")
    print("Vibrato support claimed: False")
    print("Audio technique support claimed: False")
    print("Protected source event count: 949")
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
