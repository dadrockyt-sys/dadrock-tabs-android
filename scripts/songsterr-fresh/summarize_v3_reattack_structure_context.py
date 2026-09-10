#!/usr/bin/env python3

import argparse
import copy
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

CONTRACT = "songsterr-fresh-v3-reattack-structure-context-v1"
NOTE_EVIDENCE_CONTRACT = "songsterr-fresh-isolated-polyphonic-note-evidence-v1"
V3_RELEASE_CONTRACT = "songsterr-fresh-spectral-activation-release-evidence-v3"
CONTEXT_CONTRACT = "songsterr-fresh-note-evidence-context-v1"
REATTACK_REASON = "NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK"


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Describe same-pitch reattack spacing against the frozen tempo/structure map "
            "without writing durations or selecting release thresholds."
        )
    )
    parser.add_argument("--evidence", help="v3 note-evidence JSON")
    parser.add_argument("--context", help="frozen note-evidence context JSON")
    parser.add_argument("--output", help="descriptive output JSON")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test and not all((args.evidence, args.context, args.output)):
        parser.error("--evidence, --context, and --output are required unless --self-test is used")
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


def collect_structure_slots(structure_map):
    slots = set()
    measures = structure_map.get("measures")
    require(isinstance(measures, list) and measures, "V3_REATTACK_CONTEXT_MEASURES_MISSING")
    for measure in measures:
        for field in ("start", "end"):
            value = measure.get(field)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                slots.add(float(value))
        for beat in measure.get("beats") or []:
            start = beat.get("start")
            if isinstance(start, (int, float)) and not isinstance(start, bool):
                slots.add(float(start))
            for subdivision in beat.get("subdivisions") or []:
                slots.add(float(subdivision))
    return slots


def validate_inputs(evidence, context):
    require(evidence.get("contract") == NOTE_EVIDENCE_CONTRACT, "V3_REATTACK_CONTEXT_NOTE_EVIDENCE_CONTRACT_CHANGED")
    require(evidence.get("version") == 1, "V3_REATTACK_CONTEXT_NOTE_EVIDENCE_VERSION_CHANGED")
    provenance = evidence.get("provenance") or {}
    require(provenance.get("referenceBlind") is True, "V3_REATTACK_CONTEXT_REFERENCE_BLIND_GUARD_CHANGED")
    require(provenance.get("structureConditioned") is True, "V3_REATTACK_CONTEXT_STRUCTURE_CONDITIONING_MISSING")
    require(provenance.get("structureFrozen") is True, "V3_REATTACK_CONTEXT_STRUCTURE_FROZEN_GUARD_CHANGED")
    require(provenance.get("durationEvidenceSource") == V3_RELEASE_CONTRACT, "V3_REATTACK_CONTEXT_RELEASE_CONTRACT_CHANGED")
    require(provenance.get("durationEvidenceModelInvoked") is False, "V3_REATTACK_CONTEXT_RELEASE_MODEL_GUARD_CHANGED")
    for guard in (
        "decodedModelNoteEndUsedAsDuration",
        "nextOnsetUsedAsDuration",
        "samePitchReattackUsedAsDuration",
    ):
        require(provenance.get(guard) is False, f"V3_REATTACK_CONTEXT_DURATION_GUARD_CHANGED:{guard}")

    require(context.get("contract") == CONTEXT_CONTRACT, "V3_REATTACK_CONTEXT_STRUCTURE_CONTEXT_CONTRACT_CHANGED")
    require(context.get("version") == 1, "V3_REATTACK_CONTEXT_STRUCTURE_CONTEXT_VERSION_CHANGED")
    require(context.get("referenceBlind") is True, "V3_REATTACK_CONTEXT_STRUCTURE_REFERENCE_BLIND_GUARD_CHANGED")
    require(context.get("structureFrozen") is True, "V3_REATTACK_CONTEXT_FROZEN_STRUCTURE_GUARD_CHANGED")
    require((context.get("structureAcceptance") or {}).get("accepted") is True, "V3_REATTACK_CONTEXT_STRUCTURE_NOT_ACCEPTED")

    identity = context.get("structureIdentity") or {}
    require(identity.get("contract") == "songsterr-fresh-frozen-structure-identity-v1", "V3_REATTACK_CONTEXT_STRUCTURE_IDENTITY_CONTRACT_CHANGED")
    require(isinstance(identity.get("signature"), str) and identity.get("signature"), "V3_REATTACK_CONTEXT_STRUCTURE_IDENTITY_MISSING")

    structure_map = context.get("structureMap")
    require(isinstance(structure_map, dict), "V3_REATTACK_CONTEXT_STRUCTURE_MAP_MISSING")
    require(structure_map.get("referenceBlind") is True, "V3_REATTACK_CONTEXT_STRUCTURE_MAP_REFERENCE_BLIND_CHANGED")
    duration = structure_map.get("durationSeconds")
    require(isinstance(duration, (int, float)) and not isinstance(duration, bool) and duration > 0, "V3_REATTACK_CONTEXT_STRUCTURE_DURATION_INVALID")
    tempo_segments = structure_map.get("tempoSegments")
    require(isinstance(tempo_segments, list) and tempo_segments, "V3_REATTACK_CONTEXT_TEMPO_SEGMENTS_MISSING")

    previous_start = None
    for index, segment in enumerate(tempo_segments):
        start = segment.get("start")
        bpm = segment.get("bpm")
        require(isinstance(start, (int, float)) and not isinstance(start, bool), f"V3_REATTACK_CONTEXT_TEMPO_START_INVALID:{index}")
        require(isinstance(bpm, (int, float)) and not isinstance(bpm, bool) and bpm > 0, f"V3_REATTACK_CONTEXT_TEMPO_BPM_INVALID:{index}")
        if previous_start is not None:
            require(float(start) >= previous_start, f"V3_REATTACK_CONTEXT_TEMPO_ORDER_CHANGED:{index}")
        previous_start = float(start)

    slots = collect_structure_slots(structure_map)
    onsets = evidence.get("onsets")
    require(isinstance(onsets, list), "V3_REATTACK_CONTEXT_ONSETS_MISSING")
    for onset in onsets:
        if onset.get("classification") != "unambiguous" or onset.get("selectedMidi") is None:
            continue
        nearest = onset.get("nearestStructureSlot")
        require(isinstance(nearest, (int, float)) and not isinstance(nearest, bool), f"V3_REATTACK_CONTEXT_NEAREST_SLOT_MISSING:{onset.get('onsetId')}")
        require(float(nearest) in slots, f"V3_REATTACK_CONTEXT_EVIDENCE_STRUCTURE_MISMATCH:{onset.get('onsetId')}")


def integrated_tempo_beats(structure_map, start, end):
    require(end >= start, "V3_REATTACK_CONTEXT_NEGATIVE_REATTACK_GAP")
    duration = float(structure_map["durationSeconds"])
    require(start >= 0.0 and end <= duration + 1e-9, "V3_REATTACK_CONTEXT_REATTACK_OUTSIDE_STRUCTURE")
    total = 0.0
    covered = 0.0
    segments = structure_map["tempoSegments"]
    for segment in segments:
        segment_start = float(segment["start"])
        raw_end = segment.get("end")
        segment_end = float(raw_end) if raw_end is not None else duration
        overlap_start = max(float(start), segment_start)
        overlap_end = min(float(end), segment_end)
        if overlap_end <= overlap_start:
            continue
        span = overlap_end - overlap_start
        total += span * float(segment["bpm"]) / 60.0
        covered += span
    require(abs(covered - (end - start)) <= 1e-7, "V3_REATTACK_CONTEXT_TEMPO_COVERAGE_GAP")
    return total


def summarize_rows(rows):
    gaps = [row["reattackGapSeconds"] for row in rows if row["reattackGapSeconds"] is not None]
    beat_spans = [row["reattackTempoBeatSpan"] for row in rows if row["reattackTempoBeatSpan"] is not None]
    return {
        "eventCount": len(rows),
        "withFutureSamePitchReattackCount": len(gaps),
        "withoutFutureSamePitchReattackCount": len(rows) - len(gaps),
        "reattackGapSeconds": stats(gaps),
        "reattackTempoBeatSpan": stats(beat_spans),
    }


def build_summary(evidence, context, evidence_path=None, context_path=None):
    validate_inputs(evidence, context)
    structure_map = context["structureMap"]
    onsets = evidence["onsets"]
    rows = []

    for index, onset in enumerate(onsets):
        if onset.get("classification") != "unambiguous" or onset.get("selectedMidi") is None:
            continue
        midi = int(onset["selectedMidi"])
        source_start = float(onset["sourceStart"])
        next_same_pitch = None
        for later in onsets[index + 1:]:
            if later.get("classification") != "unambiguous" or later.get("selectedMidi") is None:
                continue
            if int(later["selectedMidi"]) == midi:
                next_same_pitch = later
                break

        gap = None
        beat_span = None
        if next_same_pitch is not None:
            next_start = float(next_same_pitch["sourceStart"])
            gap = next_start - source_start
            beat_span = integrated_tempo_beats(structure_map, source_start, next_start)

        duration_evidence = (onset.get("provenance") or {}).get("durationEvidence") or {}
        resolved = onset.get("durationSeconds") is not None
        primary_reason = None if resolved else duration_evidence.get("reason") or "UNDECLARED"
        fallback_reason = None
        if not resolved and primary_reason == REATTACK_REASON:
            fallback = duration_evidence.get("activationFallback") or {}
            require(fallback.get("attempted") is True, f"V3_REATTACK_CONTEXT_FALLBACK_PROVENANCE_MISSING:{onset.get('onsetId')}")
            require(fallback.get("resolved") is False, f"V3_REATTACK_CONTEXT_UNRESOLVED_FALLBACK_CHANGED:{onset.get('onsetId')}")
            fallback_reason = fallback.get("reason") or "UNDECLARED"

        rows.append({
            "onsetId": onset.get("onsetId"),
            "selectedMidi": midi,
            "resolved": resolved,
            "resolvedMethod": duration_evidence.get("method") if resolved else None,
            "unresolvedPrimaryReason": primary_reason,
            "unresolvedFallbackReason": fallback_reason,
            "reattackGapSeconds": gap,
            "reattackTempoBeatSpan": beat_span,
        })

    resolved = [row for row in rows if row["resolved"]]
    unresolved = [row for row in rows if not row["resolved"]]
    resolved_methods = defaultdict(list)
    primary_reasons = defaultdict(list)
    fallback_rejections = defaultdict(list)
    for row in rows:
        if row["resolved"]:
            resolved_methods[row["resolvedMethod"] or "UNDECLARED"].append(row)
        else:
            primary_reasons[row["unresolvedPrimaryReason"]].append(row)
            if row["unresolvedPrimaryReason"] == REATTACK_REASON:
                fallback_rejections[row["unresolvedFallbackReason"]].append(row)

    provenance = evidence.get("provenance") or {}
    output = {
        "contract": CONTRACT,
        "version": 1,
        "descriptiveOnly": True,
        "referenceBlind": True,
        "changesDuration": False,
        "changesPitchIdentity": False,
        "invokesModel": False,
        "usesDecodedModelNoteEndAsDuration": False,
        "usesNextOnsetAsDuration": False,
        "usesSamePitchReattackAsDuration": False,
        "proposesNewReleaseRule": False,
        "thresholdSelection": False,
        "thresholdSweep": False,
        "ownsAcceptanceDecision": False,
        "source": {
            "evidencePath": str(evidence_path) if evidence_path is not None else None,
            "evidenceSha256": sha256_file(evidence_path) if evidence_path is not None else None,
            "contextPath": str(context_path) if context_path is not None else None,
            "contextSha256": sha256_file(context_path) if context_path is not None else None,
            "noteInferenceIdentity": provenance.get("noteInferenceIdentity"),
            "structureIdentity": context.get("structureIdentity"),
            "durationEvidenceSource": provenance.get("durationEvidenceSource"),
        },
        "counts": {
            "durationEligibleEvents": len(rows),
            "resolvedEvents": len(resolved),
            "unresolvedEvents": len(unresolved),
        },
        "resolved": summarize_rows(resolved),
        "unresolved": summarize_rows(unresolved),
        "resolvedMethods": {
            reason: summarize_rows(group)
            for reason, group in sorted(resolved_methods.items())
        },
        "unresolvedPrimaryReasons": {
            reason: summarize_rows(group)
            for reason, group in sorted(primary_reasons.items())
        },
        "reattackCensoredFallbackRejections": {
            reason: summarize_rows(group)
            for reason, group in sorted(fallback_rejections.items())
        },
        "hardGuards": {
            "inputEventMutation": False,
            "durationWrite": False,
            "sourceEndWrite": False,
            "pitchIdentityWrite": False,
            "modelInference": False,
            "decodedModelEndRead": False,
            "reattackTimestampUsedAsDuration": False,
            "newThresholdSelection": False,
            "acceptanceDecision": False,
        },
    }
    return output


def minimal_inputs():
    structure_map = {
        "referenceBlind": True,
        "durationSeconds": 2.0,
        "tempoSegments": [{"start": 0.0, "end": None, "bpm": 120.0}],
        "measures": [{
            "start": 0.0,
            "end": 2.0,
            "beats": [
                {"start": 0.0, "subdivisions": [0.0, 0.125, 0.25, 0.375]},
                {"start": 0.5, "subdivisions": [0.5, 0.625, 0.75, 0.875]},
                {"start": 1.0, "subdivisions": [1.0, 1.125, 1.25, 1.375]},
                {"start": 1.5, "subdivisions": [1.5, 1.625, 1.75, 1.875]},
            ],
        }],
    }
    context = {
        "contract": CONTEXT_CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "structureFrozen": True,
        "structureIdentity": {
            "contract": "songsterr-fresh-frozen-structure-identity-v1",
            "version": 1,
            "signature": "fnv1a32:selftest",
            "canonicalLength": 1,
        },
        "structureAcceptance": {"accepted": True},
        "structureMap": structure_map,
    }
    evidence = {
        "contract": NOTE_EVIDENCE_CONTRACT,
        "version": 1,
        "provenance": {
            "referenceBlind": True,
            "structureConditioned": True,
            "structureFrozen": True,
            "durationEvidenceSource": V3_RELEASE_CONTRACT,
            "durationEvidenceModelInvoked": False,
            "decodedModelNoteEndUsedAsDuration": False,
            "nextOnsetUsedAsDuration": False,
            "samePitchReattackUsedAsDuration": False,
            "noteInferenceIdentity": {"sha256": "selftest"},
        },
        "onsets": [
            {
                "onsetId": "a",
                "sourceStart": 0.0,
                "nearestStructureSlot": 0.0,
                "classification": "unambiguous",
                "selectedMidi": 55,
                "durationSeconds": None,
                "provenance": {"durationEvidence": {
                    "resolved": False,
                    "reason": REATTACK_REASON,
                    "activationFallback": {
                        "attempted": True,
                        "resolved": False,
                        "reason": "NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION",
                    },
                }},
            },
            {
                "onsetId": "b",
                "sourceStart": 0.25,
                "nearestStructureSlot": 0.25,
                "classification": "unambiguous",
                "selectedMidi": 55,
                "durationSeconds": 0.20,
                "provenance": {"durationEvidence": {
                    "resolved": True,
                    "method": "selected-pitch-sustained-spectral-decay",
                }},
            },
        ],
    }
    return evidence, context


def run_self_test():
    evidence, context = minimal_inputs()
    result = build_summary(evidence, context)
    first = result["unresolvedPrimaryReasons"][REATTACK_REASON]
    assert first["eventCount"] == 1
    assert first["reattackGapSeconds"]["median"] == 0.25
    assert first["reattackTempoBeatSpan"]["median"] == 0.5
    assert result["usesSamePitchReattackAsDuration"] is False
    assert result["ownsAcceptanceDecision"] is False

    again = build_summary(evidence, context)
    assert json.dumps(result, sort_keys=True) == json.dumps(again, sort_keys=True)

    tampered = copy.deepcopy(evidence)
    tampered["provenance"]["samePitchReattackUsedAsDuration"] = True
    try:
        build_summary(tampered, context)
    except RuntimeError as error:
        assert "samePitchReattackUsedAsDuration" in str(error)
    else:
        raise AssertionError("reattack-as-duration tamper accepted")

    tampered_context = copy.deepcopy(context)
    tampered_context["structureFrozen"] = False
    try:
        build_summary(evidence, tampered_context)
    except RuntimeError as error:
        assert "FROZEN_STRUCTURE" in str(error)
    else:
        raise AssertionError("unfrozen structure accepted")

    mismatched = copy.deepcopy(context)
    mismatched["structureMap"]["measures"][0]["beats"][0]["subdivisions"][2] = 0.26
    try:
        build_summary(evidence, mismatched)
    except RuntimeError as error:
        assert "EVIDENCE_STRUCTURE_MISMATCH" in str(error)
    else:
        raise AssertionError("mismatched structure accepted")

    print(json.dumps({
        "contract": CONTRACT,
        "selfTest": "passed",
        "deterministic": True,
        "reattackUsedAsDuration": False,
        "tempoBeatIntegrationVerified": True,
        "tamperCasesRejected": 3,
    }, sort_keys=True))


def main():
    args = parse_args()
    if args.self_test:
        run_self_test()
        return

    evidence_path = Path(args.evidence)
    context_path = Path(args.context)
    evidence = load_json(evidence_path)
    context = load_json(context_path)
    output = build_summary(evidence, context, evidence_path, context_path)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print(json.dumps({
        "contract": CONTRACT,
        "counts": output["counts"],
        "resolvedMedianTempoBeatSpan": output["resolved"]["reattackTempoBeatSpan"]["median"],
        "unresolvedMedianTempoBeatSpan": output["unresolved"]["reattackTempoBeatSpan"]["median"],
        "reattackUnresolvedMedianTempoBeatSpan": output["unresolvedPrimaryReasons"].get(REATTACK_REASON, {}).get("reattackTempoBeatSpan", {}).get("median"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
