#!/usr/bin/env python3
"""Boundary-aware independent DSP qualification for Basic Pitch proposals V2.

Normal in-clip proposals use the frozen V6 onset-birth classifier unchanged.
Clip-start proposals that lack genuine required pre-context use a separate
one-sided physical pitch-presence classifier over genuine post-onset audio.
No synthetic pre-context is fabricated and Basic Pitch confidence is never
read for a decision.
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

from clip_start_pitch_presence_v1 import (
    METHOD as CLIP_START_METHOD,
    WINDOW_SAMPLES as CLIP_START_WINDOW_SAMPLES,
    classify_clip_start_pitch_presence,
)
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

CONTRACT = "songsterr-fresh-model-note-qualification-v2"
VERSION = 2
EXPECTED_MODEL_CONTRACT = "songsterr-fresh-basic-pitch-isolated-guitar-v1"
EXPECTED_NOTE_IDENTITY_CONTRACT = "songsterr-fresh-basic-pitch-note-identity-v1"
METHOD = "v6-onset-birth-plus-clip-start-pitch-presence-wrapper-v2"
NORMAL_METHOD = "v6-complex-harmonic-onset-birth-dsp-unchanged"
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

        # Intentionally do not read note['confidence']; qualification remains independent of it.
        normalized.append({"noteId": note_id, "midi": int(midi), "startSeconds": float(start)})
    return normalized, identity


def _map_classification(result: dict[str, Any], normal_mode: bool) -> str:
    classification = result.get("classification")
    reason = result.get("reason")
    if classification == CLASS_CORROBORATED:
        return "corroborated"
    if classification == CLASS_NOT_CORROBORATED:
        return "rejected"
    if normal_mode and classification == CLASS_INSUFFICIENT and reason == NO_BIRTH_REASON:
        # Unchanged V1/V6 wrapper semantic for a fully contextualized proposed new birth.
        return "rejected"
    if classification == CLASS_INSUFFICIENT:
        return "insufficient"
    raise QualificationError(f"UNEXPECTED_CLASSIFICATION:{classification}")


def classify_proposal(audio: np.ndarray, note: dict[str, Any]) -> dict[str, Any]:
    original_onset_sample = int(round(note["startSeconds"] * SAMPLE_RATE))
    if original_onset_sample < 0:
        raise QualificationError("NEGATIVE_ONSET_SAMPLE")

    clip_start_mode = original_onset_sample < REQUIRED_LEFT_CONTEXT_SAMPLES
    if clip_start_mode:
        result = classify_clip_start_pitch_presence(audio, original_onset_sample, note["midi"])
        mode = "clip-start-one-sided-pitch-presence"
        row_method = CLIP_START_METHOD
    else:
        result = classify_audio_event(audio, original_onset_sample, note["midi"])
        mode = "normal-in-clip-onset-birth"
        row_method = NORMAL_METHOD

    status = _map_classification(result, normal_mode=not clip_start_mode)
    fit = result.get("fit") if isinstance(result.get("fit"), dict) else {}
    independent_onset_confidence = 1.0 if status == "corroborated" else 0.0

    return {
        "noteId": note["noteId"],
        "midi": note["midi"],
        "startSeconds": note["startSeconds"],
        "status": status,
        "independentOnsetConfidence": independent_onset_confidence,
        "provenance": {
            "wrapperMethod": METHOD,
            "method": row_method,
            "qualificationMode": mode,
            "classification": result.get("classification"),
            "reason": result.get("reason"),
            "leftBoundaryZeroPaddingSamples": 0,
            "syntheticPreContextUsed": False,
            "originalOnsetSample": original_onset_sample,
            "requiredLeftContextSamples": REQUIRED_LEFT_CONTEXT_SAMPLES,
            "requiredRightContextSamples": REQUIRED_RIGHT_CONTEXT_SAMPLES,
            "clipStartWindowSamples": CLIP_START_WINDOW_SAMPLES if clip_start_mode else None,
            "analysisRms": fit.get("analysisRms"),
            "innovationEnergy": fit.get("innovationEnergy"),
            "featureEnergy": fit.get("featureEnergy"),
            "selectedCoefficient": fit.get("selectedCoefficient"),
            "necessityFraction": fit.get("necessityFraction"),
            "dominantHarmonicOwner": fit.get("dominantHarmonicOwner"),
            "harmonicOwners": fit.get("harmonicOwners"),
            "candidateConfidenceReadForDecision": False,
        },
    }


def qualify(audio_path: Path, model_notes_path: Path) -> dict[str, Any]:
    model_payload = json.loads(model_notes_path.read_text(encoding="utf-8"))
    notes, identity = validate_model_notes(model_payload)
    audio, audio_details = load_analysis_audio(audio_path)

    proposals = [classify_proposal(audio, note) for note in notes]
    counts = {"corroborated": 0, "rejected": 0, "insufficient": 0}
    mode_counts = {"clip-start-one-sided-pitch-presence": 0, "normal-in-clip-onset-birth": 0}
    for row in proposals:
        counts[row["status"]] += 1
        mode = row["provenance"]["qualificationMode"]
        mode_counts[mode] += 1

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
            "modeCounts": mode_counts,
            "confidenceSemantics": "binary-corroboration-indicator-not-calibrated-probability",
            "v6NormalModeConstantsInheritedUnchanged": True,
            "clipStartUsesSyntheticPreContext": False,
            "clipStartWindowSamples": CLIP_START_WINDOW_SAMPLES,
            "noBirthLowInnovationMappedToRejectedInNormalMode": True,
            "minimumAnalysisRms": MIN_ANALYSIS_RMS,
            "minimumFeatureOrInnovationEnergy": MIN_INNOVATION_ENERGY,
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
            "syntheticPreContextUsed": False,
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
