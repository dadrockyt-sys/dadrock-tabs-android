from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

import modal

from v143_ai_tab_gpu_worker import image as separator_image


APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
CPU_ANCHOR_NORMALIZED_SHA256 = "ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f"
CPU_ANCHOR_GUITAR_SHA256 = "0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c"
CPU_ANCHOR_PCM_SHA256 = "2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed"
EXPECTED_SHIFT_TRACE = ["0,22050,6026"]

MODULES = (
    "v143_ai_tab_gpu_worker",
    "v143_production_separator",
    "v143_seeded_separator",
    "v143_seeded_audio_separator_cli",
)

app = modal.App("dadrock-v143-demucs-gpu-exact-probe")
image = separator_image.add_local_python_source(*MODULES)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@app.function(image=image, gpu="L4", timeout=420, memory=8192)
def probe(source_audio: bytes, suffix: str = ".m4a") -> dict[str, Any]:
    """One direct Demucs6s L4 candidate pass, aggregate-only and reference-free."""
    import numpy as np
    import soundfile as sf
    import torch

    from v143_production_separator import normalize_input_audio, separate_demucs_guitar
    from v143_seeded_separator import (
        CUBLAS_WORKSPACE_CONFIG,
        DEMUCS_SINGLE_THREAD_ENV,
        SEPARATOR_SEED,
        _temporary_environment,
        seeded_audio_separator_cli,
    )

    if not source_audio:
        raise ValueError("source audio empty")
    source_sha = _sha256_bytes(source_audio)
    if source_sha != APPROVED_AUDIO_SHA256:
        raise RuntimeError(f"approved fixture SHA changed: {source_sha}")
    if not torch.cuda.is_available():
        raise RuntimeError("L4 requested but Torch CUDA is unavailable")

    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="v143-demucs-gpu-exact-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"source{suffix if suffix.startswith('.') else '.audio'}"
        source.write_bytes(source_audio)
        normalized = normalize_input_audio(source, root / "normalized")
        shift_trace = root / "demucs-shift-trace.txt"
        runtime_trace = root / "demucs-runtime-trace.json"

        common_env = {
            "PYTHONHASHSEED": SEPARATOR_SEED,
            "V143_SEPARATOR_SEED": SEPARATOR_SEED,
            "CUBLAS_WORKSPACE_CONFIG": CUBLAS_WORKSPACE_CONFIG,
            "NVIDIA_TF32_OVERRIDE": "0",
        }

        # Preserve the final deterministic Demucs controls while allowing the
        # L4 to remain visible. Model, seed, shifts, overlap, segment and stem
        # are identical to the frozen CPU anchor. CPU-side numerical helpers
        # remain in the same conservative/single-thread mode.
        gpu_env = dict(DEMUCS_SINGLE_THREAD_ENV)
        gpu_env.pop("CUDA_VISIBLE_DEVICES", None)
        gpu_env["V143_DEMUCS_SHIFT_TRACE_PATH"] = str(shift_trace)
        gpu_env["V143_DEMUCS_RUNTIME_TRACE_PATH"] = str(runtime_trace)

        print(
            json.dumps(
                {
                    "marker": "gpu-exact.remote.demucs.start",
                    "deviceName": str(torch.cuda.get_device_name(0)),
                    "sourceSha256": source_sha,
                },
                sort_keys=True,
            ),
            flush=True,
        )

        separation_started = time.monotonic()
        with _temporary_environment(common_env):
            with _temporary_environment(gpu_env):
                direct = separate_demucs_guitar(
                    seeded_audio_separator_cli(),
                    normalized,
                    root / "direct",
                )
        separation_wall = time.monotonic() - separation_started

        direct_path = Path(str(direct["path"]))
        if not direct_path.exists() or direct_path.stat().st_size <= 0:
            raise RuntimeError("GPU direct Demucs output missing")

        pcm, sample_rate = sf.read(str(direct_path), dtype="int16", always_2d=True)
        pcm_le = np.asarray(pcm, dtype="<i2", order="C")
        trace_lines = (
            shift_trace.read_text(encoding="utf-8").splitlines()
            if shift_trace.exists()
            else []
        )
        child_runtime = (
            json.loads(runtime_trace.read_text(encoding="utf-8"))
            if runtime_trace.exists()
            else None
        )

        normalized_sha = _sha256_file(normalized)
        guitar_sha = _sha256_file(direct_path)
        pcm_sha = _sha256_bytes(pcm_le.tobytes(order="C"))
        exact_cpu_parity = bool(
            normalized_sha == CPU_ANCHOR_NORMALIZED_SHA256
            and guitar_sha == CPU_ANCHOR_GUITAR_SHA256
            and pcm_sha == CPU_ANCHOR_PCM_SHA256
            and trace_lines == EXPECTED_SHIFT_TRACE
        )

        result = {
            "schemaVersion": 1,
            "gate": "v143-demucs-gpu-exact-probe",
            "sourceSha256": source_sha,
            "normalizedWavSha256": normalized_sha,
            "directGuitarSha256": guitar_sha,
            "directPcmInt16Sha256": pcm_sha,
            "directBytes": int(direct_path.stat().st_size),
            "sampleRate": int(sample_rate),
            "pcmFrames": int(pcm_le.shape[0]),
            "pcmChannels": int(pcm_le.shape[1]),
            "demucsShiftTrace": trace_lines,
            "deviceName": str(torch.cuda.get_device_name(0)),
            "torchVersion": str(torch.__version__),
            "parentCudaAvailable": bool(torch.cuda.is_available()),
            "childRuntime": child_runtime,
            "separationElapsedSeconds": float(direct["elapsedSeconds"]),
            "separationWallSeconds": round(separation_wall, 3),
            "totalRemoteSeconds": round(time.monotonic() - started, 3),
            "cpuAnchorGuitarSha256": CPU_ANCHOR_GUITAR_SHA256,
            "cpuAnchorPcmSha256": CPU_ANCHOR_PCM_SHA256,
            "exactCpuParityPassed": exact_cpu_parity,
            "settings": {
                "demucsModel": "htdemucs_6s.yaml",
                "demucsSingleStem": "Guitar",
                "demucsShifts": 1,
                "demucsOverlap": 0.10,
                "demucsSegmentSize": 6,
                "deterministicSeed": 143,
                "privateShiftRng": True,
                "cublasWorkspaceConfig": CUBLAS_WORKSPACE_CONFIG,
                "tf32Disabled": True,
                "torchDeterministicAlgorithms": True,
                "modalGpuRequested": "L4",
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
                "marker": "gpu-exact.remote.aggregate.return",
                "exactCpuParityPassed": result["exactCpuParityPassed"],
                "separationWallSeconds": result["separationWallSeconds"],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return result
