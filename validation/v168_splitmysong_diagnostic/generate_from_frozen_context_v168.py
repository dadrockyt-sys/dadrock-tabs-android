#!/usr/bin/env python3
"""Final one-shot reference-blind SplitMySong generator from frozen context.

This wrapper consumes a separately PASSed historical-context preflight so Demucs
is not rerun during the sole Basic Pitch attempt. It accepts no scorer/reference
argument. The first persistent one-shot marker is created only after every private
input, context artifact, receipt, runtime, repository blob, and core-generator
identity has passed its frozen guard.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

CORE_BLOB = "95972fb9b1f9c1bf4872e2c945025b4aa69a312c"
CORE_PATH = "validation/v168_splitmysong_diagnostic/generate_splitmysong_candidate_v168.py"
CONTEXT_SCHEMA = "dadrock.tabs.v168.splitmysong-historical-context-preflight.v1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def load_core(repo: Path):
    path = repo / CORE_PATH
    if not path.is_file() or git_blob_sha(path) != CORE_BLOB:
        raise RuntimeError("frozen SplitMySong generator-core identity mismatch")
    spec = importlib.util.spec_from_file_location("v168_splitmysong_generator_core", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen generator core")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_context(core, context_dir: Path, receipt_path: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    if not context_dir.is_dir():
        raise RuntimeError(f"historical context directory missing: {context_dir}")
    if not receipt_path.is_file():
        raise RuntimeError(f"historical context receipt missing: {receipt_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("schema") != CONTEXT_SCHEMA:
        raise RuntimeError("unexpected historical context receipt schema")
    if receipt.get("status") != "HISTORICAL_CONTEXT_FROZEN" or receipt.get("validation") != "PASS":
        raise RuntimeError("historical context receipt is not PASS/frozen")
    safety = receipt.get("safety") or {}
    expected_false = (
        "basicPitchImported",
        "pitchInferenceInvoked",
        "candidateGenerated",
        "referenceRead",
        "scorerRead",
        "gpuCudaUsed",
        "modalUsed",
        "mainOrProductionModified",
    )
    for key in expected_false:
        if safety.get(key) is not False:
            raise RuntimeError(f"historical context safety flag is not false: {key}")
    if int(safety.get("referenceFacingScoreCalls", -1)) != 0:
        raise RuntimeError("historical context receipt has nonzero score calls")

    expected_receipt = {
        "mixSha256": core.HISTORICAL_MIX_SHA256,
        "guitarSha256": core.HISTORICAL_GUITAR_SHA256,
        "bassSha256": core.HISTORICAL_BASS_SHA256,
        "drumsSha256": core.HISTORICAL_DRUMS_SHA256,
    }
    if (receipt.get("normalization") or {}).get("mixSha256") != expected_receipt["mixSha256"]:
        raise RuntimeError("historical context receipt mix identity mismatch")
    demucs = receipt.get("demucs") or {}
    for key in ("guitarSha256", "bassSha256", "drumsSha256"):
        if demucs.get(key) != expected_receipt[key]:
            raise RuntimeError(f"historical context receipt {key} mismatch")
    if demucs.get("model") != "htdemucs_6s" or demucs.get("device") != "cpu":
        raise RuntimeError("historical context Demucs model/device mismatch")
    if int(demucs.get("shifts", -1)) != 1 or int(demucs.get("jobs", -1)) != 1:
        raise RuntimeError("historical context Demucs execution settings mismatch")

    files = {
        "mix": context_dir / "mix.wav",
        "guitar": context_dir / "guitar-original-demucs.wav",
        "bass": context_dir / "bass-original-demucs.wav",
        "drums": context_dir / "drums-original-demucs.wav",
    }
    core.require_file_sha(files["mix"], core.HISTORICAL_MIX_SHA256, "frozen historical mix")
    core.require_file_sha(files["guitar"], core.HISTORICAL_GUITAR_SHA256, "frozen historical Guitar stem")
    core.require_file_sha(files["bass"], core.HISTORICAL_BASS_SHA256, "frozen historical Bass stem")
    core.require_file_sha(files["drums"], core.HISTORICAL_DRUMS_SHA256, "frozen historical Drums stem")
    return receipt, files


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.chmod(path, 0o600)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--normalized-guitar", type=Path, required=True)
    ap.add_argument("--arm-receipt", type=Path, required=True)
    ap.add_argument("--environment-receipt", type=Path, required=True)
    ap.add_argument("--ffmpeg-receipt", type=Path, required=True)
    ap.add_argument("--historical-context-dir", type=Path, required=True)
    ap.add_argument("--historical-context-receipt", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()

    repo = args.repo_root.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    os.chmod(out, 0o700)

    candidate_path = out / "splitmysong-i005-candidate.json"
    receipt_path = out / "splitmysong-generation-receipt.json"
    freeze_path = out / "splitmysong-candidate-freeze.json"
    attempt_marker = out / "splitmysong-generation-attempt.marker"
    for path in (candidate_path, receipt_path, freeze_path, attempt_marker):
        if path.exists():
            raise RuntimeError(f"one-shot output/marker already exists; rerun forbidden: {path}")

    core = load_core(repo)
    core.require_file_sha(args.source, core.PRIVATE_SOURCE_SHA256, "private SplitMySong source")
    core.require_file_sha(args.normalized_guitar, core.NORMALIZED_GUITAR_SHA256, "normalized SplitMySong Guitar")
    core.require_file_sha(args.arm_receipt, core.ARM_RECEIPT_SHA256, "ARM preflight receipt")
    core.require_file_sha(args.environment_receipt, core.ENV_RECEIPT_SHA256, "CPU environment receipt")
    core.require_file_sha(args.ffmpeg_receipt, core.FFMPEG_RECEIPT_SHA256, "FFmpeg normalizer receipt")
    repo_blobs = core.verify_repo(repo)
    runtime = core.verify_runtime()
    context_receipt, context_files = load_context(
        core,
        args.historical_context_dir.resolve(),
        args.historical_context_receipt.resolve(),
    )
    context_receipt_sha = sha256_file(args.historical_context_receipt)

    attempt_marker.write_text("ONE_SHOT_PITCH_INFERENCE_ARMED_AND_STARTED\n", encoding="utf-8")
    os.chmod(attempt_marker, 0o600)

    candidate, details = core.build_candidate(
        repo,
        args.normalized_guitar.resolve(),
        context_files["mix"],
        context_files["drums"],
    )
    candidate["pipeline"]["historicalContextReceiptSha256"] = context_receipt_sha
    candidate["pipeline"]["historicalContextPreflightStatus"] = context_receipt["status"]
    write_json(candidate_path, candidate)
    candidate_sha = sha256_file(candidate_path)

    receipt = {
        "schema": "dadrock.tabs.v168.splitmysong-ayggmw-diagnostic-generation-receipt.v2",
        "status": "REFERENCE_BLIND_CANDIDATE_GENERATED_AND_HASH_FROZEN",
        "candidatePath": str(candidate_path),
        "candidateSha256": candidate_sha,
        "generatorCoreGitBlob": CORE_BLOB,
        "historicalContextReceiptSha256": context_receipt_sha,
        "inputIdentities": {
            "privateSplitMySongSourceSha256": core.PRIVATE_SOURCE_SHA256,
            "normalizedSplitMySongGuitarSha256": core.NORMALIZED_GUITAR_SHA256,
            "armReceiptSha256": core.ARM_RECEIPT_SHA256,
            "environmentReceiptSha256": core.ENV_RECEIPT_SHA256,
            "ffmpegReceiptSha256": core.FFMPEG_RECEIPT_SHA256,
            "historicalNormalizedMixSha256": core.HISTORICAL_MIX_SHA256,
            "historicalDemucsGuitarSha256": core.HISTORICAL_GUITAR_SHA256,
            "historicalDemucsBassSha256": core.HISTORICAL_BASS_SHA256,
            "historicalDemucsDrumsSha256": core.HISTORICAL_DRUMS_SHA256,
            "timebaseSha256": core.TIMEBASE_SHA256,
        },
        "repositoryGitBlobs": repo_blobs,
        "runtime": runtime,
        "generation": details,
        "safety": {
            "referenceRead": False,
            "scorerRead": False,
            "referenceFacingScoreCalls": 0,
            "professionalReferencePathsOpened": 0,
            "referenceGuidedFiltering": False,
            "thresholdTuningPerformed": False,
            "humanCorrection": False,
            "candidateGenerated": True,
            "pitchInferenceInvoked": True,
            "basicPitchActualInferenceCalls": int(details["basicPitchInference"]["actualInferenceCalls"]),
            "gpuCudaUsed": False,
            "modalUsed": False,
            "mainOrProductionModified": False,
        },
    }
    if receipt["safety"]["basicPitchActualInferenceCalls"] != 1:
        raise AssertionError("one-shot Basic Pitch inference count is not exactly 1")
    write_json(receipt_path, receipt)
    receipt_sha = sha256_file(receipt_path)

    freeze = {
        "schema": "dadrock.tabs.v168.splitmysong-ayggmw-diagnostic-candidate-freeze.v2",
        "status": "FROZEN_BEFORE_ANY_LEGACY_REFERENCE_OR_SCORER_ACCESS",
        "candidateSha256": candidate_sha,
        "generationReceiptSha256": receipt_sha,
        "historicalContextReceiptSha256": context_receipt_sha,
        "referenceRead": False,
        "scorerRead": False,
        "referenceFacingScoreCalls": 0,
    }
    write_json(freeze_path, freeze)
    freeze_sha = sha256_file(freeze_path)

    print(json.dumps({
        "status": freeze["status"],
        "candidateSha256": candidate_sha,
        "generationReceiptSha256": receipt_sha,
        "candidateFreezeSha256": freeze_sha,
        "historicalContextReceiptSha256": context_receipt_sha,
        "finalGuitarCount": len(candidate["streams"]["combinedGuitar"]),
        "i005Summary": candidate["pipeline"]["i005Summary"],
        "basicPitchActualInferenceCalls": details["basicPitchInference"]["actualInferenceCalls"],
        "referenceRead": False,
        "scorerRead": False,
        "referenceFacingScoreCalls": 0,
    }, indent=2, sort_keys=True))
    print("\nREFERENCE-BLIND CANDIDATE FROZEN")
    print("Do not run any scorer until these hashes are checkpointed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
