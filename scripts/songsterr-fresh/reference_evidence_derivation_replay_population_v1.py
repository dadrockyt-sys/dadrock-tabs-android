#!/usr/bin/env python3
"""Reference evidence derivation replay population V1.

Synthetic/software qualification only. This validator verifies immutable upstream
result/package/binding/raw-evidence identities before executing the exact
package-bound Python decoder in isolated mode. It never inspects evaluated audio
or invokes Basic Pitch, V6, correctness, or customer-delivery logic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

CONTRACT = "songsterr-fresh-purpose-built-reference-evidence-derivation-replay-population-v1"
POPULATION_IDENTITY_VERSION = "reference-evidence-derivation-replay-population-v1"
V23_CONTRACT = "songsterr-fresh-purpose-built-capture-manifest-v2.3"
V23_POPULATION_IDENTITY_VERSION = "capture-manifest-v2.3-structural-audit-input-binding-v1"
BINDING_CONTRACT = "songsterr-fresh-purpose-built-structural-audit-input-binding-v1"
COMPLETENESS_CONTRACT = "songsterr-fresh-purpose-built-reference-blind-structural-audit-population-completeness-v1"
COMPLETENESS_IDENTITY_VERSION = "reference-blind-structural-audit-population-completeness-v1"
PROVENANCE_CONTRACT = "songsterr-fresh-purpose-built-reference-calibration-package-v1"
DECODER_TIMEOUT_SECONDS = 10.0
REQUIRED_PYTHON_MAJOR_MINOR = (3, 12)

CLOSED_BOOL_FIELDS = (
    "realCalibrationAuthorized",
    "realHoldoutCaptureAuthorized",
    "basicPitchAuthorized",
    "v6Authorized",
    "correctnessAuthorized",
    "modelValidationComplete",
    "mayAdvanceDelivery",
)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and value == value.lower()
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _closed_authorization() -> dict[str, Any]:
    return {
        "realCalibrationAuthorized": False,
        "realHoldoutCaptureAuthorized": False,
        "basicPitchAuthorized": False,
        "v6Authorized": False,
        "correctnessAuthorized": False,
        "modelValidationComplete": False,
        "customerEligibleEvents": 0,
        "mayAdvanceDelivery": False,
    }


def _authorization_closed(value: Mapping[str, Any]) -> bool:
    return all(value.get(field) is False for field in CLOSED_BOOL_FIELDS) and value.get(
        "customerEligibleEvents"
    ) == 0


def _source_report(raw: Any, expected_sha256: Any) -> dict[str, Any]:
    actual = sha256_bytes(raw) if isinstance(raw, bytes) else None
    return {
        "expected": expected_sha256,
        "actual": actual,
        "matches": bool(
            actual is not None
            and _is_sha256(expected_sha256)
            and actual == expected_sha256
        ),
    }


def _verify_parse_result(
    *, raw: Any, expected_sha256: Any, prefix: str, errors: list[str]
) -> tuple[dict[str, Any] | None, str | None, dict[str, Any]]:
    report = _source_report(raw, expected_sha256)
    if not isinstance(raw, bytes):
        errors.append(f"{prefix}_NOT_BYTES")
        return None, None, report
    if not _is_sha256(expected_sha256):
        errors.append(f"{prefix}_EXPECTED_SHA256_INVALID")
        return None, None, report
    actual = report["actual"]
    if actual != expected_sha256:
        errors.append(f"{prefix}_SHA256_MISMATCH")
        return None, None, report
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"{prefix}_INVALID_JSON:{type(exc).__name__}")
        return None, actual, report
    if not isinstance(parsed, dict):
        errors.append(f"{prefix}_OBJECT_REQUIRED")
        return None, actual, report
    return parsed, actual, report


def _binding_key_rows(value: Any, prefix: str, errors: list[str]) -> list[dict[str, str]]:
    if not isinstance(value, list):
        errors.append(f"{prefix}_LIST_REQUIRED")
        return []
    rows: list[dict[str, str]] = []
    seen_attempts: set[str] = set()
    seen_keys: set[tuple[str, str]] = set()
    for index, row in enumerate(value):
        if not isinstance(row, dict):
            errors.append(f"{prefix}[{index}]_OBJECT_REQUIRED")
            continue
        attempt_id = row.get("attemptId")
        binding_sha = row.get("structuralAuditInputsSha256")
        if not _nonempty(attempt_id):
            errors.append(f"{prefix}[{index}]_ATTEMPT_ID_REQUIRED")
            continue
        if not _is_sha256(binding_sha):
            errors.append(f"{prefix}[{index}]_BINDING_SHA256_INVALID")
            continue
        attempt_id = attempt_id.strip()
        key = (attempt_id, binding_sha)
        if attempt_id in seen_attempts:
            errors.append(f"{prefix}_DUPLICATE_ATTEMPT_ID:{attempt_id}")
        seen_attempts.add(attempt_id)
        if key in seen_keys:
            errors.append(f"{prefix}_DUPLICATE_KEY:{attempt_id}:{binding_sha}")
        seen_keys.add(key)
        rows.append({"attemptId": attempt_id, "structuralAuditInputsSha256": binding_sha})
    rows.sort(key=lambda row: (row["attemptId"], row["structuralAuditInputsSha256"]))
    return rows


def _validate_v23(
    parsed: dict[str, Any], actual_sha: str, errors: list[str]
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    if parsed.get("contract") != V23_CONTRACT:
        errors.append("V23_CONTRACT_MISMATCH")
    if parsed.get("contractValid") is not True:
        errors.append("V23_CONTRACT_NOT_VALID")
    if parsed.get("errors") != []:
        errors.append("V23_ERRORS_NOT_EMPTY")
    if parsed.get("v23SemanticGuardPassed") is not True:
        errors.append("V23_SEMANTIC_GUARD_NOT_PASSED")
    if parsed.get("mayAdvanceToReferenceBlindStructuralAudit") is not True:
        errors.append("V23_MAY_ADVANCE_NOT_TRUE")
    if parsed.get("populationIdentityVersion") != V23_POPULATION_IDENTITY_VERSION:
        errors.append("V23_POPULATION_IDENTITY_VERSION_MISMATCH")
    population_sha = parsed.get("admittedPopulationManifestSha256")
    if not _is_sha256(population_sha):
        errors.append("V23_ADMITTED_POPULATION_SHA256_INVALID")
    if parsed.get("structuralAuditInputBindingContract") != BINDING_CONTRACT:
        errors.append("V23_BINDING_CONTRACT_MISMATCH")
    if not _authorization_closed(parsed):
        errors.append("V23_DOWNSTREAM_AUTHORIZATION_NOT_CLOSED")

    rows = _binding_key_rows(parsed.get("structuralAuditInputBindings"), "V23_BINDINGS", errors)
    count = parsed.get("structuralAuditInputBindingCount")
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        errors.append("V23_BINDING_COUNT_INVALID")
    elif count != len(rows):
        errors.append("V23_BINDING_COUNT_MISMATCH")

    identities = {
        "validationResultSha256": actual_sha,
        "admittedPopulationSha256": population_sha if _is_sha256(population_sha) else None,
        "provenanceResultSha256": parsed.get("calibrationPackageValidationResultSha256"),
        "packageBindingSha256": parsed.get("calibrationPackageBindingSha256"),
        "decoderConfigurationSha256": parsed.get("calibrationPackageDecoderConfigurationSha256"),
    }
    for name in (
        "provenanceResultSha256",
        "packageBindingSha256",
        "decoderConfigurationSha256",
    ):
        if not _is_sha256(identities[name]):
            errors.append(f"V23_{name.upper()}_INVALID")
    return rows, identities


def _validate_completeness(
    parsed: dict[str, Any], actual_sha: str, v23_rows: list[dict[str, str]], v23_ids: dict[str, Any], errors: list[str]
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    if parsed.get("contract") != COMPLETENESS_CONTRACT:
        errors.append("COMPLETENESS_CONTRACT_MISMATCH")
    if parsed.get("contractValid") is not True:
        errors.append("COMPLETENESS_CONTRACT_NOT_VALID")
    if parsed.get("errors") != []:
        errors.append("COMPLETENESS_ERRORS_NOT_EMPTY")
    if parsed.get("populationStructurallySuitable") is not True:
        errors.append("COMPLETENESS_POPULATION_NOT_STRUCTURALLY_SUITABLE")
    if parsed.get("populationStructuralCompletenessEstablished") is not True:
        errors.append("COMPLETENESS_NOT_ESTABLISHED")
    if parsed.get("populationIdentityVersion") != COMPLETENESS_IDENTITY_VERSION:
        errors.append("COMPLETENESS_IDENTITY_VERSION_MISMATCH")
    completeness_sha = parsed.get("populationStructuralCompletenessSha256")
    if not _is_sha256(completeness_sha):
        errors.append("COMPLETENESS_POPULATION_SHA256_INVALID")
    if parsed.get("captureManifestV23ValidationResultSha256") != v23_ids.get("validationResultSha256"):
        errors.append("COMPLETENESS_V23_RESULT_SHA256_MISMATCH")
    if parsed.get("captureManifestV23AdmittedPopulationSha256") != v23_ids.get("admittedPopulationSha256"):
        errors.append("COMPLETENESS_V23_POPULATION_SHA256_MISMATCH")
    if not _authorization_closed(parsed):
        errors.append("COMPLETENESS_DOWNSTREAM_AUTHORIZATION_NOT_CLOSED")

    admitted_rows = _binding_key_rows(parsed.get("admittedBindingKeys"), "COMPLETENESS_ADMITTED_BINDINGS", errors)
    verified_rows = _binding_key_rows(parsed.get("verifiedV12BindingKeys"), "COMPLETENESS_VERIFIED_BINDINGS", errors)
    if admitted_rows != v23_rows:
        errors.append("COMPLETENESS_ADMITTED_SET_MISMATCH")
    if verified_rows != v23_rows:
        errors.append("COMPLETENESS_VERIFIED_SET_MISMATCH")
    return admitted_rows, {
        "validationResultSha256": actual_sha,
        "populationCompletenessSha256": completeness_sha if _is_sha256(completeness_sha) else None,
    }


def _validate_provenance(
    parsed: dict[str, Any], actual_sha: str, v23_ids: dict[str, Any], errors: list[str]
) -> dict[str, Any]:
    if parsed.get("contract") != PROVENANCE_CONTRACT:
        errors.append("PROVENANCE_CONTRACT_MISMATCH")
    if parsed.get("contractValid") is not True:
        errors.append("PROVENANCE_CONTRACT_NOT_VALID")
    if parsed.get("errors") != []:
        errors.append("PROVENANCE_ERRORS_NOT_EMPTY")
    if not _authorization_closed(parsed):
        errors.append("PROVENANCE_DOWNSTREAM_AUTHORIZATION_NOT_CLOSED")

    binding = parsed.get("packageBinding")
    binding_sha = parsed.get("packageBindingSha256")
    if not isinstance(binding, dict):
        errors.append("PROVENANCE_PACKAGE_BINDING_OBJECT_REQUIRED")
        binding = {}
    if not _is_sha256(binding_sha):
        errors.append("PROVENANCE_PACKAGE_BINDING_SHA256_INVALID")
    elif binding:
        try:
            if sha256_bytes(canonical_json_bytes(binding)) != binding_sha:
                errors.append("PROVENANCE_PACKAGE_BINDING_CANONICAL_SHA256_MISMATCH")
        except (TypeError, ValueError):
            errors.append("PROVENANCE_PACKAGE_BINDING_CANONICALIZATION_FAILED")

    for field in ("usedHoldoutData", "usedModelOutputs", "derivedFromEvaluatedAudio"):
        if binding.get(field) is not False:
            errors.append(f"PROVENANCE_PACKAGE_{field.upper()}_MUST_BE_FALSE")

    decoder = binding.get("decoder") if isinstance(binding, dict) else None
    if not isinstance(decoder, dict):
        errors.append("PROVENANCE_DECODER_OBJECT_REQUIRED")
        decoder = {}
    decoder_id = decoder.get("decoderId")
    decoder_version = decoder.get("softwareVersion")
    code = decoder.get("code") if isinstance(decoder.get("code"), dict) else {}
    config = decoder.get("configuration") if isinstance(decoder.get("configuration"), dict) else {}
    code_sha = code.get("sha256")
    config_sha = config.get("sha256")
    if not _nonempty(decoder_id):
        errors.append("PROVENANCE_DECODER_ID_REQUIRED")
    if not _nonempty(decoder_version):
        errors.append("PROVENANCE_DECODER_SOFTWARE_VERSION_REQUIRED")
    if not _is_sha256(code_sha):
        errors.append("PROVENANCE_DECODER_CODE_SHA256_INVALID")
    if not _is_sha256(config_sha):
        errors.append("PROVENANCE_DECODER_CONFIGURATION_SHA256_INVALID")

    if v23_ids.get("provenanceResultSha256") != actual_sha:
        errors.append("V23_PROVENANCE_RESULT_SHA256_MISMATCH")
    if v23_ids.get("packageBindingSha256") != binding_sha:
        errors.append("V23_PACKAGE_BINDING_SHA256_MISMATCH")
    if v23_ids.get("decoderConfigurationSha256") != config_sha:
        errors.append("V23_DECODER_CONFIGURATION_SHA256_MISMATCH")

    return {
        "validationResultSha256": actual_sha,
        "packageBindingSha256": binding_sha if _is_sha256(binding_sha) else None,
        "decoderId": decoder_id.strip() if _nonempty(decoder_id) else None,
        "decoderSoftwareVersion": decoder_version.strip() if _nonempty(decoder_version) else None,
        "decoderCodeSha256": code_sha if _is_sha256(code_sha) else None,
        "decoderConfigurationSha256": config_sha if _is_sha256(config_sha) else None,
    }


def replay_population(
    *,
    capture_manifest_v23_validation_result: Any,
    expected_capture_manifest_v23_validation_result_sha256: Any,
    structural_population_completeness_result: Any,
    expected_structural_population_completeness_result_sha256: Any,
    calibration_provenance_result: Any,
    expected_calibration_provenance_result_sha256: Any,
    decoder_code: Any,
    decoder_configuration: Any,
    replay_attempts: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    errors: list[str] = []

    v23, v23_sha, v23_report = _verify_parse_result(
        raw=capture_manifest_v23_validation_result,
        expected_sha256=expected_capture_manifest_v23_validation_result_sha256,
        prefix="V23_RESULT",
        errors=errors,
    )
    completeness, completeness_result_sha, completeness_report = _verify_parse_result(
        raw=structural_population_completeness_result,
        expected_sha256=expected_structural_population_completeness_result_sha256,
        prefix="COMPLETENESS_RESULT",
        errors=errors,
    )
    provenance, provenance_sha, provenance_report = _verify_parse_result(
        raw=calibration_provenance_result,
        expected_sha256=expected_calibration_provenance_result_sha256,
        prefix="PROVENANCE_RESULT",
        errors=errors,
    )

    v23_rows: list[dict[str, str]] = []
    v23_ids: dict[str, Any] = {
        "validationResultSha256": v23_sha,
        "admittedPopulationSha256": None,
        "provenanceResultSha256": None,
        "packageBindingSha256": None,
        "decoderConfigurationSha256": None,
    }
    if v23 is not None and v23_sha is not None:
        v23_rows, v23_ids = _validate_v23(v23, v23_sha, errors)

    completeness_ids = {
        "validationResultSha256": completeness_result_sha,
        "populationCompletenessSha256": None,
    }
    if completeness is not None and completeness_result_sha is not None:
        _, completeness_ids = _validate_completeness(
            completeness, completeness_result_sha, v23_rows, v23_ids, errors
        )

    provenance_ids = {
        "validationResultSha256": provenance_sha,
        "packageBindingSha256": None,
        "decoderId": None,
        "decoderSoftwareVersion": None,
        "decoderCodeSha256": None,
        "decoderConfigurationSha256": None,
    }
    if provenance is not None and provenance_sha is not None:
        provenance_ids = _validate_provenance(provenance, provenance_sha, v23_ids, errors)

    code_report = _source_report(decoder_code, provenance_ids.get("decoderCodeSha256"))
    config_report = _source_report(
        decoder_configuration, provenance_ids.get("decoderConfigurationSha256")
    )
    if not isinstance(decoder_code, bytes):
        errors.append("DECODER_CODE_NOT_BYTES")
    else:
        try:
            decoder_code.decode("utf-8")
        except UnicodeDecodeError:
            errors.append("DECODER_CODE_NOT_UTF8")
    if not code_report["matches"]:
        errors.append("DECODER_CODE_SHA256_MISMATCH")
    if not isinstance(decoder_configuration, bytes):
        errors.append("DECODER_CONFIGURATION_NOT_BYTES")
    if not config_report["matches"]:
        errors.append("DECODER_CONFIGURATION_SHA256_MISMATCH")

    python_runtime = sys.version.split()[0]
    if sys.version_info[:2] != REQUIRED_PYTHON_MAJOR_MINOR:
        errors.append(
            f"PYTHON_RUNTIME_MAJOR_MINOR_MISMATCH:{sys.version_info.major}.{sys.version_info.minor}"
        )

    admitted_set = {
        (row["attemptId"], row["structuralAuditInputsSha256"]) for row in v23_rows
    }
    prepared: list[dict[str, Any]] = []
    seen_attempts: set[str] = set()
    seen_keys: set[tuple[str, str]] = set()
    seen_binding_shas: dict[str, str] = {}

    if not replay_attempts:
        errors.append("REPLAY_ATTEMPTS_REQUIRED")

    for index, attempt in enumerate(replay_attempts):
        if not isinstance(attempt, Mapping):
            errors.append(f"REPLAY_ATTEMPT[{index}]_OBJECT_REQUIRED")
            continue
        binding = attempt.get("structuralAuditInputs")
        expected_binding_sha = attempt.get("expectedStructuralAuditInputsSha256")
        pitch_raw = attempt.get("pitchEvidence")
        birth_raw = attempt.get("birthEvidence")

        if not isinstance(binding, dict):
            errors.append(f"REPLAY_ATTEMPT[{index}]_BINDING_OBJECT_REQUIRED")
            continue
        if binding.get("contract") != BINDING_CONTRACT:
            errors.append(f"REPLAY_ATTEMPT[{index}]_BINDING_CONTRACT_MISMATCH")
        if not _is_sha256(expected_binding_sha):
            errors.append(f"REPLAY_ATTEMPT[{index}]_EXPECTED_BINDING_SHA256_INVALID")
            continue
        try:
            actual_binding_sha = sha256_bytes(canonical_json_bytes(binding))
        except (TypeError, ValueError):
            errors.append(f"REPLAY_ATTEMPT[{index}]_BINDING_CANONICALIZATION_FAILED")
            continue
        if actual_binding_sha != expected_binding_sha:
            errors.append(f"REPLAY_ATTEMPT[{index}]_BINDING_SHA256_MISMATCH")

        attempt_id = binding.get("attemptId")
        if not _nonempty(attempt_id):
            errors.append(f"REPLAY_ATTEMPT[{index}]_ATTEMPT_ID_REQUIRED")
            continue
        attempt_id = attempt_id.strip()
        key = (attempt_id, expected_binding_sha)
        if key not in admitted_set:
            errors.append(f"REPLAY_ATTEMPT[{index}]_NOT_ADMITTED:{attempt_id}:{expected_binding_sha}")
        if attempt_id in seen_attempts:
            errors.append(f"DUPLICATE_REPLAY_ATTEMPT_ID:{attempt_id}")
        seen_attempts.add(attempt_id)
        if key in seen_keys:
            errors.append(f"DUPLICATE_REPLAY_BINDING_KEY:{attempt_id}:{expected_binding_sha}")
        seen_keys.add(key)
        if expected_binding_sha in seen_binding_shas and seen_binding_shas[expected_binding_sha] != attempt_id:
            errors.append(
                f"DUPLICATE_REPLAY_BINDING_SHA256:{expected_binding_sha}:{seen_binding_shas[expected_binding_sha]}:{attempt_id}"
            )
        seen_binding_shas[expected_binding_sha] = attempt_id

        if binding.get("calibrationPackageBindingSha256") != provenance_ids.get(
            "packageBindingSha256"
        ):
            errors.append(f"REPLAY_ATTEMPT[{index}]_PACKAGE_BINDING_SHA256_MISMATCH")
        if binding.get("derivationConfigurationSha256") != provenance_ids.get(
            "decoderConfigurationSha256"
        ):
            errors.append(f"REPLAY_ATTEMPT[{index}]_DERIVATION_CONFIGURATION_SHA256_MISMATCH")

        source_fields = (
            "pitchEvidenceSha256",
            "birthEvidenceSha256",
            "pitchLatchStreamSha256",
            "birthStreamSha256",
        )
        malformed = False
        for field in source_fields:
            if not _is_sha256(binding.get(field)):
                errors.append(f"REPLAY_ATTEMPT[{index}]_{field.upper()}_INVALID")
                malformed = True
        if not isinstance(pitch_raw, bytes):
            errors.append(f"REPLAY_ATTEMPT[{index}]_PITCH_EVIDENCE_NOT_BYTES")
            malformed = True
        elif _is_sha256(binding.get("pitchEvidenceSha256")) and sha256_bytes(pitch_raw) != binding.get(
            "pitchEvidenceSha256"
        ):
            errors.append(f"REPLAY_ATTEMPT[{index}]_PITCH_EVIDENCE_SHA256_MISMATCH")
        if not isinstance(birth_raw, bytes):
            errors.append(f"REPLAY_ATTEMPT[{index}]_BIRTH_EVIDENCE_NOT_BYTES")
            malformed = True
        elif _is_sha256(binding.get("birthEvidenceSha256")) and sha256_bytes(birth_raw) != binding.get(
            "birthEvidenceSha256"
        ):
            errors.append(f"REPLAY_ATTEMPT[{index}]_BIRTH_EVIDENCE_SHA256_MISMATCH")

        if not malformed:
            prepared.append(
                {
                    "attemptId": attempt_id,
                    "structuralAuditInputsSha256": expected_binding_sha,
                    "binding": binding,
                    "pitchEvidence": pitch_raw,
                    "birthEvidence": birth_raw,
                }
            )

    supplied_set = {
        (row["attemptId"], row["structuralAuditInputsSha256"]) for row in prepared
    }
    missing = sorted(admitted_set - supplied_set)
    extra = sorted(supplied_set - admitted_set)
    if missing:
        errors.append("MISSING_REPLAY_ATTEMPTS:" + ",".join(f"{a}:{s}" for a, s in missing))
    if extra:
        errors.append("EXTRA_REPLAY_ATTEMPTS:" + ",".join(f"{a}:{s}" for a, s in extra))
    if len(replay_attempts) != len(v23_rows):
        errors.append(f"REPLAY_ATTEMPT_COUNT_MISMATCH:{len(replay_attempts)}:{len(v23_rows)}")

    replay_rows: list[dict[str, str]] = []
    preexecution_errors = sorted(set(errors))
    if not preexecution_errors:
        assert isinstance(decoder_code, bytes)
        assert isinstance(decoder_configuration, bytes)
        for row in sorted(
            prepared, key=lambda item: (item["attemptId"], item["structuralAuditInputsSha256"])
        ):
            binding = row["binding"]
            with tempfile.TemporaryDirectory(prefix="songsterr-fresh-derivation-replay-") as td:
                root = Path(td)
                decoder_path = root / "decoder.py"
                config_path = root / "configuration.bin"
                pitch_path = root / "pitch-evidence.bin"
                birth_path = root / "birth-evidence.bin"
                pitch_output = root / "pitch-latch-output.bin"
                birth_output = root / "birth-output.bin"
                decoder_path.write_bytes(decoder_code)
                config_path.write_bytes(decoder_configuration)
                pitch_path.write_bytes(row["pitchEvidence"])
                birth_path.write_bytes(row["birthEvidence"])
                command = [
                    sys.executable,
                    "-I",
                    str(decoder_path),
                    "--pitch-evidence",
                    str(pitch_path),
                    "--birth-evidence",
                    str(birth_path),
                    "--configuration",
                    str(config_path),
                    "--pitch-latch-output",
                    str(pitch_output),
                    "--birth-output",
                    str(birth_output),
                ]
                try:
                    completed = subprocess.run(
                        command,
                        cwd=root,
                        env={"LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"},
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=DECODER_TIMEOUT_SECONDS,
                        check=False,
                    )
                except subprocess.TimeoutExpired:
                    errors.append(f"DECODER_TIMEOUT:{row['attemptId']}")
                    continue
                if completed.returncode != 0:
                    errors.append(f"DECODER_NONZERO_EXIT:{row['attemptId']}:{completed.returncode}")
                    continue
                if not pitch_output.exists() or pitch_output.is_symlink() or not pitch_output.is_file():
                    errors.append(f"DECODER_PITCH_LATCH_OUTPUT_MISSING_OR_INVALID:{row['attemptId']}")
                    continue
                if not birth_output.exists() or birth_output.is_symlink() or not birth_output.is_file():
                    errors.append(f"DECODER_BIRTH_OUTPUT_MISSING_OR_INVALID:{row['attemptId']}")
                    continue
                try:
                    pitch_bytes = pitch_output.read_bytes()
                    birth_bytes = birth_output.read_bytes()
                except OSError as exc:
                    errors.append(f"DECODER_OUTPUT_READ_FAILED:{row['attemptId']}:{type(exc).__name__}")
                    continue
                pitch_sha = sha256_bytes(pitch_bytes)
                birth_sha = sha256_bytes(birth_bytes)
                if pitch_sha != binding["pitchLatchStreamSha256"]:
                    errors.append(f"REPLAYED_PITCH_LATCH_SHA256_MISMATCH:{row['attemptId']}")
                if birth_sha != binding["birthStreamSha256"]:
                    errors.append(f"REPLAYED_BIRTH_SHA256_MISMATCH:{row['attemptId']}")
                replay_rows.append(
                    {
                        "attemptId": row["attemptId"],
                        "structuralAuditInputsSha256": row["structuralAuditInputsSha256"],
                        "pitchEvidenceSha256": binding["pitchEvidenceSha256"],
                        "birthEvidenceSha256": binding["birthEvidenceSha256"],
                        "replayedPitchLatchStreamSha256": pitch_sha,
                        "replayedBirthStreamSha256": birth_sha,
                    }
                )

    replay_rows.sort(key=lambda item: (item["attemptId"], item["structuralAuditInputsSha256"]))
    errors = sorted(set(errors))
    valid = bool(
        not errors
        and admitted_set
        and len(replay_rows) == len(admitted_set)
        and {
            (row["attemptId"], row["structuralAuditInputsSha256"]) for row in replay_rows
        }
        == admitted_set
    )

    population_sha: str | None = None
    if valid:
        population_sha = sha256_bytes(
            canonical_json_bytes(
                {
                    "populationIdentityVersion": POPULATION_IDENTITY_VERSION,
                    "captureManifestV23ValidationResultSha256": v23_ids["validationResultSha256"],
                    "captureManifestV23AdmittedPopulationSha256": v23_ids["admittedPopulationSha256"],
                    "structuralPopulationCompletenessResultSha256": completeness_ids[
                        "validationResultSha256"
                    ],
                    "structuralPopulationCompletenessSha256": completeness_ids[
                        "populationCompletenessSha256"
                    ],
                    "calibrationProvenanceResultSha256": provenance_ids[
                        "validationResultSha256"
                    ],
                    "calibrationPackageBindingSha256": provenance_ids[
                        "packageBindingSha256"
                    ],
                    "decoderCodeSha256": provenance_ids["decoderCodeSha256"],
                    "decoderConfigurationSha256": provenance_ids[
                        "decoderConfigurationSha256"
                    ],
                    "attemptReplays": replay_rows,
                }
            )
        )

    return {
        "contract": CONTRACT,
        "contractValid": valid,
        "errors": errors,
        "captureManifestV23ValidationSourceSha256": v23_report,
        "captureManifestV23ValidationResultSha256": v23_ids.get("validationResultSha256"),
        "captureManifestV23AdmittedPopulationSha256": v23_ids.get("admittedPopulationSha256"),
        "structuralPopulationCompletenessSourceSha256": completeness_report,
        "structuralPopulationCompletenessResultSha256": completeness_ids.get(
            "validationResultSha256"
        ),
        "structuralPopulationCompletenessSha256": completeness_ids.get(
            "populationCompletenessSha256"
        ),
        "calibrationProvenanceSourceSha256": provenance_report,
        "calibrationProvenanceResultSha256": provenance_ids.get("validationResultSha256"),
        "calibrationPackageBindingSha256": provenance_ids.get("packageBindingSha256"),
        "decoderId": provenance_ids.get("decoderId"),
        "decoderSoftwareVersion": provenance_ids.get("decoderSoftwareVersion"),
        "decoderCodeSha256": provenance_ids.get("decoderCodeSha256"),
        "decoderConfigurationSha256": provenance_ids.get("decoderConfigurationSha256"),
        "decoderCodeSourceSha256": code_report,
        "decoderConfigurationSourceSha256": config_report,
        "pythonRuntimeVersion": python_runtime,
        "admittedBindingCount": len(v23_rows),
        "submittedReplayCount": len(replay_attempts),
        "verifiedReplayCount": len(replay_rows) if valid else 0,
        "attemptReplays": replay_rows if valid else [],
        "populationIdentityVersion": POPULATION_IDENTITY_VERSION,
        "populationDerivationReplaySha256": population_sha,
        "populationDerivationReplayEstablished": valid,
        **_closed_authorization(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v23-result", required=True)
    parser.add_argument("--v23-result-sha256", required=True)
    parser.add_argument("--population-completeness-result", required=True)
    parser.add_argument("--population-completeness-result-sha256", required=True)
    parser.add_argument("--provenance-result", required=True)
    parser.add_argument("--provenance-result-sha256", required=True)
    parser.add_argument("--decoder-code", required=True)
    parser.add_argument("--decoder-configuration", required=True)
    parser.add_argument("--attempt-spec", action="append", default=[])
    parser.add_argument("--output")
    return parser.parse_args()


def _load_attempt_spec(path: str) -> dict[str, Any]:
    spec_path = Path(path)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if not isinstance(spec, dict):
        raise ValueError("attempt spec must be a JSON object")
    base = spec_path.parent
    binding_path = base / spec["structuralAuditInputsPath"]
    pitch_path = base / spec["pitchEvidencePath"]
    birth_path = base / spec["birthEvidencePath"]
    return {
        "structuralAuditInputs": json.loads(binding_path.read_text(encoding="utf-8")),
        "expectedStructuralAuditInputsSha256": spec["structuralAuditInputsSha256"],
        "pitchEvidence": pitch_path.read_bytes(),
        "birthEvidence": birth_path.read_bytes(),
    }


def main() -> int:
    args = parse_args()
    try:
        attempts = [_load_attempt_spec(path) for path in args.attempt_spec]
    except (OSError, KeyError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"contract": CONTRACT, "contractValid": False, "errors": [f"ATTEMPT_SPEC_LOAD_FAILED:{type(exc).__name__}"]}, sort_keys=True, separators=(",", ":")))
        return 2

    result = replay_population(
        capture_manifest_v23_validation_result=Path(args.v23_result).read_bytes(),
        expected_capture_manifest_v23_validation_result_sha256=args.v23_result_sha256,
        structural_population_completeness_result=Path(
            args.population_completeness_result
        ).read_bytes(),
        expected_structural_population_completeness_result_sha256=args.population_completeness_result_sha256,
        calibration_provenance_result=Path(args.provenance_result).read_bytes(),
        expected_calibration_provenance_result_sha256=args.provenance_result_sha256,
        decoder_code=Path(args.decoder_code).read_bytes(),
        decoder_configuration=Path(args.decoder_configuration).read_bytes(),
        replay_attempts=attempts,
    )
    rendered = canonical_json_bytes(result) + b"\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(rendered)
    print(rendered.decode("utf-8"), end="")
    return 0 if result["populationDerivationReplayEstablished"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
