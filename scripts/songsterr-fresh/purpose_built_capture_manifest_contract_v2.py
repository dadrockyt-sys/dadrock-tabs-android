#!/usr/bin/env python3
"""Fail-closed V2 declaration validator for a future purpose-built V6 holdout.

V2 is intentionally additive over the already-tested V1 capture-manifest
contract. It preserves V1 chronology/admission/policy rules and adds explicit
physical-reference provenance for pitch and note birth, non-holdout calibration,
independent clock/sync proof, machine-verifiable acquisition-failure evidence,
and anti-duplication identity.

This validator reads JSON declarations only. It MUST NOT open candidate audio,
reference sensor bytes, run Basic Pitch/V6, inspect correctness, or establish
structural suitability. A clean result can authorize only the separately
preregistered reference-blind raw-byte structural audit.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
V1_PATH = HERE / "purpose_built_capture_manifest_contract_v1.py"
spec = importlib.util.spec_from_file_location("purpose_built_capture_manifest_contract_v1", V1_PATH)
assert spec and spec.loader
v1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v1)

CONTRACT = "songsterr-fresh-purpose-built-capture-manifest-v2"
CALIBRATION_CONTRACT = "songsterr-fresh-purpose-built-reference-calibration-v1"
HARDWARE_CONTRACT = "songsterr-fresh-purpose-built-hardware-configuration-v1"
MAX_REFERENCE_TIMING_ERROR_SECONDS = 0.025

OBJECTIVE_ACQUISITION_FAILURE_CODES = {
    "ABSENT_REFERENCE_CHANNEL",
    "CLIPPING_LIMIT_EXCEEDED",
    "DEVICE_DISCONNECT",
    "MALFORMED_REFERENCE_STREAM",
    "MISSING_OR_CORRUPT_FILE",
    "TRANSPORT_FAILURE",
    "WRONG_SAMPLE_RATE_OR_FORMAT",
    "REFERENCE_SENSOR_DROPOUT",
    "REFERENCE_SENSOR_SATURATION",
    "CLOCK_SYNC_LOSS_OR_EXCEEDED_ERROR",
    "HARDWARE_CONFIGURATION_MISMATCH",
}

FORBIDDEN_FAILURE_EVIDENCE_TOKENS = {
    "basicpitch",
    "v6",
    "correctness",
    "precision",
    "recall",
    "modeloutput",
    "modelscore",
    "structuralrepair",
    "musicalquality",
    "badperformance",
    "playerpreference",
}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _finite_nonnegative_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and value >= 0
        and value == value
        and value not in (float("inf"), float("-inf"))
    )


def _normalize_token(value: str) -> str:
    return "".join(ch.lower() for ch in value if ch.isalnum())


def _scan_values_for_forbidden_tokens(
    value: Any,
    path: tuple[str, ...] = (),
) -> list[str]:
    """Scan declaration string values, never schema key names.

    Keys such as ``usedModelOutputs`` are required fail-closed declarations and
    must not trigger the semantic scanner merely by existing. Free-text/string
    values are still checked so a failure record cannot smuggle model or
    correctness observations into acquisition QA.
    """
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            findings.extend(
                _scan_values_for_forbidden_tokens(child, path + (str(key),))
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                _scan_values_for_forbidden_tokens(child, path + (str(index),))
            )
    elif isinstance(value, str):
        normalized = _normalize_token(value)
        if any(token in normalized for token in FORBIDDEN_FAILURE_EVIDENCE_TOKENS):
            findings.append(".".join(path) or "<value>")
    return findings


def _validate_source(
    source: Any,
    prefix: str,
    errors: list[str],
    *,
    require_not_audio_derived: bool = False,
) -> None:
    if not isinstance(source, dict):
        errors.append(f"{prefix}_OBJECT_REQUIRED")
        return
    if not _nonempty(source.get("path")):
        errors.append(f"{prefix}_PATH_REQUIRED")
    if not v1._is_sha256(source.get("sha256")):
        errors.append(f"{prefix}_SHA256_INVALID")
    if (
        require_not_audio_derived
        and source.get("derivedFromEvaluatedAudio") is not False
    ):
        errors.append(f"{prefix}_MUST_DECLARE_NOT_DERIVED_FROM_EVALUATED_AUDIO")


def _validate_hardware(
    corpus: dict[str, Any],
    errors: list[str],
) -> tuple[str | None, str | None]:
    hardware = corpus.get("hardware")
    if not isinstance(hardware, dict):
        errors.append("CORPUS_HARDWARE_OBJECT_REQUIRED")
        return None, None

    config = hardware.get("configuration")
    if not isinstance(config, dict):
        errors.append("HARDWARE_CONFIGURATION_OBJECT_REQUIRED")
        return None, None

    if config.get("contract") != HARDWARE_CONTRACT:
        errors.append(
            f"HARDWARE_CONFIGURATION_CONTRACT_MISMATCH:{config.get('contract')!r}"
        )
    for key in ("configurationId", "path", "firmwareVersion"):
        if not _nonempty(config.get(key)):
            errors.append(f"HARDWARE_CONFIGURATION_{key.upper()}_REQUIRED")
    config_sha = config.get("sha256")
    if not v1._is_sha256(config_sha):
        errors.append("HARDWARE_CONFIGURATION_SHA256_INVALID")
        config_sha = None

    path_ids = {
        "evaluatedAudioPathId": hardware.get("evaluatedAudioPathId"),
        "pitchEvidencePathId": hardware.get("pitchEvidencePathId"),
        "birthEvidencePathId": hardware.get("birthEvidencePathId"),
    }
    for key, value in path_ids.items():
        if not _nonempty(value):
            errors.append(f"HARDWARE_{key.upper()}_REQUIRED")
    valid_ids = [value.strip() for value in path_ids.values() if _nonempty(value)]
    if len(valid_ids) != len(set(valid_ids)):
        errors.append("HARDWARE_EVALUATED_PITCH_BIRTH_PATH_IDS_MUST_BE_DISTINCT")

    if hardware.get("evaluatedAudioIndependentFromPitchEvidence") is not True:
        errors.append("HARDWARE_AUDIO_PITCH_INDEPENDENCE_REQUIRED")
    if hardware.get("evaluatedAudioIndependentFromBirthEvidence") is not True:
        errors.append("HARDWARE_AUDIO_BIRTH_INDEPENDENCE_REQUIRED")

    setup = hardware.get("instrumentSetup")
    if not isinstance(setup, dict):
        errors.append("HARDWARE_INSTRUMENT_SETUP_OBJECT_REQUIRED")
    else:
        if not v1._is_sha256(setup.get("setupSha256")):
            errors.append("HARDWARE_INSTRUMENT_SETUP_SHA256_INVALID")
        tuning = setup.get("openStringMidi")
        if (
            not isinstance(tuning, list)
            or len(tuning) != 6
            or any(
                not isinstance(note, int)
                or isinstance(note, bool)
                or not 0 <= note <= 127
                for note in (tuning if isinstance(tuning, list) else [])
            )
        ):
            errors.append("HARDWARE_INSTRUMENT_SETUP_OPEN_STRING_MIDI_INVALID")

    return config_sha, config.get("firmwareVersion")


def _validate_calibration(
    corpus: dict[str, Any],
    errors: list[str],
) -> tuple[str | None, str | None]:
    calibration = corpus.get("referenceCalibration")
    if not isinstance(calibration, dict):
        errors.append("REFERENCE_CALIBRATION_OBJECT_REQUIRED")
        return None, None
    if calibration.get("contract") != CALIBRATION_CONTRACT:
        errors.append(
            f"REFERENCE_CALIBRATION_CONTRACT_MISMATCH:{calibration.get('contract')!r}"
        )
    calibration_id = calibration.get("calibrationId")
    if not _nonempty(calibration_id):
        errors.append("REFERENCE_CALIBRATION_ID_REQUIRED")
        calibration_id = None
    if not _nonempty(calibration.get("path")):
        errors.append("REFERENCE_CALIBRATION_PATH_REQUIRED")
    calibration_sha = calibration.get("sha256")
    if not v1._is_sha256(calibration_sha):
        errors.append("REFERENCE_CALIBRATION_SHA256_INVALID")
        calibration_sha = None
    if calibration.get("usedHoldoutData") is not False:
        errors.append("REFERENCE_CALIBRATION_MUST_NOT_USE_HOLDOUT_DATA")
    if calibration.get("usedModelOutputs") is not False:
        errors.append("REFERENCE_CALIBRATION_MUST_NOT_USE_MODEL_OUTPUTS")
    if calibration.get("derivedFromEvaluatedAudio") is not False:
        errors.append("REFERENCE_CALIBRATION_MUST_NOT_BE_DERIVED_FROM_EVALUATED_AUDIO")
    error_seconds = calibration.get("maxAbsoluteOnsetErrorSeconds")
    if not _finite_nonnegative_number(error_seconds):
        errors.append("REFERENCE_CALIBRATION_MAX_ABSOLUTE_ONSET_ERROR_INVALID")
    elif float(error_seconds) > MAX_REFERENCE_TIMING_ERROR_SECONDS:
        errors.append(
            "REFERENCE_CALIBRATION_TIMING_ERROR_EXCEEDS_BOUND:"
            f"{float(error_seconds):.9f}>{MAX_REFERENCE_TIMING_ERROR_SECONDS:.9f}"
        )
    return calibration_id, calibration_sha


def _validate_clock_sync(corpus: dict[str, Any], errors: list[str]) -> str | None:
    sync = corpus.get("clockSync")
    if not isinstance(sync, dict):
        errors.append("CLOCK_SYNC_OBJECT_REQUIRED")
        return None
    for key in ("syncId", "sourceId", "path"):
        if not _nonempty(sync.get(key)):
            errors.append(f"CLOCK_SYNC_{key.upper()}_REQUIRED")
    if not v1._is_sha256(sync.get("sha256")):
        errors.append("CLOCK_SYNC_SHA256_INVALID")
    if sync.get("derivedFromEvaluatedAudio") is not False:
        errors.append("CLOCK_SYNC_MUST_NOT_BE_DERIVED_FROM_EVALUATED_AUDIO")
    if sync.get("usedModelOutputs") is not False:
        errors.append("CLOCK_SYNC_MUST_NOT_USE_MODEL_OUTPUTS")
    max_error = sync.get("maxAbsoluteErrorSeconds")
    if not _finite_nonnegative_number(max_error):
        errors.append("CLOCK_SYNC_MAX_ABSOLUTE_ERROR_INVALID")
    elif float(max_error) > MAX_REFERENCE_TIMING_ERROR_SECONDS:
        errors.append(
            "CLOCK_SYNC_ERROR_EXCEEDS_BOUND:"
            f"{float(max_error):.9f}>{MAX_REFERENCE_TIMING_ERROR_SECONDS:.9f}"
        )
    return sync.get("syncId") if _nonempty(sync.get("syncId")) else None


def _validate_failure_evidence(
    attempt: dict[str, Any],
    prefix: str,
    allowed_reasons: set[str],
    errors: list[str],
) -> None:
    qa = attempt.get("acquisitionQa")
    if not isinstance(qa, dict):
        return
    status = qa.get("status")
    reason = qa.get("reason")
    evidence = qa.get("evidence")

    if status == "PASS":
        if evidence not in (None, {}):
            errors.append(f"{prefix}_PASS_MUST_NOT_CARRY_FAILURE_EVIDENCE")
        return
    if status != "FAIL":
        return
    if reason not in allowed_reasons:
        return
    if not isinstance(evidence, dict):
        errors.append(f"{prefix}_FAILURE_EVIDENCE_OBJECT_REQUIRED")
        return
    if evidence.get("machineVerifiable") is not True:
        errors.append(f"{prefix}_FAILURE_EVIDENCE_MUST_BE_MACHINE_VERIFIABLE")
    if not _nonempty(evidence.get("evidenceType")):
        errors.append(f"{prefix}_FAILURE_EVIDENCE_TYPE_REQUIRED")
    if not _nonempty(evidence.get("path")):
        errors.append(f"{prefix}_FAILURE_EVIDENCE_PATH_REQUIRED")
    if not v1._is_sha256(evidence.get("sha256")):
        errors.append(f"{prefix}_FAILURE_EVIDENCE_SHA256_INVALID")
    if evidence.get("derivedFromEvaluatedAudioCorrectness") is not False:
        errors.append(
            f"{prefix}_FAILURE_EVIDENCE_MUST_NOT_USE_EVALUATED_AUDIO_CORRECTNESS"
        )
    if evidence.get("usedModelOutputs") is not False:
        errors.append(f"{prefix}_FAILURE_EVIDENCE_MUST_NOT_USE_MODEL_OUTPUTS")
    for finding in _scan_values_for_forbidden_tokens(evidence):
        errors.append(f"{prefix}_FORBIDDEN_FAILURE_EVIDENCE_SEMANTIC:{finding}")


def _validate_attempt_extensions(
    manifest: dict[str, Any],
    config_sha: str | None,
    calibration_id: str | None,
    sync_id: str | None,
    errors: list[str],
) -> tuple[list[dict[str, Any]], set[str]]:
    attempts = manifest.get("attempts")
    if not isinstance(attempts, list):
        return [], set()

    declared_reasons = manifest.get("allowedAcquisitionFailureReasons")
    allowed_reasons = {
        reason.strip()
        for reason in declared_reasons
        if _nonempty(reason)
    } if isinstance(declared_reasons, list) else set()
    for reason in sorted(allowed_reasons - OBJECTIVE_ACQUISITION_FAILURE_CODES):
        errors.append(f"ACQUISITION_FAILURE_REASON_NOT_OBJECTIVE_V2:{reason}")

    admitted: list[dict[str, Any]] = []
    all_underlying_ids: set[str] = set()
    admitted_underlying_ids: set[str] = set()

    for index, attempt in enumerate(attempts):
        if not isinstance(attempt, dict):
            continue
        prefix = f"ATTEMPT[{index}]"
        _validate_failure_evidence(attempt, prefix, allowed_reasons, errors)

        underlying_id = attempt.get("underlyingPerformanceId")
        underlying_key: str | None = None
        if not _nonempty(underlying_id):
            errors.append(f"{prefix}_UNDERLYING_PERFORMANCE_ID_REQUIRED")
        else:
            underlying_key = underlying_id.strip()
            if underlying_key in all_underlying_ids:
                errors.append(
                    "DUPLICATE_UNDERLYING_PERFORMANCE_ID_ACROSS_ATTEMPTS:"
                    f"{underlying_key}"
                )
            all_underlying_ids.add(underlying_key)

        if attempt.get("admitted") is not True:
            continue
        admitted.append(attempt)
        if underlying_key is not None:
            admitted_underlying_ids.add(underlying_key)

        _validate_source(
            attempt.get("evaluatedAudio"),
            f"{prefix}_EVALUATED_AUDIO",
            errors,
        )
        _validate_source(
            attempt.get("pitchEvidence"),
            f"{prefix}_PITCH_EVIDENCE",
            errors,
            require_not_audio_derived=True,
        )
        _validate_source(
            attempt.get("birthEvidence"),
            f"{prefix}_BIRTH_EVIDENCE",
            errors,
            require_not_audio_derived=True,
        )

        pitch = (
            attempt.get("pitchEvidence")
            if isinstance(attempt.get("pitchEvidence"), dict)
            else {}
        )
        birth = (
            attempt.get("birthEvidence")
            if isinstance(attempt.get("birthEvidence"), dict)
            else {}
        )
        audio = (
            attempt.get("evaluatedAudio")
            if isinstance(attempt.get("evaluatedAudio"), dict)
            else {}
        )
        source_paths = [audio.get("path"), pitch.get("path"), birth.get("path")]
        nonempty_paths = [path.strip() for path in source_paths if _nonempty(path)]
        if len(nonempty_paths) != len(set(nonempty_paths)):
            errors.append(
                f"{prefix}_AUDIO_PITCH_BIRTH_SOURCE_PATHS_MUST_BE_DISTINCT"
            )
        source_hashes = [
            audio.get("sha256"),
            pitch.get("sha256"),
            birth.get("sha256"),
        ]
        valid_hashes = [value for value in source_hashes if v1._is_sha256(value)]
        if len(valid_hashes) != len(set(valid_hashes)):
            errors.append(
                f"{prefix}_AUDIO_PITCH_BIRTH_SOURCE_HASHES_MUST_BE_DISTINCT"
            )

        reference = attempt.get("reference")
        if not isinstance(reference, dict):
            errors.append(f"{prefix}_REFERENCE_OBJECT_REQUIRED")
            continue
        if reference.get("pitchDerivedFromEvaluatedAudio") is not False:
            errors.append(
                f"{prefix}_REFERENCE_PITCH_MUST_NOT_BE_DERIVED_FROM_EVALUATED_AUDIO"
            )
        if reference.get("birthDerivedFromEvaluatedAudio") is not False:
            errors.append(
                f"{prefix}_REFERENCE_BIRTH_MUST_NOT_BE_DERIVED_FROM_EVALUATED_AUDIO"
            )
        if reference.get("usedModelOutputs") is not False:
            errors.append(f"{prefix}_REFERENCE_MUST_NOT_USE_MODEL_OUTPUTS")
        if config_sha is not None and reference.get("configurationSha256") != config_sha:
            errors.append(f"{prefix}_REFERENCE_HARDWARE_CONFIGURATION_MISMATCH")
        if calibration_id is not None and reference.get("calibrationId") != calibration_id:
            errors.append(f"{prefix}_REFERENCE_CALIBRATION_ID_MISMATCH")
        if sync_id is not None and reference.get("clockSyncId") != sync_id:
            errors.append(f"{prefix}_REFERENCE_CLOCK_SYNC_ID_MISMATCH")
        if reference.get("pitchEvidenceSha256") != pitch.get("sha256"):
            errors.append(f"{prefix}_REFERENCE_PITCH_EVIDENCE_HASH_MISMATCH")
        if reference.get("birthEvidenceSha256") != birth.get("sha256"):
            errors.append(f"{prefix}_REFERENCE_BIRTH_EVIDENCE_HASH_MISMATCH")
        if not v1._is_sha256(reference.get("derivationConfigurationSha256")):
            errors.append(
                f"{prefix}_REFERENCE_DERIVATION_CONFIGURATION_SHA256_INVALID"
            )
        if not _nonempty(reference.get("eventSemanticsVersion")):
            errors.append(f"{prefix}_REFERENCE_EVENT_SEMANTICS_VERSION_REQUIRED")

    return admitted, admitted_underlying_ids


def _v1_projection(manifest: Any) -> Any:
    """Project a V2 declaration into the frozen V1 shape for proven base checks."""
    if not isinstance(manifest, dict):
        return manifest
    projected = copy.deepcopy(manifest)
    projected["contract"] = v1.CONTRACT
    corpus = projected.get("corpus")
    if isinstance(corpus, dict):
        hardware = corpus.get("hardware")
        if isinstance(hardware, dict):
            config = hardware.get("configuration")
            if isinstance(config, dict):
                hardware["configurationSha256"] = config.get("sha256")
                hardware["firmwareVersion"] = config.get("firmwareVersion")
            hardware["independentReferencePathId"] = (
                f"{hardware.get('pitchEvidencePathId', '')}+"
                f"{hardware.get('birthEvidencePathId', '')}"
            )
            hardware["evaluatedAudioIndependentFromReference"] = (
                hardware.get("evaluatedAudioIndependentFromPitchEvidence") is True
                and hardware.get("evaluatedAudioIndependentFromBirthEvidence") is True
            )
    return projected


def validate_manifest(manifest: Any) -> dict[str, Any]:
    base_result = v1.validate_manifest(_v1_projection(manifest))
    errors = list(base_result.get("errors", []))

    if not isinstance(manifest, dict):
        return {
            **base_result,
            "contract": CONTRACT,
            "contractValid": False,
            "errors": sorted(set(errors + ["TOP_LEVEL_OBJECT_REQUIRED"])),
            "v2SemanticGuardPassed": False,
            "mayAdvanceToReferenceBlindStructuralAudit": False,
        }
    if manifest.get("contract") != CONTRACT:
        errors.append(f"CONTRACT_MISMATCH:{manifest.get('contract')!r}")

    corpus = manifest.get("corpus")
    config_sha = None
    calibration_id = None
    calibration_sha = None
    sync_id = None
    if not isinstance(corpus, dict):
        errors.append("CORPUS_OBJECT_REQUIRED")
    else:
        config_sha, _ = _validate_hardware(corpus, errors)
        calibration_id, calibration_sha = _validate_calibration(corpus, errors)
        sync_id = _validate_clock_sync(corpus, errors)

    admitted, underlying_ids = _validate_attempt_extensions(
        manifest,
        config_sha,
        calibration_id,
        sync_id,
        errors,
    )

    merged_errors = sorted(set(errors))
    contract_valid = not merged_errors
    declared_blockers = base_result.get("declaredStructuralBlockers", [])
    may_advance = contract_valid and bool(admitted) and not declared_blockers

    population_rows: list[dict[str, Any]] = []
    for attempt in admitted:
        audio = attempt.get("evaluatedAudio") or {}
        pitch = attempt.get("pitchEvidence") or {}
        birth = attempt.get("birthEvidence") or {}
        reference = attempt.get("reference") or {}
        population_rows.append(
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
            }
        )
    population_rows.sort(
        key=lambda row: (str(row["slotId"]), str(row["attemptId"]))
    )
    population_sha = v1.sha256_bytes(
        v1.canonical_json(population_rows).encode("utf-8")
    )

    return {
        **base_result,
        "contract": CONTRACT,
        "contractValid": contract_valid,
        "errors": merged_errors,
        "v2SemanticGuardPassed": contract_valid,
        "objectiveAcquisitionFailureVocabularyVersion": (
            "purpose-built-v2-objective-acquisition-failures-2026-09-14"
        ),
        "maxReferenceTimingErrorSeconds": MAX_REFERENCE_TIMING_ERROR_SECONDS,
        "admittedUnderlyingPerformanceCount": len(underlying_ids),
        "admittedPopulationManifestSha256": population_sha,
        "mayAdvanceToReferenceBlindStructuralAudit": may_advance,
        "authoritativeStructuralSuitabilityEstablished": False,
        "basicPitchAuthorized": False,
        "v6Authorized": False,
        "correctnessAuthorized": False,
        "policyBoundary": dict(v1.REQUIRED_POLICY_BOUNDARY),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="Path to V2 capture manifest JSON")
    parser.add_argument(
        "--output",
        help="Optional deterministic validation-result JSON path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    result = validate_manifest(manifest)
    rendered = v1.canonical_json(result) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["contractValid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
