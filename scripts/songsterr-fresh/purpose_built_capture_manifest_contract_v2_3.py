#!/usr/bin/env python3
"""Purpose-built capture-manifest V2.3 structural-audit input binding.

V2.3 is declaration-only identity plumbing over accepted V2.2. It does not
open structural-audit files, evaluated audio, calibration files, or model
outputs. It binds each admitted performance to the exact future structural
input byte identities that a later structural audit must verify.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
V22_PATH = HERE / "purpose_built_capture_manifest_contract_v2_2.py"
spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_manifest_contract_v2_2", V22_PATH
)
assert spec and spec.loader
v22 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v22)

CONTRACT = "songsterr-fresh-purpose-built-capture-manifest-v2.3"
STRUCTURAL_INPUT_BINDING_CONTRACT = (
    "songsterr-fresh-purpose-built-structural-audit-input-binding-v1"
)
POPULATION_IDENTITY_VERSION = (
    "capture-manifest-v2.3-structural-audit-input-binding-v1"
)
EVENT_SEMANTICS_VERSION = "physical-reference-semantics-v1"

STRUCTURAL_SOURCE_SHA_FIELDS = (
    "hardwareSourceSha256",
    "birthStreamSha256",
    "pitchLatchStreamSha256",
    "clockSyncSourceSha256",
)


def canonical_json_bytes(value: Any) -> bytes:
    return v22.canonical_json_bytes(value)


def sha256_bytes(data: bytes) -> str:
    return v22.sha256_bytes(data)


def _canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _is_sha256(value: Any) -> bool:
    return v22._is_sha256(value)


def _nonempty(value: Any) -> bool:
    return v22._nonempty(value)


def _valid_open_string_midi(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 6
        and all(
            isinstance(note, int)
            and not isinstance(note, bool)
            and 0 <= note <= 127
            for note in value
        )
    )


def _validate_structural_binding(
    *,
    attempt: dict[str, Any],
    index: int,
    corpus: dict[str, Any],
    package_binding_sha: str | None,
    decoder_configuration_sha: str | None,
    errors: list[str],
) -> tuple[str | None, dict[str, Any] | None]:
    prefix = f"ATTEMPT[{index}]"
    reference = attempt.get("reference")
    if not isinstance(reference, dict):
        # Inherited V2.2 already reports the missing reference object.
        return None, None

    binding = reference.get("structuralAuditInputs")
    binding_sha = reference.get("structuralAuditInputsSha256")
    if not isinstance(binding, dict):
        errors.append(f"{prefix}_STRUCTURAL_AUDIT_INPUTS_OBJECT_REQUIRED")
        return None, None
    if not _is_sha256(binding_sha):
        errors.append(f"{prefix}_STRUCTURAL_AUDIT_INPUTS_SHA256_INVALID")
        binding_sha = None
    else:
        try:
            actual_binding_sha = _canonical_sha256(binding)
        except (TypeError, ValueError):
            errors.append(f"{prefix}_STRUCTURAL_AUDIT_INPUTS_CANONICALIZATION_FAILED")
        else:
            if actual_binding_sha != binding_sha:
                errors.append(f"{prefix}_STRUCTURAL_AUDIT_INPUTS_SHA256_MISMATCH")

    if binding.get("contract") != STRUCTURAL_INPUT_BINDING_CONTRACT:
        errors.append(f"{prefix}_STRUCTURAL_AUDIT_INPUTS_CONTRACT_MISMATCH")

    for field in STRUCTURAL_SOURCE_SHA_FIELDS:
        if not _is_sha256(binding.get(field)):
            errors.append(f"{prefix}_STRUCTURAL_AUDIT_INPUTS_{field.upper()}_INVALID")

    for field in (
        "attemptId",
        "slotId",
        "underlyingPerformanceId",
        "playerId",
        "exerciseId",
        "category",
    ):
        expected = attempt.get(field)
        actual = binding.get(field)
        if not _nonempty(actual):
            errors.append(f"{prefix}_STRUCTURAL_AUDIT_INPUTS_{field.upper()}_REQUIRED")
        elif actual != expected:
            errors.append(f"{prefix}_STRUCTURAL_AUDIT_INPUTS_{field.upper()}_MISMATCH")

    hardware = corpus.get("hardware") if isinstance(corpus, dict) else None
    configuration = hardware.get("configuration") if isinstance(hardware, dict) else None
    instrument_setup = hardware.get("instrumentSetup") if isinstance(hardware, dict) else None
    calibration = corpus.get("referenceCalibration") if isinstance(corpus, dict) else None
    clock_sync = corpus.get("clockSync") if isinstance(corpus, dict) else None

    expected_configuration_id = (
        configuration.get("configurationId") if isinstance(configuration, dict) else None
    )
    expected_configuration_sha = (
        configuration.get("sha256") if isinstance(configuration, dict) else None
    )
    expected_setup_sha = (
        instrument_setup.get("setupSha256") if isinstance(instrument_setup, dict) else None
    )
    expected_open_midi = (
        instrument_setup.get("openStringMidi") if isinstance(instrument_setup, dict) else None
    )
    expected_calibration_id = (
        calibration.get("calibrationId") if isinstance(calibration, dict) else None
    )
    expected_clock_sync_id = (
        clock_sync.get("syncId") if isinstance(clock_sync, dict) else None
    )

    identity_checks = (
        ("CONFIGURATION_ID", "configurationId", expected_configuration_id),
        ("CONFIGURATION_SHA256", "configurationSha256", expected_configuration_sha),
        ("INSTRUMENT_SETUP_SHA256", "instrumentSetupSha256", expected_setup_sha),
        ("CALIBRATION_ID", "calibrationId", expected_calibration_id),
        ("CLOCK_SYNC_ID", "clockSyncId", expected_clock_sync_id),
        (
            "PITCH_EVIDENCE_SHA256",
            "pitchEvidenceSha256",
            reference.get("pitchEvidenceSha256"),
        ),
        (
            "BIRTH_EVIDENCE_SHA256",
            "birthEvidenceSha256",
            reference.get("birthEvidenceSha256"),
        ),
        ("REFERENCE_ARTIFACT_SHA256", "referenceArtifactSha256", reference.get("sha256")),
        (
            "CALIBRATION_PACKAGE_BINDING_SHA256",
            "calibrationPackageBindingSha256",
            reference.get("calibrationPackageBindingSha256"),
        ),
        (
            "DERIVATION_CONFIGURATION_SHA256",
            "derivationConfigurationSha256",
            reference.get("derivationConfigurationSha256"),
        ),
    )
    for label, field, expected in identity_checks:
        actual = binding.get(field)
        if field.endswith("Sha256") and not _is_sha256(actual):
            errors.append(f"{prefix}_STRUCTURAL_AUDIT_INPUTS_{label}_INVALID")
        elif field in ("configurationId", "calibrationId", "clockSyncId") and not _nonempty(actual):
            errors.append(f"{prefix}_STRUCTURAL_AUDIT_INPUTS_{label}_REQUIRED")
        elif actual != expected:
            errors.append(f"{prefix}_STRUCTURAL_AUDIT_INPUTS_{label}_MISMATCH")

    if package_binding_sha is not None and binding.get("calibrationPackageBindingSha256") != package_binding_sha:
        errors.append(
            f"{prefix}_STRUCTURAL_AUDIT_INPUTS_PACKAGE_BINDING_CORPUS_MISMATCH"
        )
    if decoder_configuration_sha is not None and binding.get("derivationConfigurationSha256") != decoder_configuration_sha:
        errors.append(
            f"{prefix}_STRUCTURAL_AUDIT_INPUTS_DECODER_CONFIGURATION_MISMATCH"
        )

    open_midi = binding.get("openStringMidi")
    if not _valid_open_string_midi(open_midi):
        errors.append(f"{prefix}_STRUCTURAL_AUDIT_INPUTS_OPEN_STRING_MIDI_INVALID")
    elif open_midi != expected_open_midi:
        errors.append(f"{prefix}_STRUCTURAL_AUDIT_INPUTS_OPEN_STRING_MIDI_MISMATCH")

    event_semantics = binding.get("eventSemanticsVersion")
    if event_semantics != EVENT_SEMANTICS_VERSION:
        errors.append(
            f"{prefix}_STRUCTURAL_AUDIT_INPUTS_EVENT_SEMANTICS_VERSION_INVALID"
        )
    if event_semantics != reference.get("eventSemanticsVersion"):
        errors.append(
            f"{prefix}_STRUCTURAL_AUDIT_INPUTS_EVENT_SEMANTICS_VERSION_MISMATCH"
        )

    return binding_sha, binding


def validate_manifest(manifest: Any) -> dict[str, Any]:
    projected = manifest
    if isinstance(manifest, dict):
        projected = copy.deepcopy(manifest)
        projected["contract"] = v22.CONTRACT

    inherited = v22.validate_manifest(projected)
    errors = list(inherited.get("errors", []))
    binding_rows: list[dict[str, Any]] = []
    binding_map: list[dict[str, Any]] = []

    if not isinstance(manifest, dict):
        errors.append("TOP_LEVEL_OBJECT_REQUIRED")
    else:
        if manifest.get("contract") != CONTRACT:
            errors.append(f"CONTRACT_MISMATCH:{manifest.get('contract')!r}")

        corpus = manifest.get("corpus")
        if not isinstance(corpus, dict):
            corpus = {}

        package_binding_sha = inherited.get("calibrationPackageBindingSha256")
        decoder_configuration_sha = inherited.get(
            "calibrationPackageDecoderConfigurationSha256"
        )
        attempts = manifest.get("attempts")
        if isinstance(attempts, list):
            for index, attempt in enumerate(attempts):
                if not isinstance(attempt, dict):
                    continue
                reference = attempt.get("reference")
                if attempt.get("admitted") is not True:
                    if isinstance(reference, dict) and (
                        "structuralAuditInputs" in reference
                        or "structuralAuditInputsSha256" in reference
                    ):
                        errors.append(
                            f"ATTEMPT[{index}]_NONADMITTED_STRUCTURAL_AUDIT_INPUTS_FORBIDDEN"
                        )
                    continue

                binding_sha, _ = _validate_structural_binding(
                    attempt=attempt,
                    index=index,
                    corpus=corpus,
                    package_binding_sha=package_binding_sha,
                    decoder_configuration_sha=decoder_configuration_sha,
                    errors=errors,
                )
                if binding_sha is not None:
                    row = {
                        "attemptId": attempt.get("attemptId"),
                        "slotId": attempt.get("slotId"),
                        "underlyingPerformanceId": attempt.get("underlyingPerformanceId"),
                        "structuralAuditInputsSha256": binding_sha,
                    }
                    binding_rows.append(row)
                    binding_map.append(
                        {
                            "attemptId": attempt.get("attemptId"),
                            "structuralAuditInputsSha256": binding_sha,
                        }
                    )

    binding_rows.sort(key=lambda row: (str(row["slotId"]), str(row["attemptId"])))
    binding_map.sort(key=lambda row: str(row["attemptId"]))

    inherited_population_sha = inherited.get("admittedPopulationManifestSha256")
    population_sha = None
    if inherited_population_sha is not None:
        population_sha = _canonical_sha256(
            {
                "populationIdentityVersion": POPULATION_IDENTITY_VERSION,
                "inheritedV22AdmittedPopulationManifestSha256": inherited_population_sha,
                "structuralAuditInputBindings": binding_rows,
            }
        )

    merged_errors = sorted(set(errors))
    contract_valid = not merged_errors
    may_advance = bool(
        contract_valid
        and inherited.get("mayAdvanceToReferenceBlindStructuralAudit") is True
    )

    return {
        **inherited,
        "contract": CONTRACT,
        "contractValid": contract_valid,
        "errors": merged_errors,
        "v23SemanticGuardPassed": contract_valid,
        "structuralAuditInputBindingContract": STRUCTURAL_INPUT_BINDING_CONTRACT,
        "structuralAuditInputBindingCount": len(binding_rows),
        "structuralAuditInputBindings": binding_map,
        "populationIdentityVersion": POPULATION_IDENTITY_VERSION,
        "inheritedV22AdmittedPopulationManifestSha256": inherited_population_sha,
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
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="Path to V2.3 capture manifest JSON")
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
