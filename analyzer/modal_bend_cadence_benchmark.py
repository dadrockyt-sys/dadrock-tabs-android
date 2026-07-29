"""Detect repeated full-step guitar bends using contour quality plus riff cadence.

This benchmark leaves the protected V71 analyzer unchanged. It uses the two
strongest repeated bend contours to establish the riff period, then searches
near every expected repetition instead of accepting unrelated open-G motion.
"""

from __future__ import annotations

import json
import math
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v71 as analyzer

app = modal.App("dadrock-bend-cadence-benchmark")
image = analyzer.image.add_local_python_source("modal_analyzer_v71")


def rolling_median(values: list[float | None], radius: int = 2) -> list[float | None]:
    output: list[float | None] = []
    for index, value in enumerate(values):
        if value is None:
            output.append(None)
            continue
        neighbourhood = [
            candidate
            for candidate in values[max(0, index - radius): index + radius + 1]
            if candidate is not None
        ]
        output.append(float(statistics.median(neighbourhood)) if neighbourhood else None)
    return output


def build_candidate(
    source_index: int,
    times: list[float],
    midi_curve: list[float | None],
    confidence_curve: list[float],
    source_midi: float,
    target_midi: float,
    release_midi: float,
) -> dict[str, Any] | None:
    source_pitch_value = midi_curve[source_index]
    if source_pitch_value is None:
        return None

    lookahead = [
        index
        for index in range(source_index, len(times))
        if times[index] <= times[source_index] + 0.78
        and midi_curve[index] is not None
        and confidence_curve[index] >= 0.08
    ]
    if len(lookahead) < 5:
        return None

    peak_index = max(lookahead, key=lambda index: float(midi_curve[index]))
    if peak_index <= source_index:
        return None

    after_peak = [
        index
        for index in range(peak_index + 1, len(times))
        if times[index] <= times[peak_index] + 0.78
        and midi_curve[index] is not None
        and confidence_curve[index] >= 0.06
    ]

    source_pitch = float(source_pitch_value)
    peak_pitch = float(midi_curve[peak_index])
    lowest_after = (
        min(float(midi_curve[index]) for index in after_peak)
        if after_peak
        else peak_pitch
    )
    rise = peak_pitch - source_pitch
    descent = peak_pitch - lowest_after

    ascent_indices = [index for index in lookahead if index <= peak_index]
    ascent_frames = sum(
        1
        for left, right in zip(ascent_indices, ascent_indices[1:])
        if float(midi_curve[right]) >= float(midi_curve[left]) - 0.3
    )
    peak_frames = sum(
        1
        for index in lookahead
        if abs(times[index] - times[peak_index]) <= 0.12
        and float(midi_curve[index]) >= target_midi - 0.85
    )
    release_indices = [
        index
        for index in after_peak
        if float(midi_curve[index]) <= source_midi + 0.9
        or abs(float(midi_curve[index]) - release_midi) <= 1.0
    ]

    source_detected = abs(source_pitch - source_midi) <= 1.2
    target_reached = peak_pitch >= target_midi - 0.75
    release_detected = bool(release_indices)
    descent_detected = descent >= 1.0
    continuous = (
        source_detected
        and target_reached
        and rise >= 1.25
        and ascent_frames >= 2
        and peak_frames >= 2
        and descent_detected
        and release_detected
    )

    score = (
        max(0.0, 2.0 - abs(source_pitch - source_midi)) * 8.0
        + min(max(rise, 0.0), 3.0) * 7.0
        + min(max(descent, 0.0), 4.0) * 2.0
        + peak_frames * 0.7
        + ascent_frames * 0.2
        + (10.0 if target_reached else 0.0)
        + (8.0 if release_detected else 0.0)
        - abs(rise - 2.0) * 4.0
    )

    return {
        "bendStart": round(times[source_index], 4),
        "peakTime": round(times[peak_index], 4),
        "sourcePitch": round(source_pitch, 3),
        "peakPitch": round(peak_pitch, 3),
        "lowestAfterPeak": round(lowest_after, 3),
        "riseSemitones": round(rise, 3),
        "descentSemitones": round(descent, 3),
        "ascentFrames": ascent_frames,
        "sustainedPeakFrames": peak_frames,
        "sourceDetected": source_detected,
        "targetReached": target_reached,
        "descentDetected": descent_detected,
        "releaseDetected": release_detected,
        "continuousBendEvidence": continuous,
        "candidateScore": round(score, 3),
    }


def collect_candidates(
    times: list[float],
    midi_curve: list[float | None],
    confidence_curve: list[float],
    source_midi: float,
    target_midi: float,
    release_midi: float,
) -> list[dict[str, Any]]:
    raw: list[dict[str, Any]] = []
    for index, (pitch, confidence) in enumerate(zip(midi_curve, confidence_curve)):
        if pitch is None or confidence < 0.08:
            continue
        if not 54.5 <= float(pitch) <= 58.3:
            continue
        candidate = build_candidate(
            index,
            times,
            midi_curve,
            confidence_curve,
            source_midi,
            target_midi,
            release_midi,
        )
        if candidate is not None and candidate["riseSemitones"] >= 0.65:
            raw.append(candidate)

    raw.sort(key=lambda item: float(item["candidateScore"]), reverse=True)
    kept: list[dict[str, Any]] = []
    for candidate in raw:
        if any(
            abs(float(candidate["bendStart"]) - float(existing["bendStart"])) < 0.42
            for existing in kept
        ):
            continue
        kept.append(candidate)
        if len(kept) >= 24:
            break
    return sorted(kept, key=lambda item: float(item["bendStart"]))


def choose_repeated_sequence(
    candidates: list[dict[str, Any]],
    expected_count: int,
    duration: float,
) -> tuple[list[dict[str, Any]], float]:
    if expected_count <= 1:
        return candidates[:1], 0.0

    best_sequence: list[dict[str, Any]] = []
    best_period = duration / expected_count
    best_score = -1e9

    plausible_periods: list[float] = []
    for left_index, left in enumerate(candidates):
        for right in candidates[left_index + 1:]:
            gap = float(right["bendStart"]) - float(left["bendStart"])
            if 1.45 <= gap <= 2.25:
                plausible_periods.append(gap)
    if not plausible_periods:
        plausible_periods = [duration / expected_count]

    for period in plausible_periods:
        for anchor in candidates:
            anchor_time = float(anchor["bendStart"])
            for anchor_position in range(expected_count):
                first_time = anchor_time - anchor_position * period
                sequence: list[dict[str, Any]] = []
                total = 0.0
                used: set[int] = set()

                for repetition in range(expected_count):
                    expected_time = first_time + repetition * period
                    choices = [
                        (index, candidate)
                        for index, candidate in enumerate(candidates)
                        if index not in used
                        and abs(float(candidate["bendStart"]) - expected_time) <= 0.52
                    ]
                    if not choices:
                        total -= 28.0
                        continue
                    index, winner = max(
                        choices,
                        key=lambda pair: (
                            float(pair[1]["candidateScore"])
                            - abs(float(pair[1]["bendStart"]) - expected_time) * 30.0
                        ),
                    )
                    used.add(index)
                    selected = dict(winner)
                    selected["expectedStart"] = round(expected_time, 4)
                    selected["cadenceError"] = round(
                        abs(float(winner["bendStart"]) - expected_time), 4
                    )
                    sequence.append(selected)
                    total += float(winner["candidateScore"])
                    total -= selected["cadenceError"] * 30.0
                    if winner["continuousBendEvidence"]:
                        total += 18.0

                total -= abs(period - statistics.median(plausible_periods)) * 3.0
                if len(sequence) > len(best_sequence) or (
                    len(sequence) == len(best_sequence) and total > best_score
                ):
                    best_sequence = sequence
                    best_period = period
                    best_score = total

    return sorted(best_sequence, key=lambda item: float(item["expectedStart"])), best_period


@app.function(image=image, timeout=900, memory=4096)
def analyse_cadence(audio_bytes: bytes, filename: str, fixture: dict[str, Any]) -> dict[str, Any]:
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

        midi_values = rolling_median(midi_values, radius=2)
        times = [float(value) for value in times_array]
        expected_bends = fixture.get("expectedBends", [])
        example = expected_bends[0] if expected_bends else {
            "sourceMidi": 57,
            "targetMidi": 59,
            "releaseToMidi": 55,
        }
        candidates = collect_candidates(
            times,
            midi_values,
            confidences,
            float(example["sourceMidi"]),
            float(example["targetMidi"]),
            float(example["releaseToMidi"]),
        )
        sequence, period = choose_repeated_sequence(candidates, len(expected_bends), duration)

        bends: list[dict[str, Any]] = []
        for index, expected in enumerate(expected_bends):
            if index < len(sequence):
                bend = dict(sequence[index])
            else:
                bend = {
                    "continuousBendEvidence": False,
                    "reason": "no-cadence-aligned-candidate",
                }
            bend["bendId"] = expected["bendId"]
            bend["measure"] = expected["measure"]
            bends.append(bend)

        passed = sum(1 for bend in bends if bend.get("continuousBendEvidence"))
        return {
            "benchmarkVersion": 4,
            "benchmarkType": "cadence-aware-repeated-cqt-bend-contour",
            "protectedAnalyzer": "7.1-phase-1-canonical-timeline-voicing-handoff",
            "fixtureName": fixture.get("name"),
            "durationSeconds": round(duration, 4),
            "estimatedRiffPeriod": round(period, 4),
            "rawCandidateCount": len(candidates),
            "expectedBendCount": len(bends),
            "continuousBendCount": passed,
            "bendContourAccuracy": round(passed / len(bends), 4) if bends else 0.0,
            "bends": bends,
            "method": (
                "global CQT contour inventory followed by cadence-constrained selection "
                "for four repetitions of the same riff"
            ),
        }


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway_bend_reference.json",
    report_output: str = "/tmp/gomyway-cadence-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    report = analyse_cadence.remote(audio_file.read_bytes(), audio_file.name, fixture)
    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )

    print("JIMMY PAIGE CADENCE-AWARE BEND BENCHMARK")
    print("=" * 55)
    print("Protected analyzer:", report.get("protectedAnalyzer"))
    print("Duration:", report.get("durationSeconds"))
    print("Estimated riff period:", report.get("estimatedRiffPeriod"))
    print("Raw contour candidates:", report.get("rawCandidateCount"))
    print(
        "Continuous bends:",
        f"{report.get('continuousBendCount')}/{report.get('expectedBendCount')}",
    )
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
        )
    print("\nSaved report:", report_output)
    print("V71 remains unchanged and protected by the Stairway guard.")
