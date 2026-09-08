#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

CONTRACT = "songsterr-fresh-cpu-spectral-release-evidence-v1"
HOP_LENGTH = 512
SUSTAINED_LOW_FRAMES = 5
MIN_DURATION_SECONDS = 0.07
MAX_SEARCH_SECONDS = 4.0
MIN_ONSET_ABOVE_FLOOR_DB = 12.0
DROP_FROM_ONSET_DB = 18.0
MIN_FLOOR_MARGIN_DB = 6.0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def load_evidence(path):
    with open(path, "r", encoding="utf-8") as handle:
        evidence = json.load(handle)
    if evidence.get("version") != 1:
        raise RuntimeError("RELEASE_EVIDENCE_NOTE_CONTRACT_MISMATCH")
    if evidence.get("referenceBlind") is not True or evidence.get("structureFrozen") is not True:
        raise RuntimeError("RELEASE_EVIDENCE_REQUIRES_FROZEN_REFERENCE_BLIND_INPUT")
    if evidence.get("provenance", {}).get("modelInvoked") is True:
        raise RuntimeError("CPU_RELEASE_CANARY_MODEL_NOT_ALLOWED")
    if evidence.get("provenance", {}).get("gpuInvoked") is True:
        raise RuntimeError("CPU_RELEASE_CANARY_GPU_NOT_ALLOWED")
    return evidence


def sustained_release(profile_db, onset_frame, onset_level_db, pitch_floor_db, sr):
    frame_seconds = HOP_LENGTH / float(sr)
    min_frames = max(1, int(np.ceil(MIN_DURATION_SECONDS / frame_seconds)))
    search_frames = max(1, int(np.ceil(MAX_SEARCH_SECONDS / frame_seconds)))
    start = min(len(profile_db), onset_frame + min_frames)
    stop = min(len(profile_db), onset_frame + search_frames)
    if start >= stop:
        return None

    threshold_db = max(onset_level_db - DROP_FROM_ONSET_DB, pitch_floor_db + MIN_FLOOR_MARGIN_DB)
    run = 0
    run_start = None
    for frame in range(start, stop):
        if float(profile_db[frame]) <= threshold_db:
            if run == 0:
                run_start = frame
            run += 1
            if run >= SUSTAINED_LOW_FRAMES:
                end_frame = run_start
                end_seconds = librosa.frames_to_time(end_frame, sr=sr, hop_length=HOP_LENGTH)
                duration_seconds = float(end_seconds - librosa.frames_to_time(onset_frame, sr=sr, hop_length=HOP_LENGTH))
                if duration_seconds < MIN_DURATION_SECONDS:
                    return None
                low_slice = profile_db[run_start:frame + 1]
                low_level_db = float(np.mean(low_slice))
                observed_drop_db = float(onset_level_db - low_level_db)
                confidence = float(np.clip(
                    0.5 * ((observed_drop_db - 12.0) / 18.0)
                    + 0.5 * ((onset_level_db - pitch_floor_db - MIN_ONSET_ABOVE_FLOOR_DB) / 18.0),
                    0.0,
                    1.0,
                ))
                return {
                    "durationSeconds": duration_seconds,
                    "sourceEnd": float(end_seconds),
                    "durationConfidence": confidence,
                    "thresholdDb": float(threshold_db),
                    "onsetLevelDb": float(onset_level_db),
                    "releaseLevelDb": low_level_db,
                    "pitchFloorDb": float(pitch_floor_db),
                    "observedDropDb": observed_drop_db,
                }
        else:
            run = 0
            run_start = None
    return None


def main():
    args = parse_args()
    evidence = load_evidence(args.evidence)

    y, sr = sf.read(args.input, always_2d=False)
    if y.ndim != 1:
        y = np.mean(y, axis=1)
    y = np.asarray(y, dtype=np.float32)
    if sr <= 0 or len(y) == 0:
        raise RuntimeError("RELEASE_EVIDENCE_AUDIO_EMPTY")

    diagnostics = evidence.get("diagnostics") or {}
    analysis_range = diagnostics.get("analysisMidiRange")
    if not isinstance(analysis_range, list) or len(analysis_range) != 2:
        raise RuntimeError("RELEASE_EVIDENCE_ANALYSIS_RANGE_MISSING")
    analysis_midi_min = int(analysis_range[0])
    analysis_midi_max = int(analysis_range[1])
    n_bins = analysis_midi_max - analysis_midi_min + 1
    if n_bins <= 0:
        raise RuntimeError("RELEASE_EVIDENCE_ANALYSIS_RANGE_INVALID")

    harmonic = librosa.effects.harmonic(y, margin=2.0)
    cqt = np.abs(librosa.cqt(
        harmonic,
        sr=sr,
        hop_length=HOP_LENGTH,
        fmin=librosa.midi_to_hz(analysis_midi_min),
        n_bins=n_bins,
        bins_per_octave=12,
    ))
    cqt_db = librosa.amplitude_to_db(cqt, ref=np.max, top_db=80.0)
    pitch_floors = np.percentile(cqt_db, 20, axis=1)

    resolved = 0
    attempted = 0
    durations = []
    confidences = []

    for onset in evidence.get("onsets", []):
        if onset.get("classification") != "unambiguous" or onset.get("selectedMidi") is None:
            continue
        attempted += 1
        midi = int(onset["selectedMidi"])
        bin_index = midi - analysis_midi_min
        if bin_index < 0 or bin_index >= cqt_db.shape[0]:
            continue

        onset_frame = int(librosa.time_to_frames(float(onset["sourceStart"]), sr=sr, hop_length=HOP_LENGTH))
        onset_frame = max(0, min(cqt_db.shape[1] - 1, onset_frame))
        onset_stop = min(cqt_db.shape[1], onset_frame + 5)
        onset_level_db = float(np.max(cqt_db[bin_index, onset_frame:onset_stop]))
        pitch_floor_db = float(pitch_floors[bin_index])
        if onset_level_db - pitch_floor_db < MIN_ONSET_ABOVE_FLOOR_DB:
            onset.setdefault("provenance", {})["durationEvidence"] = {
                "source": CONTRACT,
                "resolved": False,
                "reason": "INSUFFICIENT_ONSET_TO_FLOOR_CONTRAST",
            }
            continue

        release = sustained_release(
            cqt_db[bin_index],
            onset_frame,
            onset_level_db,
            pitch_floor_db,
            sr,
        )
        if release is None:
            onset.setdefault("provenance", {})["durationEvidence"] = {
                "source": CONTRACT,
                "resolved": False,
                "reason": "NO_CLEAR_SUSTAINED_SPECTRAL_RELEASE",
            }
            continue

        source_start = float(onset["sourceStart"])
        source_end = float(release["sourceEnd"])
        duration_seconds = source_end - source_start
        if duration_seconds < MIN_DURATION_SECONDS:
            onset.setdefault("provenance", {})["durationEvidence"] = {
                "source": CONTRACT,
                "resolved": False,
                "reason": "RELEASE_TOO_CLOSE_TO_ONSET",
            }
            continue

        onset["sourceEnd"] = source_end
        onset["durationSeconds"] = duration_seconds
        onset["durationConfidence"] = release["durationConfidence"]
        onset.setdefault("provenance", {})["durationEvidence"] = {
            "source": CONTRACT,
            "resolved": True,
            "method": "selected-pitch-sustained-spectral-decay",
            "nextOnsetUsedAsDuration": False,
            "onsetLevelDb": release["onsetLevelDb"],
            "releaseLevelDb": release["releaseLevelDb"],
            "pitchFloorDb": release["pitchFloorDb"],
            "observedDropDb": release["observedDropDb"],
            "thresholdDb": release["thresholdDb"],
        }
        resolved += 1
        durations.append(duration_seconds)
        confidences.append(release["durationConfidence"])

    if attempted > 0 and resolved == attempted:
        duration_resolution = "complete"
    elif resolved > 0:
        duration_resolution = "partial"
    else:
        duration_resolution = "none"

    capabilities = evidence.setdefault("capabilities", {})
    capabilities["durationResolution"] = duration_resolution
    capabilities["durationMethod"] = "selected-pitch-sustained-spectral-decay"

    evidence.setdefault("diagnostics", {})["releaseEvidence"] = {
        "contract": CONTRACT,
        "attemptedPromotedOnsetCount": attempted,
        "resolvedPromotedOnsetCount": resolved,
        "unresolvedPromotedOnsetCount": attempted - resolved,
        "resolutionRate": resolved / attempted if attempted else 0.0,
        "meanResolvedDurationSeconds": float(np.mean(durations)) if durations else 0.0,
        "medianResolvedDurationSeconds": float(np.median(durations)) if durations else 0.0,
        "meanDurationConfidence": float(np.mean(confidences)) if confidences else 0.0,
        "minimumDurationSeconds": MIN_DURATION_SECONDS,
        "maximumSearchSeconds": MAX_SEARCH_SECONDS,
        "sustainedLowFrames": SUSTAINED_LOW_FRAMES,
        "minimumOnsetAboveFloorDb": MIN_ONSET_ABOVE_FLOOR_DB,
        "dropFromOnsetDb": DROP_FROM_ONSET_DB,
        "minimumFloorMarginDb": MIN_FLOOR_MARGIN_DB,
        "nextOnsetUsedAsDuration": False,
        "confidenceCalibration": "heuristic-not-calibrated-probability",
    }
    evidence.setdefault("provenance", {})["durationEvidenceSource"] = CONTRACT
    evidence["provenance"]["durationEvidenceReferenceBlind"] = True
    evidence["provenance"]["durationEvidenceModelInvoked"] = False
    evidence["provenance"]["durationEvidenceGpuInvoked"] = False

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(evidence, handle, indent=2)
        handle.write("\n")

    print(json.dumps({
        "contract": CONTRACT,
        "capabilities": capabilities,
        "releaseEvidence": evidence["diagnostics"]["releaseEvidence"],
    }))


if __name__ == "__main__":
    main()
