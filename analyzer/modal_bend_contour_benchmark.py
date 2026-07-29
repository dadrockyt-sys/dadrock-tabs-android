"""Measure continuous guitar bend contours without changing the green V71 analyzer."""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v71 as analyzer

app = modal.App("dadrock-bend-contour-benchmark")

# V71's image already contains Basic Pitch and its librosa/soundfile dependencies.
# Do not append a pip build step after V71's local Python sources: Modal rejects
# image build steps that occur after add_local_python_source().
image = analyzer.image.add_local_python_source("modal_analyzer_v71")


def rolling_median(values: list[float | None], radius: int = 2) -> list[float | None]:
    cleaned: list[float | None] = []
    for index, value in enumerate(values):
        if value is None:
            cleaned.append(None)
            continue
        neighbourhood = [
            candidate
            for candidate in values[max(0, index - radius): index + radius + 1]
            if candidate is not None
        ]
        if not neighbourhood:
            cleaned.append(None)
            continue
        neighbourhood.sort()
        cleaned.append(neighbourhood[len(neighbourhood) // 2])
    return cleaned


def nearest_index(values: list[float], target: float) -> int:
    return min(range(len(values)), key=lambda index: abs(values[index] - target))


def analyse_bend_window(
    times: list[float],
    midi_curve: list[float | None],
    confidence_curve: list[float],
    duration: float,
    expected: dict[str, Any],
) -> dict[str, Any]:
    start = float(expected["startProgress"]) * duration
    end = float(expected["endProgress"]) * duration
    source = float(expected["sourceMidi"])
    target = float(expected["targetMidi"])
    release = float(expected["releaseToMidi"])

    selected = [
        (time, midi, confidence)
        for time, midi, confidence in zip(times, midi_curve, confidence_curve)
        if start <= time < end and midi is not None and confidence >= 0.45
    ]

    if not selected:
        return {
            "bendId": expected["bendId"],
            "measure": expected["measure"],
            "start": round(start, 4),
            "end": round(end, 4),
            "voicedFrameCount": 0,
            "sourceDetected": False,
            "targetReached": False,
            "descentDetected": False,
            "releaseDetected": False,
            "continuousBendEvidence": False,
            "reason": "no-confident-pitch-frames",
            "contour": [],
        }

    frame_times = [item[0] for item in selected]
    pitches = [float(item[1]) for item in selected]
    confidences = [float(item[2]) for item in selected]

    source_candidates = [
        index for index, pitch in enumerate(pitches) if abs(pitch - source) <= 0.8
    ]
    source_index = source_candidates[0] if source_candidates else nearest_index(pitches, source)

    peak_index = max(range(source_index, len(pitches)), key=lambda index: pitches[index])
    peak_pitch = pitches[peak_index]

    after_peak = pitches[peak_index + 1:]
    descent_pitch = min(after_peak) if after_peak else peak_pitch
    release_candidates = [
        index
        for index in range(peak_index + 1, len(pitches))
        if pitches[index] <= source + 0.7
    ]
    release_index = release_candidates[0] if release_candidates else None

    source_detected = abs(pitches[source_index] - source) <= 1.0
    target_reached = peak_pitch >= target - 0.55
    rise_amount = peak_pitch - pitches[source_index]
    descent_amount = peak_pitch - descent_pitch
    descent_detected = descent_amount >= 1.0
    release_detected = release_index is not None and (
        abs(pitches[release_index] - source) <= 1.0
        or pitches[release_index] <= release + 1.0
    )

    # Require a multi-frame ascent rather than a single percussion-driven spike.
    ascent_frames = 0
    for index in range(source_index + 1, peak_index + 1):
        if pitches[index] >= pitches[index - 1] - 0.2:
            ascent_frames += 1
    sustained_peak_frames = sum(
        1
        for pitch in pitches[max(source_index, peak_index - 3): peak_index + 4]
        if pitch >= target - 0.8
    )

    continuous = (
        source_detected
        and target_reached
        and rise_amount >= 1.35
        and ascent_frames >= 2
        and sustained_peak_frames >= 2
        and descent_detected
        and release_detected
    )

    contour = [
        {
            "time": round(time, 4),
            "midi": round(pitch, 3),
            "confidence": round(confidence, 3),
        }
        for time, pitch, confidence in selected[:: max(1, len(selected) // 24)]
    ]

    return {
        "bendId": expected["bendId"],
        "measure": expected["measure"],
        "start": round(start, 4),
        "end": round(end, 4),
        "voicedFrameCount": len(selected),
        "sourcePitch": round(pitches[source_index], 3),
        "peakPitch": round(peak_pitch, 3),
        "lowestAfterPeak": round(descent_pitch, 3),
        "riseSemitones": round(rise_amount, 3),
        "descentSemitones": round(descent_amount, 3),
        "sourceDetected": source_detected,
        "targetReached": target_reached,
        "ascentFrames": ascent_frames,
        "sustainedPeakFrames": sustained_peak_frames,
        "descentDetected": descent_detected,
        "releaseDetected": release_detected,
        "continuousBendEvidence": continuous,
        "contour": contour,
    }


@app.function(image=image, timeout=900, memory=4096)
def analyse_contours(audio_bytes: bytes, filename: str, fixture: dict[str, Any]) -> dict[str, Any]:
    import librosa
    import numpy as np

    suffix = Path(filename).suffix.lower() or ".audio"
    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / f"source{suffix}"
        normalized = Path(temp_dir) / "normalized.wav"
        source.write_bytes(audio_bytes)

        analyzer.engine.normalize_audio_file(str(source), str(normalized))
        audio, sample_rate = librosa.load(str(normalized), sr=22050, mono=True)
        duration = float(librosa.get_duration(y=audio, sr=sample_rate))

        harmonic, _ = librosa.effects.hpss(audio, margin=(1.0, 4.0))
        f0, voiced_flag, voiced_probability = librosa.pyin(
            harmonic,
            fmin=librosa.note_to_hz("E2"),
            fmax=librosa.note_to_hz("E5"),
            sr=sample_rate,
            frame_length=2048,
            hop_length=128,
            fill_na=np.nan,
        )
        times_array = librosa.times_like(f0, sr=sample_rate, hop_length=128)

        midi_values: list[float | None] = []
        for frequency in f0:
            if frequency is None or not math.isfinite(float(frequency)) or frequency <= 0:
                midi_values.append(None)
            else:
                midi_values.append(float(librosa.hz_to_midi(float(frequency))))
        midi_values = rolling_median(midi_values, radius=2)

        probabilities = [
            float(value) if math.isfinite(float(value)) else 0.0
            for value in voiced_probability
        ]
        times = [float(value) for value in times_array]

        bends = [
            analyse_bend_window(times, midi_values, probabilities, duration, expected)
            for expected in fixture.get("expectedBends", [])
        ]
        passed = sum(1 for bend in bends if bend["continuousBendEvidence"])

        return {
            "benchmarkVersion": 2,
            "benchmarkType": "continuous-pitch-contour",
            "protectedAnalyzer": "7.1-phase-1-canonical-timeline-voicing-handoff",
            "fixtureName": fixture.get("name"),
            "durationSeconds": round(duration, 4),
            "sampleRate": sample_rate,
            "expectedBendCount": len(bends),
            "continuousBendCount": passed,
            "bendContourAccuracy": round(passed / len(bends), 4) if bends else 0.0,
            "bends": bends,
            "method": (
                "HPSS drum reduction followed by frame-level pYIN pitch tracking; "
                "requires source, sustained full-step peak, descent, and release"
            ),
        }


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway_bend_reference.json",
    report_output: str = "/tmp/gomyway-contour-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    report = analyse_contours.remote(audio_file.read_bytes(), audio_file.name, fixture)
    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )

    print("JIMMY PAIGE CONTINUOUS BEND-CONTOUR BENCHMARK")
    print("=" * 55)
    print("Protected analyzer:", report.get("protectedAnalyzer"))
    print("Duration:", report.get("durationSeconds"))
    print(
        "Continuous bends:",
        f"{report.get('continuousBendCount')}/{report.get('expectedBendCount')}",
    )
    for bend in report.get("bends", []):
        status = "PASS" if bend["continuousBendEvidence"] else "FAIL"
        print(
            status,
            bend["bendId"],
            "source=", bend.get("sourcePitch"),
            "peak=", bend.get("peakPitch"),
            "rise=", bend.get("riseSemitones"),
            "descent=", bend.get("descentSemitones"),
            "release=", bend.get("releaseDetected"),
        )
    print("\nSaved report:", report_output)
    print("V71 remains unchanged and protected by the Stairway guard.")
