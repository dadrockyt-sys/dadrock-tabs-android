#!/usr/bin/env python3

"""Fail-closed aggregate contract for fresh Basic Pitch cross-run measurements.

This tool validates a complete set of independent observation/runtime artifacts
and their pairwise measurement reports. It is intentionally measurement-only:
it never defines a tolerance, selects a preferred output, completes model
validation, advances delivery, or changes duration authority.
"""

import argparse
import copy
import hashlib
import itertools
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

from compare_basic_pitch_cross_run_evidence import (
    ComparisonError,
    build_report,
    canonical_json,
    make_test_evidence,
    validate_evidence,
)

CONTRACT = "songsterr-fresh-basic-pitch-cross-run-variation-measurement-set-v1"
OBSERVATION_CONTRACT = "songsterr-fresh-model-evidence-cross-run-observation-v1"
PAIR_CONTRACT = "songsterr-fresh-basic-pitch-cross-run-variation-measurement-v1"

EXPECTED_AUDIO_SOURCE = (
    "public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a@main#"
    "4dd709e3fa177b4daeed71ca97f0199757729d4b"
)
EXPECTED_DECODED_INPUT_SHA256 = (
    "e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a"
)
EXPECTED_STRUCTURE_IDENTITY = {
    "contract": "songsterr-fresh-frozen-structure-identity-v1",
    "version": 1,
    "signature": "fnv1a32:2f493225",
    "canonicalLength": 19653,
}
EXPECTED_PACKAGES = {
    "numpy": "1.26.4",
    "torch": "2.14.0",
    "huggingface-hub": "1.30.0",
    "safetensors": "0.8.0",
    "sphn": "0.2.1",
    "demucs": "4.1.0",
    "basic-pitch": "0.4.0",
    "librosa": "0.11.0",
    "soundfile": "0.13.1",
    "tflite-runtime": "2.14.0",
}
EXPECTED_THREADING_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "PYTHONHASHSEED": "0",
}
EXPECTED_MODEL = {
    "family": "Spotify Basic Pitch",
    "package": "basic-pitch",
    "packageVersion": "0.4.0",
    "polyphonic": True,
    "instrumentAgnostic": True,
    "minimumMidi": 40,
    "maximumMidi": 88,
    "onsetThreshold": 0.5,
    "frameThreshold": 0.3,
    "minimumNoteLengthMs": 127.7,
}
FALSE_GUARDS = (
    "admissionDecisionMade",
    "modelValidationComplete",
    "mayAdvanceDelivery",
    "durationAuthorityChanged",
    "referenceTabUsed",
    "professionalScorerUsed",
    "legacyV143ScorerImported",
)
PAIR_FALSE_GUARDS = FALSE_GUARDS + ("thresholdsApplied",)
MAX_GROUPS = 64


class MeasurementSetError(RuntimeError):
    """Fail-closed aggregate validation error."""


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--observation",
        nargs=3,
        action="append",
        metavar=("LABEL", "RUNTIME_JSON", "EVIDENCE_JSON"),
        help="Repeat for each independent observation.",
    )
    parser.add_argument(
        "--comparison",
        nargs=3,
        action="append",
        metavar=("LABEL_A", "LABEL_B", "REPORT_JSON"),
        help="Repeat for each unordered observation pair.",
    )
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def reject_json_constant(value):
    raise MeasurementSetError(f"NONSTANDARD_JSON_CONSTANT:{value}")


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle, parse_constant=reject_json_constant)
    except MeasurementSetError:
        raise
    except Exception as exc:
        raise MeasurementSetError(f"JSON_LOAD_FAILED:{path}") from exc


def require_bool(value, expected, label):
    if value is not expected:
        raise MeasurementSetError(f"{label}:EXPECTED_{str(expected).upper()}")


def require_nonempty_string(value, label):
    if not isinstance(value, str) or not value.strip():
        raise MeasurementSetError(f"{label}:NONEMPTY_STRING_REQUIRED")
    return value


def valid_sha256(value):
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def require_sha256(value, label):
    if not valid_sha256(value):
        raise MeasurementSetError(f"{label}:SHA256_INVALID")
    return value


def finite_nonnegative(value, label):
    if isinstance(value, bool):
        raise MeasurementSetError(f"{label}:FINITE_NONNEGATIVE_REQUIRED")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise MeasurementSetError(f"{label}:FINITE_NONNEGATIVE_REQUIRED") from exc
    if not math.isfinite(number) or number < 0:
        raise MeasurementSetError(f"{label}:FINITE_NONNEGATIVE_REQUIRED")
    return number


def require_nonnegative_int(value, label):
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise MeasurementSetError(f"{label}:NONNEGATIVE_INTEGER_REQUIRED")
    return value


def pair_key(first, second):
    if first == second:
        raise MeasurementSetError(f"PAIR_LABELS_MUST_DIFFER:{first}")
    return tuple(sorted((first, second)))


def validate_runtime(label, runtime, validated_evidence):
    if not isinstance(runtime, dict):
        raise MeasurementSetError(f"runtime[{label}]:OBJECT_REQUIRED")
    if runtime.get("contract") != OBSERVATION_CONTRACT or runtime.get("version") != 1:
        raise MeasurementSetError(f"runtime[{label}]:CONTRACT_OR_VERSION_MISMATCH")
    if runtime.get("sample") != label:
        raise MeasurementSetError(f"runtime[{label}].sample:MISMATCH")
    require_bool(runtime.get("referenceBlind"), True, f"runtime[{label}].referenceBlind")
    require_bool(runtime.get("diagnosticOnly"), True, f"runtime[{label}].diagnosticOnly")

    guards = runtime.get("hardGuards")
    if not isinstance(guards, dict):
        raise MeasurementSetError(f"runtime[{label}].hardGuards:MISSING")
    for guard in FALSE_GUARDS:
        require_bool(guards.get(guard), False, f"runtime[{label}].hardGuards.{guard}")

    decoded_sha = require_sha256(
        runtime.get("decodedSeparationWavSha256"),
        f"runtime[{label}].decodedSeparationWavSha256",
    )
    if decoded_sha != EXPECTED_DECODED_INPUT_SHA256:
        raise MeasurementSetError(f"runtime[{label}]:DECODED_INPUT_IDENTITY_CHANGED")

    stem_sha = require_sha256(
        runtime.get("guitarStemSha256"), f"runtime[{label}].guitarStemSha256"
    )
    evidence_sha = require_sha256(
        runtime.get("canonicalEvidenceSha256"),
        f"runtime[{label}].canonicalEvidenceSha256",
    )
    if evidence_sha != validated_evidence["digestSha256"]:
        raise MeasurementSetError(f"runtime[{label}]:CANONICAL_EVIDENCE_SHA_MISMATCH")

    if runtime.get("structureIdentity") != EXPECTED_STRUCTURE_IDENTITY:
        raise MeasurementSetError(f"runtime[{label}]:STRUCTURE_IDENTITY_CHANGED")
    if validated_evidence["structureIdentity"] != EXPECTED_STRUCTURE_IDENTITY:
        raise MeasurementSetError(f"evidence[{label}]:STRUCTURE_IDENTITY_CHANGED")
    if validated_evidence["audioSource"] != EXPECTED_AUDIO_SOURCE:
        raise MeasurementSetError(f"evidence[{label}]:AUDIO_SOURCE_CHANGED")
    if validated_evidence["model"] != EXPECTED_MODEL:
        raise MeasurementSetError(f"evidence[{label}]:MODEL_SETTINGS_CHANGED")

    if runtime.get("noteInferenceIdentity") != validated_evidence["noteIdentity"]:
        raise MeasurementSetError(f"runtime[{label}]:NOTE_IDENTITY_MISMATCH")
    if runtime.get("activationEvidenceIdentity") != validated_evidence["activationIdentity"]:
        raise MeasurementSetError(f"runtime[{label}]:ACTIVATION_IDENTITY_MISMATCH")

    if runtime.get("packages") != EXPECTED_PACKAGES:
        raise MeasurementSetError(f"runtime[{label}]:PACKAGE_PIN_SET_CHANGED")
    if runtime.get("threadingEnvironment") != EXPECTED_THREADING_ENVIRONMENT:
        raise MeasurementSetError(f"runtime[{label}]:THREADING_ENVIRONMENT_CHANGED")

    for field in (
        "python",
        "platform",
        "machine",
        "runnerOS",
        "runnerArch",
        "imageOS",
        "imageVersion",
        "ffmpegVersion",
    ):
        require_nonempty_string(runtime.get(field), f"runtime[{label}].{field}")
    cpu_model = runtime.get("cpuModel")
    if cpu_model is not None:
        require_nonempty_string(cpu_model, f"runtime[{label}].cpuModel")

    activation = validated_evidence["activationIdentity"]
    return {
        "label": label,
        "eventCount": len(validated_evidence["onsets"]),
        "guitarStemSha256": stem_sha,
        "canonicalEvidenceSha256": evidence_sha,
        "noteInferenceSha256": validated_evidence["noteIdentity"]["sha256"],
        "activationBundleSha256": activation["sha256"] if activation else None,
        "activationMatrixSha256": activation["activationMatrixSha256"] if activation else None,
        "frameTimesSha256": activation["frameTimesSha256"] if activation else None,
        "runtimeProvenance": {
            "python": runtime["python"],
            "platform": runtime["platform"],
            "machine": runtime["machine"],
            "processor": runtime.get("processor"),
            "cpuModel": cpu_model,
            "runnerOS": runtime["runnerOS"],
            "runnerArch": runtime["runnerArch"],
            "imageOS": runtime["imageOS"],
            "imageVersion": runtime["imageVersion"],
            "ffmpegVersion": runtime["ffmpegVersion"],
        },
    }


def normalize_report_input(item):
    if not isinstance(item, dict):
        raise MeasurementSetError("comparison.inputs:OBJECT_REQUIRED")
    note = item.get("noteInferenceIdentity")
    activation = item.get("activationEvidenceIdentity")
    if not isinstance(note, dict):
        raise MeasurementSetError("comparison.inputs.noteInferenceIdentity:MISSING")
    if activation is not None and not isinstance(activation, dict):
        raise MeasurementSetError("comparison.inputs.activationEvidenceIdentity:INVALID")
    return {
        "canonicalEvidenceSha256": require_sha256(
            item.get("canonicalEvidenceSha256"),
            "comparison.inputs.canonicalEvidenceSha256",
        ),
        "eventCount": require_nonnegative_int(item.get("eventCount"), "comparison.inputs.eventCount"),
        "noteInferenceIdentity": copy.deepcopy(note),
        "activationEvidenceIdentity": copy.deepcopy(activation),
        "separationSource": require_nonempty_string(
            item.get("separationSource"), "comparison.inputs.separationSource"
        ),
    }


def validate_pair_policy(report, pair):
    if not isinstance(report, dict):
        raise MeasurementSetError(f"comparison[{pair}]:OBJECT_REQUIRED")
    if report.get("contract") != PAIR_CONTRACT or report.get("version") != 1:
        raise MeasurementSetError(f"comparison[{pair}]:CONTRACT_OR_VERSION_MISMATCH")
    require_bool(report.get("referenceBlind"), True, f"comparison[{pair}].referenceBlind")
    require_bool(report.get("measurementOnly"), True, f"comparison[{pair}].measurementOnly")
    if report.get("semanticComparisonKey") != ["nearestStructureSlot", "selectedMidi"]:
        raise MeasurementSetError(f"comparison[{pair}]:SEMANTIC_KEY_CHANGED")
    boundary = report.get("policyBoundary")
    if not isinstance(boundary, dict):
        raise MeasurementSetError(f"comparison[{pair}].policyBoundary:MISSING")
    if boundary.get("status") != "MEASURED_REFERENCE_BLIND_VARIATION":
        raise MeasurementSetError(f"comparison[{pair}]:POLICY_STATUS_CHANGED")
    for guard in PAIR_FALSE_GUARDS:
        require_bool(boundary.get(guard), False, f"comparison[{pair}].policyBoundary.{guard}")
    comparability = report.get("comparability")
    if not isinstance(comparability, dict):
        raise MeasurementSetError(f"comparison[{pair}].comparability:MISSING")
    require_bool(
        comparability.get("exactHashesAreAdmissionCriteria"),
        False,
        f"comparison[{pair}].comparability.exactHashesAreAdmissionCriteria",
    )


def validate_pair_measurement_shape(report, pair):
    measurement = report.get("measurement")
    if not isinstance(measurement, dict):
        raise MeasurementSetError(f"comparison[{pair}].measurement:MISSING")
    inventory = measurement.get("inventory")
    if not isinstance(inventory, dict):
        raise MeasurementSetError(f"comparison[{pair}].inventory:MISSING")
    for field in (
        "eventCountFirst",
        "eventCountSecond",
        "absoluteEventCountDifference",
        "semanticKeyCountFirst",
        "semanticKeyCountSecond",
        "commonSemanticKeyCount",
        "matchedEventCount",
        "unmatchedEventCountFirst",
        "unmatchedEventCountSecond",
        "totalUnmatchedEventCount",
        "semanticKeysWithCountMismatch",
    ):
        require_nonnegative_int(inventory.get(field), f"comparison[{pair}].inventory.{field}")
    if inventory["totalUnmatchedEventCount"] != (
        inventory["unmatchedEventCountFirst"] + inventory["unmatchedEventCountSecond"]
    ):
        raise MeasurementSetError(f"comparison[{pair}]:UNMATCHED_COUNT_INCONSISTENT")

    paired = measurement.get("pairedNumericalVariation")
    if not isinstance(paired, dict):
        raise MeasurementSetError(f"comparison[{pair}].pairedNumericalVariation:MISSING")
    for field in ("sourceStartSeconds", "onsetConfidence", "diagnosticModelEndSeconds"):
        stats = paired.get(field)
        if not isinstance(stats, dict):
            raise MeasurementSetError(f"comparison[{pair}].{field}:MISSING")
        count = require_nonnegative_int(stats.get("count"), f"comparison[{pair}].{field}.count")
        if count != inventory["matchedEventCount"]:
            raise MeasurementSetError(f"comparison[{pair}].{field}:COUNT_MISMATCH")
        for stat in ("meanAbsolute", "rmsAbsolute", "maxAbsolute"):
            value = stats.get(stat)
            if count == 0:
                if value is not None:
                    raise MeasurementSetError(f"comparison[{pair}].{field}.{stat}:MUST_BE_NULL")
            else:
                finite_nonnegative(value, f"comparison[{pair}].{field}.{stat}")
    diagnostic = paired["diagnosticModelEndSeconds"]
    require_bool(
        diagnostic.get("diagnosticOnly"),
        True,
        f"comparison[{pair}].diagnosticModelEndSeconds.diagnosticOnly",
    )
    require_bool(
        diagnostic.get("usedAsDurationEvidence"),
        False,
        f"comparison[{pair}].diagnosticModelEndSeconds.usedAsDurationEvidence",
    )


def exact_groups(observation_summaries, field):
    groups = defaultdict(list)
    for summary in observation_summaries:
        value = summary.get(field)
        if value is not None:
            groups[value].append(summary["label"])
    if len(groups) > MAX_GROUPS:
        raise MeasurementSetError(f"TOO_MANY_EXACT_OUTCOME_GROUPS:{field}")
    return [
        {"sha256": sha, "observations": sorted(labels), "count": len(labels)}
        for sha, labels in sorted(groups.items())
    ]


def max_stat(pairwise, path):
    values = []
    for item in pairwise:
        value = item
        for key in path:
            value = value[key]
        if value is not None:
            values.append(finite_nonnegative(value, ".".join(path)))
    return max(values) if values else None


def build_measurement_set(observations, comparisons):
    if not isinstance(observations, dict) or len(observations) < 2:
        raise MeasurementSetError("AT_LEAST_TWO_OBSERVATIONS_REQUIRED")
    labels = sorted(observations)
    if any(not isinstance(label, str) or not label.strip() for label in labels):
        raise MeasurementSetError("OBSERVATION_LABEL_INVALID")

    validated_by_label = {}
    summaries = []
    evidences = {}
    for label in labels:
        item = observations[label]
        if not isinstance(item, dict) or "runtime" not in item or "evidence" not in item:
            raise MeasurementSetError(f"observation[{label}]:RUNTIME_AND_EVIDENCE_REQUIRED")
        evidence = item["evidence"]
        try:
            validated = validate_evidence(evidence, f"evidence[{label}]")
        except ComparisonError as exc:
            raise MeasurementSetError(f"observation[{label}]:EVIDENCE_INVALID:{exc}") from exc
        validated_by_label[label] = validated
        evidences[label] = evidence
        summaries.append(validate_runtime(label, item["runtime"], validated))

    expected_pairs = {pair_key(a, b) for a, b in itertools.combinations(labels, 2)}
    if set(comparisons) != expected_pairs:
        missing = sorted(expected_pairs - set(comparisons))
        extra = sorted(set(comparisons) - expected_pairs)
        raise MeasurementSetError(
            f"PAIR_SET_INCOMPLETE_OR_EXTRA:missing={missing}:extra={extra}"
        )

    pairwise = []
    for first, second in sorted(expected_pairs):
        pair = f"{first}{second}"
        report = comparisons[(first, second)]
        validate_pair_policy(report, pair)
        validate_pair_measurement_shape(report, pair)

        try:
            recomputed = build_report(evidences[first], evidences[second])
        except ComparisonError as exc:
            raise MeasurementSetError(f"comparison[{pair}]:RECOMPUTE_FAILED:{exc}") from exc
        if canonical_json(report) != canonical_json(recomputed):
            raise MeasurementSetError(f"comparison[{pair}]:REPORT_DOES_NOT_MATCH_RECOMPUTATION")

        actual_inputs = report.get("inputs")
        if not isinstance(actual_inputs, list) or len(actual_inputs) != 2:
            raise MeasurementSetError(f"comparison[{pair}].inputs:EXACTLY_TWO_REQUIRED")
        normalized_inputs = [normalize_report_input(item) for item in actual_inputs]
        expected_input_digests = sorted(
            [
                validated_by_label[first]["digestSha256"],
                validated_by_label[second]["digestSha256"],
            ]
        )
        if sorted(item["canonicalEvidenceSha256"] for item in normalized_inputs) != expected_input_digests:
            raise MeasurementSetError(f"comparison[{pair}]:INPUT_DIGEST_SET_MISMATCH")

        pairwise.append({
            "pair": [first, second],
            "inputs": normalized_inputs,
            "comparability": copy.deepcopy(report["comparability"]),
            "inventory": copy.deepcopy(report["measurement"]["inventory"]),
            "pairedNumericalVariation": copy.deepcopy(
                report["measurement"]["pairedNumericalVariation"]
            ),
        })

    frame_time_hashes = sorted(
        {summary["frameTimesSha256"] for summary in summaries if summary["frameTimesSha256"]}
    )

    aggregate = {
        "contract": CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "measurementOnly": True,
        "observationCount": len(labels),
        "pairwiseComparisonCount": len(pairwise),
        "completePairSetVerified": True,
        "fixedContract": {
            "audioSource": EXPECTED_AUDIO_SOURCE,
            "decodedSeparationWavSha256": EXPECTED_DECODED_INPUT_SHA256,
            "structureIdentity": copy.deepcopy(EXPECTED_STRUCTURE_IDENTITY),
            "model": copy.deepcopy(EXPECTED_MODEL),
            "packages": copy.deepcopy(EXPECTED_PACKAGES),
            "threadingEnvironment": copy.deepcopy(EXPECTED_THREADING_ENVIRONMENT),
        },
        "observations": summaries,
        "exactOutcomeGroups": {
            "guitarStemSha256": exact_groups(summaries, "guitarStemSha256"),
            "canonicalEvidenceSha256": exact_groups(summaries, "canonicalEvidenceSha256"),
            "noteInferenceSha256": exact_groups(summaries, "noteInferenceSha256"),
            "activationBundleSha256": exact_groups(summaries, "activationBundleSha256"),
            "activationMatrixSha256": exact_groups(summaries, "activationMatrixSha256"),
            "frameTimesSha256": exact_groups(summaries, "frameTimesSha256"),
        },
        "descriptiveVariationEnvelope": {
            "maxAbsoluteEventCountDifference": max(
                item["inventory"]["absoluteEventCountDifference"] for item in pairwise
            ),
            "maxTotalUnmatchedEventCount": max(
                item["inventory"]["totalUnmatchedEventCount"] for item in pairwise
            ),
            "maxSemanticKeysWithCountMismatch": max(
                item["inventory"]["semanticKeysWithCountMismatch"] for item in pairwise
            ),
            "maxAbsoluteSourceStartSeconds": max_stat(
                pairwise, ("pairedNumericalVariation", "sourceStartSeconds", "maxAbsolute")
            ),
            "maxAbsoluteOnsetConfidence": max_stat(
                pairwise, ("pairedNumericalVariation", "onsetConfidence", "maxAbsolute")
            ),
            "maxAbsoluteDiagnosticModelEndSeconds": max_stat(
                pairwise,
                ("pairedNumericalVariation", "diagnosticModelEndSeconds", "maxAbsolute"),
            ),
            "frameTimesHashGroupCount": len(frame_time_hashes),
            "descriptiveOnly": True,
            "mayDefineTolerance": False,
        },
        "pairwiseMeasurements": pairwise,
        "policyBoundary": {
            "status": "MEASURED_INDEPENDENT_RUN_VARIATION",
            "thresholdsApplied": False,
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "referenceTabUsed": False,
            "professionalScorerUsed": False,
            "legacyV143ScorerImported": False,
            "preferredOutputSelected": False,
            "exactHashesAreAdmissionCriteria": False,
            "runtimeProvenanceIsAdmissionCriterion": False,
            "observedMaximaAreAdmissionCriteria": False,
        },
    }
    canonical_json(aggregate)
    return aggregate


def make_runtime(label, evidence, *, stem_seed="stem-a", cpu="test-cpu"):
    validated = validate_evidence(evidence, f"selftest[{label}]")
    return {
        "contract": OBSERVATION_CONTRACT,
        "version": 1,
        "sample": label,
        "referenceBlind": True,
        "diagnosticOnly": True,
        "python": "3.10.21",
        "platform": "Linux-test",
        "machine": "x86_64",
        "processor": "x86_64",
        "cpuModel": cpu,
        "runnerOS": "Linux",
        "runnerArch": "X64",
        "imageOS": "ubuntu24",
        "imageVersion": "test-image",
        "ffmpegVersion": "ffmpeg test",
        "packages": copy.deepcopy(EXPECTED_PACKAGES),
        "threadingEnvironment": copy.deepcopy(EXPECTED_THREADING_ENVIRONMENT),
        "decodedSeparationWavSha256": EXPECTED_DECODED_INPUT_SHA256,
        "guitarStemSha256": hashlib.sha256(stem_seed.encode("utf-8")).hexdigest(),
        "canonicalEvidenceSha256": validated["digestSha256"],
        "noteInferenceIdentity": copy.deepcopy(validated["noteIdentity"]),
        "activationEvidenceIdentity": copy.deepcopy(validated["activationIdentity"]),
        "structureIdentity": copy.deepcopy(EXPECTED_STRUCTURE_IDENTITY),
        "hardGuards": {guard: False for guard in FALSE_GUARDS},
    }


def productionize_test_evidence(evidence):
    evidence = copy.deepcopy(evidence)
    evidence["structureIdentity"] = copy.deepcopy(EXPECTED_STRUCTURE_IDENTITY)
    evidence["provenance"]["audioSource"] = EXPECTED_AUDIO_SOURCE
    return evidence


def assert_raises(fragment, fn):
    try:
        fn()
    except MeasurementSetError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"Expected {fragment!r} in {str(exc)!r}") from exc
        return
    raise AssertionError(f"Expected MeasurementSetError containing {fragment!r}")


def run_self_test():
    base = productionize_test_evidence(make_test_evidence())
    same = copy.deepcopy(base)
    variant = productionize_test_evidence(
        make_test_evidence([
            (1.000, 1.000, 40, 0.80, 1.40),
            (1.250, 1.250, 52, 0.70, 1.60),
            (2.010, 2.000, 47, 0.89, 2.45),
            (3.000, 3.000, 64, 0.55, 3.30),
        ])
    )
    observations = {
        "a": {"runtime": make_runtime("a", base, stem_seed="stem-1", cpu="cpu-x"), "evidence": base},
        "b": {"runtime": make_runtime("b", same, stem_seed="stem-1", cpu="cpu-x"), "evidence": same},
        "c": {"runtime": make_runtime("c", variant, stem_seed="stem-2", cpu="cpu-y"), "evidence": variant},
    }
    comparisons = {
        ("a", "b"): build_report(base, same),
        ("a", "c"): build_report(base, variant),
        ("b", "c"): build_report(same, variant),
    }
    report = build_measurement_set(observations, comparisons)
    assert report["observationCount"] == 3
    assert report["pairwiseComparisonCount"] == 3
    assert report["completePairSetVerified"] is True
    assert len(report["exactOutcomeGroups"]["guitarStemSha256"]) == 2
    assert report["descriptiveVariationEnvelope"]["maxAbsoluteEventCountDifference"] == 1
    assert report["descriptiveVariationEnvelope"]["mayDefineTolerance"] is False
    assert report["policyBoundary"]["admissionDecisionMade"] is False
    assert report["policyBoundary"]["modelValidationComplete"] is False
    assert report["policyBoundary"]["preferredOutputSelected"] is False

    reversed_observations = dict(reversed(list(observations.items())))
    reversed_comparisons = dict(reversed(list(comparisons.items())))
    assert canonical_json(report) == canonical_json(
        build_measurement_set(reversed_observations, reversed_comparisons)
    )

    unsafe = copy.deepcopy(observations)
    unsafe["a"]["runtime"]["hardGuards"]["admissionDecisionMade"] = True
    assert_raises("admissionDecisionMade", lambda: build_measurement_set(unsafe, comparisons))

    bad_digest = copy.deepcopy(observations)
    bad_digest["a"]["runtime"]["canonicalEvidenceSha256"] = "0" * 64
    assert_raises("CANONICAL_EVIDENCE_SHA_MISMATCH", lambda: build_measurement_set(bad_digest, comparisons))

    missing_pair = dict(comparisons)
    missing_pair.pop(("a", "c"))
    assert_raises("PAIR_SET_INCOMPLETE_OR_EXTRA", lambda: build_measurement_set(observations, missing_pair))

    unsafe_pair = copy.deepcopy(comparisons)
    unsafe_pair[("a", "c")]["policyBoundary"]["thresholdsApplied"] = True
    assert_raises("thresholdsApplied", lambda: build_measurement_set(observations, unsafe_pair))

    altered_pair = copy.deepcopy(comparisons)
    altered_pair[("a", "c")]["measurement"]["inventory"]["absoluteEventCountDifference"] = 0
    assert_raises(
        "REPORT_DOES_NOT_MATCH_RECOMPUTATION",
        lambda: build_measurement_set(observations, altered_pair),
    )

    bad_packages = copy.deepcopy(observations)
    bad_packages["b"]["runtime"]["packages"]["basic-pitch"] = "9.9.9"
    assert_raises("PACKAGE_PIN_SET_CHANGED", lambda: build_measurement_set(bad_packages, comparisons))

    print(json.dumps({
        "ok": True,
        "contract": CONTRACT,
        "tests": [
            "complete-pair-set",
            "argument-order-invariant",
            "exact-outcome-grouping",
            "unsafe-runtime-guard-fails-closed",
            "runtime-evidence-digest-binding",
            "missing-pair-fails-closed",
            "thresholded-pair-fails-closed",
            "pair-report-recomputation",
            "package-pin-drift-fails-closed",
            "no-preferred-output-or-admission",
        ],
    }, sort_keys=True))


def parse_cli_observations(rows):
    observations = {}
    for row in rows or []:
        label, runtime_path, evidence_path = row
        if label in observations:
            raise MeasurementSetError(f"DUPLICATE_OBSERVATION_LABEL:{label}")
        observations[label] = {
            "runtime": load_json(runtime_path),
            "evidence": load_json(evidence_path),
        }
    return observations


def parse_cli_comparisons(rows):
    comparisons = {}
    for row in rows or []:
        first, second, report_path = row
        key = pair_key(first, second)
        if key in comparisons:
            raise MeasurementSetError(f"DUPLICATE_COMPARISON_PAIR:{key}")
        comparisons[key] = load_json(report_path)
    return comparisons


def main():
    args = parse_args()
    try:
        if args.self_test:
            run_self_test()
            return
        if not args.observation or not args.comparison or not args.output:
            raise MeasurementSetError(
                "OBSERVATIONS_COMPARISONS_AND_OUTPUT_REQUIRED_UNLESS_SELF_TEST"
            )
        observations = parse_cli_observations(args.observation)
        comparisons = parse_cli_comparisons(args.comparison)
        report = build_measurement_set(observations, comparisons)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
        print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    except (MeasurementSetError, ComparisonError) as exc:
        print(f"ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
