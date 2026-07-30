from __future__ import annotations

import math
import subprocess
import tempfile
import wave
from array import array
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any

FRAME_SIZE = 2048
HOP_SIZE = 512
MIN_ONSET_GAP_SECONDS = 0.055
NOISE_FLOOR_MULTIPLIER = 1.8
LOCAL_PEAK_MULTIPLIER = 1.12


def _safe_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _beats_per_measure(time_signature: str) -> int:
    try:
        numerator = int(str(time_signature or "4/4").split("/", 1)[0])
    except (TypeError, ValueError):
        return 4
    return max(1, min(numerator, 12))


def _convert_to_pcm_wav(audio_path: str) -> str:
    handle = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    handle.close()
    output_path = handle.name

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        audio_path,
        "-ac",
        "1",
        "-ar",
        "22050",
        "-c:a",
        "pcm_s16le",
        output_path,
    ]
    subprocess.run(command, check=True)
    return output_path


def _read_pcm_mono(path: str) -> tuple[list[float], int]:
    with wave.open(path, "rb") as source:
        sample_rate = source.getframerate()
        channel_count = source.getnchannels()
        sample_width = source.getsampwidth()
        frame_count = source.getnframes()
        raw = source.readframes(frame_count)

    if sample_width != 2:
        raise ValueError(f"Expected 16-bit PCM, received sample width {sample_width}")

    samples = array("h")
    samples.frombytes(raw)
    if channel_count > 1:
        samples = array(
            "h",
            (
                int(sum(samples[index:index + channel_count]) / channel_count)
                for index in range(0, len(samples), channel_count)
            ),
        )

    scale = float(2**15)
    return [sample / scale for sample in samples], sample_rate


def _frame_rms(samples: list[float]) -> list[float]:
    energies: list[float] = []
    if len(samples) < FRAME_SIZE:
        return energies

    for start in range(0, len(samples) - FRAME_SIZE + 1, HOP_SIZE):
        frame = samples[start:start + FRAME_SIZE]
        energy = math.sqrt(sum(value * value for value in frame) / FRAME_SIZE)
        energies.append(energy)
    return energies


def _detect_onsets(energies: list[float], sample_rate: int) -> list[tuple[float, float]]:
    if len(energies) < 3:
        return []

    positive_flux = [0.0]
    for index in range(1, len(energies)):
        positive_flux.append(max(0.0, energies[index] - energies[index - 1]))

    non_zero_flux = [value for value in positive_flux if value > 0.0]
    flux_floor = median(non_zero_flux) if non_zero_flux else 0.0
    minimum_flux = flux_floor * NOISE_FLOOR_MULTIPLIER
    minimum_gap_frames = max(
        1,
        int(round(MIN_ONSET_GAP_SECONDS * sample_rate / HOP_SIZE)),
    )

    candidates: list[tuple[int, float]] = []
    for index in range(1, len(positive_flux) - 1):
        value = positive_flux[index]
        neighborhood = positive_flux[max(0, index - 4):min(len(positive_flux), index + 5)]
        local_average = sum(neighborhood) / max(1, len(neighborhood))
        if (
            value >= minimum_flux
            and value >= positive_flux[index - 1]
            and value >= positive_flux[index + 1]
            and value >= local_average * LOCAL_PEAK_MULTIPLIER
        ):
            candidates.append((index, value))

    accepted: list[tuple[int, float]] = []
    for index, strength in candidates:
        if not accepted or index - accepted[-1][0] >= minimum_gap_frames:
            accepted.append((index, strength))
            continue
        if strength > accepted[-1][1]:
            accepted[-1] = (index, strength)

    strongest = max((strength for _, strength in accepted), default=1.0)
    return [
        (
            round(index * HOP_SIZE / sample_rate, 6),
            round(strength / strongest, 6),
        )
        for index, strength in accepted
    ]


def analyze_rhythm_candidates(
    audio_path: str,
    *,
    tempo: float,
    time_signature: str,
    total_measures: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Extract rhythm-onset candidates directly from the uploaded audio.

    This V8 layer is deliberately independent of V7 note events. It does not
    generate notes or change the renderer. It supplies read-only timing evidence
    that later V8 stages can compare against V7 pitch candidates before adopting
    any event.
    """

    wav_path = _convert_to_pcm_wav(audio_path)
    try:
        samples, sample_rate = _read_pcm_mono(wav_path)
    finally:
        Path(wav_path).unlink(missing_ok=True)

    energies = _frame_rms(samples)
    onsets = _detect_onsets(energies, sample_rate)

    beats = _beats_per_measure(time_signature)
    measure_seconds = 60.0 / max(1.0, tempo) * beats
    candidates: list[dict[str, Any]] = []

    for candidate_index, (start, strength) in enumerate(onsets):
        raw_measure = int(start // measure_seconds) + 1
        if raw_measure < 1 or raw_measure > total_measures:
            continue
        measure_start = (raw_measure - 1) * measure_seconds
        position = max(0.0, min(0.999999, (start - measure_start) / measure_seconds))
        quantized_step = max(0, min(15, int(round(position * 16.0))))
        candidates.append(
            {
                "candidateIndex": candidate_index,
                "start": start,
                "measureNumber": raw_measure,
                "positionInMeasure": round(position, 6),
                "quantizedStep": quantized_step,
                "strength": strength,
                "source": "direct-audio-energy-onset",
                "readOnly": True,
            }
        )

    intro_candidates = [
        item for item in candidates if 1 <= int(item["measureNumber"]) <= 16
    ]
    step_histogram = Counter(int(item["quantizedStep"]) for item in intro_candidates)
    diagnostics = {
        "candidateAnalyzer": "v8-direct-audio-energy-onset",
        "independentOfV7Events": True,
        "sampleRate": sample_rate,
        "frameSize": FRAME_SIZE,
        "hopSize": HOP_SIZE,
        "audioDurationSeconds": round(len(samples) / sample_rate, 6) if sample_rate else 0.0,
        "candidateCount": len(candidates),
        "introCandidateCount": len(intro_candidates),
        "introStepHistogram": dict(sorted(step_histogram.items())),
        "minimumOnsetGapSeconds": MIN_ONSET_GAP_SECONDS,
        "readOnly": True,
        "rendererChanged": False,
    }
    return candidates, diagnostics
