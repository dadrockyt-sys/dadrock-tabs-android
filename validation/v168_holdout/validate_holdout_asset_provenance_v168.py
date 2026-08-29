#!/usr/bin/env python3
"""Validate V168 holdout provenance and source/reference pair binding.

This is a strict companion to the already-frozen
``validate_holdout_asset_manifest_v168.py`` admission validator.  It validates the
same ``dadrock.tabs.v168.holdout-asset-manifest.v1`` payload and first calls the
frozen base validator, then requires additional prospective provenance metadata.

It never opens source audio bytes, professional reference note/event bytes,
generated candidates, or scorer code.  It cannot score anything.  Its purpose is
to make future external holdout acquisition auditable without changing the frozen
V168 two-policy evaluation rule or the frozen base admission contract.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Mapping

from validate_holdout_asset_manifest_v168 import (
    CALIBRATION_SONG_ID,
    FROZEN_POLICY_IDS,
    ManifestError as BaseManifestError,
    validate_manifest as validate_base_manifest,
)

SCHEMA = "dadrock.tabs.v168.holdout-asset-manifest.v1"
PROVENANCE_GATE = "dadrock.tabs.v168.holdout-provenance-gate.v1"
EXPECTED_BASE_VALIDATOR_GIT_BLOB = "c9e0b00ffe9cddf8138e63843afa98a715fed579"


class ProvenanceError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProvenanceError(message)


def require_text(value: Any, field: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{field} must be non-empty text")
    return value.strip()


def validate_locator(value: Any, field: str) -> dict[str, str]:
    require(isinstance(value, Mapping), f"{field} must be an object")
    locator_type = require_text(value.get("type"), f"{field}.type")
    label = require_text(value.get("label"), f"{field}.label")
    require(
        locator_type in {"repository_path", "private_artifact", "user_supplied", "licensed_source"},
        f"{field}.type is not an allowed non-secret locator type",
    )
    require(value.get("locatorFrozen") is True, f"{field}.locatorFrozen must be true")
    return {"type": locator_type, "label": label}


def validate_provenance(value: Any, field: str) -> dict[str, str]:
    require(isinstance(value, Mapping), f"{field} must be an object")
    origin = require_text(value.get("origin"), f"{field}.origin")
    acquisition = require_text(value.get("acquisitionMethod"), f"{field}.acquisitionMethod")
    use_basis = require_text(value.get("rightsOrUseBasis"), f"{field}.rightsOrUseBasis")
    require(value.get("metadataFrozen") is True, f"{field}.metadataFrozen must be true")
    return {
        "origin": origin,
        "acquisitionMethod": acquisition,
        "rightsOrUseBasis": use_basis,
    }


def validate_song_provenance(row: Mapping[str, Any], index: int) -> dict[str, Any]:
    prefix = f"songs[{index}]"
    song_id = require_text(row.get("songId"), f"{prefix}.songId")
    require(song_id != CALIBRATION_SONG_ID, f"{prefix} cannot be the V167 calibration song")

    source = row.get("sourceAudio") or {}
    reference = row.get("professionalReference") or {}
    require(isinstance(source, Mapping), f"{prefix}.sourceAudio must be an object")
    require(isinstance(reference, Mapping), f"{prefix}.professionalReference must be an object")

    source_sha = require_text(source.get("sha256"), f"{prefix}.sourceAudio.sha256").lower()
    reference_sha = require_text(
        reference.get("sha256"), f"{prefix}.professionalReference.sha256"
    ).lower()

    source_locator = validate_locator(source.get("storageLocator"), f"{prefix}.sourceAudio.storageLocator")
    reference_locator = validate_locator(
        reference.get("storageLocator"), f"{prefix}.professionalReference.storageLocator"
    )
    source_provenance = validate_provenance(
        source.get("provenance"), f"{prefix}.sourceAudio.provenance"
    )
    reference_provenance = validate_provenance(
        reference.get("provenance"), f"{prefix}.professionalReference.provenance"
    )

    require(
        source.get("acquiredBeforeAdmissionDecision") is True,
        f"{prefix}.sourceAudio.acquiredBeforeAdmissionDecision must be true",
    )
    require(
        reference.get("preparedBy") is not None,
        f"{prefix}.professionalReference.preparedBy is required",
    )
    require_text(reference.get("preparedBy"), f"{prefix}.professionalReference.preparedBy")
    require(
        reference.get("derivedFromModelOrCandidateOutput") is False,
        f"{prefix}.professionalReference.derivedFromModelOrCandidateOutput must be false",
    )
    require(
        reference.get("preparedIndependentlyOfV167Calibration") is True,
        f"{prefix}.professionalReference.preparedIndependentlyOfV167Calibration must be true",
    )
    require(
        reference.get("referenceBytesAccessibleToCandidateGeneration") is False,
        f"{prefix}.professionalReference.referenceBytesAccessibleToCandidateGeneration must be false",
    )
    require(
        reference.get("frozenV154ScorerCompatible") is True,
        f"{prefix}.professionalReference.frozenV154ScorerCompatible must be true",
    )
    require(
        reference.get("sourceAudioSha256") == source_sha,
        f"{prefix}.professionalReference.sourceAudioSha256 must bind to sourceAudio.sha256",
    )

    pair = row.get("pairBinding") or {}
    require(isinstance(pair, Mapping), f"{prefix}.pairBinding must be an object")
    require(
        pair.get("sourceAudioSha256") == source_sha,
        f"{prefix}.pairBinding.sourceAudioSha256 mismatch",
    )
    require(
        pair.get("professionalReferenceSha256") == reference_sha,
        f"{prefix}.pairBinding.professionalReferenceSha256 mismatch",
    )
    require(pair.get("sameRecording") is True, f"{prefix}.pairBinding.sameRecording must be true")
    require(pair.get("bindingFrozen") is True, f"{prefix}.pairBinding.bindingFrozen must be true")

    quality = row.get("qualityGate") or {}
    require(isinstance(quality, Mapping), f"{prefix}.qualityGate must be an object")
    require(
        quality.get("combinedGuitarCoverageReviewed") is True,
        f"{prefix}.qualityGate.combinedGuitarCoverageReviewed must be true",
    )
    require(
        quality.get("timingGridCompatibilityReviewed") is True,
        f"{prefix}.qualityGate.timingGridCompatibilityReviewed must be true",
    )
    require(
        quality.get("uncertaintyPolicyFrozen") is True,
        f"{prefix}.qualityGate.uncertaintyPolicyFrozen must be true",
    )
    require(
        quality.get("qualityDecisionMadeWithoutComparativeScores") is True,
        f"{prefix}.qualityGate.qualityDecisionMadeWithoutComparativeScores must be true",
    )

    return {
        "songId": song_id,
        "sourceSha256": source_sha,
        "referenceSha256": reference_sha,
        "sourceLocatorType": source_locator["type"],
        "referenceLocatorType": reference_locator["type"],
        "sourceOrigin": source_provenance["origin"],
        "referenceOrigin": reference_provenance["origin"],
    }


def validate_provenance_manifest(payload: Mapping[str, Any]) -> dict[str, Any]:
    try:
        base_summary = validate_base_manifest(payload)
    except BaseManifestError as exc:
        raise ProvenanceError(f"frozen base admission failed: {exc}") from exc

    require(payload.get("schema") == SCHEMA, f"schema must equal {SCHEMA}")
    require(
        payload.get("provenanceGate") == PROVENANCE_GATE,
        f"provenanceGate must equal {PROVENANCE_GATE}",
    )
    require(
        payload.get("policyIds") == FROZEN_POLICY_IDS,
        "policyIds must remain the two frozen V168 policies",
    )
    require(
        payload.get("acquisitionMetadataFrozenBeforeAdmission") is True,
        "acquisitionMetadataFrozenBeforeAdmission must be true",
    )
    require(
        payload.get("sourceReferencePairBindingsFrozen") is True,
        "sourceReferencePairBindingsFrozen must be true",
    )
    require(
        payload.get("provenanceReviewedWithoutComparativeScores") is True,
        "provenanceReviewedWithoutComparativeScores must be true",
    )

    songs = payload.get("songs") or []
    rows = [validate_song_provenance(row, i) for i, row in enumerate(songs)]
    require(len(rows) >= 2, "at least two provenance-complete holdout songs are required")

    return {
        "schema": SCHEMA,
        "provenanceGate": PROVENANCE_GATE,
        "baseAdmissionStatus": base_summary["status"],
        "songCount": len(rows),
        "songIds": [row["songId"] for row in rows],
        "policyIds": list(FROZEN_POLICY_IDS),
        "referenceFacingScoringArmed": False,
        "v168ReferenceFacingScoreCalls": 0,
        "pairBindingsFrozen": True,
        "provenanceMetadataFrozen": True,
    }


def _fake_song(index: int) -> dict[str, Any]:
    source_sha = f"{index + 1:064x}"
    reference_sha = f"{index + 101:064x}"
    return {
        "songId": f"prospective-holdout-{index + 1}",
        "artist": f"Prospective Artist {index + 1}",
        "title": f"Prospective Song {index + 1}",
        "independentFromV167CalibrationSong": True,
        "admissionDecisionMadeWithoutComparativeScores": True,
        "sourceAudio": {
            "artifactLabel": f"private source recording {index + 1}",
            "sha256": source_sha,
            "gitBlob": None,
            "identityFrozen": True,
            "storageLocator": {
                "type": "private_artifact",
                "label": f"private-source-{index + 1}",
                "locatorFrozen": True,
            },
            "provenance": {
                "origin": "self-test fixture",
                "acquisitionMethod": "prospective fixture",
                "rightsOrUseBasis": "self-test only",
                "metadataFrozen": True,
            },
            "acquiredBeforeAdmissionDecision": True,
        },
        "professionalReference": {
            "artifactLabel": f"private professional reference {index + 1}",
            "sha256": reference_sha,
            "gitBlob": None,
            "identityFrozen": True,
            "kind": "professional_scorer_ready",
            "combinedGuitarCovered": True,
            "uncertaintyAnnotationsFrozen": True,
            "candidateGenerationMayReadNoteEvents": False,
            "referenceFrozenBeforeCandidateScoring": True,
            "storageLocator": {
                "type": "private_artifact",
                "label": f"private-reference-{index + 1}",
                "locatorFrozen": True,
            },
            "provenance": {
                "origin": "self-test fixture",
                "acquisitionMethod": "prospective fixture",
                "rightsOrUseBasis": "self-test only",
                "metadataFrozen": True,
            },
            "preparedBy": "self-test professional-placeholder",
            "derivedFromModelOrCandidateOutput": False,
            "preparedIndependentlyOfV167Calibration": True,
            "referenceBytesAccessibleToCandidateGeneration": False,
            "frozenV154ScorerCompatible": True,
            "sourceAudioSha256": source_sha,
        },
        "pairBinding": {
            "sourceAudioSha256": source_sha,
            "professionalReferenceSha256": reference_sha,
            "sameRecording": True,
            "bindingFrozen": True,
        },
        "qualityGate": {
            "combinedGuitarCoverageReviewed": True,
            "timingGridCompatibilityReviewed": True,
            "uncertaintyPolicyFrozen": True,
            "qualityDecisionMadeWithoutComparativeScores": True,
        },
    }


def _valid_fixture() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "version": "V168",
        "status": "HOLDOUT_ASSETS_FROZEN_BEFORE_CANDIDATE_GENERATION",
        "calibrationSongIdExcluded": CALIBRATION_SONG_ID,
        "policyIds": list(FROZEN_POLICY_IDS),
        "minimumHoldoutSongs": 2,
        "provenanceGate": PROVENANCE_GATE,
        "acquisitionMetadataFrozenBeforeAdmission": True,
        "sourceReferencePairBindingsFrozen": True,
        "provenanceReviewedWithoutComparativeScores": True,
        "boundary": {
            "professionalReferenceReadByCandidateGeneration": False,
            "comparativeScoresReadBeforeAdmissionFreeze": False,
            "referenceFacingScoringArmed": False,
            "v168ReferenceFacingScoreCallsBeforeAssetFreeze": 0,
            "mainOrProductionModified": False,
            "gpuCudaModalUsed": False,
        },
        "songs": [_fake_song(0), _fake_song(1)],
    }


def self_test() -> dict[str, Any]:
    valid = _valid_fixture()
    summary = validate_provenance_manifest(valid)
    require(summary["songCount"] == 2, "self-test valid fixture did not admit two songs")

    rejected: list[str] = []
    cases: list[tuple[str, dict[str, Any]]] = []

    bad_binding = copy.deepcopy(valid)
    bad_binding["songs"][0]["professionalReference"]["sourceAudioSha256"] = "f" * 64
    cases.append(("source-reference-hash-binding", bad_binding))

    model_derived = copy.deepcopy(valid)
    model_derived["songs"][0]["professionalReference"]["derivedFromModelOrCandidateOutput"] = True
    cases.append(("model-derived-reference", model_derived))

    reference_visible = copy.deepcopy(valid)
    reference_visible["songs"][0]["professionalReference"]["referenceBytesAccessibleToCandidateGeneration"] = True
    cases.append(("candidate-generation-reference-access", reference_visible))

    unfrozen_rights = copy.deepcopy(valid)
    unfrozen_rights["songs"][0]["professionalReference"]["provenance"]["metadataFrozen"] = False
    cases.append(("unfrozen-provenance", unfrozen_rights))

    not_compatible = copy.deepcopy(valid)
    not_compatible["songs"][0]["professionalReference"]["frozenV154ScorerCompatible"] = False
    cases.append(("scorer-incompatible-reference", not_compatible))

    for name, payload in cases:
        try:
            validate_provenance_manifest(payload)
        except ProvenanceError:
            rejected.append(name)
        else:
            raise ProvenanceError(f"self-test expected rejection: {name}")

    return {
        "status": "SELF_TEST_PASS",
        "validSongCount": summary["songCount"],
        "negativeCasesRejected": rejected,
        "referenceFacingScoreCalls": 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--manifest", type=Path)
    group.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0

    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    summary = validate_provenance_manifest(payload)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProvenanceError as exc:
        raise SystemExit(f"V168 holdout provenance invalid: {exc}")
