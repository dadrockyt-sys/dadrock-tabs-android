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


def _canonical_sha256(value: Any) -> str:
    rendered = v21.v2.v1.canonical_json(value).encode("utf-8")
    return v21.v2.v1.sha256_bytes(rendered)


def _validate_decoder(binding: dict[str, Any], errors: list[str]) -> None:
    decoder = binding.get("decoder")
    if not isinstance(decoder, dict):
        errors.append("CALIBRATION_PACKAGE_DECODER_OBJECT_REQUIRED")
        return
    if not _nonempty(decoder.get("decoderId")):
        errors.append("CALIBRATION_PACKAGE_DECODER_ID_REQUIRED")
    if not _nonempty(decoder.get("softwareVersion")):
        errors.append("CALIBRATION_PACKAGE_DECODER_SOFTWARE_VERSION_REQUIRED")
    for label, key in (
        ("CODE", "code"),
        ("CONFIGURATION", "configuration"),
    ):
        obj = decoder.get(key)
        if not isinstance(obj, dict):
            errors.append(f"CALIBRATION_PACKAGE_DECODER_{label}_OBJECT_REQUIRED")
            continue
        if not _is_sha256(obj.get("sha256")):
            errors.append(f"CALIBRATION_PACKAGE_DECODER_{label}_SHA256_INVALID")


def _validate_package_link(
    manifest: dict[str, Any], errors: list[str]
) -> tuple[str | None, str | None]:
    corpus = manifest.get("corpus")
    if not isinstance(corpus, dict):
        errors.append("CORPUS_OBJECT_REQUIRED")
        return None, None

    package = corpus.get("referenceCalibrationPackage")
    if not isinstance(package, dict):
        errors.append("REFERENCE_CALIBRATION_PACKAGE_OBJECT_REQUIRED")
        return None, None

    if package.get("contract") != PACKAGE_CONTRACT:
        errors.append(
            "REFERENCE_CALIBRATION_PACKAGE_CONTRACT_MISMATCH:"
            f"{package.get('contract')!r}"
        )

    package_calibration_id = package.get("calibrationId")
    if not _nonempty(package_calibration_id):
        errors.append("REFERENCE_CALIBRATION_PACKAGE_CALIBRATION_ID_REQUIRED")
        package_calibration_id = None
    else:
        package_calibration_id = package_calibration_id.strip()

    binding_sha = package.get("packageBindingSha256")
    if not _is_sha256(binding_sha):
        errors.append("REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_INVALID")
        binding_sha = None

    validation_sha = package.get("validationResultSha256")
    if not _is_sha256(validation_sha):
        errors.append("REFERENCE_CALIBRATION_PACKAGE_VALIDATION_RESULT_SHA256_INVALID")
        validation_sha = None

    binding = package.get("packageBinding")
    if not isinstance(binding, dict):
        errors.append("REFERENCE_CALIBRATION_PACKAGE_BINDING_OBJECT_REQUIRED")
        return binding_sha, validation_sha

    if binding_sha is not None:
        try:
            actual_binding_sha = _canonical_sha256(binding)
        except Exception as exc:
            errors.append(
                "REFERENCE_CALIBRATION_PACKAGE_BINDING_CANONICALIZATION_FAILED:"
                f"{type(exc).__name__}"
            )
        else:
            if actual_binding_sha != binding_sha:
                errors.append("REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_MISMATCH")

    if binding.get("contract") != PACKAGE_CONTRACT:
        errors.append(
            "CALIBRATION_PACKAGE_BINDING_CONTRACT_MISMATCH:"
            f"{binding.get('contract')!r}"
        )

    binding_calibration_id = binding.get("calibrationId")
    if not _nonempty(binding_calibration_id):
        errors.append("CALIBRATION_PACKAGE_BINDING_CALIBRATION_ID_REQUIRED")
    elif (
        package_calibration_id is not None
        and binding_calibration_id.strip() != package_calibration_id
    ):
        errors.append("CALIBRATION_PACKAGE_BINDING_CALIBRATION_ID_MISMATCH")

    legacy_calibration = corpus.get("referenceCalibration")
    if isinstance(legacy_calibration, dict):
        legacy_id = legacy_calibration.get("calibrationId")
        if (
            package_calibration_id is not None
            and _nonempty(legacy_id)
            and legacy_id.strip() != package_calibration_id
        ):
            errors.append("CALIBRATION_PACKAGE_LEGACY_CALIBRATION_ID_MISMATCH")
        if (
            _nonempty(binding_calibration_id)
            and _nonempty(legacy_id)
            and binding_calibration_id.strip() != legacy_id.strip()
        ):
            errors.append("CALIBRATION_PACKAGE_BINDING_LEGACY_CALIBRATION_ID_MISMATCH")

        package_timing = binding.get("maxAbsoluteOnsetErrorSeconds")
        legacy_timing = legacy_calibration.get("maxAbsoluteOnsetErrorSeconds")
        if not _finite_nonnegative(package_timing):
            errors.append("CALIBRATION_PACKAGE_BINDING_TIMING_ERROR_INVALID")
        elif not _finite_nonnegative(legacy_timing):
            # Inherited V2.1 also reports the legacy error; keep this linkage fail closed.
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
        elif not _is_sha256(package_config.get("sha256")):
            errors.append("CALIBRATION_PACKAGE_HARDWARE_CONFIGURATION_SHA256_INVALID")
        elif isinstance(config, dict) and package_config.get("sha256") != config.get("sha256"):
            errors.append("CALIBRATION_PACKAGE_HARDWARE_CONFIGURATION_SHA256_MISMATCH")

        setup = hardware.get("instrumentSetup")
        package_setup_sha = binding.get("instrumentSetupSha256")
        if not _is_sha256(package_setup_sha):
            errors.append("CALIBRATION_PACKAGE_INSTRUMENT_SETUP_SHA256_INVALID")
        elif isinstance(setup, dict) and package_setup_sha != setup.get("setupSha256"):
            errors.append("CALIBRATION_PACKAGE_INSTRUMENT_SETUP_SHA256_MISMATCH")

    for field in ("usedHoldoutData", "usedModelOutputs", "derivedFromEvaluatedAudio"):
        if binding.get(field) is not False:
            errors.append(f"CALIBRATION_PACKAGE_BINDING_{field.upper()}_MUST_BE_FALSE")

    _validate_decoder(binding, errors)
    return binding_sha, validation_sha


def _validate_admitted_reference_links(
    manifest: dict[str, Any], binding_sha: str | None, errors: list[str]
) -> None:
    attempts = manifest.get("attempts")
    if not isinstance(attempts, list):
        return
    for index, attempt in enumerate(attempts):
        if not isinstance(attempt, dict) or attempt.get("admitted") is not True:
            continue
        reference = attempt.get("reference")
        if not isinstance(reference, dict):
            # Inherited validator owns the base object error.
            continue
        declared = reference.get("calibrationPackageBindingSha256")
        if not _is_sha256(declared):
            errors.append(
                f"ATTEMPT[{index}]_REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_INVALID"
            )
        elif binding_sha is not None and declared != binding_sha:
            errors.append(
                f"ATTEMPT[{index}]_REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_MISMATCH"
            )


def _population_sha(manifest: dict[str, Any], binding_sha: str | None) -> str:
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
                    "calibrationPackageBindingSha256": binding_sha,
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
    errors = list(inherited.get("errors", []))

    if not isinstance(manifest, dict):
        errors.append("TOP_LEVEL_OBJECT_REQUIRED")
        binding_sha = None
        validation_sha = None
    else:
        if manifest.get("contract") != CONTRACT:
            errors.append(f"CONTRACT_MISMATCH:{manifest.get('contract')!r}")
        binding_sha, validation_sha = _validate_package_link(manifest, errors)
        _validate_admitted_reference_links(manifest, binding_sha, errors)

    merged_errors = sorted(set(errors))
    contract_valid = not merged_errors
    population_sha = (
        _population_sha(manifest, binding_sha)
        if isinstance(manifest, dict)
        else inherited.get("admittedPopulationManifestSha256")
    )
    may_advance = bool(
        contract_valid and inherited.get("mayAdvanceToReferenceBlindStructuralAudit") is True
    )

    return {
        **inherited,
        "contract": CONTRACT,
        "contractValid": contract_valid,
        "errors": merged_errors,
        "v2SemanticGuardPassed": contract_valid,
        "calibrationPackageBridgeVersion": BRIDGE_VERSION,
        "calibrationPackageBindingSha256": binding_sha,
        "calibrationPackageValidationResultSha256": validation_sha,
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
    rendered = v21.v2.v1.canonical_json(result) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["contractValid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
