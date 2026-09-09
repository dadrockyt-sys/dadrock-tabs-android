#!/usr/bin/env python3

import base64
import hashlib
import struct
import zlib

import numpy as np

ACTIVATION_CONTRACT = "songsterr-fresh-basic-pitch-note-activation-evidence-v1"
NOTE_IDENTITY_CONTRACT = "songsterr-fresh-basic-pitch-note-identity-v1"
BUNDLE_IDENTITY_CONTRACT = "songsterr-fresh-basic-pitch-inference-bundle-v1"
NOTE_IDENTITY_CANONICALIZATION = (
    "sha256-domain-v1+sorted(little-endian-f64-start,u8-midi,little-endian-f64-confidence)"
)
BASIC_PITCH_MIDI_OFFSET = 21


def _finite(value, label):
    number = float(value)
    if not np.isfinite(number):
        raise RuntimeError(f"BASIC_PITCH_ACTIVATION_NONFINITE_{label}")
    return number


def note_identity_rows_from_notes(notes):
    rows = []
    for index, note in enumerate(notes):
        rows.append((
            _finite(note["startSeconds"], f"NOTE_START_{index}"),
            int(note["midi"]),
            _finite(note["confidence"], f"NOTE_CONFIDENCE_{index}"),
        ))
    return sorted(rows, key=lambda row: (row[0], row[1], row[2]))


def note_identity_rows_from_evidence(evidence):
    rows = []
    for index, onset in enumerate(evidence.get("onsets", [])):
        if onset.get("classification") != "unambiguous" or onset.get("selectedMidi") is None:
            continue
        rows.append((
            _finite(onset["sourceStart"], f"EVIDENCE_START_{index}"),
            int(onset["selectedMidi"]),
            _finite(onset.get("onsetConfidence", 0.0), f"EVIDENCE_CONFIDENCE_{index}"),
        ))
    return sorted(rows, key=lambda row: (row[0], row[1], row[2]))


def build_note_identity(rows):
    normalized = sorted(
        [(_finite(start, "IDENTITY_START"), int(midi), _finite(confidence, "IDENTITY_CONFIDENCE"))
         for start, midi, confidence in rows],
        key=lambda row: (row[0], row[1], row[2]),
    )
    digest = hashlib.sha256()
    digest.update((NOTE_IDENTITY_CONTRACT + "\0").encode("utf-8"))
    for start, midi, confidence in normalized:
        if midi < 0 or midi > 127:
            raise RuntimeError("BASIC_PITCH_NOTE_IDENTITY_MIDI_INVALID")
        digest.update(struct.pack("<dBd", start, midi, confidence))
    return {
        "contract": NOTE_IDENTITY_CONTRACT,
        "version": 1,
        "algorithm": "sha256",
        "canonicalization": NOTE_IDENTITY_CANONICALIZATION,
        "eventCount": len(normalized),
        "sha256": digest.hexdigest(),
    }


def _encode_array(array, dtype):
    values = np.ascontiguousarray(np.asarray(array, dtype=np.dtype(dtype)))
    if values.size == 0 or not np.all(np.isfinite(values)):
        raise RuntimeError("BASIC_PITCH_ACTIVATION_ARRAY_INVALID")
    raw = values.tobytes(order="C")
    compressed = zlib.compress(raw, level=9)
    return {
        "dtype": np.dtype(dtype).str,
        "shape": [int(value) for value in values.shape],
        "encoding": "zlib+base64",
        "rawByteLength": len(raw),
        "rawSha256": hashlib.sha256(raw).hexdigest(),
        "data": base64.b64encode(compressed).decode("ascii"),
    }


def _decode_array(payload, label):
    if payload.get("encoding") != "zlib+base64":
        raise RuntimeError(f"BASIC_PITCH_ACTIVATION_{label}_ENCODING_CHANGED")
    try:
        compressed = base64.b64decode(payload["data"], validate=True)
        raw = zlib.decompress(compressed)
    except Exception as exc:
        raise RuntimeError(f"BASIC_PITCH_ACTIVATION_{label}_DECODE_FAILED") from exc
    if len(raw) != int(payload.get("rawByteLength", -1)):
        raise RuntimeError(f"BASIC_PITCH_ACTIVATION_{label}_RAW_LENGTH_MISMATCH")
    if hashlib.sha256(raw).hexdigest() != payload.get("rawSha256"):
        raise RuntimeError(f"BASIC_PITCH_ACTIVATION_{label}_RAW_SHA_MISMATCH")
    dtype = np.dtype(payload.get("dtype"))
    shape = tuple(int(value) for value in payload.get("shape", []))
    if not shape or any(value <= 0 for value in shape):
        raise RuntimeError(f"BASIC_PITCH_ACTIVATION_{label}_SHAPE_INVALID")
    expected_count = int(np.prod(shape, dtype=np.int64))
    values = np.frombuffer(raw, dtype=dtype)
    if values.size != expected_count:
        raise RuntimeError(f"BASIC_PITCH_ACTIVATION_{label}_SHAPE_MISMATCH")
    values = values.reshape(shape)
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"BASIC_PITCH_ACTIVATION_{label}_NONFINITE")
    return values


def _bundle_identity(note_identity, activation_matrix, frame_times, minimum_midi, maximum_midi):
    digest = hashlib.sha256()
    digest.update((BUNDLE_IDENTITY_CONTRACT + "\0").encode("utf-8"))
    digest.update(bytes.fromhex(note_identity["sha256"]))
    digest.update(bytes.fromhex(activation_matrix["rawSha256"]))
    digest.update(bytes.fromhex(frame_times["rawSha256"]))
    digest.update(struct.pack(
        "<HHII",
        int(minimum_midi),
        int(maximum_midi),
        int(activation_matrix["shape"][0]),
        int(activation_matrix["shape"][1]),
    ))
    return {
        "contract": BUNDLE_IDENTITY_CONTRACT,
        "version": 1,
        "algorithm": "sha256",
        "noteIdentitySha256": note_identity["sha256"],
        "activationMatrixSha256": activation_matrix["rawSha256"],
        "frameTimesSha256": frame_times["rawSha256"],
        "minimumMidi": int(minimum_midi),
        "maximumMidi": int(maximum_midi),
        "frameCount": int(activation_matrix["shape"][0]),
        "midiBinCount": int(activation_matrix["shape"][1]),
        "sha256": digest.hexdigest(),
    }


def build_activation_sidecar(
    *,
    model_note_matrix,
    frame_times,
    notes,
    minimum_midi,
    maximum_midi,
    audio_source,
    separation_source,
    model_metadata,
    gpu_invoked=False,
):
    matrix = np.asarray(model_note_matrix, dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[0] == 0 or not np.all(np.isfinite(matrix)):
        raise RuntimeError("BASIC_PITCH_ACTIVATION_MATRIX_INVALID")
    start_index = int(minimum_midi) - BASIC_PITCH_MIDI_OFFSET
    stop_index = int(maximum_midi) - BASIC_PITCH_MIDI_OFFSET + 1
    if start_index < 0 or stop_index > matrix.shape[1] or start_index >= stop_index:
        raise RuntimeError("BASIC_PITCH_ACTIVATION_MIDI_SLICE_INVALID")

    selected = matrix[:, start_index:stop_index]
    times = np.asarray(frame_times, dtype=np.float64)
    if (
        times.ndim != 1
        or len(times) != matrix.shape[0]
        or not np.all(np.isfinite(times))
        or np.any(np.diff(times) <= 0)
    ):
        raise RuntimeError("BASIC_PITCH_ACTIVATION_FRAME_TIME_AXIS_INVALID")

    note_identity = build_note_identity(note_identity_rows_from_notes(notes))
    encoded_matrix = _encode_array(selected, "<f4")
    encoded_times = _encode_array(times, "<f8")
    bundle_identity = _bundle_identity(
        note_identity,
        encoded_matrix,
        encoded_times,
        minimum_midi,
        maximum_midi,
    )

    payload = {
        "contract": ACTIVATION_CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "role": "guitar",
        "noteInferenceIdentity": note_identity,
        "inferenceBundleIdentity": bundle_identity,
        "model": dict(model_metadata),
        "activationMatrix": {
            **encoded_matrix,
            "modelOutputKey": "note",
            "sourceMidiOffset": BASIC_PITCH_MIDI_OFFSET,
            "minimumMidi": int(minimum_midi),
            "maximumMidi": int(maximum_midi),
            "midiBinCount": int(selected.shape[1]),
            "frameCount": int(selected.shape[0]),
        },
        "frameTimesSeconds": {
            **encoded_times,
            "frameCount": int(times.shape[0]),
        },
        "hardGuards": {
            "sameInferenceAsDecodedNotes": True,
            "decodedModelNoteEndsIncluded": False,
            "decodedModelNoteEndsUsedAsDuration": False,
            "writesSourceEnd": False,
            "writesDurationSeconds": False,
            "activeDurationAuthority": False,
            "changesPitchIdentity": False,
        },
        "provenance": {
            "source": ACTIVATION_CONTRACT,
            "audioSource": audio_source,
            "separationSource": separation_source,
            "referenceBlind": True,
            "modelInvoked": True,
            "gpuInvoked": bool(gpu_invoked),
            "legacyV143ScorerImported": False,
            "professionalScorerUsed": False,
            "referenceTabUsed": False,
        },
    }
    return payload


def activation_identity_summary(payload):
    return dict(payload["inferenceBundleIdentity"])


def decode_and_verify_activation_sidecar(payload, *, evidence=None, expected_bundle_identity=None):
    if payload.get("contract") != ACTIVATION_CONTRACT or payload.get("version") != 1:
        raise RuntimeError("BASIC_PITCH_ACTIVATION_CONTRACT_MISMATCH")
    if payload.get("referenceBlind") is not True or payload.get("role") != "guitar":
        raise RuntimeError("BASIC_PITCH_ACTIVATION_REFERENCE_BLIND_ROLE_MISMATCH")

    guards = payload.get("hardGuards", {})
    if guards.get("sameInferenceAsDecodedNotes") is not True:
        raise RuntimeError("BASIC_PITCH_ACTIVATION_SAME_INFERENCE_GUARD_MISSING")
    for key in (
        "decodedModelNoteEndsIncluded",
        "decodedModelNoteEndsUsedAsDuration",
        "writesSourceEnd",
        "writesDurationSeconds",
        "activeDurationAuthority",
        "changesPitchIdentity",
    ):
        if guards.get(key) is not False:
            raise RuntimeError(f"BASIC_PITCH_ACTIVATION_GUARD_CHANGED:{key}")

    matrix_payload = payload.get("activationMatrix", {})
    times_payload = payload.get("frameTimesSeconds", {})
    activations = _decode_array(matrix_payload, "MATRIX")
    frame_times = _decode_array(times_payload, "FRAME_TIMES")

    if activations.ndim != 2 or frame_times.ndim != 1:
        raise RuntimeError("BASIC_PITCH_ACTIVATION_DECODE_DIMENSION_MISMATCH")
    if len(frame_times) != activations.shape[0] or np.any(np.diff(frame_times) <= 0):
        raise RuntimeError("BASIC_PITCH_ACTIVATION_DECODE_TIME_AXIS_MISMATCH")
    minimum_midi = int(matrix_payload.get("minimumMidi", -1))
    maximum_midi = int(matrix_payload.get("maximumMidi", -1))
    if maximum_midi - minimum_midi + 1 != activations.shape[1]:
        raise RuntimeError("BASIC_PITCH_ACTIVATION_DECODE_MIDI_RANGE_MISMATCH")
    if int(matrix_payload.get("midiBinCount", -1)) != activations.shape[1]:
        raise RuntimeError("BASIC_PITCH_ACTIVATION_DECODE_MIDI_BIN_MISMATCH")
    if int(matrix_payload.get("frameCount", -1)) != activations.shape[0]:
        raise RuntimeError("BASIC_PITCH_ACTIVATION_DECODE_FRAME_COUNT_MISMATCH")
    if int(times_payload.get("frameCount", -1)) != len(frame_times):
        raise RuntimeError("BASIC_PITCH_ACTIVATION_DECODE_TIME_COUNT_MISMATCH")

    note_identity = payload.get("noteInferenceIdentity", {})
    recomputed_bundle = _bundle_identity(
        note_identity,
        matrix_payload,
        times_payload,
        minimum_midi,
        maximum_midi,
    )
    if recomputed_bundle != payload.get("inferenceBundleIdentity"):
        raise RuntimeError("BASIC_PITCH_ACTIVATION_BUNDLE_IDENTITY_MISMATCH")

    if evidence is not None:
        expected_note_identity = build_note_identity(note_identity_rows_from_evidence(evidence))
        if note_identity != expected_note_identity:
            raise RuntimeError("BASIC_PITCH_ACTIVATION_NOTE_IDENTITY_MISMATCH")
        evidence_bundle = evidence.get("provenance", {}).get("activationEvidenceIdentity")
        if evidence_bundle is not None and evidence_bundle != recomputed_bundle:
            raise RuntimeError("BASIC_PITCH_ACTIVATION_EVIDENCE_BUNDLE_MISMATCH")

    if expected_bundle_identity is not None and expected_bundle_identity != recomputed_bundle:
        raise RuntimeError("BASIC_PITCH_ACTIVATION_EXPECTED_BUNDLE_MISMATCH")

    return {
        "activations": activations,
        "frameTimesSeconds": frame_times,
        "minimumMidi": minimum_midi,
        "maximumMidi": maximum_midi,
        "noteInferenceIdentity": note_identity,
        "inferenceBundleIdentity": recomputed_bundle,
    }
