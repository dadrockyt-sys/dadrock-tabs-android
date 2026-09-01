#!/usr/bin/env python3
"""Reference-blind preflight for the SplitMySong AYGGMW guitar diagnostic.

This module performs no pitch inference and has no scorer/reference inputs.
It has two explicit phases:

* ``input``: verify the private user-supplied audio and deterministic PCM
  normalization. This phase can run outside a repository checkout.
* ``arm``: additionally verify every frozen repository blob, the historical CPU
  package/runtime identity, and the Basic Pitch TFLite model hash. Passing this
  phase only proves that generation may be armed; it does not generate a
  candidate or read any professional/legacy reference.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as metadata
import json
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any

SCHEMA = "dadrock.tabs.v168.splitmysong-diagnostic-preflight.v1"
CONTRACT_SCHEMA = "dadrock.tabs.v168.splitmysong-diagnostic-contract.v1"
PREREG_SCHEMA = "dadrock.tabs.v168.splitmysong-diagnostic-preregistration.v1"

EXPECTED_SOURCE = {
    "sha256": "6601b8d01cbbbe6b6e70d9ec0ca3c15d17873c78e62ae4acdc258c96f168e3c9",
    "bytes": 3_610_958,
    "durationSeconds": 217.060136,
    "codecName": "aac",
    "sampleRate": 44_100,
    "channels": 2,
}
EXPECTED_NORMALIZED = {
    "sha256": "fdb0578d71f77c150e7fe66766a03953be55e7028fef4c24dc777416f2e7ff4f",
    "bytes": 9_572_600,
    "durationSeconds": 217.060136,
    "codecName": "pcm_s16le",
    "sampleRate": 22_050,
    "channels": 1,
}
DURATION_TOLERANCE_SECONDS = 0.005

NORMALIZATION_COMMAND = [
    "ffmpeg",
    "-hide_banner",
    "-loglevel",
    "error",
    "-y",
    "-i",
    "{source}",
    "-map",
    "0:a:0",
    "-vn",
    "-ar",
    "22050",
    "-ac",
    "1",
    "-c:a",
    "pcm_s16le",
    "{normalized}",
]

FROZEN_GIT_BLOBS = {
    "v165EnvironmentReceipt": {
        "path": "debug/v165-cpu-autonomous/environment-receipt.json",
        "blob": "84160ae885316450ad59c3dca5bbb9692e4dfdc9",
    },
    "v165Transcriber": {
        "path": "validation/v165_cpu_autonomous/transcribe_v165.py",
        "blob": "45d595853302b077fbf4f3094e9a4922fba02435",
    },
    "v164Transcriber": {
        "path": "validation/v164_cpu_autonomous/transcribe_v164.py",
        "blob": "df1302216df404bc3368ff820f005d6b63ae100d",
    },
    "v162Transcriber": {
        "path": "validation/v162_cpu_autonomous/transcribe_v162.py",
        "blob": "fa163cafe2131aa73cdbb50df10d4e4912cff53b",
    },
    "v167BaseBuilder": {
        "path": "validation/v167_single_song_calibration/build_upstream_recovery_variants_v167.py",
        "blob": "24413d321f64bbfcce48812ceb85b4593dcfa80c",
    },
    "v167StateSplitBuilder": {
        "path": "validation/v167_single_song_calibration/build_state_split_guitar_variants_v167.py",
        "blob": "6b480d43744a5c67c02510d55162581d896afee4",
    },
    "v167StateSplitPromotion": {
        "path": "validation/v167_single_song_calibration/promote_state_split_guitar_winner_v167.py",
        "blob": "a912018b58f9bd7243229fcba3d8895e33300c44",
    },
}

EXPECTED_RUNTIME = {
    "python": "3.10.21",
    "packages": {
        "basic-pitch": "0.4.0",
        "demucs": "4.1.0",
        "imageio-ffmpeg": "0.6.0",
        "librosa": "0.11.0",
        "numpy": "1.26.4",
        "scipy": "1.13.1",
        "soundfile": "0.12.1",
        "tflite-runtime": "2.14.0",
        "torch": "2.8.0+cpu",
    },
    "torchCudaVersion": None,
    "cudaAvailable": False,
    "basicPitchModelSha256": "3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676",
}

FROZEN_I005_POLICY = {
    "id": "gss-active-only",
    "templateRankMin": 0.975,
    "activitySupportMin": 0.05,
    "onsetSupportMin": 0.50,
    "requireBasicPitchActiveContext": True,
    "fundamentalPresentRequired": True,
    "candidateToMaxActiveTemplateScoreMin": 1.00,
    "harmonicOctaveIntervalsRejected": [12, 19, 24],
    "maxAddsPerSite": 1,
    "existingIteration003EventsPreferred": True,
    "stepMidiDedupe": True,
    "polyphonyCap": 6,
    "inactiveBranchEnabled": False,
    "globalPhaseCorrectionGridSteps": -12,
    "topOneOrdering": [
        "candidate_to_max_active_template_ratio_desc",
        "template_rank_desc",
        "template_score_desc",
        "onset_support_desc",
        "activity_support_desc",
        "midi_asc",
    ],
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def load_object(path: Path, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} must be a JSON object")
    return value


def ffprobe_audio(path: Path) -> dict[str, Any]:
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        raise RuntimeError("ffprobe not found")
    command = [
        ffprobe,
        "-v",
        "error",
        "-select_streams",
        "a:0",
        "-show_entries",
        "stream=codec_name,sample_rate,channels,duration",
        "-of",
        "json",
        str(path),
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    payload = json.loads(completed.stdout)
    streams = payload.get("streams") or []
    if len(streams) != 1:
        raise RuntimeError(f"expected exactly one selected audio stream in {path}")
    stream = streams[0]
    return {
        "codecName": str(stream["codec_name"]),
        "sampleRate": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
        "durationSeconds": float(stream["duration"]),
    }


def verify_audio(path: Path, expected: dict[str, Any], label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"{label} file missing: {path}")
    observed = {
        "name": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        **ffprobe_audio(path),
    }
    for key in ("bytes", "sha256", "codecName", "sampleRate", "channels"):
        if observed[key] != expected[key]:
            raise RuntimeError(
                f"{label} {key} mismatch: observed {observed[key]!r}, expected {expected[key]!r}"
            )
    if abs(observed["durationSeconds"] - float(expected["durationSeconds"])) > DURATION_TOLERANCE_SECONDS:
        raise RuntimeError(
            f"{label} duration mismatch: observed {observed['durationSeconds']}, "
            f"expected {expected['durationSeconds']} +/- {DURATION_TOLERANCE_SECONDS}"
        )
    return observed


def normalize(source: Path, normalized: Path) -> list[str]:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg not found")
    normalized.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg if token == "ffmpeg" else token.format(source=str(source), normalized=str(normalized))
        for token in NORMALIZATION_COMMAND
    ]
    subprocess.run(command, check=True)
    return command


def verify_contract(preregistration_path: Path, contract_path: Path) -> dict[str, Any]:
    prereg = load_object(preregistration_path, "preregistration")
    contract = load_object(contract_path, "implementation contract")
    if prereg.get("schema") != PREREG_SCHEMA or prereg.get("validation") != "PASS":
        raise RuntimeError("diagnostic preregistration is not frozen PASS")
    if contract.get("schema") != CONTRACT_SCHEMA or contract.get("validation") != "PASS":
        raise RuntimeError("diagnostic implementation contract is not frozen PASS")
    if prereg.get("sourceIdentity") != EXPECTED_SOURCE:
        raise RuntimeError("preregistration source identity drift")
    if prereg.get("normalizedIdentity") != EXPECTED_NORMALIZED:
        raise RuntimeError("preregistration normalized identity drift")
    if contract.get("runtime") != EXPECTED_RUNTIME:
        raise RuntimeError("implementation-contract runtime drift")
    if contract.get("frozenGitBlobs") != FROZEN_GIT_BLOBS:
        raise RuntimeError("implementation-contract repository pin drift")
    if contract.get("policy") != FROZEN_I005_POLICY:
        raise RuntimeError("implementation-contract I005 policy drift")
    return {
        "preregistration": {
            "name": preregistration_path.name,
            "sha256": sha256_file(preregistration_path),
            "gitBlob": git_blob_sha(preregistration_path),
        },
        "implementationContract": {
            "name": contract_path.name,
            "sha256": sha256_file(contract_path),
            "gitBlob": git_blob_sha(contract_path),
        },
    }


def verify_repo_pins(repo_root: Path) -> dict[str, Any]:
    observed: dict[str, Any] = {}
    for key, record in FROZEN_GIT_BLOBS.items():
        path = repo_root / str(record["path"])
        if not path.is_file():
            raise RuntimeError(f"frozen repository dependency missing: {path}")
        blob = git_blob_sha(path)
        if blob != record["blob"]:
            raise RuntimeError(
                f"frozen repository dependency drift for {key}: observed {blob}, expected {record['blob']}"
            )
        observed[key] = {"path": record["path"], "gitBlob": blob}
    return observed


def verify_runtime(model_path: Path) -> dict[str, Any]:
    if platform.python_version() != EXPECTED_RUNTIME["python"]:
        raise RuntimeError(
            f"Python version mismatch: observed {platform.python_version()}, expected {EXPECTED_RUNTIME['python']}"
        )
    packages: dict[str, str] = {}
    for package, expected in EXPECTED_RUNTIME["packages"].items():
        observed = metadata.version(package)
        if observed != expected:
            raise RuntimeError(
                f"package version mismatch for {package}: observed {observed}, expected {expected}"
            )
        packages[package] = observed

    import torch  # Imported only inside the strict arm gate.

    if torch.version.cuda is not None:
        raise RuntimeError(f"Torch CUDA build detected: {torch.version.cuda}")
    if bool(torch.cuda.is_available()):
        raise RuntimeError("CUDA is available; diagnostic arm is CPU-only")
    if not model_path.is_file():
        raise RuntimeError(f"Basic Pitch model missing: {model_path}")
    model_sha = sha256_file(model_path)
    if model_sha != EXPECTED_RUNTIME["basicPitchModelSha256"]:
        raise RuntimeError(
            f"Basic Pitch model SHA256 mismatch: observed {model_sha}, "
            f"expected {EXPECTED_RUNTIME['basicPitchModelSha256']}"
        )
    return {
        "pythonVersion": platform.python_version(),
        "packages": packages,
        "torchCudaVersion": None,
        "cudaAvailable": False,
        "basicPitchModelPathName": model_path.name,
        "basicPitchModelSha256": model_sha,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("input", "arm"), required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--normalized-output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path)
    parser.add_argument("--implementation-contract", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--model-path", type=Path)
    args = parser.parse_args()

    source = verify_audio(args.source, EXPECTED_SOURCE, "source")
    command = normalize(args.source, args.normalized_output)
    normalized = verify_audio(args.normalized_output, EXPECTED_NORMALIZED, "normalized audio")

    contract_identity = None
    repo_pins = None
    runtime = None
    if args.phase == "arm":
        missing = [
            name
            for name, value in (
                ("--preregistration", args.preregistration),
                ("--implementation-contract", args.implementation_contract),
                ("--repo-root", args.repo_root),
                ("--model-path", args.model_path),
            )
            if value is None
        ]
        if missing:
            raise RuntimeError(f"arm phase requires: {', '.join(missing)}")
        contract_identity = verify_contract(args.preregistration, args.implementation_contract)
        repo_pins = verify_repo_pins(args.repo_root)
        runtime = verify_runtime(args.model_path)

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "phase": args.phase,
        "status": "ARM_PREFLIGHT_PASS" if args.phase == "arm" else "INPUT_FROZEN",
        "validation": "PASS",
        "source": source,
        "normalization": {
            "commandTemplate": NORMALIZATION_COMMAND,
            "executedCommandRedacted": NORMALIZATION_COMMAND,
            "output": normalized,
            "byteDeterminismExpectedSha256": EXPECTED_NORMALIZED["sha256"],
        },
        "frozenPolicy": FROZEN_I005_POLICY,
        "frozenRuntimeTarget": EXPECTED_RUNTIME,
        "frozenRepositoryPins": FROZEN_GIT_BLOBS,
        "contractIdentity": contract_identity,
        "verifiedRepositoryPins": repo_pins,
        "verifiedRuntime": runtime,
        "safety": {
            "candidateGenerated": False,
            "pitchInferenceInvoked": False,
            "professionalReferenceRead": False,
            "legacyAyggmwReferenceRead": False,
            "scorerRead": False,
            "referenceFacingScoreCalls": 0,
            "thresholdSweep": False,
            "humanCorrection": False,
            "gpuCudaUsed": False,
            "modalUsed": False,
            "mainOrProductionModified": False,
            "audioCommittedToRepository": False,
        },
    }
    write_json(args.receipt, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
