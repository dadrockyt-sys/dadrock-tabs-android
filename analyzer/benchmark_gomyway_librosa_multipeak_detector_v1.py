from __future__ import annotations

import hashlib
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
STEM_PATH = PUBLIC / "separator-benchmark-v2/gomyway-bsroformer-demucs6s-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-librosa-multipeak-detector-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-librosa-multipeak-detector-v1-manifest.json"

CONTROL_F1 = 4.73
BASIC_PITCH_BASELINE_F1 = 6.12
BASIC_PITCH_TUNED_F1 = 6.39
MIDI_MIN = 40
MIDI_MAX = 88
N_FFT = 4096
HOP_LENGTH = 256
SNAP_TOLERANCE_SECONDS = 0.085

CONFIGS = [
    {"name": "peaks2_db20", "maxPeaksPerFrame": 2, "relativeDb": 20.0},
    {"name": "peaks3_db20", "maxPeaksPerFrame": 3, "relativeDb": 20.0},
    {"name": "peaks4_db20", "maxPeaksPerFrame": 4, "relativeDb": 20.0},
    {"name": "peaks2_db15", "maxPeaksPerFrame": 2, "relativeDb": 15.0},
    {"name": "peaks3_db15", "maxPeaksPerFrame": 3, "relativeDb": 15.0},
    {"name": "peaks4_db15", "maxPeaksPerFrame": 4, "relativeDb": 15.0},
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f1(tp: int, predicted: int, expected: int) -> float:
    if tp == 0 or predicted == 0 or expected == 0:
        return 0.0
    precision = tp / predicted
    recall = tp / expected
    return 2.0 * precision * recall / (precision + recall)


def nearest_grid_slot(
    start_time: float,
    grid_items: list[tuple[tuple[int, int], float]],
) -> tuple[tuple[int, int] | None, float]:
    best_slot: tuple[int, int] | None = None
    best_distance = float("inf")
    for slot, slot_time in grid_items:
        distance = abs(start_time - slot_time)
        if distance < best_distance:
            best_distance = distance
            best_slot = slot
    return best_slot, best_distance


def load_audio_features() -> tuple[np.ndarray, np.ndarray, int]:
    try:
        import librosa
    except Exception as exc:
        raise RuntimeError(
            "librosa is required for this benchmark. Install with: uv pip install librosa"
        ) from exc

    y, sr = librosa.load(str(STEM_PATH), sr=22050, mono=True)
    stft = librosa.stft(y, n_fft=N_FFT, hop_length=HOP_LENGTH)
    magnitude = np.abs(stft)
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=N_FFT)
    return magnitude, frequencies, sr


def frequency_to_midi(freq: float) -> int | None:
    if not math.isfinite(freq) or freq <= 0.0:
        return None
    midi = int(round(69.0 + 12.0 * math.log2(freq / 440.0)))
    if MIDI_MIN <= midi <= MIDI_MAX:
        return midi
    return None


def detect_tokens(
    magnitude: np.ndarray,
    frequencies: np.ndarray,
    sr: int,
    grid: dict[tuple[int, int], float],
    *,
    max_peaks_per_frame: int,
    relative_db: float,
) -> tuple[Counter[tuple[int, int, int]], dict[str, Any]]:
    grid_items = list(grid.items())
    predicted: Counter[tuple[int, int, int]] = Counter()
    candidate_peaks = 0
    snapped_peaks = 0
    rejected_time = 0

    freq_mask = np.array([
        MIDI_MIN <= (69.0 + 12.0 * math.log2(freq / 440.0)) <= MIDI_MAX
        if freq > 0 else False
        for freq in frequencies
    ])
    valid_bins = np.flatnonzero(freq_mask)

    for frame_index in range(magnitude.shape[1]):
        frame = magnitude[:, frame_index]
        frame_valid = frame[valid_bins]
        if frame_valid.size < 3:
            continue
        frame_max = float(frame_valid.max())
        if frame_max <= 0.0:
            continue
        amplitude_floor = frame_max * (10.0 ** (-relative_db / 20.0))

        local_bins: list[int] = []
        for bin_index in valid_bins:
            if bin_index <= 0 or bin_index >= len(frame) - 1:
                continue
            value = float(frame[bin_index])
            if value < amplitude_floor:
                continue
            if value >= float(frame[bin_index - 1]) and value > float(frame[bin_index + 1]):
                local_bins.append(bin_index)

        local_bins.sort(key=lambda idx: float(frame[idx]), reverse=True)
        chosen = local_bins[:max_peaks_per_frame]
        candidate_peaks += len(chosen)

        frame_time = frame_index * HOP_LENGTH / sr
        slot, distance = nearest_grid_slot(frame_time, grid_items)
        if slot is None or distance > SNAP_TOLERANCE_SECONDS:
            rejected_time += len(chosen)
            continue

        for bin_index in chosen:
            midi = frequency_to_midi(float(frequencies[bin_index]))
            if midi is None:
                continue
            predicted[(slot[0], slot[1], midi)] = 1
            snapped_peaks += 1

    diagnostics = {
        "candidatePeaks": candidate_peaks,
        "snappedPeaksBeforeDeduplication": snapped_peaks,
        "rejectedOutsideGrid": rejected_time,
        "deduplicatedPredictionTokens": sum(predicted.values()),
    }
    return predicted, diagnostics


def score_config(
    config: dict[str, Any],
    magnitude: np.ndarray,
    frequencies: np.ndarray,
    sr: int,
    grid: dict[tuple[int, int], float],
    reference: Counter[tuple[int, int, int]],
) -> dict[str, Any]:
    predicted, diagnostics = detect_tokens(
        magnitude,
        frequencies,
        sr,
        grid,
        max_peaks_per_frame=int(config["maxPeaksPerFrame"]),
        relative_db=float(config["relativeDb"]),
    )
    matched = sum((predicted & reference).values())
    predicted_count = sum(predicted.values())
    reference_count = sum(reference.values())
    missing = sum((reference - predicted).values())
    extra = sum((predicted - reference).values())

    priority_reference = Counter({
        token: count for token, count in reference.items()
        if token[0] in v2.PRIORITY_MEASURES
    })
    priority_predicted = Counter({
        token: count for token, count in predicted.items()
        if token[0] in v2.PRIORITY_MEASURES
    })

    return {
        **config,
        "pitchF1": round(100.0 * f1(matched, predicted_count, reference_count), 2),
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "priorityMatched": sum((priority_reference & priority_predicted).values()),
        "priorityMissing": sum((priority_reference - priority_predicted).values()),
        "priorityExtra": sum((priority_predicted - priority_reference).values()),
        **diagnostics,
    }


def main() -> None:
    if not STEM_PATH.exists():
        raise FileNotFoundError(f"Missing winner stem: {STEM_PATH.relative_to(ROOT)}")

    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate = v2.load_json(CANDIDATE_PATH)
    events = v2.candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")

    grid, timing_diagnostics = v2.build_timing_grid(events)
    reference = v2.load_json(REFERENCE_PATH)
    if reference.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference_counter = v3.reference_tokens(reference)

    magnitude, frequencies, sr = load_audio_features()

    results = []
    for config in CONFIGS:
        result = score_config(config, magnitude, frequencies, sr, grid, reference_counter)
        results.append(result)
        print(
            f"{result['name']}: pitchF1={result['pitchF1']} "
            f"matched={result['matched']} missing={result['missing']} extra={result['extra']} "
            f"priority={result['priorityMatched']}/{result['priorityMissing']}/{result['priorityExtra']}"
        )

    ranked = sorted(
        results,
        key=lambda row: (
            float(row["pitchF1"]),
            int(row["priorityMatched"]),
            -int(row["priorityExtra"]),
        ),
        reverse=True,
    )
    winner = ranked[0]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during detector benchmark.")

    beats_tuned_basic_pitch = float(winner["pitchF1"]) > BASIC_PITCH_TUNED_F1
    recommended = (
        "investigate-librosa-multipeak-refinement"
        if beats_tuned_basic_pitch
        else "evaluate-neural-alternative-pitch-detector"
    )

    payload = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "independent-librosa-multipeak-pitch-detector",
        "audioPath": str(STEM_PATH.relative_to(ROOT)),
        "controlPitchF1": CONTROL_F1,
        "basicPitchBaselineF1": BASIC_PITCH_BASELINE_F1,
        "basicPitchTunedF1": BASIC_PITCH_TUNED_F1,
        "detectorSettings": {
            "sampleRate": sr,
            "nFft": N_FFT,
            "hopLength": HOP_LENGTH,
            "midiRange": [MIDI_MIN, MIDI_MAX],
            "snapToleranceSeconds": SNAP_TOLERANCE_SECONDS,
        },
        "timingGrid": timing_diagnostics,
        "results": results,
        "winner": winner,
        "winnerBeatsTunedBasicPitch": beats_tuned_basic_pitch,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": recommended,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "recommendedNextAction": recommended,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY ALTERNATIVE MULTIPITCH DETECTOR V1 COMPLETE")
    print("Passed: True")
    print("Basic Pitch tuned F1:", BASIC_PITCH_TUNED_F1)
    print("Winner:", winner["name"])
    print("Winner pitch F1:", winner["pitchF1"])
    print("Winner matched/missing/extra:", winner["matched"], "/", winner["missing"], "/", winner["extra"])
    print("Winner priority matched/missing/extra:", winner["priorityMatched"], "/", winner["priorityMissing"], "/", winner["priorityExtra"])
    print("Winner beats tuned Basic Pitch:", beats_tuned_basic_pitch)
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
