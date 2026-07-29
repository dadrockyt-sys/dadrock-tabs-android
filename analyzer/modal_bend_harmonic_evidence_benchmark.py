"""Recover repeated bends from multi-bin harmonic energy instead of one dominant pitch.

The source-anchored benchmark proved bends 2 and 3 are clean, while drums and
adjacent open-string energy mask either the source or target of bends 1 and 4.
This benchmark keeps the verified 129 BPM grid, but measures coordinated energy
movement around MIDI 57 and 59 (plus their octave harmonics). V71 is untouched.
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

app = modal.App("dadrock-bend-harmonic-evidence-benchmark")
image = (
    analyzer.image
    .add_local_python_source("modal_analyzer_v71")
    .add_local_python_source("modal_bend_cadence_benchmark")
    .add_local_python_source("modal_bend_tempo_grid_benchmark")
)


def _band_energy(
    cqt: Any,
    midi_bins: Any,
    centre: float,
    half_width: float = 0.45,
) -> Any:
    import numpy as np

    indices = np.where(
        (midi_bins >= centre - half_width)
        & (midi_bins <= centre + half_width)
    )[0]
    if len(indices) == 0:
        return np.zeros(cqt.shape[1], dtype=float)
    return np.sum(cqt[indices, :], axis=0)


def _smooth(values: Any, width: int = 5) -> Any:
    import numpy as np

    if width <= 1:
        return values
    kernel = np.ones(width, dtype=float) / float(width)
    return np.convolve(values, kernel, mode="same")


def evaluate_grid_window(
    expected_start: float,
    times: Any,
    source_energy: Any,
    target_energy: Any,
    release_energy: Any,
) -> dict[str, Any]:
    import numpy as np

    indices = np.where(
        (times >= expected_start - 0.16)
        & (times <= expected_start + 0.86)
    )[0]
    if len(indices) < 8:
        return {
            "expectedStart": round(expected_start, 4),
            "continuousBendEvidence": False,
            "reason": "insufficient-grid-window-frames",
        }

    local_times = times[indices]
    local_source = source_energy[indices]
    local_target = target_energy[indices]
    local_release = release_energy[indices]

    # Normalize inside each measure so loudness differences do not decide the test.
    scale = float(
        np.percentile(local_source + local_target + local_release, 95)
    )
    scale = max(scale, 1e-9)
    local_source = local_source / scale
    local_target = local_target / scale
    local_release = local_release / scale

    early_mask = local_times <= expected_start + 0.32
    target_mask = (
        (local_times >= expected_start + 0.05)
        & (local_times <= expected_start + 0.58)
    )
    late_mask = local_times >= expected_start + 0.24

    if not np.any(early_mask) or not np.any(target_mask) or not np.any(late_mask):
        return {
            "expectedStart": round(expected_start, 4),
            "continuousBendEvidence": False,
            "reason": "incomplete-source-target-release-window",
        }

    source_candidates = np.where(early_mask)[0]
    source_index = int(
        source_candidates[
            np.argmax(
                local_source[source_candidates]
                - 0.30 * local_target[source_candidates]
            )
        ]
    )

    target_candidates = np.where(
        target_mask & (np.arange(len(local_times)) > source_index)
    )[0]
    if len(target_candidates) == 0:
        return {
            "expectedStart": round(expected_start, 4),
            "continuousBendEvidence": False,
            "reason": "no-target-frame-after-source",
        }

    target_index = int(
        target_candidates[
            np.argmax(
                local_target[target_candidates]
                - 0.20 * local_source[target_candidates]
            )
        ]
    )

    release_candidates = np.where(
        late_mask & (np.arange(len(local_times)) > target_index)
    )[0]
    if len(release_candidates) == 0:
        release_index = target_index
    else:
        release_index = int(
            release_candidates[
                np.argmax(
                    local_release[release_candidates]
                    + 0.35 * local_source[release_candidates]
                    - 0.20 * local_target[release_candidates]
                )
            ]
        )

    source_strength = float(local_source[source_index])
    target_strength = float(local_target[target_index])
    release_strength = float(local_release[release_index])
    target_gain = float(
        local_target[target_index] - local_target[source_index]
    )
    source_to_target_time = float(
        local_times[target_index] - local_times[source_index]
    )
    release_drop = float(
        local_target[target_index] - local_target[release_index]
    )

    source_present = source_strength >= 0.075
    target_present = target_strength >= 0.085
    ordered_rise = 0.025 <= source_to_target_time <= 0.55
    target_grew = target_gain >= 0.025
    release_detected = (
        release_index > target_index
        and release_drop >= 0.018
        and release_strength >= 0.045
    )

    passed = bool(
        source_present
        and target_present
        and ordered_rise
        and target_grew
        and release_detected
    )

    return {
        "expectedStart": round(expected_start, 4),
        "bendStart": round(float(local_times[source_index]), 4),
        "targetTime": round(float(local_times[target_index]), 4),
        "releaseTime": round(float(local_times[release_index]), 4),
        "sourceStrength": round(source_strength, 4),
        "targetStrength": round(target_strength, 4),
        "releaseStrength": round(release_strength, 4),
        "targetGain": round(target_gain, 4),
        "riseDuration": round(source_to_target_time, 4),
        "targetReleaseDrop": round(release_drop, 4),
        "sourceDetected": source_present,
        "targetDetected": target_present,
        "releaseDetected": release_detected,
        "continuousBendEvidence": passed,
        "reason": None if passed else "harmonic-energy-criteria-not-met",
    }


@app.function(image=image, timeout=900, memory=4096)
def analyse_harmonic_evidence(
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
        harmonic, _ = librosa.effects.hpss(audio, margin=(1.0, 6.0))
        hop_length = 128
        bins_per_octave = 48
        cqt = np.abs(
            librosa.cqt(
                harmonic,
                sr=sample_rate,
                hop_length=hop_length,
                fmin=librosa.note_to_hz("C3"),
                n_bins=96,
                bins_per_octave=bins_per_octave,
            )
        )
        midi_bins = librosa.hz_to_midi(
            librosa.cqt_frequencies(
                cqt.shape[0],
                fmin=librosa.note_to_hz("C3"),
                bins_per_octave=bins_per_octave,
            )
        )
        times = librosa.times_like(
            cqt[0], sr=sample_rate, hop_length=hop_length
        )

        expected_bends = fixture.get("expectedBends", [])
        example = expected_bends[0]
        source_midi = float(example["sourceMidi"])
        target_midi = float(example["targetMidi"])
        release_midi = float(example["releaseToMidi"])

        # Fundamental plus octave harmonic makes the evidence robust when drums or
        # an open string temporarily dominate the lowest tracked bin.
        source_energy = (
            _band_energy(cqt, midi_bins, source_midi)
            + 0.55 * _band_energy(cqt, midi_bins, source_midi + 12.0)
        )
        target_energy = (
            _band_energy(cqt, midi_bins, target_midi)
            + 0.55 * _band_energy(cqt, midi_bins, target_midi + 12.0)
        )
        release_energy = (
            _band_energy(cqt, midi_bins, release_midi)
            + 0.45 * _band_energy(cqt, midi_bins, release_midi + 12.0)
        )
        source_energy = _smooth(source_energy, 5)
        target_energy = _smooth(target_energy, 5)
        release_energy = _smooth(release_energy, 5)

        # Keep the already verified tempo-grid construction.
        midi_values: list[float | None] = []
        confidences: list[float] = []
        guitar_band = np.where((midi_bins >= 53.0) & (midi_bins <= 62.0))[0]
        for frame_index in range(cqt.shape[1]):
            magnitudes = cqt[guitar_band, frame_index]
            total = float(np.sum(magnitudes))
            if total <= 1e-8:
                midi_values.append(None)
                confidences.append(0.0)
                continue
            local_peak = int(np.argmax(magnitudes))
            peak_index = int(guitar_band[local_peak])
            midi_values.append(float(midi_bins[peak_index]))
            confidences.append(float(np.max(magnitudes) / max(total, 1e-8)))

        midi_values = contour.rolling_median(midi_values, radius=2)
        raw_candidates = contour.collect_candidates(
            [float(value) for value in times],
            midi_values,
            confidences,
            source_midi,
            target_midi,
            release_midi,
        )
        expected_starts, period, offset = tempo_grid.build_tempo_grid(
            raw_candidates, fixture
        )

        bends: list[dict[str, Any]] = []
        for index, expected in enumerate(expected_bends):
            bend = evaluate_grid_window(
                expected_starts[index],
                times,
                source_energy,
                target_energy,
                release_energy,
            )
            bend["bendId"] = expected["bendId"]
            bend["measure"] = expected["measure"]
            bends.append(bend)

        passed = sum(1 for bend in bends if bend.get("continuousBendEvidence"))
        return {
            "benchmarkVersion": 7,
            "benchmarkType": "tempo-grid-multi-harmonic-energy-bend-evidence",
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
    report_output: str = "/tmp/gomyway-harmonic-evidence-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    report = analyse_harmonic_evidence.remote(
        audio_file.read_bytes(), audio_file.name, fixture
    )
    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )

    print("JIMMY PAIGE HARMONIC-EVIDENCE BEND BENCHMARK")
    print("=" * 62)
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
            "target=", bend.get("targetTime"),
            "sourceEnergy=", bend.get("sourceStrength"),
            "targetEnergy=", bend.get("targetStrength"),
            "targetGain=", bend.get("targetGain"),
            "release=", bend.get("releaseDetected"),
            "reason=", bend.get("reason"),
        )
    print("\nSaved report:", report_output)
    print("V71 remains unchanged and protected by the Stairway guard.")
