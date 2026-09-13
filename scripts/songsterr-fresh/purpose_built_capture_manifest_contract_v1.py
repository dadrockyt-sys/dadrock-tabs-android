#!/usr/bin/env python3
"""Reference-blind contract validator for a future purpose-built V6 holdout.

This tool validates only capture-manifest invariants that can be checked without
opening candidate audio/MIDI files and without invoking Basic Pitch, V6, or any
correctness matcher. It deliberately does NOT establish structural suitability.
Raw media/reference bytes still require a separately preregistered reference-
blind structural/alignment audit before any model execution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

CONTRACT = "songsterr-fresh-purpose-built-capture-manifest-v1"
ALLOWED_CATEGORIES = {"chords", "scales", "singlenotes", "techniques", "music"}
ALLOWED_QA_STATUSES = {"PASS", "FAIL"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

# The manifest is reference-blind. These fields are forbidden anywhere except
# the explicit policyBoundary object, where only fixed fail-closed values are
# accepted. This guards against quietly carrying model/correctness observations
# into population construction.
FORBIDDEN_OBSERVATION_KEYS = {
    "basicpitchoutput",
    "basicpitchevents",
    "v6class",
    "v6classes",
    "v6output",
    "correctness",
    "precision",
    "recall",
    "matchedcount",
    "truepositivecount",
    "falsepositivecount",
    "falsenegativecount",
}

REQUIRED_POLICY_BOUNDARY = {
    "basicPitchInvoked": False,
    "v6Invoked": False,
    "correctnessComputed": False,
    "protectedSongUsed": False,
    "modelValidationComplete": False,
    "customerEligibleEvents": 0,
    "mayAdvanceDelivery": False,
    "durationAuthorityChanged": False,
}


class ContractError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _is_commit(value: Any) -> bool:
    return isinstance(value, str) and COMMIT_RE.fullmatch(value) is not None


def _normalize_key(value: str) -> str:
    return "".join(character.lower() for character in value if character.isalnum())


def _scan_forbidden_observation_keys(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_string = str(key)
            child_path = path + (key_string,)
            # policyBoundary itself is intentionally allowed and validated
            # separately against REQUIRED_POLICY_BOUNDARY.
            if not path or path[-1] != "policyBoundary":
                if _normalize_key(key_string) in FORBIDDEN_OBSERVATION_KEYS:
                    findings.append(".".join(child_path))
            findings.extend(_scan_forbidden_observation_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_scan_forbidden_observation_keys(child, path + (str(index),)))
    return findings


def _validate_identity_block(manifest: dict[str, Any], errors: list[str]) -> None:
    if manifest.get("contract") != CONTRACT:
        errors.append(f"CONTRACT_MISMATCH:{manifest.get('contract')!r}")

    corpus = manifest.get("corpus")
    if not isinstance(corpus, dict):
        errors.append("CORPUS_OBJECT_REQUIRED")
        return

    for key in ("name", "version", "capturePreregistrationPath"):
        if not _is_nonempty_string(corpus.get(key)):
            errors.append(f"CORPUS_{key.upper()}_REQUIRED")

    if not _is_commit(corpus.get("capturePreregistrationCommit")):
        errors.append("CORPUS_CAPTURE_PREREGISTRATION_COMMIT_INVALID")

    rights = corpus.get("rights")
    if not isinstance(rights, dict):
        errors.append("CORPUS_RIGHTS_OBJECT_REQUIRED")
    else:
        if not _is_nonempty_string(rights.get("documentId")):
            errors.append("RIGHTS_DOCUMENT_ID_REQUIRED")
        if not _is_sha256(rights.get("documentSha256")):
            errors.append("RIGHTS_DOCUMENT_SHA256_INVALID")
        if rights.get("productValidationUseAuthorized") is not True:
            errors.append("RIGHTS_PRODUCT_VALIDATION_AUTHORIZATION_REQUIRED")
        if rights.get("protectedSongMaterialExcluded") is not True:
            errors.append("RIGHTS_PROTECTED_SONG_EXCLUSION_REQUIRED")

    hardware = corpus.get("hardware")
    if not isinstance(hardware, dict):
        errors.append("CORPUS_HARDWARE_OBJECT_REQUIRED")
    else:
        if not _is_nonempty_string(hardware.get("evaluatedAudioPathId")):
            errors.append("HARDWARE_EVALUATED_AUDIO_PATH_ID_REQUIRED")
        if not _is_nonempty_string(hardware.get("independentReferencePathId")):
            errors.append("HARDWARE_REFERENCE_PATH_ID_REQUIRED")
        if hardware.get("evaluatedAudioIndependentFromReference") is not True:
            errors.append("HARDWARE_SIGNAL_INDEPENDENCE_REQUIRED")
        if not _is_sha256(hardware.get("configurationSha256")):
            errors.append("HARDWARE_CONFIGURATION_SHA256_INVALID")
        if not _is_nonempty_string(hardware.get("firmwareVersion")):
            errors.append("HARDWARE_FIRMWARE_VERSION_REQUIRED")


def _validate_policy_boundary(manifest: dict[str, Any], errors: list[str]) -> None:
    policy = manifest.get("policyBoundary")
    if not isinstance(policy, dict):
        errors.append("POLICY_BOUNDARY_OBJECT_REQUIRED")
        return
    for key, frozen_value in REQUIRED_POLICY_BOUNDARY.items():
        if policy.get(key) != frozen_value:
            errors.append(f"POLICY_BOUNDARY_CHANGED:{key}:{policy.get(key)!r}!={frozen_value!r}")


def _validate_failure_reasons(manifest: dict[str, Any], errors: list[str]) -> set[str]:
    values = manifest.get("allowedAcquisitionFailureReasons")
    if not isinstance(values, list) or not values:
        errors.append("ALLOWED_ACQUISITION_FAILURE_REASONS_NONEMPTY_LIST_REQUIRED")
        return set()
    reasons: set[str] = set()
    for value in values:
        if not _is_nonempty_string(value):
            errors.append("ALLOWED_ACQUISITION_FAILURE_REASON_INVALID")
            continue
        reason = value.strip()
        if reason in reasons:
            errors.append(f"DUPLICATE_ACQUISITION_FAILURE_REASON:{reason}")
        reasons.add(reason)
    return reasons


def _validate_source_identity(source: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(source, dict):
        errors.append(f"{prefix}_OBJECT_REQUIRED")
        return
    if not _is_nonempty_string(source.get("path")):
        errors.append(f"{prefix}_PATH_REQUIRED")
    if not _is_sha256(source.get("sha256")):
        errors.append(f"{prefix}_SHA256_INVALID")


def _validate_reference_declaration(reference: Any, prefix: str, errors: list[str]) -> list[str]:
    blockers: list[str] = []
    if not isinstance(reference, dict):
        errors.append(f"{prefix}_OBJECT_REQUIRED")
        return blockers

    _validate_source_identity(reference, prefix, errors)
    if not _is_nonempty_string(reference.get("format")):
        errors.append(f"{prefix}_FORMAT_REQUIRED")
    if not _is_sha256(reference.get("configurationSha256")):
        errors.append(f"{prefix}_CONFIGURATION_SHA256_INVALID")
    if not _is_nonempty_string(reference.get("calibrationId")):
        errors.append(f"{prefix}_CALIBRATION_ID_REQUIRED")
    if reference.get("derivedFromEvaluatedAudio") is not False:
        errors.append(f"{prefix}_MUST_DECLARE_NOT_DERIVED_FROM_EVALUATED_AUDIO")

    summary = reference.get("declaredStructuralSummary")
    if summary is not None:
        if not isinstance(summary, dict):
            errors.append(f"{prefix}_DECLARED_STRUCTURAL_SUMMARY_INVALID")
        else:
            for key in ("unmatchedNoteOnCount", "unmatchedNoteOffCount", "sameKeyOverlapCount"):
                value = summary.get(key)
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    errors.append(f"{prefix}_{key.upper()}_INVALID")
                elif value != 0:
                    blockers.append(f"{prefix}:{key}={value}")
            paired = summary.get("pairedEventCount")
            if not isinstance(paired, int) or isinstance(paired, bool) or paired < 0:
                errors.append(f"{prefix}_PAIRED_EVENT_COUNT_INVALID")

    return blockers


def _validate_attempts(
    manifest: dict[str, Any],
    allowed_failure_reasons: set[str],
    errors: list[str],
) -> tuple[list[dict[str, Any]], list[str], dict[str, int]]:
    attempts = manifest.get("attempts")
    if not isinstance(attempts, list) or not attempts:
        errors.append("ATTEMPTS_NONEMPTY_LIST_REQUIRED")
        return [], [], {"attemptCount": 0, "admittedCount": 0, "failedAcquisitionCount": 0}

    seen_attempt_ids: set[str] = set()
    by_slot: dict[str, list[dict[str, Any]]] = defaultdict(list)
    declared_blockers: list[str] = []

    for index, attempt in enumerate(attempts):
        prefix = f"ATTEMPT[{index}]"
        if not isinstance(attempt, dict):
            errors.append(f"{prefix}_OBJECT_REQUIRED")
            continue

        attempt_id = attempt.get("attemptId")
        slot_id = attempt.get("slotId")
        player_id = attempt.get("playerId")
        exercise_id = attempt.get("exerciseId")
        category = attempt.get("category")
        attempt_number = attempt.get("attemptNumber")
        timestamp = attempt.get("capturedAtUtc")

        if not _is_nonempty_string(attempt_id):
            errors.append(f"{prefix}_ATTEMPT_ID_REQUIRED")
        elif attempt_id in seen_attempt_ids:
            errors.append(f"DUPLICATE_ATTEMPT_ID:{attempt_id}")
        else:
            seen_attempt_ids.add(attempt_id)

        if not _is_nonempty_string(slot_id):
            errors.append(f"{prefix}_SLOT_ID_REQUIRED")
        if not _is_nonempty_string(player_id):
            errors.append(f"{prefix}_PLAYER_ID_REQUIRED")
        if not _is_nonempty_string(exercise_id):
            errors.append(f"{prefix}_EXERCISE_ID_REQUIRED")
        if category not in ALLOWED_CATEGORIES:
            errors.append(f"{prefix}_CATEGORY_INVALID:{category!r}")
        if not isinstance(attempt_number, int) or isinstance(attempt_number, bool) or attempt_number <= 0:
            errors.append(f"{prefix}_ATTEMPT_NUMBER_INVALID:{attempt_number!r}")
        if not _is_nonempty_string(timestamp):
            errors.append(f"{prefix}_CAPTURED_AT_UTC_REQUIRED")

        qa = attempt.get("acquisitionQa")
        if not isinstance(qa, dict):
            errors.append(f"{prefix}_ACQUISITION_QA_OBJECT_REQUIRED")
            continue
        status = qa.get("status")
        reason = qa.get("reason")
        if status not in ALLOWED_QA_STATUSES:
            errors.append(f"{prefix}_ACQUISITION_QA_STATUS_INVALID:{status!r}")
        elif status == "PASS":
            if reason not in (None, ""):
                errors.append(f"{prefix}_PASS_REASON_MUST_BE_EMPTY")
        else:
            if not _is_nonempty_string(reason) or reason not in allowed_failure_reasons:
                errors.append(f"{prefix}_FAIL_REASON_NOT_FROZEN:{reason!r}")

        admitted = attempt.get("admitted")
        if not isinstance(admitted, bool):
            errors.append(f"{prefix}_ADMITTED_BOOLEAN_REQUIRED")
        if admitted is True and status != "PASS":
            errors.append(f"{prefix}_ADMITTED_ATTEMPT_MUST_PASS_ACQUISITION_QA")
        if admitted is False and status == "PASS":
            # A transport-valid attempt may not be silently discarded to seek
            # a later/better take.
            errors.append(f"{prefix}_PASS_ATTEMPT_MUST_BE_ADMITTED")

        if admitted is True:
            audio = attempt.get("evaluatedAudio")
            reference = attempt.get("reference")
            _validate_source_identity(audio, f"{prefix}_EVALUATED_AUDIO", errors)
            declared_blockers.extend(
                _validate_reference_declaration(reference, f"{prefix}_REFERENCE", errors)
            )
            if isinstance(audio, dict) and isinstance(reference, dict):
                if audio.get("path") == reference.get("path"):
                    errors.append(f"{prefix}_AUDIO_REFERENCE_PATHS_MUST_DIFFER")
                if _is_sha256(audio.get("sha256")) and audio.get("sha256") == reference.get("sha256"):
                    errors.append(f"{prefix}_AUDIO_REFERENCE_HASHES_MUST_DIFFER")
        else:
            # Failed attempts may preserve partial source identities for
            # chronology/provenance, but are never required to have complete
            # media/reference objects.
            if "evaluatedAudio" in attempt and attempt["evaluatedAudio"] is not None:
                _validate_source_identity(attempt["evaluatedAudio"], f"{prefix}_FAILED_AUDIO", errors)
            if "reference" in attempt and attempt["reference"] is not None:
                _validate_source_identity(attempt["reference"], f"{prefix}_FAILED_REFERENCE", errors)

        if _is_nonempty_string(slot_id):
            by_slot[slot_id].append(attempt)

    admitted_rows: list[dict[str, Any]] = []
    for slot_id, rows in sorted(by_slot.items()):
        numbers = [row.get("attemptNumber") for row in rows]
        valid_numbers = [value for value in numbers if isinstance(value, int) and not isinstance(value, bool) and value > 0]
        if len(valid_numbers) != len(set(valid_numbers)):
            errors.append(f"DUPLICATE_ATTEMPT_NUMBER_IN_SLOT:{slot_id}")

        sorted_rows = sorted(
            rows,
            key=lambda row: (
                row.get("attemptNumber") if isinstance(row.get("attemptNumber"), int) else 10**18,
                str(row.get("attemptId", "")),
            ),
        )
        pass_rows = [row for row in sorted_rows if isinstance(row.get("acquisitionQa"), dict) and row["acquisitionQa"].get("status") == "PASS"]
        admitted = [row for row in sorted_rows if row.get("admitted") is True]

        if pass_rows:
            first_pass = pass_rows[0]
            if len(admitted) != 1:
                errors.append(f"SLOT_MUST_HAVE_EXACTLY_ONE_ADMITTED_PASS:{slot_id}:{len(admitted)}")
            elif admitted[0] is not first_pass:
                errors.append(f"FIRST_TRANSPORT_VALID_ATTEMPT_NOT_ADMITTED:{slot_id}")
            first_pass_number = first_pass.get("attemptNumber")
            if isinstance(first_pass_number, int):
                later = [
                    row for row in sorted_rows
                    if isinstance(row.get("attemptNumber"), int) and row["attemptNumber"] > first_pass_number
                ]
                if later:
                    errors.append(f"ATTEMPTS_EXIST_AFTER_FIRST_ADMITTED_PASS:{slot_id}")
        elif admitted:
            errors.append(f"SLOT_ADMITTED_WITHOUT_PASS:{slot_id}")

        if len(admitted) == 1:
            admitted_rows.append(admitted[0])

    stats = {
        "attemptCount": len([row for row in attempts if isinstance(row, dict)]),
        "admittedCount": len(admitted_rows),
        "failedAcquisitionCount": sum(
            1
            for row in attempts
            if isinstance(row, dict)
            and isinstance(row.get("acquisitionQa"), dict)
            and row["acquisitionQa"].get("status") == "FAIL"
        ),
    }
    return admitted_rows, declared_blockers, stats


def _population_identity_rows(admitted_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for attempt in admitted_rows:
        audio = attempt.get("evaluatedAudio") or {}
        reference = attempt.get("reference") or {}
        rows.append({
            "attemptId": attempt.get("attemptId"),
            "slotId": attempt.get("slotId"),
            "playerId": attempt.get("playerId"),
            "exerciseId": attempt.get("exerciseId"),
            "category": attempt.get("category"),
            "attemptNumber": attempt.get("attemptNumber"),
            "evaluatedAudioPath": audio.get("path"),
            "evaluatedAudioSha256": audio.get("sha256"),
            "referencePath": reference.get("path"),
            "referenceSha256": reference.get("sha256"),
            "referenceConfigurationSha256": reference.get("configurationSha256"),
            "calibrationId": reference.get("calibrationId"),
        })
    rows.sort(key=lambda row: (str(row["slotId"]), int(row["attemptNumber"] or 0), str(row["attemptId"])))
    return rows


def validate_manifest(manifest: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return {
            "contract": CONTRACT,
            "contractValid": False,
            "errors": ["TOP_LEVEL_OBJECT_REQUIRED"],
            "warnings": [],
            "declaredStructuralBlockers": [],
            "mayAdvanceToReferenceBlindStructuralAudit": False,
            "authoritativeStructuralSuitabilityEstablished": False,
            "correctnessAuthorized": False,
        }

    _validate_identity_block(manifest, errors)
    _validate_policy_boundary(manifest, errors)
    failure_reasons = _validate_failure_reasons(manifest, errors)

    forbidden = _scan_forbidden_observation_keys(manifest)
    for path in forbidden:
        errors.append(f"FORBIDDEN_MODEL_OR_CORRECTNESS_OBSERVATION_FIELD:{path}")

    admitted_rows, declared_blockers, stats = _validate_attempts(
        manifest,
        failure_reasons,
        errors,
    )

    hardware = manifest.get("corpus", {}).get("hardware", {}) if isinstance(manifest.get("corpus"), dict) else {}
    hardware_config_sha = hardware.get("configurationSha256") if isinstance(hardware, dict) else None
    for attempt in admitted_rows:
        reference = attempt.get("reference")
        if isinstance(reference, dict) and _is_sha256(hardware_config_sha):
            if reference.get("configurationSha256") != hardware_config_sha:
                errors.append(
                    f"REFERENCE_CONFIGURATION_MISMATCH:{attempt.get('attemptId')}:{reference.get('configurationSha256')}!={hardware_config_sha}"
                )

    population_rows = _population_identity_rows(admitted_rows)
    population_sha = sha256_bytes(canonical_json(population_rows).encode("utf-8"))

    warnings: list[str] = []
    if not admitted_rows:
        warnings.append("NO_ADMITTED_POPULATION_YET")

    raw_reference_planning_count = 0
    summaries_complete = True
    for attempt in admitted_rows:
        reference = attempt.get("reference")
        summary = reference.get("declaredStructuralSummary") if isinstance(reference, dict) else None
        if not isinstance(summary, dict) or not isinstance(summary.get("pairedEventCount"), int):
            summaries_complete = False
            continue
        raw_reference_planning_count += max(0, int(summary["pairedEventCount"]))
    if not summaries_complete and admitted_rows:
        warnings.append("DECLARED_REFERENCE_EVENT_TOTAL_INCOMPLETE")

    contract_valid = not errors
    # Even a clean declaration merely allows a future raw-byte structural audit.
    # It cannot establish source truth or authorize model execution.
    may_advance_to_structural_audit = contract_valid and not declared_blockers and bool(admitted_rows)

    return {
        "contract": CONTRACT,
        "contractValid": contract_valid,
        "errors": sorted(errors),
        "warnings": sorted(warnings),
        "attemptStats": stats,
        "admittedPopulationCount": len(admitted_rows),
        "admittedPopulationManifestSha256": population_sha,
        "declaredRawReferencePairedEventCountPlanningOnly": raw_reference_planning_count,
        "declaredStructuralBlockers": sorted(declared_blockers),
        "mayAdvanceToReferenceBlindStructuralAudit": may_advance_to_structural_audit,
        "authoritativeStructuralSuitabilityEstablished": False,
        "basicPitchAuthorized": False,
        "v6Authorized": False,
        "correctnessAuthorized": False,
        "policyBoundary": dict(REQUIRED_POLICY_BOUNDARY),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="Path to capture manifest JSON")
    parser.add_argument("--output", help="Optional deterministic validation-result JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = validate_manifest(manifest)
    rendered = canonical_json(result) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["contractValid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
