#!/usr/bin/env python3

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

CONTRACT = "songsterr-fresh-v3-spectral-valley-neighborhood-context-v1"
SOURCE_CONTRACT = "songsterr-fresh-v3-activation-spectral-rejection-context-v1"
CORROBORATED = "CORROBORATED"
INSUFFICIENT_SPECTRAL = "INSUFFICIENT_SPECTRAL_CORROBORATION"
ALLOWED_CATEGORIES = (CORROBORATED, INSUFFICIENT_SPECTRAL)
HOP_LENGTH = 512
BINS_PER_OCTAVE = 12
SPECTRAL_CONTEXT_FRAMES = 3
SEMITONE_OFFSETS = (-2, -1, 1, 2)
OCTAVE_OFFSETS = (-12, 12)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Describe local semitone/octave CQT context at the already-observed V3 "
            "activation valley without changing duration or selecting a threshold."
        )
    )
    parser.add_argument("--input", help="exact isolated guitar stem used by the source context")
    parser.add_argument("--context", help="activation/spectral rejection context JSON")
    parser.add_argument("--output", help="output JSON")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test and not all((args.input, args.context, args.output)):
        parser.error("--input, --context, and --output are required unless --self-test is used")
    return args


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def percentile(values, q):
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def stats(values):
    cleaned = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    if not cleaned:
        return {
            "count": 0,
            "minimum": None,
            "p10": None,
            "median": None,
            "mean": None,
            "p90": None,
            "maximum": None,
        }
    return {
        "count": len(cleaned),
        "minimum": min(cleaned),
        "p10": percentile(cleaned, 0.10),
        "median": percentile(cleaned, 0.50),
        "mean": sum(cleaned) / len(cleaned),
        "p90": percentile(cleaned, 0.90),
        "maximum": max(cleaned),
    }


def histogram(values):
    counts = Counter(int(value) for value in values)
    return {str(key): counts[key] for key in sorted(counts)}


def ranked_position(levels, selected_midi):
    ordered = sorted(
        levels.items(),
        key=lambda item: (-float(item[1]), abs(int(item[0]) - int(selected_midi)), int(item[0])),
    )
    for index, (midi, _level) in enumerate(ordered):
        if int(midi) == int(selected_midi):
            return index + 1
    raise RuntimeError("V3_VALLEY_NEIGHBORHOOD_SELECTED_MIDI_MISSING_FROM_RANK")


def validate_source_context(context, *, audio_sha256):
    require(context.get("contract") == SOURCE_CONTRACT, "V3_VALLEY_NEIGHBORHOOD_SOURCE_CONTRACT_CHANGED")
    require(context.get("version") == 1, "V3_VALLEY_NEIGHBORHOOD_SOURCE_VERSION_CHANGED")
    require(context.get("descriptiveOnly") is True, "V3_VALLEY_NEIGHBORHOOD_SOURCE_NOT_DESCRIPTIVE")
    require(context.get("referenceBlind") is True, "V3_VALLEY_NEIGHBORHOOD_SOURCE_REFERENCE_GUARD_CHANGED")

    for key in (
        "changesDuration",
        "changesPitchIdentity",
        "invokesModel",
        "readsDecodedModelNoteEnd",
        "usesDecodedModelNoteEndAsDuration",
        "usesNextOnsetAsDuration",
        "usesSamePitchReattackAsDuration",
        "proposesNewReleaseRule",
        "thresholdSelection",
        "thresholdSweep",
        "ownsAcceptanceDecision",
    ):
        require(context.get(key) is False, f"V3_VALLEY_NEIGHBORHOOD_SOURCE_GUARD_CHANGED:{key}")

    hard = context.get("hardGuards") or {}
    for key in (
        "inputEventMutation",
        "durationWrite",
        "sourceEndWrite",
        "pitchIdentityWrite",
        "modelInferenceByProbe",
        "decodedModelEndRead",
        "nextOnsetDuration",
        "samePitchReattackDuration",
        "newThresholdSelection",
        "acceptanceDecision",
    ):
        require(hard.get(key) is False, f"V3_VALLEY_NEIGHBORHOOD_SOURCE_HARD_GUARD_CHANGED:{key}")

    source = context.get("source") or {}
    require(source.get("audioSha256") == audio_sha256, "V3_VALLEY_NEIGHBORHOOD_AUDIO_IDENTITY_MISMATCH")

    fixed_rule = context.get("fixedEvidenceRule") or {}
    require(fixed_rule.get("thresholdSweepUsed") is False, "V3_VALLEY_NEIGHBORHOOD_FIXED_RULE_SWEEP_CHANGED")
    require(int(fixed_rule.get("spectralCorroborationFrames", -1)) == SPECTRAL_CONTEXT_FRAMES,
            "V3_VALLEY_NEIGHBORHOOD_SPECTRAL_FRAME_CONTRACT_CHANGED")

    rows = context.get("rows")
    require(isinstance(rows, list) and rows, "V3_VALLEY_NEIGHBORHOOD_SOURCE_ROWS_EMPTY")
    seen = set()
    for index, row in enumerate(rows):
        onset_id = str(row.get("onsetId"))
        require(onset_id not in seen, f"V3_VALLEY_NEIGHBORHOOD_DUPLICATE_ONSET:{onset_id}")
        seen.add(onset_id)
        require(row.get("category") in ALLOWED_CATEGORIES,
                f"V3_VALLEY_NEIGHBORHOOD_CATEGORY_INVALID:index={index}")
        midi = int(row.get("midi"))
        require(0 <= midi <= 127, f"V3_VALLEY_NEIGHBORHOOD_MIDI_INVALID:index={index}")
        for field in ("sourceStartSeconds", "observedValleySeconds"):
            value = float(row.get(field))
            require(math.isfinite(value) and value >= 0.0,
                    f"V3_VALLEY_NEIGHBORHOOD_TIME_INVALID:{field}:index={index}")
        require(float(row["observedValleySeconds"]) >= float(row["sourceStartSeconds"]),
                f"V3_VALLEY_NEIGHBORHOOD_VALLEY_BEFORE_ONSET:index={index}")
        require(row.get("spectralCorroborationPassed") is (row.get("category") == CORROBORATED),
                f"V3_VALLEY_NEIGHBORHOOD_CATEGORY_PARITY_CHANGED:index={index}")

    diagnostics = context.get("diagnostics") or {}
    outcome_counts = diagnostics.get("spectralOutcomeCounts") or {}
    actual = Counter(row["category"] for row in rows)
    for category in ALLOWED_CATEGORIES:
        require(int(outcome_counts.get(category, -1)) == int(actual.get(category, 0)),
                f"V3_VALLEY_NEIGHBORHOOD_SOURCE_COUNT_MISMATCH:{category}")
    require(int(diagnostics.get("activationQualifiedCount", -1)) == len(rows),
            "V3_VALLEY_NEIGHBORHOOD_ACTIVATION_QUALIFIED_COUNT_MISMATCH")
    return rows, fixed_rule, source


def summarize_group(rows):
    return {
        "count": len(rows),
        "midiHistogram": {str(k): v for k, v in sorted(Counter(row["midi"] for row in rows).items())},
        "selectedValleySpectralDb": stats([row.get("selectedValleySpectralDb") for row in rows]),
        "selectedMinusBestSemitoneNeighborDb": stats([
            row.get("selectedMinusBestSemitoneNeighborDb") for row in rows
        ]),
        "localSemitoneRankHistogram": histogram([row["localSemitoneRank"] for row in rows]),
        "selectedMinusOctaveBelowDb": stats([row.get("selectedMinusOctaveBelowDb") for row in rows]),
        "selectedMinusOctaveAboveDb": stats([row.get("selectedMinusOctaveAboveDb") for row in rows]),
        "octaveRankHistogram": histogram([row["octaveRank"] for row in rows]),
        "selectedMinusBestComparedAlternativeDb": stats([
            row.get("selectedMinusBestComparedAlternativeDb") for row in rows
        ]),
    }


def run_probe(input_path, context_path):
    # Heavy DSP dependencies are intentionally lazy so --self-test stays dependency/model free.
    import librosa
    import numpy as np
    import soundfile as sf

    input_path = Path(input_path)
    context_path = Path(context_path)
    audio_sha256 = sha256_file(input_path)
    context = load_json(context_path)
    source_rows, fixed_rule, source = validate_source_context(context, audio_sha256=audio_sha256)

    y, sr = sf.read(input_path, always_2d=False)
    if getattr(y, "ndim", 0) == 2:
        y = np.mean(y, axis=1)
    y = np.asarray(y, dtype=np.float32)
    require(sr > 0 and y.size > 0 and np.all(np.isfinite(y)), "V3_VALLEY_NEIGHBORHOOD_AUDIO_INVALID")

    selected_midis = [int(row["midi"]) for row in source_rows]
    cqt_min_midi = max(0, min(selected_midis) + min(OCTAVE_OFFSETS))
    cqt_max_midi = min(127, max(selected_midis) + max(OCTAVE_OFFSETS))
    n_bins = cqt_max_midi - cqt_min_midi + 1
    require(n_bins > 0, "V3_VALLEY_NEIGHBORHOOD_CQT_RANGE_INVALID")

    harmonic = librosa.effects.harmonic(y, margin=2.0)
    cqt = np.abs(librosa.cqt(
        harmonic,
        sr=sr,
        hop_length=HOP_LENGTH,
        fmin=librosa.midi_to_hz(cqt_min_midi),
        n_bins=n_bins,
        bins_per_octave=BINS_PER_OCTAVE,
    ))
    require(cqt.ndim == 2 and cqt.shape[0] == n_bins and cqt.shape[1] > 0,
            "V3_VALLEY_NEIGHBORHOOD_CQT_INVALID")
    cqt_db = librosa.amplitude_to_db(cqt, ref=np.max, top_db=80.0)

    def valley_level(midi, valley_seconds):
        if midi < cqt_min_midi or midi > cqt_max_midi:
            return None
        frame = int(librosa.time_to_frames(valley_seconds, sr=sr, hop_length=HOP_LENGTH))
        frame = max(0, min(cqt_db.shape[1] - 1, frame))
        stop = min(cqt_db.shape[1], frame + SPECTRAL_CONTEXT_FRAMES)
        segment = cqt_db[midi - cqt_min_midi, frame:stop]
        require(segment.size > 0, "V3_VALLEY_NEIGHBORHOOD_EMPTY_WINDOW")
        return float(np.median(segment))

    output_rows = []
    by_category = defaultdict(list)
    for row in source_rows:
        onset_id = str(row["onsetId"])
        selected_midi = int(row["midi"])
        valley_seconds = float(row["observedValleySeconds"])
        selected_db = valley_level(selected_midi, valley_seconds)
        require(selected_db is not None, f"V3_VALLEY_NEIGHBORHOOD_SELECTED_BIN_MISSING:{onset_id}")

        semitone_levels = {selected_midi: selected_db}
        for offset in SEMITONE_OFFSETS:
            midi = selected_midi + offset
            level = valley_level(midi, valley_seconds)
            if level is not None:
                semitone_levels[midi] = level
        semitone_neighbors = {midi: level for midi, level in semitone_levels.items() if midi != selected_midi}
        require(semitone_neighbors, f"V3_VALLEY_NEIGHBORHOOD_NO_SEMITONE_NEIGHBOR:{onset_id}")
        best_neighbor_midi, best_neighbor_db = max(
            semitone_neighbors.items(),
            key=lambda item: (float(item[1]), -abs(int(item[0]) - selected_midi), -int(item[0])),
        )
        local_rank = ranked_position(semitone_levels, selected_midi)

        octave_levels = {selected_midi: selected_db}
        octave_below_db = valley_level(selected_midi - 12, valley_seconds)
        octave_above_db = valley_level(selected_midi + 12, valley_seconds)
        if octave_below_db is not None:
            octave_levels[selected_midi - 12] = octave_below_db
        if octave_above_db is not None:
            octave_levels[selected_midi + 12] = octave_above_db
        octave_rank = ranked_position(octave_levels, selected_midi)

        alternatives = dict(semitone_neighbors)
        if octave_below_db is not None:
            alternatives[selected_midi - 12] = octave_below_db
        if octave_above_db is not None:
            alternatives[selected_midi + 12] = octave_above_db
        best_alt_midi, best_alt_db = max(
            alternatives.items(),
            key=lambda item: (float(item[1]), -abs(int(item[0]) - selected_midi), -int(item[0])),
        )

        out = {
            "onsetId": onset_id,
            "category": row["category"],
            "midi": selected_midi,
            "sourceStartSeconds": float(row["sourceStartSeconds"]),
            "observedValleySeconds": valley_seconds,
            "sourceSpectralDropDb": float(row["spectralDropDb"]),
            "selectedValleySpectralDb": selected_db,
            "localSemitoneRank": local_rank,
            "bestSemitoneNeighborMidi": int(best_neighbor_midi),
            "bestSemitoneNeighborSpectralDb": float(best_neighbor_db),
            "selectedMinusBestSemitoneNeighborDb": float(selected_db - best_neighbor_db),
            "octaveBelowSpectralDb": octave_below_db,
            "octaveAboveSpectralDb": octave_above_db,
            "selectedMinusOctaveBelowDb": None if octave_below_db is None else float(selected_db - octave_below_db),
            "selectedMinusOctaveAboveDb": None if octave_above_db is None else float(selected_db - octave_above_db),
            "octaveRank": octave_rank,
            "bestComparedAlternativeMidi": int(best_alt_midi),
            "bestComparedAlternativeSpectralDb": float(best_alt_db),
            "selectedMinusBestComparedAlternativeDb": float(selected_db - best_alt_db),
        }
        output_rows.append(out)
        by_category[row["category"]].append(out)

    groups = {category: summarize_group(by_category[category]) for category in ALLOWED_CATEGORIES}
    payload = {
        "contract": CONTRACT,
        "version": 1,
        "descriptiveOnly": True,
        "referenceBlind": True,
        "changesDuration": False,
        "changesPitchIdentity": False,
        "invokesModel": False,
        "readsDecodedModelNoteEnd": False,
        "usesDecodedModelNoteEndAsDuration": False,
        "usesNextOnsetAsDuration": False,
        "usesSamePitchReattackAsDuration": False,
        "usesSpectralNeighborhoodAsDuration": False,
        "proposesNewReleaseRule": False,
        "thresholdSelection": False,
        "thresholdSweep": False,
        "ownsAcceptanceDecision": False,
        "source": {
            "audioPath": str(input_path),
            "audioSha256": audio_sha256,
            "contextPath": str(context_path),
            "contextSha256": sha256_file(context_path),
            "sourceContract": SOURCE_CONTRACT,
            "structureIdentity": source.get("structureIdentity"),
            "noteInferenceIdentity": source.get("noteInferenceIdentity"),
            "inferenceBundleIdentity": source.get("inferenceBundleIdentity"),
        },
        "method": {
            "domain": "isolated-guitar-harmonic-cqt",
            "harmonicPreprocessing": "librosa.effects.harmonic(margin=2.0)",
            "hopLength": HOP_LENGTH,
            "binsPerOctave": BINS_PER_OCTAVE,
            "valleyWindowFrames": SPECTRAL_CONTEXT_FRAMES,
            "valleyWindowOrigin": "already-observed-fixed-activation-valley",
            "semitoneComparisonOffsets": list(SEMITONE_OFFSETS),
            "octaveComparisonOffsets": list(OCTAVE_OFFSETS),
            "fixedSourceRule": fixed_rule,
            "acceptanceThresholdDefined": False,
            "thresholdSweepUsed": False,
        },
        "diagnostics": {
            "sourceRowCount": len(source_rows),
            "reportedRowCount": len(output_rows),
            "categoryCounts": {category: len(by_category[category]) for category in ALLOWED_CATEGORIES},
            "exactOnsetIdentityPreserved": [row["onsetId"] for row in output_rows] == [str(row["onsetId"]) for row in source_rows],
        },
        "groups": groups,
        "rows": output_rows,
        "hardGuards": {
            "inputEventMutation": False,
            "durationWrite": False,
            "sourceEndWrite": False,
            "pitchIdentityWrite": False,
            "modelInferenceByProbe": False,
            "decodedModelEndRead": False,
            "nextOnsetDuration": False,
            "samePitchReattackDuration": False,
            "spectralNeighborhoodDuration": False,
            "newThresholdSelection": False,
            "acceptanceDecision": False,
        },
    }
    require(payload["diagnostics"]["exactOnsetIdentityPreserved"] is True,
            "V3_VALLEY_NEIGHBORHOOD_IDENTITY_ORDER_CHANGED")
    return payload


def run_self_test():
    synthetic = [
        {
            "midi": 64,
            "selectedValleySpectralDb": -20.0,
            "selectedMinusBestSemitoneNeighborDb": 3.0,
            "localSemitoneRank": 1,
            "selectedMinusOctaveBelowDb": 5.0,
            "selectedMinusOctaveAboveDb": -2.0,
            "octaveRank": 2,
            "selectedMinusBestComparedAlternativeDb": -2.0,
        },
        {
            "midi": 52,
            "selectedValleySpectralDb": -30.0,
            "selectedMinusBestSemitoneNeighborDb": -4.0,
            "localSemitoneRank": 3,
            "selectedMinusOctaveBelowDb": None,
            "selectedMinusOctaveAboveDb": 1.0,
            "octaveRank": 1,
            "selectedMinusBestComparedAlternativeDb": -4.0,
        },
    ]
    first = summarize_group(synthetic)
    second = summarize_group(synthetic)
    require(first == second, "V3_VALLEY_NEIGHBORHOOD_SELF_TEST_NONDETERMINISTIC")
    require(first["count"] == 2, "V3_VALLEY_NEIGHBORHOOD_SELF_TEST_COUNT")
    require(first["localSemitoneRankHistogram"] == {"1": 1, "3": 1},
            "V3_VALLEY_NEIGHBORHOOD_SELF_TEST_LOCAL_RANK")
    require(first["octaveRankHistogram"] == {"1": 1, "2": 1},
            "V3_VALLEY_NEIGHBORHOOD_SELF_TEST_OCTAVE_RANK")
    print(json.dumps({
        "contract": CONTRACT,
        "selfTest": "passed",
        "deterministic": True,
        "changesDuration": False,
        "modelInvoked": False,
        "thresholdSelection": False,
        "thresholdSweep": False,
    }, sort_keys=True))


def main():
    args = parse_args()
    if args.self_test:
        run_self_test()
        return
    payload = run_probe(args.input, args.context)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    print(json.dumps({
        "contract": payload["contract"],
        "categoryCounts": payload["diagnostics"]["categoryCounts"],
        "corroboratedSelectedMinusBestSemitoneNeighborDb": payload["groups"][CORROBORATED]["selectedMinusBestSemitoneNeighborDb"],
        "insufficientSelectedMinusBestSemitoneNeighborDb": payload["groups"][INSUFFICIENT_SPECTRAL]["selectedMinusBestSemitoneNeighborDb"],
        "corroboratedLocalSemitoneRankHistogram": payload["groups"][CORROBORATED]["localSemitoneRankHistogram"],
        "insufficientLocalSemitoneRankHistogram": payload["groups"][INSUFFICIENT_SPECTRAL]["localSemitoneRankHistogram"],
        "hardGuards": payload["hardGuards"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
