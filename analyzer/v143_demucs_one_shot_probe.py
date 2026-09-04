from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import modal

from v143_ai_tab_gpu_worker import image as separator_gpu_image


app = modal.App("dadrock-v143-demucs-one-shot-probe")

probe_image = separator_gpu_image.add_local_python_source(
    "v143_production_separator",
    "v143_seeded_audio_separator_cli",
    "v143_seeded_separator",
    "v143_demucs_perf_probe_cli",
)


@contextmanager
def temporary_environment(updates: dict[str, str | None]) -> Iterator[None]:
    previous = {key: os.environ.get(key) for key in updates}
    try:
        for key, value in updates.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = str(value)
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@app.function(image=probe_image, gpu="L4", timeout=700, memory=8192)
def run_cpu_policy(
    audio_url: str,
    policy: str,
    clip_seconds: float = 6.0,
) -> dict:
    """Run exactly one ephemeral Demucs pass and return aggregate timing/hash only."""
    from v143_production_separator import separate_demucs_guitar
    from v143_seeded_separator import (
        CUBLAS_WORKSPACE_CONFIG,
        DEMUCS_SINGLE_THREAD_ENV,
        SEPARATOR_SEED,
        seeded_audio_separator_cli,
    )

    if not audio_url.startswith("https://raw.githubusercontent.com/"):
        raise ValueError("Diagnostic URL must be the authorized raw GitHub asset")
    if policy not in {"frozen-cpu1", "cpu4"}:
        raise ValueError("Unsupported diagnostic policy")
    if clip_seconds < 6.0 or clip_seconds > 10.0:
        raise ValueError("Diagnostic clip must be between 6 and 10 seconds")

    common_env = {
        "PYTHONHASHSEED": SEPARATOR_SEED,
        "V143_SEPARATOR_SEED": SEPARATOR_SEED,
        "CUBLAS_WORKSPACE_CONFIG": CUBLAS_WORKSPACE_CONFIG,
        "NVIDIA_TF32_OVERRIDE": "0",
    }
    policy_env = dict(DEMUCS_SINGLE_THREAD_ENV)
    cli = seeded_audio_separator_cli()

    if policy == "cpu4":
        policy_env.update(
            {
                "OMP_NUM_THREADS": "4",
                "MKL_NUM_THREADS": "4",
                "OPENBLAS_NUM_THREADS": "4",
                "VECLIB_MAXIMUM_THREADS": "4",
                "NUMEXPR_NUM_THREADS": "4",
                "TBB_NUM_THREADS": "4",
                "V143_DIAGNOSTIC_TORCH_THREADS": "4",
            }
        )
        cli = [sys.executable, "-m", "v143_demucs_perf_probe_cli"]

    with tempfile.TemporaryDirectory(prefix="v143-demucs-one-shot-") as temp_dir:
        root = Path(temp_dir)
        source = root / "source.m4a"
        clip = root / "clip.wav"
        output = root / "output"

        request = urllib.request.Request(
            audio_url,
            headers={"User-Agent": "DadRock-V143-Demucs-One-Shot/1.0"},
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            source.write_bytes(response.read())

        ffmpeg = subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(source), "-t", f"{clip_seconds:.3f}", "-vn",
                "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", str(clip),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if ffmpeg.returncode != 0 or not clip.exists() or clip.stat().st_size <= 0:
            raise RuntimeError("Diagnostic clip creation failed")

        started = time.monotonic()
        with temporary_environment(common_env):
            with temporary_environment(policy_env):
                separated = separate_demucs_guitar(cli, clip, output)
        wall = time.monotonic() - started
        stem = Path(separated["path"])
        aggregate = {
            "schemaVersion": 1,
            "gate": "v143-demucs-one-shot-policy-probe",
            "policy": policy,
            "clipSeconds": clip_seconds,
            "model": "htdemucs_6s.yaml",
            "singleStem": "Guitar",
            "demucsShifts": 1,
            "demucsOverlap": 0.10,
            "demucsSegmentSize": 6,
            "separatorSeed": 143,
            "device": "cpu",
            "elapsedSeconds": round(float(separated["elapsedSeconds"]), 3),
            "wallSeconds": round(wall, 3),
            "sha256": sha256_file(stem),
            "bytes": stem.stat().st_size,
            "referenceFree": True,
            "referenceFacingAccuracyScored": False,
            "referenceScoreCalls": 0,
            "rawAudioRetained": False,
            "stemBytesRetained": False,
        }

    return aggregate
