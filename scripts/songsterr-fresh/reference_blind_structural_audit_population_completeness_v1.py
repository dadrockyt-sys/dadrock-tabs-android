#!/usr/bin/env python3
"""Population completeness aggregator for immutable Structural Audit V1.2 results.

Result-only software. This module never opens structural source files, evaluated
audio, calibration sources, or model outputs. All supplied result byte streams
are SHA-256 verified before semantic parsing according to the frozen contract.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

CONTRACT = (
    "songsterr-fresh-purpose-built-reference-blind-structural-audit-"
    "population-completeness-v1"
)
V23_RESULT_CONTRACT = "songsterr-fresh-purpose-built-capture-manifest-v2.3"
V23_POPULATION_IDENTITY_VERSION = (
    "capture-manifest-v2.3-structural-audit-input-binding-v1"
)
STRUCTURAL_INPUT_BINDING_CONTRACT = (
    "songsterr-fresh-purpose-built-structural-audit-input-binding-v1"
)
V12_RESULT_CONTRACT = (
    "songsterr-fresh-purpose-built-reference-blind-structural-audit-v1.2"
)
POPULATION_IDENTITY_VERSION = (
    "reference-blind-structural-audit-population-completeness-v1"
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


def _canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


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


def _auth_errors(prefix: str, value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in (
        "realCalibrationAuthorized",
        "realHoldoutCaptureAuthorized",
        "basicPitchAuthorized",
        "v6Authorized",
        "correctnessAuthorized",
        "modelValidationComplete",
        "mayAdvanceDelivery",
    ):
        if value.get(key) is not False:
            errors.append(f"{prefix}_{key.upper()}_MUST_BE_FALSE")
    if value.get("customerEligibleEvents") != 0:
        errors.append(f"{prefix}_CUSTOMER_ELIGIBLE_EVENTS_MUST_BE_ZERO")
    return errors


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


def _parse_json_bytes(raw: bytes, prefix: str, errors: list[str]) -> Any:
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"{prefix}_INVALID_JSON:{type(exc).__name__}")
        return None


def _validate_v23_semantics(
    parsed: Any,
    verified_sha: str,
    errors: list[str],
) -> tuple[str | None, list[dict[str, str]]]:
    if not isinstance(parsed, dict):
        errors.append("V23_RESULT_OBJECT_REQUIRED")
        return None, []
    if parsed.get("contract") != V23_RESULT_CONTRACT:
        errors.append("V23_RESULT_CONTRACT_MISMATCH")
    if parsed.get("contractValid") is not True:
        errors.append("V23_RESULT_CONTRACT_NOT_VALID")
    if parsed.get("errors") != []:
        errors.append("V23_RESULT_ERRORS_NOT_EMPTY")
    if parsed.get("v23SemanticGuardPassed") is not True:
        errors.append("V23_SEMANTIC_GUARD_NOT_PASSED")
    if parsed.get("mayAdvanceToReferenceBlindStructuralAudit") is not True:
        errors.append("V23_MAY_ADVANCE_NOT_TRUE")
    if parsed.get("populationIdentityVersion") != V23_POPULATION_IDENTITY_VERSION:
        errors.append("V23_POPULATION_IDENTITY_VERSION_MISMATCH")

    population_sha = parsed.get("admittedPopulationManifestSha256")
    if not _is_sha256(population_sha):
        errors.append("V23_ADMITTED_POPULATION_SHA256_INVALID")
        population_sha = None

    if parsed.get("structuralAuditInputBindingContract") != STRUCTURAL_INPUT_BINDING_CONTRACT:
        errors.append("V23_STRUCTURAL_BINDING_CONTRACT_MISMATCH")

    bindings = parsed.get("structuralAuditInputBindings")
    count = parsed.get("structuralAuditInputBindingCount")
    if not isinstance(bindings, list):
        errors.append("V23_STRUCTURAL_BINDINGS_LIST_REQUIRED")
        bindings = []
    if (
        not isinstance(count, int)
        or isinstance(count, bool)
        or count != len(bindings)
        or count < 1
    ):
        errors.append("V23_STRUCTURAL_BINDING_COUNT_INVALID")

    rows: list[dict[str, str]] = []
    seen_attempts: set[str] = set()
    seen_keys: set[tuple[str, str]] = set()
    for index, entry in enumerate(bindings):
        if not isinstance(entry, dict):
            errors.append(f"V23_BINDING[{index}]_OBJECT_REQUIRED")
            continue
        attempt_id = entry.get("attemptId")
        binding_sha = entry.get("structuralAuditInputsSha256")
        if not _nonempty(attempt_id):
            errors.append(f"V23_BINDING[{index}]_ATTEMPT_ID_REQUIRED")
            continue
        attempt_id = attempt_id.strip()
        if not _is_sha256(binding_sha):
            errors.append(f"V23_BINDING[{index}]_SHA256_INVALID")
            continue
        key = (attempt_id, binding_sha)
        if attempt_id in seen_attempts:
            errors.append(f"V23_DUPLICATE_ATTEMPT_ID:{attempt_id}")
        if key in seen_keys:
            errors.append(f"V23_DUPLICATE_BINDING_KEY:{attempt_id}:{binding_sha}")
        seen_attempts.add(attempt_id)
        seen_keys.add(key)
        rows.append(
            {
                "attemptId": attempt_id,
                "structuralAuditInputsSha256": binding_sha,
            }
        )

    errors.extend(_auth_errors("V23", parsed))
    rows.sort(key=lambda row: (row["attemptId"], row["structuralAuditInputsSha256"]))
    return population_sha, rows


def _validate_v12_semantics(
    parsed: Any,
    result_sha: str,
    v23_result_sha: str,
    v23_population_sha: str | None,
    index: int,
    errors: list[str],
) -> dict[str, str] | None:
    prefix = f"V12[{index}]"
    if not isinstance(parsed, dict):
        errors.append(f"{prefix}_RESULT_OBJECT_REQUIRED")
        return None
    if parsed.get("contract") != V12_RESULT_CONTRACT:
        errors.append(f"{prefix}_CONTRACT_MISMATCH")
    if parsed.get("contractValid") is not True:
        errors.append(f"{prefix}_CONTRACT_NOT_VALID")
    if parsed.get("errors") != []:
        errors.append(f"{prefix}_ERRORS_NOT_EMPTY")
    if parsed.get("datasetStructurallySuitable") is not True:
        errors.append(f"{prefix}_DATASET_STRUCTURALLY_SUITABLE_NOT_TRUE")
    if parsed.get("authoritativeStructuralSuitabilityEstablished") is not True:
        errors.append(f"{prefix}_AUTHORITATIVE_SUITABILITY_NOT_TRUE")
    if parsed.get("capturePopulationBindingViolationCount") != 0:
        errors.append(f"{prefix}_CAPTURE_POPULATION_BINDING_VIOLATIONS_NONZERO")
    if parsed.get("calibrationProvenanceBridgeViolationCount") != 0:
        errors.append(f"{prefix}_CALIBRATION_PROVENANCE_BRIDGE_VIOLATIONS_NONZERO")

    blockers = parsed.get("blockerCounts")
    if not isinstance(blockers, dict):
        errors.append(f"{prefix}_BLOCKER_COUNTS_OBJECT_REQUIRED")
    else:
        for key, value in blockers.items():
            if not isinstance(value, int) or isinstance(value, bool) or value != 0:
                errors.append(f"{prefix}_BLOCKER_NONZERO:{key}:{value!r}")

    attempt_id = parsed.get("attemptId")
    binding_sha = parsed.get("structuralAuditInputsSha256")
    derived_sha = parsed.get("derivedPopulationSha256")
    if not _nonempty(attempt_id):
        errors.append(f"{prefix}_ATTEMPT_ID_REQUIRED")
        attempt_id = None
    else:
        attempt_id = attempt_id.strip()
    if not _is_sha256(binding_sha):
        errors.append(f"{prefix}_STRUCTURAL_BINDING_SHA256_INVALID")
        binding_sha = None
    if not _is_sha256(derived_sha):
        errors.append(f"{prefix}_DERIVED_POPULATION_SHA256_INVALID")
        derived_sha = None

    if parsed.get("captureManifestV23ValidationResultSha256") != v23_result_sha:
        errors.append(f"{prefix}_V23_RESULT_SHA256_MISMATCH")
    if (
        v23_population_sha is None
        or parsed.get("captureManifestV23AdmittedPopulationSha256") != v23_population_sha
    ):
        errors.append(f"{prefix}_V23_POPULATION_SHA256_MISMATCH")

    errors.extend(_auth_errors(prefix, parsed))
    if attempt_id is None or binding_sha is None or derived_sha is None:
        return None
    return {
        "attemptId": attempt_id,
        "structuralAuditInputsSha256": binding_sha,
        "v12ValidationResultSha256": result_sha,
        "v12DerivedPopulationSha256": derived_sha,
    }


def aggregate_population(
    *,
    capture_manifest_v23_validation_result: Any,
    expected_capture_manifest_v23_validation_result_sha256: Any,
    v12_validation_results: Iterable[tuple[Any, Any]],
) -> dict[str, Any]:
    errors: list[str] = []
    v23_report = _source_report(
        capture_manifest_v23_validation_result,
        expected_capture_manifest_v23_validation_result_sha256,
    )

    # V2.3 hash gate before V2.3 parse.
    v23_hash_ok = True
    if not isinstance(capture_manifest_v23_validation_result, bytes):
        errors.append("V23_RESULT_NOT_BYTES")
        v23_hash_ok = False
    if not _is_sha256(expected_capture_manifest_v23_validation_result_sha256):
        errors.append("V23_EXPECTED_SHA256_INVALID")
        v23_hash_ok = False
    v23_actual_sha = v23_report["actual"]
    if (
        isinstance(capture_manifest_v23_validation_result, bytes)
        and _is_sha256(expected_capture_manifest_v23_validation_result_sha256)
        and v23_actual_sha != expected_capture_manifest_v23_validation_result_sha256
    ):
        errors.append("V23_RESULT_SHA256_MISMATCH")
        v23_hash_ok = False

    v23_parsed = None
    v23_population_sha: str | None = None
    admitted_rows: list[dict[str, str]] = []
    if v23_hash_ok:
        v23_parsed = _parse_json_bytes(
            capture_manifest_v23_validation_result,
            "V23_RESULT",
            errors,
        )
        if v23_parsed is not None:
            v23_population_sha, admitted_rows = _validate_v23_semantics(
                v23_parsed,
                v23_actual_sha,
                errors,
            )

    # Materialize collection once. The entire V1.2 collection passes raw/hash
    # gates before ANY V1.2 semantic parse is attempted.
    result_inputs = list(v12_validation_results)
    reports: list[dict[str, Any]] = []
    all_v12_hashes_ok = True
    verified_hashes: list[str] = []
    for index, pair in enumerate(result_inputs):
        if not isinstance(pair, tuple) or len(pair) != 2:
            errors.append(f"V12[{index}]_INPUT_PAIR_REQUIRED")
            reports.append({"expected": None, "actual": None, "matches": False})
            all_v12_hashes_ok = False
            continue
        raw, expected = pair
        report = _source_report(raw, expected)
        reports.append(report)
        if not isinstance(raw, bytes):
            errors.append(f"V12[{index}]_RESULT_NOT_BYTES")
            all_v12_hashes_ok = False
        if not _is_sha256(expected):
            errors.append(f"V12[{index}]_EXPECTED_SHA256_INVALID")
            all_v12_hashes_ok = False
        if isinstance(raw, bytes) and _is_sha256(expected) and report["actual"] != expected:
            errors.append(f"V12[{index}]_RESULT_SHA256_MISMATCH")
            all_v12_hashes_ok = False
        if report["actual"] is not None:
            verified_hashes.append(report["actual"])

    if not result_inputs:
        errors.append("V12_RESULTS_REQUIRED")
        all_v12_hashes_ok = False

    if len(verified_hashes) != len(set(verified_hashes)):
        errors.append("DUPLICATE_V12_RESULT_SHA256")

    verified_rows: list[dict[str, str]] = []
    # Semantic parse of V1.2 streams is permitted only if every V1.2 hash gate passed.
    if all_v12_hashes_ok and v23_actual_sha is not None:
        for index, pair in enumerate(result_inputs):
            raw, _expected = pair
            parsed = _parse_json_bytes(raw, f"V12[{index}]_RESULT", errors)
            if parsed is None:
                continue
            row = _validate_v12_semantics(
                parsed,
                reports[index]["actual"],
                v23_actual_sha,
                v23_population_sha,
                index,
                errors,
            )
            if row is not None:
                verified_rows.append(row)

    # Duplicate checks and exact set equality.
    v12_attempt_ids = [row["attemptId"] for row in verified_rows]
    if len(v12_attempt_ids) != len(set(v12_attempt_ids)):
        errors.append("DUPLICATE_V12_ATTEMPT_ID")
    v12_keys = [
        (row["attemptId"], row["structuralAuditInputsSha256"])
        for row in verified_rows
    ]
    if len(v12_keys) != len(set(v12_keys)):
        errors.append("DUPLICATE_V12_BINDING_KEY")

    admitted_keys = {
        (row["attemptId"], row["structuralAuditInputsSha256"])
        for row in admitted_rows
    }
    verified_key_set = set(v12_keys)
    for attempt_id, binding_sha in sorted(admitted_keys - verified_key_set):
        errors.append(f"MISSING_V12_AUDIT:{attempt_id}:{binding_sha}")
    for attempt_id, binding_sha in sorted(verified_key_set - admitted_keys):
        errors.append(f"EXTRA_V12_AUDIT:{attempt_id}:{binding_sha}")

    admitted_key_rows = [
        {"attemptId": attempt_id, "structuralAuditInputsSha256": binding_sha}
        for attempt_id, binding_sha in sorted(admitted_keys)
    ]
    verified_key_rows = [
        {"attemptId": attempt_id, "structuralAuditInputsSha256": binding_sha}
        for attempt_id, binding_sha in sorted(verified_key_set)
    ]
    verified_rows.sort(
        key=lambda row: (row["attemptId"], row["structuralAuditInputsSha256"])
    )

    merged_errors = sorted(set(errors))
    contract_valid = bool(
        not merged_errors
        and v23_hash_ok
        and all_v12_hashes_ok
        and len(admitted_keys) >= 1
        and admitted_keys == verified_key_set
        and len(verified_rows) == len(admitted_keys)
    )
    completeness_sha = None
    if contract_valid and v23_actual_sha is not None and v23_population_sha is not None:
        completeness_sha = _canonical_sha256(
            {
                "populationIdentityVersion": POPULATION_IDENTITY_VERSION,
                "captureManifestV23ValidationResultSha256": v23_actual_sha,
                "captureManifestV23AdmittedPopulationSha256": v23_population_sha,
                "verifiedAttemptResults": verified_rows,
            }
        )

    return {
        "contract": CONTRACT,
        "contractValid": contract_valid,
        "errors": merged_errors,
        "captureManifestV23ValidationSourceSha256": v23_report,
        "captureManifestV23ValidationResultSha256": (
            v23_actual_sha if v23_hash_ok else None
        ),
        "captureManifestV23AdmittedPopulationSha256": v23_population_sha,
        "v12ValidationSourceSha256": reports,
        "admittedBindingCount": len(admitted_keys),
        "verifiedV12ResultCount": len(verified_rows),
        "admittedBindingKeys": admitted_key_rows,
        "verifiedV12BindingKeys": verified_key_rows,
        "verifiedAttemptResults": verified_rows,
        "populationIdentityVersion": POPULATION_IDENTITY_VERSION,
        "populationStructuralCompletenessSha256": completeness_sha,
        "populationStructurallySuitable": contract_valid,
        "populationStructuralCompletenessEstablished": contract_valid,
        **_closed_authorization(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-manifest-v23-result", required=True)
    parser.add_argument("--capture-manifest-v23-result-sha256", required=True)
    parser.add_argument("--v12-result", action="append", required=True)
    parser.add_argument("--v12-result-sha256", action="append", required=True)
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if len(args.v12_result) != len(args.v12_result_sha256):
        raise SystemExit("--v12-result and --v12-result-sha256 counts must match")
    v23_bytes = Path(args.capture_manifest_v23_result).read_bytes()
    v12_inputs = [
        (Path(path).read_bytes(), expected)
        for path, expected in zip(args.v12_result, args.v12_result_sha256)
    ]
    result = aggregate_population(
        capture_manifest_v23_validation_result=v23_bytes,
        expected_capture_manifest_v23_validation_result_sha256=(
            args.capture_manifest_v23_result_sha256
        ),
        v12_validation_results=v12_inputs,
    )
    rendered = canonical_json_bytes(result) + b"\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(rendered)
    print(rendered.decode("utf-8"), end="")
    return 0 if result["contractValid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
