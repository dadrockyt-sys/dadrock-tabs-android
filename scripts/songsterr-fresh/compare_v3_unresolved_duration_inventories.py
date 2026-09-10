#!/usr/bin/env python3

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path

CONTRACT = "songsterr-fresh-v3-unresolved-duration-inventory-comparison-v1"
INVENTORY_CONTRACT = "songsterr-fresh-v3-unresolved-duration-inventory-v2"
V3_RELEASE_CONTRACT = "songsterr-fresh-spectral-activation-release-evidence-v3"
REATTACK_REASON = "NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK"

TOP_LEVEL_FALSE_GUARDS = (
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
)
HARD_FALSE_GUARDS = (
    "inputEventMutation",
    "durationWrite",
    "sourceEndWrite",
    "pitchIdentityWrite",
    "modelInference",
    "decodedModelEndRead",
    "newThresholdSelection",
)
STAT_FIELDS = ("minimum", "p10", "median", "mean", "p90", "maximum")


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Compare two descriptive v3 unresolved-duration inventory-v2 JSON files "
            "without changing events, selecting thresholds, or deciding acceptance."
        )
    )
    parser.add_argument("--first", help="first inventory-v2 JSON")
    parser.add_argument("--second", help="second inventory-v2 JSON")
    parser.add_argument("--output", help="comparison JSON")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run deterministic guard/comparison regression checks",
    )
    args = parser.parse_args()
    if not args.self_test and not all((args.first, args.second, args.output)):
        parser.error("--first, --second, and --output are required unless --self-test is used")
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


def int_value(value, code):
    require(isinstance(value, int) and not isinstance(value, bool) and value >= 0, code)
    return value


def validate_inventory(inventory, label):
    prefix = f"V3_INVENTORY_COMPARISON_{label.upper()}"
    require(inventory.get("contract") == INVENTORY_CONTRACT, f"{prefix}_CONTRACT_CHANGED")
    require(inventory.get("version") == 2, f"{prefix}_VERSION_CHANGED")
    require(inventory.get("descriptiveOnly") is True, f"{prefix}_DESCRIPTIVE_GUARD_CHANGED")
    require(inventory.get("referenceBlind") is True, f"{prefix}_REFERENCE_BLIND_GUARD_CHANGED")

    for guard in TOP_LEVEL_FALSE_GUARDS:
        require(inventory.get(guard) is False, f"{prefix}_TOP_LEVEL_GUARD_CHANGED:{guard}")

    hard_guards = inventory.get("hardGuards")
    require(isinstance(hard_guards, dict), f"{prefix}_HARD_GUARDS_MISSING")
    for guard in HARD_FALSE_GUARDS:
        require(hard_guards.get(guard) is False, f"{prefix}_HARD_GUARD_CHANGED:{guard}")

    source = inventory.get("sourceEvidence")
    require(isinstance(source, dict), f"{prefix}_SOURCE_EVIDENCE_MISSING")
    require(
        source.get("releaseContract") == V3_RELEASE_CONTRACT,
        f"{prefix}_V3_RELEASE_CONTRACT_CHANGED",
    )
    require(isinstance(source.get("activationRule"), dict), f"{prefix}_ACTIVATION_RULE_MISSING")

    counts = inventory.get("counts")
    require(isinstance(counts, dict), f"{prefix}_COUNTS_MISSING")
    eligible = int_value(counts.get("durationEligibleEvents"), f"{prefix}_ELIGIBLE_COUNT_INVALID")
    resolved = int_value(counts.get("resolvedEvents"), f"{prefix}_RESOLVED_COUNT_INVALID")
    unresolved = int_value(counts.get("unresolvedEvents"), f"{prefix}_UNRESOLVED_COUNT_INVALID")
    require(eligible == resolved + unresolved, f"{prefix}_RESOLUTION_ACCOUNTING_MISMATCH")

    primary = inventory.get("unresolvedPrimaryReasons")
    fallback = inventory.get("reattackCensoredFallbackRejections")
    require(isinstance(primary, dict), f"{prefix}_PRIMARY_REASONS_MISSING")
    require(isinstance(fallback, dict), f"{prefix}_FALLBACK_REASONS_MISSING")

    primary_total = sum(
        int_value(group.get("count"), f"{prefix}_PRIMARY_REASON_COUNT_INVALID:{reason}")
        for reason, group in primary.items()
        if isinstance(group, dict)
    )
    require(primary_total == unresolved, f"{prefix}_PRIMARY_REASON_ACCOUNTING_MISMATCH")

    reattack_count = int((primary.get(REATTACK_REASON) or {}).get("count", 0))
    fallback_total = sum(
        int_value(group.get("count"), f"{prefix}_FALLBACK_REASON_COUNT_INVALID:{reason}")
        for reason, group in fallback.items()
        if isinstance(group, dict)
    )
    require(fallback_total == reattack_count, f"{prefix}_FALLBACK_REASON_ACCOUNTING_MISMATCH")

    resolution_context = inventory.get("resolutionContext")
    require(isinstance(resolution_context, dict), f"{prefix}_RESOLUTION_CONTEXT_MISSING")
    by_midi = resolution_context.get("byMidi")
    require(isinstance(by_midi, dict), f"{prefix}_BY_MIDI_CONTEXT_MISSING")

    midi_eligible = midi_resolved = midi_unresolved = 0
    for midi, context in by_midi.items():
        require(isinstance(context, dict), f"{prefix}_MIDI_CONTEXT_INVALID:{midi}")
        midi_eligible += int_value(context.get("eligibleCount"), f"{prefix}_MIDI_ELIGIBLE_INVALID:{midi}")
        midi_resolved += int_value(context.get("resolvedCount"), f"{prefix}_MIDI_RESOLVED_INVALID:{midi}")
        midi_unresolved += int_value(context.get("unresolvedCount"), f"{prefix}_MIDI_UNRESOLVED_INVALID:{midi}")
    require(midi_eligible == eligible, f"{prefix}_MIDI_ELIGIBLE_ACCOUNTING_MISMATCH")
    require(midi_resolved == resolved, f"{prefix}_MIDI_RESOLVED_ACCOUNTING_MISMATCH")
    require(midi_unresolved == unresolved, f"{prefix}_MIDI_UNRESOLVED_ACCOUNTING_MISMATCH")


def nonzero_int_deltas(first, second):
    result = {}
    for key in sorted(set(first) | set(second)):
        delta = int(second.get(key, 0)) - int(first.get(key, 0))
        if delta:
            result[key] = delta
    return result


def reason_count_deltas(first, second):
    result = {}
    for reason in sorted(set(first) | set(second)):
        first_count = int((first.get(reason) or {}).get("count", 0))
        second_count = int((second.get(reason) or {}).get("count", 0))
        delta = second_count - first_count
        if delta:
            result[reason] = delta
    return result


def numeric_delta(first, second):
    if first is None and second is None:
        return None
    if first is None or second is None:
        return {"first": first, "second": second, "delta": None}
    if not isinstance(first, (int, float)) or isinstance(first, bool):
        return None
    if not isinstance(second, (int, float)) or isinstance(second, bool):
        return None
    if not (math.isfinite(float(first)) and math.isfinite(float(second))):
        return None
    delta = float(second) - float(first)
    if delta == 0.0:
        return None
    return {"first": float(first), "second": float(second), "delta": delta}


def stat_deltas(first, second):
    first = first if isinstance(first, dict) else {}
    second = second if isinstance(second, dict) else {}
    result = {}
    for field in STAT_FIELDS:
        delta = numeric_delta(first.get(field), second.get(field))
        if delta is not None:
            result[field] = delta
    return result


def exact_overall_continuous_deltas(first, second):
    result = {}
    for name in (
        "resolvedOnsetConfidence",
        "unresolvedOnsetConfidence",
        "resolvedNextSamePitchReattackGapSeconds",
        "unresolvedNextSamePitchReattackGapSeconds",
    ):
        deltas = stat_deltas(first.get(name), second.get(name))
        if deltas:
            result[name] = deltas
    return result


def update_max_summary(summary, path, delta_record):
    delta = delta_record.get("delta")
    if delta is None:
        summary["nonComparableFieldCount"] += 1
        return
    summary["nonzeroDeltaCount"] += 1
    absolute = abs(float(delta))
    if summary["maxAbsoluteDelta"] is None or absolute > summary["maxAbsoluteDelta"]:
        summary["maxAbsoluteDelta"] = absolute
        summary["maxAbsoluteDeltaPath"] = path
        summary["maxAbsoluteDeltaFirst"] = delta_record.get("first")
        summary["maxAbsoluteDeltaSecond"] = delta_record.get("second")
        summary["maxAbsoluteSignedDelta"] = delta


def new_delta_summary():
    return {
        "nonzeroDeltaCount": 0,
        "nonComparableFieldCount": 0,
        "maxAbsoluteDelta": None,
        "maxAbsoluteDeltaPath": None,
        "maxAbsoluteDeltaFirst": None,
        "maxAbsoluteDeltaSecond": None,
        "maxAbsoluteSignedDelta": None,
    }


def grouped_continuous_summary(first_groups, second_groups):
    summary = {
        "onsetConfidence": new_delta_summary(),
        "nextSamePitchReattackGapSeconds": new_delta_summary(),
    }
    for group in sorted(set(first_groups) | set(second_groups)):
        first = first_groups.get(group) or {}
        second = second_groups.get(group) or {}
        for statistic in summary:
            deltas = stat_deltas(first.get(statistic), second.get(statistic))
            for field, record in deltas.items():
                update_max_summary(summary[statistic], f"{group}.{statistic}.{field}", record)
    return summary


def midi_count_reason_deltas(first_by_midi, second_by_midi):
    result = {}
    for midi in sorted(set(first_by_midi) | set(second_by_midi), key=lambda value: int(value)):
        first = first_by_midi.get(midi) or {}
        second = second_by_midi.get(midi) or {}
        entry = {}
        for field in ("eligibleCount", "resolvedCount", "unresolvedCount"):
            delta = int(second.get(field, 0)) - int(first.get(field, 0))
            if delta:
                entry[f"{field}Delta"] = delta

        fraction_delta = numeric_delta(first.get("unresolvedFraction"), second.get("unresolvedFraction"))
        if fraction_delta is not None:
            entry["unresolvedFractionDelta"] = fraction_delta

        primary = nonzero_int_deltas(
            first.get("unresolvedPrimaryReasonCounts") or {},
            second.get("unresolvedPrimaryReasonCounts") or {},
        )
        fallback = nonzero_int_deltas(
            first.get("unresolvedFallbackReasonCounts") or {},
            second.get("unresolvedFallbackReasonCounts") or {},
        )
        if primary:
            entry["unresolvedPrimaryReasonCountDeltas"] = primary
        if fallback:
            entry["unresolvedFallbackReasonCountDeltas"] = fallback
        if entry:
            result[midi] = entry
    return result


def midi_continuous_summary(first_by_midi, second_by_midi):
    summary = {
        "resolvedOnsetConfidence": new_delta_summary(),
        "unresolvedOnsetConfidence": new_delta_summary(),
        "resolvedNextSamePitchReattackGapSeconds": new_delta_summary(),
        "unresolvedNextSamePitchReattackGapSeconds": new_delta_summary(),
    }
    changed_midis = set()
    for midi in sorted(set(first_by_midi) | set(second_by_midi), key=lambda value: int(value)):
        first = first_by_midi.get(midi) or {}
        second = second_by_midi.get(midi) or {}
        for statistic in summary:
            deltas = stat_deltas(first.get(statistic), second.get(statistic))
            if deltas:
                changed_midis.add(midi)
            for field, record in deltas.items():
                update_max_summary(summary[statistic], f"{midi}.{statistic}.{field}", record)
    return {
        "changedMidiCount": len(changed_midis),
        "statistics": summary,
    }


def compare_inventories(first, second, first_source=None, second_source=None):
    validate_inventory(first, "first")
    validate_inventory(second, "second")

    first_counts = first["counts"]
    second_counts = second["counts"]
    count_deltas = {
        key: int(second_counts.get(key, 0)) - int(first_counts.get(key, 0))
        for key in sorted(set(first_counts) | set(second_counts))
    }
    count_deltas = {key: value for key, value in count_deltas.items() if value}

    first_context = first["resolutionContext"]
    second_context = second["resolutionContext"]
    first_by_midi = first_context["byMidi"]
    second_by_midi = second_context["byMidi"]

    first_primary = first["unresolvedPrimaryReasons"]
    second_primary = second["unresolvedPrimaryReasons"]
    first_fallback = first["reattackCensoredFallbackRejections"]
    second_fallback = second["reattackCensoredFallbackRejections"]

    output = {
        "contract": CONTRACT,
        "version": 1,
        "descriptiveOnly": True,
        "referenceBlind": True,
        "ownsAcceptanceDecision": False,
        "changesDuration": False,
        "changesPitchIdentity": False,
        "invokesModel": False,
        "readsDecodedModelNoteEnd": False,
        "usesDecodedModelNoteEndAsDuration": False,
        "usesNextOnsetAsDuration": False,
        "usesSamePitchReattackAsDuration": False,
        "proposesNewReleaseRule": False,
        "thresholdSelection": False,
        "thresholdSweep": False,
        "sources": {
            "first": {
                "path": str(first_source) if first_source is not None else None,
                "sha256": sha256_file(first_source) if first_source is not None else None,
                "counts": first_counts,
                "sourceEvidenceSha256": (first.get("sourceEvidence") or {}).get("sha256"),
            },
            "second": {
                "path": str(second_source) if second_source is not None else None,
                "sha256": sha256_file(second_source) if second_source is not None else None,
                "counts": second_counts,
                "sourceEvidenceSha256": (second.get("sourceEvidence") or {}).get("sha256"),
            },
        },
        "activationRuleEqual": (
            (first.get("sourceEvidence") or {}).get("activationRule")
            == (second.get("sourceEvidence") or {}).get("activationRule")
        ),
        "countDeltas": count_deltas,
        "unresolvedPrimaryReasonCountDeltas": reason_count_deltas(first_primary, second_primary),
        "reattackFallbackReasonCountDeltas": reason_count_deltas(first_fallback, second_fallback),
        "midiCountReasonDeltas": midi_count_reason_deltas(first_by_midi, second_by_midi),
        "overallContinuousStatisticDeltas": exact_overall_continuous_deltas(first_context, second_context),
        "unresolvedPrimaryReasonContinuousSummary": grouped_continuous_summary(first_primary, second_primary),
        "reattackFallbackContinuousSummary": grouped_continuous_summary(first_fallback, second_fallback),
        "midiContinuousSummary": midi_continuous_summary(first_by_midi, second_by_midi),
        "hardGuards": {
            "acceptanceDecision": False,
            "inputEventMutation": False,
            "durationWrite": False,
            "sourceEndWrite": False,
            "pitchIdentityWrite": False,
            "modelInference": False,
            "decodedModelEndRead": False,
            "newThresholdSelection": False,
        },
    }
    return output


def minimal_inventory():
    stat = {
        "count": 1,
        "minimum": 0.5,
        "p10": 0.5,
        "median": 0.5,
        "mean": 0.5,
        "p90": 0.5,
        "maximum": 0.5,
    }
    empty_stat = {
        "count": 0,
        "minimum": None,
        "p10": None,
        "median": None,
        "mean": None,
        "p90": None,
        "maximum": None,
    }
    return {
        "contract": INVENTORY_CONTRACT,
        "version": 2,
        "descriptiveOnly": True,
        "referenceBlind": True,
        "changesDuration": False,
        "changesPitchIdentity": False,
        "invokesModel": False,
        "readsDecodedModelNoteEnd": False,
        "usesDecodedModelNoteEndAsDuration": False,
        "usesNextOnsetAsDuration": False,
        "usesSamePitchReattackAsDuration": False,
        "proposesNewReleaseRule": False,
        "thresholdSelection": False,
        "thresholdSweep": False,
        "sourceEvidence": {
            "path": "fixture.json",
            "sha256": "example",
            "releaseContract": V3_RELEASE_CONTRACT,
            "activationRule": {"fixed": True},
        },
        "counts": {
            "durationEligibleEvents": 1,
            "resolvedEvents": 0,
            "unresolvedEvents": 1,
        },
        "resolutionContext": {
            "resolvedOnsetConfidence": empty_stat,
            "unresolvedOnsetConfidence": stat,
            "resolvedNextSamePitchReattackGapSeconds": empty_stat,
            "unresolvedNextSamePitchReattackGapSeconds": stat,
            "byMidi": {
                "55": {
                    "eligibleCount": 1,
                    "resolvedCount": 0,
                    "unresolvedCount": 1,
                    "unresolvedFraction": 1.0,
                    "resolvedOnsetConfidence": empty_stat,
                    "unresolvedOnsetConfidence": stat,
                    "resolvedNextSamePitchReattackGapSeconds": empty_stat,
                    "unresolvedNextSamePitchReattackGapSeconds": stat,
                    "unresolvedPrimaryReasonCounts": {REATTACK_REASON: 1},
                    "unresolvedFallbackReasonCounts": {"NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION": 1},
                }
            },
        },
        "unresolvedPrimaryReasons": {
            REATTACK_REASON: {
                "count": 1,
                "midiHistogram": {"55": 1},
                "onsetConfidence": stat,
                "nextSamePitchReattackGapSeconds": stat,
            }
        },
        "reattackCensoredFallbackRejections": {
            "NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION": {
                "count": 1,
                "midiHistogram": {"55": 1},
                "onsetConfidence": stat,
                "nextSamePitchReattackGapSeconds": stat,
            }
        },
        "hardGuards": {
            "inputEventMutation": False,
            "durationWrite": False,
            "sourceEndWrite": False,
            "pitchIdentityWrite": False,
            "modelInference": False,
            "decodedModelEndRead": False,
            "newThresholdSelection": False,
        },
    }


def run_self_test():
    first = minimal_inventory()
    second = copy.deepcopy(first)
    second["counts"]["durationEligibleEvents"] = 2
    second["counts"]["unresolvedEvents"] = 2
    second["resolutionContext"]["byMidi"]["55"]["eligibleCount"] = 2
    second["resolutionContext"]["byMidi"]["55"]["unresolvedCount"] = 2
    second["resolutionContext"]["byMidi"]["55"]["unresolvedPrimaryReasonCounts"][REATTACK_REASON] = 2
    second["resolutionContext"]["byMidi"]["55"]["unresolvedFallbackReasonCounts"]["NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION"] = 2
    second["unresolvedPrimaryReasons"][REATTACK_REASON]["count"] = 2
    second["reattackCensoredFallbackRejections"]["NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION"]["count"] = 2
    comparison = compare_inventories(first, second)
    assert comparison["countDeltas"] == {"durationEligibleEvents": 1, "unresolvedEvents": 1}
    assert comparison["unresolvedPrimaryReasonCountDeltas"] == {REATTACK_REASON: 1}
    assert comparison["reattackFallbackReasonCountDeltas"] == {"NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION": 1}
    assert comparison["midiCountReasonDeltas"]["55"]["eligibleCountDelta"] == 1
    assert comparison["midiCountReasonDeltas"]["55"]["unresolvedCountDelta"] == 1
    assert comparison["ownsAcceptanceDecision"] is False
    assert comparison["changesDuration"] is False
    assert comparison["thresholdSelection"] is False

    for field in ("changesDuration", "changesPitchIdentity", "invokesModel", "thresholdSelection", "thresholdSweep"):
        tampered = copy.deepcopy(first)
        tampered[field] = True
        try:
            compare_inventories(tampered, second)
        except RuntimeError as error:
            assert field in str(error)
        else:
            raise AssertionError(f"tampered top-level guard accepted: {field}")

    for field in HARD_FALSE_GUARDS:
        tampered = copy.deepcopy(first)
        tampered["hardGuards"][field] = True
        try:
            compare_inventories(tampered, second)
        except RuntimeError as error:
            assert field in str(error)
        else:
            raise AssertionError(f"tampered hard guard accepted: {field}")

    again = compare_inventories(first, second)
    assert json.dumps(comparison, sort_keys=True) == json.dumps(again, sort_keys=True)
    print(json.dumps({
        "contract": CONTRACT,
        "selfTest": "passed",
        "tamperCasesRejected": 5 + len(HARD_FALSE_GUARDS),
        "deterministic": True,
    }, sort_keys=True))


def main():
    args = parse_args()
    if args.self_test:
        run_self_test()
        return

    first_path = Path(args.first)
    second_path = Path(args.second)
    first = load_json(first_path)
    second = load_json(second_path)
    output = compare_inventories(first, second, first_path, second_path)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print(json.dumps({
        "contract": CONTRACT,
        "activationRuleEqual": output["activationRuleEqual"],
        "countDeltas": output["countDeltas"],
        "unresolvedPrimaryReasonCountDeltas": output["unresolvedPrimaryReasonCountDeltas"],
        "reattackFallbackReasonCountDeltas": output["reattackFallbackReasonCountDeltas"],
        "midiCountReasonDeltaKeys": list(output["midiCountReasonDeltas"].keys()),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
