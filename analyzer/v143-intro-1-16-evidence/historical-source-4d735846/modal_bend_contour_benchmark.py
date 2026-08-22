"""Measure repeated guitar bend contours without changing the green V71 analyzer."""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v71 as analyzer

app = modal.App("dadrock-bend-contour-benchmark")
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


def analyse_measure_bend(
    times: list[float],
    midi_curve: list[float | None],
    confidence_curve: list[float],
    duration: float,
    expected: dict[str, Any],
    measure_count: int,
) -> dict[str, Any]:
    measure = int(expected["measure"])
    measure_start = (measure - 1) * duration / measure_count
    measure_end = measure * duration / measure_count
    search_end = measure_start + (measure_end - measure_start) * 0.72

    source = float(expected["sourceMidi"])
    target = float(expected["targetMidi"])
    release = float(expected["releaseToMidi"])

    frame_indices = [
        index
        for index, (time, midi, confidence) in enumerate(
            zip(times, midi_curve, confidence_curve)
        )
        if measure_start <= time < search_end
        and midi is not None
        and confidence >= 0.12
        and 53.5 <= float(midi) <= 61.5
    ]

    if not frame_indices:
        return {
            "bendId": expected["bendId"],
            "measure": measure,
            "measureStart": round(measure_start, 4),
            "measureEnd": round(measure_end, 4),
            "voicedFrameCount": 0,
            "sourceDetected": False,
            "targetReached": False,
            "descentDetected": False,
            "releaseDetected": False,
            "continuousBendEvidence": False,
            "reason": "no-guitar-band-frames",
            "contour": [],
        }

    source_candidates = [
        index
        for index in frame_indices
        if abs(float(midi_curve[index]) - source) <= 1.15
    ]

    if not source_candidates:
        source_candidates = sorted(
            frame_indices,
            key=lambda index: abs(float(midi_curve[index]) - source),
        )[:8]

    best: dict[str, Any] | None = None
    max_lookahead = 0.95

    for source_index in source_candidates:
        lookahead = [
            index
            for index in frame_indices
            if source_index <= index
            and times[index] <= times[source_index] + max_lookahead
        ]
        if len(lookahead) < 4:
            continue

        peak_index = max(lookahead, key=lambda index: float(midi_curve[index]))
        if peak_index <= source_index:
            continue

        after_peak = [
            index
            for index in frame_indices
            if peak_index < index
            and times[index] <= min(measure_end, times[peak_index] + 0.85)
        ]

        source_pitch = float(midi_curve[source_index])
        peak_pitch = float(midi_curve[peak_index])
        lowest_after = (
            min(float(midi_curve[index]) for index in after_peak)
            if after_peak
            else peak_pitch
        )
        rise = peak_pitch - source_pitch
        descent = peak_pitch - lowest_after

        ascent_indices = [
            index for index in lookahead if source_index <= index <= peak_index
        ]
        ascent_frames = sum(
            1
            for left, right in zip(ascent_indices, ascent_indices[1:])
            if float(midi_curve[right]) >= float(midi_curve[left]) - 0.28
        )
        sustained_peak_frames = sum(
            1
            for index in lookahead
            if abs(times[index] - times[peak_index]) <= 0.12
            and float(midi_curve[index]) >= target - 0.85
        )

        release_indices = [
            index
            for index in after_peak
            if float(midi_curve[index]) <= source + 0.85
        ]
        open_g_indices = [
            index
            for index in after_peak
            if abs(float(midi_curve[index]) - release) <= 1.0
        ]

        source_detected = abs(source_pitch - source) <= 1.15
        target_reached = peak_pitch >= target - 0.7
        descent_detected = descent >= 1.0
        release_detected = bool(release_indices or open_g_indices)
        continuous = (
            source_detected
            and target_reached
            and rise >= 1.25
            and ascent_frames >= 2
            and sustained_peak_frames >= 2
            and descent_detected
            and release_detected
        )

        score = (
            rise * 4.0
            + descent * 2.0
            + ascent_frames * 0.25
            + sustained_peak_frames * 0.5
            + (8.0 if source_detected else 0.0)
            + (8.0 if target_reached else 0.0)
            + (8.0 if release_detected else 0.0)
        )

        candidate = {
            "bendId": expected["bendId"],
            "measure": measure,
            "measureStart": round(measure_start, 4),
            "measureEnd": round(measure_end, 4),
            "bendStart": round(times[source_index], 4),
            "peakTime": round(times[peak_index], 4),
            "voicedFrameCount": len(frame_indices),
            "sourcePitch": round(source_pitch, 3),
            "peakPitch": round(peak_pitch, 3),
            "lowestAfterPeak": round(lowest_after, 3),
            "riseSemitones": round(rise, 3),
            "descentSemitones": round(descent, 3),
            "sourceDetected": source_detected,
            "targetReached": target_reached,
            "ascentFrames": ascent_frames,
            "sustainedPeakFrames": sustained_peak_frames,
            "descentDetected": descent_detected,
            "releaseDetected": release_detected,
            "openGDetected": bool(open_g_indices),
            "continuousBendEvidence": continuous,
            "candidateScore": round(score, 3),
        }
        if best is None or score > float(best["candidateScore"]):
            best = candidate

    if best is None:
        best = {
            "bendId": expected["bendId"],
            "measure": measure,
            "measureStart": round(measure_start, 4),
            "measureEnd": round(measure_end, 4),
            "voicedFrameCount": len(frame_indices),
            "sourceDetected": False,
            "targetReached": False,
            "descentDetected": False,
            "releaseDetected": False,
            "continuousBendEvidence": False,
            "reason": "no-rising-contour-candidate",
        }

    sample_indices = frame_indices[:: max(1, len(frame_indices) // 28)]
    best["contour"] = [
        {
            "time": round(times[index], 4),
            "midi": round(float(midi_curve[index]), 3),
            "confidence": round(float(confidence_curve[index]), 3),
        }
        for index in sample_indices
    ]
    return best


@app.function(image=image, timeout=900, memory=4096)
def analyse_contours(
    audio_bytes: bytes,
    filename: str,
    fixture: dict[str, Any],
) -> dict[str, Any]:
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

        # Stronger harmonic extraction suppresses drums before high-resolution CQT.
        harmonic, _ = librosa.effects.hpss(audio, margin=(1.0, 5.0))
        hop_length = 128
        bins_per_octave = 36
        cqt = np.abs(
            librosa.cqt(
                harmonic,
                sr=sample_rate,
                hop_length=hop_length,
                fmin=librosa.note_to_hz("C3"),
                n_bins=72,
                bins_per_octave=bins_per_octave,
            )
        )
        frequencies = librosa.cqt_frequencies(
            cqt.shape[0],
            fmin=librosa.note_to_hz("C3"),
            bins_per_octave=bins_per_octave,
        )
        midi_bins = librosa.hz_to_midi(frequencies)
        guitar_band = np.where((midi_bins >= 53.0) & (midi_bins <= 62.0))[0]
        times_array = librosa.times_like(
            cqt[0], sr=sample_rate, hop_length=hop_length
        )

        midi_values: list[float | None] = []
        confidences: list[float] = []
        for frame_index in range(cqt.shape[1]):
            magnitudes = cqt[guitar_band, frame_index]
            total = float(np.sum(magnitudes))
            if total <= 1e-8:
                midi_values.append(None)
                confidences.append(0.0)
                continue

            local_peak = int(np.argmax(magnitudes))
            peak_band_index = int(guitar_band[local_peak])
            neighbourhood = np.arange(
                max(guitar_band[0], peak_band_index - 2),
                min(guitar_band[-1], peak_band_index + 2) + 1,
            )
            weights = cqt[neighbourhood, frame_index]
            weight_total = float(np.sum(weights))
            pitch = float(
                np.sum(midi_bins[neighbourhood] * weights) / max(weight_total, 1e-8)
            )
            confidence = float(np.max(magnitudes) / max(total, 1e-8))
            midi_values.append(pitch)
            confidences.append(confidence)

        midi_values = rolling_median(midi_values, radius=2)
        times = [float(value) for value in times_array]
        measure_count = int(fixture.get("measureCount") or 4)

        bends = [
            analyse_measure_bend(
                times,
                midi_values,
                confidences,
                duration,
                expected,
                measure_count,
            )
            for expected in fixture.get("expectedBends", [])
        ]
        passed = sum(1 for bend in bends if bend["continuousBendEvidence"])

        return {
            "benchmarkVersion": 3,
            "benchmarkType": "adaptive-cqt-bend-contour",
            "protectedAnalyzer": "7.1-phase-1-canonical-timeline-voicing-handoff",
            "fixtureName": fixture.get("name"),
            "durationSeconds": round(duration, 4),
            "sampleRate": sample_rate,
            "expectedBendCount": len(bends),
            "continuousBendCount": passed,
            "bendContourAccuracy": round(passed / len(bends), 4) if bends else 0.0,
            "bends": bends,
            "method": (
                "measure-wide adaptive search using HPSS drum reduction and a "
                "36-bins-per-octave CQT tracker in the G-string bend register"
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

    print("JIMMY PAIGE ADAPTIVE BEND-CONTOUR BENCHMARK")
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
            "start=", bend.get("bendStart"),
            "source=", bend.get("sourcePitch"),
            "peak=", bend.get("peakPitch"),
            "rise=", bend.get("riseSemitones"),
            "descent=", bend.get("descentSemitones"),
            "release=", bend.get("releaseDetected"),
        )
    print("\nSaved report:", report_output)
    print("V71 remains unchanged and protected by the Stairway guard.")
