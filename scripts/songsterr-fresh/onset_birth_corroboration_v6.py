#!/usr/bin/env python3
"""Synthetic-development onset-synchronous complex-harmonic corroboration V6.

Reference-blind research only. Authorized for synthetic/metadata development by
SONGSTERR_FRESH_SUCCESSOR_RESEARCH_CHARTER_V6.md. No real-corpus scoring mode
is exposed by this module.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import nnls

CONTRACT = "songsterr-fresh-onset-birth-complex-harmonic-corroboration-research-v6"
FIXTURE_CONTRACT = "songsterr-fresh-v6-onset-birth-synthetic-fixtures-v1"
VERSION = 6

SAMPLE_RATE = 44100
FRAME_SAMPLES = 2048
HOP_SAMPLES = 256
FFT_SIZE = 8192
FRAME_END_OFFSETS = tuple(range(-6 * HOP_SAMPLES, 7 * HOP_SAMPLES, HOP_SAMPLES))
POST_END_MAX = 4 * HOP_SAMPLES

PLAYABLE_MIDI_MIN = 40
PLAYABLE_MIDI_MAX = 88
HARMONIC_COUNT_MAX = 6

MIN_ANALYSIS_RMS = 1e-5
MIN_INNOVATION_ENERGY = 1e-6
TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN = 0.20
NECESSITY_FRACTION_MIN = 0.01

CLASS_CORROBORATED = "onset-birth-corroborated-candidate"
CLASS_NOT_CORROBORATED = "not-onset-birth-corroborated"
CLASS_INSUFFICIENT = "insufficient-evidence"


class CorroborationError(RuntimeError):
    pass


def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def midi_to_hz(midi: float) -> float:
    return 440.0 * (2.0 ** ((float(midi) - 69.0) / 12.0))


def _frame_complex_spectra(audio: np.ndarray, onset_sample: int) -> tuple[np.ndarray, np.ndarray]:
    frames: list[np.ndarray] = []
    for end_offset in FRAME_END_OFFSETS:
        stop = onset_sample + int(end_offset)
        start = stop - FRAME_SAMPLES
        if start < 0 or stop > audio.size:
            raise CorroborationError("REQUIRED_PRE_POST_CONTEXT_OUTSIDE_AUDIO")
        frame = np.asarray(audio[start:stop], dtype=np.float64)
        if frame.size != FRAME_SAMPLES or not np.all(np.isfinite(frame)):
            raise CorroborationError("FINITE_EXACT_FRAME_REQUIRED")
        demeaned = frame - float(np.mean(frame))
        frames.append(np.fft.rfft(demeaned * np.hanning(FRAME_SAMPLES), n=FFT_SIZE))
    return np.asarray(frames, dtype=np.complex128), np.asarray(FRAME_END_OFFSETS, dtype=np.int64)


def _complex_prediction_deviation(spectra: np.ndarray) -> np.ndarray:
    if spectra.ndim != 2 or spectra.shape[0] < 3:
        raise CorroborationError("THREE_OR_MORE_COMPLEX_FRAMES_REQUIRED")
    magnitude = np.abs(spectra)
    phase = np.angle(spectra)
    deviation = np.zeros_like(magnitude, dtype=np.float64)
    for index in range(2, spectra.shape[0]):
        predicted = magnitude[index - 1] * np.exp(1j * (2.0 * phase[index - 1] - phase[index - 2]))
        deviation[index] = np.abs(spectra[index] - predicted)
    if not np.all(np.isfinite(deviation)):
        raise CorroborationError("NONFINITE_COMPLEX_DEVIATION")
    return deviation


def _onset_innovation_spectrum(audio: np.ndarray, onset_sample: int) -> dict:
    spectra, offsets = _frame_complex_spectra(audio, onset_sample)
    deviation = _complex_prediction_deviation(spectra)

    frame_rms = []
    for end_offset in FRAME_END_OFFSETS:
        stop = onset_sample + int(end_offset)
        frame = np.asarray(audio[stop - FRAME_SAMPLES : stop], dtype=np.float64)
        demeaned = frame - float(np.mean(frame))
        frame_rms.append(float(np.sqrt(np.mean(np.square(demeaned)))))
    analysis_rms = max(frame_rms) if frame_rms else 0.0
    if not math.isfinite(analysis_rms) or analysis_rms < MIN_ANALYSIS_RMS:
        return {"status": "INSUFFICIENT_LOW_AUDIO_SUPPORT", "analysisRms": analysis_rms}

    indices = np.arange(offsets.size, dtype=np.int64)
    pre = indices[(offsets <= 0) & (indices >= 2)]
    post = indices[(offsets > 0) & (offsets <= POST_END_MAX)]
    if pre.size == 0 or post.size == 0:
        raise CorroborationError("PRE_POST_NOVELTY_FRAMES_REQUIRED")

    pre_max = np.max(deviation[pre], axis=0)
    post_max = np.max(deviation[post], axis=0)
    innovation = np.maximum(0.0, post_max - pre_max)
    energy = float(np.linalg.norm(innovation))
    if not math.isfinite(energy) or energy < MIN_INNOVATION_ENERGY:
        return {
            "status": "INSUFFICIENT_LOW_ONSET_INNOVATION",
            "analysisRms": analysis_rms,
            "innovationEnergy": energy,
        }
    return {
        "status": "OK",
        "analysisRms": analysis_rms,
        "innovationEnergy": energy,
        "innovation": innovation,
    }


def _candidate_template(midi: int, innovation: np.ndarray, frequencies: np.ndarray) -> dict:
    low_hz = midi_to_hz(float(midi) - 0.5)
    high_hz = midi_to_hz(float(midi) + 0.5)
    fundamental_indices = np.flatnonzero((frequencies >= low_hz) & (frequencies < high_hz))
    if fundamental_indices.size == 0:
        return {"valid": False, "reason": "NO_FUNDAMENTAL_CELL_BIN"}

    local = innovation[fundamental_indices]
    fundamental_bin = int(fundamental_indices[int(np.argmax(local))])
    fundamental_hz = float(frequencies[fundamental_bin])
    if not math.isfinite(fundamental_hz) or fundamental_hz <= 0.0:
        return {"valid": False, "reason": "INVALID_FUNDAMENTAL_FREQUENCY"}

    bins: list[int] = []
    weights: list[float] = []
    observed: list[float] = []
    for harmonic in range(1, HARMONIC_COUNT_MAX + 1):
        target_hz = float(harmonic) * fundamental_hz
        if target_hz >= SAMPLE_RATE / 2.0:
            break
        position = target_hz * float(FFT_SIZE) / float(SAMPLE_RATE)
        nearest = int(math.floor(position + 0.5))
        left = max(0, nearest - 1)
        right = min(innovation.size - 1, nearest + 1)
        search = innovation[left : right + 1]
        chosen = int(left + int(np.argmax(search)))
        bins.append(chosen)
        weights.append(1.0 / float(harmonic))
        observed.append(float(innovation[chosen]))

    if len(bins) < 3:
        return {"valid": False, "reason": "FEWER_THAN_THREE_HARMONICS"}
    if not all(math.isfinite(x) and x >= 0.0 for x in observed):
        return {"valid": False, "reason": "NONFINITE_HARMONIC_INNOVATION"}

    maximum = max(observed)
    ratio = 0.0 if maximum <= 0.0 else float(observed[0] / maximum)
    if ratio < TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN:
        return {
            "valid": False,
            "reason": "FUNDAMENTAL_ONSET_INNOVATION_TOO_WEAK",
            "fundamentalToMaxHarmonicInnovationRatio": ratio,
        }

    norm = float(np.linalg.norm(np.asarray(weights, dtype=np.float64)))
    if not math.isfinite(norm) or norm <= 0.0:
        return {"valid": False, "reason": "INVALID_TEMPLATE_NORM"}
    normalized = [float(weight / norm) for weight in weights]
    return {
        "valid": True,
        "midi": int(midi),
        "fundamentalBin": fundamental_bin,
        "fundamentalHz": fundamental_hz,
        "bins": bins,
        "weights": normalized,
        "observedHarmonicInnovation": observed,
        "fundamentalToMaxHarmonicInnovationRatio": ratio,
    }


def _fit_onset_birth(audio: np.ndarray, onset_sample: int, selected_midi: int) -> dict:
    onset = _onset_innovation_spectrum(audio, onset_sample)
    if onset["status"] != "OK":
        return {
            "status": onset["status"],
            "analysisRms": onset.get("analysisRms"),
            "innovationEnergy": onset.get("innovationEnergy"),
            "selectedMidi": selected_midi,
        }

    innovation = onset["innovation"]
    frequencies = np.fft.rfftfreq(FFT_SIZE, d=1.0 / float(SAMPLE_RATE))
    templates: dict[int, dict] = {
        midi: _candidate_template(midi, innovation, frequencies)
        for midi in range(PLAYABLE_MIDI_MIN, PLAYABLE_MIDI_MAX + 1)
    }
    valid_midis = sorted(midi for midi, row in templates.items() if row.get("valid"))
    if selected_midi not in valid_midis:
        return {
            "status": "OK_SELECTED_TEMPLATE_NOT_PHYSICALLY_PLAUSIBLE",
            "analysisRms": onset["analysisRms"],
            "innovationEnergy": onset["innovationEnergy"],
            "selectedMidi": selected_midi,
            "selectedCoefficient": 0.0,
            "necessityFraction": 0.0,
            "passed": False,
        }

    feature_bins = sorted({bin_index for midi in valid_midis for bin_index in templates[midi]["bins"]})
    if not feature_bins:
        return {"status": "INSUFFICIENT_NO_FEATURE_BINS", "selectedMidi": selected_midi}
    row_for_bin = {bin_index: row for row, bin_index in enumerate(feature_bins)}
    observed = np.asarray([innovation[b] for b in feature_bins], dtype=np.float64)
    feature_energy = float(np.linalg.norm(observed))
    if not math.isfinite(feature_energy) or feature_energy < MIN_INNOVATION_ENERGY:
        return {"status": "INSUFFICIENT_LOW_FEATURE_ENERGY", "selectedMidi": selected_midi}

    dictionary = np.zeros((len(feature_bins), len(valid_midis)), dtype=np.float64)
    for column, midi in enumerate(valid_midis):
        template = templates[midi]
        for bin_index, weight in zip(template["bins"], template["weights"]):
            dictionary[row_for_bin[bin_index], column] += float(weight)

    try:
        coefficients, full_residual = nnls(dictionary, observed)
    except Exception as exc:
        return {"status": "INSUFFICIENT_NNLS_FULL_FAILED", "selectedMidi": selected_midi, "errorType": type(exc).__name__}

    selected_column = valid_midis.index(selected_midi)
    reduced = np.delete(dictionary, selected_column, axis=1)
    if reduced.shape[1] == 0:
        return {"status": "INSUFFICIENT_REDUCED_DICTIONARY_EMPTY", "selectedMidi": selected_midi}
    try:
        _reduced_coefficients, without_residual = nnls(reduced, observed)
    except Exception as exc:
        return {"status": "INSUFFICIENT_NNLS_REDUCED_FAILED", "selectedMidi": selected_midi, "errorType": type(exc).__name__}

    selected_coefficient = float(coefficients[selected_column])
    full_residual = float(full_residual)
    without_residual = float(without_residual)
    necessity_fraction = float((without_residual - full_residual) / max(feature_energy, 1e-15))
    if not all(math.isfinite(value) for value in (selected_coefficient, full_residual, without_residual, necessity_fraction)):
        return {"status": "INSUFFICIENT_NONFINITE_FIT", "selectedMidi": selected_midi}

    passed = bool(selected_coefficient > 0.0 and necessity_fraction >= NECESSITY_FRACTION_MIN)
    return {
        "status": "OK",
        "selectedMidi": selected_midi,
        "analysisRms": onset["analysisRms"],
        "innovationEnergy": onset["innovationEnergy"],
        "featureEnergy": feature_energy,
        "validCandidateCount": len(valid_midis),
        "selectedCoefficient": selected_coefficient,
        "fullResidual": full_residual,
        "withoutSelectedResidual": without_residual,
        "necessityFraction": necessity_fraction,
        "fundamentalToMaxHarmonicInnovationRatio": templates[selected_midi]["fundamentalToMaxHarmonicInnovationRatio"],
        "passed": passed,
    }


def classify_audio_event(audio: np.ndarray, onset_sample: int, selected_midi: int) -> dict:
    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        raise CorroborationError("SELECTED_MIDI_INTEGER_REQUIRED")
    selected_midi = int(selected_midi)
    if not PLAYABLE_MIDI_MIN <= selected_midi <= PLAYABLE_MIDI_MAX:
        raise CorroborationError("SELECTED_MIDI_OUTSIDE_PLAYABLE_RANGE")
    if isinstance(onset_sample, bool) or not isinstance(onset_sample, (int, np.integer)):
        raise CorroborationError("ONSET_SAMPLE_INTEGER_REQUIRED")
    onset_sample = int(onset_sample)

    values = np.asarray(audio, dtype=np.float64)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise CorroborationError("FINITE_MONO_AUDIO_REQUIRED")
    if onset_sample < 0:
        return {"classification": CLASS_INSUFFICIENT, "selectedMidi": selected_midi, "reason": "ONSET_BEFORE_AUDIO"}

    try:
        fit = _fit_onset_birth(values, onset_sample, selected_midi)
    except CorroborationError as exc:
        return {"classification": CLASS_INSUFFICIENT, "selectedMidi": selected_midi, "reason": str(exc)}

    if fit["status"].startswith("INSUFFICIENT"):
        classification = CLASS_INSUFFICIENT
    elif bool(fit.get("passed")):
        classification = CLASS_CORROBORATED
    else:
        classification = CLASS_NOT_CORROBORATED
    return {"classification": classification, "selectedMidi": selected_midi, "reason": fit["status"], "fit": fit}


def _synth_events(duration_seconds: float, events: list[dict], seed: int = 0) -> tuple[np.ndarray, np.random.Generator]:
    sample_count = int(round(float(duration_seconds) * SAMPLE_RATE))
    audio = np.zeros(sample_count, dtype=np.float64)
    for event_index, event in enumerate(events):
        onset = int(round(float(event["onsetSeconds"]) * SAMPLE_RATE))
        stop_seconds = float(event.get("stopSeconds", duration_seconds))
        stop = min(sample_count, int(round(stop_seconds * SAMPLE_RATE)))
        if stop <= onset:
            continue
        midi = float(event["midi"])
        cents = float(event.get("cents", 0.0))
        amplitude = float(event.get("amplitude", 1.0))
        decay = float(event.get("decayPerSecond", 1.5))
        fundamental = midi_to_hz(midi + cents / 100.0)
        time = np.arange(stop - onset, dtype=np.float64) / float(SAMPLE_RATE)
        envelope = np.exp(-decay * time)
        harmonic_amplitudes = event.get("harmonicAmplitudes", [1.0 / float(harmonic) for harmonic in range(1, HARMONIC_COUNT_MAX + 1)])
        event_audio = np.zeros(stop - onset, dtype=np.float64)
        base_phase = float(event.get("phase", 0.11 * (event_index + 1)))
        for harmonic, harmonic_amplitude in enumerate(harmonic_amplitudes, start=1):
            frequency = float(harmonic) * fundamental
            if frequency >= SAMPLE_RATE / 2.0:
                break
            event_audio += float(harmonic_amplitude) * np.sin(2.0 * math.pi * frequency * time + base_phase * harmonic)
        audio[onset:stop] += amplitude * event_audio * envelope
    return audio, np.random.default_rng(int(seed))


def _fixture_audio(fixture: dict) -> np.ndarray:
    duration = float(fixture.get("durationSeconds", 1.0))
    audio, rng = _synth_events(duration, list(fixture.get("events", [])), int(fixture.get("seed", 0)))

    transient = fixture.get("transient")
    if transient:
        onset = int(round(float(transient["onsetSeconds"]) * SAMPLE_RATE))
        length = int(round(float(transient.get("durationSeconds", 0.03)) * SAMPLE_RATE))
        stop = min(audio.size, onset + length)
        if 0 <= onset < stop:
            indices = np.arange(stop - onset, dtype=np.float64)
            envelope = np.exp(-indices / max(1.0, float(transient.get("decaySeconds", 0.006)) * SAMPLE_RATE))
            audio[onset:stop] += float(transient.get("amplitude", 0.5)) * envelope * rng.standard_normal(stop - onset)

    noise_amplitude = float(fixture.get("noiseAmplitude", 0.0))
    if noise_amplitude > 0.0:
        audio += noise_amplitude * rng.standard_normal(audio.size)

    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak > 0.95:
        audio = audio * (0.95 / peak)
    return np.asarray(audio, dtype=np.float64)


def run_self_test(manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("contract") != FIXTURE_CONTRACT:
        raise CorroborationError("FIXTURE_MANIFEST_CONTRACT_CHANGED")

    rows = []
    counts: dict[str, int] = {}
    for fixture in manifest["fixtures"]:
        audio = _fixture_audio(fixture)
        selected_midi = int(fixture["selectedMidi"])
        onset_sample = int(round(float(fixture["onsetSeconds"]) * SAMPLE_RATE))
        result = classify_audio_event(audio, onset_sample, selected_midi)
        actual = result["classification"]
        expected = fixture["expectedClassification"]
        counts[actual] = counts.get(actual, 0) + 1
        row = {
            "id": fixture["id"],
            "expected": expected,
            "actual": actual,
            "selectedMidi": result["selectedMidi"],
            "audioSha256": sha256_bytes(np.asarray(audio, dtype="<f8").tobytes()),
            "necessityFraction": result.get("fit", {}).get("necessityFraction"),
            "reason": result.get("reason"),
        }
        rows.append(row)
        if actual != expected:
            raise CorroborationError(f"SYNTHETIC_CLASSIFICATION_CHANGED:{fixture['id']}:{actual}!={expected}")
        if result["selectedMidi"] != selected_midi:
            raise CorroborationError(f"EVENT_MIDI_IDENTITY_CHANGED:{fixture['id']}")

    return {
        "contract": CONTRACT,
        "version": VERSION,
        "fixtureContract": FIXTURE_CONTRACT,
        "fixtureCount": len(rows),
        "classificationCounts": dict(sorted(counts.items())),
        "constants": {
            "sampleRate": SAMPLE_RATE,
            "frameSamples": FRAME_SAMPLES,
            "hopSamples": HOP_SAMPLES,
            "fftSize": FFT_SIZE,
            "frameEndOffsets": list(FRAME_END_OFFSETS),
            "postEndMax": POST_END_MAX,
            "harmonicCountMax": HARMONIC_COUNT_MAX,
            "minimumAnalysisRms": MIN_ANALYSIS_RMS,
            "minimumInnovationEnergy": MIN_INNOVATION_ENERGY,
            "templateFundamentalToMaxHarmonicInnovationMin": TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN,
            "necessityFractionMin": NECESSITY_FRACTION_MIN,
        },
        "results": rows,
        "policyBoundary": {
            "realCorpusEvaluated": False,
            "protectedSongUsed": False,
            "modelInferenceInvoked": False,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--fixture-manifest")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        if not args.fixture_manifest:
            raise CorroborationError("SELF_TEST_REQUIRES_FIXTURE_MANIFEST")
        print(canonical_json(run_self_test(Path(args.fixture_manifest))))
        return 0
    raise CorroborationError("NO_STANDALONE_REAL_CORPUS_MODE_AUTHORIZED")


if __name__ == "__main__":
    raise SystemExit(main())
