#!/usr/bin/env python3
"""Research-only one-sided clip-start adapter for frozen V7/V3 evidence.

This module preserves the frozen V2 no-fabrication boundary signal construction:
exactly 8192 genuine post-onset samples, demean + Hann, 8192-point real-FFT
magnitude. The resulting nonnegative spectrum is explicitly treated as
clip-start post-spectrum evidence on the frozen FFT grid; it is not described
as pre/post onset innovation.

Frozen by:
  docs/checkpoints/SONGSTERR_FRESH_V7_REAL_EVALUATION_PRE.md
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as frozen_v6
import onset_birth_corroboration_v7 as frozen_v7

CONTRACT = "songsterr-fresh-clip-start-post-spectrum-v7-research"
VERSION = 7
METHOD = "clip-start-post-spectrum-evidence-v7"
WINDOW_SAMPLES = frozen_v6.FFT_SIZE

# A finite spectrum that reaches the frozen V7/V3 composite owns a decision.
# These statuses indicate unavailable/malformed evidence rather than a finite
# physical rejection and therefore remain insufficient.
_UNAVAILABLE_V7_STATUSES = {
    "FROZEN_DEPENDENCY_CONTRACT_MISMATCH",
    "MIDI_INTEGER_REQUIRED",
    "MIDI_OUTSIDE_PLAYABLE_RANGE",
    "INPUT_COERCION_FAILED",
    "SPECTRUM_AND_FREQUENCIES_MUST_BE_1D",
    "SPECTRUM_FREQUENCY_SHAPE_MISMATCH",
    "FREQUENCY_GRID_MISSING_BINS",
    "NONFINITE_SPECTRUM_OR_FREQUENCY",
    "NEGATIVE_INNOVATION_NOT_ALLOWED",
    "FREQUENCY_GRID_MISMATCH",
    "INSUFFICIENT_INNOVATION",
    "V3_RESULT_NOT_MAPPING",
}


class ClipStartV7Error(RuntimeError):
    pass


def _failure(classification: str, selected_midi: Any, reason: str, **fit: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "classification": classification,
        "selectedMidi": selected_midi,
        "reason": reason,
        "method": METHOD,
        "evidenceKind": "clip-start-post-spectrum-evidence",
    }
    if fit:
        row["fit"] = fit
    return row


def classify_clip_start_pitch_presence_v7(
    audio: np.ndarray | list[float],
    onset_sample: int,
    selected_midi: int,
) -> dict[str, Any]:
    """Classify one clip-start proposal with frozen V7/V3 evidence logic."""

    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        raise ClipStartV7Error("SELECTED_MIDI_INTEGER_REQUIRED")
    selected_midi = int(selected_midi)
    if not frozen_v6.PLAYABLE_MIDI_MIN <= selected_midi <= frozen_v6.PLAYABLE_MIDI_MAX:
        raise ClipStartV7Error("SELECTED_MIDI_OUTSIDE_PLAYABLE_RANGE")
    if isinstance(onset_sample, bool) or not isinstance(onset_sample, (int, np.integer)):
        raise ClipStartV7Error("ONSET_SAMPLE_INTEGER_REQUIRED")
    onset_sample = int(onset_sample)
    if onset_sample < 0:
        return _failure(
            frozen_v6.CLASS_INSUFFICIENT,
            selected_midi,
            "ONSET_BEFORE_AUDIO",
        )

    try:
        values = np.asarray(audio, dtype=np.float64)
    except Exception as exc:
        return _failure(
            frozen_v6.CLASS_INSUFFICIENT,
            selected_midi,
            "AUDIO_COERCION_FAILED",
            errorType=type(exc).__name__,
        )
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        return _failure(
            frozen_v6.CLASS_INSUFFICIENT,
            selected_midi,
            "FINITE_MONO_AUDIO_REQUIRED",
        )

    stop = onset_sample + WINDOW_SAMPLES
    if stop > values.size:
        return _failure(
            frozen_v6.CLASS_INSUFFICIENT,
            selected_midi,
            "BOUNDARY_REQUIRED_POST_CONTEXT_OUTSIDE_AUDIO",
            windowSamples=WINDOW_SAMPLES,
            availablePostSamples=max(0, int(values.size - onset_sample)),
        )

    frame = np.asarray(values[onset_sample:stop], dtype=np.float64)
    if frame.size != WINDOW_SAMPLES or not np.all(np.isfinite(frame)):
        return _failure(
            frozen_v6.CLASS_INSUFFICIENT,
            selected_midi,
            "BOUNDARY_FINITE_EXACT_POST_FRAME_REQUIRED",
            windowSamples=WINDOW_SAMPLES,
        )

    demeaned = frame - float(np.mean(frame))
    analysis_rms = float(np.sqrt(np.mean(np.square(demeaned))))
    if not math.isfinite(analysis_rms) or analysis_rms < frozen_v6.MIN_ANALYSIS_RMS:
        return _failure(
            frozen_v6.CLASS_INSUFFICIENT,
            selected_midi,
            "BOUNDARY_INSUFFICIENT_LOW_AUDIO_SUPPORT",
            analysisRms=analysis_rms,
            windowSamples=WINDOW_SAMPLES,
        )

    spectrum = np.abs(
        np.fft.rfft(
            demeaned * np.hanning(WINDOW_SAMPLES),
            n=frozen_v6.FFT_SIZE,
        )
    )
    if spectrum.ndim != 1 or not np.all(np.isfinite(spectrum)) or np.any(spectrum < 0.0):
        return _failure(
            frozen_v6.CLASS_INSUFFICIENT,
            selected_midi,
            "BOUNDARY_NONFINITE_OR_NEGATIVE_SPECTRUM",
            analysisRms=analysis_rms,
            windowSamples=WINDOW_SAMPLES,
        )

    frequencies = frozen_v7.expected_frequency_grid()
    v7_result = frozen_v7.evaluate_in_memory_innovation(
        selected_midi,
        spectrum,
        frequencies,
    )
    if not isinstance(v7_result, dict):
        return _failure(
            frozen_v6.CLASS_INSUFFICIENT,
            selected_midi,
            "BOUNDARY_V7_RESULT_NOT_MAPPING",
            analysisRms=analysis_rms,
            windowSamples=WINDOW_SAMPLES,
        )

    status = str(v7_result.get("status", "V7_STATUS_MISSING"))
    if v7_result.get("passed") is True:
        classification = frozen_v6.CLASS_CORROBORATED
        reason = "OK"
    elif status in _UNAVAILABLE_V7_STATUSES:
        classification = frozen_v6.CLASS_INSUFFICIENT
        reason = f"BOUNDARY_{status}"
    else:
        classification = frozen_v6.CLASS_NOT_CORROBORATED
        reason = f"BOUNDARY_{status}"

    fit = {
        "analysisRms": analysis_rms,
        "windowSamples": WINDOW_SAMPLES,
        "evidenceKind": "clip-start-post-spectrum-evidence",
        "v7Status": status,
        "passed": bool(v7_result.get("passed") is True),
        "necessityFraction": v7_result.get("necessityFraction"),
        "candidateEvidenceFraction": v7_result.get("candidateEvidenceFraction"),
        "credibleLowerOwners": v7_result.get("credibleLowerOwners", []),
        "vetoingOwners": v7_result.get("vetoingOwners", []),
        "v3Composite": v7_result.get("v3Composite"),
        "v7Composite": v7_result,
    }
    return {
        "classification": classification,
        "selectedMidi": selected_midi,
        "reason": reason,
        "method": METHOD,
        "evidenceKind": "clip-start-post-spectrum-evidence",
        "fit": fit,
    }
