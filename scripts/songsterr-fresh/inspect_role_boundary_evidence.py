#!/usr/bin/env python3

import argparse
import json
from collections import Counter
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

CONTRACT = "songsterr-fresh-role-boundary-inspection-v1"
HOP_LENGTH = 512
WINDOW_FRAMES = 5


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def local_peaks(profile, midi_min, floor_db):
    peaks = []
    for index in range(1, len(profile) - 1):
        value = float(profile[index])
        left = float(profile[index - 1])
        right = float(profile[index + 1])
        if value < left or value < right or value < floor_db:
            continue
        peaks.append({
            "midi": int(midi_min + index),
            "spectralDb": value,
            "prominenceDb": float(max(0.0, value - max(left, right))),
        })
    peaks.sort(key=lambda item: (-item["spectralDb"], item["midi"]))
    return peaks


def main():
    args = parse_args()
    with open(args.evidence, "r", encoding="utf-8") as handle:
        evidence = json.load(handle)

    provenance = evidence.get("provenance") or {}
    if evidence.get("referenceBlind") is not True or evidence.get("structureFrozen") is not True:
        raise RuntimeError("ROLE_BOUNDARY_INSPECTION_REQUIRES_FROZEN_REFERENCE_BLIND_EVIDENCE")
    if provenance.get("modelInvoked") is not False or provenance.get("gpuInvoked") is not False:
        raise RuntimeError("ROLE_BOUNDARY_INSPECTION_CPU_ONLY")
    if provenance.get("legacyV143ScorerImported") is not False:
        raise RuntimeError("ROLE_BOUNDARY_INSPECTION_LEGACY_SCORER_FORBIDDEN")

    diagnostics = evidence.get("diagnostics") or {}
    analysis_range = diagnostics.get("analysisMidiRange")
    playable_range = diagnostics.get("playableMidiRange")
    if not isinstance(analysis_range, list) or len(analysis_range) != 2:
        raise RuntimeError("ROLE_BOUNDARY_ANALYSIS_RANGE_MISSING")
    if not isinstance(playable_range, list) or len(playable_range) != 2:
        raise RuntimeError("ROLE_BOUNDARY_PLAYABLE_RANGE_MISSING")

    analysis_min, analysis_max = [int(value) for value in analysis_range]
    playable_min, playable_max = [int(value) for value in playable_range]
    floor_db = float(diagnostics.get("candidateFloorDb", -18.0))

    y, sr = sf.read(args.input, always_2d=False)
    if getattr(y, "ndim", 1) != 1:
        y = np.mean(y, axis=1)
    y = np.asarray(y, dtype=np.float32)
    if len(y) == 0 or sr <= 0:
        raise RuntimeError("ROLE_BOUNDARY_AUDIO_EMPTY")

    harmonic = librosa.effects.harmonic(y, margin=2.0)
    n_bins = analysis_max - analysis_min + 1
    cqt = np.abs(librosa.cqt(
        harmonic,
        sr=sr,
        hop_length=HOP_LENGTH,
        fmin=librosa.midi_to_hz(analysis_min),
        n_bins=n_bins,
        bins_per_octave=12,
    ))
    cqt_db = librosa.amplitude_to_db(cqt, ref=np.max, top_db=80.0)

    boundary_selected_count = 0
    boundary_with_lower_peak_count = 0
    boundary_gap_db = []
    strongest_lower_histogram = Counter()
    lower_peak_count_histogram = Counter()
    inspected_count = 0

    for onset in evidence.get("onsets", []):
        frame = int(librosa.time_to_frames(float(onset["sourceStart"]), sr=sr, hop_length=HOP_LENGTH))
        start = max(0, frame)
        stop = min(cqt_db.shape[1], start + WINDOW_FRAMES)
        if stop <= start:
            continue
        profile = np.max(cqt_db[:, start:stop], axis=1)
        if not np.any(np.isfinite(profile)):
            continue
        profile = profile - float(np.max(profile))
        peaks = local_peaks(profile, analysis_min, floor_db)
        lower = [peak for peak in peaks if peak["midi"] < playable_min]
        upper = [peak for peak in peaks if peak["midi"] > playable_max]
        strongest_lower = lower[0] if lower else None
        strongest_upper = upper[0] if upper else None
        top_candidate = (onset.get("candidates") or [None])[0]
        boundary_selected = onset.get("selectedMidi") == playable_min

        boundary = {
            "contract": CONTRACT,
            "descriptiveOnly": True,
            "changesClassification": False,
            "playableLowerBoundaryMidi": playable_min,
            "playableUpperBoundaryMidi": playable_max,
            "lowerGuardPeakCount": len(lower),
            "upperGuardPeakCount": len(upper),
            "strongestLowerGuardPeak": strongest_lower,
            "strongestUpperGuardPeak": strongest_upper,
            "selectedAtLowerPlayableBoundary": boundary_selected,
        }
        if top_candidate and strongest_lower:
            boundary["topPlayableMinusLowerGuardDb"] = float(
                float(top_candidate.get("spectralDb", 0.0)) - strongest_lower["spectralDb"]
            )
            boundary["lowerGuardIntervalSemitones"] = int(
                int(top_candidate["midi"]) - int(strongest_lower["midi"])
            )
        onset.setdefault("provenance", {})["roleBoundaryEvidence"] = boundary
        inspected_count += 1

        if boundary_selected:
            boundary_selected_count += 1
            lower_peak_count_histogram[str(len(lower))] += 1
            if strongest_lower:
                boundary_with_lower_peak_count += 1
                strongest_lower_histogram[str(strongest_lower["midi"])] += 1
                boundary_gap_db.append(boundary["topPlayableMinusLowerGuardDb"])

    role_boundary_diagnostics = {
        "contract": CONTRACT,
        "descriptiveOnly": True,
        "changesClassification": False,
        "inspectedOnsetCount": inspected_count,
        "selectedAtLowerPlayableBoundaryCount": boundary_selected_count,
        "selectedBoundaryWithLowerGuardPeakCount": boundary_with_lower_peak_count,
        "selectedBoundaryWithoutLowerGuardPeakCount": boundary_selected_count - boundary_with_lower_peak_count,
        "selectedBoundaryLowerGuardPeakCountHistogram": dict(sorted(lower_peak_count_histogram.items(), key=lambda item: int(item[0]))),
        "selectedBoundaryStrongestLowerGuardMidiHistogram": dict(sorted(strongest_lower_histogram.items(), key=lambda item: int(item[0]))),
        "selectedBoundaryTopMinusLowerGuardDb": {
            "count": len(boundary_gap_db),
            "mean": float(np.mean(boundary_gap_db)) if boundary_gap_db else None,
            "median": float(np.median(boundary_gap_db)) if boundary_gap_db else None,
            "p10": float(np.percentile(boundary_gap_db, 10)) if boundary_gap_db else None,
            "p90": float(np.percentile(boundary_gap_db, 90)) if boundary_gap_db else None,
            "min": float(np.min(boundary_gap_db)) if boundary_gap_db else None,
            "max": float(np.max(boundary_gap_db)) if boundary_gap_db else None,
        },
        "candidateFloorDb": floor_db,
        "analysisMidiRange": [analysis_min, analysis_max],
        "playableMidiRange": [playable_min, playable_max],
        "confidenceCalibration": "not-applicable-descriptive-spectrum",
    }
    evidence.setdefault("diagnostics", {})["roleBoundaryInspection"] = role_boundary_diagnostics
    evidence.setdefault("provenance", {})["roleBoundaryInspectionSource"] = CONTRACT
    evidence["provenance"]["roleBoundaryInspectionChangesClassification"] = False

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(evidence, handle, indent=2)
        handle.write("\n")

    print(json.dumps(role_boundary_diagnostics))


if __name__ == "__main__":
    main()
