#!/usr/bin/env python3
"""Reference-blind structural audit V1.1 provenance-result bridge.

Synthetic/software qualification only. V1.1 preserves the frozen V1 four-source
reference audit and adds one separately supplied calibration-provenance result
byte stream. The fifth stream is SHA-256 verified before it is decoded or parsed.
No evaluated audio, model output, correctness data, or network access is used.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent
V1_PATH = HERE / "purpose_built_reference_blind_structural_audit_v1.py"
spec = importlib.util.spec_from_file_location("purpose_built_reference_blind_structural_audit_v1", V1_PATH)
assert spec and spec.loader
v1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v1)

CONTRACT = "songsterr-fresh-purpose-built-reference-blind-structural-audit-v1.1"
PROVENANCE_RESULT_CONTRACT = "songsterr-fresh-purpose-built-reference-calibration-package-v1"
POPULATION_IDENTITY_VERSION = "reference-blind-structural-audit-v1.1-provenance-bridge-v1"
TIMING_BOUND_SECONDS = v1.TIMING_BOUND_SECONDS


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


def _finite_nonnegative(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and float(value) >= 0.0
    )


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


def _provenance_source_report(raw: Any, expected_sha256: Any) -> dict[str, Any]:
    actual = sha256_bytes(raw) if isinstance(raw, bytes) else None
    matches = bool(
        actual is not None
        and _is_sha256(expected_sha256)
        and actual == expected_sha256
    )
    return {"expected": expected_sha256, "actual": actual, "matches": matches}


def _validate_provenance_bridge(
    *,
    calibration_provenance_result: Any,
    expected_calibration_provenance_result_sha256: Any,
    declared_provenance_result_sha256: Any,
    declared_calibration_package_binding_sha256: Any,
) -> tuple[dict[str, Any], list[str]]:
    details: dict[str, Any] = {
        "calibrationProvenanceSourceSha256": _provenance_source_report(
            calibration_provenance_result,
            expected_calibration_provenance_result_sha256,
        ),
        "calibrationProvenanceResultContract": None,
        "calibrationProvenanceResultSha256": None,
        "calibrationPackageBindingSha256": None,
        "calibrationPackageDecoderId": None,
        "calibrationPackageDecoderSoftwareVersion": None,
        "calibrationPackageDecoderCodeSha256": None,
        "calibrationPackageDecoderConfigurationSha256": None,
    }
    errors: list[str] = []

    # Frozen pre-parse identity gates for the fifth stream.
    if not isinstance(calibration_provenance_result, bytes):
        errors.append("CALIBRATION_PROVENANCE_RESULT_NOT_BYTES")
        return details, errors

    if not _is_sha256(expected_calibration_provenance_result_sha256):
        errors.append("CALIBRATION_PROVENANCE_EXPECTED_SHA256_INVALID")
        return details, errors

    actual_sha = details["calibrationProvenanceSourceSha256"]["actual"]
    if actual_sha != expected_calibration_provenance_result_sha256:
        errors.append("CALIBRATION_PROVENANCE_RESULT_SHA256_MISMATCH")
        return details, errors

    if not _is_sha256(declared_provenance_result_sha256):
        errors.append("DECLARED_PROVENANCE_RESULT_SHA256_INVALID")
        return details, errors

    if expected_calibration_provenance_result_sha256 != declared_provenance_result_sha256:
        errors.append("CALIBRATION_PROVENANCE_EXPECTED_V22_SHA256_MISMATCH")
        return details, errors

    if not _is_sha256(declared_calibration_package_binding_sha256):
        errors.append("DECLARED_CALIBRATION_PACKAGE_BINDING_SHA256_INVALID")
        return details, errors

    # Only now may the provenance result bytes be decoded and parsed.
    try:
        parsed = json.loads(calibration_provenance_result.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"CALIBRATION_PROVENANCE_RESULT_INVALID_JSON:{type(exc).__name__}")
        return details, errors

    if not isinstance(parsed, dict):
        errors.append("CALIBRATION_PROVENANCE_RESULT_OBJECT_REQUIRED")
        return details, errors

    details["calibrationProvenanceResultContract"] = parsed.get("contract")
    details["calibrationProvenanceResultSha256"] = actual_sha

    if parsed.get("contract") != PROVENANCE_RESULT_CONTRACT:
        errors.append("CALIBRATION_PROVENANCE_RESULT_CONTRACT_MISMATCH")
    if parsed.get("contractValid") is not True:
        errors.append("CALIBRATION_PROVENANCE_RESULT_CONTRACT_NOT_VALID")
    if parsed.get("errors") != []:
        errors.append("CALIBRATION_PROVENANCE_RESULT_ERRORS_NOT_EMPTY")

    binding_sha = parsed.get("packageBindingSha256")
    if not _is_sha256(binding_sha):
        errors.append("CALIBRATION_PROVENANCE_PACKAGE_BINDING_SHA256_INVALID")
    else:
        details["calibrationPackageBindingSha256"] = binding_sha
        if binding_sha != declared_calibration_package_binding_sha256:
            errors.append("CALIBRATION_PROVENANCE_PACKAGE_BINDING_SHA256_DECLARATION_MISMATCH")

    binding = parsed.get("packageBinding")
    if not isinstance(binding, dict):
        errors.append("CALIBRATION_PROVENANCE_PACKAGE_BINDING_OBJECT_REQUIRED")
        return details, errors

    try:
        canonical_binding_sha = sha256_bytes(canonical_json_bytes(binding))
    except (TypeError, ValueError):
        errors.append("CALIBRATION_PROVENANCE_PACKAGE_BINDING_CANONICALIZATION_FAILED")
    else:
        if _is_sha256(binding_sha) and canonical_binding_sha != binding_sha:
            errors.append("CALIBRATION_PROVENANCE_PACKAGE_BINDING_CANONICAL_SHA256_MISMATCH")

    for field in ("usedHoldoutData", "usedModelOutputs", "derivedFromEvaluatedAudio"):
        if binding.get(field) is not False:
            errors.append(f"CALIBRATION_PROVENANCE_PACKAGE_{field.upper()}_MUST_BE_FALSE")

    timing = binding.get("maxAbsoluteOnsetErrorSeconds")
    if not _finite_nonnegative(timing):
        errors.append("CALIBRATION_PROVENANCE_PACKAGE_TIMING_INVALID")
    elif float(timing) > TIMING_BOUND_SECONDS:
        errors.append("CALIBRATION_PROVENANCE_PACKAGE_TIMING_EXCEEDS_BOUND")

    if not _nonempty(binding.get("calibrationId")):
        errors.append("CALIBRATION_PROVENANCE_PACKAGE_CALIBRATION_ID_REQUIRED")

    decoder = binding.get("decoder")
    if not isinstance(decoder, dict):
        errors.append("CALIBRATION_PROVENANCE_PACKAGE_DECODER_OBJECT_REQUIRED")
    else:
        decoder_id = decoder.get("decoderId")
        software_version = decoder.get("softwareVersion")
        if not _nonempty(decoder_id):
            errors.append("CALIBRATION_PROVENANCE_PACKAGE_DECODER_ID_REQUIRED")
        else:
            details["calibrationPackageDecoderId"] = decoder_id.strip()
        if not _nonempty(software_version):
            errors.append("CALIBRATION_PROVENANCE_PACKAGE_DECODER_SOFTWARE_VERSION_REQUIRED")
        else:
            details["calibrationPackageDecoderSoftwareVersion"] = software_version.strip()

        code = decoder.get("code")
        code_sha = code.get("sha256") if isinstance(code, dict) else None
        if not _is_sha256(code_sha):
            errors.append("CALIBRATION_PROVENANCE_PACKAGE_DECODER_CODE_SHA256_INVALID")
        else:
            details["calibrationPackageDecoderCodeSha256"] = code_sha

        configuration = decoder.get("configuration")
        configuration_sha = configuration.get("sha256") if isinstance(configuration, dict) else None
        if not _is_sha256(configuration_sha):
            errors.append("CALIBRATION_PROVENANCE_PACKAGE_DECODER_CONFIGURATION_SHA256_INVALID")
        else:
            details["calibrationPackageDecoderConfigurationSha256"] = configuration_sha

    return details, errors


def audit_raw_sources_v1_1(
    *,
    raw_sources: Mapping[str, bytes],
    expected_sha256: Mapping[str, str],
    calibration_provenance_result: Any,
    expected_calibration_provenance_result_sha256: Any,
    declared_provenance_result_sha256: Any,
    declared_calibration_package_binding_sha256: Any,
) -> dict[str, Any]:
    """Run frozen V1 plus the separately hash-gated provenance-result bridge."""
    inherited = v1.audit_raw_sources(
        raw_sources=raw_sources,
        expected_sha256=expected_sha256,
    )

    bridge_details, bridge_errors = _validate_provenance_bridge(
        calibration_provenance_result=calibration_provenance_result,
        expected_calibration_provenance_result_sha256=expected_calibration_provenance_result_sha256,
        declared_provenance_result_sha256=declared_provenance_result_sha256,
        declared_calibration_package_binding_sha256=declared_calibration_package_binding_sha256,
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
    augmented_population_sha: str | None = None
    verified_provenance_sha = bridge_details.get("calibrationProvenanceResultSha256")
    verified_binding_sha = bridge_details.get("calibrationPackageBindingSha256")
    if (
        inherited_population_sha is not None
        and verified_provenance_sha is not None
        and verified_binding_sha is not None
        and bridge_violation_count == 0
    ):
        augmented_population_sha = sha256_bytes(
            canonical_json_bytes(
                {
                    "populationIdentityVersion": POPULATION_IDENTITY_VERSION,
                    "inheritedV1DerivedPopulationSha256": inherited_population_sha,
                    "calibrationProvenanceResultSha256": verified_provenance_sha,
                    "calibrationPackageBindingSha256": verified_binding_sha,
                }
            )
        )

    return {
        "contract": CONTRACT,
        "contractValid": contract_valid,
        "sourceSha256": inherited.get("sourceSha256", {}),
        **bridge_details,
        "calibrationProvenanceBridgeViolationCount": bridge_violation_count,
        "populationIdentityVersion": POPULATION_IDENTITY_VERSION,
        "inheritedV1DerivedPopulationSha256": inherited_population_sha,
        "derivedPopulationSha256": augmented_population_sha,
        "derivedNoteEventCount": inherited.get("derivedNoteEventCount", 0),
        "blockerCounts": dict(inherited.get("blockerCounts", {})),
        "errors": errors,
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
    result = audit_raw_sources_v1_1(
        raw_sources=raw_sources,
        expected_sha256=expected,
        calibration_provenance_result=provenance_bytes,
        expected_calibration_provenance_result_sha256=args.calibration_provenance_result_sha256,
        declared_provenance_result_sha256=args.declared_provenance_result_sha256,
        declared_calibration_package_binding_sha256=args.declared_calibration_package_binding_sha256,
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
