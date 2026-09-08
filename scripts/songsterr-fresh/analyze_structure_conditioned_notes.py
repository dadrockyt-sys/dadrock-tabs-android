#!/usr/bin/env python3

import argparse
import bisect
import json
import math
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

CONTRACT = "songsterr-fresh-cpu-note-evidence-v3"
MIDI_MIN_GUITAR = 40
MIDI_MAX_GUITAR = 88
MIDI_MIN_BASS = 28
MIDI_MAX_BASS = 67
SPECTRAL_GUARD_SEMITONES = 12
HOP_LENGTH = 512
CANDIDATE_FLOOR_DB = -18.0
MAX_CANDIDATES = 6
UNAMBIGUOUS_MIN_CONFIDENCE = 0.78
UNAMBIGUOUS_MIN_MARGIN = 0.12
UNAMBIGUOUS_MIN_PROMINENCE_DB = 3.5
UNAMBIGUOUS_SECOND_MAX_DB = -9.0

# A duration is emitted only when the selected pitch itself shows a sustained
# release in its CQT track. A repeated same-pitch attack only censors the search;
# it is never used as an invented note end.
DURATION_MIN_SECONDS = 0.08
DURATION_MAX_SEARCH_SECONDS = 2.50
DURATION_RELEASE_DROP_DB = 14.0
DURATION_RELEASE_SUSTAIN_FRAMES = 4
DURATION_MIN_ATTACK_LEVEL_DB = -45.0


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
    return min(candidates, key=lambda candidate: (abs(value - candidate), candidate))


def robust_onset_confidences(onset_env, onset_frames):
    if len(onset_frames) == 0:
        return []
    sampled = np.asarray([float(onset_env[min(int(frame), len(onset_env) - 1)]) for frame in onset_frames])
    reference = float(np.percentile(sampled, 95)) if sampled.size else 0.0
    if reference <= 0:
        return [0.0 for _ in onset_frames]
    return [float(np.clip(math.sqrt(max(value, 0.0) / reference), 0.0, 1.0)) for value in sampled]


def candidate_confidence(relative_db, prominence_db, onset_confidence):
    amplitude_support = float(np.clip((relative_db - CANDIDATE_FLOOR_DB) / abs(CANDIDATE_FLOOR_DB), 0.0, 1.0))
    prominence_support = float(np.clip(prominence_db / 10.0, 0.0, 1.0))
    value = 0.55 * amplitude_support + 0.25 * prominence_support + 0.20 * onset_confidence
    return float(np.clip(value, 0.0, 1.0))


def extract_candidates(
    cqt_db,
    onset_frame,
    analysis_midi_min,
    playable_midi_min,
    playable_midi_max,
    onset_confidence,
):
    start = max(0, int(onset_frame))
    stop = min(cqt_db.shape[1], start + 5)
    if stop <= start:
        return []

    profile = np.max(cqt_db[:, start:stop], axis=1)
    if not np.any(np.isfinite(profile)):
        return []

    profile = profile - float(np.max(profile))

    candidates = []
    for index in range(1, len(profile) - 1):
        midi = int(analysis_midi_min + index)
        if midi < playable_midi_min or midi > playable_midi_max:
            continue

        value = float(profile[index])
        left = float(profile[index - 1])
        right = float(profile[index + 1])
        if value < left or value < right:
            continue
        if value < CANDIDATE_FLOOR_DB:
            continue

        prominence_db = float(max(0.0, value - max(left, right)))
        confidence = candidate_confidence(value, prominence_db, onset_confidence)
        candidates.append(
            {
                "midi": midi,
                "confidence": confidence,
                "spectralDb": value,
                "prominenceDb": prominence_db,
                "harmonicSupport": None,
                "provenance": {
                    "source": "guarded-harmonic-cqt-local-peak",
                    "windowFrames": stop - start,
                    "confidenceSemantics": "heuristic-not-calibrated-probability",
                    "analysisRangeGuarded": True,
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


def next_same_pitch_attack_frame(onsets, index):
    midi = onsets[index].get("selectedMidi")
    if midi is None:
        return None
    for later in onsets[index + 1 :]:
        if later.get("classification") == "unambiguous" and later.get("selectedMidi") == midi:
            return int(later["_analysisFrame"])
    return None


def duration_evidence_for_onset(onsets, index, cqt_db, analysis_midi_min, sr):
    onset = onsets[index]
    if onset.get("classification") != "unambiguous" or onset.get("selectedMidi") is None:
        return None, "NOT_ELIGIBLE_AMBIGUOUS"

    midi = int(onset["selectedMidi"])
    row = midi - analysis_midi_min
    if row < 0 or row >= cqt_db.shape[0]:
        return None, "SELECTED_MIDI_OUTSIDE_ANALYSIS_RANGE"

    start_frame = int(onset["_analysisFrame"])
    if start_frame < 0 or start_frame >= cqt_db.shape[1]:
        return None, "ONSET_FRAME_OUTSIDE_CQT"

    attack_stop = min(cqt_db.shape[1], start_frame + 5)
    attack_level_db = float(np.max(cqt_db[row, start_frame:attack_stop]))
    if not np.isfinite(attack_level_db) or attack_level_db < DURATION_MIN_ATTACK_LEVEL_DB:
        return None, "SELECTED_PITCH_ATTACK_TOO_WEAK"

    min_frames = max(1, int(math.ceil(DURATION_MIN_SECONDS * sr / HOP_LENGTH)))
    max_search_frames = max(
        min_frames + DURATION_RELEASE_SUSTAIN_FRAMES,
        int(math.ceil(DURATION_MAX_SEARCH_SECONDS * sr / HOP_LENGTH)),
    )
    search_start = start_frame + min_frames
    search_end = min(cqt_db.shape[1], start_frame + max_search_frames)

    same_pitch_frame = next_same_pitch_attack_frame(onsets, index)
    censored_by_same_pitch_reattack = False
    if same_pitch_frame is not None and same_pitch_frame < search_end:
        search_end = same_pitch_frame
        censored_by_same_pitch_reattack = True

    if search_end - search_start < DURATION_RELEASE_SUSTAIN_FRAMES:
        return None, "SEARCH_CENSORED_BEFORE_RELEASE_EVIDENCE"

    release_threshold_db = attack_level_db - DURATION_RELEASE_DROP_DB
    track = cqt_db[row]
    release_start = None
    release_window = None
    last_start = search_end - DURATION_RELEASE_SUSTAIN_FRAMES
    for frame in range(search_start, last_start + 1):
        window = np.asarray(track[frame : frame + DURATION_RELEASE_SUSTAIN_FRAMES], dtype=float)
        if window.size != DURATION_RELEASE_SUSTAIN_FRAMES or not np.all(np.isfinite(window)):
            continue
        if np.all(window <= release_threshold_db):
            release_start = frame
            release_window = window
            break

    if release_start is None:
        reason = (
            "NO_CLEAR_SELECTED_PITCH_RELEASE_BEFORE_CAP"
            if censored_by_same_pitch_reattack
            else "NO_CLEAR_SELECTED_PITCH_RELEASE"
        )
        return None, reason

    source_end = float(librosa.frames_to_time(release_start, sr=sr, hop_length=HOP_LENGTH))
    source_start = float(onset["sourceStart"])
    duration_seconds = source_end - source_start
    if duration_seconds < DURATION_MIN_SECONDS:
        return None, "RELEASE_DURATION_BELOW_MINIMUM"

    release_level_db = float(np.mean(release_window))
    observed_drop_db = attack_level_db - release_level_db
    drop_support = float(np.clip((observed_drop_db - DURATION_RELEASE_DROP_DB) / 12.0, 0.0, 1.0))
    pitch_confidence = float(onset["candidates"][0]["confidence"])
    duration_confidence = float(np.clip(0.50 + 0.25 * drop_support + 0.25 * pitch_confidence, 0.0, 1.0))

    return {
        "sourceEnd": source_end,
        "durationSeconds": duration_seconds,
        "durationConfidence": duration_confidence,
        "releaseDiagnostics": {
            "attackLevelDb": attack_level_db,
            "releaseThresholdDb": release_threshold_db,
            "releaseLevelDb": release_level_db,
            "observedDropDb": observed_drop_db,
            "censoredBySamePitchReattack": censored_by_same_pitch_reattack,
            "confidenceSemantics": "heuristic-not-calibrated-probability",
        },
    }, None


def attach_duration_evidence(onsets, cqt_db, analysis_midi_min, sr):
    reason_counts = {}
    resolved_durations = []
    resolved_confidences = []
    eligible_count = 0

    for index, onset in enumerate(onsets):
        if onset.get("classification") != "unambiguous":
            continue
        eligible_count += 1
        evidence, reason = duration_evidence_for_onset(onsets, index, cqt_db, analysis_midi_min, sr)
        if evidence is None:
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
            onset["provenance"]["durationEvidenceProvided"] = False
            onset["provenance"]["durationEvidenceUnresolvedReason"] = reason
            continue

        onset["sourceEnd"] = evidence["sourceEnd"]
        onset["durationSeconds"] = evidence["durationSeconds"]
        onset["durationConfidence"] = evidence["durationConfidence"]
        onset["provenance"]["durationEvidenceProvided"] = True
        onset["provenance"]["durationEvidenceSource"] = "selected-pitch-sustained-cqt-release"
        onset["provenance"]["durationReleaseDiagnostics"] = evidence["releaseDiagnostics"]
        resolved_durations.append(evidence["durationSeconds"])
        resolved_confidences.append(evidence["durationConfidence"])

    return {
        "eligibleUnambiguousCount": eligible_count,
        "resolvedCount": len(resolved_durations),
        "unresolvedEligibleCount": eligible_count - len(resolved_durations),
        "resolvedRateAmongEligible": len(resolved_durations) / eligible_count if eligible_count else 0.0,
        "unresolvedReasonCounts": reason_counts,
        "meanResolvedDurationSeconds": float(np.mean(resolved_durations)) if resolved_durations else None,
        "medianResolvedDurationSeconds": float(np.median(resolved_durations)) if resolved_durations else None,
        "maxResolvedDurationSeconds": float(np.max(resolved_durations)) if resolved_durations else None,
        "meanDurationConfidence": float(np.mean(resolved_confidences)) if resolved_confidences else None,
        "method": "selected-pitch-sustained-cqt-release",
        "minDurationSeconds": DURATION_MIN_SECONDS,
        "maxSearchSeconds": DURATION_MAX_SEARCH_SECONDS,
        "releaseDropDb": DURATION_RELEASE_DROP_DB,
        "releaseSustainFrames": DURATION_RELEASE_SUSTAIN_FRAMES,
        "minAttackLevelDb": DURATION_MIN_ATTACK_LEVEL_DB,
        "samePitchReattackIsCensorOnly": True,
        "nextOnsetUsedAsDuration": False,
        "confidenceCalibration": "heuristic-not-calibrated-probability",
    }


def summarize(onsets):
    classifications = {"unambiguous": 0, "ambiguous": 0, "no-candidate": 0}
    candidate_count = 0
    displacement = []
    selected_midis = []
    top_midis = []
    for onset in onsets:
        classifications[onset["classification"]] += 1
        candidate_count += len(onset["candidates"])
        displacement.append(abs(onset["sourceStart"] - onset["nearestStructureSlot"]))
        if onset["candidates"]:
            top_midis.append(int(onset["candidates"][0]["midi"]))
        if onset.get("selectedMidi") is not None:
            selected_midis.append(int(onset["selectedMidi"]))
    displacement_np = np.asarray(displacement, dtype=float) if displacement else np.asarray([], dtype=float)

    selected_histogram = {}
    for midi in selected_midis:
        selected_histogram[str(midi)] = selected_histogram.get(str(midi), 0) + 1
    top_histogram = {}
    for midi in top_midis:
        top_histogram[str(midi)] = top_histogram.get(str(midi), 0) + 1

    return {
        "onsetCount": len(onsets),
        "candidateCount": candidate_count,
        "classificationCounts": classifications,
        "unambiguousRate": classifications["unambiguous"] / len(onsets) if onsets else 0.0,
        "meanAbsStructureDisplacementSeconds": float(np.mean(displacement_np)) if displacement_np.size else 0.0,
        "maxAbsStructureDisplacementSeconds": float(np.max(displacement_np)) if displacement_np.size else 0.0,
        "selectedMidiHistogram": selected_histogram,
        "topCandidateMidiHistogram": top_histogram,
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
    playable_midi_min = MIDI_MIN_GUITAR if args.role == "guitar" else MIDI_MIN_BASS
    playable_midi_max = MIDI_MAX_GUITAR if args.role == "guitar" else MIDI_MAX_BASS
    analysis_midi_min = max(0, playable_midi_min - SPECTRAL_GUARD_SEMITONES)
    analysis_midi_max = min(127, playable_midi_max + SPECTRAL_GUARD_SEMITONES)
    n_bins = analysis_midi_max - analysis_midi_min + 1
    cqt = np.abs(
        librosa.cqt(
            harmonic,
            sr=sr,
            hop_length=HOP_LENGTH,
            fmin=librosa.midi_to_hz(analysis_midi_min),
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
        candidates = extract_candidates(
            cqt_db,
            onset_frame,
            analysis_midi_min,
            playable_midi_min,
            playable_midi_max,
            onset_confidence,
        )
        classification, selected_midi = classify(candidates)
        onset = {
            "onsetId": f"cpu-onset-{index}",
            "sourceStart": source_start,
            "nearestStructureSlot": float(nearest_slot(source_start, slots)),
            "onsetConfidence": float(onset_confidence),
            "classification": classification,
            "selectedMidi": selected_midi,
            "candidates": candidates,
            "_analysisFrame": int(onset_frame),
            "provenance": {
                "source": "full-mixture-onset-plus-guarded-harmonic-cqt",
                "structureConditioned": True,
                "durationEvidenceProvided": False,
                "analysisRangeGuarded": True,
            },
        }
        onsets.append(onset)

    duration_diagnostics = attach_duration_evidence(onsets, cqt_db, analysis_midi_min, sr)
    for onset in onsets:
        onset.pop("_analysisFrame", None)

    output = {
        "version": 1,
        "referenceBlind": True,
        "structureFrozen": True,
        "role": args.role,
        "structureIdentity": context["structureIdentity"],
        "capabilities": {
            "roleRelevanceResolved": False,
            "polyphonyResolved": False,
            "durationResolution": "partial-selected-pitch-release-only",
            "instrumentIsolation": "none",
            "confidenceCalibration": "heuristic-not-calibrated-probability",
        },
        "onsets": onsets,
        "diagnostics": {
            **summarize(onsets),
            "audioDurationSeconds": duration,
            "sampleRate": int(sr),
            "hopLength": HOP_LENGTH,
            "playableMidiRange": [playable_midi_min, playable_midi_max],
            "analysisMidiRange": [analysis_midi_min, analysis_midi_max],
            "spectralGuardSemitones": SPECTRAL_GUARD_SEMITONES,
            "candidateFloorDb": CANDIDATE_FLOOR_DB,
            "maxCandidatesPerOnset": MAX_CANDIDATES,
            "unambiguousThresholds": {
                "minTopConfidence": UNAMBIGUOUS_MIN_CONFIDENCE,
                "minConfidenceMargin": UNAMBIGUOUS_MIN_MARGIN,
                "minTopProminenceDb": UNAMBIGUOUS_MIN_PROMINENCE_DB,
                "maxSecondCandidateDb": UNAMBIGUOUS_SECOND_MAX_DB,
            },
            "durationEvidence": duration_diagnostics,
            "confidenceCalibration": "heuristic-not-calibrated-probability",
            "sourceSeparation": "none; harmonic/percussive filtering only",
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
            "note": "Guarded-range CPU spectral evidence with conservative selected-pitch release durations; not instrument-isolated and not an accuracy score.",
        },
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)
        handle.write("\n")

    print(json.dumps({"contract": CONTRACT, "structureIdentity": context["structureIdentity"], "capabilities": output["capabilities"], **output["diagnostics"]}))


if __name__ == "__main__":
    main()
