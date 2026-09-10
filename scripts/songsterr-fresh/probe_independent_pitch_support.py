#!/usr/bin/env python3

import argparse
import hashlib
import json
import re
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from basic_pitch_activation_evidence import build_note_identity, note_identity_rows_from_evidence


CONTRACT = "songsterr-fresh-independent-pitch-support-probe-v1"
EXPECTED_EVIDENCE_CONTRACT = "songsterr-fresh-isolated-polyphonic-note-evidence-v1"
ONSET_WINDOW_SECONDS = 0.080
SEMITONE_OFFSETS = (-2, -1, 1, 2)
OCTAVE_OFFSETS = (-12, 12)
PITCH_FLOOR_PERCENTILE = 20.0
HOP_LENGTH = 512
BINS_PER_OCTAVE = 12


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Exact isolated guitar-stem WAV used upstream.")
    parser.add_argument("--evidence", required=True, help="Duration-free model note-evidence JSON.")
    parser.add_argument("--output", required=True, help="Descriptive probe JSON output.")
    return parser.parse_args()


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def finite(value, label):
    number = float(value)
    if not np.isfinite(number):
        raise RuntimeError(f"PITCH_SUPPORT_NONFINITE:{label}")
    return number


def load_and_verify_evidence(path, *, stem_sha256):
    with open(path, "r", encoding="utf-8") as handle:
        evidence = json.load(handle)

    if (
        evidence.get("contract") != EXPECTED_EVIDENCE_CONTRACT
        or evidence.get("version") != 1
        or evidence.get("referenceBlind") is not True
        or evidence.get("structureFrozen") is not True
        or evidence.get("role") != "guitar"
    ):
        raise RuntimeError("PITCH_SUPPORT_EVIDENCE_CONTRACT_MISMATCH")

    provenance = evidence.get("provenance", {})
    if (
        provenance.get("referenceBlind") is not True
        or provenance.get("structureFrozen") is not True
        or provenance.get("modelInvoked") is not True
        or provenance.get("legacyV143ScorerImported") is not False
        or provenance.get("professionalScorerUsed") is not False
        or provenance.get("referenceTabUsed") is not False
        or provenance.get("modelNoteEndsUsedAsDuration") is not False
    ):
        raise RuntimeError("PITCH_SUPPORT_EVIDENCE_PROVENANCE_INVALID")

    separation_source = provenance.get("sourceSeparationSource")
    if not isinstance(separation_source, str):
        raise RuntimeError("PITCH_SUPPORT_SEPARATION_SOURCE_MISSING")
    match = re.search(r"@sha256:([0-9a-f]{64})$", separation_source)
    if match is None:
        raise RuntimeError("PITCH_SUPPORT_SEPARATION_SHA_MISSING")
    if match.group(1) != stem_sha256:
        raise RuntimeError("PITCH_SUPPORT_STEM_IDENTITY_MISMATCH")

    onsets = evidence.get("onsets")
    if not isinstance(onsets, list) or not onsets:
        raise RuntimeError("PITCH_SUPPORT_EVIDENCE_EMPTY")

    for index, onset in enumerate(onsets):
        if onset.get("classification") != "unambiguous" or onset.get("selectedMidi") is None:
            raise RuntimeError(f"PITCH_SUPPORT_REQUIRES_SELECTED_MIDI:index={index}")
        if onset.get("durationSeconds") is not None or onset.get("sourceEnd") is not None:
            raise RuntimeError(f"PITCH_SUPPORT_REQUIRES_DURATION_FREE_INPUT:index={index}")
        midi = int(onset["selectedMidi"])
        if midi < 0 or midi > 127:
            raise RuntimeError(f"PITCH_SUPPORT_MIDI_INVALID:index={index}")
        finite(onset["sourceStart"], f"sourceStart:{index}")
        finite(onset.get("onsetConfidence", 0.0), f"onsetConfidence:{index}")

    recomputed_identity = build_note_identity(note_identity_rows_from_evidence(evidence))
    diagnostic_identity = evidence.get("diagnostics", {}).get("noteInferenceIdentity")
    provenance_identity = provenance.get("noteInferenceIdentity")
    for label, identity in (("diagnostics", diagnostic_identity), ("provenance", provenance_identity)):
        if not isinstance(identity, dict) or identity != recomputed_identity:
            raise RuntimeError(f"PITCH_SUPPORT_NOTE_IDENTITY_MISMATCH:{label}")

    return evidence, recomputed_identity, separation_source


def summary(values):
    array = np.asarray([float(value) for value in values if value is not None], dtype=np.float64)
    if array.size == 0:
        return {"count": 0}
    if not np.all(np.isfinite(array)):
        raise RuntimeError("PITCH_SUPPORT_SUMMARY_NONFINITE")
    return {
        "count": int(array.size),
        "mean": float(np.mean(array)),
        "min": float(np.min(array)),
        "p10": float(np.quantile(array, 0.10)),
        "p25": float(np.quantile(array, 0.25)),
        "median": float(np.quantile(array, 0.50)),
        "p75": float(np.quantile(array, 0.75)),
        "p90": float(np.quantile(array, 0.90)),
        "max": float(np.max(array)),
    }


def rank_histogram(values):
    counts = {}
    for value in values:
        key = str(int(value))
        counts[key] = counts.get(key, 0) + 1
    return {key: counts[key] for key in sorted(counts, key=int)}


def fixed_window_level(cqt_db, *, bin_index, start_frame, stop_frame):
    segment = cqt_db[bin_index, start_frame:stop_frame]
    if segment.size == 0:
        segment = cqt_db[bin_index, start_frame:start_frame + 1]
    return float(np.max(segment))


def ranked_position(levels, selected_midi):
    ordered = sorted(
        levels.items(),
        key=lambda item: (-float(item[1]), abs(int(item[0]) - int(selected_midi)), int(item[0])),
    )
    for index, (midi, _level) in enumerate(ordered):
        if int(midi) == int(selected_midi):
            return index + 1
    raise RuntimeError("PITCH_SUPPORT_SELECTED_MIDI_MISSING_FROM_RANK")


def main():
    args = parse_args()
    input_path = Path(args.input)
    stem_sha256 = sha256_file(input_path)
    evidence, note_identity, separation_source = load_and_verify_evidence(
        args.evidence,
        stem_sha256=stem_sha256,
    )

    y, sr = sf.read(input_path, always_2d=False)
    if getattr(y, "ndim", 0) == 2:
        y = np.mean(y, axis=1)
    y = np.asarray(y, dtype=np.float32)
    if sr <= 0 or y.size == 0 or not np.all(np.isfinite(y)):
        raise RuntimeError("PITCH_SUPPORT_AUDIO_INVALID")

    onsets = evidence["onsets"]
    selected_midis = [int(onset["selectedMidi"]) for onset in onsets]
    cqt_min_midi = max(0, min(selected_midis) + min(OCTAVE_OFFSETS))
    cqt_max_midi = min(127, max(selected_midis) + max(OCTAVE_OFFSETS))
    n_bins = cqt_max_midi - cqt_min_midi + 1
    if n_bins <= 0:
        raise RuntimeError("PITCH_SUPPORT_CQT_RANGE_INVALID")

    # This is independent audio-domain DSP. It does not consume Basic Pitch activations,
    # decoded note ends, reference tabs, or any reference/scorer signal.
    harmonic = librosa.effects.harmonic(y, margin=2.0)
    cqt = np.abs(librosa.cqt(
        harmonic,
        sr=sr,
        hop_length=HOP_LENGTH,
        fmin=librosa.midi_to_hz(cqt_min_midi),
        n_bins=n_bins,
        bins_per_octave=BINS_PER_OCTAVE,
    ))
    if cqt.ndim != 2 or cqt.shape[0] != n_bins or cqt.shape[1] == 0:
        raise RuntimeError("PITCH_SUPPORT_CQT_INVALID")
    cqt_db = librosa.amplitude_to_db(cqt, ref=np.max, top_db=80.0)
    pitch_floors = np.percentile(cqt_db, PITCH_FLOOR_PERCENTILE, axis=1)

    event_rows = []
    selected_above_floor = []
    semitone_margins = []
    local_ranks = []
    octave_below_margins = []
    octave_above_margins = []
    octave_ranks = []
    best_alternative_margins = []

    for onset in onsets:
        onset_id = str(onset["onsetId"])
        source_start = finite(onset["sourceStart"], f"sourceStart:{onset_id}")
        selected_midi = int(onset["selectedMidi"])
        model_confidence = finite(onset.get("onsetConfidence", 0.0), f"confidence:{onset_id}")

        start_frame = int(librosa.time_to_frames(
            source_start,
            sr=sr,
            hop_length=HOP_LENGTH,
        ))
        stop_frame = int(librosa.time_to_frames(
            source_start + ONSET_WINDOW_SECONDS,
            sr=sr,
            hop_length=HOP_LENGTH,
        )) + 1
        start_frame = max(0, min(cqt_db.shape[1] - 1, start_frame))
        stop_frame = max(start_frame + 1, min(cqt_db.shape[1], stop_frame))

        def level_for(midi):
            if midi < cqt_min_midi or midi > cqt_max_midi:
                return None
            return fixed_window_level(
                cqt_db,
                bin_index=midi - cqt_min_midi,
                start_frame=start_frame,
                stop_frame=stop_frame,
            )

        selected_db = level_for(selected_midi)
        if selected_db is None:
            raise RuntimeError(f"PITCH_SUPPORT_SELECTED_BIN_MISSING:{onset_id}")
        floor_db = float(pitch_floors[selected_midi - cqt_min_midi])
        above_floor_db = float(selected_db - floor_db)

        semitone_levels = {selected_midi: selected_db}
        for offset in SEMITONE_OFFSETS:
            midi = selected_midi + offset
            level = level_for(midi)
            if level is not None:
                semitone_levels[midi] = level
        semitone_neighbors = {
            midi: level for midi, level in semitone_levels.items() if midi != selected_midi
        }
        best_neighbor_midi, best_neighbor_db = max(
            semitone_neighbors.items(),
            key=lambda item: (float(item[1]), -abs(int(item[0]) - selected_midi), -int(item[0])),
        )
        semitone_margin_db = float(selected_db - best_neighbor_db)
        local_rank = ranked_position(semitone_levels, selected_midi)

        octave_levels = {selected_midi: selected_db}
        octave_below_db = level_for(selected_midi - 12)
        octave_above_db = level_for(selected_midi + 12)
        if octave_below_db is not None:
            octave_levels[selected_midi - 12] = octave_below_db
        if octave_above_db is not None:
            octave_levels[selected_midi + 12] = octave_above_db
        octave_rank = ranked_position(octave_levels, selected_midi)

        octave_below_margin_db = (
            None if octave_below_db is None else float(selected_db - octave_below_db)
        )
        octave_above_margin_db = (
            None if octave_above_db is None else float(selected_db - octave_above_db)
        )

        alternative_levels = dict(semitone_neighbors)
        if octave_below_db is not None:
            alternative_levels[selected_midi - 12] = octave_below_db
        if octave_above_db is not None:
            alternative_levels[selected_midi + 12] = octave_above_db
        best_alternative_midi, best_alternative_db = max(
            alternative_levels.items(),
            key=lambda item: (float(item[1]), -abs(int(item[0]) - selected_midi), -int(item[0])),
        )
        best_alternative_margin_db = float(selected_db - best_alternative_db)

        row = {
            "onsetId": onset_id,
            "sourceStart": source_start,
            "selectedMidi": selected_midi,
            "modelConfidence": model_confidence,
            "fixedOnsetWindow": {
                "startSeconds": source_start,
                "stopSeconds": float(source_start + ONSET_WINDOW_SECONDS),
                "startFrame": start_frame,
                "stopFrameExclusive": stop_frame,
            },
            "selectedPitch": {
                "spectralDb": selected_db,
                "pitchFloorDb": floor_db,
                "aboveFloorDb": above_floor_db,
            },
            "localSemitoneComparison": {
                "offsetsSemitones": list(SEMITONE_OFFSETS),
                "rankAmongSelectedAndNeighbors": local_rank,
                "bestNeighborMidi": int(best_neighbor_midi),
                "bestNeighborSpectralDb": float(best_neighbor_db),
                "selectedMinusBestNeighborDb": semitone_margin_db,
                "levelsDb": {str(midi): float(level) for midi, level in sorted(semitone_levels.items())},
            },
            "octaveComparison": {
                "offsetsSemitones": list(OCTAVE_OFFSETS),
                "rankAmongAvailableSelectedAndOctaves": octave_rank,
                "octaveBelowSpectralDb": octave_below_db,
                "octaveAboveSpectralDb": octave_above_db,
                "selectedMinusOctaveBelowDb": octave_below_margin_db,
                "selectedMinusOctaveAboveDb": octave_above_margin_db,
            },
            "bestAlternative": {
                "midi": int(best_alternative_midi),
                "spectralDb": float(best_alternative_db),
                "selectedMinusBestAlternativeDb": best_alternative_margin_db,
            },
        }
        event_rows.append(row)
        selected_above_floor.append(above_floor_db)
        semitone_margins.append(semitone_margin_db)
        local_ranks.append(local_rank)
        octave_below_margins.append(octave_below_margin_db)
        octave_above_margins.append(octave_above_margin_db)
        octave_ranks.append(octave_rank)
        best_alternative_margins.append(best_alternative_margin_db)

    payload = {
        "contract": CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "role": "guitar",
        "descriptiveOnly": True,
        "method": {
            "domain": "isolated-guitar-audio-cqt",
            "harmonicPreprocessing": "librosa.effects.harmonic(margin=2.0)",
            "hopLength": HOP_LENGTH,
            "binsPerOctave": BINS_PER_OCTAVE,
            "onsetWindowSeconds": ONSET_WINDOW_SECONDS,
            "semitoneComparisonOffsets": list(SEMITONE_OFFSETS),
            "octaveComparisonOffsets": list(OCTAVE_OFFSETS),
            "pitchFloorPercentile": PITCH_FLOOR_PERCENTILE,
            "cqtMinimumMidi": cqt_min_midi,
            "cqtMaximumMidi": cqt_max_midi,
            "thresholdSweepUsed": False,
            "acceptanceThresholdDefined": False,
        },
        "identityProof": {
            "inputStemSha256": stem_sha256,
            "declaredSeparationSource": separation_source,
            "declaredStemSha256MatchesInput": True,
            "noteInferenceIdentity": note_identity,
            "evidenceEventCount": len(onsets),
            "reportedEventCount": len(event_rows),
            "exactEventIdentityPreserved": True,
        },
        "summary": {
            "eventCount": len(event_rows),
            "selectedPitchAboveFloorDb": summary(selected_above_floor),
            "selectedMinusBestSemitoneNeighborDb": summary(semitone_margins),
            "localSemitoneRankHistogram": rank_histogram(local_ranks),
            "selectedMinusOctaveBelowDb": summary(octave_below_margins),
            "selectedMinusOctaveAboveDb": summary(octave_above_margins),
            "octaveRankHistogram": rank_histogram(octave_ranks),
            "selectedMinusBestComparedAlternativeDb": summary(best_alternative_margins),
        },
        "events": event_rows,
        "hardGuards": {
            "descriptiveOnly": True,
            "ownsAcceptanceDecision": False,
            "setsModelValidationComplete": False,
            "changesPitchIdentity": False,
            "writesDurationSeconds": False,
            "writesSourceEnd": False,
            "usesDecodedModelNoteEnd": False,
            "usesBasicPitchActivations": False,
            "invokesModel": False,
            "usesReferenceTab": False,
            "usesProfessionalScorer": False,
            "importsArchivedV143Logic": False,
            "thresholdSweepUsed": False,
            "acceptanceThresholdDefined": False,
        },
        "provenance": {
            "source": CONTRACT,
            "audioSource": evidence.get("provenance", {}).get("audioSource"),
            "structureIdentity": evidence.get("structureIdentity"),
            "referenceBlind": True,
            "upstreamModelInvoked": True,
            "probeModelInvoked": False,
            "legacyV143ScorerImported": False,
            "professionalScorerUsed": False,
            "referenceTabUsed": False,
            "note": (
                "Descriptive audio-domain support for already-selected MIDI/onset identities only; "
                "this probe does not validate, reject, rewrite, or promote model evidence."
            ),
        },
    }

    output_path = Path(args.output)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")

    print(json.dumps({
        "contract": payload["contract"],
        "eventCount": payload["summary"]["eventCount"],
        "selectedPitchAboveFloorDb": payload["summary"]["selectedPitchAboveFloorDb"],
        "selectedMinusBestSemitoneNeighborDb": payload["summary"]["selectedMinusBestSemitoneNeighborDb"],
        "localSemitoneRankHistogram": payload["summary"]["localSemitoneRankHistogram"],
        "octaveRankHistogram": payload["summary"]["octaveRankHistogram"],
        "selectedMinusBestComparedAlternativeDb": payload["summary"]["selectedMinusBestComparedAlternativeDb"],
        "hardGuards": payload["hardGuards"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
