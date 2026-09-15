#!/usr/bin/env python3
"""One-sided clip-start pitch-presence corroboration.

This module exists only for proposals too close to the beginning of an audio
clip to have the genuine pre-onset context required by the frozen V6 onset-
birth classifier. It never fabricates pre-context. It uses only genuine
post-onset audio and inherits the frozen V6 spectral/harmonic constants.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.optimize import nnls

from onset_birth_corroboration_v6 import (
    CLASS_CORROBORATED,
    CLASS_INSUFFICIENT,
    CLASS_NOT_CORROBORATED,
    FFT_SIZE,
    HARMONIC_COUNT_MAX,
    MIN_ANALYSIS_RMS,
    MIN_INNOVATION_ENERGY,
    NECESSITY_FRACTION_MIN,
    PLAYABLE_MIDI_MAX,
    PLAYABLE_MIDI_MIN,
    SAMPLE_RATE,
    _candidate_template,
    midi_to_hz,
)

METHOD = "clip-start-post-spectrum-harmonic-necessity-v1"
WINDOW_SAMPLES = FFT_SIZE
HARMONIC_MATCH_TOLERANCE_CENTS = 50.0


class ClipStartPresenceError(RuntimeError):
    pass


def _finite_audio(audio: np.ndarray) -> np.ndarray:
    values = np.asarray(audio, dtype=np.float64)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise ClipStartPresenceError("FINITE_MONO_AUDIO_REQUIRED")
    return values


def _necessity_for_column(
    dictionary: np.ndarray,
    observed: np.ndarray,
    feature_energy: float,
    full_residual: float,
    column: int,
) -> tuple[float | None, float | None, str | None]:
    reduced = np.delete(dictionary, column, axis=1)
    if reduced.shape[1] == 0:
        return None, None, "INSUFFICIENT_REDUCED_DICTIONARY_EMPTY"
    try:
        _coefficients, without_residual = nnls(reduced, observed)
    except Exception as exc:
        return None, None, f"INSUFFICIENT_NNLS_REDUCED_FAILED:{type(exc).__name__}"
    without_residual = float(without_residual)
    necessity = float((without_residual - full_residual) / max(feature_energy, 1e-15))
    if not math.isfinite(without_residual) or not math.isfinite(necessity):
        return None, None, "INSUFFICIENT_NONFINITE_REDUCED_FIT"
    return necessity, without_residual, None


def classify_clip_start_pitch_presence(audio: np.ndarray, onset_sample: int, selected_midi: int) -> dict[str, Any]:
    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        raise ClipStartPresenceError("SELECTED_MIDI_INTEGER_REQUIRED")
    selected_midi = int(selected_midi)
    if not PLAYABLE_MIDI_MIN <= selected_midi <= PLAYABLE_MIDI_MAX:
        raise ClipStartPresenceError("SELECTED_MIDI_OUTSIDE_PLAYABLE_RANGE")
    if isinstance(onset_sample, bool) or not isinstance(onset_sample, (int, np.integer)):
        raise ClipStartPresenceError("ONSET_SAMPLE_INTEGER_REQUIRED")
    onset_sample = int(onset_sample)
    if onset_sample < 0:
        return {
            "classification": CLASS_INSUFFICIENT,
            "selectedMidi": selected_midi,
            "reason": "ONSET_BEFORE_AUDIO",
        }

    values = _finite_audio(audio)
    stop = onset_sample + WINDOW_SAMPLES
    if stop > values.size:
        return {
            "classification": CLASS_INSUFFICIENT,
            "selectedMidi": selected_midi,
            "reason": "BOUNDARY_REQUIRED_POST_CONTEXT_OUTSIDE_AUDIO",
            "fit": {
                "windowSamples": WINDOW_SAMPLES,
                "availablePostSamples": max(0, int(values.size - onset_sample)),
            },
        }

    frame = np.asarray(values[onset_sample:stop], dtype=np.float64)
    if frame.size != WINDOW_SAMPLES or not np.all(np.isfinite(frame)):
        return {
            "classification": CLASS_INSUFFICIENT,
            "selectedMidi": selected_midi,
            "reason": "BOUNDARY_FINITE_EXACT_POST_FRAME_REQUIRED",
        }

    demeaned = frame - float(np.mean(frame))
    analysis_rms = float(np.sqrt(np.mean(np.square(demeaned))))
    if not math.isfinite(analysis_rms) or analysis_rms < MIN_ANALYSIS_RMS:
        return {
            "classification": CLASS_INSUFFICIENT,
            "selectedMidi": selected_midi,
            "reason": "BOUNDARY_INSUFFICIENT_LOW_AUDIO_SUPPORT",
            "fit": {
                "analysisRms": analysis_rms,
                "windowSamples": WINDOW_SAMPLES,
            },
        }

    spectrum = np.abs(np.fft.rfft(demeaned * np.hanning(WINDOW_SAMPLES), n=FFT_SIZE))
    if spectrum.ndim != 1 or not np.all(np.isfinite(spectrum)):
        return {
            "classification": CLASS_INSUFFICIENT,
            "selectedMidi": selected_midi,
            "reason": "BOUNDARY_NONFINITE_SPECTRUM",
        }

    frequencies = np.fft.rfftfreq(FFT_SIZE, d=1.0 / float(SAMPLE_RATE))
    templates: dict[int, dict[str, Any]] = {
        midi: _candidate_template(midi, spectrum, frequencies)
        for midi in range(PLAYABLE_MIDI_MIN, PLAYABLE_MIDI_MAX + 1)
    }
    valid_midis = sorted(midi for midi, row in templates.items() if row.get("valid"))
    if selected_midi not in valid_midis:
        return {
            "classification": CLASS_NOT_CORROBORATED,
            "selectedMidi": selected_midi,
            "reason": "BOUNDARY_SELECTED_TEMPLATE_NOT_PHYSICALLY_PLAUSIBLE",
            "fit": {
                "analysisRms": analysis_rms,
                "windowSamples": WINDOW_SAMPLES,
                "selectedTemplate": templates.get(selected_midi),
                "selectedCoefficient": 0.0,
                "necessityFraction": 0.0,
                "dominantHarmonicOwner": False,
                "passed": False,
            },
        }

    feature_bins = sorted({bin_index for midi in valid_midis for bin_index in templates[midi]["bins"]})
    if not feature_bins:
        return {
            "classification": CLASS_INSUFFICIENT,
            "selectedMidi": selected_midi,
            "reason": "BOUNDARY_INSUFFICIENT_NO_FEATURE_BINS",
        }

    row_for_bin = {bin_index: row for row, bin_index in enumerate(feature_bins)}
    observed = np.asarray([spectrum[bin_index] for bin_index in feature_bins], dtype=np.float64)
    feature_energy = float(np.linalg.norm(observed))
    if not math.isfinite(feature_energy) or feature_energy < MIN_INNOVATION_ENERGY:
        return {
            "classification": CLASS_INSUFFICIENT,
            "selectedMidi": selected_midi,
            "reason": "BOUNDARY_INSUFFICIENT_LOW_FEATURE_ENERGY",
            "fit": {
                "analysisRms": analysis_rms,
                "featureEnergy": feature_energy,
                "windowSamples": WINDOW_SAMPLES,
            },
        }

    dictionary = np.zeros((len(feature_bins), len(valid_midis)), dtype=np.float64)
    for column, midi in enumerate(valid_midis):
        template = templates[midi]
        for bin_index, weight in zip(template["bins"], template["weights"]):
            dictionary[row_for_bin[bin_index], column] += float(weight)

    try:
        coefficients, full_residual = nnls(dictionary, observed)
    except Exception as exc:
        return {
            "classification": CLASS_INSUFFICIENT,
            "selectedMidi": selected_midi,
            "reason": f"BOUNDARY_INSUFFICIENT_NNLS_FULL_FAILED:{type(exc).__name__}",
        }

    full_residual = float(full_residual)
    selected_column = valid_midis.index(selected_midi)
    selected_coefficient = float(coefficients[selected_column])
    selected_necessity, without_selected_residual, selected_error = _necessity_for_column(
        dictionary,
        observed,
        feature_energy,
        full_residual,
        selected_column,
    )
    if selected_error is not None or selected_necessity is None or without_selected_residual is None:
        return {
            "classification": CLASS_INSUFFICIENT,
            "selectedMidi": selected_midi,
            "reason": f"BOUNDARY_{selected_error or 'INSUFFICIENT_SELECTED_NECESSITY'}",
        }

    harmonic_owners: list[dict[str, Any]] = []
    for lower_midi in valid_midis:
        if lower_midi >= selected_midi:
            continue
        lower_column = valid_midis.index(lower_midi)
        lower_coefficient = float(coefficients[lower_column])
        if lower_coefficient <= 0.0:
            continue
        for harmonic in range(2, HARMONIC_COUNT_MAX + 1):
            harmonic_midi = float(lower_midi) + 12.0 * math.log2(float(harmonic))
            cents_from_selected = 100.0 * (float(selected_midi) - harmonic_midi)
            if abs(cents_from_selected) > HARMONIC_MATCH_TOLERANCE_CENTS:
                continue
            owner_necessity, owner_without_residual, owner_error = _necessity_for_column(
                dictionary,
                observed,
                feature_energy,
                full_residual,
                lower_column,
            )
            if owner_error is not None or owner_necessity is None or owner_without_residual is None:
                continue
            owner_qualifies = owner_necessity >= NECESSITY_FRACTION_MIN
            dominant = bool(owner_qualifies and owner_necessity >= selected_necessity)
            harmonic_owners.append({
                "lowerMidi": lower_midi,
                "harmonic": harmonic,
                "centsFromSelected": cents_from_selected,
                "coefficient": lower_coefficient,
                "necessityFraction": owner_necessity,
                "withoutOwnerResidual": owner_without_residual,
                "ownerQualifies": owner_qualifies,
                "dominant": dominant,
            })

    dominant_owners = [row for row in harmonic_owners if row["dominant"]]
    passed = bool(
        selected_coefficient > 0.0
        and selected_necessity >= NECESSITY_FRACTION_MIN
        and not dominant_owners
    )
    reason = "OK" if passed else "BOUNDARY_NOT_NECESSARY_OR_DOMINANT_HARMONIC_OWNER"
    classification = CLASS_CORROBORATED if passed else CLASS_NOT_CORROBORATED

    return {
        "classification": classification,
        "selectedMidi": selected_midi,
        "reason": reason,
        "fit": {
            "analysisRms": analysis_rms,
            "featureEnergy": feature_energy,
            "validCandidateCount": len(valid_midis),
            "selectedCoefficient": selected_coefficient,
            "fullResidual": full_residual,
            "withoutSelectedResidual": without_selected_residual,
            "necessityFraction": selected_necessity,
            "fundamentalToMaxHarmonicRatio": templates[selected_midi].get("fundamentalToMaxHarmonicInnovationRatio"),
            "harmonicOwners": harmonic_owners,
            "dominantHarmonicOwners": dominant_owners,
            "dominantHarmonicOwner": bool(dominant_owners),
            "windowSamples": WINDOW_SAMPLES,
            "harmonicMatchToleranceCents": HARMONIC_MATCH_TOLERANCE_CENTS,
            "passed": passed,
        },
    }
