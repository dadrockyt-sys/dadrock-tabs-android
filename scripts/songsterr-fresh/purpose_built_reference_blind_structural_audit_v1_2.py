#!/usr/bin/env python3
"""Reference-blind structural audit V1.2 capture-population identity bridge.

V1.2 is an additive wrapper over V1.1. It preserves all V1/V1.1 structural
and provenance semantics, hash-verifies one successful Capture Manifest V2.3
validation result before parsing it, and proves that the actual structural
source bytes belong to the admitted V2.3 performance/binding/population.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent
V11_PATH = HERE / "purpose_built_reference_blind_structural_audit_v1_1.py"
spec = importlib.util.spec_from_file_location(
    "purpose_built_reference_blind_structural_audit_v1_1", V11_PATH
)
assert spec and spec.loader
v11 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v11)

CONTRACT = "songsterr-fresh-purpose-built-reference-blind-structural-audit-v1.2"
V23_RESULT_CONTRACT = "songsterr-fresh-purpose-built-capture-manifest-v2.3"
STRUCTURAL_INPUT_BINDING_CONTRACT = (
    "songsterr-fresh-purpose-built-structural-audit-input-binding-v1"
)
V23_POPULATION_IDENTITY_VERSION = (
    "capture-manifest-v2.3-structural-audit-input-binding-v1"
)
POPULATION_IDENTITY_VERSION = (
    "reference-blind-structural-audit-v1.2-capture-population-binding-v1"
)

SOURCE_BINDING_FIELDS = {
    "hardware": "hardwareSourceSha256",
    "birth": "birthStreamSha256",
    "pitchLatch": "pitchLatchStreamSha256",
    "clockSync": "clockSyncSourceSha256",
}


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


def _v23_source_report(raw: Any, expected_sha256: Any) -> dict[str, Any]:
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


def _validate_v23_result(
    *,
    raw: Any,
    expected_sha256: Any,
    expected_population_sha256: Any,
    binding: Any,
    expected_binding_sha256: Any,
    inherited: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any] | None, list[str]]:
    details: dict[str, Any] = {
        "captureManifestV23ValidationSourceSha256": _v23_source_report(
            raw, expected_sha256
        ),
        "captureManifestV23ValidationResultSha256": None,
        "captureManifestV23AdmittedPopulationSha256": None,
        "structuralAuditInputsSha256": None,
        "configurationSha256": None,
        "instrumentSetupSha256": None,
        "attemptId": None,
        "slotId": None,
        "underlyingPerformanceId": None,
        "playerId": None,
        "exerciseId": None,
        "category": None,
    }
    errors: list[str] = []

    if not isinstance(raw, bytes):
        errors.append("CAPTURE_MANIFEST_V23_RESULT_NOT_BYTES")
        return details, None, errors
    if not _is_sha256(expected_sha256):
        errors.append("CAPTURE_MANIFEST_V23_EXPECTED_SHA256_INVALID")
        return details, None, errors
    actual_sha = details["captureManifestV23ValidationSourceSha256"]["actual"]
    if actual_sha != expected_sha256:
        errors.append("CAPTURE_MANIFEST_V23_RESULT_SHA256_MISMATCH")
        return details, None, errors
    details["captureManifestV23ValidationResultSha256"] = actual_sha

    if not _is_sha256(expected_population_sha256):
        errors.append("CAPTURE_MANIFEST_V23_EXPECTED_POPULATION_SHA256_INVALID")
    if not isinstance(binding, dict):
        errors.append("STRUCTURAL_AUDIT_INPUTS_OBJECT_REQUIRED")
        return details, None, errors
    if not _is_sha256(expected_binding_sha256):
        errors.append("STRUCTURAL_AUDIT_INPUTS_EXPECTED_SHA256_INVALID")
    else:
        try:
            actual_binding_sha = _canonical_sha256(binding)
        except (TypeError, ValueError):
            errors.append("STRUCTURAL_AUDIT_INPUTS_CANONICALIZATION_FAILED")
        else:
            if actual_binding_sha != expected_binding_sha256:
                errors.append("STRUCTURAL_AUDIT_INPUTS_SHA256_MISMATCH")
            else:
                details["structuralAuditInputsSha256"] = actual_binding_sha

    if binding.get("contract") != STRUCTURAL_INPUT_BINDING_CONTRACT:
        errors.append("STRUCTURAL_AUDIT_INPUTS_CONTRACT_MISMATCH")

    for field in (
        "attemptId",
        "slotId",
        "underlyingPerformanceId",
        "playerId",
        "exerciseId",
        "category",
    ):
        value = binding.get(field)
        if not _nonempty(value):
            errors.append(f"STRUCTURAL_AUDIT_INPUTS_{field.upper()}_REQUIRED")
        else:
            details[field] = value.strip()

    for field in ("configurationSha256", "instrumentSetupSha256"):
        value = binding.get(field)
        if not _is_sha256(value):
            errors.append(f"STRUCTURAL_AUDIT_INPUTS_{field.upper()}_INVALID")
        else:
            details[field] = value

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"CAPTURE_MANIFEST_V23_RESULT_INVALID_JSON:{type(exc).__name__}")
        return details, None, errors
    if not isinstance(parsed, dict):
        errors.append("CAPTURE_MANIFEST_V23_RESULT_OBJECT_REQUIRED")
        return details, None, errors

    if parsed.get("contract") != V23_RESULT_CONTRACT:
        errors.append("CAPTURE_MANIFEST_V23_RESULT_CONTRACT_MISMATCH")
    if parsed.get("contractValid") is not True:
        errors.append("CAPTURE_MANIFEST_V23_RESULT_CONTRACT_NOT_VALID")
    if parsed.get("errors") != []:
        errors.append("CAPTURE_MANIFEST_V23_RESULT_ERRORS_NOT_EMPTY")
    if parsed.get("v23SemanticGuardPassed") is not True:
        errors.append("CAPTURE_MANIFEST_V23_SEMANTIC_GUARD_NOT_PASSED")
    if parsed.get("mayAdvanceToReferenceBlindStructuralAudit") is not True:
        errors.append("CAPTURE_MANIFEST_V23_MAY_ADVANCE_NOT_TRUE")
    if parsed.get("populationIdentityVersion") != V23_POPULATION_IDENTITY_VERSION:
        errors.append("CAPTURE_MANIFEST_V23_POPULATION_IDENTITY_VERSION_MISMATCH")

    parsed_population_sha = parsed.get("admittedPopulationManifestSha256")
    if not _is_sha256(parsed_population_sha):
        errors.append("CAPTURE_MANIFEST_V23_POPULATION_SHA256_INVALID")
    elif (
        _is_sha256(expected_population_sha256)
        and parsed_population_sha != expected_population_sha256
    ):
        errors.append("CAPTURE_MANIFEST_V23_POPULATION_SHA256_MISMATCH")
    else:
        details["captureManifestV23AdmittedPopulationSha256"] = parsed_population_sha

    if parsed.get("structuralAuditInputBindingContract") != STRUCTURAL_INPUT_BINDING_CONTRACT:
        errors.append("CAPTURE_MANIFEST_V23_BINDING_CONTRACT_MISMATCH")

    binding_map = parsed.get("structuralAuditInputBindings")
    binding_count = parsed.get("structuralAuditInputBindingCount")
    if not isinstance(binding_map, list):
        errors.append("CAPTURE_MANIFEST_V23_BINDING_MAP_LIST_REQUIRED")
        binding_map = []
    if (
        not isinstance(binding_count, int)
        or isinstance(binding_count, bool)
        or binding_count != len(binding_map)
    ):
        errors.append("CAPTURE_MANIFEST_V23_BINDING_COUNT_MISMATCH")

    attempt_id = binding.get("attemptId")
    matching = [
        entry
        for entry in binding_map
        if isinstance(entry, dict) and entry.get("attemptId") == attempt_id
    ]
    if len(matching) != 1:
        errors.append("CAPTURE_MANIFEST_V23_AUDITED_ATTEMPT_BINDING_ENTRY_COUNT_INVALID")
    elif expected_binding_sha256 is not None and matching[0].get(
        "structuralAuditInputsSha256"
    ) != expected_binding_sha256:
        errors.append("CAPTURE_MANIFEST_V23_AUDITED_ATTEMPT_BINDING_SHA256_MISMATCH")

    inherited_provenance_sha = inherited.get("calibrationProvenanceResultSha256")
    inherited_package_sha = inherited.get("calibrationPackageBindingSha256")
    inherited_decoder_configuration_sha = inherited.get(
        "calibrationPackageDecoderConfigurationSha256"
    )
    if parsed.get("calibrationPackageValidationResultSha256") != inherited_provenance_sha:
        errors.append("CAPTURE_MANIFEST_V23_PROVENANCE_RESULT_SHA256_MISMATCH")
    if parsed.get("calibrationPackageBindingSha256") != inherited_package_sha:
        errors.append("CAPTURE_MANIFEST_V23_PACKAGE_BINDING_SHA256_MISMATCH")
    if (
        parsed.get("calibrationPackageDecoderConfigurationSha256")
        != inherited_decoder_configuration_sha
    ):
        errors.append("CAPTURE_MANIFEST_V23_DECODER_CONFIGURATION_SHA256_MISMATCH")

    for key in (
        "realCalibrationAuthorized",
        "realHoldoutCaptureAuthorized",
        "basicPitchAuthorized",
        "v6Authorized",
        "correctnessAuthorized",
        "modelValidationComplete",
        "mayAdvanceDelivery",
    ):
        if parsed.get(key) is not False:
            errors.append(f"CAPTURE_MANIFEST_V23_{key.upper()}_MUST_BE_FALSE")
    if parsed.get("customerEligibleEvents") != 0:
        errors.append("CAPTURE_MANIFEST_V23_CUSTOMER_ELIGIBLE_EVENTS_MUST_BE_ZERO")

    if binding.get("calibrationPackageBindingSha256") != inherited_package_sha:
        errors.append("STRUCTURAL_AUDIT_INPUTS_PACKAGE_BINDING_SHA256_MISMATCH")
    if binding.get("derivationConfigurationSha256") != inherited_decoder_configuration_sha:
        errors.append("STRUCTURAL_AUDIT_INPUTS_DERIVATION_CONFIGURATION_SHA256_MISMATCH")

    return details, parsed, errors


def _validate_source_and_declaration_links(
    *,
    raw_sources: Mapping[str, bytes],
    inherited: dict[str, Any],
    binding: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    source_report = inherited.get("sourceSha256")
    if not isinstance(source_report, dict):
        errors.append("INHERITED_V11_SOURCE_SHA256_REPORT_REQUIRED")
        return errors

    for source_name, binding_field in SOURCE_BINDING_FIELDS.items():
        source = source_report.get(source_name)
        actual = source.get("actual") if isinstance(source, dict) else None
        if actual != binding.get(binding_field):
            errors.append(
                f"STRUCTURAL_AUDIT_INPUTS_{binding_field.upper()}_ACTUAL_MISMATCH"
            )

    # Only compare parsed declarations after V1.1 accepted the exact source bytes.
    if inherited.get("contractValid") is not True:
        return errors
    try:
        hardware = json.loads(raw_sources["hardware"].decode("utf-8"))
        clock_sync = json.loads(raw_sources["clockSync"].decode("utf-8"))
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError):
        errors.append("V11_ACCEPTED_SOURCE_REPARSE_FAILED")
        return errors

    if not isinstance(hardware, dict) or not isinstance(clock_sync, dict):
        errors.append("V11_ACCEPTED_SOURCE_DECLARATION_OBJECT_REQUIRED")
        return errors

    comparisons = (
        ("CONFIGURATION_ID", hardware.get("configurationId"), binding.get("configurationId")),
        ("CALIBRATION_ID", hardware.get("calibrationId"), binding.get("calibrationId")),
        ("OPEN_STRING_MIDI", hardware.get("openStringMidi"), binding.get("openStringMidi")),
        (
            "EVENT_SEMANTICS_VERSION",
            hardware.get("eventSemanticsVersion"),
            binding.get("eventSemanticsVersion"),
        ),
        ("CLOCK_SYNC_ID", clock_sync.get("syncId"), binding.get("clockSyncId")),
    )
    for label, actual, expected in comparisons:
        if actual != expected:
            errors.append(f"STRUCTURAL_DECLARATION_{label}_MISMATCH")
    return errors


def audit_raw_sources_v1_2(
    *,
    raw_sources: Mapping[str, bytes],
    expected_sha256: Mapping[str, str],
    calibration_provenance_result: Any,
    expected_calibration_provenance_result_sha256: Any,
    declared_provenance_result_sha256: Any,
    declared_calibration_package_binding_sha256: Any,
    capture_manifest_v23_validation_result: Any,
    expected_capture_manifest_v23_validation_result_sha256: Any,
    structural_audit_inputs: Any,
    expected_structural_audit_inputs_sha256: Any,
    expected_capture_manifest_v23_admitted_population_sha256: Any,
) -> dict[str, Any]:
    inherited = v11.audit_raw_sources_v1_1(
        raw_sources=raw_sources,
        expected_sha256=expected_sha256,
        calibration_provenance_result=calibration_provenance_result,
        expected_calibration_provenance_result_sha256=expected_calibration_provenance_result_sha256,
        declared_provenance_result_sha256=declared_provenance_result_sha256,
        declared_calibration_package_binding_sha256=declared_calibration_package_binding_sha256,
    )

    details, _parsed_v23, bridge_errors = _validate_v23_result(
        raw=capture_manifest_v23_validation_result,
        expected_sha256=expected_capture_manifest_v23_validation_result_sha256,
        expected_population_sha256=expected_capture_manifest_v23_admitted_population_sha256,
        binding=structural_audit_inputs,
        expected_binding_sha256=expected_structural_audit_inputs_sha256,
        inherited=inherited,
    )
    if isinstance(structural_audit_inputs, dict):
        bridge_errors.extend(
            _validate_source_and_declaration_links(
                raw_sources=raw_sources,
                inherited=inherited,
                binding=structural_audit_inputs,
            )
        )
    bridge_errors = sorted(set(bridge_errors))
    bridge_violation_count = len(bridge_errors)

    inherited_errors = list(inherited.get("errors", []))
    errors = sorted(set(inherited_errors + bridge_errors))
    contract_valid = bool(inherited.get("contractValid") is True and bridge_violation_count == 0)
    suitable = bool(
        inherited.get("datasetStructurallySuitable") is True
        and bridge_violation_count == 0
    )

    inherited_population_sha = inherited.get("derivedPopulationSha256")
    derived_population_sha = None
    if (
        inherited_population_sha is not None
        and bridge_violation_count == 0
        and details.get("captureManifestV23ValidationResultSha256") is not None
        and details.get("captureManifestV23AdmittedPopulationSha256") is not None
        and details.get("structuralAuditInputsSha256") is not None
        and details.get("attemptId") is not None
        and details.get("slotId") is not None
        and details.get("underlyingPerformanceId") is not None
    ):
        derived_population_sha = _canonical_sha256(
            {
                "populationIdentityVersion": POPULATION_IDENTITY_VERSION,
                "inheritedV11DerivedPopulationSha256": inherited_population_sha,
                "captureManifestV23ValidationResultSha256": details[
                    "captureManifestV23ValidationResultSha256"
                ],
                "captureManifestV23AdmittedPopulationSha256": details[
                    "captureManifestV23AdmittedPopulationSha256"
                ],
                "attemptId": details["attemptId"],
                "slotId": details["slotId"],
                "underlyingPerformanceId": details["underlyingPerformanceId"],
                "structuralAuditInputsSha256": details["structuralAuditInputsSha256"],
            }
        )

    return {
        **inherited,
        "contract": CONTRACT,
        "contractValid": contract_valid,
        "errors": errors,
        **details,
        "capturePopulationBindingViolationCount": bridge_violation_count,
        "populationIdentityVersion": POPULATION_IDENTITY_VERSION,
        "inheritedV11DerivedPopulationSha256": inherited_population_sha,
        "derivedPopulationSha256": derived_population_sha,
        "datasetStructurallySuitable": suitable,
        "authoritativeStructuralSuitabilityEstablished": suitable,
        **_closed_authorization(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hardware", required=True)
    parser.add_argument("--hardware-sha256", required=True)
    parser.add_argument("--birth-stream", required=True)
    parser.add_argument("--birth-stream-sha256", required=True)
    parser.add_argument("--pitch-latch-stream", required=True)
    parser.add_argument("--pitch-latch-stream-sha256", required=True)
    parser.add_argument("--clock-sync", required=True)
    parser.add_argument("--clock-sync-sha256", required=True)
    parser.add_argument("--calibration-provenance-result", required=True)
    parser.add_argument("--calibration-provenance-result-sha256", required=True)
    parser.add_argument("--declared-provenance-result-sha256", required=True)
    parser.add_argument("--declared-calibration-package-binding-sha256", required=True)
    parser.add_argument("--capture-manifest-v23-validation-result", required=True)
    parser.add_argument("--capture-manifest-v23-validation-result-sha256", required=True)
    parser.add_argument("--structural-audit-inputs", required=True)
    parser.add_argument("--structural-audit-inputs-sha256", required=True)
    parser.add_argument("--capture-manifest-v23-admitted-population-sha256", required=True)
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw_sources = {
        "hardware": Path(args.hardware).read_bytes(),
        "birth": Path(args.birth_stream).read_bytes(),
        "pitchLatch": Path(args.pitch_latch_stream).read_bytes(),
        "clockSync": Path(args.clock_sync).read_bytes(),
    }
    expected = {
        "hardware": args.hardware_sha256,
        "birth": args.birth_stream_sha256,
        "pitchLatch": args.pitch_latch_stream_sha256,
        "clockSync": args.clock_sync_sha256,
    }
    provenance_bytes = Path(args.calibration_provenance_result).read_bytes()
    v23_result_bytes = Path(args.capture_manifest_v23_validation_result).read_bytes()
    structural_binding = json.loads(Path(args.structural_audit_inputs).read_text(encoding="utf-8"))
    result = audit_raw_sources_v1_2(
        raw_sources=raw_sources,
        expected_sha256=expected,
        calibration_provenance_result=provenance_bytes,
        expected_calibration_provenance_result_sha256=args.calibration_provenance_result_sha256,
        declared_provenance_result_sha256=args.declared_provenance_result_sha256,
        declared_calibration_package_binding_sha256=args.declared_calibration_package_binding_sha256,
        capture_manifest_v23_validation_result=v23_result_bytes,
        expected_capture_manifest_v23_validation_result_sha256=args.capture_manifest_v23_validation_result_sha256,
        structural_audit_inputs=structural_binding,
        expected_structural_audit_inputs_sha256=args.structural_audit_inputs_sha256,
        expected_capture_manifest_v23_admitted_population_sha256=args.capture_manifest_v23_admitted_population_sha256,
    )
    rendered = canonical_json_bytes(result) + b"\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(rendered)
    print(rendered.decode("utf-8"), end="")
    return 0 if result["datasetStructurallySuitable"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
