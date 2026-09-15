#!/usr/bin/env python3
"""Fail-closed purpose-built reference calibration package provenance V1.

Current use is synthetic/software-only. This validator never authorizes real
calibration, holdout capture, Basic Pitch, V6, correctness, or delivery.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
from typing import Any

CONTRACT = "songsterr-fresh-purpose-built-reference-calibration-package-v1"
MAX_REFERENCE_TIMING_ERROR_SECONDS = 0.025
RAW_ROLES = {
    "physical_pitch_state",
    "event_birth",
    "clock_sync",
    "sensor_health",
}
REQUIRED_RAW_ROLES = {"physical_pitch_state", "event_birth", "clock_sync"}
DERIVED_ROLES = {
    "physical_string_fret_mapping",
    "event_birth_calibration",
    "hardware_timing_proof",
    "technique_capability_matrix",
    "acquisition_qa_configuration",
}
AUTHORIZATION_BOUNDARY = {
    "basicPitchAuthorized": False,
    "v6Authorized": False,
    "correctnessAuthorized": False,
    "modelValidationComplete": False,
    "customerEligibleEvents": 0,
    "mayAdvanceDelivery": False,
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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and value == value.lower()
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _finite_nonnegative(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and float(value) >= 0.0
    )


def _safe_path(root: Path, value: Any, label: str, errors: list[str]) -> Path | None:
    if not _nonempty(value):
        errors.append(f"{label}_PATH_REQUIRED")
        return None
    raw = value.strip()
    if "\\" in raw:
        errors.append(f"{label}_PATH_MUST_BE_POSIX_RELATIVE")
        return None
    posix = PurePosixPath(raw)
    if posix.is_absolute() or not posix.parts or any(part in ("", ".", "..") for part in posix.parts):
        errors.append(f"{label}_PATH_UNSAFE")
        return None
    root_resolved = root.resolve()
    candidate = (root_resolved / Path(*posix.parts)).resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError:
        errors.append(f"{label}_PATH_ESCAPES_PACKAGE_ROOT")
        return None
    return candidate


def _verify_file(
    root: Path,
    obj: Any,
    label: str,
    errors: list[str],
    used_paths: set[str],
    verified: list[dict[str, str]],
) -> None:
    if not isinstance(obj, dict):
        errors.append(f"{label}_OBJECT_REQUIRED")
        return
    path_value = obj.get("path")
    sha_value = obj.get("sha256")
    path = _safe_path(root, path_value, label, errors)
    if not _is_sha256(sha_value):
        errors.append(f"{label}_SHA256_INVALID")
    if _nonempty(path_value):
        key = path_value.strip()
        if key in used_paths:
            errors.append(f"DUPLICATE_PACKAGE_PATH:{key}")
        used_paths.add(key)
    if path is None or not _is_sha256(sha_value):
        return
    if not path.is_file():
        errors.append(f"{label}_FILE_MISSING")
        return
    actual = sha256_file(path)
    if actual != sha_value:
        errors.append(f"{label}_SHA256_MISMATCH")
        return
    verified.append({"path": path_value.strip(), "sha256": actual})


def _sorted_binding(manifest: dict[str, Any]) -> dict[str, Any]:
    binding = copy.deepcopy(manifest)
    binding["hardwareIdentities"] = sorted(
        binding["hardwareIdentities"], key=lambda x: (x["componentId"], x["immutableIdentity"])
    )
    binding["rawSources"] = sorted(binding["rawSources"], key=lambda x: x["sourceId"])
    for source in binding["rawSources"]:
        source["roles"] = sorted(source["roles"])
    binding["derivedOutputs"] = sorted(binding["derivedOutputs"], key=lambda x: x["outputId"])
    return binding


def validate_package(manifest: Any, package_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    verified: list[dict[str, str]] = []
    used_paths: set[str] = set()

    if not isinstance(manifest, dict):
        errors.append("TOP_LEVEL_OBJECT_REQUIRED")
        manifest = {}
    if manifest.get("contract") != CONTRACT:
        errors.append(f"CONTRACT_MISMATCH:{manifest.get('contract')!r}")
    if not _nonempty(manifest.get("calibrationId")):
        errors.append("CALIBRATION_ID_REQUIRED")
    for field in ("usedHoldoutData", "usedModelOutputs", "derivedFromEvaluatedAudio"):
        if manifest.get(field) is not False:
            errors.append(f"{field.upper()}_MUST_BE_FALSE")
    timing = manifest.get("maxAbsoluteOnsetErrorSeconds")
    if not _finite_nonnegative(timing):
        errors.append("MAX_ABSOLUTE_ONSET_ERROR_INVALID")
    elif float(timing) > MAX_REFERENCE_TIMING_ERROR_SECONDS:
        errors.append("MAX_ABSOLUTE_ONSET_ERROR_EXCEEDS_0_025")

    hardware = manifest.get("hardwareConfiguration")
    if not isinstance(hardware, dict):
        errors.append("HARDWARE_CONFIGURATION_OBJECT_REQUIRED")
    else:
        if not _nonempty(hardware.get("configurationId")):
            errors.append("HARDWARE_CONFIGURATION_ID_REQUIRED")
        if not _nonempty(hardware.get("firmwareVersion")):
            errors.append("HARDWARE_CONFIGURATION_FIRMWARE_VERSION_REQUIRED")
        _verify_file(package_root, hardware, "HARDWARE_CONFIGURATION", errors, used_paths, verified)

    if not _is_sha256(manifest.get("instrumentSetupSha256")):
        errors.append("INSTRUMENT_SETUP_SHA256_INVALID")

    identities = manifest.get("hardwareIdentities")
    component_ids: set[str] = set()
    immutable_ids: set[str] = set()
    if not isinstance(identities, list) or not identities:
        errors.append("HARDWARE_IDENTITIES_NONEMPTY_LIST_REQUIRED")
    else:
        for i, item in enumerate(identities):
            label = f"HARDWARE_IDENTITY[{i}]"
            if not isinstance(item, dict):
                errors.append(f"{label}_OBJECT_REQUIRED")
                continue
            for key in ("componentId", "immutableIdentity", "role"):
                if not _nonempty(item.get(key)):
                    errors.append(f"{label}_{key.upper()}_REQUIRED")
            if _nonempty(item.get("componentId")):
                value = item["componentId"].strip()
                if value in component_ids:
                    errors.append(f"DUPLICATE_HARDWARE_COMPONENT_ID:{value}")
                component_ids.add(value)
            if _nonempty(item.get("immutableIdentity")):
                value = item["immutableIdentity"].strip()
                if value in immutable_ids:
                    errors.append(f"DUPLICATE_HARDWARE_IMMUTABLE_IDENTITY:{value}")
                immutable_ids.add(value)

    topology = manifest.get("wiringTopology")
    if not isinstance(topology, dict):
        errors.append("WIRING_TOPOLOGY_OBJECT_REQUIRED")
    else:
        if not _nonempty(topology.get("topologyId")):
            errors.append("WIRING_TOPOLOGY_ID_REQUIRED")
        _verify_file(package_root, topology, "WIRING_TOPOLOGY", errors, used_paths, verified)

    fixture = manifest.get("calibrationFixture")
    if not isinstance(fixture, dict):
        errors.append("CALIBRATION_FIXTURE_OBJECT_REQUIRED")
    else:
        if not _nonempty(fixture.get("fixtureId")):
            errors.append("CALIBRATION_FIXTURE_ID_REQUIRED")
        _verify_file(package_root, fixture, "CALIBRATION_FIXTURE", errors, used_paths, verified)

    decoder = manifest.get("decoder")
    if not isinstance(decoder, dict):
        errors.append("DECODER_OBJECT_REQUIRED")
    else:
        for key in ("decoderId", "softwareVersion"):
            if not _nonempty(decoder.get(key)):
                errors.append(f"DECODER_{key.upper()}_REQUIRED")
        _verify_file(package_root, decoder.get("code"), "DECODER_CODE", errors, used_paths, verified)
        _verify_file(package_root, decoder.get("configuration"), "DECODER_CONFIGURATION", errors, used_paths, verified)

    raw_sources = manifest.get("rawSources")
    raw_ids: set[str] = set()
    raw_coverage: set[str] = set()
    if not isinstance(raw_sources, list) or not raw_sources:
        errors.append("RAW_SOURCES_NONEMPTY_LIST_REQUIRED")
    else:
        for i, source in enumerate(raw_sources):
            label = f"RAW_SOURCE[{i}]"
            if not isinstance(source, dict):
                errors.append(f"{label}_OBJECT_REQUIRED")
                continue
            source_id = source.get("sourceId")
            if not _nonempty(source_id):
                errors.append(f"{label}_SOURCE_ID_REQUIRED")
            else:
                key = source_id.strip()
                if key in raw_ids:
                    errors.append(f"DUPLICATE_RAW_SOURCE_ID:{key}")
                raw_ids.add(key)
            roles = source.get("roles")
            if not isinstance(roles, list) or not roles or any(not _nonempty(r) for r in roles):
                errors.append(f"{label}_ROLES_NONEMPTY_LIST_REQUIRED")
            else:
                normalized = [r.strip() for r in roles]
                if len(normalized) != len(set(normalized)):
                    errors.append(f"{label}_DUPLICATE_ROLE")
                for role in normalized:
                    if role not in RAW_ROLES:
                        errors.append(f"{label}_UNKNOWN_ROLE:{role}")
                    else:
                        raw_coverage.add(role)
            if source.get("nonHoldout") is not True:
                errors.append(f"{label}_NON_HOLDOUT_MUST_BE_TRUE")
            if source.get("usedModelOutputs") is not False:
                errors.append(f"{label}_USED_MODEL_OUTPUTS_MUST_BE_FALSE")
            if source.get("derivedFromEvaluatedAudio") is not False:
                errors.append(f"{label}_DERIVED_FROM_EVALUATED_AUDIO_MUST_BE_FALSE")
            _verify_file(package_root, source, label, errors, used_paths, verified)
    for role in sorted(REQUIRED_RAW_ROLES - raw_coverage):
        errors.append(f"MISSING_REQUIRED_RAW_ROLE:{role}")

    outputs = manifest.get("derivedOutputs")
    output_ids: set[str] = set()
    role_counts: dict[str, int] = {role: 0 for role in DERIVED_ROLES}
    if not isinstance(outputs, list) or not outputs:
        errors.append("DERIVED_OUTPUTS_NONEMPTY_LIST_REQUIRED")
    else:
        for i, output in enumerate(outputs):
            label = f"DERIVED_OUTPUT[{i}]"
            if not isinstance(output, dict):
                errors.append(f"{label}_OBJECT_REQUIRED")
                continue
            output_id = output.get("outputId")
            if not _nonempty(output_id):
                errors.append(f"{label}_OUTPUT_ID_REQUIRED")
            else:
                key = output_id.strip()
                if key in output_ids:
                    errors.append(f"DUPLICATE_DERIVED_OUTPUT_ID:{key}")
                output_ids.add(key)
            role = output.get("role")
            if not _nonempty(role) or role not in DERIVED_ROLES:
                errors.append(f"{label}_ROLE_INVALID:{role!r}")
            else:
                role_counts[role] += 1
            _verify_file(package_root, output, label, errors, used_paths, verified)
    for role in sorted(DERIVED_ROLES):
        if role_counts[role] == 0:
            errors.append(f"MISSING_DERIVED_OUTPUT_ROLE:{role}")
        elif role_counts[role] > 1:
            errors.append(f"DUPLICATE_DERIVED_OUTPUT_ROLE:{role}")

    errors = sorted(set(errors))
    valid = not errors
    binding: dict[str, Any] | None = None
    binding_sha: str | None = None
    if valid:
        binding = _sorted_binding(manifest)
        binding_sha = sha256_bytes(canonical_json_bytes(binding))

    return {
        "contract": CONTRACT,
        "studyStage": "SYNTHETIC_SOFTWARE_CONTRACT_ONLY",
        "contractValid": valid,
        "errors": errors,
        "verifiedFileCount": len(verified),
        "verifiedFiles": sorted(verified, key=lambda item: item["path"]),
        "packageBinding": binding,
        "packageBindingSha256": binding_sha,
        "realCalibrationAuthorized": False,
        "realHoldoutCaptureAuthorized": False,
        **AUTHORIZATION_BOUNDARY,
    }


def _write(root: Path, rel: str, data: bytes) -> dict[str, str]:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"path": rel, "sha256": sha256_bytes(data)}


def build_synthetic_fixture(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    hardware = _write(root, "hardware/configuration.json", b'{"synthetic":true,"configuration":"cfg-v1"}\n')
    topology = _write(root, "hardware/topology.txt", b"synthetic six-string reference topology\n")
    fixture = _write(root, "fixture/calibration-fixture.txt", b"synthetic fixture only\n")
    code = _write(root, "decoder/decoder.py", b"# synthetic decoder identity fixture\n")
    config = _write(root, "decoder/config.json", b'{"synthetic":true,"thresholds":"fixture-only"}\n')
    raw_pitch = _write(root, "raw/pitch.bin", b"synthetic physical pitch-state bytes\x00\x01")
    raw_birth = _write(root, "raw/birth.bin", b"synthetic event-birth bytes\x02\x03")
    raw_sync = _write(root, "raw/sync.bin", b"synthetic clock-sync bytes\x04\x05")
    raw_health = _write(root, "raw/health.bin", b"synthetic sensor-health bytes\x06")
    outputs = {
        role: _write(root, f"derived/{role}.json", canonical_json_bytes({"synthetic": True, "role": role}))
        for role in sorted(DERIVED_ROLES)
    }
    return {
        "contract": CONTRACT,
        "calibrationId": "synthetic-calibration-v1",
        "usedHoldoutData": False,
        "usedModelOutputs": False,
        "derivedFromEvaluatedAudio": False,
        "maxAbsoluteOnsetErrorSeconds": 0.025,
        "hardwareConfiguration": {
            "configurationId": "synthetic-hardware-config-v1",
            "firmwareVersion": "synthetic-fw-v1",
            **hardware,
        },
        "instrumentSetupSha256": sha256_bytes(b"synthetic-instrument-setup-v1"),
        "hardwareIdentities": [
            {"componentId": "logger", "immutableIdentity": "synthetic-logger-001", "role": "reference_logger"},
            {"componentId": "interface", "immutableIdentity": "synthetic-interface-001", "role": "audio_interface"},
        ],
        "wiringTopology": {"topologyId": "synthetic-topology-v1", **topology},
        "calibrationFixture": {"fixtureId": "synthetic-fixture-v1", **fixture},
        "decoder": {
            "decoderId": "synthetic-decoder-v1",
            "softwareVersion": "1.0.0-synthetic",
            "code": code,
            "configuration": config,
        },
        "rawSources": [
            {"sourceId": "pitch", "roles": ["physical_pitch_state"], "nonHoldout": True, "usedModelOutputs": False, "derivedFromEvaluatedAudio": False, **raw_pitch},
            {"sourceId": "birth", "roles": ["event_birth"], "nonHoldout": True, "usedModelOutputs": False, "derivedFromEvaluatedAudio": False, **raw_birth},
            {"sourceId": "sync", "roles": ["clock_sync"], "nonHoldout": True, "usedModelOutputs": False, "derivedFromEvaluatedAudio": False, **raw_sync},
            {"sourceId": "health", "roles": ["sensor_health"], "nonHoldout": True, "usedModelOutputs": False, "derivedFromEvaluatedAudio": False, **raw_health},
        ],
        "derivedOutputs": [
            {"outputId": f"synthetic-{role}", "role": role, **outputs[role]}
            for role in sorted(DERIVED_ROLES)
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest")
    parser.add_argument("--package-root", required=True)
    parser.add_argument("--generate-synthetic-fixture", action="store_true")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.package_root)
    if args.generate_synthetic_fixture:
        manifest = build_synthetic_fixture(root)
        (root / "manifest.json").write_bytes(canonical_json_bytes(manifest))
    else:
        if not args.manifest:
            parser.error("--manifest is required unless --generate-synthetic-fixture is used")
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    result = validate_package(manifest, root)
    rendered = canonical_json_bytes(result)
    Path(args.output).write_bytes(rendered)
    print(rendered.decode("utf-8"))
    return 0 if result["contractValid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
