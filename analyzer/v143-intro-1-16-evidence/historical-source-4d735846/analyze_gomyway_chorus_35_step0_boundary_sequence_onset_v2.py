from __future__ import annotations

import json
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

AUDIO_PATH = PUBLIC / "gomywayfullaitest.m4a"
CONFLICT_PATH = PUBLIC / "gomyway-chorus-33-35-remaining-v2-timing-conflict-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-35-step0-boundary-sequence-onset-v2.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-35-step0-boundary-sequence-onset-v2-manifest.json"

SAMPLE_RATE = 22050
FRAME_SIZE = 1024
HOP_SIZE = 256
SEARCH_PADDING_SECONDS = 0.08
MIN_NEIGHBOR_CLEARANCE_SECONDS = 0.035


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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
        return np.frombuffer(frames, dtype=np.int16).astype(np.float64) / 32768.0


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
    threshold = median + max(2.5 * mad, 0.008)
    return [
        index
        for index in range(1, len(values) - 1)
        if values[index] >= threshold
        and values[index] > values[index - 1]
        and values[index] >= values[index + 1]
    ]


def main() -> None:
    diagnostic = load(CONFLICT_PATH)
    if diagnostic.get("passed") is not True:
        raise RuntimeError("Remaining V2 timing conflict diagnostic is not green.")
    if diagnostic.get("recommendedNextAction") != (
        "arbitrate-single-cross-measure-boundary-with-local-audio-onsets"
    ):
        raise RuntimeError("Conflict diagnostic did not authorize boundary onset arbitration.")

    conflicts = [row for row in diagnostic.get("conflicts", []) if isinstance(row, dict)]
    if len(conflicts) != 1:
        raise RuntimeError(f"Expected one remaining conflict, found {len(conflicts)}.")
    conflict = conflicts[0]

    left = conflict.get("left", {})
    right = conflict.get("right", {})
    following = conflict.get("followingNeighbor", {})
    left_time = number(left.get("resolvedStartSeconds"))
    old_target_time = number(right.get("resolvedStartSeconds"))
    following_time = number(following.get("resolvedStartSeconds"))
    if left_time is None or old_target_time is None or following_time is None:
        raise RuntimeError("Boundary conflict is missing required timestamps.")
    if int(left.get("measureNumber", -1)) != 34 or int(left.get("quantizedStep", -1)) != 15:
        raise RuntimeError("Expected left boundary event m34s15.")
    if int(right.get("measureNumber", -1)) != 35 or int(right.get("quantizedStep", -1)) != 0:
        raise RuntimeError("Expected target boundary event m35s0.")
    if int(following.get("measureNumber", -1)) != 35 or int(following.get("quantizedStep", -1)) != 1:
        raise RuntimeError("Expected following boundary event m35s1.")

    search_start = max(0.0, left_time - SEARCH_PADDING_SECONDS)
    search_end = following_time + SEARCH_PADDING_SECONDS
    audio = decode_window(search_start, search_end)
    frame_times, flux = spectral_flux(audio)
    peak_indexes = local_peaks(flux)

    peaks: list[dict[str, Any]] = []
    for index in peak_indexes:
        onset = search_start + float(frame_times[index])
        inside_ordered_gap = (
            onset > left_time + MIN_NEIGHBOR_CLEARANCE_SECONDS
            and onset < following_time - MIN_NEIGHBOR_CLEARANCE_SECONDS
        )
        peaks.append({
            "timeSeconds": round(onset, 6),
            "spectralFlux": round(float(flux[index]), 8),
            "afterLeftSeconds": round(onset - left_time, 6),
            "beforeFollowingSeconds": round(following_time - onset, 6),
            "insideOrderedBoundaryGap": inside_ordered_gap,
        })

    eligible = [row for row in peaks if row["insideOrderedBoundaryGap"]]
    # Select the strongest independent onset that preserves m34s15 < m35s0 < m35s1.
    eligible.sort(key=lambda row: (-float(row["spectralFlux"]), float(row["timeSeconds"])))
    selected = eligible[0] if eligible else None
    resolved = number(selected.get("timeSeconds")) if selected else None
    quality_gate = bool(
        resolved is not None
        and left_time < resolved < following_time
        and resolved - left_time >= MIN_NEIGHBOR_CLEARANCE_SECONDS
        and following_time - resolved >= MIN_NEIGHBOR_CLEARANCE_SECONDS
    )

    output = {
        "schemaVersion": 2,
        "analysisType": "read-only-ordered-cross-measure-boundary-onset-sequence",
        "passed": True,
        "targetMeasure": 35,
        "targetStep": 0,
        "leftBoundaryTimeSeconds": round(left_time, 6),
        "oldResolvedStartSeconds": round(old_target_time, 6),
        "followingBoundaryTimeSeconds": round(following_time, 6),
        "searchWindowStartSeconds": round(search_start, 6),
        "searchWindowEndSeconds": round(search_end, 6),
        "detectedOnsetPeakCount": len(peaks),
        "eligibleOrderedOnsetCount": len(eligible),
        "onsetPeaks": sorted(peaks, key=lambda row: float(row["timeSeconds"])),
        "selectedOnset": selected,
        "resolvedStartSeconds": round(resolved, 6) if resolved is not None else None,
        "qualityGate": quality_gate,
        "readyForCompletedTimingPlanV3": quality_gate,
        "audioTimingEvidenceClaimed": quality_gate,
        "audioTechniqueSupportClaimed": False,
        "timingRepairAppliedToProtectedSource": False,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }

    manifest = {
        "schemaVersion": 2,
        "passed": True,
        "detectedOnsetPeakCount": len(peaks),
        "eligibleOrderedOnsetCount": len(eligible),
        "resolvedStartSeconds": output["resolvedStartSeconds"],
        "qualityGate": quality_gate,
        "readyForCompletedTimingPlanV3": quality_gate,
        "audioTechniqueSupportClaimed": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 35 STEP 0 BOUNDARY SEQUENCE ONSET V2 COMPLETE")
    print("Passed: True")
    print("Left boundary m34s15:", round(left_time, 6))
    print("Old m35s0 timing:", round(old_target_time, 6))
    print("Following boundary m35s1:", round(following_time, 6))
    print("Detected onset peaks:", len(peaks))
    print("Eligible ordered onsets:", len(eligible))
    for row in sorted(peaks, key=lambda item: float(item["timeSeconds"])):
        print(
            f"onset={row['timeSeconds']} flux={row['spectralFlux']} "
            f"afterLeft={row['afterLeftSeconds']} "
            f"beforeFollowing={row['beforeFollowingSeconds']} "
            f"eligible={row['insideOrderedBoundaryGap']}"
        )
    print("Resolved measure 35 step 0 start:", output["resolvedStartSeconds"])
    print("Quality gate:", quality_gate)
    print("Ready for completed timing plan V3:", quality_gate)
    print("Timing repair applied to protected source: False")
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
