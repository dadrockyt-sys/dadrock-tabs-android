#!/usr/bin/env python3

import argparse
import json
import math
from collections import Counter
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from basic_pitch.inference import predict
from basic_pitch.note_creation import model_frames_to_time

from activation_valley_release_evidence import (
    evaluate_activation_spectral_valley,
    fixed_rule_manifest,
)
from basic_pitch_activation_evidence import decode_and_verify_activation_sidecar

CONTRACT = "songsterr-fresh-model-activation-valley-probe-v2"
EXPECTED_STRUCTURE = "fnv1a32:2f493225"
EXPECTED_NOTE_CONTRACT = "songsterr-fresh-isolated-polyphonic-note-evidence-v1"
LEGACY_BASIC_PITCH_MIDI_OFFSET = 21
HOP_LENGTH = 512


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="isolated guitar stem")
    parser.add_argument("--evidence", required=True, help="v2 release output")
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--activation-evidence",
        help=(
            "Optional same-inference Basic Pitch activation sidecar. When supplied, "
            "the probe does not invoke Basic Pitch a second time."
        ),
    )
    return parser.parse_args()


def midi_to_hz(midi):
    return 440.0 * 2.0 ** ((float(midi) - 69.0) / 12.0)


def percentile(values, q):
    return float(np.percentile(values, q)) if values else None


def load_evidence(path):
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if data.get("contract") != EXPECTED_NOTE_CONTRACT or data.get("version") != 1:
        raise RuntimeError("ACTIVATION_PROBE_NOTE_CONTRACT_MISMATCH")
    if data.get("referenceBlind") is not True or data.get("structureFrozen") is not True:
        raise RuntimeError("ACTIVATION_PROBE_REQUIRES_FROZEN_REFERENCE_BLIND_EVIDENCE")
    if data.get("structureIdentity", {}).get("signature") != EXPECTED_STRUCTURE:
        raise RuntimeError("ACTIVATION_PROBE_FROZEN_STRUCTURE_CHANGED")
    if data.get("provenance", {}).get("modelInvoked") is not True:
        raise RuntimeError("ACTIVATION_PROBE_REQUIRES_AUTHORIZED_MODEL_EVIDENCE")
    if data.get("provenance", {}).get("modelNoteEndsUsedAsDuration") is not False:
        raise RuntimeError("ACTIVATION_PROBE_MODEL_END_GUARD_MISSING")
    return data


def normalized_model_identity(note_events):
    rows = []
    for event in note_events:
        if len(event) < 4:
            raise RuntimeError("ACTIVATION_PROBE_BASIC_PITCH_EVENT_SHAPE_INVALID")
        start = float(event[0])
        midi = int(event[2])
        confidence = float(event[3])
        if not math.isfinite(start) or not math.isfinite(confidence):
            raise RuntimeError("ACTIVATION_PROBE_NONFINITE_MODEL_EVENT")
        rows.append((start, midi, confidence))
    return sorted(rows, key=lambda row: (row[0], row[1], row[2]))


def evidence_identity(evidence):
    rows = []
    for onset in evidence.get("onsets", []):
        if onset.get("classification") != "unambiguous" or onset.get("selectedMidi") is None:
            continue
        rows.append((
            float(onset["sourceStart"]),
            int(onset["selectedMidi"]),
            float(onset.get("onsetConfidence", 0.0)),
        ))
    return sorted(rows, key=lambda row: (row[0], row[1], row[2]))


def verify_identity(model_rows, evidence_rows):
    if len(model_rows) != len(evidence_rows):
        raise RuntimeError(
            f"ACTIVATION_PROBE_MODEL_IDENTITY_COUNT_MISMATCH:{len(model_rows)}:{len(evidence_rows)}"
        )
    max_start_delta = 0.0
    max_confidence_delta = 0.0
    for index, (model, evidence) in enumerate(zip(model_rows, evidence_rows)):
        if model[1] != evidence[1]:
            raise RuntimeError(f"ACTIVATION_PROBE_MODEL_MIDI_IDENTITY_MISMATCH:{index}")
        start_delta = abs(model[0] - evidence[0])
        confidence_delta = abs(model[2] - evidence[2])
        max_start_delta = max(max_start_delta, start_delta)
        max_confidence_delta = max(max_confidence_delta, confidence_delta)
        if start_delta > 1e-9 or confidence_delta > 1e-9:
            raise RuntimeError(
                f"ACTIVATION_PROBE_MODEL_EVENT_IDENTITY_MISMATCH:{index}:{start_delta}:{confidence_delta}"
            )
    return max_start_delta, max_confidence_delta


def load_activation_source(a, evidence):
    if a.activation_evidence:
        with open(a.activation_evidence, "r", encoding="utf-8") as handle:
            sidecar = json.load(handle)
        decoded = decode_and_verify_activation_sidecar(sidecar, evidence=evidence)
        evidence_rows = evidence_identity(evidence)
        note_identity = decoded["noteInferenceIdentity"]
        if int(note_identity.get("eventCount", -1)) != len(evidence_rows):
            raise RuntimeError("ACTIVATION_PROBE_SIDECAR_EVENT_COUNT_MISMATCH")
        return {
            "activations": np.asarray(decoded["activations"], dtype=np.float32),
            "frameTimes": np.asarray(decoded["frameTimesSeconds"], dtype=np.float64),
            "minimumMidi": int(decoded["minimumMidi"]),
            "maximumMidi": int(decoded["maximumMidi"]),
            "modelInvokedByProbe": False,
            "sameInferenceSidecarUsed": True,
            "identityProof": {
                "modelEventCount": int(note_identity["eventCount"]),
                "evidenceEventCount": len(evidence_rows),
                "exactMidiIdentityPreserved": True,
                "maxStartDeltaSeconds": 0.0,
                "maxConfidenceDelta": 0.0,
                "identityMethod": "canonical-note-sha256-plus-inference-bundle-sha256",
                "noteIdentitySha256": note_identity["sha256"],
                "inferenceBundleSha256": decoded["inferenceBundleIdentity"]["sha256"],
            },
        }

    model_output, _, note_events = predict(
        a.input,
        onset_threshold=0.5,
        frame_threshold=0.3,
        minimum_note_length=127.7,
        minimum_frequency=midi_to_hz(40),
        maximum_frequency=midi_to_hz(88),
        multiple_pitch_bends=False,
        melodia_trick=True,
    )
    model_rows = normalized_model_identity(note_events)
    evidence_rows = evidence_identity(evidence)
    max_start_delta, max_confidence_delta = verify_identity(model_rows, evidence_rows)
    activations = np.asarray(model_output.get("note"), dtype=np.float32)
    if activations.ndim != 2 or activations.shape[0] == 0 or not np.all(np.isfinite(activations)):
        raise RuntimeError("ACTIVATION_PROBE_NOTE_MATRIX_INVALID")
    frame_times = np.asarray(model_frames_to_time(activations.shape[0]), dtype=np.float64)
    if len(frame_times) != activations.shape[0] or np.any(np.diff(frame_times) <= 0):
        raise RuntimeError("ACTIVATION_PROBE_FRAME_TIME_AXIS_INVALID")
    return {
        "activations": activations,
        "frameTimes": frame_times,
        "minimumMidi": LEGACY_BASIC_PITCH_MIDI_OFFSET,
        "maximumMidi": LEGACY_BASIC_PITCH_MIDI_OFFSET + activations.shape[1] - 1,
        "modelInvokedByProbe": True,
        "sameInferenceSidecarUsed": False,
        "identityProof": {
            "modelEventCount": len(model_rows),
            "evidenceEventCount": len(evidence_rows),
            "exactMidiIdentityPreserved": True,
            "maxStartDeltaSeconds": max_start_delta,
            "maxConfidenceDelta": max_confidence_delta,
            "identityMethod": "second-basic-pitch-run-direct-row-comparison",
            "noteIdentitySha256": None,
            "inferenceBundleSha256": None,
        },
    }


def next_same_pitch(onsets, index, midi):
    for later in onsets[index + 1:]:
        if later.get("classification") == "unambiguous" and int(later.get("selectedMidi", -1)) == midi:
            return float(later["sourceStart"])
    return None


def main():
    a = args()
    evidence = load_evidence(a.evidence)
    activation_source = load_activation_source(a, evidence)
    activations = activation_source["activations"]
    frame_times = activation_source["frameTimes"]
    activation_min_midi = activation_source["minimumMidi"]
    activation_max_midi = activation_source["maximumMidi"]

    y, sr = sf.read(a.input, always_2d=False)
    if y.ndim != 1:
        y = np.mean(y, axis=1)
    y = np.asarray(y, dtype=np.float32)
    harmonic = librosa.effects.harmonic(y, margin=2.0)
    cqt = np.abs(librosa.cqt(
        harmonic,
        sr=sr,
        hop_length=HOP_LENGTH,
        fmin=librosa.midi_to_hz(40),
        n_bins=49,
        bins_per_octave=12,
    ))
    cqt_db = librosa.amplitude_to_db(cqt, ref=np.max, top_db=80.0)

    examined = 0
    candidates = []
    rejections = Counter()
    candidate_midis = Counter()
    onsets = evidence.get("onsets", [])
    for index, onset in enumerate(onsets):
        duration_evidence = onset.get("provenance", {}).get("durationEvidence", {})
        if duration_evidence.get("reason") != "NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK":
            continue
        midi = int(onset["selectedMidi"])
        reattack = next_same_pitch(onsets, index, midi)
        if reattack is None:
            rejections["MISSING_SAME_PITCH_REATTACK"] += 1
            continue
        pitch_index = midi - activation_min_midi
        if midi > activation_max_midi or pitch_index < 0 or pitch_index >= activations.shape[1]:
            rejections["MIDI_OUTSIDE_ACTIVATION_MATRIX"] += 1
            continue
        examined += 1
        candidate, reason = evaluate_activation_spectral_valley(
            trace=activations[:, pitch_index],
            frame_times=frame_times,
            source_start=float(onset["sourceStart"]),
            reattack=reattack,
            cqt_db=cqt_db,
            bin_index=midi - 40,
            sr=sr,
            hop_length=HOP_LENGTH,
        )
        if candidate is None:
            rejections[reason] += 1
            continue

        candidate_midis[midi] += 1
        candidates.append({
            "onsetId": onset.get("onsetId"),
            "midi": midi,
            "sourceStartSeconds": float(onset["sourceStart"]),
            "nextSamePitchReattackSeconds": reattack,
            **candidate,
        })

    spans = [row["observedSpanFromOnsetSeconds"] for row in candidates]
    payload = {
        "contract": CONTRACT,
        "version": 2,
        "descriptiveOnly": True,
        "changesDuration": False,
        "referenceBlind": True,
        "structureFrozen": True,
        "structureIdentity": evidence.get("structureIdentity"),
        "hardGuards": {
            "decodedModelNoteEndsUsed": False,
            "nextOnsetUsedAsDuration": False,
            "writesSourceEnd": False,
            "writesDurationSeconds": False,
            "changesPitchIdentity": False,
            "thresholdSweepUsed": False,
        },
        "identityProof": activation_source["identityProof"],
        "activationSource": {
            "sameInferenceSidecarUsed": activation_source["sameInferenceSidecarUsed"],
            "modelInvokedByProbe": activation_source["modelInvokedByProbe"],
            "minimumMidi": activation_min_midi,
            "maximumMidi": activation_max_midi,
            "frameCount": int(activations.shape[0]),
            "midiBinCount": int(activations.shape[1]),
        },
        "fixedEvidenceRule": fixed_rule_manifest(),
        "diagnostics": {
            "reattackCensoredExaminedCount": examined,
            "corroboratedValleyCandidateCount": len(candidates),
            "corroboratedValleyCandidateRate": len(candidates) / examined if examined else 0.0,
            "rejectionReasonCounts": dict(sorted(rejections.items())),
            "candidateMidiHistogram": {str(k): v for k, v in sorted(candidate_midis.items())},
            "observedSpanSeconds": {
                "mean": float(np.mean(spans)) if spans else None,
                "median": float(np.median(spans)) if spans else None,
                "p10": percentile(spans, 10),
                "p90": percentile(spans, 90),
                "max": float(np.max(spans)) if spans else None,
            },
            "basicPitchFrameCount": int(activations.shape[0]),
        },
        "candidates": candidates,
        "provenance": {
            "source": CONTRACT,
            "audioSource": evidence.get("provenance", {}).get("audioSource"),
            "separationSource": evidence.get("provenance", {}).get("sourceSeparationSource"),
            "activationEvidenceSource": (
                evidence.get("provenance", {}).get("activationEvidenceIdentity")
                if activation_source["sameInferenceSidecarUsed"] else None
            ),
            "upstreamModelInvoked": True,
            "modelInvokedByProbe": activation_source["modelInvokedByProbe"],
            "gpuInvokedByProbe": False,
            "legacyV143ScorerImported": False,
            "professionalScorerUsed": False,
            "referenceTabUsed": False,
        },
    }
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    with open(a.output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    print(json.dumps({
        "contract": CONTRACT,
        "identityProof": payload["identityProof"],
        "activationSource": payload["activationSource"],
        "fixedEvidenceRule": payload["fixedEvidenceRule"],
        "diagnostics": payload["diagnostics"],
        "hardGuards": payload["hardGuards"],
    }))


if __name__ == "__main__":
    main()
