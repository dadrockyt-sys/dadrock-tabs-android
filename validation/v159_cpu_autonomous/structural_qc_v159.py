#!/usr/bin/env python3
"""Independent reference-blind structural QC for the single V159 candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

QC_SCHEMA = "dadrock.tabs.v159.reference-blind-structural-qc.v1"
CANDIDATE_SCHEMA = "dadrock.tabs.v159.cpu-timebase-first-generated.v1"
GENERATION_SCHEMA = "dadrock.tabs.v159.cpu-generation-receipt.v1"
TIMEBASE_SCHEMA = "dadrock.tabs.v159.reference-blind-timebase.v1"
TIMEBASE_QC_SCHEMA = "dadrock.tabs.v159.reference-blind-timebase-qc.v1"
PRE_RUN_SCHEMA = "dadrock.tabs.v159.pre-run-identity-receipt.v1"
ENV_SCHEMA = "dadrock.tabs.v159.cpu-environment-receipt.v1"
REQUIRED_EVENT_FIELDS = {
    "measure", "step", "midi", "startSeconds", "rawGridStep", "absoluteGridStep", "source"
}
RANGES = {"combinedGuitar": (40, 88), "bass": (28, 67)}
PRECEDENCE = {"basic_pitch": 0, "harmonic_track": 1, "onset_harmonic_pyin": 2}


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


def raw_step(seconds: float, times: np.ndarray, steps: np.ndarray) -> float:
    t = float(seconds)
    if t <= times[0]:
        period = float(times[1] - times[0])
        return float(steps[0] + 4.0 * (t - times[0]) / period)
    if t >= times[-1]:
        period = float(times[-1] - times[-2])
        return float(steps[-1] + 4.0 * (t - times[-1]) / period)
    hi = int(np.searchsorted(times, t, side="right"))
    lo = hi - 1
    dt = float(times[hi] - times[lo])
    return float(steps[lo] + ((t - float(times[lo])) / dt) * (steps[hi] - steps[lo]))


def safety_pass(safety: Any) -> bool:
    if not isinstance(safety, dict):
        return False
    return (
        safety.get("referenceRead") is False
        and safety.get("professionalReferencePathsOpened") == 0
        and safety.get("referenceFacingScoreCalls") == 0
        and safety.get("priorGeneratedCandidateRead") is False
        and safety.get("priorScoreRead") is False
        and safety.get("priorDiagnosticReadByRuntime") is False
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
    times: np.ndarray,
    steps: np.ndarray,
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not isinstance(rows, list) or not rows:
        return False, [f"{name}: stream empty/not-list"]
    midi_min, midi_max = RANGES[name]
    prior_sort_key: tuple[int, int, str] | None = None
    dedupe: set[tuple[int, int]] = set()
    for index, row in enumerate(rows):
        prefix = f"{name}[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix}: event not object")
            continue
        missing = REQUIRED_EVENT_FIELDS - set(row.keys())
        if missing:
            errors.append(f"{prefix}: missing {sorted(missing)}")
            continue
        for key in ("midi", "startSeconds", "rawGridStep", "absoluteGridStep", "measure", "step"):
            if not finite(row.get(key)):
                errors.append(f"{prefix}: nonfinite {key}")
        if errors and errors[-1].startswith(prefix + ": nonfinite"):
            continue
        midi = int(row["midi"])
        start = float(row["startSeconds"])
        absolute = int(row["absoluteGridStep"])
        measure = int(row["measure"])
        step = int(row["step"])
        source = str(row["source"])
        if not midi_min <= midi <= midi_max:
            errors.append(f"{prefix}: MIDI outside {midi_min}..{midi_max}")
        if start < 0.0:
            errors.append(f"{prefix}: negative start")
        if "endSeconds" in row and (not finite(row["endSeconds"]) or float(row["endSeconds"]) < start):
            errors.append(f"{prefix}: invalid endSeconds")
        if "durationSeconds" in row and (not finite(row["durationSeconds"]) or float(row["durationSeconds"]) < 0.0):
            errors.append(f"{prefix}: invalid durationSeconds")
        expected_raw = raw_step(start, times, steps)
        if abs(float(row["rawGridStep"]) - expected_raw) > 1e-9:
            errors.append(f"{prefix}: rawGridStep disagrees with frozen timebase")
        expected_absolute = int(round(expected_raw))
        if absolute != expected_absolute:
            errors.append(f"{prefix}: absoluteGridStep disagrees with Python round(rawGridStep)")
        if measure != absolute // 16 + 1 or step != absolute % 16:
            errors.append(f"{prefix}: measure/step mapping inconsistent")
        if row.get("stream") != name:
            errors.append(f"{prefix}: stream label mismatch")
        if name == "bass":
            if "onsetProposalIndex" not in row or not isinstance(row.get("onsetProposalIndex"), int):
                errors.append(f"{prefix}: bass event missing onsetProposalIndex")
            if source != "onset_harmonic_pyin":
                errors.append(f"{prefix}: unexpected bass source {source}")
        else:
            if source in {"cqt", "cqt_only", "single_frame_cqt"}:
                errors.append(f"{prefix}: forbidden guitar source {source}")
            if source not in {"basic_pitch", "harmonic_track"}:
                errors.append(f"{prefix}: unexpected guitar source {source}")
        key = (absolute, midi)
        if key in dedupe:
            errors.append(f"{prefix}: duplicate same-stream absoluteGridStep/MIDI")
        dedupe.add(key)
        sort_key = (absolute, midi, source)
        if prior_sort_key is not None and sort_key < prior_sort_key:
            errors.append(f"{prefix}: deterministic sort order violated")
        prior_sort_key = sort_key
    return len(errors) == 0, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--generation-receipt", type=Path, required=True)
    parser.add_argument("--timebase", type=Path, required=True)
    parser.add_argument("--timebase-qc", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--implementation-contract", type=Path, required=True)
    parser.add_argument("--pre-run-receipt", type=Path, required=True)
    parser.add_argument("--environment-receipt", type=Path, required=True)
    parser.add_argument("--transcriber", type=Path, required=True)
    parser.add_argument("--timebase-builder", type=Path, required=True)
    parser.add_argument("--timebase-qc-code", type=Path, required=True)
    parser.add_argument("--negative-runtime-guard", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    if args.receipt.exists():
        raise RuntimeError("V159 structural-QC receipt is write-once")
    for path in (
        args.candidate, args.generation_receipt, args.timebase, args.timebase_qc,
        args.preregistration, args.implementation_contract, args.pre_run_receipt,
        args.environment_receipt, args.transcriber, args.timebase_builder,
        args.timebase_qc_code, args.negative_runtime_guard,
    ):
        if not path.is_file():
            raise RuntimeError(f"missing V159 structural-QC input: {path}")

    candidate = load_json(args.candidate)
    generation = load_json(args.generation_receipt)
    timebase = load_json(args.timebase)
    timebase_qc = load_json(args.timebase_qc)
    prereg = load_json(args.preregistration)
    contract = load_json(args.implementation_contract)
    pre_run = load_json(args.pre_run_receipt)
    environment = load_json(args.environment_receipt)

    checks: dict[str, bool] = {}
    errors: list[str] = []
    schemas = contract.get("canonicalSchemas", {})
    checks["candidateSchema"] = candidate.get("schema") == CANDIDATE_SCHEMA == schemas.get("candidate")
    checks["generationSchema"] = generation.get("schema") == GENERATION_SCHEMA == schemas.get("generationReceipt")
    checks["structuralQcSchemaContract"] = schemas.get("structuralQc") == QC_SCHEMA
    checks["timebaseSchema"] = timebase.get("schema") == TIMEBASE_SCHEMA == schemas.get("timebase")
    checks["timebaseQcPass"] = timebase_qc.get("schema") == TIMEBASE_QC_SCHEMA and timebase_qc.get("validation") == "PASS"
    checks["preRunReceipt"] = pre_run.get("schema") == PRE_RUN_SCHEMA and pre_run.get("validation") == "PASS"
    checks["environmentReceipt"] = environment.get("schema") == ENV_SCHEMA and environment.get("validation") == "PASS" and environment.get("device") == "cpu" and environment.get("cudaAvailable") is False and environment.get("torchCudaVersion") is None

    checks["candidateHash"] = generation.get("candidateSha256") == sha256_file(args.candidate)
    checks["timebaseHashChain"] = (
        timebase_qc.get("timebaseSha256") == sha256_file(args.timebase)
        and generation.get("timebaseSha256") == sha256_file(args.timebase)
        and candidate.get("timebaseIdentity", {}).get("sha256") == sha256_file(args.timebase)
    )
    checks["timebaseQcHashChain"] = (
        generation.get("timebaseQcSha256") == sha256_file(args.timebase_qc)
        and candidate.get("timebaseIdentity", {}).get("timebaseQcSha256") == sha256_file(args.timebase_qc)
    )
    checks["sealedJsonHashChain"] = (
        generation.get("preregistrationSha256") == sha256_file(args.preregistration)
        and generation.get("implementationContractSha256") == sha256_file(args.implementation_contract)
        and generation.get("preRunReceiptSha256") == sha256_file(args.pre_run_receipt)
        and generation.get("environmentReceiptSha256") == sha256_file(args.environment_receipt)
    )

    pins = pre_run.get("pinnedGitBlobs") or {}
    checks["codePins"] = (
        pins.get("preregistration") == git_blob_sha(args.preregistration)
        and pins.get("implementationContract") == git_blob_sha(args.implementation_contract)
        and pins.get("timebaseBuilder") == git_blob_sha(args.timebase_builder)
        and pins.get("timebaseQc") == git_blob_sha(args.timebase_qc_code)
        and pins.get("transcriber") == git_blob_sha(args.transcriber)
        and pins.get("structuralQc") == git_blob_sha(Path(__file__))
        and pins.get("negativeRuntimeGuard") == git_blob_sha(args.negative_runtime_guard)
    )
    checks["generationTranscriberPin"] = generation.get("implementation", {}).get("canonicalEntryPointGitBlob") == git_blob_sha(args.transcriber)
    checks["writeOnceBoundary"] = pre_run.get("timebaseMustNotExistAtSeal") is True and pre_run.get("candidateMustNotExistAtSeal") is True and pre_run.get("generationReceiptMustNotExistAtSeal") is True
    generation_environment = generation.get("environment") or {}
    checks["environmentReceiptEmbeddedExactly"] = generation_environment == environment
    checks["singleGenerationWorkflowRun"] = (
        environment.get("workflowRunNumber") == 1
        and environment.get("workflowRunAttempt") == 1
        and generation_environment.get("workflowRunNumber") == 1
        and generation_environment.get("workflowRunAttempt") == 1
        and generation_environment.get("workflowRunId") == environment.get("workflowRunId")
        and isinstance(environment.get("workflowRunId"), int)
        and environment.get("workflowRunId") > 0
    )

    times = np.asarray(timebase.get("gridBeatTimesSeconds", []), dtype=float)
    steps = np.asarray(timebase.get("gridBeatSteps", []), dtype=float)
    checks["frozenGrid"] = len(times) >= 2 and len(times) == len(steps) and np.all(np.isfinite(times)) and np.all(np.isfinite(steps)) and np.all(np.diff(times) > 0.0) and np.all(np.diff(steps) == 4.0)
    streams = candidate.get("streams") or {}
    if checks["frozenGrid"]:
        guitar_ok, guitar_errors = stream_check("combinedGuitar", streams.get("combinedGuitar"), times, steps)
        bass_ok, bass_errors = stream_check("bass", streams.get("bass"), times, steps)
        checks["combinedGuitarStructure"] = guitar_ok
        checks["bassStructure"] = bass_ok
        errors.extend(guitar_errors)
        errors.extend(bass_errors)
    else:
        checks["combinedGuitarStructure"] = False
        checks["bassStructure"] = False
        errors.append("frozen grid invalid; event mapping cannot be independently recomputed")

    counts = generation.get("counts") or {}
    checks["streamCounts"] = (
        isinstance(streams.get("combinedGuitar"), list)
        and isinstance(streams.get("bass"), list)
        and counts.get("combinedGuitar") == len(streams.get("combinedGuitar", []))
        and counts.get("bass") == len(streams.get("bass", []))
        and counts.get("combinedGuitar", 0) > 0
        and counts.get("bass", 0) > 0
    )
    checks["candidateSafety"] = safety_pass(candidate.get("safety"))
    checks["generationSafety"] = safety_pass(generation.get("safety"))
    checks["preRunReferenceBlind"] = pre_run.get("referenceReadAtSeal") is False and pre_run.get("professionalReferencePathsOpenedAtSeal") == 0
    checks["timebaseReferenceBlind"] = (timebase.get("safety") or {}).get("referenceRead") is False and (timebase.get("safety") or {}).get("professionalReferencePathsOpened") == 0

    passed = all(bool(value) for value in checks.values()) and not errors
    receipt = {
        "schema": QC_SCHEMA,
        "version": "V159",
        "validation": "PASS" if passed else "FAIL",
        "terminalForV159OnFailure": True,
        "candidatePath": str(args.candidate),
        "candidateSha256": sha256_file(args.candidate),
        "generationReceiptPath": str(args.generation_receipt),
        "generationReceiptSha256": sha256_file(args.generation_receipt),
        "timebaseSha256": sha256_file(args.timebase),
        "timebaseQcSha256": sha256_file(args.timebase_qc),
        "checks": checks,
        "errors": errors,
        "safety": {
            "referenceRead": False,
            "professionalReferencePathsOpened": 0,
            "referenceFacingScoreCalls": 0,
            "priorGeneratedCandidateRead": False,
            "priorScoreRead": False,
            "priorDiagnosticReadByRuntime": False,
        },
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "validation": receipt["validation"],
        "failedChecks": [name for name, ok in checks.items() if not ok],
        "errorCount": len(errors),
    }, sort_keys=True))
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
