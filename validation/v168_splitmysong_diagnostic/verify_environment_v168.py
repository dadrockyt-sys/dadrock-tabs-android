#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as md
import json
import platform
from pathlib import Path

EXPECTED_PYTHON = "3.10.21"
EXPECTED_PACKAGES = {
    "basic-pitch": "0.4.0",
    "demucs": "4.1.0",
    "imageio-ffmpeg": "0.6.0",
    "librosa": "0.11.0",
    "numpy": "1.26.4",
    "scipy": "1.13.1",
    "soundfile": "0.12.1",
    "tflite-runtime": "2.14.0",
    "torch": "2.8.0+cpu",
}
EXPECTED_MODEL_SHA256 = "3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676"
EXPECTED_GIT_BLOBS = {
    "debug/v165-cpu-autonomous/environment-receipt.json": "84160ae885316450ad59c3dca5bbb9692e4dfdc9",
    "validation/v165_cpu_autonomous/transcribe_v165.py": "45d595853302b077fbf4f3094e9a4922fba02435",
    "validation/v164_cpu_autonomous/transcribe_v164.py": "df1302216df404bc3368ff820f005d6b63ae100d",
    "validation/v162_cpu_autonomous/transcribe_v162.py": "fa163cafe2131aa73cdbb50df10d4e4912cff53b",
    "validation/v167_single_song_calibration/build_upstream_recovery_variants_v167.py": "24413d321f64bbfcce48812ceb85b4593dcfa80c",
    "validation/v167_single_song_calibration/build_state_split_guitar_variants_v167.py": "6b480d43744a5c67c02510d55162581d896afee4",
    "validation/v167_single_song_calibration/promote_state_split_guitar_winner_v167.py": "a912018b58f9bd7243229fcba3d8895e33300c44",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    if platform.python_version() != EXPECTED_PYTHON:
        raise RuntimeError(f"Python mismatch: {platform.python_version()} != {EXPECTED_PYTHON}")

    packages = {}
    for name, expected in EXPECTED_PACKAGES.items():
        observed = md.version(name)
        if observed != expected:
            raise RuntimeError(f"{name} mismatch: {observed} != {expected}")
        packages[name] = observed

    import torch
    if torch.__version__ != "2.8.0+cpu":
        raise RuntimeError(f"Torch mismatch: {torch.__version__}")
    if torch.version.cuda is not None or torch.cuda.is_available():
        raise RuntimeError("CUDA-capable Torch/runtime detected")

    from basic_pitch import ICASSP_2022_MODEL_PATH
    model_path = Path(ICASSP_2022_MODEL_PATH)
    if not model_path.is_file():
        raise RuntimeError(f"Basic Pitch model missing: {model_path}")
    model_sha = sha256_file(model_path)
    if model_sha != EXPECTED_MODEL_SHA256:
        raise RuntimeError(f"Basic Pitch model hash mismatch: {model_sha}")

    blobs = {}
    for rel, expected in EXPECTED_GIT_BLOBS.items():
        path = args.repo_root / rel
        if not path.is_file():
            raise RuntimeError(f"Frozen repo dependency missing: {rel}")
        observed = git_blob_sha(path)
        if observed != expected:
            raise RuntimeError(f"Frozen repo dependency drift: {rel}: {observed} != {expected}")
        blobs[rel] = observed

    payload = {
        "schema": "dadrock.tabs.v168.splitmysong-diagnostic-environment-smoke.v1",
        "status": "CPU_ENVIRONMENT_READY",
        "validation": "PASS",
        "pythonVersion": platform.python_version(),
        "packages": packages,
        "torchCudaVersion": None,
        "cudaAvailable": False,
        "basicPitchModelPathName": model_path.name,
        "basicPitchModelSha256": model_sha,
        "frozenRepositoryPins": blobs,
        "safety": {
            "audioRead": False,
            "audioCommitted": False,
            "candidateGenerated": False,
            "pitchInferenceInvoked": False,
            "referenceRead": False,
            "scorerRead": False,
            "referenceFacingScoreCalls": 0,
            "gpuCudaUsed": False,
        },
    }
    text = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
