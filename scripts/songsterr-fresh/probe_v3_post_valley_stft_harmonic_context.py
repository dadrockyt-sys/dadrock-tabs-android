#!/usr/bin/env python3

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

CONTRACT = "songsterr-fresh-v3-post-valley-stft-harmonic-context-v1"
SOURCE_CONTRACT = "songsterr-fresh-v3-activation-spectral-rejection-context-v1"
CORROBORATED = "CORROBORATED"
INSUFFICIENT_SPECTRAL = "INSUFFICIENT_SPECTRAL_CORROBORATION"
ALLOWED_CATEGORIES = (CORROBORATED, INSUFFICIENT_SPECTRAL)
HOP_LENGTH = 512
N_FFT = 2048
WINDOW = "hann"
CENTER = False
OBSERVATION_FRAMES = 3
HARMONICS = (1, 2, 3, 4)
FIXED_POST_VALLEY_OFFSETS_SECONDS = (0.05, 0.10, 0.20)
POWER_EPSILON = 1e-20


def parse_args():
    parser = argparse.ArgumentParser(description=(
        "Describe fixed STFT harmonic-comb energy at the already-observed V3 activation "
        "valley and fixed post-valley horizons without changing duration or searching "
        "for a release timestamp."
    ))
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
        return {"count": 0, "minimum": None, "p10": None, "median": None,
                "mean": None, "p90": None, "maximum": None}
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
    require(context.get("contract") == SOURCE_CONTRACT, "V3_STFT_SOURCE_CONTRACT_CHANGED")
    require(context.get("version") == 1, "V3_STFT_SOURCE_VERSION_CHANGED")
    require(context.get("descriptiveOnly") is True, "V3_STFT_SOURCE_NOT_DESCRIPTIVE")
    require(context.get("referenceBlind") is True, "V3_STFT_SOURCE_REFERENCE_GUARD_CHANGED")
    for key in (
        "changesDuration", "changesPitchIdentity", "invokesModel",
        "readsDecodedModelNoteEnd", "usesDecodedModelNoteEndAsDuration",
        "usesNextOnsetAsDuration", "usesSamePitchReattackAsDuration",
        "proposesNewReleaseRule", "thresholdSelection", "thresholdSweep",
        "ownsAcceptanceDecision",
    ):
        require(context.get(key) is False, f"V3_STFT_SOURCE_GUARD_CHANGED:{key}")
    hard = context.get("hardGuards") or {}
    for key in (
        "inputEventMutation", "durationWrite", "sourceEndWrite", "pitchIdentityWrite",
        "modelInferenceByProbe", "decodedModelEndRead", "nextOnsetDuration",
        "samePitchReattackDuration", "newThresholdSelection", "acceptanceDecision",
    ):
        require(hard.get(key) is False, f"V3_STFT_SOURCE_HARD_GUARD_CHANGED:{key}")
    source = context.get("source") or {}
    require(source.get("audioSha256") == audio_sha256, "V3_STFT_AUDIO_IDENTITY_MISMATCH")
    fixed_rule = context.get("fixedEvidenceRule") or {}
    require(fixed_rule.get("thresholdSweepUsed") is False, "V3_STFT_FIXED_RULE_SWEEP_CHANGED")
    rows = context.get("rows")
    require(isinstance(rows, list) and rows, "V3_STFT_SOURCE_ROWS_EMPTY")
    seen = set()
    for index, row in enumerate(rows):
        onset_id = str(row.get("onsetId"))
        require(onset_id not in seen, f"V3_STFT_DUPLICATE_ONSET:{onset_id}")
        seen.add(onset_id)
        require(row.get("category") in ALLOWED_CATEGORIES,
                f"V3_STFT_CATEGORY_INVALID:index={index}")
        midi = int(row.get("midi"))
        require(0 <= midi <= 127, f"V3_STFT_MIDI_INVALID:index={index}")
        for field in ("sourceStartSeconds", "observedValleySeconds", "samePitchReattackSeconds"):
            value = float(row.get(field))
            require(math.isfinite(value) and value >= 0.0,
                    f"V3_STFT_TIME_INVALID:{field}:index={index}")
        require(float(row["samePitchReattackSeconds"]) > float(row["observedValleySeconds"]),
                f"V3_STFT_REATTACK_NOT_AFTER_VALLEY:index={index}")
        require(row.get("spectralCorroborationPassed") is (row.get("category") == CORROBORATED),
                f"V3_STFT_CATEGORY_PARITY_CHANGED:index={index}")
    diagnostics = context.get("diagnostics") or {}
    outcome_counts = diagnostics.get("spectralOutcomeCounts") or {}
    actual = Counter(row["category"] for row in rows)
    for category in ALLOWED_CATEGORIES:
        require(int(outcome_counts.get(category, -1)) == int(actual.get(category, 0)),
                f"V3_STFT_SOURCE_COUNT_MISMATCH:{category}")
    require(int(diagnostics.get("activationQualifiedCount", -1)) == len(rows),
            "V3_STFT_ACTIVATION_QUALIFIED_COUNT_MISMATCH")
    return rows, fixed_rule, source


def summarize_group(rows):
    summary = {
        "count": len(rows),
        "midiHistogram": {str(k): v for k, v in sorted(Counter(row["midi"] for row in rows).items())},
        "valleyHarmonicPowerDb": stats([row.get("valleyHarmonicPowerDb") for row in rows]),
        "fixedPostValleyOffsets": {},
    }
    for offset_seconds in FIXED_POST_VALLEY_OFFSETS_SECONDS:
        key = offset_key(offset_seconds)
        available = [row["fixedPostValley"][key] for row in rows if row["fixedPostValley"][key]["available"]]
        summary["fixedPostValleyOffsets"][key] = {
            "offsetSeconds": offset_seconds,
            "availableCount": len(available),
            "unavailableCount": len(rows) - len(available),
            "harmonicPowerDb": stats([item.get("harmonicPowerDb") for item in available]),
            "valleyMinusObservedDb": stats([item.get("valleyMinusObservedDb") for item in available]),
        }
    return summary


def run_probe(input_path, context_path):
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
    require(sr > 0 and y.size >= N_FFT and np.all(np.isfinite(y)), "V3_STFT_AUDIO_INVALID")

    stft = librosa.stft(y, n_fft=N_FFT, hop_length=HOP_LENGTH, win_length=N_FFT,
                        window=WINDOW, center=CENTER)
    power = np.abs(stft) ** 2
    require(power.ndim == 2 and power.shape[1] > 0, "V3_STFT_MATRIX_INVALID")
    fft_frequencies = librosa.fft_frequencies(sr=sr, n_fft=N_FFT)
    nyquist = float(sr) / 2.0

    selected_midis = sorted({int(row["midi"]) for row in source_rows})
    harmonic_bins = {}
    energy_by_midi = {}
    for midi in selected_midis:
        fundamental_hz = float(librosa.midi_to_hz(midi))
        bins = []
        used = set()
        for harmonic in HARMONICS:
            target_hz = fundamental_hz * harmonic
            if target_hz >= nyquist:
                continue
            bin_index = int(np.argmin(np.abs(fft_frequencies - target_hz)))
            if bin_index in used:
                continue
            used.add(bin_index)
            bins.append({"harmonic": harmonic, "targetHz": target_hz,
                         "binIndex": bin_index, "binHz": float(fft_frequencies[bin_index])})
        require(bins, f"V3_STFT_NO_HARMONIC_BINS:midi={midi}")
        harmonic_bins[midi] = bins
        energy_by_midi[midi] = np.sum(power[[item["binIndex"] for item in bins], :], axis=0)

    def frame_for_time(seconds):
        # center=False: choose the first frame whose start is not before the requested
        # observation time. No post-valley window may borrow pre-observation samples.
        frame = int(math.ceil(float(seconds) * sr / HOP_LENGTH))
        return max(0, min(power.shape[1] - 1, frame))

    def observation_window(seconds):
        frame = frame_for_time(seconds)
        stop = min(power.shape[1], frame + OBSERVATION_FRAMES)
        require(stop > frame, "V3_STFT_EMPTY_OBSERVATION_WINDOW")
        actual_start = float(frame * HOP_LENGTH / sr)
        require(actual_start + 1e-12 >= float(seconds), "V3_STFT_WINDOW_STARTS_BEFORE_OBSERVATION")
        return frame, stop, actual_start

    def window_end_seconds(stop_frame):
        last_frame = stop_frame - 1
        return float((last_frame * HOP_LENGTH + N_FFT) / sr)

    def level_db(midi, start_frame, stop_frame):
        segment = energy_by_midi[midi][start_frame:stop_frame]
        require(segment.size > 0, "V3_STFT_EMPTY_ENERGY_SEGMENT")
        mean_power = float(np.mean(segment))
        require(math.isfinite(mean_power) and mean_power >= 0.0, "V3_STFT_POWER_INVALID")
        return float(10.0 * math.log10(max(mean_power, POWER_EPSILON)))

    output_rows = []
    by_category = defaultdict(list)
    for source_row in source_rows:
        onset_id = str(source_row["onsetId"])
        midi = int(source_row["midi"])
        valley = float(source_row["observedValleySeconds"])
        reattack = float(source_row["samePitchReattackSeconds"])
        valley_start, valley_stop, valley_actual_start = observation_window(valley)
        valley_db = level_db(midi, valley_start, valley_stop)
        fixed = {}
        for offset_seconds in FIXED_POST_VALLEY_OFFSETS_SECONDS:
            key = offset_key(offset_seconds)
            requested = valley + float(offset_seconds)
            start, stop, actual_start = observation_window(requested)
            available = window_end_seconds(stop) < reattack
            if available:
                observed_db = level_db(midi, start, stop)
                fixed[key] = {
                    "offsetSeconds": offset_seconds,
                    "available": True,
                    "requestedObservationSeconds": requested,
                    "actualWindowStartSeconds": actual_start,
                    "harmonicPowerDb": observed_db,
                    "valleyMinusObservedDb": float(valley_db - observed_db),
                }
            else:
                fixed[key] = {
                    "offsetSeconds": offset_seconds,
                    "available": False,
                    "requestedObservationSeconds": requested,
                    "actualWindowStartSeconds": actual_start,
                    "harmonicPowerDb": None,
                    "valleyMinusObservedDb": None,
                }
        row = {
            "onsetId": onset_id,
            "category": source_row["category"],
            "midi": midi,
            "sourceStartSeconds": float(source_row["sourceStartSeconds"]),
            "observedValleySeconds": valley,
            "valleyWindowStartSeconds": valley_actual_start,
            "samePitchReattackSeconds": reattack,
            "valleyHarmonicPowerDb": valley_db,
            "fixedPostValley": fixed,
        }
        output_rows.append(row)
        by_category[row["category"]].append(row)

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
        "usesFixedObservationAsDuration": False,
        "searchesForAlternateReleaseTimestamp": False,
        "outputsAlternateReleaseTimestamp": False,
        "proposesNewReleaseRule": False,
        "thresholdSelection": False,
        "thresholdSweep": False,
        "ownsAcceptanceDecision": False,
        "source": {
            "audioPath": str(input_path), "audioSha256": audio_sha256,
            "contextPath": str(context_path), "contextSha256": sha256_file(context_path),
            "sourceContract": SOURCE_CONTRACT,
            "structureIdentity": source.get("structureIdentity"),
            "noteInferenceIdentity": source.get("noteInferenceIdentity"),
            "inferenceBundleIdentity": source.get("inferenceBundleIdentity"),
        },
        "method": {
            "domain": "isolated-guitar-raw-waveform-stft-harmonic-comb-power",
            "nFft": N_FFT, "hopLength": HOP_LENGTH, "window": WINDOW, "center": CENTER,
            "observationFrames": OBSERVATION_FRAMES,
            "observationFrameSelection": "first-frame-start-at-or-after-requested-time",
            "harmonics": list(HARMONICS),
            "fixedPostValleyOffsetsSeconds": list(FIXED_POST_VALLEY_OFFSETS_SECONDS),
            "observationOrigin": "already-observed-fixed-activation-valley",
            "availabilityRequiresEntireStftWindowBeforeSamePitchReattack": True,
            "powerDbDefinition": "10*log10(mean(sum(selected harmonic-bin power)))",
            "harmonicBinSelection": "nearest fixed FFT bin to integer harmonics 1..4 below Nyquist",
            "fixedSourceRule": fixed_rule,
            "acceptanceThresholdDefined": False,
            "delayThresholdDefined": False,
            "thresholdSweepUsed": False,
        },
        "harmonicBinsByMidi": {str(midi): harmonic_bins[midi] for midi in selected_midis},
        "diagnostics": {
            "sourceRowCount": len(source_rows), "reportedRowCount": len(output_rows),
            "categoryCounts": {category: len(by_category[category]) for category in ALLOWED_CATEGORIES},
            "exactOnsetIdentityPreserved": [row["onsetId"] for row in output_rows] == [str(row["onsetId"]) for row in source_rows],
        },
        "groups": {category: summarize_group(by_category[category]) for category in ALLOWED_CATEGORIES},
        "rows": output_rows,
        "hardGuards": {
            "inputEventMutation": False, "durationWrite": False, "sourceEndWrite": False,
            "pitchIdentityWrite": False, "modelInferenceByProbe": False,
            "decodedModelEndRead": False, "nextOnsetDuration": False,
            "samePitchReattackDuration": False, "fixedObservationDuration": False,
            "alternateReleaseSearch": False, "alternateReleaseOutput": False,
            "delayThresholdSelection": False, "newThresholdSelection": False,
            "acceptanceDecision": False,
        },
    }
    require(payload["diagnostics"]["exactOnsetIdentityPreserved"] is True,
            "V3_STFT_IDENTITY_ORDER_CHANGED")
    return payload


def run_self_test():
    def synthetic_row(midi, valley, values):
        fixed = {}
        for offset_seconds in FIXED_POST_VALLEY_OFFSETS_SECONDS:
            key = offset_key(offset_seconds)
            value = values.get(key)
            fixed[key] = {
                "offsetSeconds": offset_seconds, "available": value is not None,
                "harmonicPowerDb": value,
                "valleyMinusObservedDb": None if value is None else valley - value,
            }
        return {"midi": midi, "valleyHarmonicPowerDb": valley, "fixedPostValley": fixed}

    rows = [
        synthetic_row(52, -20.0, {"plus50ms": -23.0, "plus100ms": -25.0, "plus200ms": -26.0}),
        synthetic_row(64, -18.0, {"plus50ms": -17.0, "plus100ms": -19.0, "plus200ms": None}),
    ]
    first = summarize_group(rows)
    second = summarize_group(rows)
    require(first == second, "V3_STFT_SELF_TEST_NONDETERMINISTIC")
    require(first["count"] == 2, "V3_STFT_SELF_TEST_COUNT")
    require(first["fixedPostValleyOffsets"]["plus50ms"]["availableCount"] == 2,
            "V3_STFT_SELF_TEST_50MS")
    require(first["fixedPostValleyOffsets"]["plus200ms"]["availableCount"] == 1,
            "V3_STFT_SELF_TEST_200MS")
    require(first["fixedPostValleyOffsets"]["plus100ms"]["valleyMinusObservedDb"]["median"] == 3.0,
            "V3_STFT_SELF_TEST_DELTA")
    require(N_FFT == 2048 and HOP_LENGTH == 512 and CENTER is False and HARMONICS == (1, 2, 3, 4),
            "V3_STFT_SELF_TEST_METHOD_CHANGED")
    print(json.dumps({
        "contract": CONTRACT, "selfTest": "passed", "deterministic": True,
        "observationFrameSelection": "first-frame-start-at-or-after-requested-time",
        "changesDuration": False, "modelInvoked": False,
        "searchesForAlternateReleaseTimestamp": False,
        "outputsAlternateReleaseTimestamp": False, "delayThresholdDefined": False,
        "thresholdSelection": False, "thresholdSweep": False,
    }, sort_keys=True))


def main():
    args = parse_args()
    if args.self_test:
        run_self_test()
        return
    payload = run_probe(args.input, args.context)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    print(json.dumps({
        "contract": payload["contract"],
        "categoryCounts": payload["diagnostics"]["categoryCounts"],
        "corroboratedFixedOffsets": payload["groups"][CORROBORATED]["fixedPostValleyOffsets"],
        "insufficientFixedOffsets": payload["groups"][INSUFFICIENT_SPECTRAL]["fixedPostValleyOffsets"],
        "hardGuards": payload["hardGuards"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
