#!/usr/bin/env python3

import argparse
import json
import math
from collections import Counter
from pathlib import Path

CONTRACT = "songsterr-fresh-v3-post-valley-representation-comparison-v1"
CQT_CONTRACT = "songsterr-fresh-v3-post-valley-spectral-trajectory-context-v1"
STFT_CONTRACT = "songsterr-fresh-v3-post-valley-stft-harmonic-context-v1"
CORROBORATED = "CORROBORATED"
INSUFFICIENT = "INSUFFICIENT_SPECTRAL_CORROBORATION"
CATEGORIES = (CORROBORATED, INSUFFICIENT)
OFFSET_KEYS = ("plus50ms", "plus100ms", "plus200ms")
OFFSET_SECONDS = {"plus50ms": 0.05, "plus100ms": 0.10, "plus200ms": 0.20}


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Compare already-produced same-run CQT and STFT fixed-horizon trajectory "
            "diagnostics without selecting a release, duration, threshold, or acceptance rule."
        )
    )
    parser.add_argument("--cqt", help="post-valley CQT trajectory JSON")
    parser.add_argument("--stft", help="post-valley STFT harmonic trajectory JSON")
    parser.add_argument("--output", help="comparison JSON")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test and not all((args.cqt, args.stft, args.output)):
        parser.error("--cqt, --stft, and --output are required unless --self-test is used")
    return args


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def percentile(values, q):
    if not values:
        return None
    ordered = sorted(float(v) for v in values)
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
    cleaned = [float(v) for v in values if v is not None and math.isfinite(float(v))]
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


def pearson(xs, ys):
    require(len(xs) == len(ys), "REPRESENTATION_COMPARISON_VECTOR_LENGTH_MISMATCH")
    if len(xs) < 2:
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    dx = [x - mean_x for x in xs]
    dy = [y - mean_y for y in ys]
    denom_x = math.sqrt(sum(v * v for v in dx))
    denom_y = math.sqrt(sum(v * v for v in dy))
    if denom_x == 0.0 or denom_y == 0.0:
        return None
    return sum(a * b for a, b in zip(dx, dy)) / (denom_x * denom_y)


def sign(value):
    value = float(value)
    if value > 0.0:
        return 1
    if value < 0.0:
        return -1
    return 0


def validate_common(payload, expected_contract, label):
    require(payload.get("contract") == expected_contract, f"{label}_CONTRACT_CHANGED")
    require(payload.get("version") == 1, f"{label}_VERSION_CHANGED")
    require(payload.get("descriptiveOnly") is True, f"{label}_NOT_DESCRIPTIVE")
    require(payload.get("referenceBlind") is True, f"{label}_REFERENCE_GUARD_CHANGED")
    false_keys = (
        "changesDuration",
        "changesPitchIdentity",
        "invokesModel",
        "usesDecodedModelNoteEndAsDuration",
        "usesNextOnsetAsDuration",
        "usesSamePitchReattackAsDuration",
        "searchesForAlternateReleaseTimestamp",
        "outputsAlternateReleaseTimestamp",
        "proposesNewReleaseRule",
        "thresholdSelection",
        "thresholdSweep",
        "ownsAcceptanceDecision",
    )
    for key in false_keys:
        require(payload.get(key) is False, f"{label}_GUARD_CHANGED:{key}")
    source = payload.get("source") or {}
    require(isinstance(source.get("audioSha256"), str) and source["audioSha256"],
            f"{label}_AUDIO_SHA_MISSING")
    require(isinstance(source.get("contextSha256"), str) and source["contextSha256"],
            f"{label}_CONTEXT_SHA_MISSING")
    method = payload.get("method") or {}
    require(method.get("fixedPostValleyOffsetsSeconds") == [0.05, 0.1, 0.2],
            f"{label}_OFFSETS_CHANGED")
    require(method.get("acceptanceThresholdDefined") is False,
            f"{label}_ACCEPTANCE_THRESHOLD_DEFINED")
    require(method.get("delayThresholdDefined") is False,
            f"{label}_DELAY_THRESHOLD_DEFINED")
    require(method.get("thresholdSweepUsed") is False,
            f"{label}_THRESHOLD_SWEEP_CHANGED")
    rows = payload.get("rows")
    require(isinstance(rows, list) and rows, f"{label}_ROWS_EMPTY")
    return rows, source


def identity(row):
    return (
        str(row.get("onsetId")),
        str(row.get("category")),
        int(row.get("midi")),
        float(row.get("sourceStartSeconds")),
        float(row.get("observedValleySeconds")),
        float(row.get("samePitchReattackSeconds")),
    )


def validate_pair(cqt, stft):
    cqt_rows, cqt_source = validate_common(cqt, CQT_CONTRACT, "CQT")
    stft_rows, stft_source = validate_common(stft, STFT_CONTRACT, "STFT")
    require(cqt_source.get("audioSha256") == stft_source.get("audioSha256"),
            "REPRESENTATION_COMPARISON_AUDIO_IDENTITY_MISMATCH")
    require(cqt_source.get("contextSha256") == stft_source.get("contextSha256"),
            "REPRESENTATION_COMPARISON_CONTEXT_IDENTITY_MISMATCH")
    require(cqt_source.get("structureIdentity") == stft_source.get("structureIdentity"),
            "REPRESENTATION_COMPARISON_STRUCTURE_IDENTITY_MISMATCH")
    require(cqt_source.get("noteInferenceIdentity") == stft_source.get("noteInferenceIdentity"),
            "REPRESENTATION_COMPARISON_NOTE_INFERENCE_IDENTITY_MISMATCH")
    require(cqt_source.get("inferenceBundleIdentity") == stft_source.get("inferenceBundleIdentity"),
            "REPRESENTATION_COMPARISON_INFERENCE_BUNDLE_IDENTITY_MISMATCH")
    require(len(cqt_rows) == len(stft_rows), "REPRESENTATION_COMPARISON_ROW_COUNT_MISMATCH")
    cqt_ids = [identity(row) for row in cqt_rows]
    stft_ids = [identity(row) for row in stft_rows]
    require(cqt_ids == stft_ids, "REPRESENTATION_COMPARISON_EXACT_ROW_IDENTITY_MISMATCH")
    require(len(set(cqt_ids)) == len(cqt_ids), "REPRESENTATION_COMPARISON_DUPLICATE_IDENTITY")
    counts = Counter(row.get("category") for row in cqt_rows)
    require(set(counts) == set(CATEGORIES), "REPRESENTATION_COMPARISON_CATEGORY_SET_CHANGED")
    return cqt_rows, stft_rows, cqt_source


def summarize_pairs(pairs):
    cqt_values = [pair["cqtValleyMinusObservedDb"] for pair in pairs]
    stft_values = [pair["stftValleyMinusObservedDb"] for pair in pairs]
    directions = Counter()
    for pair in pairs:
        c = sign(pair["cqtValleyMinusObservedDb"])
        s = sign(pair["stftValleyMinusObservedDb"])
        if c == 0 or s == 0:
            directions["ZERO_PRESENT"] += 1
        elif c > 0 and s > 0:
            directions["BOTH_DECAY"] += 1
        elif c < 0 and s < 0:
            directions["BOTH_RISE"] += 1
        elif c > 0 and s < 0:
            directions["CQT_DECAY_STFT_RISE"] += 1
        else:
            directions["CQT_RISE_STFT_DECAY"] += 1
    nonzero = len(pairs) - directions.get("ZERO_PRESENT", 0)
    agreement = directions.get("BOTH_DECAY", 0) + directions.get("BOTH_RISE", 0)
    return {
        "pairedCount": len(pairs),
        "cqtValleyMinusObservedDb": stats(cqt_values),
        "stftValleyMinusObservedDb": stats(stft_values),
        "pearsonCorrelation": pearson(cqt_values, stft_values),
        "directionCounts": {
            key: int(directions.get(key, 0))
            for key in (
                "BOTH_DECAY",
                "BOTH_RISE",
                "CQT_DECAY_STFT_RISE",
                "CQT_RISE_STFT_DECAY",
                "ZERO_PRESENT",
            )
        },
        "nonzeroDirectionCount": nonzero,
        "directionAgreementRate": (agreement / nonzero) if nonzero else None,
    }


def compare_payloads(cqt, stft):
    cqt_rows, stft_rows, source = validate_pair(cqt, stft)
    grouped = {category: {} for category in CATEGORIES}
    row_results = []
    by_category_offset = {
        category: {key: [] for key in OFFSET_KEYS}
        for category in CATEGORIES
    }

    for cqt_row, stft_row in zip(cqt_rows, stft_rows):
        category = cqt_row["category"]
        require(category in CATEGORIES, "REPRESENTATION_COMPARISON_CATEGORY_INVALID")
        result = {
            "onsetId": cqt_row["onsetId"],
            "category": category,
            "midi": int(cqt_row["midi"]),
            "sourceStartSeconds": float(cqt_row["sourceStartSeconds"]),
            "fixedPostValley": {},
        }
        for key in OFFSET_KEYS:
            cqt_obs = (cqt_row.get("fixedPostValley") or {}).get(key) or {}
            stft_obs = (stft_row.get("fixedPostValley") or {}).get(key) or {}
            require(float(cqt_obs.get("offsetSeconds")) == OFFSET_SECONDS[key],
                    f"REPRESENTATION_COMPARISON_CQT_OFFSET_CHANGED:{key}")
            require(float(stft_obs.get("offsetSeconds")) == OFFSET_SECONDS[key],
                    f"REPRESENTATION_COMPARISON_STFT_OFFSET_CHANGED:{key}")
            paired = bool(cqt_obs.get("available")) and bool(stft_obs.get("available"))
            entry = {
                "offsetSeconds": OFFSET_SECONDS[key],
                "cqtAvailable": bool(cqt_obs.get("available")),
                "stftAvailable": bool(stft_obs.get("available")),
                "pairedAvailable": paired,
                "cqtValleyMinusObservedDb": None,
                "stftValleyMinusObservedDb": None,
                "directionAgreement": None,
            }
            if paired:
                cqt_delta = float(cqt_obs.get("valleyMinusObservedDb"))
                stft_delta = float(stft_obs.get("valleyMinusObservedDb"))
                require(math.isfinite(cqt_delta) and math.isfinite(stft_delta),
                        f"REPRESENTATION_COMPARISON_NONFINITE_DELTA:{key}")
                entry["cqtValleyMinusObservedDb"] = cqt_delta
                entry["stftValleyMinusObservedDb"] = stft_delta
                entry["directionAgreement"] = (
                    sign(cqt_delta) == sign(stft_delta)
                    if sign(cqt_delta) != 0 and sign(stft_delta) != 0
                    else None
                )
                by_category_offset[category][key].append({
                    "cqtValleyMinusObservedDb": cqt_delta,
                    "stftValleyMinusObservedDb": stft_delta,
                })
            result["fixedPostValley"][key] = entry
        row_results.append(result)

    for category in CATEGORIES:
        for key in OFFSET_KEYS:
            grouped[category][key] = {
                "offsetSeconds": OFFSET_SECONDS[key],
                **summarize_pairs(by_category_offset[category][key]),
            }

    return {
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
        "usesRepresentationAgreementAsDuration": False,
        "searchesForAlternateReleaseTimestamp": False,
        "outputsAlternateReleaseTimestamp": False,
        "proposesNewReleaseRule": False,
        "thresholdSelection": False,
        "thresholdSweep": False,
        "ownsAcceptanceDecision": False,
        "source": {
            "audioSha256": source.get("audioSha256"),
            "contextSha256": source.get("contextSha256"),
            "structureIdentity": source.get("structureIdentity"),
            "noteInferenceIdentity": source.get("noteInferenceIdentity"),
            "inferenceBundleIdentity": source.get("inferenceBundleIdentity"),
            "cqtContract": CQT_CONTRACT,
            "stftContract": STFT_CONTRACT,
        },
        "method": {
            "comparison": "same-run-fixed-horizon-CQT-vs-STFT-delta",
            "fixedPostValleyOffsetsSeconds": [0.05, 0.1, 0.2],
            "identityAuthority": "exact same-run onsetId/category/MIDI/start/valley/reattack tuple",
            "pairedOnlyForStatistics": True,
            "directionDefinition": "positive delta=decay from valley; negative delta=rise from valley",
            "acceptanceThresholdDefined": False,
            "delayThresholdDefined": False,
            "agreementThresholdDefined": False,
            "thresholdSweepUsed": False,
        },
        "diagnostics": {
            "rowCount": len(row_results),
            "categoryCounts": {
                category: sum(1 for row in row_results if row["category"] == category)
                for category in CATEGORIES
            },
            "exactSameRunIdentityRequired": True,
        },
        "groups": grouped,
        "rows": row_results,
        "hardGuards": {
            "inputEventMutation": False,
            "durationWrite": False,
            "sourceEndWrite": False,
            "pitchIdentityWrite": False,
            "modelInferenceByComparator": False,
            "decodedModelEndRead": False,
            "nextOnsetDuration": False,
            "samePitchReattackDuration": False,
            "representationAgreementDuration": False,
            "alternateReleaseSearch": False,
            "thresholdSelection": False,
            "thresholdSweep": False,
            "acceptanceDecision": False,
        },
    }


def fake_payload(contract):
    common_false = {
        "changesDuration": False,
        "changesPitchIdentity": False,
        "invokesModel": False,
        "usesDecodedModelNoteEndAsDuration": False,
        "usesNextOnsetAsDuration": False,
        "usesSamePitchReattackAsDuration": False,
        "searchesForAlternateReleaseTimestamp": False,
        "outputsAlternateReleaseTimestamp": False,
        "proposesNewReleaseRule": False,
        "thresholdSelection": False,
        "thresholdSweep": False,
        "ownsAcceptanceDecision": False,
    }
    rows = []
    for index, (category, midi, start) in enumerate((
        (CORROBORATED, 52, 1.0),
        (CORROBORATED, 55, 2.0),
        (INSUFFICIENT, 59, 3.0),
        (INSUFFICIENT, 64, 4.0),
    )):
        fixed = {}
        for key, offset in OFFSET_SECONDS.items():
            delta = (index + 1) * (1 if category == INSUFFICIENT else -1) * offset * 10
            fixed[key] = {
                "offsetSeconds": offset,
                "available": True,
                "valleyMinusObservedDb": delta if contract == CQT_CONTRACT else delta * 0.5,
            }
        rows.append({
            "onsetId": f"note-{index}",
            "category": category,
            "midi": midi,
            "sourceStartSeconds": start,
            "observedValleySeconds": start + 0.2,
            "samePitchReattackSeconds": start + 1.0,
            "fixedPostValley": fixed,
        })
    return {
        "contract": contract,
        "version": 1,
        "descriptiveOnly": True,
        "referenceBlind": True,
        **common_false,
        "source": {
            "audioSha256": "a" * 64,
            "contextSha256": "b" * 64,
            "structureIdentity": {"signature": "fnv1a32:test"},
            "noteInferenceIdentity": "notes",
            "inferenceBundleIdentity": "bundle",
        },
        "method": {
            "fixedPostValleyOffsetsSeconds": [0.05, 0.1, 0.2],
            "acceptanceThresholdDefined": False,
            "delayThresholdDefined": False,
            "thresholdSweepUsed": False,
        },
        "rows": rows,
    }


def self_test():
    cqt = fake_payload(CQT_CONTRACT)
    stft = fake_payload(STFT_CONTRACT)
    first = compare_payloads(cqt, stft)
    second = compare_payloads(cqt, stft)
    require(
        json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True),
        "REPRESENTATION_COMPARISON_SELF_TEST_NONDETERMINISTIC",
    )
    require(first["diagnostics"]["rowCount"] == 4, "REPRESENTATION_COMPARISON_SELF_TEST_COUNT")
    require(first["changesDuration"] is False, "REPRESENTATION_COMPARISON_SELF_TEST_DURATION_GUARD")
    broken = json.loads(json.dumps(stft))
    broken["rows"][0]["midi"] = 53
    try:
        compare_payloads(cqt, broken)
    except RuntimeError as exc:
        require("EXACT_ROW_IDENTITY_MISMATCH" in str(exc),
                "REPRESENTATION_COMPARISON_SELF_TEST_WRONG_IDENTITY_FAILURE")
    else:
        raise RuntimeError("REPRESENTATION_COMPARISON_SELF_TEST_IDENTITY_FAIL_OPEN")
    broken = json.loads(json.dumps(stft))
    broken["source"]["contextSha256"] = "c" * 64
    try:
        compare_payloads(cqt, broken)
    except RuntimeError as exc:
        require("CONTEXT_IDENTITY_MISMATCH" in str(exc),
                "REPRESENTATION_COMPARISON_SELF_TEST_WRONG_CONTEXT_FAILURE")
    else:
        raise RuntimeError("REPRESENTATION_COMPARISON_SELF_TEST_CONTEXT_FAIL_OPEN")
    print(json.dumps({
        "selfTest": "PASS",
        "contract": CONTRACT,
        "descriptiveOnly": True,
        "changesDuration": False,
        "thresholdSweep": False,
        "ownsAcceptanceDecision": False,
    }, sort_keys=True))


def main():
    args = parse_args()
    if args.self_test:
        self_test()
        return
    payload = compare_payloads(load_json(args.cqt), load_json(args.stft))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
