from __future__ import annotations

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
DIAGNOSTIC_PATH = PUBLIC / "gomyway-chorus-35-step0-boundary-anchor-diagnostic-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-35-step0-audio-onset-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-35-step0-audio-onset-v1-manifest.json"

SAMPLE_RATE = 22050
FRAME_SIZE = 1024
HOP_SIZE = 256
SEARCH_PADDING_SECONDS = 0.25
MAX_ACCEPTED_ANCHOR_DISTANCE_SECONDS = 0.18


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def decode_window(start: float, end: float) -> np.ndarray:
    if not AUDIO_PATH.exists():
        raise FileNotFoundError(f"Missing audio: {AUDIO_PATH.relative_to(ROOT)}")
    duration = max(0.1, end - start)
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
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float64) / 32768.0
    return audio


def spectral_flux(audio: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if len(audio) < FRAME_SIZE * 2:
        return np.array([], dtype=float), np.array([], dtype=float)
    window = np.hanning(FRAME_SIZE)
    spectra: list[np.ndarray] = []
    frame_times: list[float] = []
    for offset in range(0, len(audio) - FRAME_SIZE + 1, HOP_SIZE):
        frame = audio[offset:offset + FRAME_SIZE] * window
        magnitude = np.abs(np.fft.rfft(frame))
        magnitude /= max(float(np.sum(magnitude)), 1e-12)
        spectra.append(magnitude)
        frame_times.append((offset + FRAME_SIZE / 2) / SAMPLE_RATE)
    flux = np.zeros(len(spectra), dtype=float)
    for index in range(1, len(spectra)):
        delta = spectra[index] - spectra[index - 1]
        flux[index] = float(np.sum(np.maximum(delta, 0.0)))
    return np.asarray(frame_times), flux


def local_peaks(values: np.ndarray) -> list[int]:
    if len(values) < 3:
        return []
    median = float(np.median(values))
    mad = float(np.median(np.abs(values - median)))
    threshold = median + max(3.0 * mad, 0.01)
    peaks: list[int] = []
    for index in range(1, len(values) - 1):
        if values[index] >= threshold and values[index] > values[index - 1] and values[index] >= values[index + 1]:
            peaks.append(index)
    return peaks


def main() -> None:
    diagnostic = load(DIAGNOSTIC_PATH)
    if diagnostic.get("passed") is not True:
        raise RuntimeError("Boundary-anchor diagnostic is not green.")
    if diagnostic.get("recommendedNextAction") != "compare-local-anchor-estimates":
        raise RuntimeError("Boundary diagnostic did not authorize audio-onset arbitration.")
    if int(diagnostic.get("passingLocalCandidateCount", 0)) != 2:
        raise RuntimeError("Expected two passing local boundary candidates.")

    candidates = [
        row for row in diagnostic.get("localCandidates", [])
        if isinstance(row, dict) and row.get("qualityGate") is True
    ]
    estimates = [float(row["estimatedStartSeconds"]) for row in candidates]
    search_start = max(0.0, min(estimates) - SEARCH_PADDING_SECONDS)
    search_end = max(estimates) + SEARCH_PADDING_SECONDS

    audio = decode_window(search_start, search_end)
    frame_times, flux = spectral_flux(audio)
    peak_indexes = local_peaks(flux)

    peak_rows: list[dict[str, Any]] = []
    for index in peak_indexes:
        absolute_time = search_start + float(frame_times[index])
        distances = {
            str(candidate["direction"]): abs(
                absolute_time - float(candidate["estimatedStartSeconds"])
            )
            for candidate in candidates
        }
        peak_rows.append({
            "timeSeconds": round(absolute_time, 6),
            "spectralFlux": round(float(flux[index]), 8),
            "distanceToLocalEstimatesSeconds": {
                key: round(value, 6) for key, value in distances.items()
            },
        })

    peak_rows.sort(key=lambda row: float(row["spectralFlux"]), reverse=True)
    strongest = peak_rows[0] if peak_rows else None

    candidate_scores: list[dict[str, Any]] = []
    for candidate in candidates:
        estimate = float(candidate["estimatedStartSeconds"])
        nearest = min(
            peak_rows,
            key=lambda peak: abs(float(peak["timeSeconds"]) - estimate),
            default=None,
        )
        distance = (
            abs(float(nearest["timeSeconds"]) - estimate)
            if nearest is not None else math.inf
        )
        candidate_scores.append({
            "direction": candidate["direction"],
            "estimatedStartSeconds": round(estimate, 6),
            "localIntervalCount": candidate.get("localIntervalCount"),
            "localMadSeconds": candidate.get("localMadSeconds"),
            "nearestOnsetTimeSeconds": nearest["timeSeconds"] if nearest else None,
            "nearestOnsetFlux": nearest["spectralFlux"] if nearest else None,
            "nearestOnsetDistanceSeconds": round(distance, 6) if math.isfinite(distance) else None,
            "audioOnsetGate": bool(
                nearest is not None
                and distance <= MAX_ACCEPTED_ANCHOR_DISTANCE_SECONDS
            ),
        })

    passing = [row for row in candidate_scores if row["audioOnsetGate"]]
    passing.sort(key=lambda row: (
        float(row["nearestOnsetDistanceSeconds"]),
        float(row["localMadSeconds"]),
        -int(row["localIntervalCount"]),
    ))
    selected = passing[0] if passing else None

    # The audio onset is evidence for timing only. It makes no bend or vibrato claim.
    quality_gate = bool(
        selected is not None
        and len(peak_rows) > 0
        and float(selected["nearestOnsetDistanceSeconds"])
        <= MAX_ACCEPTED_ANCHOR_DISTANCE_SECONDS
    )

    output = {
        "schemaVersion": 1,
        "analysisType": "read-only-chorus-boundary-audio-onset-arbitration",
        "passed": True,
        "targetMeasure": 35,
        "targetStep": 0,
        "searchWindowStartSeconds": round(search_start, 6),
        "searchWindowEndSeconds": round(search_end, 6),
        "detectedOnsetPeakCount": len(peak_rows),
        "strongestOnsetPeak": strongest,
        "onsetPeaks": peak_rows[:20],
        "candidateScores": candidate_scores,
        "selectedCandidate": selected,
        "resolvedStartSeconds": (
            selected["nearestOnsetTimeSeconds"] if selected else None
        ),
        "qualityGate": quality_gate,
        "readyForReadOnlyTimingCompletion": quality_gate,
        "audioTimingEvidenceClaimed": quality_gate,
        "audioTechniqueSupportClaimed": False,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }

    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "detectedOnsetPeakCount": len(peak_rows),
        "selectedCandidateDirection": selected["direction"] if selected else None,
        "qualityGate": quality_gate,
        "readyForReadOnlyTimingCompletion": quality_gate,
        "audioTechniqueSupportClaimed": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 35 STEP 0 AUDIO ONSET V1 COMPLETE")
    print("Passed: True")
    print("Search window start:", output["searchWindowStartSeconds"])
    print("Search window end:", output["searchWindowEndSeconds"])
    print("Detected onset peaks:", len(peak_rows))
    for row in candidate_scores:
        print(
            f"direction={row['direction']} "
            f"estimate={row['estimatedStartSeconds']} "
            f"nearestOnset={row['nearestOnsetTimeSeconds']} "
            f"distance={row['nearestOnsetDistanceSeconds']} "
            f"audioOnsetGate={row['audioOnsetGate']}"
        )
    print("Selected candidate:", selected["direction"] if selected else None)
    print("Resolved measure 35 step 0 start:", output["resolvedStartSeconds"])
    print("Quality gate:", quality_gate)
    print("Ready for read-only timing completion:", quality_gate)
    print("Audio technique support claimed: False")
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
