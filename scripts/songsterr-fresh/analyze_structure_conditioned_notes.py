#!/usr/bin/env python3

import argparse
import bisect
import json
import math
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

CONTRACT = "songsterr-fresh-cpu-note-evidence-v1"
MIDI_MIN_GUITAR = 40
MIDI_MAX_GUITAR = 88
MIDI_MIN_BASS = 28
MIDI_MAX_BASS = 67
HOP_LENGTH = 512
CANDIDATE_FLOOR_DB = -18.0
MAX_CANDIDATES = 6
UNAMBIGUOUS_MIN_CONFIDENCE = 0.78
UNAMBIGUOUS_MIN_MARGIN = 0.12
UNAMBIGUOUS_MIN_PROMINENCE_DB = 3.5
UNAMBIGUOUS_SECOND_MAX_DB = -9.0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--context", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--role", choices=("guitar", "bass"), default="guitar")
    parser.add_argument("--audio-source", required=True)
    parser.add_argument("--expected-structure-signature", required=True)
    return parser.parse_args()


def load_context(path, expected_signature):
    with open(path, "r", encoding="utf-8") as handle:
        context = json.load(handle)

    if context.get("contract") != "songsterr-fresh-note-evidence-context-v1":
        raise RuntimeError("NOTE_EVIDENCE_CONTEXT_CONTRACT_MISMATCH")
    if context.get("referenceBlind") is not True or context.get("structureFrozen") is not True:
        raise RuntimeError("NOTE_EVIDENCE_CONTEXT_NOT_FROZEN_REFERENCE_BLIND")
    if context.get("structureAcceptance", {}).get("accepted") is not True:
        raise RuntimeError("NOTE_EVIDENCE_CONTEXT_STRUCTURE_NOT_ACCEPTED")

    identity = context.get("structureIdentity") or {}
    if identity.get("contract") != "songsterr-fresh-frozen-structure-identity-v1":
        raise RuntimeError("NOTE_EVIDENCE_CONTEXT_IDENTITY_CONTRACT_MISMATCH")
    if identity.get("signature") != expected_signature:
        raise RuntimeError(
            f"NOTE_EVIDENCE_FROZEN_STRUCTURE_SIGNATURE_MISMATCH expected={expected_signature} actual={identity.get('signature')}"
        )

    structure_map = context.get("structureMap")
    if not isinstance(structure_map, dict):
        raise RuntimeError("NOTE_EVIDENCE_CONTEXT_STRUCTURE_MAP_MISSING")
    return context


def structure_slots(structure_map):
    slots = []
    for measure in structure_map.get("measures", []):
        for beat in measure.get("beats", []):
            slots.extend(float(value) for value in beat.get("subdivisions", []))
    slots.append(float(structure_map["durationSeconds"]))
    slots = sorted(set(slots))
    if not slots:
        raise RuntimeError("NOTE_EVIDENCE_STRUCTURE_HAS_NO_SLOTS")
    return slots


def nearest_slot(value, slots):
    index = bisect.bisect_left(slots, value)
    candidates = []
    if index < len(slots):
        candidates.append(slots[index])
    if index > 0:
        candidates.append(slots[index - 1])
    if not candidates:
        return slots[0]
    # Match structureMap.mjs: nearest distance, then earlier slot on an exact tie.
    return min(candidates, key=lambda candidate: (abs(value - candidate), candidate))


def robust_onset_confidences(onset_env, onset_frames):
    if len(onset_frames) == 0:
        return []
    sampled = np.asarray([float(onset_env[min(int(frame), len(onset_env) - 1)]) for frame in onset_frames])
    reference = float(np.percentile(sampled, 95)) if sampled.size else 0.0
    if reference <= 0:
        return [0.0 for _ in onset_frames]
    return [float(np.clip(math.sqrt(max(value, 0.0) / reference), 0.0, 1.0)) for value in sampled]


def local_peak_indices(values):
    peaks = []
    for index, value in enumerate(values):
        left = values[index - 1] if index > 0 else -np.inf
        right = values[index + 1] if index + 1 < len(values) else -np.inf
        if value >= left and value >= right:
            peaks.append(index)
    return peaks


def candidate_confidence(relative_db, prominence_db, onset_confidence):
    amplitude_support = float(np.clip((relative_db - CANDIDATE_FLOOR_DB) / abs(CANDIDATE_FLOOR_DB), 0.0, 1.0))
    prominence_support = float(np.clip(prominence_db / 10.0, 0.0, 1.0))
    value = 0.55 * amplitude_support + 0.25 * prominence_support + 0.20 * onset_confidence
    return float(np.clip(value, 0.0, 1.0))


def extract_candidates(cqt_db, onset_frame, midi_min, onset_confidence):
    start = max(0, int(onset_frame))
    stop = min(cqt_db.shape[1], start + 5)
    if stop <= start:
        return []

    profile = np.max(cqt_db[:, start:stop], axis=1)
    if not np.any(np.isfinite(profile)):
        return []
    profile = profile - float(np.max(profile))

    peaks = local_peak_indices(profile)
    candidates = []
    for index in peaks:
        relative_db = float(profile[index])
        if relative_db < CANDIDATE_FLOOR_DB:
            continue
        neighbors = []
        if index > 0:
            neighbors.append(float(profile[index - 1]))
        if index + 1 < len(profile):
            neighbors.append(float(profile[index + 1]))
        neighbor_db = max(neighbors) if neighbors else CANDIDATE_FLOOR_DB
        prominence_db = float(max(0.0, relative_db - neighbor_db))
        confidence = candidate_confidence(relative_db, prominence_db, onset_confidence)
        candidates.append(
            {
                "midi": int(midi_min + index),
                "confidence": confidence,
                "spectralDb": relative_db,
                "prominenceDb": prominence_db,
                "harmonicSupport": None,
                "provenance": {
                    "source": "harmonic-cqt-local-peak",
                    "windowFrames": stop - start,
                    "confidenceSemantics": "heuristic-not-calibrated-probability",
                },
            }
        )

    candidates.sort(key=lambda item: (-item["confidence"], item["midi"]))
    return candidates[:MAX_CANDIDATES]


def classify(candidates):
    if not candidates:
        return "no-candidate", None

    top = candidates[0]
    second = candidates[1] if len(candidates) > 1 else None
    margin = top["confidence"] - (second["confidence"] if second else 0.0)
    second_db = second["spectralDb"] if second else -120.0

    unambiguous = (
        top["confidence"] >= UNAMBIGUOUS_MIN_CONFIDENCE
        and margin >= UNAMBIGUOUS_MIN_MARGIN
        and top["prominenceDb"] >= UNAMBIGUOUS_MIN_PROMINENCE_DB
        and second_db <= UNAMBIGUOUS_SECOND_MAX_DB
    )
    return ("unambiguous", top["midi"]) if unambiguous else ("ambiguous", None)


def summarize(onsets):
    classifications = {"unambiguous": 0, "ambiguous": 0, "no-candidate": 0}
    candidate_count = 0
    displacement = []
    for onset in onsets:
        classifications[onset["classification"]] += 1
        candidate_count += len(onset["candidates"])
        displacement.append(abs(onset["sourceStart"] - onset["nearestStructureSlot"]))
    displacement_np = np.asarray(displacement, dtype=float) if displacement else np.asarray([], dtype=float)
    return {
        "onsetCount": len(onsets),
        "candidateCount": candidate_count,
        "classificationCounts": classifications,
        "unambiguousRate": classifications["unambiguous"] / len(onsets) if onsets else 0.0,
        "meanAbsStructureDisplacementSeconds": float(np.mean(displacement_np)) if displacement_np.size else 0.0,
        "maxAbsStructureDisplacementSeconds": float(np.max(displacement_np)) if displacement_np.size else 0.0,
    }


def main():
    args = parse_args()
    context = load_context(args.context, args.expected_structure_signature)
    structure_map = context["structureMap"]
    slots = structure_slots(structure_map)

    y, sr = sf.read(args.input, always_2d=False)
    if y.ndim != 1:
        y = np.mean(y, axis=1)
    y = np.asarray(y, dtype=np.float32)
    if sr <= 0 or len(y) == 0:
        raise RuntimeError("NOTE_EVIDENCE_AUDIO_EMPTY")

    duration = len(y) / float(sr)
    structure_duration = float(structure_map["durationSeconds"])
    if abs(duration - structure_duration) > 0.10:
        raise RuntimeError(
            f"NOTE_EVIDENCE_AUDIO_STRUCTURE_DURATION_MISMATCH audio={duration} structure={structure_duration}"
        )

    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP_LENGTH)
    onset_frames = librosa.onset.onset_detect(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=HOP_LENGTH,
        units="frames",
        backtrack=False,
    )
    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=HOP_LENGTH)
    onset_confidences = robust_onset_confidences(onset_env, onset_frames)

    harmonic = librosa.effects.harmonic(y, margin=2.0)
    midi_min = MIDI_MIN_GUITAR if args.role == "guitar" else MIDI_MIN_BASS
    midi_max = MIDI_MAX_GUITAR if args.role == "guitar" else MIDI_MAX_BASS
    n_bins = midi_max - midi_min + 1
    cqt = np.abs(
        librosa.cqt(
            harmonic,
            sr=sr,
            hop_length=HOP_LENGTH,
            fmin=librosa.midi_to_hz(midi_min),
            n_bins=n_bins,
            bins_per_octave=12,
        )
    )
    cqt_db = librosa.amplitude_to_db(cqt, ref=np.max, top_db=80.0)

    onsets = []
    for index, (onset_frame, onset_time, onset_confidence) in enumerate(
        zip(onset_frames, onset_times, onset_confidences)
    ):
        source_start = float(onset_time)
        if source_start < 0 or source_start > structure_duration:
            continue
        candidates = extract_candidates(cqt_db, onset_frame, midi_min, onset_confidence)
        classification, selected_midi = classify(candidates)
        onset = {
            "onsetId": f"cpu-onset-{index}",
            "sourceStart": source_start,
            "nearestStructureSlot": float(nearest_slot(source_start, slots)),
            "onsetConfidence": float(onset_confidence),
            "classification": classification,
            "selectedMidi": selected_midi,
            "candidates": candidates,
            "provenance": {
                "source": "full-mixture-onset-plus-harmonic-cqt",
                "structureConditioned": True,
                "durationEvidenceProvided": False,
            },
        }
        onsets.append(onset)

    output = {
        "version": 1,
        "referenceBlind": True,
        "structureFrozen": True,
        "role": args.role,
        "structureIdentity": context["structureIdentity"],
        "onsets": onsets,
        "diagnostics": {
            **summarize(onsets),
            "audioDurationSeconds": duration,
            "sampleRate": int(sr),
            "hopLength": HOP_LENGTH,
            "midiRange": [midi_min, midi_max],
            "candidateFloorDb": CANDIDATE_FLOOR_DB,
            "maxCandidatesPerOnset": MAX_CANDIDATES,
            "unambiguousThresholds": {
                "minTopConfidence": UNAMBIGUOUS_MIN_CONFIDENCE,
                "minConfidenceMargin": UNAMBIGUOUS_MIN_MARGIN,
                "minTopProminenceDb": UNAMBIGUOUS_MIN_PROMINENCE_DB,
                "maxSecondCandidateDb": UNAMBIGUOUS_SECOND_MAX_DB,
            },
            "confidenceCalibration": "heuristic-not-calibrated-probability",
            "sourceSeparation": "none; harmonic/percussive filtering only",
            "durationInference": "none",
        },
        "provenance": {
            "source": CONTRACT,
            "audioSource": args.audio_source,
            "referenceBlind": True,
            "structureConditioned": True,
            "structureFrozen": True,
            "modelInvoked": False,
            "gpuInvoked": False,
            "legacyV143ScorerImported": False,
            "roleConditioning": args.role,
            "note": "Baseline CPU spectral evidence from the full mixture; not instrument-isolated and not an accuracy score.",
        },
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)
        handle.write("\n")

    print(json.dumps({"contract": CONTRACT, "structureIdentity": context["structureIdentity"], **output["diagnostics"]}))


if __name__ == "__main__":
    main()
