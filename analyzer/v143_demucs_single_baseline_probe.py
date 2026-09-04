from __future__ import annotations

import hashlib
import json
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


app = modal.App("dadrock-v143-demucs-single-baseline-probe")

probe_image = (
    separator_gpu_image
    .add_local_python_source(
        "v143_production_separator",
        "v143_seeded_audio_separator_cli",
        "v143_seeded_separator",
    )
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


def marker(name: str, **fields: object) -> None:
    payload = {"marker": name, **fields}
    print(json.dumps(payload, sort_keys=True), flush=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_authorized_clip(audio_url: str, clip_seconds: float, root: Path) -> Path:
    if not audio_url.startswith("https://raw.githubusercontent.com/dadrockyt-sys/dadrock-tabs-android/main/"):
        raise ValueError("Diagnostic audio URL must be the authorized repository-owned raw GitHub asset")
    if clip_seconds != 6.0:
        raise ValueError("Single frozen baseline is fixed at exactly 6.0 seconds")

    source = root / "source.m4a"
    clip = root / "clip.wav"
    marker("baseline.remote.authorized-download.start")
    request = urllib.request.Request(
        audio_url,
        headers={"User-Agent": "DadRock-V143-Single-Baseline-Probe/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        source.write_bytes(response.read())
    marker("baseline.remote.authorized-download.done", sourceBytes=source.stat().st_size)

    marker("baseline.remote.clip-create.start", clipSeconds=clip_seconds)
    ffmpeg = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-t",
            f"{clip_seconds:.3f}",
            "-vn",
            "-ar",
            "44100",
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            str(clip),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if ffmpeg.returncode != 0 or not clip.exists() or clip.stat().st_size <= 0:
        raise RuntimeError("Diagnostic clip creation failed")
    marker("baseline.remote.clip-create.done", clipBytes=clip.stat().st_size)
    return clip


@app.function(
    image=probe_image,
    gpu="L4",
    timeout=420,
    memory=8192,
)
def run_single_frozen_baseline(audio_url: str, clip_seconds: float = 6.0) -> dict:
    """Run exactly one frozen CPU/single-thread Demucs pass and return aggregate-only evidence."""
    from v143_production_separator import separate_demucs_guitar
    from v143_seeded_separator import (
        CUBLAS_WORKSPACE_CONFIG,
        DEMUCS_SINGLE_THREAD_ENV,
        SEPARATOR_SEED,
        seeded_audio_separator_cli,
    )

    common_env = {
        "PYTHONHASHSEED": SEPARATOR_SEED,
        "V143_SEPARATOR_SEED": SEPARATOR_SEED,
        "CUBLAS_WORKSPACE_CONFIG": CUBLAS_WORKSPACE_CONFIG,
        "NVIDIA_TF32_OVERRIDE": "0",
    }
    frozen_env = dict(DEMUCS_SINGLE_THREAD_ENV)
    cli = seeded_audio_separator_cli()

    marker(
        "baseline.remote.enter",
        policy="frozen",
        clipSeconds=clip_seconds,
        device="cpu",
    )

    with tempfile.TemporaryDirectory(prefix="v143-demucs-single-baseline-") as temp_dir:
        root = Path(temp_dir)
        clip = make_authorized_clip(audio_url, clip_seconds, root)
        output_dir = root / "output"
        marker("baseline.remote.demucs.start", policy="frozen")
        started = time.monotonic()
        with temporary_environment(common_env):
            with temporary_environment(frozen_env):
                result = separate_demucs_guitar(cli, clip, output_dir)
        wall = time.monotonic() - started
        marker(
            "baseline.remote.demucs.done",
            elapsedSeconds=round(float(result["elapsedSeconds"]), 3),
            wallSeconds=round(wall, 3),
        )

        stem = Path(result["path"])
        aggregate = {
            "schemaVersion": 1,
            "gate": "v143-demucs-single-frozen-baseline",
            "policy": "frozen",
            "clipSeconds": clip_seconds,
            "model": "htdemucs_6s.yaml",
            "singleStem": "Guitar",
            "demucsShifts": 1,
            "demucsOverlap": 0.10,
            "demucsSegmentSize": 6,
            "separatorSeed": 143,
            "device": "cpu",
            "elapsedSeconds": round(float(result["elapsedSeconds"]), 3),
            "wallSeconds": round(wall, 3),
            "sha256": sha256_file(stem),
            "bytes": stem.stat().st_size,
            "referenceFree": True,
            "referenceFacingAccuracyScored": False,
            "referenceScoreCalls": 0,
            "rawAudioRetained": False,
            "stemBytesRetained": False,
        }

    marker("baseline.remote.aggregate.return", completed=True)
    return aggregate
