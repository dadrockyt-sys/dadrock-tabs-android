#!/usr/bin/env python3

import argparse
import json
from collections import Counter
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

CONTRACT = "songsterr-fresh-role-boundary-inspection-v2"
HOP_LENGTH = 512
WINDOW_FRAMES = 5
SLOT_KEY_DECIMALS = 9


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--context", required=True)
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


def slot_key(value):
    return round(float(value), SLOT_KEY_DECIMALS)


def load_structure_context(path, evidence):
    with open(path, "r", encoding="utf-8") as handle:
        context = json.load(handle)

    if context.get("contract") != "songsterr-fresh-note-evidence-context-v1":
        raise RuntimeError("ROLE_BOUNDARY_CONTEXT_CONTRACT_MISMATCH")
    if context.get("referenceBlind") is not True or context.get("structureFrozen") is not True:
        raise RuntimeError("ROLE_BOUNDARY_CONTEXT_NOT_FROZEN_REFERENCE_BLIND")
    if context.get("structureAcceptance", {}).get("accepted") is not True:
        raise RuntimeError("ROLE_BOUNDARY_CONTEXT_STRUCTURE_NOT_ACCEPTED")

    context_identity = context.get("structureIdentity") or {}
    evidence_identity = evidence.get("structureIdentity") or {}
    if context_identity.get("signature") != evidence_identity.get("signature"):
        raise RuntimeError("ROLE_BOUNDARY_CONTEXT_STRUCTURE_IDENTITY_MISMATCH")

    structure_map = context.get("structureMap")
    if not isinstance(structure_map, dict):
        raise RuntimeError("ROLE_BOUNDARY_CONTEXT_STRUCTURE_MAP_MISSING")
    return structure_map


def build_structure_slot_lookup(structure_map):
    lookup = {}
    global_beat_index = 0
    for measure in structure_map.get("measures", []):
        measure_number = int(measure.get("measureNumber"))
        for beat in measure.get("beats", []):
            beat_number = int(beat.get("beatNumber"))
            for subdivision_index, value in enumerate(beat.get("subdivisions", [])):
                key = slot_key(value)
                if key in lookup:
                    raise RuntimeError(f"ROLE_BOUNDARY_DUPLICATE_STRUCTURE_SLOT key={key}")
                lookup[key] = {
                    "measureNumber": measure_number,
                    "beatNumber": beat_number,
                    "globalBeatIndex": global_beat_index,
                    "subdivisionIndex": int(subdivision_index),
                    "isBeatStart": subdivision_index == 0,
                }
            global_beat_index += 1
    return lookup


def numeric_summary(values):
    array = np.asarray(values, dtype=float) if values else np.asarray([], dtype=float)
    return {
        "count": int(array.size),
        "mean": float(np.mean(array)) if array.size else None,
        "median": float(np.median(array)) if array.size else None,
        "p10": float(np.percentile(array, 10)) if array.size else None,
        "p90": float(np.percentile(array, 90)) if array.size else None,
        "min": float(np.min(array)) if array.size else None,
        "max": float(np.max(array)) if array.size else None,
    }


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

    structure_map = load_structure_context(args.context, evidence)
    structure_slots = build_structure_slot_lookup(structure_map)

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

    boundary_selected = []
    boundary_measure_numbers = set()
    boundary_beat_start_count = 0
    boundary_multi_candidate_count = 0
    boundary_second_candidate_intervals = Counter()

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
        candidates = onset.get("candidates") or []
        top_candidate = candidates[0] if candidates else None
        selected_at_boundary = onset.get("selectedMidi") == playable_min

        structure_location = structure_slots.get(slot_key(onset["nearestStructureSlot"]))
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
            "selectedAtLowerPlayableBoundary": selected_at_boundary,
            "nearestStructureLocation": structure_location,
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

        if selected_at_boundary:
            boundary_selected_count += 1
            lower_peak_count_histogram[str(len(lower))] += 1

            selected_record = {
                "onsetId": onset.get("onsetId"),
                "sourceStart": float(onset["sourceStart"]),
                "nearestStructureSlot": float(onset["nearestStructureSlot"]),
                "structureLocation": structure_location,
            }
            boundary_selected.append(selected_record)

            if structure_location is not None:
                boundary_measure_numbers.add(structure_location["measureNumber"])
                if structure_location["isBeatStart"]:
                    boundary_beat_start_count += 1

            if len(candidates) > 1:
                boundary_multi_candidate_count += 1
                interval = int(candidates[1]["midi"]) - int(onset["selectedMidi"])
                boundary_second_candidate_intervals[str(interval)] += 1

            if strongest_lower:
                boundary_with_lower_peak_count += 1
                strongest_lower_histogram[str(strongest_lower["midi"])] += 1
                boundary_gap_db.append(boundary["topPlayableMinusLowerGuardDb"])

    boundary_selected.sort(key=lambda item: (item["sourceStart"], item["onsetId"] or ""))
    reattack_gaps = []
    rounded_gap_histogram = Counter()
    beat_gap_histogram = Counter()
    for previous, current in zip(boundary_selected, boundary_selected[1:]):
        gap = float(current["sourceStart"] - previous["sourceStart"])
        reattack_gaps.append(gap)
        rounded_gap_histogram[f"{gap:.2f}"] += 1

        previous_location = previous["structureLocation"]
        current_location = current["structureLocation"]
        if (
            previous_location is not None
            and current_location is not None
            and previous_location["isBeatStart"]
            and current_location["isBeatStart"]
        ):
            beat_gap = int(current_location["globalBeatIndex"] - previous_location["globalBeatIndex"])
            if beat_gap > 0:
                beat_gap_histogram[str(beat_gap)] += 1

    role_boundary_diagnostics = {
        "contract": CONTRACT,
        "descriptiveOnly": True,
        "changesClassification": False,
        "inspectedOnsetCount": inspected_count,
        "selectedAtLowerPlayableBoundaryCount": boundary_selected_count,
        "selectedBoundaryWithLowerGuardPeakCount": boundary_with_lower_peak_count,
        "selectedBoundaryWithoutLowerGuardPeakCount": boundary_selected_count - boundary_with_lower_peak_count,
        "selectedBoundaryLowerGuardPeakCountHistogram": dict(
            sorted(lower_peak_count_histogram.items(), key=lambda item: int(item[0]))
        ),
        "selectedBoundaryStrongestLowerGuardMidiHistogram": dict(
            sorted(strongest_lower_histogram.items(), key=lambda item: int(item[0]))
        ),
        "selectedBoundaryTopMinusLowerGuardDb": numeric_summary(boundary_gap_db),
        "selectedBoundaryStructure": {
            "mappedToFrozenStructureCount": sum(
                1 for item in boundary_selected if item["structureLocation"] is not None
            ),
            "beatStartCount": boundary_beat_start_count,
            "uniqueMeasureCount": len(boundary_measure_numbers),
            "measureNumbers": sorted(boundary_measure_numbers),
        },
        "selectedBoundaryCandidateRelationships": {
            "multiplePlayableCandidateCount": boundary_multi_candidate_count,
            "secondCandidateIntervalSemitoneHistogram": dict(
                sorted(boundary_second_candidate_intervals.items(), key=lambda item: int(item[0]))
            ),
        },
        "selectedBoundarySamePitchReattack": {
            "gapSeconds": numeric_summary(reattack_gaps),
            "roundedHundredthsGapHistogram": dict(
                sorted(rounded_gap_histogram.items(), key=lambda item: float(item[0]))
            ),
            "beatStartToBeatStartGapHistogram": dict(
                sorted(beat_gap_histogram.items(), key=lambda item: int(item[0]))
            ),
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
