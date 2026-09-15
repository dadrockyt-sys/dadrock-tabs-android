#!/usr/bin/env python3
"""Reference-blind independent DSP qualification for Basic Pitch note proposals.

This wrapper performs no model inference. It binds one qualification decision to
one immutable Basic Pitch note identity and uses the already-frozen V6
onset-birth DSP classifier. Basic Pitch candidate confidence is never read for a
decision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from math import gcd
from pathlib import Path
from typing import Any

import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

from onset_birth_corroboration_v6 import (
    CLASS_CORROBORATED,
    CLASS_INSUFFICIENT,
    CLASS_NOT_CORROBORATED,
    FRAME_END_OFFSETS,
    FRAME_SAMPLES,
    MIN_ANALYSIS_RMS,
    MIN_INNOVATION_ENERGY,
    NECESSITY_FRACTION_MIN,
    SAMPLE_RATE,
    classify_audio_event,
)

CONTRACT = "songsterr-fresh-model-note-qualification-v1"
VERSION = 1
EXPECTED_MODEL_CONTRACT = "songsterr-fresh-basic-pitch-isolated-guitar-v1"
EXPECTED_NOTE_IDENTITY_CONTRACT = "songsterr-fresh-basic-pitch-note-identity-v1"
METHOD = "v6-complex-harmonic-onset-birth-dsp-wrapper-v1"
PLAYABLE_MIDI_MIN = 40
PLAYABLE_MIDI_MAX = 88
NO_BIRTH_REASON = "INSUFFICIENT_LOW_ONSET_INNOVATION"
REQUIRED_LEFT_CONTEXT_SAMPLES = FRAME_SAMPLES - min(FRAME_END_OFFSETS)
REQUIRED_RIGHT_CONTEXT_SAMPLES = max(FRAME_END_OFFSETS)


class QualificationError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _pcm_to_float64(values: np.ndarray) -> tuple[np.ndarray, str]:
    array = np.asarray(values)
    dtype_name = str(array.dtype)
    if np.issubdtype(array.dtype, np.floating):
        converted = np.asarray(array, dtype=np.float64)
    elif np.issubdtype(array.dtype, np.unsignedinteger):
        info = np.iinfo(array.dtype)
        midpoint = (float(info.max) + float(info.min) + 1.0) / 2.0
        scale = max(1.0, midpoint)
        converted = (array.astype(np.float64) - midpoint) / scale
    elif np.issubdtype(array.dtype, np.signedinteger):
        info = np.iinfo(array.dtype)
        scale = max(abs(float(info.min)), abs(float(info.max)))
        converted = array.astype(np.float64) / scale
    else:
        raise QualificationError(f"UNSUPPORTED_WAV_DTYPE:{dtype_name}")
    if not np.all(np.isfinite(converted)):
        raise QualificationError("NONFINITE_WAV_AUDIO")
    return converted, dtype_name


def load_analysis_audio(path: Path) -> tuple[np.ndarray, dict[str, Any]]:
    source_rate, raw = wavfile.read(path)
    if isinstance(source_rate, bool) or not isinstance(source_rate, (int, np.integer)) or int(source_rate) <= 0:
        raise QualificationError("INVALID_WAV_SAMPLE_RATE")
    values, source_dtype = _pcm_to_float64(np.asarray(raw))
    if values.ndim == 1:
        source_channels = 1
        mono = values
    elif values.ndim == 2 and values.shape[1] >= 1:
        source_channels = int(values.shape[1])
        mono = np.mean(values, axis=1, dtype=np.float64)
    else:
        raise QualificationError("WAV_AUDIO_MUST_BE_MONO_OR_INTERLEAVED_CHANNELS")
    if mono.size == 0:
        raise QualificationError("WAV_AUDIO_EMPTY")

    source_rate = int(source_rate)
    resampled = source_rate != SAMPLE_RATE
    if resampled:
        factor = gcd(source_rate, SAMPLE_RATE)
        up = SAMPLE_RATE // factor
        down = source_rate // factor
        mono = resample_poly(mono, up, down).astype(np.float64, copy=False)
    if mono.ndim != 1 or mono.size == 0 or not np.all(np.isfinite(mono)):
        raise QualificationError("ANALYSIS_AUDIO_INVALID_AFTER_RESAMPLE")

    return mono, {
        "sourceSampleRate": source_rate,
        "analysisSampleRate": SAMPLE_RATE,
        "sourceChannels": source_channels,
        "sourceDtype": source_dtype,
        "channelReduction": "mean" if source_channels > 1 else "none",
        "resampled": resampled,
        "resampleMethod": "scipy.signal.resample_poly" if resampled else "none",
        "analysisSampleCount": int(mono.size),
    }


def validate_model_notes(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if (
        payload.get("contract") != EXPECTED_MODEL_CONTRACT
        or payload.get("version") != 1
        or payload.get("referenceBlind") is not True
        or payload.get("role") != "guitar"
    ):
        raise QualificationError("MODEL_NOTES_CONTRACT_MISMATCH")
    if payload.get("provenance", {}).get("modelInvoked") is not True:
        raise QualificationError("MODEL_NOTES_MUST_DECLARE_MODEL_INFERENCE")

    notes = payload.get("notes")
    if not isinstance(notes, list) or not notes:
        raise QualificationError("MODEL_NOTES_EMPTY")

    identity = payload.get("noteInferenceIdentity")
    if not isinstance(identity, dict):
        raise QualificationError("MODEL_NOTE_IDENTITY_MISSING")
    sha = identity.get("sha256")
    if (
        identity.get("contract") != EXPECTED_NOTE_IDENTITY_CONTRACT
        or identity.get("version") != 1
        or identity.get("algorithm") != "sha256"
        or identity.get("eventCount") != len(notes)
        or not isinstance(sha, str)
        or len(sha) != 64
        or any(ch not in "0123456789abcdef" for ch in sha)
    ):
        raise QualificationError("MODEL_NOTE_IDENTITY_INVALID")

    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, note in enumerate(notes):
        note_id = note.get("noteId")
        if not isinstance(note_id, str) or not note_id:
            raise QualificationError(f"MODEL_NOTE_ID_INVALID:{index}")
        if note_id in seen:
            raise QualificationError(f"MODEL_NOTE_ID_DUPLICATE:{note_id}")
        seen.add(note_id)

        midi = note.get("midi")
        if isinstance(midi, bool) or not isinstance(midi, int) or not PLAYABLE_MIDI_MIN <= midi <= PLAYABLE_MIDI_MAX:
            raise QualificationError(f"MODEL_NOTE_MIDI_INVALID:{note_id}")
        start = note.get("startSeconds")
        if isinstance(start, bool) or not isinstance(start, (int, float)) or not math.isfinite(float(start)) or float(start) < 0.0:
            raise QualificationError(f"MODEL_NOTE_START_INVALID:{note_id}")

        # Intentionally do not read note['confidence']; qualification must remain independent of it.
        normalized.append({"noteId": note_id, "midi": int(midi), "startSeconds": float(start)})
    return normalized, identity


def classify_proposal(audio: np.ndarray, note: dict[str, Any]) -> dict[str, Any]:
    original_onset_sample = int(round(note["startSeconds"] * SAMPLE_RATE))
    if original_onset_sample < 0:
        raise QualificationError("NEGATIVE_ONSET_SAMPLE")

    left_padding = max(0, REQUIRED_LEFT_CONTEXT_SAMPLES - original_onset_sample)
    if left_padding > 0:
        analysis_audio = np.pad(audio, (left_padding, 0), mode="constant", constant_values=0.0)
        analysis_onset_sample = original_onset_sample + left_padding
    else:
        analysis_audio = audio
        analysis_onset_sample = original_onset_sample

    # No right padding. The inherited classifier will return insufficient evidence
    # when required post-context is unavailable.
    result = classify_audio_event(analysis_audio, analysis_onset_sample, note["midi"])
    classification = result.get("classification")
    reason = result.get("reason")

    if classification == CLASS_CORROBORATED:
        status = "corroborated"
    elif classification == CLASS_NOT_CORROBORATED:
        status = "rejected"
    elif classification == CLASS_INSUFFICIENT and reason == NO_BIRTH_REASON:
        # Frozen wrapper semantic: full-context, adequate-RMS, sub-floor onset
        # innovation is negative evidence for a proposed *new note birth*.
        status = "rejected"
    elif classification == CLASS_INSUFFICIENT:
        status = "insufficient"
    else:
        raise QualificationError(f"UNEXPECTED_V6_CLASSIFICATION:{classification}")

    fit = result.get("fit") if isinstance(result.get("fit"), dict) else {}
    innovation_energy = fit.get("innovationEnergy")
    analysis_rms = fit.get("analysisRms")
    necessity_fraction = fit.get("necessityFraction")

    # Diagnostic only: a binary corroboration indicator, not a calibrated
    # probability and not the owner of the status decision.
    independent_onset_confidence = 1.0 if status == "corroborated" else 0.0

    return {
        "noteId": note["noteId"],
        "midi": note["midi"],
        "startSeconds": note["startSeconds"],
        "status": status,
        "independentOnsetConfidence": independent_onset_confidence,
        "provenance": {
            "method": METHOD,
            "v6Classification": classification,
            "v6Reason": reason,
            "leftBoundaryZeroPaddingSamples": left_padding,
            "analysisOnsetSample": analysis_onset_sample,
            "originalOnsetSample": original_onset_sample,
            "requiredLeftContextSamples": REQUIRED_LEFT_CONTEXT_SAMPLES,
            "requiredRightContextSamples": REQUIRED_RIGHT_CONTEXT_SAMPLES,
            "analysisRms": analysis_rms,
            "innovationEnergy": innovation_energy,
            "necessityFraction": necessity_fraction,
            "candidateConfidenceReadForDecision": False,
        },
    }


def qualify(audio_path: Path, model_notes_path: Path) -> dict[str, Any]:
    model_payload = json.loads(model_notes_path.read_text(encoding="utf-8"))
    notes, identity = validate_model_notes(model_payload)
    audio, audio_details = load_analysis_audio(audio_path)

    proposals = [classify_proposal(audio, note) for note in notes]
    counts = {"corroborated": 0, "rejected": 0, "insufficient": 0}
    for row in proposals:
        counts[row["status"]] += 1

    return {
        "contract": CONTRACT,
        "version": VERSION,
        "referenceBlind": True,
        "modelNoteIdentitySha256": identity["sha256"],
        "method": METHOD,
        "candidateConfidenceUsedForDecision": False,
        "independentOfBasicPitchCandidateConfidence": True,
        "referenceTabUsed": False,
        "proposals": proposals,
        "diagnostics": {
            "proposalCount": len(proposals),
            "statusCounts": counts,
            "confidenceSemantics": "binary-corroboration-indicator-not-calibrated-probability",
            "v6ConstantsInheritedUnchanged": True,
            "noBirthLowInnovationMappedToRejected": True,
            "minimumAnalysisRms": MIN_ANALYSIS_RMS,
            "minimumInnovationEnergy": MIN_INNOVATION_ENERGY,
            "necessityFractionMin": NECESSITY_FRACTION_MIN,
            "requiredLeftContextSamples": REQUIRED_LEFT_CONTEXT_SAMPLES,
            "requiredRightContextSamples": REQUIRED_RIGHT_CONTEXT_SAMPLES,
            "audio": audio_details,
        },
        "provenance": {
            "audioPathName": audio_path.name,
            "audioSha256": sha256_file(audio_path),
            "modelNotesPathName": model_notes_path.name,
            "modelNoteIdentity": dict(identity),
            "modelInvokedByQualifier": False,
            "gpuInvoked": False,
            "networkInvoked": False,
            "candidateConfidenceReadForDecision": False,
            "referenceTabUsed": False,
            "legacyV143ScorerImported": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", required=True)
    parser.add_argument("--model-notes", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = qualify(Path(args.audio), Path(args.model_notes))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(canonical_json({
        "contract": output["contract"],
        "version": output["version"],
        "method": output["method"],
        "modelNoteIdentitySha256": output["modelNoteIdentitySha256"],
        "diagnostics": output["diagnostics"],
        "provenance": output["provenance"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
