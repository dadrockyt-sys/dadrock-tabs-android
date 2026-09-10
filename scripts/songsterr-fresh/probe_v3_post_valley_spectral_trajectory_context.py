#!/usr/bin/env python3

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

CONTRACT = "songsterr-fresh-v3-post-valley-spectral-trajectory-context-v1"
SOURCE_CONTRACT = "songsterr-fresh-v3-activation-spectral-rejection-context-v1"
CORROBORATED = "CORROBORATED"
INSUFFICIENT_SPECTRAL = "INSUFFICIENT_SPECTRAL_CORROBORATION"
ALLOWED_CATEGORIES = (CORROBORATED, INSUFFICIENT_SPECTRAL)
HOP_LENGTH = 512
BINS_PER_OCTAVE = 12
SPECTRAL_CONTEXT_FRAMES = 3
SOURCE_CQT_MIN_MIDI = 40
SOURCE_CQT_N_BINS = 49
SOURCE_CQT_MAX_MIDI = SOURCE_CQT_MIN_MIDI + SOURCE_CQT_N_BINS - 1
FIXED_POST_VALLEY_OFFSETS_SECONDS = (0.05, 0.10, 0.20)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Describe selected-pitch CQT levels at fixed post-valley observation horizons "
            "without searching for or outputting an alternate release timestamp."
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


def offset_key(offset_seconds):
    return f"plus{int(round(float(offset_seconds) * 1000.0))}ms"


def validate_source_context(context, *, audio_sha256):
    require(context.get("contract") == SOURCE_CONTRACT, "V3_POST_VALLEY_SOURCE_CONTRACT_CHANGED")
    require(context.get("version") == 1, "V3_POST_VALLEY_SOURCE_VERSION_CHANGED")
    require(context.get("descriptiveOnly") is True, "V3_POST_VALLEY_SOURCE_NOT_DESCRIPTIVE")
    require(context.get("referenceBlind") is True, "V3_POST_VALLEY_SOURCE_REFERENCE_GUARD_CHANGED")

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
        require(context.get(key) is False, f"V3_POST_VALLEY_SOURCE_GUARD_CHANGED:{key}")

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
        require(hard.get(key) is False, f"V3_POST_VALLEY_SOURCE_HARD_GUARD_CHANGED:{key}")

    source = context.get("source") or {}
    require(source.get("audioSha256") == audio_sha256, "V3_POST_VALLEY_AUDIO_IDENTITY_MISMATCH")

    fixed_rule = context.get("fixedEvidenceRule") or {}
    require(fixed_rule.get("thresholdSweepUsed") is False, "V3_POST_VALLEY_FIXED_RULE_SWEEP_CHANGED")
    require(int(fixed_rule.get("spectralCorroborationFrames", -1)) == SPECTRAL_CONTEXT_FRAMES,
            "V3_POST_VALLEY_SPECTRAL_FRAME_CONTRACT_CHANGED")

    rows = context.get("rows")
    require(isinstance(rows, list) and rows, "V3_POST_VALLEY_SOURCE_ROWS_EMPTY")
    seen = set()
    for index, row in enumerate(rows):
        onset_id = str(row.get("onsetId"))
        require(onset_id not in seen, f"V3_POST_VALLEY_DUPLICATE_ONSET:{onset_id}")
        seen.add(onset_id)
        require(row.get("category") in ALLOWED_CATEGORIES,
                f"V3_POST_VALLEY_CATEGORY_INVALID:index={index}")
        midi = int(row.get("midi"))
        require(SOURCE_CQT_MIN_MIDI <= midi <= SOURCE_CQT_MAX_MIDI,
                f"V3_POST_VALLEY_MIDI_OUTSIDE_SOURCE_CQT:index={index}")
        for field in (
            "sourceStartSeconds",
            "observedValleySeconds",
            "samePitchReattackSeconds",
            "onsetSpectralDb",
            "valleySpectralDb",
            "spectralDropDb",
        ):
            value = float(row.get(field))
            require(math.isfinite(value), f"V3_POST_VALLEY_FIELD_INVALID:{field}:index={index}")
        require(float(row["observedValleySeconds"]) >= float(row["sourceStartSeconds"]),
                f"V3_POST_VALLEY_VALLEY_BEFORE_ONSET:index={index}")
        require(float(row["samePitchReattackSeconds"]) > float(row["observedValleySeconds"]),
                f"V3_POST_VALLEY_REATTACK_NOT_AFTER_VALLEY:index={index}")
        require(row.get("spectralCorroborationPassed") is (row.get("category") == CORROBORATED),
                f"V3_POST_VALLEY_CATEGORY_PARITY_CHANGED:index={index}")

    diagnostics = context.get("diagnostics") or {}
    outcome_counts = diagnostics.get("spectralOutcomeCounts") or {}
    actual = Counter(row["category"] for row in rows)
    for category in ALLOWED_CATEGORIES:
        require(int(outcome_counts.get(category, -1)) == int(actual.get(category, 0)),
                f"V3_POST_VALLEY_SOURCE_COUNT_MISMATCH:{category}")
    require(int(diagnostics.get("activationQualifiedCount", -1)) == len(rows),
            "V3_POST_VALLEY_ACTIVATION_QUALIFIED_COUNT_MISMATCH")
    return rows, fixed_rule, source


def summarize_group(rows):
    summary = {
        "count": len(rows),
        "midiHistogram": {str(k): v for k, v in sorted(Counter(row["midi"] for row in rows).items())},
        "sourceOnsetSpectralDb": stats([row.get("sourceOnsetSpectralDb") for row in rows]),
        "sourceValleySpectralDb": stats([row.get("sourceValleySpectralDb") for row in rows]),
        "sourceSpectralDropDb": stats([row.get("sourceSpectralDropDb") for row in rows]),
        "fixedPostValleyOffsets": {},
    }
    for offset_seconds in FIXED_POST_VALLEY_OFFSETS_SECONDS:
        key = offset_key(offset_seconds)
        available = [row["fixedPostValley"][key] for row in rows if row["fixedPostValley"][key]["available"]]
        summary["fixedPostValleyOffsets"][key] = {
            "offsetSeconds": offset_seconds,
            "availableCount": len(available),
            "unavailableCount": len(rows) - len(available),
            "selectedSpectralDb": stats([item.get("selectedSpectralDb") for item in available]),
            "onsetMinusObservedDb": stats([item.get("onsetMinusObservedDb") for item in available]),
            "valleyMinusObservedDb": stats([item.get("valleyMinusObservedDb") for item in available]),
        }
    return summary


def run_probe(input_path, context_path):
    # Heavy DSP dependencies are lazy so --self-test stays dependency/model free.
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
    require(sr > 0 and y.size > 0 and np.all(np.isfinite(y)), "V3_POST_VALLEY_AUDIO_INVALID")

    # Use the exact CQT range of the green source spectral-context probe so the
    # amplitude_to_db(ref=np.max) reference is identical and dB subtraction is valid.
    harmonic = librosa.effects.harmonic(y, margin=2.0)
    cqt = np.abs(librosa.cqt(
        harmonic,
        sr=sr,
        hop_length=HOP_LENGTH,
        fmin=librosa.midi_to_hz(SOURCE_CQT_MIN_MIDI),
        n_bins=SOURCE_CQT_N_BINS,
        bins_per_octave=BINS_PER_OCTAVE,
    ))
    require(cqt.ndim == 2 and cqt.shape[0] == SOURCE_CQT_N_BINS and cqt.shape[1] > 0,
            "V3_POST_VALLEY_CQT_INVALID")
    cqt_db = librosa.amplitude_to_db(cqt, ref=np.max, top_db=80.0)
    conservative_window_seconds = float(SPECTRAL_CONTEXT_FRAMES * HOP_LENGTH / sr)

    def selected_level(midi, observation_seconds):
        frame = int(librosa.time_to_frames(observation_seconds, sr=sr, hop_length=HOP_LENGTH))
        frame = max(0, min(cqt_db.shape[1] - 1, frame))
        stop = min(cqt_db.shape[1], frame + SPECTRAL_CONTEXT_FRAMES)
        segment = cqt_db[midi - SOURCE_CQT_MIN_MIDI, frame:stop]
        require(segment.size > 0, "V3_POST_VALLEY_EMPTY_WINDOW")
        return float(np.mean(segment))

    output_rows = []
    by_category = defaultdict(list)
    for source_row in source_rows:
        onset_id = str(source_row["onsetId"])
        midi = int(source_row["midi"])
        valley = float(source_row["observedValleySeconds"])
        reattack = float(source_row["samePitchReattackSeconds"])
        onset_db = float(source_row["onsetSpectralDb"])
        valley_db = float(source_row["valleySpectralDb"])

        fixed = {}
        for offset_seconds in FIXED_POST_VALLEY_OFFSETS_SECONDS:
            key = offset_key(offset_seconds)
            observation = valley + float(offset_seconds)
            available = observation + conservative_window_seconds < reattack
            if available:
                observed_db = selected_level(midi, observation)
                fixed[key] = {
                    "offsetSeconds": offset_seconds,
                    "available": True,
                    "selectedSpectralDb": observed_db,
                    "onsetMinusObservedDb": float(onset_db - observed_db),
                    "valleyMinusObservedDb": float(valley_db - observed_db),
                }
            else:
                fixed[key] = {
                    "offsetSeconds": offset_seconds,
                    "available": False,
                    "selectedSpectralDb": None,
                    "onsetMinusObservedDb": None,
                    "valleyMinusObservedDb": None,
                }

        row = {
            "onsetId": onset_id,
            "category": source_row["category"],
            "midi": midi,
            "sourceStartSeconds": float(source_row["sourceStartSeconds"]),
            "observedValleySeconds": valley,
            "samePitchReattackSeconds": reattack,
            "sourceOnsetSpectralDb": onset_db,
            "sourceValleySpectralDb": valley_db,
            "sourceSpectralDropDb": float(source_row["spectralDropDb"]),
            "fixedPostValley": fixed,
        }
        output_rows.append(row)
        by_category[row["category"]].append(row)

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
        "usesFixedPostValleyObservationAsDuration": False,
        "searchesForAlternateReleaseTimestamp": False,
        "outputsAlternateReleaseTimestamp": False,
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
            "sourceCqtMinimumMidi": SOURCE_CQT_MIN_MIDI,
            "sourceCqtMaximumMidi": SOURCE_CQT_MAX_MIDI,
            "sourceCqtBinCount": SOURCE_CQT_N_BINS,
            "sourceDbReferenceAligned": True,
            "observationWindowFrames": SPECTRAL_CONTEXT_FRAMES,
            "fixedPostValleyOffsetsSeconds": list(FIXED_POST_VALLEY_OFFSETS_SECONDS),
            "observationOrigin": "already-observed-fixed-activation-valley",
            "availabilityRequiresWindowBeforeSamePitchReattack": True,
            "fixedSourceRule": fixed_rule,
            "acceptanceThresholdDefined": False,
            "delayThresholdDefined": False,
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
            "fixedObservationDuration": False,
            "alternateReleaseSearch": False,
            "alternateReleaseOutput": False,
            "delayThresholdSelection": False,
            "newThresholdSelection": False,
            "acceptanceDecision": False,
        },
    }
    require(payload["diagnostics"]["exactOnsetIdentityPreserved"] is True,
            "V3_POST_VALLEY_IDENTITY_ORDER_CHANGED")
    return payload


def run_self_test():
    def synthetic_row(midi, values):
        fixed = {}
        for offset_seconds in FIXED_POST_VALLEY_OFFSETS_SECONDS:
            key = offset_key(offset_seconds)
            value = values.get(key)
            fixed[key] = {
                "offsetSeconds": offset_seconds,
                "available": value is not None,
                "selectedSpectralDb": None if value is None else value,
                "onsetMinusObservedDb": None if value is None else -10.0 - value,
                "valleyMinusObservedDb": None if value is None else -20.0 - value,
            }
        return {
            "midi": midi,
            "sourceOnsetSpectralDb": -10.0,
            "sourceValleySpectralDb": -20.0,
            "sourceSpectralDropDb": 10.0,
            "fixedPostValley": fixed,
        }

    rows = [
        synthetic_row(52, {"plus50ms": -22.0, "plus100ms": -24.0, "plus200ms": -26.0}),
        synthetic_row(64, {"plus50ms": -18.0, "plus100ms": -21.0, "plus200ms": None}),
    ]
    first = summarize_group(rows)
    second = summarize_group(rows)
    require(first == second, "V3_POST_VALLEY_SELF_TEST_NONDETERMINISTIC")
    require(first["count"] == 2, "V3_POST_VALLEY_SELF_TEST_COUNT")
    require(first["fixedPostValleyOffsets"]["plus50ms"]["availableCount"] == 2,
            "V3_POST_VALLEY_SELF_TEST_50MS")
    require(first["fixedPostValleyOffsets"]["plus200ms"]["availableCount"] == 1,
            "V3_POST_VALLEY_SELF_TEST_200MS")
    require(first["fixedPostValleyOffsets"]["plus100ms"]["valleyMinusObservedDb"]["median"] == 2.5,
            "V3_POST_VALLEY_SELF_TEST_DELTA")
    require(SOURCE_CQT_MIN_MIDI == 40 and SOURCE_CQT_N_BINS == 49 and SOURCE_CQT_MAX_MIDI == 88,
            "V3_POST_VALLEY_SELF_TEST_SOURCE_CQT_SCALE")
    print(json.dumps({
        "contract": CONTRACT,
        "selfTest": "passed",
        "deterministic": True,
        "sourceDbReferenceAligned": True,
        "changesDuration": False,
        "modelInvoked": False,
        "searchesForAlternateReleaseTimestamp": False,
        "outputsAlternateReleaseTimestamp": False,
        "delayThresholdDefined": False,
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
        "sourceDbReferenceAligned": payload["method"]["sourceDbReferenceAligned"],
        "corroboratedFixedOffsets": payload["groups"][CORROBORATED]["fixedPostValleyOffsets"],
        "insufficientFixedOffsets": payload["groups"][INSUFFICIENT_SPECTRAL]["fixedPostValleyOffsets"],
        "hardGuards": payload["hardGuards"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
