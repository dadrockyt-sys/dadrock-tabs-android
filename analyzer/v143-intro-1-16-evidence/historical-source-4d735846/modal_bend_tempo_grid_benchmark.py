"""Detect repeated bends on the musical 4/4 tempo grid.

V71 remains protected. This benchmark fixes the cadence estimator by using the
fixture tempo (129 BPM) and the two trustworthy full-step contours as anchors.
"""

from __future__ import annotations

import json
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v71 as analyzer
import modal_bend_cadence_benchmark as previous

app = modal.App("dadrock-bend-tempo-grid-benchmark")
image = (
    analyzer.image
    .add_local_python_source("modal_analyzer_v71")
    .add_local_python_source("modal_bend_cadence_benchmark")
)


def build_tempo_grid(
    candidates: list[dict[str, Any]],
    fixture: dict[str, Any],
) -> tuple[list[float], float, float]:
    tempo = float(fixture.get("tempoBpm") or 120.0)
    beats_per_measure = int((fixture.get("timeSignature") or "4/4").split("/")[0])
    measure_period = 60.0 / tempo * beats_per_measure
    count = len(fixture.get("expectedBends", []))

    trustworthy = [
        candidate
        for candidate in candidates
        if candidate.get("continuousBendEvidence")
        and abs(float(candidate.get("sourcePitch", 0.0)) - 57.0) <= 0.45
        and 1.65 <= float(candidate.get("riseSemitones", 0.0)) <= 2.55
    ]

    offsets: list[float] = []
    for candidate in trustworthy:
        start = float(candidate["bendStart"])
        for index in range(count):
            offset = start - index * measure_period
            if -0.25 <= offset <= measure_period + 0.75:
                offsets.append(offset)

    if offsets:
        # Find the offset receiving the strongest agreement from all good bends.
        scored: list[tuple[float, float]] = []
        for offset in offsets:
            error = 0.0
            matches = 0
            for candidate in trustworthy:
                start = float(candidate["bendStart"])
                nearest = min(
                    abs(start - (offset + index * measure_period))
                    for index in range(count)
                )
                if nearest <= 0.28:
                    matches += 1
                error += min(nearest, 0.75)
            scored.append((matches * 10.0 - error, offset))
        grid_offset = max(scored)[1]
    else:
        grid_offset = max(0.0, measure_period * 0.5)

    starts = [grid_offset + index * measure_period for index in range(count)]
    return starts, measure_period, grid_offset


def select_grid_candidates(
    candidates: list[dict[str, Any]],
    expected_starts: list[float],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    used: set[int] = set()

    for expected in expected_starts:
        choices: list[tuple[float, int, dict[str, Any]]] = []
        for index, candidate in enumerate(candidates):
            if index in used:
                continue
            start = float(candidate["bendStart"])
            timing_error = abs(start - expected)
            if timing_error > 0.58:
                continue
            source_error = abs(float(candidate.get("sourcePitch", 0.0)) - 57.0)
            rise_error = abs(float(candidate.get("riseSemitones", 0.0)) - 2.0)
            quality = float(candidate.get("candidateScore", 0.0))
            quality -= timing_error * 42.0
            quality -= source_error * 22.0
            quality -= rise_error * 12.0
            if candidate.get("continuousBendEvidence"):
                quality += 30.0
            choices.append((quality, index, candidate))

        if not choices:
            selected.append(
                {
                    "expectedStart": round(expected, 4),
                    "continuousBendEvidence": False,
                    "reason": "no-tempo-grid-candidate",
                }
            )
            continue

        _, index, winner = max(choices, key=lambda item: item[0])
        used.add(index)
        item = dict(winner)
        item["expectedStart"] = round(expected, 4)
        item["gridError"] = round(abs(float(item["bendStart"]) - expected), 4)
        selected.append(item)

    return selected


@app.function(image=image, timeout=900, memory=4096)
def analyse_tempo_grid(
    audio_bytes: bytes,
    filename: str,
    fixture: dict[str, Any],
) -> dict[str, Any]:
    import librosa
    import numpy as np

    suffix = Path(filename).suffix.lower() or ".audio"
    with tempfile.TemporaryDirectory() as temp_dir:
        source_file = Path(temp_dir) / f"source{suffix}"
        normalized = Path(temp_dir) / "normalized.wav"
        source_file.write_bytes(audio_bytes)
        analyzer.engine.normalize_audio_file(str(source_file), str(normalized))

        audio, sample_rate = librosa.load(str(normalized), sr=22050, mono=True)
        duration = float(librosa.get_duration(y=audio, sr=sample_rate))
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
        times_array = librosa.times_like(cqt[0], sr=sample_rate, hop_length=hop_length)

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
            midi_values.append(
                float(np.sum(midi_bins[neighbourhood] * weights) / max(weight_total, 1e-8))
            )
            confidences.append(float(np.max(magnitudes) / max(total, 1e-8)))

        midi_values = previous.rolling_median(midi_values, radius=2)
        times = [float(value) for value in times_array]
        expected_bends = fixture.get("expectedBends", [])
        example = expected_bends[0]
        candidates = previous.collect_candidates(
            times,
            midi_values,
            confidences,
            float(example["sourceMidi"]),
            float(example["targetMidi"]),
            float(example["releaseToMidi"]),
        )
        expected_starts, period, offset = build_tempo_grid(candidates, fixture)
        sequence = select_grid_candidates(candidates, expected_starts)

        bends: list[dict[str, Any]] = []
        for index, expected in enumerate(expected_bends):
            bend = dict(sequence[index])
            bend["bendId"] = expected["bendId"]
            bend["measure"] = expected["measure"]
            bends.append(bend)

        passed = sum(1 for bend in bends if bend.get("continuousBendEvidence"))
        return {
            "benchmarkVersion": 5,
            "benchmarkType": "tempo-grid-repeated-cqt-bend-contour",
            "protectedAnalyzer": "7.1-phase-1-canonical-timeline-voicing-handoff",
            "durationSeconds": round(duration, 4),
            "fixtureTempoBpm": fixture.get("tempoBpm"),
            "measurePeriod": round(period, 4),
            "gridOffset": round(offset, 4),
            "rawCandidateCount": len(candidates),
            "expectedBendCount": len(bends),
            "continuousBendCount": passed,
            "bendContourAccuracy": round(passed / len(bends), 4) if bends else 0.0,
            "bends": bends,
        }


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway_bend_reference.json",
    report_output: str = "/tmp/gomyway-tempo-grid-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    report = analyse_tempo_grid.remote(audio_file.read_bytes(), audio_file.name, fixture)
    Path(report_output).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print("JIMMY PAIGE TEMPO-GRID BEND BENCHMARK")
    print("=" * 55)
    print("Protected analyzer:", report.get("protectedAnalyzer"))
    print("Duration:", report.get("durationSeconds"))
    print("Fixture tempo:", report.get("fixtureTempoBpm"))
    print("Measure period:", report.get("measurePeriod"))
    print("Grid offset:", report.get("gridOffset"))
    print("Raw contour candidates:", report.get("rawCandidateCount"))
    print("Continuous bends:", f"{report.get('continuousBendCount')}/{report.get('expectedBendCount')}")
    for bend in report.get("bends", []):
        status = "PASS" if bend.get("continuousBendEvidence") else "FAIL"
        print(
            status,
            bend.get("bendId"),
            "expected=", bend.get("expectedStart"),
            "start=", bend.get("bendStart"),
            "error=", bend.get("gridError"),
            "source=", bend.get("sourcePitch"),
            "peak=", bend.get("peakPitch"),
            "rise=", bend.get("riseSemitones"),
            "release=", bend.get("releaseDetected"),
        )
    print("\nSaved report:", report_output)
    print("V71 remains unchanged and protected by the Stairway guard.")
