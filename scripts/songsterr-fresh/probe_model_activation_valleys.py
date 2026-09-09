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

CONTRACT = "songsterr-fresh-model-activation-valley-probe-v1"
EXPECTED_STRUCTURE = "fnv1a32:2f493225"
EXPECTED_NOTE_CONTRACT = "songsterr-fresh-isolated-polyphonic-note-evidence-v1"
MIDI_OFFSET = 21
HOP_LENGTH = 512
MIN_DURATION_SECONDS = 0.07
MAX_SEARCH_SECONDS = 4.0
ACTIVATION_LOW_THRESHOLD = 0.20
ACTIVATION_SUSTAINED_LOW_FRAMES = 3
ACTIVATION_MIN_DROP = 0.15
ACTIVATION_ONSET_WINDOW_SECONDS = 0.08
SPECTRAL_MIN_DROP_DB = 6.0
SPECTRAL_FRAMES = 3


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="isolated guitar stem")
    parser.add_argument("--evidence", required=True, help="v2 release output")
    parser.add_argument("--output", required=True)
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


def next_same_pitch(onsets, index, midi):
    for later in onsets[index + 1:]:
        if later.get("classification") == "unambiguous" and int(later.get("selectedMidi", -1)) == midi:
            return float(later["sourceStart"])
    return None


def first_activation_valley(trace, frame_times, source_start, reattack):
    start_time = source_start + MIN_DURATION_SECONDS
    stop_time = min(source_start + MAX_SEARCH_SECONDS, reattack)
    start = int(np.searchsorted(frame_times, start_time, side="left"))
    stop = int(np.searchsorted(frame_times, stop_time, side="left"))
    if start >= stop:
        return None, "NO_ACTIVATION_SEARCH_WINDOW"

    onset_start = int(np.searchsorted(frame_times, source_start, side="left"))
    onset_stop = int(np.searchsorted(
        frame_times,
        source_start + ACTIVATION_ONSET_WINDOW_SECONDS,
        side="right",
    ))
    onset_start = max(0, min(len(trace) - 1, onset_start))
    onset_stop = max(onset_start + 1, min(len(trace), onset_stop))
    onset_peak = float(np.max(trace[onset_start:onset_stop]))

    run = 0
    run_start = None
    saw_sustained_low = False
    saw_drop = False
    for frame in range(start, stop):
        if float(trace[frame]) <= ACTIVATION_LOW_THRESHOLD:
            if run == 0:
                run_start = frame
            run += 1
            if run < ACTIVATION_SUSTAINED_LOW_FRAMES:
                continue
            saw_sustained_low = True
            valley = float(np.mean(trace[run_start:frame + 1]))
            drop = onset_peak - valley
            if drop < ACTIVATION_MIN_DROP:
                continue
            saw_drop = True
            return {
                "frameIndex": int(run_start),
                "timeSeconds": float(frame_times[run_start]),
                "onsetActivationPeak": onset_peak,
                "valleyActivationMean": valley,
                "activationDrop": float(drop),
            }, None
        else:
            run = 0
            run_start = None

    if not saw_sustained_low:
        return None, "NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION"
    if not saw_drop:
        return None, "INSUFFICIENT_ACTIVATION_DROP"
    return None, "NO_QUALIFYING_ACTIVATION_VALLEY"


def main():
    a = args()
    evidence = load_evidence(a.evidence)

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
    if activations.ndim != 2 or activations.shape[0] == 0:
        raise RuntimeError("ACTIVATION_PROBE_NOTE_MATRIX_INVALID")
    if not np.all(np.isfinite(activations)):
        raise RuntimeError("ACTIVATION_PROBE_NOTE_MATRIX_NONFINITE")
    frame_times = np.asarray(model_frames_to_time(activations.shape[0]), dtype=np.float64)
    if len(frame_times) != activations.shape[0] or np.any(np.diff(frame_times) <= 0):
        raise RuntimeError("ACTIVATION_PROBE_FRAME_TIME_AXIS_INVALID")

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
        pitch_index = midi - MIDI_OFFSET
        if pitch_index < 0 or pitch_index >= activations.shape[1]:
            rejections["MIDI_OUTSIDE_ACTIVATION_MATRIX"] += 1
            continue
        examined += 1
        valley, reason = first_activation_valley(
            activations[:, pitch_index],
            frame_times,
            float(onset["sourceStart"]),
            reattack,
        )
        if valley is None:
            rejections[reason] += 1
            continue

        release_frame = int(librosa.time_to_frames(
            valley["timeSeconds"],
            sr=sr,
            hop_length=HOP_LENGTH,
        ))
        release_frame = max(0, min(cqt_db.shape[1] - 1, release_frame))
        release_stop = min(cqt_db.shape[1], release_frame + SPECTRAL_FRAMES)
        release_level = float(np.mean(cqt_db[midi - 40, release_frame:release_stop]))

        onset_frame = int(librosa.time_to_frames(
            float(onset["sourceStart"]),
            sr=sr,
            hop_length=HOP_LENGTH,
        ))
        onset_frame = max(0, min(cqt_db.shape[1] - 1, onset_frame))
        onset_stop = min(cqt_db.shape[1], onset_frame + 5)
        onset_level = float(np.max(cqt_db[midi - 40, onset_frame:onset_stop]))
        spectral_drop = onset_level - release_level
        if spectral_drop < SPECTRAL_MIN_DROP_DB:
            rejections["INSUFFICIENT_SPECTRAL_CORROBORATION"] += 1
            continue

        observed_span = valley["timeSeconds"] - float(onset["sourceStart"])
        if observed_span < MIN_DURATION_SECONDS or valley["timeSeconds"] >= reattack:
            rejections["VALLEY_OUTSIDE_VALID_RELEASE_WINDOW"] += 1
            continue
        candidate_midis[midi] += 1
        candidates.append({
            "onsetId": onset.get("onsetId"),
            "midi": midi,
            "sourceStartSeconds": float(onset["sourceStart"]),
            "nextSamePitchReattackSeconds": reattack,
            "observedValleySeconds": valley["timeSeconds"],
            "observedSpanFromOnsetSeconds": observed_span,
            "onsetActivationPeak": valley["onsetActivationPeak"],
            "valleyActivationMean": valley["valleyActivationMean"],
            "activationDrop": valley["activationDrop"],
            "onsetSpectralDb": onset_level,
            "valleySpectralDb": release_level,
            "spectralDropDb": spectral_drop,
        })

    spans = [row["observedSpanFromOnsetSeconds"] for row in candidates]
    payload = {
        "contract": CONTRACT,
        "version": 1,
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
        },
        "identityProof": {
            "modelEventCount": len(model_rows),
            "evidenceEventCount": len(evidence_rows),
            "exactMidiIdentityPreserved": True,
            "maxStartDeltaSeconds": max_start_delta,
            "maxConfidenceDelta": max_confidence_delta,
        },
        "fixedEvidenceRule": {
            "activationLowThreshold": ACTIVATION_LOW_THRESHOLD,
            "activationSustainedLowFrames": ACTIVATION_SUSTAINED_LOW_FRAMES,
            "activationMinimumDrop": ACTIVATION_MIN_DROP,
            "minimumObservedSpanSeconds": MIN_DURATION_SECONDS,
            "maximumSearchSeconds": MAX_SEARCH_SECONDS,
            "spectralCorroborationMinimumDropDb": SPECTRAL_MIN_DROP_DB,
            "spectralCorroborationFrames": SPECTRAL_FRAMES,
            "thresholdSweepUsed": False,
        },
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
            "modelInvoked": True,
            "gpuInvoked": False,
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
        "fixedEvidenceRule": payload["fixedEvidenceRule"],
        "diagnostics": payload["diagnostics"],
        "hardGuards": payload["hardGuards"],
    }))


if __name__ == "__main__":
    main()
