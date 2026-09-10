#!/usr/bin/env python3

"""Reference-blind cross-run measurement for fresh Basic Pitch note evidence.

This tool deliberately does not make an admission decision. It validates that two
adapted fresh model-evidence artifacts are comparable, then measures semantic
inventory and numerical variation using the already-frozen structure map.
"""

import argparse
import copy
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

CONTRACT = "songsterr-fresh-basic-pitch-cross-run-variation-measurement-v1"
EXPECTED_EVIDENCE_CONTRACT = "songsterr-fresh-isolated-polyphonic-note-evidence-v1"
EXPECTED_NOTE_IDENTITY_CONTRACT = "songsterr-fresh-basic-pitch-note-identity-v1"
EXPECTED_ACTIVATION_BUNDLE_CONTRACT = "songsterr-fresh-basic-pitch-inference-bundle-v1"
PLAYABLE_MIDI_MIN = 40
PLAYABLE_MIDI_MAX = 88
MAX_KEY_SAMPLES = 25


class ComparisonError(RuntimeError):
    """Fail-closed validation/comparability error."""


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence_a", nargs="?")
    parser.add_argument("evidence_b", nargs="?")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def reject_json_constant(value):
    raise ComparisonError(f"NONSTANDARD_JSON_CONSTANT:{value}")


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle, parse_constant=reject_json_constant)
    except ComparisonError:
        raise
    except Exception as exc:
        raise ComparisonError(f"JSON_LOAD_FAILED:{path}") from exc


def canonical_json(value):
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ComparisonError("CANONICAL_JSON_FAILED") from exc


def sha256_json(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def finite_number(value, label):
    if isinstance(value, bool):
        raise ComparisonError(f"{label}:MUST_BE_FINITE_NUMBER")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ComparisonError(f"{label}:MUST_BE_FINITE_NUMBER") from exc
    if not math.isfinite(number):
        raise ComparisonError(f"{label}:MUST_BE_FINITE_NUMBER")
    return number


def bounded_confidence(value, label):
    number = finite_number(value, label)
    if number < 0.0 or number > 1.0:
        raise ComparisonError(f"{label}:OUTSIDE_0_1")
    return number


def require_bool(value, expected, label):
    if value is not expected:
        raise ComparisonError(f"{label}:EXPECTED_{str(expected).upper()}")


def require_nonempty_string(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ComparisonError(f"{label}:NONEMPTY_STRING_REQUIRED")
    return value


def valid_sha256(value):
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def validate_note_identity(identity, event_count, label):
    if not isinstance(identity, dict):
        raise ComparisonError(f"{label}:MISSING")
    if identity.get("contract") != EXPECTED_NOTE_IDENTITY_CONTRACT:
        raise ComparisonError(f"{label}:CONTRACT_MISMATCH")
    if identity.get("version") != 1 or identity.get("algorithm") != "sha256":
        raise ComparisonError(f"{label}:VERSION_OR_ALGORITHM_MISMATCH")
    if identity.get("eventCount") != event_count:
        raise ComparisonError(f"{label}:EVENT_COUNT_MISMATCH")
    if not valid_sha256(identity.get("sha256")):
        raise ComparisonError(f"{label}:SHA256_INVALID")
    return identity


def validate_activation_identity(identity, note_identity, label):
    if identity is None:
        return None
    if not isinstance(identity, dict):
        raise ComparisonError(f"{label}:INVALID")
    if identity.get("contract") != EXPECTED_ACTIVATION_BUNDLE_CONTRACT:
        raise ComparisonError(f"{label}:CONTRACT_MISMATCH")
    if identity.get("version") != 1 or identity.get("algorithm") != "sha256":
        raise ComparisonError(f"{label}:VERSION_OR_ALGORITHM_MISMATCH")
    if identity.get("noteIdentitySha256") != note_identity.get("sha256"):
        raise ComparisonError(f"{label}:NOTE_IDENTITY_MISMATCH")
    for field in ("activationMatrixSha256", "frameTimesSha256", "sha256"):
        if not valid_sha256(identity.get(field)):
            raise ComparisonError(f"{label}:{field}:INVALID")
    return identity


def validate_model_metadata(model, label):
    if not isinstance(model, dict):
        raise ComparisonError(f"{label}:MISSING")
    if model.get("family") != "Spotify Basic Pitch" or model.get("package") != "basic-pitch":
        raise ComparisonError(f"{label}:FAMILY_OR_PACKAGE_MISMATCH")
    require_nonempty_string(model.get("packageVersion"), f"{label}.packageVersion")
    require_bool(model.get("polyphonic"), True, f"{label}.polyphonic")
    require_bool(model.get("instrumentAgnostic"), True, f"{label}.instrumentAgnostic")
    minimum_midi = model.get("minimumMidi")
    maximum_midi = model.get("maximumMidi")
    if not isinstance(minimum_midi, int) or isinstance(minimum_midi, bool):
        raise ComparisonError(f"{label}.minimumMidi:INTEGER_REQUIRED")
    if not isinstance(maximum_midi, int) or isinstance(maximum_midi, bool):
        raise ComparisonError(f"{label}.maximumMidi:INTEGER_REQUIRED")
    if minimum_midi != PLAYABLE_MIDI_MIN or maximum_midi != PLAYABLE_MIDI_MAX:
        raise ComparisonError(f"{label}:MIDI_RANGE_MISMATCH")
    for field in ("onsetThreshold", "frameThreshold"):
        value = bounded_confidence(model.get(field), f"{label}.{field}")
        if value < 0.0 or value > 1.0:
            raise ComparisonError(f"{label}.{field}:INVALID")
    if finite_number(model.get("minimumNoteLengthMs"), f"{label}.minimumNoteLengthMs") <= 0:
        raise ComparisonError(f"{label}.minimumNoteLengthMs:MUST_BE_POSITIVE")
    return copy.deepcopy(model)


def validate_safe_provenance(evidence, label):
    provenance = evidence.get("provenance")
    if not isinstance(provenance, dict):
        raise ComparisonError(f"{label}.provenance:MISSING")
    require_bool(provenance.get("referenceBlind"), True, f"{label}.provenance.referenceBlind")
    require_bool(provenance.get("structureConditioned"), True, f"{label}.provenance.structureConditioned")
    require_bool(provenance.get("structureFrozen"), True, f"{label}.provenance.structureFrozen")
    require_bool(provenance.get("sourceSeparationModelInvoked"), True, f"{label}.provenance.sourceSeparationModelInvoked")
    require_bool(provenance.get("modelInvoked"), True, f"{label}.provenance.modelInvoked")
    require_bool(provenance.get("legacyV143ScorerImported"), False, f"{label}.provenance.legacyV143ScorerImported")
    require_bool(provenance.get("professionalScorerUsed"), False, f"{label}.provenance.professionalScorerUsed")
    require_bool(provenance.get("referenceTabUsed"), False, f"{label}.provenance.referenceTabUsed")
    require_bool(provenance.get("modelNoteEndsUsedAsDuration"), False, f"{label}.provenance.modelNoteEndsUsedAsDuration")
    require_bool(
        provenance.get("activationEvidenceActiveDurationAuthority"),
        False,
        f"{label}.provenance.activationEvidenceActiveDurationAuthority",
    )
    audio_source = require_nonempty_string(provenance.get("audioSource"), f"{label}.provenance.audioSource")
    separation_source = require_nonempty_string(
        provenance.get("sourceSeparationSource"),
        f"{label}.provenance.sourceSeparationSource",
    )
    return audio_source, separation_source


def validate_evidence(evidence, label):
    if not isinstance(evidence, dict):
        raise ComparisonError(f"{label}:OBJECT_REQUIRED")
    if evidence.get("contract") != EXPECTED_EVIDENCE_CONTRACT or evidence.get("version") != 1:
        raise ComparisonError(f"{label}:CONTRACT_OR_VERSION_MISMATCH")
    require_bool(evidence.get("referenceBlind"), True, f"{label}.referenceBlind")
    require_bool(evidence.get("structureFrozen"), True, f"{label}.structureFrozen")
    if evidence.get("role") != "guitar":
        raise ComparisonError(f"{label}.role:GUITAR_REQUIRED")

    structure_identity = evidence.get("structureIdentity")
    if not isinstance(structure_identity, dict) or not structure_identity:
        raise ComparisonError(f"{label}.structureIdentity:MISSING")
    canonical_json(structure_identity)

    capabilities = evidence.get("capabilities")
    if not isinstance(capabilities, dict):
        raise ComparisonError(f"{label}.capabilities:MISSING")
    require_bool(capabilities.get("roleRelevanceResolved"), True, f"{label}.capabilities.roleRelevanceResolved")
    require_bool(capabilities.get("polyphonyResolved"), True, f"{label}.capabilities.polyphonyResolved")
    if capabilities.get("durationResolution") != "none":
        raise ComparisonError(f"{label}.capabilities.durationResolution:MUST_BE_NONE")

    audio_source, separation_source = validate_safe_provenance(evidence, label)

    diagnostics = evidence.get("diagnostics")
    if not isinstance(diagnostics, dict):
        raise ComparisonError(f"{label}.diagnostics:MISSING")
    require_bool(diagnostics.get("modelNoteEndsAreDiagnosticOnly"), True, f"{label}.diagnostics.modelNoteEndsAreDiagnosticOnly")
    require_bool(diagnostics.get("modelNoteEndsUsedAsDuration"), False, f"{label}.diagnostics.modelNoteEndsUsedAsDuration")
    duration_evidence = diagnostics.get("durationEvidence")
    if not isinstance(duration_evidence, dict) or duration_evidence.get("authority") != "none-in-model-pitch-stage":
        raise ComparisonError(f"{label}.diagnostics.durationEvidence:AUTHORITY_CHANGED")
    if duration_evidence.get("resolvedCount") != 0:
        raise ComparisonError(f"{label}.diagnostics.durationEvidence:RESOLVED_COUNT_NONZERO")
    require_bool(duration_evidence.get("nextOnsetUsedAsDuration"), False, f"{label}.diagnostics.durationEvidence.nextOnsetUsedAsDuration")
    require_bool(duration_evidence.get("syntheticDurationInference"), False, f"{label}.diagnostics.durationEvidence.syntheticDurationInference")

    model = validate_model_metadata(diagnostics.get("polyphonicInference"), f"{label}.diagnostics.polyphonicInference")

    onsets = evidence.get("onsets")
    if not isinstance(onsets, list) or not onsets:
        raise ComparisonError(f"{label}.onsets:NONEMPTY_LIST_REQUIRED")

    validated_onsets = []
    for index, onset in enumerate(onsets):
        event_label = f"{label}.onsets[{index}]"
        if not isinstance(onset, dict):
            raise ComparisonError(f"{event_label}:OBJECT_REQUIRED")
        if onset.get("classification") != "unambiguous":
            raise ComparisonError(f"{event_label}.classification:UNAMBIGUOUS_REQUIRED")
        midi = onset.get("selectedMidi")
        if not isinstance(midi, int) or isinstance(midi, bool) or midi < PLAYABLE_MIDI_MIN or midi > PLAYABLE_MIDI_MAX:
            raise ComparisonError(f"{event_label}.selectedMidi:UNSUPPORTED")
        source_start = finite_number(onset.get("sourceStart"), f"{event_label}.sourceStart")
        if source_start < 0:
            raise ComparisonError(f"{event_label}.sourceStart:NEGATIVE")
        nearest_slot = finite_number(onset.get("nearestStructureSlot"), f"{event_label}.nearestStructureSlot")
        if nearest_slot < 0:
            raise ComparisonError(f"{event_label}.nearestStructureSlot:NEGATIVE")
        confidence = bounded_confidence(onset.get("onsetConfidence"), f"{event_label}.onsetConfidence")
        for duration_field in ("sourceEnd", "durationSeconds", "durationConfidence"):
            if onset.get(duration_field) is not None:
                raise ComparisonError(f"{event_label}.{duration_field}:MUST_BE_NULL")

        candidates = onset.get("candidates")
        if not isinstance(candidates, list) or len(candidates) != 1:
            raise ComparisonError(f"{event_label}.candidates:EXACTLY_ONE_REQUIRED")
        candidate = candidates[0]
        if not isinstance(candidate, dict) or candidate.get("midi") != midi:
            raise ComparisonError(f"{event_label}.candidates:MIDI_MISMATCH")
        candidate_confidence = bounded_confidence(candidate.get("confidence"), f"{event_label}.candidates[0].confidence")
        if candidate_confidence != confidence:
            raise ComparisonError(f"{event_label}.candidates:CONFIDENCE_MISMATCH")

        event_provenance = onset.get("provenance")
        if not isinstance(event_provenance, dict):
            raise ComparisonError(f"{event_label}.provenance:MISSING")
        require_bool(event_provenance.get("modelEndUsedAsDuration"), False, f"{event_label}.provenance.modelEndUsedAsDuration")
        diagnostic_end = finite_number(
            event_provenance.get("modelDiagnosticEndSeconds"),
            f"{event_label}.provenance.modelDiagnosticEndSeconds",
        )
        if diagnostic_end <= source_start:
            raise ComparisonError(f"{event_label}.provenance.modelDiagnosticEndSeconds:NOT_AFTER_START")

        validated_onsets.append({
            "sourceStart": source_start,
            "nearestStructureSlot": nearest_slot,
            "selectedMidi": midi,
            "onsetConfidence": confidence,
            "diagnosticModelEndSeconds": diagnostic_end,
            "onsetId": str(onset.get("onsetId", "")),
        })

    note_identity = validate_note_identity(
        diagnostics.get("noteInferenceIdentity"),
        len(validated_onsets),
        f"{label}.diagnostics.noteInferenceIdentity",
    )
    provenance_note_identity = evidence.get("provenance", {}).get("noteInferenceIdentity")
    if provenance_note_identity != note_identity:
        raise ComparisonError(f"{label}.provenance.noteInferenceIdentity:MISMATCH")

    activation_identity = validate_activation_identity(
        diagnostics.get("activationEvidenceIdentity"),
        note_identity,
        f"{label}.diagnostics.activationEvidenceIdentity",
    )
    if evidence.get("provenance", {}).get("activationEvidenceIdentity") != activation_identity:
        raise ComparisonError(f"{label}.provenance.activationEvidenceIdentity:MISMATCH")

    declared_count = diagnostics.get("onsetCount")
    if declared_count != len(validated_onsets):
        raise ComparisonError(f"{label}.diagnostics.onsetCount:MISMATCH")

    # Ensures no hidden non-finite/non-JSON values elsewhere can enter a canonical digest.
    digest = sha256_json(evidence)
    return {
        "digestSha256": digest,
        "structureIdentity": copy.deepcopy(structure_identity),
        "audioSource": audio_source,
        "separationSource": separation_source,
        "model": model,
        "noteIdentity": copy.deepcopy(note_identity),
        "activationIdentity": copy.deepcopy(activation_identity),
        "onsets": validated_onsets,
    }


def semantic_key(onset):
    return (onset["nearestStructureSlot"], onset["selectedMidi"])


def sorted_group(onsets):
    return sorted(
        onsets,
        key=lambda event: (
            event["sourceStart"],
            event["onsetConfidence"],
            event["diagnosticModelEndSeconds"],
            event["onsetId"],
        ),
    )


def summarize_deltas(values):
    if not values:
        return {"count": 0, "meanAbsolute": None, "rmsAbsolute": None, "maxAbsolute": None}
    absolute = [abs(float(value)) for value in values]
    return {
        "count": len(absolute),
        "meanAbsolute": sum(absolute) / len(absolute),
        "rmsAbsolute": math.sqrt(sum(value * value for value in absolute) / len(absolute)),
        "maxAbsolute": max(absolute),
    }


def key_payload(key, count_a=None, count_b=None):
    payload = {
        "nearestStructureSlot": key[0],
        "selectedMidi": key[1],
    }
    if count_a is not None:
        payload["countFirst"] = count_a
    if count_b is not None:
        payload["countSecond"] = count_b
    return payload


def compare_validated(first, second):
    if first["structureIdentity"] != second["structureIdentity"]:
        raise ComparisonError("NOT_COMPARABLE:STRUCTURE_IDENTITY_MISMATCH")
    if first["audioSource"] != second["audioSource"]:
        raise ComparisonError("NOT_COMPARABLE:AUDIO_SOURCE_MISMATCH")
    if first["model"] != second["model"]:
        raise ComparisonError("NOT_COMPARABLE:MODEL_SETTINGS_MISMATCH")

    groups_first = defaultdict(list)
    groups_second = defaultdict(list)
    for onset in first["onsets"]:
        groups_first[semantic_key(onset)].append(onset)
    for onset in second["onsets"]:
        groups_second[semantic_key(onset)].append(onset)

    all_keys = sorted(set(groups_first) | set(groups_second), key=lambda key: (key[0], key[1]))
    common_keys = sorted(set(groups_first) & set(groups_second), key=lambda key: (key[0], key[1]))
    onset_deltas = []
    confidence_deltas = []
    diagnostic_end_deltas = []
    matched_count = 0
    unmatched_first = 0
    unmatched_second = 0
    mismatched_key_counts = []

    for key in all_keys:
        first_events = sorted_group(groups_first.get(key, []))
        second_events = sorted_group(groups_second.get(key, []))
        pair_count = min(len(first_events), len(second_events))
        matched_count += pair_count
        unmatched_first += len(first_events) - pair_count
        unmatched_second += len(second_events) - pair_count
        if len(first_events) != len(second_events):
            mismatched_key_counts.append(key_payload(key, len(first_events), len(second_events)))
        for index in range(pair_count):
            event_first = first_events[index]
            event_second = second_events[index]
            onset_deltas.append(event_second["sourceStart"] - event_first["sourceStart"])
            confidence_deltas.append(event_second["onsetConfidence"] - event_first["onsetConfidence"])
            diagnostic_end_deltas.append(
                event_second["diagnosticModelEndSeconds"] - event_first["diagnosticModelEndSeconds"]
            )

    midi_first = Counter(event["selectedMidi"] for event in first["onsets"])
    midi_second = Counter(event["selectedMidi"] for event in second["onsets"])
    midi_values = sorted(set(midi_first) | set(midi_second))
    midi_histogram_delta = {
        str(midi): midi_second.get(midi, 0) - midi_first.get(midi, 0)
        for midi in midi_values
        if midi_second.get(midi, 0) != midi_first.get(midi, 0)
    }

    return {
        "inventory": {
            "eventCountFirst": len(first["onsets"]),
            "eventCountSecond": len(second["onsets"]),
            "absoluteEventCountDifference": abs(len(first["onsets"]) - len(second["onsets"])),
            "semanticKeyCountFirst": len(groups_first),
            "semanticKeyCountSecond": len(groups_second),
            "commonSemanticKeyCount": len(common_keys),
            "matchedEventCount": matched_count,
            "unmatchedEventCountFirst": unmatched_first,
            "unmatchedEventCountSecond": unmatched_second,
            "totalUnmatchedEventCount": unmatched_first + unmatched_second,
            "semanticKeysWithCountMismatch": len(mismatched_key_counts),
            "semanticKeyCountMismatchSamples": mismatched_key_counts[:MAX_KEY_SAMPLES],
            "midiHistogramDeltaSecondMinusFirst": midi_histogram_delta,
        },
        "pairedNumericalVariation": {
            "sourceStartSeconds": summarize_deltas(onset_deltas),
            "onsetConfidence": summarize_deltas(confidence_deltas),
            "diagnosticModelEndSeconds": {
                **summarize_deltas(diagnostic_end_deltas),
                "diagnosticOnly": True,
                "usedAsDurationEvidence": False,
            },
        },
    }


def build_report(evidence_a, evidence_b):
    validated_a = validate_evidence(evidence_a, "evidenceA")
    validated_b = validate_evidence(evidence_b, "evidenceB")

    # Canonical ordering makes the report independent of CLI A/B argument order.
    ordered = sorted(
        [validated_a, validated_b],
        key=lambda item: (item["digestSha256"], canonical_json(item["noteIdentity"])),
    )
    first, second = ordered
    measurements = compare_validated(first, second)

    activation_first = first["activationIdentity"]
    activation_second = second["activationIdentity"]
    return {
        "contract": CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "measurementOnly": True,
        "semanticComparisonKey": ["nearestStructureSlot", "selectedMidi"],
        "duplicatePairing": "sorted(sourceStart,onsetConfidence,diagnosticModelEndSeconds,onsetId)-within-semantic-key",
        "inputs": [
            {
                "canonicalEvidenceSha256": first["digestSha256"],
                "eventCount": len(first["onsets"]),
                "noteInferenceIdentity": first["noteIdentity"],
                "activationEvidenceIdentity": activation_first,
                "separationSource": first["separationSource"],
            },
            {
                "canonicalEvidenceSha256": second["digestSha256"],
                "eventCount": len(second["onsets"]),
                "noteInferenceIdentity": second["noteIdentity"],
                "activationEvidenceIdentity": activation_second,
                "separationSource": second["separationSource"],
            },
        ],
        "comparability": {
            "structureIdentity": first["structureIdentity"],
            "audioSource": first["audioSource"],
            "model": first["model"],
            "sameExactNoteInferenceSha256": first["noteIdentity"]["sha256"] == second["noteIdentity"]["sha256"],
            "sameExactActivationBundleSha256": (
                activation_first is not None
                and activation_second is not None
                and activation_first.get("sha256") == activation_second.get("sha256")
            ),
            "sameSeparationSourceString": first["separationSource"] == second["separationSource"],
            "exactHashesAreAdmissionCriteria": False,
        },
        "measurement": measurements,
        "policyBoundary": {
            "status": "MEASURED_REFERENCE_BLIND_VARIATION",
            "thresholdsApplied": False,
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "referenceTabUsed": False,
            "professionalScorerUsed": False,
            "legacyV143ScorerImported": False,
        },
    }


def fake_sha(seed):
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def make_test_evidence(events=None, *, structure_token="structure-1", audio_source="fixture.m4a", model_patch=None):
    if events is None:
        events = [
            (1.000, 1.000, 40, 0.80, 1.40),
            (1.250, 1.250, 52, 0.70, 1.60),
            (2.010, 2.000, 47, 0.90, 2.45),
        ]
    model = {
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
    if model_patch:
        model.update(model_patch)
    onsets = []
    for index, (start, slot, midi, confidence, diagnostic_end) in enumerate(events):
        onset_id = f"basic-pitch-note-{index:06d}"
        onsets.append({
            "onsetId": onset_id,
            "sourceStart": start,
            "nearestStructureSlot": slot,
            "onsetConfidence": confidence,
            "classification": "unambiguous",
            "selectedMidi": midi,
            "sourceEnd": None,
            "durationSeconds": None,
            "durationConfidence": None,
            "candidates": [{
                "candidateId": f"{onset_id}-midi-{midi}",
                "midi": midi,
                "confidence": confidence,
                "spectralDb": None,
                "prominenceDb": None,
                "harmonicSupport": None,
                "provenance": {"source": "songsterr-fresh-basic-pitch-isolated-guitar-v1", "modelNoteId": onset_id},
            }],
            "provenance": {
                "source": "songsterr-fresh-basic-pitch-isolated-guitar-v1",
                "modelNoteId": onset_id,
                "modelDiagnosticEndSeconds": diagnostic_end,
                "modelEndUsedAsDuration": False,
                "separationSource": "run/guitar.wav",
            },
        })
    note_sha = fake_sha(canonical_json([(e[0], e[2], e[3]) for e in events]))
    note_identity = {
        "contract": EXPECTED_NOTE_IDENTITY_CONTRACT,
        "version": 1,
        "algorithm": "sha256",
        "canonicalization": "test",
        "eventCount": len(onsets),
        "sha256": note_sha,
    }
    activation_identity = {
        "contract": EXPECTED_ACTIVATION_BUNDLE_CONTRACT,
        "version": 1,
        "algorithm": "sha256",
        "noteIdentitySha256": note_sha,
        "activationMatrixSha256": fake_sha("activation-" + note_sha),
        "frameTimesSha256": fake_sha("times"),
        "minimumMidi": 40,
        "maximumMidi": 88,
        "frameCount": 10,
        "midiBinCount": 49,
        "sha256": fake_sha("bundle-" + note_sha),
    }
    provenance = {
        "source": EXPECTED_EVIDENCE_CONTRACT,
        "audioSource": audio_source,
        "referenceBlind": True,
        "structureConditioned": True,
        "structureFrozen": True,
        "roleConditioning": "guitar-isolated-stem",
        "sourceSeparationModelInvoked": True,
        "sourceSeparationSource": "run/guitar.wav",
        "modelInvoked": True,
        "gpuInvoked": False,
        "noteInferenceIdentity": copy.deepcopy(note_identity),
        "activationEvidenceIdentity": copy.deepcopy(activation_identity),
        "activationEvidenceSameInference": True,
        "activationEvidenceActiveDurationAuthority": False,
        "legacyV143ScorerImported": False,
        "professionalScorerUsed": False,
        "referenceTabUsed": False,
        "modelNoteEndsUsedAsDuration": False,
    }
    return {
        "contract": EXPECTED_EVIDENCE_CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "structureFrozen": True,
        "structureIdentity": {"contract": "test-structure", "sha256": fake_sha(structure_token)},
        "role": "guitar",
        "capabilities": {
            "roleRelevanceResolved": True,
            "polyphonyResolved": True,
            "durationResolution": "none",
            "instrumentIsolation": "run/guitar.wav",
            "confidenceCalibration": "basic-pitch-note-amplitude-not-calibrated-probability",
        },
        "onsets": onsets,
        "diagnostics": {
            "contract": EXPECTED_EVIDENCE_CONTRACT,
            "onsetCount": len(onsets),
            "candidateCount": len(onsets),
            "classificationCounts": {"unambiguous": len(onsets), "ambiguous": 0, "no-candidate": 0},
            "analysisMidiRange": [40, 88],
            "playableMidiRange": [40, 88],
            "sourceSeparation": "run/guitar.wav",
            "sourceSeparationModelInvoked": True,
            "polyphonicInference": model,
            "polyphonicStartClusterCount": 0,
            "maxStartClusterSize": 1,
            "noteInferenceIdentity": copy.deepcopy(note_identity),
            "activationEvidenceIdentity": copy.deepcopy(activation_identity),
            "sameInferenceActivationEvidenceCaptured": True,
            "modelNoteEndsAreDiagnosticOnly": True,
            "modelNoteEndsUsedAsDuration": False,
            "durationEvidence": {
                "authority": "none-in-model-pitch-stage",
                "resolvedCount": 0,
                "nextOnsetUsedAsDuration": False,
                "syntheticDurationInference": False,
            },
            "confidenceCalibration": "basic-pitch-note-amplitude-not-calibrated-probability",
        },
        "provenance": provenance,
    }


def assert_raises(expected_fragment, fn):
    try:
        fn()
    except ComparisonError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"Expected {expected_fragment!r} in {str(exc)!r}") from exc
        return
    raise AssertionError(f"Expected ComparisonError containing {expected_fragment!r}")


def run_self_test():
    base = make_test_evidence()
    exact_report = build_report(copy.deepcopy(base), copy.deepcopy(base))
    inventory = exact_report["measurement"]["inventory"]
    variation = exact_report["measurement"]["pairedNumericalVariation"]
    assert inventory["totalUnmatchedEventCount"] == 0
    assert variation["sourceStartSeconds"]["maxAbsolute"] == 0.0
    assert variation["onsetConfidence"]["maxAbsolute"] == 0.0
    assert exact_report["policyBoundary"]["thresholdsApplied"] is False
    assert exact_report["policyBoundary"]["admissionDecisionMade"] is False
    assert exact_report["policyBoundary"]["modelValidationComplete"] is False
    assert exact_report["policyBoundary"]["mayAdvanceDelivery"] is False

    perturbed = make_test_evidence([
        (1.002, 1.000, 40, 0.79, 1.41),
        (1.250, 1.250, 52, 0.70, 1.60),
        (2.010, 2.000, 47, 0.90, 2.45),
    ])
    forward = build_report(base, perturbed)
    reverse = build_report(perturbed, base)
    assert canonical_json(forward) == canonical_json(reverse)
    assert forward["measurement"]["inventory"]["totalUnmatchedEventCount"] == 0
    assert forward["measurement"]["pairedNumericalVariation"]["sourceStartSeconds"]["maxAbsolute"] > 0
    assert forward["measurement"]["pairedNumericalVariation"]["onsetConfidence"]["maxAbsolute"] > 0

    extra = make_test_evidence([
        (1.000, 1.000, 40, 0.80, 1.40),
        (1.250, 1.250, 52, 0.70, 1.60),
        (2.010, 2.000, 47, 0.90, 2.45),
        (3.000, 3.000, 55, 0.75, 3.40),
    ])
    extra_report = build_report(base, extra)
    assert extra_report["measurement"]["inventory"]["totalUnmatchedEventCount"] == 1
    assert extra_report["policyBoundary"]["admissionDecisionMade"] is False

    moved_slot = make_test_evidence([
        (1.000, 1.125, 40, 0.80, 1.40),
        (1.250, 1.250, 52, 0.70, 1.60),
        (2.010, 2.000, 47, 0.90, 2.45),
    ])
    moved_report = build_report(base, moved_slot)
    assert moved_report["measurement"]["inventory"]["totalUnmatchedEventCount"] == 2

    bad_provenance = copy.deepcopy(base)
    bad_provenance["provenance"]["referenceTabUsed"] = True
    assert_raises("referenceTabUsed", lambda: build_report(base, bad_provenance))

    bad_nonfinite = copy.deepcopy(base)
    bad_nonfinite["onsets"][0]["sourceStart"] = float("nan")
    assert_raises("sourceStart", lambda: build_report(base, bad_nonfinite))

    bad_midi = copy.deepcopy(base)
    bad_midi["onsets"][0]["selectedMidi"] = 39
    assert_raises("selectedMidi", lambda: build_report(base, bad_midi))

    duration_leak = copy.deepcopy(base)
    duration_leak["onsets"][0]["durationSeconds"] = 0.2
    assert_raises("durationSeconds", lambda: build_report(base, duration_leak))

    structure_mismatch = make_test_evidence(structure_token="structure-2")
    assert_raises("STRUCTURE_IDENTITY_MISMATCH", lambda: build_report(base, structure_mismatch))

    source_mismatch = make_test_evidence(audio_source="other.m4a")
    assert_raises("AUDIO_SOURCE_MISMATCH", lambda: build_report(base, source_mismatch))

    model_mismatch = make_test_evidence(model_patch={"onsetThreshold": 0.51})
    assert_raises("MODEL_SETTINGS_MISMATCH", lambda: build_report(base, model_mismatch))

    unsafe_model_end = copy.deepcopy(base)
    unsafe_model_end["provenance"]["modelNoteEndsUsedAsDuration"] = True
    assert_raises("modelNoteEndsUsedAsDuration", lambda: build_report(base, unsafe_model_end))

    print(json.dumps({
        "contract": CONTRACT,
        "selfTest": "PASS",
        "measurementOnly": True,
        "thresholdsApplied": False,
        "admissionDecisionMade": False,
        "modelValidationComplete": False,
    }, sort_keys=True))


def main():
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    if not args.evidence_a or not args.evidence_b or not args.output:
        raise ComparisonError("USAGE_REQUIRES_TWO_EVIDENCE_FILES_AND_OUTPUT")

    evidence_a = load_json(args.evidence_a)
    evidence_b = load_json(args.evidence_b)
    report = build_report(evidence_a, evidence_b)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    print(json.dumps({
        "contract": CONTRACT,
        "output": str(output_path),
        "measurementOnly": True,
        "thresholdsApplied": False,
        "admissionDecisionMade": False,
        "modelValidationComplete": False,
        "inventory": report["measurement"]["inventory"],
        "pairedNumericalVariation": report["measurement"]["pairedNumericalVariation"],
    }, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ComparisonError as exc:
        print(json.dumps({
            "contract": CONTRACT,
            "status": "REJECTED_NOT_COMPARABLE_OR_INVALID",
            "measurementOnly": True,
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "error": str(exc),
        }, sort_keys=True), file=sys.stderr)
        sys.exit(2)
