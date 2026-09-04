from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import modal

from v143_ai_tab_gpu_worker import image as separator_image


APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
CPU_ANCHOR_NORMALIZED_SHA256 = "ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f"
CPU_ANCHOR_GUITAR_SHA256 = "0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c"
CPU_ANCHOR_PCM_SHA256 = "2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed"
EXPECTED_SHIFT_TRACE = ["0,22050,6026"]
SPLIT_WORKERS = 4

MODULES = (
    "v143_ai_tab_gpu_worker",
    "v143_production_separator",
    "v143_seeded_separator",
    "v143_seeded_audio_separator_cli",
    "v143_demucs_split_parallel_cli",
)

app = modal.App("dadrock-v143-demucs-split-parallel-probe")
image = separator_image.add_local_python_source(*MODULES)


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


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_parallel_cli() -> list[str]:
    return [sys.executable, "-m", "v143_demucs_split_parallel_cli"]


@app.function(image=image, cpu=4.0, timeout=480, memory=16384)
def probe(source_audio: bytes, suffix: str = ".m4a") -> dict:
    """Run the exact frozen CPU Demucs graph with only split-chunk concurrency changed."""
    import numpy as np
    import soundfile as sf
    import torch

    from v143_production_separator import normalize_input_audio, separate_demucs_guitar
    from v143_seeded_separator import CUBLAS_WORKSPACE_CONFIG, DEMUCS_SINGLE_THREAD_ENV, SEPARATOR_SEED

    if not source_audio:
        raise ValueError("source audio empty")
    source_sha = sha256_bytes(source_audio)
    if source_sha != APPROVED_AUDIO_SHA256:
        raise RuntimeError(f"approved fixture SHA changed: {source_sha}")
    if torch.cuda.is_available():
        raise RuntimeError("split-parallel CPU probe must not have CUDA available")

    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="v143-demucs-split-parallel-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"source{suffix if suffix.startswith('.') else '.audio'}"
        source.write_bytes(source_audio)
        normalized = normalize_input_audio(source, root / "normalized")
        shift_trace = root / "demucs-shift-trace.txt"
        runtime_trace = root / "demucs-runtime-trace.json"
        parallel_trace = root / "demucs-split-parallel-trace.json"

        common_env = {
            "PYTHONHASHSEED": SEPARATOR_SEED,
            "V143_SEPARATOR_SEED": SEPARATOR_SEED,
            "CUBLAS_WORKSPACE_CONFIG": CUBLAS_WORKSPACE_CONFIG,
            "NVIDIA_TF32_OVERRIDE": "0",
        }
        demucs_env = dict(DEMUCS_SINGLE_THREAD_ENV)
        demucs_env["V143_DEMUCS_FIXED_SHIFT_RNG"] = "1"
        demucs_env["V143_DEMUCS_SHIFT_TRACE_PATH"] = str(shift_trace)
        demucs_env["V143_DEMUCS_RUNTIME_TRACE_PATH"] = str(runtime_trace)
        demucs_env["V143_DEMUCS_SPLIT_WORKERS"] = str(SPLIT_WORKERS)
        demucs_env["V143_DEMUCS_SPLIT_PARALLEL_TRACE_PATH"] = str(parallel_trace)

        print(
            json.dumps(
                {
                    "marker": "split-parallel.remote.demucs.start",
                    "splitWorkers": SPLIT_WORKERS,
                    "modalCpu": 4.0,
                    "torchThreadsPerOp": 1,
                },
                sort_keys=True,
            ),
            flush=True,
        )

        separation_started = time.monotonic()
        with temporary_environment(common_env):
            with temporary_environment(demucs_env):
                direct = separate_demucs_guitar(
                    split_parallel_cli(),
                    normalized,
                    root / "direct",
                )
        separation_wall = time.monotonic() - separation_started

        direct_path = Path(str(direct["path"]))
        if not direct_path.exists() or direct_path.stat().st_size <= 0:
            raise RuntimeError("split-parallel direct Demucs output missing")

        pcm, sample_rate = sf.read(str(direct_path), dtype="int16", always_2d=True)
        pcm_le = np.asarray(pcm, dtype="<i2", order="C")
        shift_lines = shift_trace.read_text(encoding="utf-8").splitlines() if shift_trace.exists() else []
        child_runtime = json.loads(runtime_trace.read_text(encoding="utf-8")) if runtime_trace.exists() else None
        split_trace = json.loads(parallel_trace.read_text(encoding="utf-8")) if parallel_trace.exists() else None

        normalized_sha = sha256_file(normalized)
        guitar_sha = sha256_file(direct_path)
        pcm_sha = sha256_bytes(pcm_le.tobytes(order="C"))
        exact_cpu_parity = bool(
            normalized_sha == CPU_ANCHOR_NORMALIZED_SHA256
            and guitar_sha == CPU_ANCHOR_GUITAR_SHA256
            and pcm_sha == CPU_ANCHOR_PCM_SHA256
            and shift_lines == EXPECTED_SHIFT_TRACE
        )

        result = {
            "schemaVersion": 1,
            "gate": "v143-demucs-split-parallel-probe",
            "sourceSha256": source_sha,
            "normalizedWavSha256": normalized_sha,
            "directGuitarSha256": guitar_sha,
            "directPcmInt16Sha256": pcm_sha,
            "directBytes": int(direct_path.stat().st_size),
            "sampleRate": int(sample_rate),
            "pcmFrames": int(pcm_le.shape[0]),
            "pcmChannels": int(pcm_le.shape[1]),
            "demucsShiftTrace": shift_lines,
            "childRuntime": child_runtime,
            "splitParallelTrace": split_trace,
            "separationElapsedSeconds": float(direct["elapsedSeconds"]),
            "separationWallSeconds": round(separation_wall, 3),
            "totalRemoteSeconds": round(time.monotonic() - started, 3),
            "exactCpuParityPassed": exact_cpu_parity,
            "settings": {
                "demucsModel": "htdemucs_6s.yaml",
                "demucsSingleStem": "Guitar",
                "demucsShifts": 1,
                "demucsOverlap": 0.10,
                "demucsSegmentSize": 6,
                "demucsExecutionDevice": "cpu",
                "demucsTorchThreadsPerOp": 1,
                "demucsSplitWorkers": SPLIT_WORKERS,
                "modalCpu": 4.0,
                "deterministicSeed": 143,
                "privateShiftRng": True,
                "mkldnnDisabled": True,
                "atenCpuCapability": "default",
                "mklCbwr": "COMPATIBLE",
            },
            "referenceFree": True,
            "referenceFacingAccuracyScored": False,
            "referenceScoreCalls": 0,
            "rawAudioRetained": False,
            "stemBytesRetained": False,
            "productionWorkerChanged": False,
            "productionBridgeChanged": False,
            "vercelChanged": False,
        }

    print(
        json.dumps(
            {
                "marker": "split-parallel.remote.aggregate.return",
                "exactCpuParityPassed": result["exactCpuParityPassed"],
                "separationWallSeconds": result["separationWallSeconds"],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return result
