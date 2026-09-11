#!/usr/bin/env python3

"""Reference-blind comparison of same-inference Basic Pitch decision surfaces.

The comparator explains inventory differences without making an admission
judgment. It samples decoder-native raw/effective onset and note-frame
activations at unmatched semantic events and measures full-matrix variation.
"""

import argparse
import copy
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from basic_pitch_activation_evidence import decode_and_verify_activation_sidecar
from basic_pitch_decision_surface_diagnostic import (
    CONTRACT as DECISION_CONTRACT,
    DecisionSurfaceError,
    build_decision_surface_sidecar,
    decode_and_verify_decision_surface,
)
from compare_basic_pitch_cross_run_evidence import (
    ComparisonError,
    canonical_json,
    make_test_evidence,
    semantic_key,
    sorted_group,
    validate_evidence,
)

CONTRACT = "songsterr-fresh-basic-pitch-decision-surface-comparison-v1"
MAX_UNMATCHED_SAMPLES = 50


class DecisionComparisonError(RuntimeError):
    pass


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(
                handle,
                parse_constant=lambda value: (_ for _ in ()).throw(
                    DecisionComparisonError(f"NONSTANDARD_JSON_CONSTANT:{value}")
                ),
            )
    except DecisionComparisonError:
        raise
    except Exception as exc:
        raise DecisionComparisonError(f"JSON_LOAD_FAILED:{path}") from exc


def finite(value, label):
    if isinstance(value, bool):
        raise DecisionComparisonError(f"{label}:FINITE_REQUIRED")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise DecisionComparisonError(f"{label}:FINITE_REQUIRED") from exc
    if not math.isfinite(number):
        raise DecisionComparisonError(f"{label}:FINITE_REQUIRED")
    return number


def digest_json(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def matrix_stats(first, second):
    a = np.asarray(first, dtype=np.float64)
    b = np.asarray(second, dtype=np.float64)
    if a.shape != b.shape or a.size == 0:
        raise DecisionComparisonError("DECISION_MATRIX_SHAPE_MISMATCH")
    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise DecisionComparisonError("DECISION_MATRIX_NONFINITE")
    delta = np.abs(b - a)
    return {
        "elementCount": int(delta.size),
        "meanAbsolute": float(np.mean(delta)),
        "rmsAbsolute": float(np.sqrt(np.mean(delta * delta))),
        "maxAbsolute": float(np.max(delta)),
        "exactElementCount": int(np.sum(delta == 0.0)),
        "differentElementCount": int(np.sum(delta != 0.0)),
    }


def strict_peak(matrix, frame_index, midi_index):
    if frame_index <= 0 or frame_index >= matrix.shape[0] - 1:
        return False
    value = float(matrix[frame_index, midi_index])
    return value > float(matrix[frame_index - 1, midi_index]) and value > float(matrix[frame_index + 1, midi_index])


def local_three_max(matrix, frame_index, midi_index):
    start = max(0, frame_index - 1)
    stop = min(matrix.shape[0], frame_index + 2)
    return float(np.max(matrix[start:stop, midi_index]))


def semantic_groups(onsets):
    groups = defaultdict(list)
    for onset in onsets:
        groups[semantic_key(onset)].append(onset)
    return {key: sorted_group(events) for key, events in groups.items()}


def validate_input(evidence, activation, decision, label):
    try:
        validated = validate_evidence(evidence, label)
        decoded_activation = decode_and_verify_activation_sidecar(activation, evidence=evidence)
        decoded_decision = decode_and_verify_decision_surface(
            decision,
            activation_payload=activation,
            evidence=evidence,
        )
    except (ComparisonError, DecisionSurfaceError, RuntimeError) as exc:
        raise DecisionComparisonError(f"{label}:INVALID_OR_UNBOUND:{exc}") from exc

    if decision.get("contract") != DECISION_CONTRACT:
        raise DecisionComparisonError(f"{label}:DECISION_CONTRACT_CHANGED")
    if decision.get("model") != validated["model"]:
        raise DecisionComparisonError(f"{label}:DECISION_MODEL_MISMATCH")
    if decision.get("provenance", {}).get("audioSource") != validated["audioSource"]:
        raise DecisionComparisonError(f"{label}:DECISION_AUDIO_SOURCE_MISMATCH")
    if decision.get("provenance", {}).get("separationSource") != validated["separationSource"]:
        raise DecisionComparisonError(f"{label}:DECISION_SEPARATION_SOURCE_MISMATCH")

    frame_times = np.asarray(decoded_activation["frameTimesSeconds"], dtype=np.float64)
    note_frames = np.asarray(decoded_activation["activations"], dtype=np.float64)
    raw = np.asarray(decoded_decision["rawOnsets"], dtype=np.float64)
    effective = np.asarray(decoded_decision["effectiveOnsets"], dtype=np.float64)
    if note_frames.shape != raw.shape or raw.shape != effective.shape:
        raise DecisionComparisonError(f"{label}:DECISION_ACTIVATION_SHAPE_MISMATCH")
    if frame_times.ndim != 1 or len(frame_times) != raw.shape[0]:
        raise DecisionComparisonError(f"{label}:FRAME_TIME_SHAPE_MISMATCH")

    return {
        "digestSha256": validated["digestSha256"],
        "structureIdentity": validated["structureIdentity"],
        "audioSource": validated["audioSource"],
        "model": validated["model"],
        "onsets": validated["onsets"],
        "noteIdentity": validated["noteIdentity"],
        "activationIdentity": validated["activationIdentity"],
        "decisionIdentity": copy.deepcopy(decision["decisionSurfaceIdentity"]),
        "frameTimes": frame_times,
        "noteFrames": note_frames,
        "rawOnsets": raw,
        "effectiveOnsets": effective,
        "minimumMidi": decoded_decision["minimumMidi"],
        "maximumMidi": decoded_decision["maximumMidi"],
    }


def sample_surface(item, source_start, midi, threshold):
    if midi < item["minimumMidi"] or midi > item["maximumMidi"]:
        raise DecisionComparisonError("UNMATCHED_MIDI_OUTSIDE_DECISION_SURFACE")
    distances = np.abs(item["frameTimes"] - float(source_start))
    frame_index = int(np.argmin(distances))
    midi_index = int(midi - item["minimumMidi"])
    raw = float(item["rawOnsets"][frame_index, midi_index])
    effective = float(item["effectiveOnsets"][frame_index, midi_index])
    note = float(item["noteFrames"][frame_index, midi_index])
    return {
        "frameIndex": frame_index,
        "frameTimeSeconds": float(item["frameTimes"][frame_index]),
        "absoluteSourceStartToFrameTimeSeconds": float(distances[frame_index]),
        "rawOnsetActivation": raw,
        "effectiveOnsetActivation": effective,
        "noteFrameActivation": note,
        "effectiveOnsetMinusThreshold": effective - threshold,
        "effectiveStrictLocalPeakAtFrame": strict_peak(item["effectiveOnsets"], frame_index, midi_index),
        "effectiveAtOrAboveThresholdAtFrame": effective >= threshold,
        "rawLocalThreeFrameMax": local_three_max(item["rawOnsets"], frame_index, midi_index),
        "effectiveLocalThreeFrameMax": local_three_max(item["effectiveOnsets"], frame_index, midi_index),
        "noteLocalThreeFrameMax": local_three_max(item["noteFrames"], frame_index, midi_index),
    }


def peak_inventory(matrix, minimum_midi, threshold):
    counts = Counter()
    for frame_index in range(1, matrix.shape[0] - 1):
        row = matrix[frame_index]
        mask = (row > matrix[frame_index - 1]) & (row > matrix[frame_index + 1]) & (row >= threshold)
        for midi_index in np.flatnonzero(mask):
            counts[int(minimum_midi + midi_index)] += 1
    return counts


def compare_inputs(first, second):
    if first["structureIdentity"] != second["structureIdentity"]:
        raise DecisionComparisonError("NOT_COMPARABLE:STRUCTURE_IDENTITY_MISMATCH")
    if first["audioSource"] != second["audioSource"]:
        raise DecisionComparisonError("NOT_COMPARABLE:AUDIO_SOURCE_MISMATCH")
    if first["model"] != second["model"]:
        raise DecisionComparisonError("NOT_COMPARABLE:MODEL_SETTINGS_MISMATCH")
    if first["minimumMidi"] != second["minimumMidi"] or first["maximumMidi"] != second["maximumMidi"]:
        raise DecisionComparisonError("NOT_COMPARABLE:MIDI_RANGE_MISMATCH")
    if first["activationIdentity"]["frameTimesSha256"] != second["activationIdentity"]["frameTimesSha256"]:
        raise DecisionComparisonError("NOT_COMPARABLE:FRAME_TIME_IDENTITY_MISMATCH")
    if not np.array_equal(first["frameTimes"], second["frameTimes"]):
        raise DecisionComparisonError("NOT_COMPARABLE:FRAME_TIME_VALUES_MISMATCH")

    threshold = finite(first["model"].get("onsetThreshold"), "model.onsetThreshold")
    groups_first = semantic_groups(first["onsets"])
    groups_second = semantic_groups(second["onsets"])
    all_keys = sorted(set(groups_first) | set(groups_second), key=lambda key: (key[0], key[1]))
    unmatched = []
    for key in all_keys:
        a = groups_first.get(key, [])
        b = groups_second.get(key, [])
        pair_count = min(len(a), len(b))
        extras = [("first", event) for event in a[pair_count:]] + [("second", event) for event in b[pair_count:]]
        for present_side, event in extras:
            source_start = float(event["sourceStart"])
            midi = int(event["selectedMidi"])
            unmatched.append({
                "nearestStructureSlot": key[0],
                "selectedMidi": key[1],
                "presentIn": present_side,
                "sourceStart": source_start,
                "semanticKeyCountFirst": len(a),
                "semanticKeyCountSecond": len(b),
                "firstSurface": sample_surface(first, source_start, midi, threshold),
                "secondSurface": sample_surface(second, source_start, midi, threshold),
            })

    peak_first = peak_inventory(first["effectiveOnsets"], first["minimumMidi"], threshold)
    peak_second = peak_inventory(second["effectiveOnsets"], second["minimumMidi"], threshold)
    midi_values = sorted(set(peak_first) | set(peak_second))
    peak_delta = {
        str(midi): peak_second.get(midi, 0) - peak_first.get(midi, 0)
        for midi in midi_values
        if peak_second.get(midi, 0) != peak_first.get(midi, 0)
    }

    return {
        "matrixVariation": {
            "rawOnsetActivation": matrix_stats(first["rawOnsets"], second["rawOnsets"]),
            "effectiveOnsetActivation": matrix_stats(first["effectiveOnsets"], second["effectiveOnsets"]),
            "noteFrameActivation": matrix_stats(first["noteFrames"], second["noteFrames"]),
        },
        "effectiveThresholdPeakInventory": {
            "onsetThreshold": threshold,
            "countFirst": int(sum(peak_first.values())),
            "countSecond": int(sum(peak_second.values())),
            "absoluteCountDifference": abs(int(sum(peak_first.values())) - int(sum(peak_second.values()))),
            "midiHistogramDeltaSecondMinusFirst": peak_delta,
        },
        "semanticInventory": {
            "eventCountFirst": len(first["onsets"]),
            "eventCountSecond": len(second["onsets"]),
            "unmatchedSemanticEventCount": len(unmatched),
            "unmatchedSemanticEventSamples": unmatched[:MAX_UNMATCHED_SAMPLES],
            "unmatchedSampleLimit": MAX_UNMATCHED_SAMPLES,
        },
    }


def build_report(evidence_a, activation_a, decision_a, evidence_b, activation_b, decision_b):
    a = validate_input(evidence_a, activation_a, decision_a, "inputA")
    b = validate_input(evidence_b, activation_b, decision_b, "inputB")
    ordered = sorted([a, b], key=lambda item: (item["digestSha256"], item["decisionIdentity"]["sha256"]))
    first, second = ordered
    return {
        "contract": CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "measurementOnly": True,
        "canonicalInputOrdering": "evidence-sha256+decision-surface-sha256",
        "inputs": [
            {
                "canonicalEvidenceSha256": first["digestSha256"],
                "noteInferenceSha256": first["noteIdentity"]["sha256"],
                "activationBundleSha256": first["activationIdentity"]["sha256"],
                "decisionSurfaceSha256": first["decisionIdentity"]["sha256"],
            },
            {
                "canonicalEvidenceSha256": second["digestSha256"],
                "noteInferenceSha256": second["noteIdentity"]["sha256"],
                "activationBundleSha256": second["activationIdentity"]["sha256"],
                "decisionSurfaceSha256": second["decisionIdentity"]["sha256"],
            },
        ],
        "measurement": compare_inputs(first, second),
        "interpretationBoundary": {
            "effectiveOnsetThresholdIsDecoderSetting": True,
            "thresholdMarginIsDescriptiveOnly": True,
            "melodiaCanCreateNotesWithoutThresholdedOnsetPeak": True,
            "unmatchedEventIsNotAutomaticallyThresholdFailure": True,
        },
        "policyBoundary": {
            "status": "MEASURED_BASIC_PITCH_DECISION_SURFACE_VARIATION",
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


def _patch_identity(evidence, activation_payload):
    patched = copy.deepcopy(evidence)
    note_identity = copy.deepcopy(activation_payload["noteInferenceIdentity"])
    bundle = copy.deepcopy(activation_payload["inferenceBundleIdentity"])
    patched["diagnostics"]["noteInferenceIdentity"] = copy.deepcopy(note_identity)
    patched["provenance"]["noteInferenceIdentity"] = copy.deepcopy(note_identity)
    patched["diagnostics"]["activationEvidenceIdentity"] = copy.deepcopy(bundle)
    patched["provenance"]["activationEvidenceIdentity"] = copy.deepcopy(bundle)
    patched["diagnostics"]["sameInferenceActivationEvidenceCaptured"] = True
    patched["provenance"]["activationEvidenceSameInference"] = True
    return patched


def _make_bundle(events, variant=False):
    evidence = make_test_evidence(events)
    frame_count = 32
    full_bins = 88
    note_matrix = np.zeros((frame_count, full_bins), dtype=np.float32)
    onset_matrix = np.zeros((frame_count, full_bins), dtype=np.float32)
    for frame in range(frame_count):
        note_matrix[frame, :] = 0.02 + frame * 0.0001
    for index, event in enumerate(events):
        start, _slot, midi, confidence, _end = event
        frame = min(frame_count - 2, max(1, int(round(start * 8))))
        col = midi - 21
        note_matrix[max(0, frame - 1):min(frame_count, frame + 4), col] = 0.7 + (0.001 if variant else 0.0)
        onset_matrix[frame, col] = 0.72 + (0.002 if variant else 0.0)
    onset_matrix[3, 40 - 21] = 0.9
    note_matrix[2:5, 40 - 21] = [0.2, 0.8, 0.4]
    frame_times = np.arange(frame_count, dtype=np.float64) / 8.0
    notes = [
        {"startSeconds": e[0], "midi": e[2], "confidence": e[3]}
        for e in events
    ]
    model = evidence["diagnostics"]["polyphonicInference"]
    from basic_pitch_activation_evidence import build_activation_sidecar
    activation = build_activation_sidecar(
        model_note_matrix=note_matrix,
        frame_times=frame_times,
        notes=notes,
        minimum_midi=40,
        maximum_midi=88,
        audio_source=evidence["provenance"]["audioSource"],
        separation_source=evidence["provenance"]["sourceSeparationSource"],
        model_metadata=model,
    )
    evidence = _patch_identity(evidence, activation)
    decision = build_decision_surface_sidecar(
        model_onset_matrix=onset_matrix,
        model_note_matrix=note_matrix,
        note_identity=activation["noteInferenceIdentity"],
        activation_bundle_identity=activation["inferenceBundleIdentity"],
        minimum_midi=40,
        maximum_midi=88,
        audio_source=evidence["provenance"]["audioSource"],
        separation_source=evidence["provenance"]["sourceSeparationSource"],
        model_metadata=model,
    )
    return evidence, activation, decision


def run_self_test():
    common = [
        (1.000, 1.000, 40, 0.80, 1.40),
        (2.000, 2.000, 52, 0.70, 2.40),
    ]
    extra = common + [(2.750, 2.750, 64, 0.60, 3.10)]
    a = _make_bundle(common, variant=False)
    b = _make_bundle(extra, variant=True)
    forward = build_report(*a, *b)
    reverse = build_report(*b, *a)
    assert canonical_json(forward) == canonical_json(reverse)
    assert forward["measurement"]["semanticInventory"]["unmatchedSemanticEventCount"] == 1
    sample = forward["measurement"]["semanticInventory"]["unmatchedSemanticEventSamples"][0]
    assert sample["selectedMidi"] == 64
    assert "effectiveOnsetMinusThreshold" in sample["firstSurface"]
    assert "effectiveOnsetMinusThreshold" in sample["secondSurface"]
    assert forward["measurement"]["matrixVariation"]["effectiveOnsetActivation"]["differentElementCount"] > 0
    assert forward["policyBoundary"]["admissionDecisionMade"] is False
    assert forward["policyBoundary"]["modelValidationComplete"] is False
    assert forward["policyBoundary"]["changesDecodedEventInventory"] is False

    tampered = copy.deepcopy(b[2])
    tampered["hardGuards"]["usedForAcceptance"] = True
    try:
        build_report(*a, b[0], b[1], tampered)
    except DecisionComparisonError as exc:
        assert "usedForAcceptance" in str(exc)
    else:
        raise AssertionError("unsafe decision surface must fail")

    print(json.dumps({
        "contract": CONTRACT,
        "selfTest": "PASS",
        "argumentOrderInvariant": True,
        "unmatchedSemanticEventsMeasured": True,
        "thresholdMarginDescriptiveOnly": True,
        "admissionDecisionMade": False,
        "modelValidationComplete": False,
    }, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence_a", nargs="?")
    parser.add_argument("activation_a", nargs="?")
    parser.add_argument("decision_a", nargs="?")
    parser.add_argument("evidence_b", nargs="?")
    parser.add_argument("activation_b", nargs="?")
    parser.add_argument("decision_b", nargs="?")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return
    paths = [args.evidence_a, args.activation_a, args.decision_a, args.evidence_b, args.activation_b, args.decision_b]
    if any(path is None for path in paths):
        raise DecisionComparisonError("SIX_INPUT_FILES_REQUIRED")
    values = [load_json(path) for path in paths]
    report = build_report(*values)
    text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    try:
        main()
    except DecisionComparisonError as exc:
        print(f"DECISION_SURFACE_COMPARISON_ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2)
