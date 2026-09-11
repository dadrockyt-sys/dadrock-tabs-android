#!/usr/bin/env python3

"""Same-inference Basic Pitch decision-surface diagnostics.

This sidecar is diagnostic-only. It captures the raw onset surface and the
`infer_onsets=True` effective onset surface used by Basic Pitch 0.4.0's decoder,
then binds those arrays to the existing same-inference note-activation bundle.
It never changes decoded note inventory, pitch identity, acceptance, or duration.
"""

import base64
import copy
import hashlib
import json
import math
import struct
import zlib

import numpy as np

from basic_pitch_activation_evidence import (
    BUNDLE_IDENTITY_CONTRACT,
    NOTE_IDENTITY_CONTRACT,
    decode_and_verify_activation_sidecar,
)

CONTRACT = "songsterr-fresh-basic-pitch-decision-surface-diagnostic-v1"
IDENTITY_CONTRACT = "songsterr-fresh-basic-pitch-decision-surface-identity-v1"
BASIC_PITCH_MIDI_OFFSET = 21
INFER_ONSET_DIFF_COUNT = 2


class DecisionSurfaceError(RuntimeError):
    pass


def _finite(value, label):
    if isinstance(value, bool):
        raise DecisionSurfaceError(f"{label}:FINITE_NUMBER_REQUIRED")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise DecisionSurfaceError(f"{label}:FINITE_NUMBER_REQUIRED") from exc
    if not math.isfinite(number):
        raise DecisionSurfaceError(f"{label}:FINITE_NUMBER_REQUIRED")
    return number


def _sha256(value, label):
    if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise DecisionSurfaceError(f"{label}:SHA256_INVALID")
    return value


def _canonical_json(value):
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise DecisionSurfaceError("CANONICAL_JSON_FAILED") from exc


def _encode_array(array, dtype):
    values = np.ascontiguousarray(np.asarray(array, dtype=np.dtype(dtype)))
    if values.size == 0 or not np.all(np.isfinite(values)):
        raise DecisionSurfaceError("DECISION_SURFACE_ARRAY_INVALID")
    raw = values.tobytes(order="C")
    return {
        "dtype": np.dtype(dtype).str,
        "shape": [int(v) for v in values.shape],
        "encoding": "zlib+base64",
        "rawByteLength": len(raw),
        "rawSha256": hashlib.sha256(raw).hexdigest(),
        "data": base64.b64encode(zlib.compress(raw, level=9)).decode("ascii"),
    }


def _decode_array(payload, label):
    if not isinstance(payload, dict) or payload.get("encoding") != "zlib+base64":
        raise DecisionSurfaceError(f"{label}:ENCODING_CHANGED")
    try:
        compressed = base64.b64decode(payload["data"], validate=True)
        raw = zlib.decompress(compressed)
    except Exception as exc:
        raise DecisionSurfaceError(f"{label}:DECODE_FAILED") from exc
    if len(raw) != int(payload.get("rawByteLength", -1)):
        raise DecisionSurfaceError(f"{label}:RAW_LENGTH_MISMATCH")
    if hashlib.sha256(raw).hexdigest() != payload.get("rawSha256"):
        raise DecisionSurfaceError(f"{label}:RAW_SHA_MISMATCH")
    try:
        dtype = np.dtype(payload.get("dtype"))
        shape = tuple(int(v) for v in payload.get("shape", []))
    except Exception as exc:
        raise DecisionSurfaceError(f"{label}:DTYPE_OR_SHAPE_INVALID") from exc
    if not shape or any(v <= 0 for v in shape):
        raise DecisionSurfaceError(f"{label}:SHAPE_INVALID")
    expected = int(np.prod(shape, dtype=np.int64))
    values = np.frombuffer(raw, dtype=dtype)
    if values.size != expected:
        raise DecisionSurfaceError(f"{label}:SHAPE_MISMATCH")
    values = values.reshape(shape)
    if not np.all(np.isfinite(values)):
        raise DecisionSurfaceError(f"{label}:NONFINITE")
    return values


def effective_onsets_basic_pitch_v040(raw_onsets, note_frames):
    """Mirror Basic Pitch 0.4.0 get_infered_onsets(..., n_diff=2)."""
    onsets = np.asarray(raw_onsets, dtype=np.float64)
    frames = np.asarray(note_frames, dtype=np.float64)
    if onsets.ndim != 2 or frames.ndim != 2 or onsets.shape != frames.shape or onsets.size == 0:
        raise DecisionSurfaceError("DECISION_SURFACE_INPUT_SHAPE_MISMATCH")
    if not np.all(np.isfinite(onsets)) or not np.all(np.isfinite(frames)):
        raise DecisionSurfaceError("DECISION_SURFACE_INPUT_NONFINITE")

    diffs = []
    for n_diff in range(1, INFER_ONSET_DIFF_COUNT + 1):
        padded = np.concatenate([np.zeros((n_diff, frames.shape[1])), frames], axis=0)
        diffs.append(padded[n_diff:, :] - padded[:-n_diff, :])
    frame_diff = np.min(diffs, axis=0)
    frame_diff[frame_diff < 0] = 0
    frame_diff[:INFER_ONSET_DIFF_COUNT, :] = 0

    max_frame_diff = float(np.max(frame_diff))
    max_raw_onset = float(np.max(onsets))
    if max_frame_diff <= 0:
        # Upstream would divide by zero in this degenerate case. Fail closed instead
        # of serializing NaNs into a diagnostic artifact.
        raise DecisionSurfaceError("DECISION_SURFACE_INFERRED_ONSET_SCALE_DEGENERATE")
    scaled_diff = max_raw_onset * frame_diff / max_frame_diff
    effective = np.maximum(onsets, scaled_diff)
    if not np.all(np.isfinite(effective)):
        raise DecisionSurfaceError("DECISION_SURFACE_EFFECTIVE_ONSET_NONFINITE")
    return effective


def _strict_local_peak_mask(values):
    matrix = np.asarray(values, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] < 3:
        raise DecisionSurfaceError("DECISION_SURFACE_PEAK_MATRIX_TOO_SHORT")
    mask = np.zeros(matrix.shape, dtype=bool)
    mask[1:-1, :] = (matrix[1:-1, :] > matrix[:-2, :]) & (matrix[1:-1, :] > matrix[2:, :])
    return mask


def _peak_summary(matrix, threshold, minimum_midi):
    mask = _strict_local_peak_mask(matrix)
    above = mask & (matrix >= threshold)
    histogram = {
        str(minimum_midi + index): int(np.sum(above[:, index]))
        for index in range(matrix.shape[1])
        if int(np.sum(above[:, index])) > 0
    }
    return {
        "strictLocalPeakCount": int(np.sum(mask)),
        "strictLocalPeakAtOrAboveOnsetThresholdCount": int(np.sum(above)),
        "strictLocalPeakAtOrAboveOnsetThresholdMidiHistogram": histogram,
    }


def _validate_note_identity(identity):
    if not isinstance(identity, dict):
        raise DecisionSurfaceError("NOTE_IDENTITY_MISSING")
    if identity.get("contract") != NOTE_IDENTITY_CONTRACT or identity.get("version") != 1:
        raise DecisionSurfaceError("NOTE_IDENTITY_CONTRACT_CHANGED")
    if identity.get("algorithm") != "sha256":
        raise DecisionSurfaceError("NOTE_IDENTITY_ALGORITHM_CHANGED")
    _sha256(identity.get("sha256"), "noteIdentity.sha256")
    return copy.deepcopy(identity)


def _validate_activation_bundle(identity, note_identity):
    if not isinstance(identity, dict):
        raise DecisionSurfaceError("ACTIVATION_BUNDLE_MISSING")
    if identity.get("contract") != BUNDLE_IDENTITY_CONTRACT or identity.get("version") != 1:
        raise DecisionSurfaceError("ACTIVATION_BUNDLE_CONTRACT_CHANGED")
    if identity.get("algorithm") != "sha256":
        raise DecisionSurfaceError("ACTIVATION_BUNDLE_ALGORITHM_CHANGED")
    if identity.get("noteIdentitySha256") != note_identity.get("sha256"):
        raise DecisionSurfaceError("ACTIVATION_BUNDLE_NOTE_IDENTITY_MISMATCH")
    for field in ("activationMatrixSha256", "frameTimesSha256", "sha256"):
        _sha256(identity.get(field), f"activationBundle.{field}")
    return copy.deepcopy(identity)


def _identity_payload(note_identity, activation_bundle, raw_payload, effective_payload, minimum_midi, maximum_midi, model_metadata):
    semantic = {
        "contract": IDENTITY_CONTRACT,
        "version": 1,
        "noteInferenceSha256": note_identity["sha256"],
        "activationBundleSha256": activation_bundle["sha256"],
        "frameTimesSha256": activation_bundle["frameTimesSha256"],
        "rawOnsetMatrixSha256": raw_payload["rawSha256"],
        "effectiveOnsetMatrixSha256": effective_payload["rawSha256"],
        "minimumMidi": int(minimum_midi),
        "maximumMidi": int(maximum_midi),
        "inferOnsets": True,
        "inferOnsetDiffCount": INFER_ONSET_DIFF_COUNT,
        "onsetThreshold": _finite(model_metadata.get("onsetThreshold"), "model.onsetThreshold"),
        "frameThreshold": _finite(model_metadata.get("frameThreshold"), "model.frameThreshold"),
        "minimumNoteLengthMs": _finite(model_metadata.get("minimumNoteLengthMs"), "model.minimumNoteLengthMs"),
        "melodiaTrick": True,
    }
    digest = hashlib.sha256((IDENTITY_CONTRACT + "\0" + _canonical_json(semantic)).encode("utf-8")).hexdigest()
    return {**semantic, "algorithm": "sha256", "sha256": digest}


def build_decision_surface_sidecar(
    *,
    model_onset_matrix,
    model_note_matrix,
    note_identity,
    activation_bundle_identity,
    minimum_midi,
    maximum_midi,
    audio_source,
    separation_source,
    model_metadata,
):
    note_identity = _validate_note_identity(note_identity)
    activation_bundle = _validate_activation_bundle(activation_bundle_identity, note_identity)
    if int(minimum_midi) != int(activation_bundle.get("minimumMidi")) or int(maximum_midi) != int(activation_bundle.get("maximumMidi")):
        raise DecisionSurfaceError("DECISION_SURFACE_MIDI_RANGE_NOT_BOUND_TO_ACTIVATION")

    raw = np.asarray(model_onset_matrix, dtype=np.float64)
    frames = np.asarray(model_note_matrix, dtype=np.float64)
    if raw.ndim != 2 or frames.ndim != 2 or raw.shape != frames.shape:
        raise DecisionSurfaceError("DECISION_SURFACE_MODEL_MATRIX_SHAPE_MISMATCH")
    start_index = int(minimum_midi) - BASIC_PITCH_MIDI_OFFSET
    stop_index = int(maximum_midi) - BASIC_PITCH_MIDI_OFFSET + 1
    if start_index < 0 or stop_index > raw.shape[1] or start_index >= stop_index:
        raise DecisionSurfaceError("DECISION_SURFACE_MIDI_SLICE_INVALID")

    effective = effective_onsets_basic_pitch_v040(raw, frames)
    raw_selected = raw[:, start_index:stop_index]
    effective_selected = effective[:, start_index:stop_index]
    raw_payload = _encode_array(raw_selected, "<f4")
    effective_payload = _encode_array(effective_selected, "<f4")
    identity = _identity_payload(
        note_identity,
        activation_bundle,
        raw_payload,
        effective_payload,
        minimum_midi,
        maximum_midi,
        model_metadata,
    )
    onset_threshold = float(model_metadata["onsetThreshold"])

    payload = {
        "contract": CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "role": "guitar",
        "measurementOnly": True,
        "noteInferenceIdentity": note_identity,
        "activationEvidenceIdentity": activation_bundle,
        "decisionSurfaceIdentity": identity,
        "model": copy.deepcopy(model_metadata),
        "rawOnsetMatrix": {
            **raw_payload,
            "modelOutputKey": "onset",
            "sourceMidiOffset": BASIC_PITCH_MIDI_OFFSET,
            "minimumMidi": int(minimum_midi),
            "maximumMidi": int(maximum_midi),
            "frameCount": int(raw_selected.shape[0]),
            "midiBinCount": int(raw_selected.shape[1]),
        },
        "effectiveOnsetMatrix": {
            **effective_payload,
            "derivation": "basic-pitch-v0.4.0-get_infered_onsets-n_diff-2",
            "inferOnsets": True,
            "inferOnsetDiffCount": INFER_ONSET_DIFF_COUNT,
            "minimumMidi": int(minimum_midi),
            "maximumMidi": int(maximum_midi),
            "frameCount": int(effective_selected.shape[0]),
            "midiBinCount": int(effective_selected.shape[1]),
        },
        "diagnostics": {
            "frameTimesOwnedByActivationBundle": True,
            "frameTimesSha256": activation_bundle["frameTimesSha256"],
            "rawOnsetPeaks": _peak_summary(raw_selected, onset_threshold, int(minimum_midi)),
            "effectiveOnsetPeaks": _peak_summary(effective_selected, onset_threshold, int(minimum_midi)),
            "onsetThreshold": onset_threshold,
            "frameThreshold": float(model_metadata["frameThreshold"]),
            "minimumNoteLengthMs": float(model_metadata["minimumNoteLengthMs"]),
            "melodiaTrick": True,
            "decoderCanCreateNotesWithoutThresholdedOnsetPeak": True,
        },
        "hardGuards": {
            "sameInferenceAsDecodedNotes": True,
            "sameInferenceAsActivationBundle": True,
            "diagnosticOnly": True,
            "usedForAcceptance": False,
            "usedForDuration": False,
            "writesSourceEnd": False,
            "writesDurationSeconds": False,
            "changesPitchIdentity": False,
            "changesDecodedEventInventory": False,
            "referenceTabUsed": False,
            "professionalScorerUsed": False,
            "legacyV143ScorerImported": False,
        },
        "provenance": {
            "source": CONTRACT,
            "audioSource": audio_source,
            "separationSource": separation_source,
            "referenceBlind": True,
            "modelInvoked": True,
            "diagnosticOnly": True,
        },
    }
    return payload


def decode_and_verify_decision_surface(payload, *, activation_payload=None, evidence=None):
    if not isinstance(payload, dict) or payload.get("contract") != CONTRACT or payload.get("version") != 1:
        raise DecisionSurfaceError("DECISION_SURFACE_CONTRACT_MISMATCH")
    if payload.get("referenceBlind") is not True or payload.get("role") != "guitar" or payload.get("measurementOnly") is not True:
        raise DecisionSurfaceError("DECISION_SURFACE_SCOPE_CHANGED")
    guards = payload.get("hardGuards")
    if not isinstance(guards, dict):
        raise DecisionSurfaceError("DECISION_SURFACE_GUARDS_MISSING")
    true_guards = ("sameInferenceAsDecodedNotes", "sameInferenceAsActivationBundle", "diagnosticOnly")
    false_guards = (
        "usedForAcceptance",
        "usedForDuration",
        "writesSourceEnd",
        "writesDurationSeconds",
        "changesPitchIdentity",
        "changesDecodedEventInventory",
        "referenceTabUsed",
        "professionalScorerUsed",
        "legacyV143ScorerImported",
    )
    for field in true_guards:
        if guards.get(field) is not True:
            raise DecisionSurfaceError(f"DECISION_SURFACE_GUARD_CHANGED:{field}")
    for field in false_guards:
        if guards.get(field) is not False:
            raise DecisionSurfaceError(f"DECISION_SURFACE_GUARD_CHANGED:{field}")

    note_identity = _validate_note_identity(payload.get("noteInferenceIdentity"))
    activation_bundle = _validate_activation_bundle(payload.get("activationEvidenceIdentity"), note_identity)
    raw = _decode_array(payload.get("rawOnsetMatrix"), "RAW_ONSET_MATRIX")
    effective = _decode_array(payload.get("effectiveOnsetMatrix"), "EFFECTIVE_ONSET_MATRIX")
    if raw.shape != effective.shape:
        raise DecisionSurfaceError("DECISION_SURFACE_DECODED_SHAPE_MISMATCH")
    raw_meta = payload["rawOnsetMatrix"]
    effective_meta = payload["effectiveOnsetMatrix"]
    minimum_midi = int(raw_meta.get("minimumMidi", -1))
    maximum_midi = int(raw_meta.get("maximumMidi", -1))
    expected_bins = maximum_midi - minimum_midi + 1
    if expected_bins != raw.shape[1] or int(raw_meta.get("frameCount", -1)) != raw.shape[0]:
        raise DecisionSurfaceError("DECISION_SURFACE_RAW_METADATA_MISMATCH")
    if int(raw_meta.get("midiBinCount", -1)) != raw.shape[1]:
        raise DecisionSurfaceError("DECISION_SURFACE_RAW_MIDI_BIN_MISMATCH")
    if int(effective_meta.get("minimumMidi", -1)) != minimum_midi or int(effective_meta.get("maximumMidi", -1)) != maximum_midi:
        raise DecisionSurfaceError("DECISION_SURFACE_EFFECTIVE_MIDI_RANGE_MISMATCH")
    if int(effective_meta.get("frameCount", -1)) != effective.shape[0] or int(effective_meta.get("midiBinCount", -1)) != effective.shape[1]:
        raise DecisionSurfaceError("DECISION_SURFACE_EFFECTIVE_METADATA_MISMATCH")

    identity = payload.get("decisionSurfaceIdentity")
    expected_identity = _identity_payload(
        note_identity,
        activation_bundle,
        raw_meta,
        effective_meta,
        minimum_midi,
        maximum_midi,
        payload.get("model", {}),
    )
    if identity != expected_identity:
        raise DecisionSurfaceError("DECISION_SURFACE_IDENTITY_MISMATCH")

    diagnostics = payload.get("diagnostics")
    if not isinstance(diagnostics, dict):
        raise DecisionSurfaceError("DECISION_SURFACE_DIAGNOSTICS_MISSING")
    if diagnostics.get("frameTimesOwnedByActivationBundle") is not True:
        raise DecisionSurfaceError("DECISION_SURFACE_FRAME_TIME_OWNERSHIP_CHANGED")
    if diagnostics.get("frameTimesSha256") != activation_bundle.get("frameTimesSha256"):
        raise DecisionSurfaceError("DECISION_SURFACE_FRAME_TIME_IDENTITY_MISMATCH")
    if diagnostics.get("decoderCanCreateNotesWithoutThresholdedOnsetPeak") is not True:
        raise DecisionSurfaceError("DECISION_SURFACE_MELODIA_GUARD_CHANGED")

    if activation_payload is not None:
        decoded_activation = decode_and_verify_activation_sidecar(activation_payload, evidence=evidence)
        if decoded_activation.get("inferenceBundleIdentity") != activation_bundle:
            raise DecisionSurfaceError("DECISION_SURFACE_ACTIVATION_BUNDLE_NOT_BOUND")
        if decoded_activation["activations"].shape != raw.shape:
            raise DecisionSurfaceError("DECISION_SURFACE_ACTIVATION_SHAPE_MISMATCH")
        if decoded_activation.get("minimumMidi") != minimum_midi or decoded_activation.get("maximumMidi") != maximum_midi:
            raise DecisionSurfaceError("DECISION_SURFACE_ACTIVATION_MIDI_RANGE_MISMATCH")

    return {
        "rawOnsets": raw,
        "effectiveOnsets": effective,
        "minimumMidi": minimum_midi,
        "maximumMidi": maximum_midi,
        "noteInferenceIdentity": note_identity,
        "activationEvidenceIdentity": activation_bundle,
        "decisionSurfaceIdentity": expected_identity,
    }


def _fake_sha(seed):
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _fake_identities(frame_count=6, midi_bins=49):
    note_identity = {
        "contract": NOTE_IDENTITY_CONTRACT,
        "version": 1,
        "algorithm": "sha256",
        "canonicalization": "test",
        "eventCount": 1,
        "sha256": _fake_sha("note"),
    }
    activation_bundle = {
        "contract": BUNDLE_IDENTITY_CONTRACT,
        "version": 1,
        "algorithm": "sha256",
        "noteIdentitySha256": note_identity["sha256"],
        "activationMatrixSha256": _fake_sha("activation"),
        "frameTimesSha256": _fake_sha("times"),
        "minimumMidi": 40,
        "maximumMidi": 88,
        "frameCount": frame_count,
        "midiBinCount": midi_bins,
        "sha256": _fake_sha("bundle"),
    }
    return note_identity, activation_bundle


def run_self_test():
    columns = 88
    frames = np.zeros((6, columns), dtype=np.float32)
    onsets = np.zeros((6, columns), dtype=np.float32)
    midi_index = 64 - BASIC_PITCH_MIDI_OFFSET
    frames[:, midi_index] = [0.0, 0.1, 0.8, 0.9, 0.2, 0.1]
    onsets[:, midi_index] = [0.0, 0.1, 0.4, 0.7, 0.2, 0.1]
    # Keep the global onset maximum non-zero and frame differences non-degenerate.
    onsets[2, 40 - BASIC_PITCH_MIDI_OFFSET] = 0.9
    frames[:, 40 - BASIC_PITCH_MIDI_OFFSET] = [0.0, 0.2, 0.6, 0.4, 0.3, 0.1]

    note_identity, activation_bundle = _fake_identities()
    model = {
        "family": "Spotify Basic Pitch",
        "package": "basic-pitch",
        "packageVersion": "0.4.0",
        "polyphonic": True,
        "instrumentAgnostic": True,
        "minimumMidi": 40,
        "maximumMidi": 88,
        "onsetThreshold": 0.5,
        "frameThreshold": 0.3,
        "minimumNoteLengthMs": 127.7,
    }
    payload = build_decision_surface_sidecar(
        model_onset_matrix=onsets,
        model_note_matrix=frames,
        note_identity=note_identity,
        activation_bundle_identity=activation_bundle,
        minimum_midi=40,
        maximum_midi=88,
        audio_source="fixture.m4a",
        separation_source="guitar.wav",
        model_metadata=model,
    )
    decoded = decode_and_verify_decision_surface(payload)
    assert decoded["rawOnsets"].shape == (6, 49)
    assert decoded["effectiveOnsets"].shape == (6, 49)
    assert payload["hardGuards"]["usedForAcceptance"] is False
    assert payload["hardGuards"]["usedForDuration"] is False
    assert payload["hardGuards"]["changesDecodedEventInventory"] is False
    assert payload["diagnostics"]["decoderCanCreateNotesWithoutThresholdedOnsetPeak"] is True
    assert np.max(decoded["effectiveOnsets"]) >= np.max(decoded["rawOnsets"])

    tampered = copy.deepcopy(payload)
    tampered["hardGuards"]["usedForAcceptance"] = True
    try:
        decode_and_verify_decision_surface(tampered)
    except DecisionSurfaceError as exc:
        assert "usedForAcceptance" in str(exc)
    else:
        raise AssertionError("acceptance guard tamper must fail")

    tampered = copy.deepcopy(payload)
    tampered["rawOnsetMatrix"]["rawSha256"] = _fake_sha("wrong")
    try:
        decode_and_verify_decision_surface(tampered)
    except DecisionSurfaceError as exc:
        assert "RAW_SHA_MISMATCH" in str(exc)
    else:
        raise AssertionError("raw matrix tamper must fail")

    bad = onsets.copy()
    bad[1, 1] = np.nan
    try:
        build_decision_surface_sidecar(
            model_onset_matrix=bad,
            model_note_matrix=frames,
            note_identity=note_identity,
            activation_bundle_identity=activation_bundle,
            minimum_midi=40,
            maximum_midi=88,
            audio_source="fixture.m4a",
            separation_source="guitar.wav",
            model_metadata=model,
        )
    except DecisionSurfaceError as exc:
        assert "NONFINITE" in str(exc)
    else:
        raise AssertionError("non-finite decision surface must fail")

    print(json.dumps({
        "contract": CONTRACT,
        "selfTest": "PASS",
        "sameInferenceRequired": True,
        "measurementOnly": True,
        "usedForAcceptance": False,
        "usedForDuration": False,
        "changesDecodedEventInventory": False,
    }, sort_keys=True))


if __name__ == "__main__":
    run_self_test()
