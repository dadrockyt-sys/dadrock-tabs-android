#!/usr/bin/env python3
"""Purpose-built capture-manifest V2.2 calibration-package identity bridge.

V2.2 is deliberately additive over V2.1. It preserves all inherited capture,
retry, acquisition-QA, structural, policy, timing, and correctness boundaries
and adds only deterministic linkage to one already-validated calibration
package provenance identity.

Declaration-only software: this module does not open calibration-package files,
media, reference bytes, or validation-result artifacts.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
V21_PATH = HERE / "purpose_built_capture_manifest_contract_v2_1.py"
spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_manifest_contract_v2_1", V21_PATH
)
assert spec and spec.loader
v21 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v21)

CONTRACT = "songsterr-fresh-purpose-built-capture-manifest-v2.2"
PACKAGE_CONTRACT = "songsterr-fresh-purpose-built-reference-calibration-package-v1"
BRIDGE_VERSION = "capture-manifest-calibration-package-bridge-v1"
POPULATION_IDENTITY_VERSION = "capture-manifest-v2.2-calibration-package-bridge-v1"
MAX_REFERENCE_TIMING_ERROR_SECONDS = 0.025


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


def _nonempty(value: Any) -> bool:
    return v21.v2._nonempty(value)


def _is_sha256(value: Any) -> bool:
    return v21.v2.v1._is_sha256(value)


def _finite_nonnegative(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and float(value) >= 0.0
    )


def _safe_relative_posix_path(value: Any) -> bool:
    if not _nonempty(value):
        return False
    text = value.strip()
    if "\\" in text or text.startswith("/") or text.endswith("/"):
        return False
    parts = text.split("/")
    if any(part in ("", ".", "..") for part in parts):
        return False
    return True


def _validate_decoder(
    binding: dict[str, Any], errors: list[str]
) -> tuple[str | None, str | None, str | None, str | None]:
    decoder = binding.get("decoder")
    if not isinstance(decoder, dict):
        errors.append("CALIBRATION_PACKAGE_DECODER_OBJECT_REQUIRED")
        return None, None, None, None

    decoder_id = decoder.get("decoderId")
    if not _nonempty(decoder_id):
        errors.append("CALIBRATION_PACKAGE_DECODER_ID_REQUIRED")
        decoder_id = None
    else:
        decoder_id = decoder_id.strip()

    software_version = decoder.get("softwareVersion")
    if not _nonempty(software_version):
        errors.append("CALIBRATION_PACKAGE_DECODER_SOFTWARE_VERSION_REQUIRED")
        software_version = None
    else:
        software_version = software_version.strip()

    code_sha: str | None = None
    configuration_sha: str | None = None
    for label, key in (("CODE", "code"), ("CONFIGURATION", "configuration")):
        obj = decoder.get(key)
        if not isinstance(obj, dict):
            errors.append(f"CALIBRATION_PACKAGE_DECODER_{label}_OBJECT_REQUIRED")
            continue
        declared_sha = obj.get("sha256")
        if not _is_sha256(declared_sha):
            errors.append(f"CALIBRATION_PACKAGE_DECODER_{label}_SHA256_INVALID")
            continue
        if key == "code":
            code_sha = declared_sha
        else:
            configuration_sha = declared_sha

    return decoder_id, software_version, code_sha, configuration_sha


def _validate_package_link(
    manifest: dict[str, Any], errors: list[str]
) -> dict[str, Any]:
    details: dict[str, Any] = {
        "validationResultPath": None,
        "validationResultSha256": None,
        "packageBindingSha256": None,
        "decoderId": None,
        "decoderSoftwareVersion": None,
        "decoderCodeSha256": None,
        "decoderConfigurationSha256": None,
    }

    corpus = manifest.get("corpus")
    if not isinstance(corpus, dict):
        errors.append("CORPUS_OBJECT_REQUIRED")
        return details

    package = corpus.get("referenceCalibrationPackage")
    if not isinstance(package, dict):
        errors.append("REFERENCE_CALIBRATION_PACKAGE_OBJECT_REQUIRED")
        return details

    if package.get("contract") != PACKAGE_CONTRACT:
        errors.append(
            "REFERENCE_CALIBRATION_PACKAGE_CONTRACT_MISMATCH:"
            f"{package.get('contract')!r}"
        )

    validation_path = package.get("validationResultPath")
    if not _safe_relative_posix_path(validation_path):
        errors.append("REFERENCE_CALIBRATION_PACKAGE_VALIDATION_RESULT_PATH_INVALID")
    else:
        details["validationResultPath"] = validation_path.strip()

    validation_sha = package.get("validationResultSha256")
    if not _is_sha256(validation_sha):
        errors.append("REFERENCE_CALIBRATION_PACKAGE_VALIDATION_RESULT_SHA256_INVALID")
    else:
        details["validationResultSha256"] = validation_sha

    binding_sha = package.get("packageBindingSha256")
    if not _is_sha256(binding_sha):
        errors.append("REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_INVALID")
    else:
        details["packageBindingSha256"] = binding_sha

    binding = package.get("packageBinding")
    if not isinstance(binding, dict):
        errors.append("REFERENCE_CALIBRATION_PACKAGE_BINDING_OBJECT_REQUIRED")
        return details

    if details["packageBindingSha256"] is not None:
        try:
            actual_binding_sha = _canonical_sha256(binding)
        except (TypeError, ValueError):
            errors.append("REFERENCE_CALIBRATION_PACKAGE_BINDING_CANONICALIZATION_FAILED")
        else:
            if actual_binding_sha != details["packageBindingSha256"]:
                errors.append("REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_MISMATCH")

    if binding.get("contract") != PACKAGE_CONTRACT:
        errors.append(
            "CALIBRATION_PACKAGE_BINDING_CONTRACT_MISMATCH:"
            f"{binding.get('contract')!r}"
        )

    binding_calibration_id = binding.get("calibrationId")
    if not _nonempty(binding_calibration_id):
        errors.append("CALIBRATION_PACKAGE_BINDING_CALIBRATION_ID_REQUIRED")
        binding_calibration_id = None
    else:
        binding_calibration_id = binding_calibration_id.strip()

    legacy_calibration = corpus.get("referenceCalibration")
    if isinstance(legacy_calibration, dict):
        legacy_id = legacy_calibration.get("calibrationId")
        if (
            binding_calibration_id is not None
            and _nonempty(legacy_id)
            and binding_calibration_id != legacy_id.strip()
        ):
            errors.append("CALIBRATION_PACKAGE_LEGACY_CALIBRATION_ID_MISMATCH")

        package_timing = binding.get("maxAbsoluteOnsetErrorSeconds")
        legacy_timing = legacy_calibration.get("maxAbsoluteOnsetErrorSeconds")
        if not _finite_nonnegative(package_timing):
            errors.append("CALIBRATION_PACKAGE_BINDING_TIMING_ERROR_INVALID")
        else:
            if float(package_timing) > MAX_REFERENCE_TIMING_ERROR_SECONDS:
                errors.append("CALIBRATION_PACKAGE_BINDING_TIMING_ERROR_EXCEEDS_BOUND")
            if not _finite_nonnegative(legacy_timing):
                errors.append("CALIBRATION_PACKAGE_LEGACY_TIMING_ERROR_INVALID")
            elif float(package_timing) != float(legacy_timing):
                errors.append("CALIBRATION_PACKAGE_LEGACY_TIMING_ERROR_MISMATCH")
    else:
        errors.append("REFERENCE_CALIBRATION_OBJECT_REQUIRED")

    hardware = corpus.get("hardware")
    if isinstance(hardware, dict):
        config = hardware.get("configuration")
        package_config = binding.get("hardwareConfiguration")
        if not isinstance(package_config, dict):
            errors.append("CALIBRATION_PACKAGE_HARDWARE_CONFIGURATION_OBJECT_REQUIRED")
        else:
            package_config_id = package_config.get("configurationId")
            if not _nonempty(package_config_id):
                errors.append("CALIBRATION_PACKAGE_HARDWARE_CONFIGURATION_ID_REQUIRED")
            elif (
                isinstance(config, dict)
                and _nonempty(config.get("configurationId"))
                and package_config_id.strip() != config.get("configurationId").strip()
            ):
                errors.append("CALIBRATION_PACKAGE_HARDWARE_CONFIGURATION_ID_MISMATCH")

            package_config_sha = package_config.get("sha256")
            if not _is_sha256(package_config_sha):
                errors.append("CALIBRATION_PACKAGE_HARDWARE_CONFIGURATION_SHA256_INVALID")
            elif (
                isinstance(config, dict)
                and package_config_sha != config.get("sha256")
            ):
                errors.append("CALIBRATION_PACKAGE_HARDWARE_CONFIGURATION_SHA256_MISMATCH")

        setup = hardware.get("instrumentSetup")
        package_setup_sha = binding.get("instrumentSetupSha256")
        if not _is_sha256(package_setup_sha):
            errors.append("CALIBRATION_PACKAGE_INSTRUMENT_SETUP_SHA256_INVALID")
        elif (
            isinstance(setup, dict)
            and package_setup_sha != setup.get("setupSha256")
        ):
            errors.append("CALIBRATION_PACKAGE_INSTRUMENT_SETUP_SHA256_MISMATCH")
    else:
        errors.append("HARDWARE_OBJECT_REQUIRED")

    for field in ("usedHoldoutData", "usedModelOutputs", "derivedFromEvaluatedAudio"):
        if binding.get(field) is not False:
            errors.append(f"CALIBRATION_PACKAGE_BINDING_{field.upper()}_MUST_BE_FALSE")

    (
        details["decoderId"],
        details["decoderSoftwareVersion"],
        details["decoderCodeSha256"],
        details["decoderConfigurationSha256"],
    ) = _validate_decoder(binding, errors)

    return details


def _validate_admitted_reference_links(
    manifest: dict[str, Any], package: dict[str, Any], errors: list[str]
) -> None:
    binding_sha = package.get("packageBindingSha256")
    decoder_configuration_sha = package.get("decoderConfigurationSha256")
    attempts = manifest.get("attempts")
    if not isinstance(attempts, list):
        return

    for index, attempt in enumerate(attempts):
        if not isinstance(attempt, dict) or attempt.get("admitted") is not True:
            continue
        reference = attempt.get("reference")
        if not isinstance(reference, dict):
            continue

        declared_binding_sha = reference.get("calibrationPackageBindingSha256")
        if not _is_sha256(declared_binding_sha):
            errors.append(
                f"ATTEMPT[{index}]_REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_INVALID"
            )
        elif binding_sha is not None and declared_binding_sha != binding_sha:
            errors.append(
                f"ATTEMPT[{index}]_REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_MISMATCH"
            )

        derivation_sha = reference.get("derivationConfigurationSha256")
        if not _is_sha256(derivation_sha):
            errors.append(
                f"ATTEMPT[{index}]_REFERENCE_DERIVATION_CONFIGURATION_SHA256_INVALID"
            )
        elif (
            decoder_configuration_sha is not None
            and derivation_sha != decoder_configuration_sha
        ):
            errors.append(
                f"ATTEMPT[{index}]_REFERENCE_DERIVATION_CONFIGURATION_SHA256_MISMATCH"
            )


def _population_sha(manifest: dict[str, Any], package: dict[str, Any]) -> str:
    corpus = manifest.get("corpus") if isinstance(manifest, dict) else None
    calibration_sha = None
    sync_id = None
    config_sha = None
    if isinstance(corpus, dict):
        calibration = corpus.get("referenceCalibration")
        if isinstance(calibration, dict):
            calibration_sha = calibration.get("sha256")
        sync = corpus.get("clockSync")
        if isinstance(sync, dict):
            sync_id = sync.get("syncId")
        hardware = corpus.get("hardware")
        if isinstance(hardware, dict):
            config = hardware.get("configuration")
            if isinstance(config, dict):
                config_sha = config.get("sha256")

    rows: list[dict[str, Any]] = []
    attempts = manifest.get("attempts") if isinstance(manifest, dict) else None
    if isinstance(attempts, list):
        for attempt in attempts:
            if not isinstance(attempt, dict) or attempt.get("admitted") is not True:
                continue
            audio = attempt.get("evaluatedAudio") or {}
            pitch = attempt.get("pitchEvidence") or {}
            birth = attempt.get("birthEvidence") or {}
            reference = attempt.get("reference") or {}
            rows.append(
                {
                    "attemptId": attempt.get("attemptId"),
                    "slotId": attempt.get("slotId"),
                    "underlyingPerformanceId": attempt.get("underlyingPerformanceId"),
                    "playerId": attempt.get("playerId"),
                    "exerciseId": attempt.get("exerciseId"),
                    "category": attempt.get("category"),
                    "evaluatedAudioSha256": audio.get("sha256"),
                    "pitchEvidenceSha256": pitch.get("sha256"),
                    "birthEvidenceSha256": birth.get("sha256"),
                    "referenceSha256": reference.get("sha256"),
                    "derivationConfigurationSha256": reference.get(
                        "derivationConfigurationSha256"
                    ),
                    "hardwareConfigurationSha256": config_sha,
                    "calibrationSha256": calibration_sha,
                    "clockSyncId": sync_id,
                    "calibrationPackageBindingSha256": package.get(
                        "packageBindingSha256"
                    ),
                    "calibrationPackageValidationResultSha256": package.get(
                        "validationResultSha256"
                    ),
                }
            )
    rows.sort(key=lambda row: (str(row["slotId"]), str(row["attemptId"])))
    return _canonical_sha256(rows)


def validate_manifest(manifest: Any) -> dict[str, Any]:
    projected = manifest
    if isinstance(manifest, dict):
        projected = copy.deepcopy(manifest)
        projected["contract"] = v21.CONTRACT

    inherited = v21.validate_manifest(projected)
    inherited_errors = list(inherited.get("errors", []))
    bridge_errors: list[str] = []

    if not isinstance(manifest, dict):
        bridge_errors.append("TOP_LEVEL_OBJECT_REQUIRED")
        package = {
            "validationResultPath": None,
            "validationResultSha256": None,
            "packageBindingSha256": None,
            "decoderId": None,
            "decoderSoftwareVersion": None,
            "decoderCodeSha256": None,
            "decoderConfigurationSha256": None,
        }
    else:
        if manifest.get("contract") != CONTRACT:
            bridge_errors.append(f"CONTRACT_MISMATCH:{manifest.get('contract')!r}")
        package = _validate_package_link(manifest, bridge_errors)
        _validate_admitted_reference_links(manifest, package, bridge_errors)

    merged_errors = sorted(set(inherited_errors + bridge_errors))
    contract_valid = not merged_errors
    package_bridge_valid = not bridge_errors
    population_sha = (
        _population_sha(manifest, package)
        if isinstance(manifest, dict)
        else inherited.get("admittedPopulationManifestSha256")
    )
    may_advance = bool(
        contract_valid
        and inherited.get("mayAdvanceToReferenceBlindStructuralAudit") is True
    )

    return {
        **inherited,
        "contract": CONTRACT,
        "contractValid": contract_valid,
        "errors": merged_errors,
        "v22SemanticGuardPassed": contract_valid,
        "packageBridgeValid": package_bridge_valid,
        "calibrationPackageBridgeVersion": BRIDGE_VERSION,
        "calibrationPackageValidationResultPath": package.get("validationResultPath"),
        "calibrationPackageValidationResultSha256": package.get(
            "validationResultSha256"
        ),
        "calibrationPackageBindingSha256": package.get("packageBindingSha256"),
        "calibrationPackageDecoderId": package.get("decoderId"),
        "calibrationPackageDecoderSoftwareVersion": package.get(
            "decoderSoftwareVersion"
        ),
        "calibrationPackageDecoderCodeSha256": package.get("decoderCodeSha256"),
        "calibrationPackageDecoderConfigurationSha256": package.get(
            "decoderConfigurationSha256"
        ),
        "populationIdentityVersion": POPULATION_IDENTITY_VERSION,
        "inheritedV21AdmittedPopulationManifestSha256": inherited.get(
            "admittedPopulationManifestSha256"
        ),
        "admittedPopulationManifestSha256": population_sha,
        "mayAdvanceToReferenceBlindStructuralAudit": may_advance,
        "authoritativeStructuralSuitabilityEstablished": False,
        "realCalibrationAuthorized": False,
        "realHoldoutCaptureAuthorized": False,
        "basicPitchAuthorized": False,
        "v6Authorized": False,
        "correctnessAuthorized": False,
        "modelValidationComplete": False,
        "customerEligibleEvents": 0,
        "mayAdvanceDelivery": False,
        "policyBoundary": dict(v21.v2.v1.REQUIRED_POLICY_BOUNDARY),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="Path to V2.2 capture manifest JSON")
    parser.add_argument("--output", help="Optional deterministic validation-result JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    result = validate_manifest(manifest)
    rendered = canonical_json_bytes(result) + b"\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(rendered)
    print(rendered.decode("utf-8"), end="")
    return 0 if result["contractValid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
