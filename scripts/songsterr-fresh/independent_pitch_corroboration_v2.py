#!/usr/bin/env python3
"""Independent two-channel pitch corroboration research contract v2.

Reference-blind research only. Frozen by
docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V2.md
before authorized-song evaluation.

This module does not invoke Demucs or Basic Pitch, does not change upstream
pitch/event identity, does not write duration, and does not promote model
validation or customer eligibility.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import wave
from pathlib import Path

import numpy as np

CONTRACT = "songsterr-fresh-independent-pitch-corroboration-research-v2"
FIXTURE_CONTRACT = "songsterr-fresh-independent-pitch-corroboration-fixtures-v2"
EXPECTED_EVIDENCE_CONTRACT = "songsterr-fresh-isolated-polyphonic-note-evidence-v1"

SAMPLE_RATE = 44100
WINDOW_SAMPLES = 16384
FFT_SIZE = 32768
PLAYABLE_MIDI_MIN = 40
PLAYABLE_MIDI_MAX = 88
COMPETITOR_OFFSETS = (-12, -7, -2, -1, 1, 2, 7, 12)
HARMONIC_COUNT = 4
SPECTRAL_LOG_FLOOR = 1e-15
MIN_WINDOW_RMS = 1e-4
FIXTURE_PEAK = 0.75

CLASS_CORROBORATED = "independently-corroborated-candidate"
CLASS_NOT_CORROBORATED = "not-independently-corroborated"
CLASS_INSUFFICIENT = "insufficient-evidence"
ALLOWED_CLASSES = {
    CLASS_CORROBORATED,
    CLASS_NOT_CORROBORATED,
    CLASS_INSUFFICIENT,
}


class CorroborationError(RuntimeError):
    pass


def canonical_json(value) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def midi_to_hz(midi: float) -> float:
    return 440.0 * (2.0 ** ((float(midi) - 69.0) / 12.0))


def competitor_midis(selected_midi: int) -> list[int]:
    values = [selected_midi]
    for offset in COMPETITOR_OFFSETS:
        candidate = selected_midi + offset
        if PLAYABLE_MIDI_MIN <= candidate <= PLAYABLE_MIDI_MAX:
            values.append(candidate)
    return values


def _finite_float(value, label: str) -> float:
    if isinstance(value, bool):
        raise CorroborationError(f"{label}:FINITE_NUMBER_REQUIRED")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise CorroborationError(f"{label}:FINITE_NUMBER_REQUIRED") from exc
    if not math.isfinite(number):
        raise CorroborationError(f"{label}:FINITE_NUMBER_REQUIRED")
    return number


def _prepare_window(samples: np.ndarray) -> np.ndarray:
    values = np.asarray(samples, dtype=np.float64)
    if values.ndim != 1:
        raise CorroborationError("MONO_WINDOW_REQUIRED")
    if values.size != WINDOW_SAMPLES:
        raise CorroborationError("EXACT_WINDOW_SAMPLE_COUNT_REQUIRED")
    if not np.all(np.isfinite(values)):
        raise CorroborationError("NONFINITE_AUDIO_WINDOW")
    return values - float(np.mean(values))


def _spectral_magnitudes(samples: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    values = _prepare_window(samples)
    windowed = values * np.hanning(WINDOW_SAMPLES)
    spectrum = np.fft.rfft(windowed, n=FFT_SIZE)
    magnitude = np.abs(spectrum)
    total = float(np.sum(magnitude))
    if not math.isfinite(total) or total <= 0.0:
        raise CorroborationError("SPECTRAL_MAGNITUDE_SUPPORT_REQUIRED")
    normalized = magnitude / total
    frequencies = np.fft.rfftfreq(FFT_SIZE, d=1.0 / float(SAMPLE_RATE))
    return normalized, frequencies


def _candidate_fundamental_bin(
    magnitude: np.ndarray,
    frequencies: np.ndarray,
    midi: int,
) -> int | None:
    low_hz = midi_to_hz(float(midi) - 0.5)
    high_hz = midi_to_hz(float(midi) + 0.5)
    indices = np.flatnonzero((frequencies >= low_hz) & (frequencies < high_hz))
    if indices.size == 0:
        return None
    local = magnitude[indices]
    if local.size == 0 or not np.all(np.isfinite(local)):
        return None
    # np.argmax returns the first maximum, so an exact bin tie deterministically
    # chooses the lower-frequency bin because indices are ascending.
    return int(indices[int(np.argmax(local))])


def _nearest_bin_neighborhood_max(
    magnitude: np.ndarray,
    frequencies: np.ndarray,
    target_hz: float,
) -> float | None:
    if not math.isfinite(target_hz) or target_hz <= 0.0 or target_hz >= SAMPLE_RATE / 2.0:
        return None
    position = target_hz * float(FFT_SIZE) / float(SAMPLE_RATE)
    nearest = int(math.floor(position + 0.5))
    left = max(0, nearest - 1)
    right = min(magnitude.size - 1, nearest + 1)
    values = magnitude[left : right + 1]
    if values.size == 0 or not np.all(np.isfinite(values)):
        return None
    return float(np.max(values))


def coherent_harmonic_product_scores(
    samples: np.ndarray,
    midis: list[int],
) -> tuple[dict[int, float], dict[int, dict]]:
    """Channel A: coherent semitone-cell harmonic geometric-mean salience."""
    magnitude, frequencies = _spectral_magnitudes(samples)
    scores: dict[int, float] = {}
    details: dict[int, dict] = {}
    for midi in midis:
        fundamental_bin = _candidate_fundamental_bin(magnitude, frequencies, midi)
        if fundamental_bin is None:
            scores[midi] = float("-inf")
            details[midi] = {
                "fundamentalBin": None,
                "fundamentalHz": None,
                "harmonicMagnitudes": [],
            }
            continue
        f_hat = float(frequencies[fundamental_bin])
        harmonic_magnitudes: list[float] = []
        valid = True
        for harmonic in range(1, HARMONIC_COUNT + 1):
            value = _nearest_bin_neighborhood_max(
                magnitude,
                frequencies,
                float(harmonic) * f_hat,
            )
            if value is None or not math.isfinite(value):
                valid = False
                break
            harmonic_magnitudes.append(value)
        if not valid or len(harmonic_magnitudes) != HARMONIC_COUNT:
            scores[midi] = float("-inf")
        else:
            logs = [math.log(max(SPECTRAL_LOG_FLOOR, value)) for value in harmonic_magnitudes]
            scores[midi] = float(sum(logs) / float(HARMONIC_COUNT))
        details[midi] = {
            "fundamentalBin": fundamental_bin,
            "fundamentalHz": f_hat,
            "harmonicMagnitudes": harmonic_magnitudes,
        }
    return scores, details


def _linear_autocorrelation(values: np.ndarray, max_lag: int) -> np.ndarray:
    """Return non-cyclic positive-lag autocorrelation through max_lag."""
    if max_lag < 0 or max_lag >= values.size:
        raise CorroborationError("YIN_MAX_LAG_OUT_OF_RANGE")
    fft_size = FFT_SIZE
    if fft_size < 2 * values.size:
        raise CorroborationError("YIN_FFT_SIZE_TOO_SMALL")
    transform = np.fft.rfft(values, n=fft_size)
    autocorrelation = np.fft.irfft(transform * np.conj(transform), n=fft_size)
    result = np.asarray(autocorrelation[: max_lag + 1], dtype=np.float64)
    if not np.all(np.isfinite(result)):
        raise CorroborationError("YIN_AUTOCORRELATION_NONFINITE")
    return result


def _yin_cmnd(samples: np.ndarray) -> np.ndarray:
    values = _prepare_window(samples)
    maximum_lag = int(math.ceil(float(SAMPLE_RATE) / midi_to_hz(PLAYABLE_MIDI_MIN - 0.5))) + 2
    autocorrelation = _linear_autocorrelation(values, maximum_lag)
    squares = np.square(values)
    prefix = np.concatenate(([0.0], np.cumsum(squares, dtype=np.float64)))
    difference = np.zeros(maximum_lag + 1, dtype=np.float64)
    n = values.size
    for lag in range(1, maximum_lag + 1):
        left_energy = float(prefix[n - lag] - prefix[0])
        right_energy = float(prefix[n] - prefix[lag])
        value = left_energy + right_energy - 2.0 * float(autocorrelation[lag])
        # Numerical roundoff can produce a tiny negative value for a theoretically
        # non-negative squared-difference sum.
        difference[lag] = max(0.0, value)
    cmnd = np.ones(maximum_lag + 1, dtype=np.float64)
    cumulative = 0.0
    for lag in range(1, maximum_lag + 1):
        cumulative += float(difference[lag])
        if cumulative <= 0.0:
            cmnd[lag] = 1.0
        else:
            cmnd[lag] = float(difference[lag]) * float(lag) / cumulative
    if not np.all(np.isfinite(cmnd)):
        raise CorroborationError("YIN_CMND_NONFINITE")
    return cmnd


def _interpolate_array(values: np.ndarray, position: float) -> float | None:
    if not math.isfinite(position) or position < 0.0 or position >= values.size - 1:
        return None
    lower = int(math.floor(position))
    upper = lower + 1
    fraction = position - float(lower)
    lower_value = float(values[lower])
    upper_value = float(values[upper])
    if not math.isfinite(lower_value) or not math.isfinite(upper_value):
        return None
    return (1.0 - fraction) * lower_value + fraction * upper_value


def octave_disambiguated_yin_scores(
    samples: np.ndarray,
    midis: list[int],
) -> tuple[dict[int, float], dict[int, dict]]:
    """Channel B: CMND minimum contrasted against its half-period explanation."""
    cmnd = _yin_cmnd(samples)
    scores: dict[int, float] = {}
    details: dict[int, dict] = {}
    for midi in midis:
        low_hz = midi_to_hz(float(midi) - 0.5)
        high_hz = midi_to_hz(float(midi) + 0.5)
        # Frequency cell [low_hz, high_hz) maps inversely into lag space.
        minimum_lag = int(math.ceil(float(SAMPLE_RATE) / high_hz))
        maximum_lag = int(math.floor(float(SAMPLE_RATE) / low_hz))
        lags = [lag for lag in range(minimum_lag, maximum_lag + 1) if 0 < lag < cmnd.size]
        if not lags:
            scores[midi] = float("-inf")
            details[midi] = {
                "selectedLag": None,
                "selectedCmnd": None,
                "halfLagCmnd": None,
            }
            continue
        center_lag = float(SAMPLE_RATE) / midi_to_hz(midi)
        best_lag = min(lags, key=lambda lag: (float(cmnd[lag]), abs(float(lag) - center_lag), lag))
        primary = float(cmnd[best_lag])
        half = _interpolate_array(cmnd, float(best_lag) / 2.0)
        if half is None or not math.isfinite(primary):
            scores[midi] = float("-inf")
        else:
            scores[midi] = float(half - primary)
        details[midi] = {
            "selectedLag": int(best_lag),
            "selectedCmnd": primary,
            "halfLagCmnd": half,
        }
    return scores, details


def _winner_measurement(scores: dict[int, float], selected_midi: int) -> dict:
    if selected_midi not in scores:
        raise CorroborationError("SELECTED_MIDI_SCORE_MISSING")
    selected = float(scores[selected_midi])
    competitors = {
        int(midi): float(score)
        for midi, score in scores.items()
        if int(midi) != int(selected_midi)
    }
    finite_competitors = {
        midi: score for midi, score in competitors.items() if math.isfinite(score)
    }
    if not math.isfinite(selected) or len(finite_competitors) != len(competitors) or not competitors:
        return {
            "selectedScore": None if not math.isfinite(selected) else selected,
            "bestCompetitorMidi": None,
            "bestCompetitorScore": None,
            "selectedMinusBestCompetitor": None,
            "uniqueBest": False,
            "insufficient": True,
        }
    best_midi, best_score = max(
        finite_competitors.items(),
        key=lambda item: (item[1], -abs(item[0] - selected_midi), -item[0]),
    )
    margin = selected - best_score
    return {
        "selectedScore": selected,
        "bestCompetitorMidi": int(best_midi),
        "bestCompetitorScore": float(best_score),
        "selectedMinusBestCompetitor": float(margin),
        "uniqueBest": bool(selected > best_score),
        "insufficient": False,
    }


def classify_window(samples: np.ndarray, selected_midi: int) -> dict:
    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        raise CorroborationError("SELECTED_MIDI_INTEGER_REQUIRED")
    selected_midi = int(selected_midi)
    if not PLAYABLE_MIDI_MIN <= selected_midi <= PLAYABLE_MIDI_MAX:
        raise CorroborationError("SELECTED_MIDI_OUTSIDE_PLAYABLE_RANGE")
    values = _prepare_window(samples)
    rms = float(np.sqrt(np.mean(np.square(values))))
    candidates = competitor_midis(selected_midi)
    if rms < MIN_WINDOW_RMS:
        return {
            "classification": CLASS_INSUFFICIENT,
            "selectedMidi": selected_midi,
            "competitorMidis": candidates,
            "windowRms": rms,
            "channelA": None,
            "channelB": None,
            "reason": "WINDOW_RMS_BELOW_FIXED_MINIMUM",
        }
    try:
        channel_a_scores, channel_a_details = coherent_harmonic_product_scores(values, candidates)
        channel_b_scores, channel_b_details = octave_disambiguated_yin_scores(values, candidates)
    except CorroborationError:
        return {
            "classification": CLASS_INSUFFICIENT,
            "selectedMidi": selected_midi,
            "competitorMidis": candidates,
            "windowRms": rms,
            "channelA": None,
            "channelB": None,
            "reason": "CHANNEL_SCORE_INSUFFICIENT",
        }
    channel_a = _winner_measurement(channel_a_scores, selected_midi)
    channel_b = _winner_measurement(channel_b_scores, selected_midi)
    if channel_a["insufficient"] or channel_b["insufficient"]:
        classification = CLASS_INSUFFICIENT
        reason = "CHANNEL_SCORE_INSUFFICIENT"
    elif channel_a["uniqueBest"] and channel_b["uniqueBest"]:
        classification = CLASS_CORROBORATED
        reason = "BOTH_CHANNELS_STRICT_UNIQUE_BEST"
    else:
        classification = CLASS_NOT_CORROBORATED
        reason = "CHANNEL_DISAGREEMENT_OR_NON_UNIQUE_SELECTED"
    return {
        "classification": classification,
        "selectedMidi": selected_midi,
        "competitorMidis": candidates,
        "windowRms": rms,
        "channelA": {
            "method": "hann16384-rfft32768-normalized-magnitude-coherent-four-harmonic-log-mean",
            "scores": {str(k): float(v) for k, v in sorted(channel_a_scores.items())},
            "details": {str(k): v for k, v in sorted(channel_a_details.items())},
            **channel_a,
        },
        "channelB": {
            "method": "yin-cmnd-cell-minimum-half-period-contrast",
            "scores": {str(k): float(v) for k, v in sorted(channel_b_scores.items())},
            "details": {str(k): v for k, v in sorted(channel_b_details.items())},
            **channel_b,
        },
        "reason": reason,
    }


def _pluck(
    midi: int,
    *,
    cents: float = 0.0,
    amplitudes=(1.0, 0.55, 0.30, 0.18, 0.10, 0.06),
    decay_per_second: float = 8.0,
) -> np.ndarray:
    time = np.arange(WINDOW_SAMPLES, dtype=np.float64) / float(SAMPLE_RATE)
    envelope = np.exp(-float(decay_per_second) * time)
    fundamental = midi_to_hz(float(midi) + float(cents) / 100.0)
    signal = np.zeros(WINDOW_SAMPLES, dtype=np.float64)
    for harmonic, amplitude in enumerate(amplitudes, start=1):
        frequency = fundamental * float(harmonic)
        if frequency >= SAMPLE_RATE / 2.0:
            continue
        signal += float(amplitude) * np.sin(2.0 * np.pi * frequency * time)
    return signal * envelope


def _normalize_peak(values: np.ndarray, peak: float = FIXTURE_PEAK) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    maximum = float(np.max(np.abs(values))) if values.size else 0.0
    return values.copy() if maximum <= 0.0 else values * (float(peak) / maximum)


def _fixture_signals() -> dict[str, tuple[np.ndarray, int, str]]:
    attack_rng = np.random.default_rng(97531)
    attack = np.zeros(WINDOW_SAMPLES, dtype=np.float64)
    attack_samples = 512
    attack[:attack_samples] = (
        0.30
        * attack_rng.standard_normal(attack_samples)
        * np.exp(-np.arange(attack_samples, dtype=np.float64) / 120.0)
    )
    low_noise_rng = np.random.default_rng(2468)
    return {
        "mono_low_m40": (_normalize_peak(_pluck(40)), 40, CLASS_CORROBORATED),
        "mono_mid_m64": (_normalize_peak(_pluck(64)), 64, CLASS_CORROBORATED),
        "mono_high_m88": (_normalize_peak(_pluck(88)), 88, CLASS_CORROBORATED),
        "detuned_plus35_m64": (
            _normalize_peak(_pluck(64, cents=35.0)),
            64,
            CLASS_CORROBORATED,
        ),
        "detuned_minus35_m52": (
            _normalize_peak(_pluck(52, cents=-35.0)),
            52,
            CLASS_CORROBORATED,
        ),
        "attack_noise_m64": (
            _normalize_peak(_pluck(64) + attack),
            64,
            CLASS_CORROBORATED,
        ),
        "wrong_octave_up_selected_m52": (
            _normalize_peak(_pluck(64)),
            52,
            CLASS_NOT_CORROBORATED,
        ),
        "wrong_octave_down_selected_m64": (
            _normalize_peak(_pluck(52)),
            64,
            CLASS_NOT_CORROBORATED,
        ),
        "dominant_second_harmonic_m52": (
            _normalize_peak(
                _pluck(
                    52,
                    amplitudes=(0.05, 1.0, 0.05, 0.02, 0.01, 0.01),
                    decay_per_second=6.0,
                )
            ),
            52,
            CLASS_NOT_CORROBORATED,
        ),
        "stronger_semitone_m60": (
            _normalize_peak(0.4 * _pluck(60) + 1.0 * _pluck(61)),
            60,
            CLASS_NOT_CORROBORATED,
        ),
        "stronger_fifth_m60": (
            _normalize_peak(0.4 * _pluck(60) + 1.0 * _pluck(67)),
            60,
            CLASS_NOT_CORROBORATED,
        ),
        "equal_close_dyad_m60": (
            _normalize_peak(_pluck(60) + _pluck(61)),
            60,
            CLASS_NOT_CORROBORATED,
        ),
        "cluster_polyphony_m60": (
            _normalize_peak(_pluck(59) + _pluck(60) + _pluck(64)),
            60,
            CLASS_NOT_CORROBORATED,
        ),
        "silence_m60": (
            np.zeros(WINDOW_SAMPLES, dtype=np.float64),
            60,
            CLASS_INSUFFICIENT,
        ),
        "low_noise_m60": (
            1e-5 * low_noise_rng.standard_normal(WINDOW_SAMPLES),
            60,
            CLASS_INSUFFICIENT,
        ),
    }


def _pcm16_wav_bytes(values: np.ndarray) -> bytes:
    import io

    clipped = np.clip(np.asarray(values, dtype=np.float64), -1.0, 1.0)
    pcm = np.rint(clipped * 32767.0).astype("<i2")
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(pcm.tobytes())
    return buffer.getvalue()


def _decode_pcm16_fixture_bytes(data: bytes) -> np.ndarray:
    import io

    with wave.open(io.BytesIO(data), "rb") as handle:
        if (
            handle.getnchannels() != 1
            or handle.getsampwidth() != 2
            or handle.getframerate() != SAMPLE_RATE
            or handle.getnframes() != WINDOW_SAMPLES
        ):
            raise CorroborationError("CONTROLLED_FIXTURE_WAV_FORMAT_CHANGED")
        pcm = handle.readframes(WINDOW_SAMPLES)
    return np.frombuffer(pcm, dtype="<i2").astype(np.float64) / 32768.0


def write_controlled_fixtures(output_dir: Path) -> list[dict]:
    output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for name, (signal, selected_midi, expected_classification) in _fixture_signals().items():
        wav_bytes = _pcm16_wav_bytes(signal)
        path = output_dir / f"{name}.wav"
        path.write_bytes(wav_bytes)
        records.append(
            {
                "name": name,
                "selectedMidi": selected_midi,
                "expectedClassification": expected_classification,
                "pcm16WavSha256": sha256_bytes(wav_bytes),
                "sampleRate": SAMPLE_RATE,
                "sampleCount": WINDOW_SAMPLES,
                "channels": 1,
            }
        )
    return records


def load_fixture_manifest(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CorroborationError("FIXTURE_MANIFEST_LOAD_FAILED") from exc
    if value.get("contract") != FIXTURE_CONTRACT:
        raise CorroborationError("FIXTURE_MANIFEST_CONTRACT_CHANGED")
    if value.get("version") != 2:
        raise CorroborationError("FIXTURE_MANIFEST_VERSION_CHANGED")
    if value.get("fixtureCount") != len(value.get("fixtures", [])):
        raise CorroborationError("FIXTURE_MANIFEST_COUNT_CHANGED")
    return value


def run_controlled_fixture_suite(manifest_path: Path, output_dir: Path) -> dict:
    manifest = load_fixture_manifest(manifest_path)
    generated = write_controlled_fixtures(output_dir)
    expected_by_name = {item["name"]: item for item in manifest.get("fixtures", [])}
    generated_by_name = {item["name"]: item for item in generated}
    if set(expected_by_name) != set(generated_by_name):
        raise CorroborationError("FIXTURE_NAME_SET_CHANGED")
    rows = []
    for name in sorted(expected_by_name):
        expected = expected_by_name[name]
        actual = generated_by_name[name]
        for field in (
            "selectedMidi",
            "expectedClassification",
            "pcm16WavSha256",
            "sampleRate",
            "sampleCount",
            "channels",
        ):
            if actual.get(field) != expected.get(field):
                raise CorroborationError(f"FIXTURE_IDENTITY_CHANGED:{name}:{field}")
        data = (output_dir / f"{name}.wav").read_bytes()
        samples = _decode_pcm16_fixture_bytes(data)
        result = classify_window(samples, int(expected["selectedMidi"]))
        if result["classification"] != expected["expectedClassification"]:
            raise CorroborationError(
                f"FIXTURE_CLASSIFICATION_FAILED:{name}:"
                f"{result['classification']}!={expected['expectedClassification']}"
            )
        rows.append(
            {
                "name": name,
                "expectedClassification": expected["expectedClassification"],
                "observedClassification": result["classification"],
                "pcm16WavSha256": expected["pcm16WavSha256"],
                "channelAUniqueBest": (
                    None if result["channelA"] is None else result["channelA"]["uniqueBest"]
                ),
                "channelBUniqueBest": (
                    None if result["channelB"] is None else result["channelB"]["uniqueBest"]
                ),
            }
        )
    return {
        "contract": CONTRACT,
        "fixtureContract": FIXTURE_CONTRACT,
        "suiteStatus": "PASS",
        "fixtureCount": len(rows),
        "fixtures": rows,
        "policyBoundary": {
            "authorizedSongEvaluated": False,
            "referenceTabUsed": False,
            "professionalScorerUsed": False,
            "legacyV143ScorerImported": False,
            "goatResearchUsed": False,
            "basicPitchActivationUsed": False,
            "basicPitchDecisionSurfaceUsed": False,
            "basicPitchNoteSpanAmplitudeUsed": False,
            "basicPitchDecodedNoteEndUsed": False,
            "durationAuthorityChanged": False,
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "customerEligibleEvents": 0,
        },
    }


def _read_audio(path: Path) -> tuple[np.ndarray, int]:
    try:
        import soundfile as sf
    except Exception as exc:
        raise CorroborationError("SOUNDFILE_PACKAGE_REQUIRED") from exc
    try:
        audio, sample_rate = sf.read(str(path), dtype="float64", always_2d=True)
    except Exception as exc:
        raise CorroborationError("AUDIO_READ_FAILED") from exc
    if int(sample_rate) != SAMPLE_RATE:
        raise CorroborationError(f"SAMPLE_RATE_MUST_BE_{SAMPLE_RATE}")
    if audio.shape[0] < WINDOW_SAMPLES:
        raise CorroborationError("AUDIO_TOO_SHORT")
    mono = np.mean(audio, axis=1, dtype=np.float64)
    if not np.all(np.isfinite(mono)):
        raise CorroborationError("AUDIO_CONTAINS_NONFINITE_VALUES")
    return mono, int(sample_rate)


def _validate_evidence(evidence: dict) -> list[dict]:
    if evidence.get("contract") != EXPECTED_EVIDENCE_CONTRACT:
        raise CorroborationError("EVIDENCE_CONTRACT_CHANGED")
    if evidence.get("referenceBlind") is not True:
        raise CorroborationError("EVIDENCE_NOT_REFERENCE_BLIND")
    if evidence.get("structureFrozen") is not True:
        raise CorroborationError("EVIDENCE_STRUCTURE_NOT_FROZEN")
    if evidence.get("role") != "guitar":
        raise CorroborationError("EVIDENCE_ROLE_NOT_GUITAR")
    provenance = evidence.get("provenance", {})
    for field in (
        "referenceTabUsed",
        "professionalScorerUsed",
        "legacyV143ScorerImported",
        "modelNoteEndsUsedAsDuration",
    ):
        if provenance.get(field) is not False:
            raise CorroborationError(f"EVIDENCE_PROVENANCE_GUARD_CHANGED:{field}")
    rows = []
    for index, onset in enumerate(evidence.get("onsets", [])):
        source_start = _finite_float(onset.get("sourceStart"), f"onsets[{index}].sourceStart")
        midi_raw = onset.get("selectedMidi")
        if isinstance(midi_raw, bool) or not isinstance(midi_raw, int):
            raise CorroborationError(f"onsets[{index}].selectedMidi:INTEGER_REQUIRED")
        if not PLAYABLE_MIDI_MIN <= midi_raw <= PLAYABLE_MIDI_MAX:
            raise CorroborationError(f"onsets[{index}].selectedMidi:OUT_OF_RANGE")
        if onset.get("sourceEnd") is not None or onset.get("durationSeconds") is not None:
            raise CorroborationError(f"onsets[{index}]:DURATION_MUST_REMAIN_UNRESOLVED")
        onset_id = onset.get("onsetId")
        if not isinstance(onset_id, str) or not onset_id:
            raise CorroborationError(f"onsets[{index}].onsetId:NONEMPTY_STRING_REQUIRED")
        rows.append(
            {
                "onsetId": onset_id,
                "sourceStart": source_start,
                "selectedMidi": midi_raw,
            }
        )
    if not rows:
        raise CorroborationError("EVIDENCE_ONSETS_REQUIRED")
    return rows


def evaluate_evidence(stem_path: Path, evidence_path: Path) -> dict:
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    events = _validate_evidence(evidence)
    audio, sample_rate = _read_audio(stem_path)
    stem_sha256 = sha256_bytes(stem_path.read_bytes())
    results = []
    counts = {name: 0 for name in sorted(ALLOWED_CLASSES)}
    for event in events:
        start_sample = int(math.floor(event["sourceStart"] * sample_rate + 0.5))
        stop_sample = start_sample + WINDOW_SAMPLES
        if start_sample < 0 or stop_sample > audio.size:
            result = {
                "classification": CLASS_INSUFFICIENT,
                "selectedMidi": event["selectedMidi"],
                "competitorMidis": competitor_midis(event["selectedMidi"]),
                "windowRms": None,
                "channelA": None,
                "channelB": None,
                "reason": "FIXED_WINDOW_OUTSIDE_AUDIO",
            }
        else:
            result = classify_window(audio[start_sample:stop_sample], event["selectedMidi"])
        counts[result["classification"]] += 1
        results.append(
            {
                "onsetId": event["onsetId"],
                "sourceStart": event["sourceStart"],
                "selectedMidi": event["selectedMidi"],
                "startSample": start_sample,
                "stopSampleExclusive": stop_sample,
                **result,
            }
        )
    return {
        "contract": CONTRACT,
        "version": 2,
        "referenceBlind": True,
        "researchOnly": True,
        "methodFrozenBeforeAuthorizedSongEvaluation": True,
        "method": {
            "sampleRate": SAMPLE_RATE,
            "windowSamples": WINDOW_SAMPLES,
            "windowSeconds": WINDOW_SAMPLES / float(SAMPLE_RATE),
            "startSampleRule": "floor(sourceStartSeconds*44100+0.5)",
            "playableMidiRange": [PLAYABLE_MIDI_MIN, PLAYABLE_MIDI_MAX],
            "competitorOffsetsSemitones": list(COMPETITOR_OFFSETS),
            "minimumWindowRms": MIN_WINDOW_RMS,
            "scoreMarginThreshold": None,
            "winnerRule": "strict-greater-than; exact equality fails closed",
            "channelA": {
                "window": "numpy.hanning(16384)",
                "fftSize": FFT_SIZE,
                "spectrum": "rfft-normalized-magnitude",
                "fundamentalSearch": "maximum bin inside candidate semitone cell",
                "harmonicCount": HARMONIC_COUNT,
                "harmonicSampling": "nearest-bin-plus-immediate-neighbors maximum",
                "spectralLogFloor": SPECTRAL_LOG_FLOOR,
                "score": "mean-natural-log-four-coherent-harmonic-magnitudes",
            },
            "channelB": {
                "method": "YIN cumulative-mean normalized difference",
                "candidateLagSearch": "minimum CMND inside candidate semitone cell",
                "lagTieRule": "nearest equal-tempered center lag then smaller lag",
                "halfLagInterpolation": "linear",
                "score": "CMND(tau/2)-CMND(tau)",
            },
            "corroborationRule": "selected MIDI strict unique best in both channels; otherwise fail closed",
        },
        "identityProof": {
            "inputStemSha256": stem_sha256,
            "evidenceCanonicalSha256": hashlib.sha256(
                canonical_json(evidence).encode("utf-8")
            ).hexdigest(),
            "structureIdentity": evidence.get("structureIdentity"),
            "eventCount": len(events),
            "exactEventIdentityPreserved": True,
        },
        "summary": {
            "eventCount": len(results),
            "classificationCounts": counts,
        },
        "events": results,
        "hardGuards": {
            "invokesDemucs": False,
            "invokesBasicPitch": False,
            "usesBasicPitchActivations": False,
            "usesBasicPitchDecisionSurface": False,
            "usesBasicPitchNoteSpanAmplitude": False,
            "usesBasicPitchDecodedNoteEnd": False,
            "usesReferenceTab": False,
            "usesProfessionalScorer": False,
            "importsArchivedV143Logic": False,
            "usesGoatResearch": False,
            "usesGenericNextOnset": False,
            "usesSamePitchReattack": False,
            "changesPitchIdentity": False,
            "changesOnsetIdentity": False,
            "writesDurationSeconds": False,
            "writesSourceEnd": False,
            "ownsAdmissionDecision": False,
            "setsModelValidationComplete": False,
            "setsCustomerEligibility": False,
        },
        "policyBoundary": {
            "status": "INDEPENDENT_CORROBORATION_V2_RESEARCH_ONLY",
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "customerEligibleEvents": 0,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--fixture-manifest")
    parser.add_argument("--fixture-output-dir")
    parser.add_argument("--input-stem")
    parser.add_argument("--evidence")
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        if not args.fixture_manifest or not args.fixture_output_dir:
            raise CorroborationError("SELF_TEST_REQUIRES_FIXTURE_MANIFEST_AND_OUTPUT_DIR")
        report = run_controlled_fixture_suite(
            Path(args.fixture_manifest),
            Path(args.fixture_output_dir),
        )
        print(canonical_json(report))
        return 0
    if not args.input_stem or not args.evidence or not args.output:
        raise CorroborationError("USAGE_REQUIRES_INPUT_STEM_EVIDENCE_AND_OUTPUT")
    result = evaluate_evidence(Path(args.input_stem), Path(args.evidence))
    Path(args.output).write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        canonical_json(
            {
                "contract": CONTRACT,
                "output": args.output,
                "summary": result["summary"],
                "policyBoundary": result["policyBoundary"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CorroborationError as exc:
        print(f"INDEPENDENT_CORROBORATION_ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2)
