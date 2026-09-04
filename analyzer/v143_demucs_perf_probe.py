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


app = modal.App("dadrock-v143-demucs-perf-probe")

probe_image = (
    separator_gpu_image
    .add_local_python_source(
        "v143_production_separator",
        "v143_seeded_audio_separator_cli",
        "v143_seeded_separator",
        "v143_demucs_perf_probe_cli",
    )
)


PROMOTION_SPEEDUP_THRESHOLD = 1.25


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


def _policy_runtime(policy: str) -> tuple[list[str], dict[str, str], dict[str, str]]:
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

    if policy == "frozen":
        return seeded_audio_separator_cli(), common_env, dict(DEMUCS_SINGLE_THREAD_ENV)

    if policy == "threads4":
        policy_env = dict(DEMUCS_SINGLE_THREAD_ENV)
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
        return [sys.executable, "-m", "v143_demucs_perf_probe_cli"], common_env, policy_env

    raise ValueError("policy must be frozen or threads4")


def _make_authorized_clip(audio_url: str, clip_seconds: float, root: Path) -> Path:
    if not audio_url.startswith("https://raw.githubusercontent.com/"):
        raise ValueError("Diagnostic audio URL must be the authorized raw GitHub asset")
    if clip_seconds < 6.0 or clip_seconds > 20.0:
        raise ValueError("Diagnostic clip must be between 6 and 20 seconds")

    source = root / "source.m4a"
    clip = root / "clip.wav"
    request = urllib.request.Request(
        audio_url,
        headers={"User-Agent": "DadRock-V143-Demucs-Perf-Probe/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        source.write_bytes(response.read())

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
    return clip


@app.function(
    image=probe_image,
    gpu="L4",
    timeout=1100,
    memory=8192,
)
def run_cpu_policy_once(
    audio_url: str,
    policy: str,
    clip_seconds: float = 6.0,
) -> dict:
    """Run one isolated Demucs policy trial and return aggregate timing/hash only."""
    from v143_production_separator import separate_demucs_guitar

    cli, common_env, policy_env = _policy_runtime(policy)

    with tempfile.TemporaryDirectory(prefix="v143-demucs-micro-") as temp_dir:
        root = Path(temp_dir)
        clip = _make_authorized_clip(audio_url, clip_seconds, root)
        output_dir = root / "output"
        started = time.monotonic()
        with temporary_environment(common_env):
            with temporary_environment(policy_env):
                result = separate_demucs_guitar(cli, clip, output_dir)
        wall = time.monotonic() - started
        stem = Path(result["path"])
        aggregate = {
            "schemaVersion": 1,
            "gate": "v143-demucs-cpu-policy-micro-probe",
            "policy": policy,
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

    return aggregate


@app.function(
    image=probe_image,
    gpu="L4",
    timeout=1100,
    memory=8192,
)
def compare_cpu_thread_policy(
    audio_url: str,
    clip_seconds: float = 12.0,
) -> dict:
    """Compare frozen Demucs CPU/1-thread against CPU/4-thread on one short clip.

    This function is a separate diagnostic app. It never reads references,
    labels, scores, or Production secrets, and it returns only hashes/timings.
    No audio or stem bytes leave the ephemeral Modal container.
    """
    from v143_production_separator import separate_demucs_guitar

    frozen_cli, common_env, frozen_env = _policy_runtime("frozen")
    threads4_cli, _, threads4_env = _policy_runtime("threads4")

    with tempfile.TemporaryDirectory(prefix="v143-demucs-perf-") as temp_dir:
        root = Path(temp_dir)
        clip = _make_authorized_clip(audio_url, clip_seconds, root)

        def run_once(label: str, cli: list[str], policy_env: dict[str, str]) -> dict:
            output_dir = root / label
            started = time.monotonic()
            with temporary_environment(common_env):
                with temporary_environment(policy_env):
                    result = separate_demucs_guitar(cli, clip, output_dir)
            wall = time.monotonic() - started
            stem = Path(result["path"])
            return {
                "label": label,
                "elapsedSeconds": round(float(result["elapsedSeconds"]), 3),
                "wallSeconds": round(wall, 3),
                "sha256": sha256_file(stem),
                "bytes": stem.stat().st_size,
            }

        runs = [
            run_once("frozen-1", frozen_cli, frozen_env),
            run_once("frozen-2", frozen_cli, frozen_env),
            run_once("threads4-1", threads4_cli, threads4_env),
            run_once("threads4-2", threads4_cli, threads4_env),
        ]

    frozen_hashes = {runs[0]["sha256"], runs[1]["sha256"]}
    candidate_hashes = {runs[2]["sha256"], runs[3]["sha256"]}
    frozen_repeatable = len(frozen_hashes) == 1
    candidate_repeatable = len(candidate_hashes) == 1
    exact_baseline_parity = (
        frozen_repeatable
        and candidate_repeatable
        and next(iter(frozen_hashes)) == next(iter(candidate_hashes))
    )

    frozen_mean = (runs[0]["elapsedSeconds"] + runs[1]["elapsedSeconds"]) / 2.0
    candidate_mean = (runs[2]["elapsedSeconds"] + runs[3]["elapsedSeconds"]) / 2.0
    speedup = frozen_mean / candidate_mean if candidate_mean > 0 else None

    return {
        "schemaVersion": 1,
        "gate": "v143-demucs-cpu-thread-policy-probe",
        "clipSeconds": clip_seconds,
        "model": "htdemucs_6s.yaml",
        "singleStem": "Guitar",
        "demucsShifts": 1,
        "demucsOverlap": 0.10,
        "demucsSegmentSize": 6,
        "separatorSeed": 143,
        "device": "cpu",
        "runs": runs,
        "frozenRepeatable": frozen_repeatable,
        "candidateRepeatable": candidate_repeatable,
        "exactBaselineParity": exact_baseline_parity,
        "frozenMeanSeconds": round(frozen_mean, 3),
        "candidateMeanSeconds": round(candidate_mean, 3),
        "speedup": None if speedup is None else round(speedup, 3),
        "promotionSpeedupThreshold": PROMOTION_SPEEDUP_THRESHOLD,
        "promotionEligible": bool(
            exact_baseline_parity
            and speedup is not None
            and speedup >= PROMOTION_SPEEDUP_THRESHOLD
        ),
        "referenceFree": True,
        "referenceFacingAccuracyScored": False,
        "referenceScoreCalls": 0,
        "rawAudioRetained": False,
        "stemBytesRetained": False,
    }
