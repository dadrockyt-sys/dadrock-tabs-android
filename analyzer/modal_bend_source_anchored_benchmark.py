"""Recover repeated full-step bends from the known fret-2 source pitch.

V71 remains protected. This benchmark keeps the verified 129 BPM grid, then
backtracks from each target-pitch peak to the nearest preceding MIDI-57 frame.
That prevents open-G frames near MIDI 55 from being mistaken for bend starts.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v71 as analyzer
import modal_bend_cadence_benchmark as contour
import modal_bend_tempo_grid_benchmark as tempo_grid

app = modal.App("dadrock-bend-source-anchored-benchmark")
image = (
    analyzer.image
    .add_local_python_source("modal_analyzer_v71")
    .add_local_python_source("modal_bend_cadence_benchmark")
    .add_local_python_source("modal_bend_tempo_grid_benchmark")
)


def recover_grid_bend(
    expected_start: float,
    times: list[float],
    midi_curve: list[float | None],
    confidence_curve: list[float],
    source_midi: float,
    target_midi: float,
    release_midi: float,
) -> dict[str, Any]:
    peak_choices: list[tuple[float, int]] = []
    for index, pitch in enumerate(midi_curve):
        if pitch is None or confidence_curve[index] < 0.06:
            continue
        time = times[index]
        if not expected_start - 0.18 <= time <= expected_start + 0.82:
            continue
        if float(pitch) < target_midi - 0.8:
            continue
        timing = abs(time - (expected_start + 0.22))
        peak_quality = float(pitch) - timing * 2.0 + confidence_curve[index]
        peak_choices.append((peak_quality, index))

    if not peak_choices:
        return {
            "expectedStart": round(expected_start, 4),
            "continuousBendEvidence": False,
            "reason": "no-target-pitch-peak-near-grid",
        }

    for _, peak_index in sorted(peak_choices, reverse=True):
        source_choices: list[tuple[float, int]] = []
        for index in range(peak_index - 1, -1, -1):
            if times[index] < times[peak_index] - 0.62:
                break
            pitch = midi_curve[index]
            if pitch is None or confidence_curve[index] < 0.055:
                continue
            source_error = abs(float(pitch) - source_midi)
            if source_error > 0.7:
                continue
            # Prefer a source close to the expected onset, followed by enough
            # time for an actual bend rather than a descending target crossing.
            lead_time = times[peak_index] - times[index]
            if lead_time < 0.045:
                continue
            score = (
                8.0
                - source_error * 6.0
                - abs(times[index] - expected_start) * 5.0
                + min(lead_time, 0.35) * 2.0
                + confidence_curve[index]
            )
            source_choices.append((score, index))

        for _, source_index in sorted(source_choices, reverse=True):
            candidate = contour.build_candidate(
                source_index,
                times,
                midi_curve,
                confidence_curve,
                source_midi,
                target_midi,
                release_midi,
            )
            if candidate is None:
                continue
            candidate = dict(candidate)
            candidate["expectedStart"] = round(expected_start, 4)
            candidate["gridError"] = round(
                abs(float(candidate["bendStart"]) - expected_start), 4
            )
            candidate["sourceRecoveredFromPeak"] = True
            candidate["selectedPeakTime"] = round(times[peak_index], 4)
            if (
                abs(float(candidate.get("sourcePitch", 0.0)) - source_midi) <= 0.7
                and float(candidate.get("peakPitch", 0.0)) >= target_midi - 0.75
                and 1.45 <= float(candidate.get("riseSemitones", 0.0)) <= 2.75
                and candidate.get("releaseDetected")
            ):
                candidate["continuousBendEvidence"] = True
                return candidate

    return {
        "expectedStart": round(expected_start, 4),
        "continuousBendEvidence": False,
        "reason": "target-found-but-no-valid-midi-57-source",
        "peakCandidates": len(peak_choices),
    }


@app.function(image=image, timeout=900, memory=4096)
def analyse_source_anchored(
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
            midi_values.append(
                float(
                    np.sum(midi_bins[neighbourhood] * weights)
                    / max(weight_total, 1e-8)
                )
            )
            confidences.append(float(np.max(magnitudes) / max(total, 1e-8)))

        midi_values = contour.rolling_median(midi_values, radius=2)
        times = [float(value) for value in times_array]
        expected_bends = fixture.get("expectedBends", [])
        example = expected_bends[0]

        raw_candidates = contour.collect_candidates(
            times,
            midi_values,
            confidences,
            float(example["sourceMidi"]),
            float(example["targetMidi"]),
            float(example["releaseToMidi"]),
        )
        expected_starts, period, offset = tempo_grid.build_tempo_grid(
            raw_candidates, fixture
        )

        bends: list[dict[str, Any]] = []
        for index, expected in enumerate(expected_bends):
            bend = recover_grid_bend(
                expected_starts[index],
                times,
                midi_values,
                confidences,
                float(expected["sourceMidi"]),
                float(expected["targetMidi"]),
                float(expected["releaseToMidi"]),
            )
            bend["bendId"] = expected["bendId"]
            bend["measure"] = expected["measure"]
            bends.append(bend)

        passed = sum(1 for bend in bends if bend.get("continuousBendEvidence"))
        return {
            "benchmarkVersion": 6,
            "benchmarkType": "tempo-grid-source-anchored-cqt-bend-contour",
            "protectedAnalyzer": "7.1-phase-1-canonical-timeline-voicing-handoff",
            "durationSeconds": round(duration, 4),
            "fixtureTempoBpm": fixture.get("tempoBpm"),
            "measurePeriod": round(period, 4),
            "gridOffset": round(offset, 4),
            "rawCandidateCount": len(raw_candidates),
            "expectedBendCount": len(bends),
            "continuousBendCount": passed,
            "bendContourAccuracy": round(passed / len(bends), 4) if bends else 0.0,
            "bends": bends,
        }


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway_bend_reference.json",
    report_output: str = "/tmp/gomyway-source-anchored-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    report = analyse_source_anchored.remote(
        audio_file.read_bytes(), audio_file.name, fixture
    )
    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )

    print("JIMMY PAIGE SOURCE-ANCHORED BEND BENCHMARK")
    print("=" * 58)
    print("Protected analyzer:", report.get("protectedAnalyzer"))
    print("Duration:", report.get("durationSeconds"))
    print("Fixture tempo:", report.get("fixtureTempoBpm"))
    print("Measure period:", report.get("measurePeriod"))
    print("Grid offset:", report.get("gridOffset"))
    print("Continuous bends:", f"{report.get('continuousBendCount')}/{report.get('expectedBendCount')}")
    for bend in report.get("bends", []):
        status = "PASS" if bend.get("continuousBendEvidence") else "FAIL"
        print(
            status,
            bend.get("bendId"),
            "expected=", bend.get("expectedStart"),
            "start=", bend.get("bendStart"),
            "source=", bend.get("sourcePitch"),
            "peak=", bend.get("peakPitch"),
            "rise=", bend.get("riseSemitones"),
            "release=", bend.get("releaseDetected"),
            "reason=", bend.get("reason"),
        )
    print("\nSaved report:", report_output)
    print("V71 remains unchanged and protected by the Stairway guard.")
