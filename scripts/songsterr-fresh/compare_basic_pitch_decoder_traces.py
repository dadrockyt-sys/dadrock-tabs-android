#!/usr/bin/env python3

"""Reference-blind comparison of exact Basic Pitch decoder replay traces.

This comparator consumes only traces that already proved exact replay of their
bound evidence. It measures semantic inventory, decoder-mechanism stability,
and decoder frame-span variation. It never defines an admission threshold,
changes note identity, scores a reference tab, or advances duration/delivery.
"""

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

TRACE_CONTRACT = "songsterr-fresh-basic-pitch-decoder-mechanism-trace-v1"
CONTRACT = "songsterr-fresh-basic-pitch-decoder-trace-comparison-v1"
MAX_SAMPLES = 50


class DecoderTraceComparisonError(RuntimeError):
    pass


def canonical_json(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise DecoderTraceComparisonError("CANONICAL_JSON_FAILED") from exc


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(
                handle,
                parse_constant=lambda value: (_ for _ in ()).throw(
                    DecoderTraceComparisonError(f"NONSTANDARD_JSON_CONSTANT:{value}")
                ),
            )
    except DecoderTraceComparisonError:
        raise
    except Exception as exc:
        raise DecoderTraceComparisonError(f"JSON_LOAD_FAILED:{path}") from exc


def finite(value, label):
    if isinstance(value, bool):
        raise DecoderTraceComparisonError(f"{label}:FINITE_NUMBER_REQUIRED")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise DecoderTraceComparisonError(f"{label}:FINITE_NUMBER_REQUIRED") from exc
    if not math.isfinite(number):
        raise DecoderTraceComparisonError(f"{label}:FINITE_NUMBER_REQUIRED")
    return number


def integer(value, label):
    if isinstance(value, bool):
        raise DecoderTraceComparisonError(f"{label}:INTEGER_REQUIRED")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise DecoderTraceComparisonError(f"{label}:INTEGER_REQUIRED") from exc
    if number != value:
        raise DecoderTraceComparisonError(f"{label}:INTEGER_REQUIRED")
    return number


def sha256(value, label):
    if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise DecoderTraceComparisonError(f"{label}:SHA256_INVALID")
    return value


def require_bool(mapping, key, expected, label):
    if not isinstance(mapping, dict) or mapping.get(key) is not expected:
        raise DecoderTraceComparisonError(f"{label}.{key}:EXPECTED_{str(expected).upper()}")


def validate_identity(identity, label):
    if not isinstance(identity, dict):
        raise DecoderTraceComparisonError(f"{label}:IDENTITY_REQUIRED")
    sha256(identity.get("sha256"), f"{label}.sha256")
    return identity


def semantic_key(event):
    return (finite(event.get("nearestStructureSlot"), "event.nearestStructureSlot"), integer(event.get("selectedMidi"), "event.selectedMidi"))


def event_order(event):
    return (
        finite(event.get("sourceStart"), "event.sourceStart"),
        integer(event.get("decoderStartFrame"), "event.decoderStartFrame"),
        finite(event.get("diagnosticModelEndSeconds"), "event.diagnosticModelEndSeconds"),
        integer(event.get("decoderEndFrame"), "event.decoderEndFrame"),
        finite(event.get("noteSpanMeanActivation"), "event.noteSpanMeanActivation"),
    )


def validate_trace(trace, label):
    if not isinstance(trace, dict):
        raise DecoderTraceComparisonError(f"{label}:OBJECT_REQUIRED")
    if trace.get("contract") != TRACE_CONTRACT or trace.get("version") != 1:
        raise DecoderTraceComparisonError(f"{label}:TRACE_CONTRACT_CHANGED")
    require_bool(trace, "referenceBlind", True, label)
    require_bool(trace, "measurementOnly", True, label)
    evidence_sha = sha256(trace.get("sourceEvidenceSha256"), f"{label}.sourceEvidenceSha256")
    note_identity = validate_identity(trace.get("noteInferenceIdentity"), f"{label}.noteInferenceIdentity")
    activation_identity = validate_identity(trace.get("activationEvidenceIdentity"), f"{label}.activationEvidenceIdentity")
    decision_identity = validate_identity(trace.get("decisionSurfaceIdentity"), f"{label}.decisionSurfaceIdentity")

    decoder = trace.get("decoderContract")
    if not isinstance(decoder, dict):
        raise DecoderTraceComparisonError(f"{label}:DECODER_CONTRACT_REQUIRED")
    if decoder.get("basicPitchPackageVersion") != "0.4.0":
        raise DecoderTraceComparisonError(f"{label}:BASIC_PITCH_VERSION_CHANGED")
    if decoder.get("inferOnsets") is not True or decoder.get("inferOnsetDiffCount") != 2 or decoder.get("melodiaTrick") is not True:
        raise DecoderTraceComparisonError(f"{label}:DECODER_MECHANICS_CHANGED")
    finite(decoder.get("onsetThreshold"), f"{label}.decoderContract.onsetThreshold")
    finite(decoder.get("frameThreshold"), f"{label}.decoderContract.frameThreshold")
    finite(decoder.get("minimumNoteLengthMs"), f"{label}.decoderContract.minimumNoteLengthMs")
    integer(decoder.get("minimumNoteLengthFrames"), f"{label}.decoderContract.minimumNoteLengthFrames")
    integer(decoder.get("energyToleranceFrames"), f"{label}.decoderContract.energyToleranceFrames")

    hard = trace.get("hardGuards")
    for key, expected in {
        "decoderReplayExactlyReproducedEvidence": True,
        "modelInvokedByTracer": False,
        "changesDecodedEventInventory": False,
        "usedForAcceptance": False,
        "usedForDuration": False,
        "referenceTabUsed": False,
        "professionalScorerUsed": False,
        "legacyV143ScorerImported": False,
    }.items():
        require_bool(hard, key, expected, f"{label}.hardGuards")

    policy = trace.get("policyBoundary")
    for key, expected in {
        "thresholdsAppliedForAdmission": False,
        "admissionDecisionMade": False,
        "modelValidationComplete": False,
        "mayAdvanceDelivery": False,
        "durationAuthorityChanged": False,
    }.items():
        require_bool(policy, key, expected, f"{label}.policyBoundary")

    events = trace.get("events")
    if not isinstance(events, list):
        raise DecoderTraceComparisonError(f"{label}:EVENTS_REQUIRED")
    if integer(trace.get("eventCount"), f"{label}.eventCount") != len(events):
        raise DecoderTraceComparisonError(f"{label}:EVENT_COUNT_MISMATCH")

    mechanisms = Counter()
    normalized = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise DecoderTraceComparisonError(f"{label}.events[{index}]:OBJECT_REQUIRED")
        key = semantic_key(event)
        order = event_order(event)
        mechanism = event.get("decoderMechanism")
        if mechanism not in {"threshold-onset-pass", "melodia-residual-pass"}:
            raise DecoderTraceComparisonError(f"{label}.events[{index}]:MECHANISM_INVALID")
        if order[1] < 0 or order[3] <= order[1]:
            raise DecoderTraceComparisonError(f"{label}.events[{index}]:FRAME_SPAN_INVALID")
        mechanisms[mechanism] += 1
        normalized.append({
            "nearestStructureSlot": key[0],
            "selectedMidi": key[1],
            "sourceStart": order[0],
            "decoderStartFrame": order[1],
            "diagnosticModelEndSeconds": order[2],
            "decoderEndFrame": order[3],
            "noteSpanMeanActivation": order[4],
            "decoderMechanism": mechanism,
        })

    declared_counts = trace.get("mechanismCounts")
    if not isinstance(declared_counts, dict) or dict(sorted(mechanisms.items())) != declared_counts:
        raise DecoderTraceComparisonError(f"{label}:MECHANISM_COUNT_MISMATCH")

    return {
        "sourceEvidenceSha256": evidence_sha,
        "noteInferenceSha256": note_identity["sha256"],
        "activationEvidenceSha256": activation_identity["sha256"],
        "decisionSurfaceSha256": decision_identity["sha256"],
        "decoderContract": decoder,
        "events": normalized,
        "mechanismCounts": dict(sorted(mechanisms.items())),
    }


def group_events(events):
    groups = defaultdict(list)
    for event in events:
        groups[semantic_key(event)].append(event)
    for key in groups:
        groups[key].sort(key=event_order)
    return groups


def numeric_stats(values):
    if not values:
        return {"count": 0, "differentCount": 0, "maxAbsolute": 0.0, "meanAbsolute": 0.0}
    absolute = [abs(float(value)) for value in values]
    return {
        "count": len(absolute),
        "differentCount": sum(value != 0.0 for value in absolute),
        "maxAbsolute": max(absolute),
        "meanAbsolute": sum(absolute) / len(absolute),
    }


def integer_stats(values):
    stats = numeric_stats(values)
    stats["maxAbsolute"] = int(stats["maxAbsolute"])
    return stats


def compare_validated(first, second):
    if first["decoderContract"] != second["decoderContract"]:
        raise DecoderTraceComparisonError("NOT_COMPARABLE:DECODER_CONTRACT_MISMATCH")

    groups_first = group_events(first["events"])
    groups_second = group_events(second["events"])
    all_keys = sorted(set(groups_first) | set(groups_second), key=lambda item: (item[0], item[1]))

    unmatched = []
    mechanism_mismatches = []
    start_frame_deltas = []
    end_frame_deltas = []
    source_start_deltas = []
    model_end_deltas = []
    activation_deltas = []
    common_count = 0

    for key in all_keys:
        a = groups_first.get(key, [])
        b = groups_second.get(key, [])
        pair_count = min(len(a), len(b))
        for index in range(pair_count):
            event_a = a[index]
            event_b = b[index]
            common_count += 1
            if event_a["decoderMechanism"] != event_b["decoderMechanism"]:
                mechanism_mismatches.append({
                    "nearestStructureSlot": key[0],
                    "selectedMidi": key[1],
                    "mechanismFirst": event_a["decoderMechanism"],
                    "mechanismSecond": event_b["decoderMechanism"],
                })
            start_frame_deltas.append(event_b["decoderStartFrame"] - event_a["decoderStartFrame"])
            end_frame_deltas.append(event_b["decoderEndFrame"] - event_a["decoderEndFrame"])
            source_start_deltas.append(event_b["sourceStart"] - event_a["sourceStart"])
            model_end_deltas.append(event_b["diagnosticModelEndSeconds"] - event_a["diagnosticModelEndSeconds"])
            activation_deltas.append(event_b["noteSpanMeanActivation"] - event_a["noteSpanMeanActivation"])
        for side, event in [("first", item) for item in a[pair_count:]] + [("second", item) for item in b[pair_count:]]:
            unmatched.append({
                "nearestStructureSlot": key[0],
                "selectedMidi": key[1],
                "presentIn": side,
                "decoderMechanism": event["decoderMechanism"],
                "sourceStart": event["sourceStart"],
                "decoderStartFrame": event["decoderStartFrame"],
                "decoderEndFrame": event["decoderEndFrame"],
            })

    return {
        "semanticInventory": {
            "eventCountFirst": len(first["events"]),
            "eventCountSecond": len(second["events"]),
            "commonPairedEventCount": common_count,
            "unmatchedSemanticEventCount": len(unmatched),
            "unmatchedSemanticEventSamples": unmatched[:MAX_SAMPLES],
            "unmatchedSampleLimit": MAX_SAMPLES,
        },
        "decoderMechanism": {
            "countsFirst": first["mechanismCounts"],
            "countsSecond": second["mechanismCounts"],
            "commonMechanismMismatchCount": len(mechanism_mismatches),
            "commonMechanismMismatchSamples": mechanism_mismatches[:MAX_SAMPLES],
            "mismatchSampleLimit": MAX_SAMPLES,
        },
        "commonEventVariation": {
            "decoderStartFrameDelta": integer_stats(start_frame_deltas),
            "decoderEndFrameDelta": integer_stats(end_frame_deltas),
            "sourceStartSecondsDelta": numeric_stats(source_start_deltas),
            "diagnosticModelEndSecondsDelta": numeric_stats(model_end_deltas),
            "noteSpanMeanActivationDelta": numeric_stats(activation_deltas),
        },
    }


def build_report(trace_a, trace_b):
    a = validate_trace(trace_a, "inputA")
    b = validate_trace(trace_b, "inputB")
    ordered = sorted([a, b], key=lambda item: (item["sourceEvidenceSha256"], item["decisionSurfaceSha256"]))
    first, second = ordered
    return {
        "contract": CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "measurementOnly": True,
        "canonicalInputOrdering": "source-evidence-sha256+decision-surface-sha256",
        "inputs": [
            {
                "sourceEvidenceSha256": first["sourceEvidenceSha256"],
                "noteInferenceSha256": first["noteInferenceSha256"],
                "activationEvidenceSha256": first["activationEvidenceSha256"],
                "decisionSurfaceSha256": first["decisionSurfaceSha256"],
            },
            {
                "sourceEvidenceSha256": second["sourceEvidenceSha256"],
                "noteInferenceSha256": second["noteInferenceSha256"],
                "activationEvidenceSha256": second["activationEvidenceSha256"],
                "decisionSurfaceSha256": second["decisionSurfaceSha256"],
            },
        ],
        "measurement": compare_validated(first, second),
        "interpretationBoundary": {
            "frameDeltasAreRepresentationDiagnosticsOnly": True,
            "noteSpanMeanActivationIsDiagnosticOnly": True,
            "observedVariationDoesNotDefineAdmissionTolerance": True,
            "mechanismStabilityDoesNotPromoteModelValidation": True,
        },
        "policyBoundary": {
            "status": "MEASURED_BASIC_PITCH_DECODER_TRACE_VARIATION",
            "thresholdsAppliedForAdmission": False,
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "changesDecodedEventInventory": False,
            "referenceTabUsed": False,
            "professionalScorerUsed": False,
            "legacyV143ScorerImported": False,
        },
    }


def make_trace(seed, events):
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    counts = Counter(event["decoderMechanism"] for event in events)
    identity = lambda suffix: {"sha256": hashlib.sha256((seed + suffix).encode("utf-8")).hexdigest()}
    return {
        "contract": TRACE_CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "measurementOnly": True,
        "sourceEvidenceSha256": digest,
        "noteInferenceIdentity": identity("note"),
        "activationEvidenceIdentity": identity("activation"),
        "decisionSurfaceIdentity": identity("decision"),
        "decoderContract": {
            "basicPitchPackageVersion": "0.4.0",
            "inferOnsets": True,
            "inferOnsetDiffCount": 2,
            "onsetThreshold": 0.5,
            "frameThreshold": 0.3,
            "minimumNoteLengthMs": 127.7,
            "minimumNoteLengthFrames": 11,
            "melodiaTrick": True,
            "energyToleranceFrames": 11,
        },
        "eventCount": len(events),
        "mechanismCounts": dict(sorted(counts.items())),
        "events": events,
        "hardGuards": {
            "decoderReplayExactlyReproducedEvidence": True,
            "modelInvokedByTracer": False,
            "changesDecodedEventInventory": False,
            "usedForAcceptance": False,
            "usedForDuration": False,
            "referenceTabUsed": False,
            "professionalScorerUsed": False,
            "legacyV143ScorerImported": False,
        },
        "policyBoundary": {
            "thresholdsAppliedForAdmission": False,
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
        },
    }


def run_self_test():
    base = [
        {"sourceStart": 1.0, "diagnosticModelEndSeconds": 1.2, "selectedMidi": 40, "noteSpanMeanActivation": 0.8, "nearestStructureSlot": 0.95, "decoderStartFrame": 100, "decoderEndFrame": 120, "decoderMechanism": "threshold-onset-pass"},
        {"sourceStart": 2.0, "diagnosticModelEndSeconds": 2.3, "selectedMidi": 64, "noteSpanMeanActivation": 0.6, "nearestStructureSlot": 1.95, "decoderStartFrame": 200, "decoderEndFrame": 230, "decoderMechanism": "melodia-residual-pass"},
    ]
    varied = [
        {**base[0], "sourceStart": 1.02, "decoderStartFrame": 102, "decoderEndFrame": 123, "diagnosticModelEndSeconds": 1.23, "noteSpanMeanActivation": 0.79},
        dict(base[1]),
        {"sourceStart": 3.0, "diagnosticModelEndSeconds": 3.2, "selectedMidi": 55, "noteSpanMeanActivation": 0.4, "nearestStructureSlot": 2.95, "decoderStartFrame": 300, "decoderEndFrame": 320, "decoderMechanism": "threshold-onset-pass"},
    ]
    first = make_trace("first", base)
    second = make_trace("second", varied)
    report = build_report(first, second)
    measurement = report["measurement"]
    assert measurement["semanticInventory"]["unmatchedSemanticEventCount"] == 1
    assert measurement["decoderMechanism"]["commonMechanismMismatchCount"] == 0
    assert measurement["commonEventVariation"]["decoderStartFrameDelta"]["differentCount"] == 1
    assert measurement["commonEventVariation"]["decoderStartFrameDelta"]["maxAbsolute"] == 2
    assert build_report(first, second) == build_report(second, first)
    assert report["policyBoundary"]["modelValidationComplete"] is False
    assert report["interpretationBoundary"]["observedVariationDoesNotDefineAdmissionTolerance"] is True

    bad = json.loads(json.dumps(first))
    bad["hardGuards"]["decoderReplayExactlyReproducedEvidence"] = False
    try:
        build_report(bad, second)
    except DecoderTraceComparisonError:
        pass
    else:
        raise AssertionError("non-exact replay trace must fail closed")

    print(json.dumps({
        "contract": CONTRACT,
        "selfTest": "PASS",
        "argumentOrderInvariant": True,
        "exactReplayRequired": True,
        "referenceBlind": True,
        "measurementOnly": True,
        "modelValidationComplete": False,
        "thresholdsAppliedForAdmission": False,
    }, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("trace_a", nargs="?")
    parser.add_argument("trace_b", nargs="?")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return
    if not args.trace_a or not args.trace_b:
        raise DecoderTraceComparisonError("TWO_DECODER_TRACES_REQUIRED")
    report = build_report(load_json(args.trace_a), load_json(args.trace_b))
    text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    try:
        main()
    except DecoderTraceComparisonError as exc:
        print(f"DECODER_TRACE_COMPARISON_ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2)
