#!/usr/bin/env python3
"""Independent reference-blind structural QC for the single V162 candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from event_logic_v162 import build_subdivision_lattice, select_event_step

QC_SCHEMA = "dadrock.tabs.v162.reference-blind-structural-qc.v1"
CANDIDATE_SCHEMA = "dadrock.tabs.v162.cpu-state-segmented-generated.v1"
GENERATION_SCHEMA = "dadrock.tabs.v162.cpu-generation-receipt.v1"
TIMEBASE_SCHEMA = "dadrock.tabs.v162.reference-blind-subdivision-timebase.v1"
TIMEBASE_QC_SCHEMA = "dadrock.tabs.v162.reference-blind-subdivision-timebase-qc.v1"
PRE_RUN_SCHEMA = "dadrock.tabs.v162.pre-run-identity-receipt.v1"
ENV_SCHEMA = "dadrock.tabs.v162.cpu-environment-receipt.v1"
SR = 22050
HOP = 256
EPS = 1e-12
RANGES = {"combinedGuitar": (40, 88), "bass": (28, 67)}
GUITAR_SOURCES = {"basic_pitch_segmented", "basic_pitch_active_state_reattack"}
BASS_SOURCES = {"bass_detected_onset_state", "bass_same_pitch_reattack_state", "bass_state_change"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def json_native(value: Any) -> Any:
    if value is None:
        return None
    if type(value) in (str, bool, int):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise RuntimeError("nonfinite native float is not permitted in V162 QC receipt")
        return value
    if isinstance(value, np.generic):
        return json_native(value.item())
    if isinstance(value, np.ndarray):
        return json_native(value.tolist())
    if isinstance(value, (list, tuple)):
        return [json_native(item) for item in value]
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise RuntimeError("V162 QC receipt dictionary keys must be native strings")
            normalized[key] = json_native(item)
        return normalized
    raise RuntimeError(f"unsupported V162 QC receipt type: {type(value).__name__}")


def load_mono(path: Path) -> np.ndarray:
    import librosa
    y, sr = librosa.load(str(path), sr=SR, mono=True)
    y = np.asarray(y, dtype=np.float32)
    if sr != SR or y.size == 0 or not np.all(np.isfinite(y)):
        raise RuntimeError(f"invalid V162 structural-QC audio load: {path}")
    return y


def onset_env(y: np.ndarray) -> np.ndarray:
    import librosa
    x = np.asarray(librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP), dtype=float)
    if x.size == 0 or not np.all(np.isfinite(x)):
        raise RuntimeError("invalid V162 structural-QC onset envelope")
    return x


def positive_unit_scale(x: np.ndarray) -> np.ndarray:
    x = np.maximum(np.asarray(x, dtype=float), 0.0)
    peak = float(np.max(x)) if x.size else 0.0
    if not math.isfinite(peak) or peak <= EPS:
        raise RuntimeError("V162 structural-QC unit-scale input lacks positive evidence")
    return x / peak


def shared_env(mix: np.ndarray, drums: np.ndarray) -> np.ndarray:
    a = onset_env(mix)
    b = onset_env(drums)
    n = min(len(a), len(b))
    return 0.65 * positive_unit_scale(b[:n]) + 0.35 * positive_unit_scale(a[:n])


def safety_pass(safety: Any) -> bool:
    if not isinstance(safety, dict):
        return False
    return (
        safety.get("referenceRead") is False
        and safety.get("professionalReferencePathsOpened") == 0
        and safety.get("referenceFacingScoreCalls") == 0
        and safety.get("priorGeneratedCandidateRead") is False
        and safety.get("priorScoreRead") is False
        and safety.get("V161CandidateRead") is False
        and safety.get("referenceGuidedFiltering") is False
        and safety.get("thresholdSweep") is False
        and safety.get("variantSelection") is False
        and safety.get("humanCorrection") is False
        and safety.get("cudaGpuUsed") is False
        and safety.get("modalUsed") is False
        and safety.get("mainOrProductionModified") is False
    )


def stream_check(
    name: str,
    rows: Any,
    lattice: list[float],
    instrument_env: np.ndarray,
    shared: np.ndarray,
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not isinstance(rows, list) or not rows:
        return False, [f"{name}: stream empty/not-list"]
    lo_midi, hi_midi = RANGES[name]
    prior_sort: tuple[int, int, str] | None = None
    dedupe: set[tuple[int, int]] = set()
    per_step: dict[int, int] = {}
    for index, row in enumerate(rows):
        prefix = f"{name}[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix}: event not object")
            continue
        required = {"measure", "step", "midi", "startSeconds", "absoluteGridStep", "source", "nearestLatticeStep", "selectedLatticeTimeSeconds", "gridCorrectionSteps", "stepSelection"}
        missing = required - set(row)
        if missing:
            errors.append(f"{prefix}: missing {sorted(missing)}")
            continue
        for key in ("measure", "step", "midi", "startSeconds", "absoluteGridStep", "nearestLatticeStep", "selectedLatticeTimeSeconds", "gridCorrectionSteps"):
            if not finite(row.get(key)):
                errors.append(f"{prefix}: nonfinite {key}")
        if any(message.startswith(prefix + ": nonfinite") for message in errors):
            continue
        midi = int(row["midi"])
        absolute = int(row["absoluteGridStep"])
        source = str(row["source"])
        if not lo_midi <= midi <= hi_midi:
            errors.append(f"{prefix}: MIDI outside range")
        if float(row["startSeconds"]) < 0.0:
            errors.append(f"{prefix}: negative start")
        if row.get("stream") != name:
            errors.append(f"{prefix}: stream label mismatch")
        if int(row["measure"]) != absolute // 16 + 1 or int(row["step"]) != absolute % 16:
            errors.append(f"{prefix}: measure/step mapping inconsistent")
        if not 0 <= absolute < len(lattice):
            errors.append(f"{prefix}: absolute step outside lattice")
            continue
        if abs(float(row["selectedLatticeTimeSeconds"]) - float(lattice[absolute])) > 1e-12:
            errors.append(f"{prefix}: selected lattice time mismatch")
        recomputed, selection = select_event_step(float(row["startSeconds"]), lattice, instrument_env, shared)
        if recomputed != absolute:
            errors.append(f"{prefix}: evidence step selection does not recompute")
        if int(row["nearestLatticeStep"]) != int(selection["nearestStep"]):
            errors.append(f"{prefix}: nearest lattice step mismatch")
        if int(row["gridCorrectionSteps"]) != absolute - int(selection["nearestStep"]):
            errors.append(f"{prefix}: grid correction mismatch")
        if abs(int(row["gridCorrectionSteps"])) > 1:
            errors.append(f"{prefix}: correction exceeds one step")
        stored_selection = row.get("stepSelection")
        if not isinstance(stored_selection, dict) or int((stored_selection.get("winner") or {}).get("step", -999)) != absolute:
            errors.append(f"{prefix}: stored winner metadata mismatch")

        score_value = row.get("admissionScore", row.get("recoveryScore"))
        if not finite(score_value) or not 0.0 <= float(score_value) <= 1.0:
            errors.append(f"{prefix}: invalid admission/recovery score")

        if name == "combinedGuitar":
            if source not in GUITAR_SOURCES:
                errors.append(f"{prefix}: forbidden Guitar source {source}")
            if "harmonic" in source:
                errors.append(f"{prefix}: standalone harmonic Guitar source forbidden")
            context = row.get("registerContext")
            if not isinstance(context, dict):
                errors.append(f"{prefix}: missing registerContext")
            elif row.get("registerRepaired") is True:
                if context.get("contextCenter") is None or context.get("reason") != "SEQUENCE_ELIGIBLE":
                    errors.append(f"{prefix}: repaired register lacks sequence context proof")
            if source == "basic_pitch_active_state_reattack":
                if not finite(row.get("recoveryScore")) or row.get("fundamentalPresent") is not True:
                    errors.append(f"{prefix}: recovery lacks score/fundamental proof")
                if float(row.get("parentConfidence", 0.0)) + EPS < 0.35 or float(row.get("templateRank", 0.0)) + EPS < 0.80:
                    errors.append(f"{prefix}: recovery violates parent/rank gate")
        else:
            if source not in BASS_SOURCES:
                errors.append(f"{prefix}: forbidden Bass source {source}")
            if not isinstance(row.get("proposalKind"), str) or not isinstance(row.get("stateMidi"), int) or not finite(row.get("stateVoicedProbability")):
                errors.append(f"{prefix}: missing Bass stable-state metadata")
            if not 0.0 <= float(row.get("stateVoicedProbability", -1.0)) <= 1.0:
                errors.append(f"{prefix}: invalid Bass state voiced probability")

        key = (absolute, midi)
        if key in dedupe:
            errors.append(f"{prefix}: duplicate absoluteStep/MIDI")
        dedupe.add(key)
        per_step[absolute] = per_step.get(absolute, 0) + 1
        sort_key = (absolute, midi, source)
        if prior_sort is not None and sort_key < prior_sort:
            errors.append(f"{prefix}: deterministic sort order violated")
        prior_sort = sort_key

    cap = 6 if name == "combinedGuitar" else 1
    if any(count > cap for count in per_step.values()):
        errors.append(f"{name}: per-step cap {cap} violated")
    return not errors, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--generation-receipt", type=Path, required=True)
    parser.add_argument("--timebase", type=Path, required=True)
    parser.add_argument("--timebase-qc", type=Path, required=True)
    parser.add_argument("--mix", type=Path, required=True)
    parser.add_argument("--drums", type=Path, required=True)
    parser.add_argument("--guitar", type=Path, required=True)
    parser.add_argument("--bass", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--implementation-contract", type=Path, required=True)
    parser.add_argument("--pre-run-receipt", type=Path, required=True)
    parser.add_argument("--environment-receipt", type=Path, required=True)
    parser.add_argument("--event-logic", type=Path, required=True)
    parser.add_argument("--transcriber", type=Path, required=True)
    parser.add_argument("--timebase-builder", type=Path, required=True)
    parser.add_argument("--timebase-qc-code", type=Path, required=True)
    parser.add_argument("--negative-runtime-guard", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    if args.receipt.exists():
        raise RuntimeError("V162 structural-QC receipt is write-once")
    for path in (args.candidate, args.generation_receipt, args.timebase, args.timebase_qc, args.mix, args.drums, args.guitar, args.bass, args.preregistration, args.implementation_contract, args.pre_run_receipt, args.environment_receipt, args.event_logic, args.transcriber, args.timebase_builder, args.timebase_qc_code, args.negative_runtime_guard):
        if not path.is_file():
            raise RuntimeError(f"missing V162 structural-QC input: {path}")

    candidate = load_json(args.candidate)
    generation = load_json(args.generation_receipt)
    timebase = load_json(args.timebase)
    timebase_qc = load_json(args.timebase_qc)
    contract = load_json(args.implementation_contract)
    prereg = load_json(args.preregistration)
    pre_run = load_json(args.pre_run_receipt)
    environment = load_json(args.environment_receipt)
    schemas = contract.get("canonicalSchemas") or {}

    checks: dict[str, bool] = {}
    errors: list[str] = []
    checks["candidateSchema"] = candidate.get("schema") == CANDIDATE_SCHEMA == schemas.get("candidate")
    checks["generationSchema"] = generation.get("schema") == GENERATION_SCHEMA == schemas.get("generationReceipt")
    checks["structuralQcSchemaContract"] = schemas.get("structuralQc") == QC_SCHEMA
    checks["timebaseSchema"] = timebase.get("schema") == TIMEBASE_SCHEMA == schemas.get("timebase")
    checks["timebaseQcPass"] = timebase_qc.get("schema") == TIMEBASE_QC_SCHEMA and timebase_qc.get("validation") == "PASS"
    checks["preRunReceipt"] = pre_run.get("schema") == PRE_RUN_SCHEMA and pre_run.get("validation") == "PASS"
    checks["environmentReceipt"] = environment.get("schema") == ENV_SCHEMA and environment.get("validation") == "PASS" and environment.get("device") == "cpu" and environment.get("cudaAvailable") is False and environment.get("torchCudaVersion") is None
    checks["preregistrationState"] = prereg.get("version") == "V162" and prereg.get("status") == "PREREGISTERED_BEFORE_IMPLEMENTATION_CODE"

    checks["candidateHash"] = generation.get("candidateSha256") == sha256_file(args.candidate)
    checks["timebaseHashChain"] = timebase_qc.get("timebaseSha256") == sha256_file(args.timebase) and generation.get("timebaseSha256") == sha256_file(args.timebase) and candidate.get("timebaseIdentity", {}).get("sha256") == sha256_file(args.timebase)
    checks["timebaseQcHashChain"] = generation.get("timebaseQcSha256") == sha256_file(args.timebase_qc) and candidate.get("timebaseIdentity", {}).get("timebaseQcSha256") == sha256_file(args.timebase_qc)
    checks["sealedJsonHashChain"] = generation.get("preregistrationSha256") == sha256_file(args.preregistration) and generation.get("implementationContractSha256") == sha256_file(args.implementation_contract) and generation.get("preRunReceiptSha256") == sha256_file(args.pre_run_receipt) and generation.get("environmentReceiptSha256") == sha256_file(args.environment_receipt)

    pins = pre_run.get("pinnedGitBlobs") or {}
    checks["codePins"] = (
        pins.get("preregistration") == git_blob_sha(args.preregistration)
        and pins.get("implementationContract") == git_blob_sha(args.implementation_contract)
        and pins.get("eventLogic") == git_blob_sha(args.event_logic)
        and pins.get("timebaseBuilder") == git_blob_sha(args.timebase_builder)
        and pins.get("timebaseQc") == git_blob_sha(args.timebase_qc_code)
        and pins.get("transcriber") == git_blob_sha(args.transcriber)
        and pins.get("structuralQc") == git_blob_sha(Path(__file__))
        and pins.get("negativeRuntimeGuard") == git_blob_sha(args.negative_runtime_guard)
    )
    checks["generationCodePins"] = generation.get("implementation", {}).get("canonicalEntryPointGitBlob") == git_blob_sha(args.transcriber) and generation.get("implementation", {}).get("eventLogicGitBlob") == git_blob_sha(args.event_logic)
    checks["writeOnceBoundary"] = pre_run.get("timebaseMustNotExistAtSeal") is True and pre_run.get("timebaseQcReceiptMustNotExistAtSeal") is True and pre_run.get("candidateMustNotExistAtSeal") is True and pre_run.get("generationReceiptMustNotExistAtSeal") is True
    generation_environment = generation.get("environment") or {}
    checks["environmentReceiptEmbeddedExactly"] = generation_environment == environment
    checks["singleGenerationWorkflowRun"] = environment.get("workflowRunNumber") == 1 and environment.get("workflowRunAttempt") == 1 and generation_environment.get("workflowRunNumber") == 1 and generation_environment.get("workflowRunAttempt") == 1 and generation_environment.get("workflowRunId") == environment.get("workflowRunId") and isinstance(environment.get("workflowRunId"), int) and environment.get("workflowRunId") > 0

    grid_times = np.asarray(timebase.get("gridBeatTimesSeconds", []), dtype=float)
    lattice = [float(x) for x in timebase.get("subdivisionTimesSeconds", [])]
    checks["frozenBeatGrid"] = bool(len(grid_times) >= 2 and np.all(np.isfinite(grid_times)) and np.all(np.diff(grid_times) > 0.0))
    checks["frozenSubdivisionGrid"] = bool(len(lattice) == 4 * len(grid_times) + 1 and len(lattice) >= 2 and np.all(np.isfinite(lattice)) and np.all(np.diff(np.asarray(lattice)) > 0.0))

    mix_y = load_mono(args.mix)
    drums_y = load_mono(args.drums)
    guitar_y = load_mono(args.guitar)
    bass_y = load_mono(args.bass)
    shared = shared_env(mix_y, drums_y)
    recomputed_lattice = build_subdivision_lattice(grid_times.tolist(), shared) if checks["frozenBeatGrid"] else []
    checks["subdivisionLatticeRecomputed"] = len(recomputed_lattice) == len(lattice) and all(abs(a - b) <= 1e-12 for a, b in zip(recomputed_lattice, lattice))
    guitar_env = onset_env(guitar_y)
    bass_env = onset_env(bass_y)

    streams = candidate.get("streams") or {}
    if checks["frozenSubdivisionGrid"] and checks["subdivisionLatticeRecomputed"]:
        guitar_ok, guitar_errors = stream_check("combinedGuitar", streams.get("combinedGuitar"), lattice, guitar_env, shared)
        bass_ok, bass_errors = stream_check("bass", streams.get("bass"), lattice, bass_env, shared)
        checks["combinedGuitarStructure"] = guitar_ok
        checks["bassStructure"] = bass_ok
        errors.extend(guitar_errors)
        errors.extend(bass_errors)
    else:
        checks["combinedGuitarStructure"] = False
        checks["bassStructure"] = False
        errors.append("subdivision lattice invalid; event selection cannot be recomputed")

    counts = generation.get("counts") or {}
    checks["streamCounts"] = isinstance(streams.get("combinedGuitar"), list) and isinstance(streams.get("bass"), list) and counts.get("combinedGuitar") == len(streams.get("combinedGuitar", [])) and counts.get("bass") == len(streams.get("bass", [])) and counts.get("combinedGuitar", 0) > 0 and counts.get("bass", 0) > 0
    checks["guitarNoStandaloneHarmonicRecovery"] = all(str(row.get("source")) in GUITAR_SOURCES and "harmonic" not in str(row.get("source")) for row in streams.get("combinedGuitar", [])) if isinstance(streams.get("combinedGuitar"), list) else False
    checks["guitarPolyphonyCapSix"] = all(sum(1 for row in streams.get("combinedGuitar", []) if int(row.get("absoluteGridStep", -1)) == step) <= 6 for step in {int(row.get("absoluteGridStep", -1)) for row in streams.get("combinedGuitar", [])}) if isinstance(streams.get("combinedGuitar"), list) else False
    checks["bassGridMonophonyCapOne"] = len({int(row.get("absoluteGridStep", -1)) for row in streams.get("bass", [])}) == len(streams.get("bass", [])) if isinstance(streams.get("bass"), list) else False
    checks["candidateSafety"] = safety_pass(candidate.get("safety"))
    checks["generationSafety"] = safety_pass(generation.get("safety"))
    checks["preRunReferenceBlind"] = pre_run.get("referenceReadAtSeal") is False and pre_run.get("professionalReferencePathsOpenedAtSeal") == 0 and pre_run.get("V161CandidateReadAtSeal") is False
    checks["timebaseReferenceBlind"] = (timebase.get("safety") or {}).get("referenceRead") is False and (timebase.get("safety") or {}).get("professionalReferencePathsOpened") == 0 and (timebase.get("safety") or {}).get("V161CandidateRead") is False

    passed = all(bool(value) for value in checks.values()) and not errors
    native_checks = {key: bool(value) for key, value in checks.items()}
    receipt = {
        "schema": QC_SCHEMA,
        "version": "V162",
        "validation": "PASS" if passed else "FAIL",
        "terminalForV162OnFailure": True,
        "candidatePath": str(args.candidate),
        "candidateSha256": sha256_file(args.candidate),
        "generationReceiptPath": str(args.generation_receipt),
        "generationReceiptSha256": sha256_file(args.generation_receipt),
        "timebaseSha256": sha256_file(args.timebase),
        "timebaseQcSha256": sha256_file(args.timebase_qc),
        "checks": native_checks,
        "errors": errors,
        "safety": {
            "referenceRead": False,
            "professionalReferencePathsOpened": 0,
            "referenceFacingScoreCalls": 0,
            "priorGeneratedCandidateRead": False,
            "priorScoreRead": False,
            "V161CandidateRead": False,
            "gpuUsed": False,
        },
    }
    normalized = json_native(receipt)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(normalized, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"validation": normalized["validation"], "failedChecks": [k for k, ok in native_checks.items() if not ok], "errorCount": len(errors)}, sort_keys=True))
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
