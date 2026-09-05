from __future__ import annotations

import hashlib
import io
import json
import multiprocessing
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import modal

from v143_ai_tab_gpu_worker import image as separator_image


APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EXPECTED_NORMALIZED_SHA256 = "ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f"
EXPECTED_DIRECT_GUITAR_SHA256 = "0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c"
EXPECTED_DIRECT_PCM_SHA256 = "2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed"
EXPECTED_ROFORMER_SHA256 = "ce7ae8c6c57e00e1e191b8c15a8c4f39627cbcdf3b7a75ac7ca4c246f6f64b14"
EXPECTED_ROFORMER_PCM_SHA256 = "16e0a16a54ab1b007d15647d293900ecfbfabceccfa886f004a86162d4a454dd"
EXPECTED_CASCADE_GUITAR_SHA256 = "546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41"
EXPECTED_CASCADE_PCM_SHA256 = "75c0feefb416d8438641ceebe903253f935bd19c550e97e9ef0a90426e7727ba"
EXPECTED_SHIFT_TRACE = ["0,22050,6026"]
EXPECTED_DEMUCS_WEIGHT_FILENAME = "5c90dfd2-34c22ccb.th"
EXPECTED_DEMUCS_WEIGHT_SHA256 = "34c22ccb381c6f9fdbf324f04e1e2fe21aaaf293f5ded163a162697ff9a02ddd"
EXPECTED_DEMUCS_CONFIG_FILENAME = "htdemucs_6s.yaml"
EXPECTED_DEMUCS_CONFIG_SHA256 = "207405151270af8fd81c2373c25d27950916682ac91dca7884a11ce13dad6f58"
EXPECTED_ROFORMER_WEIGHT_SHA256 = "5b84f37e8d444c8cb30c79d77f613a41c05868ff9c9ac6c7049c00aefae115aa"
HISTORICAL_SEQUENTIAL_STAGE_SUM_SECONDS = 649.633 + 90.044 + 748.029

MODULES = (
    "v143_ai_tab_gpu_worker",
    "v143_production_separator",
    "v143_seeded_separator",
    "v143_seeded_audio_separator_cli",
    "v143_view_level_demucs_child",
)

app = modal.App("dadrock-v143-view-level-concurrency-probe")
image = separator_image.add_local_python_source(*MODULES)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _decode_pcm_identity(wav_bytes: bytes) -> dict[str, Any]:
    import numpy as np
    import soundfile as sf

    pcm, sample_rate = sf.read(io.BytesIO(wav_bytes), dtype="int16", always_2d=True)
    pcm_le = np.asarray(pcm, dtype="<i2", order="C")
    return {
        "pcmSha256": _sha256_bytes(pcm_le.tobytes(order="C")),
        "sampleRate": int(sample_rate),
        "pcmFrames": int(pcm_le.shape[0]),
        "pcmChannels": int(pcm_le.shape[1]),
    }


def _model_dir() -> Path:
    return Path(os.environ.get("AUDIO_SEPARATOR_MODEL_DIR", "/tmp/audio-separator-models/"))


def _prefetch_models(cli: list[str]) -> dict[str, Any]:
    from v143_production_separator import BS_ROFORMER_MODEL, DEMUCS_6S_MODEL
    from v143_seeded_separator import (
        CUBLAS_WORKSPACE_CONFIG,
        DEMUCS_SINGLE_THREAD_ENV,
        SEPARATOR_SEED,
        _temporary_environment,
    )

    common_env = {
        "PYTHONHASHSEED": SEPARATOR_SEED,
        "V143_SEPARATOR_SEED": SEPARATOR_SEED,
        "CUBLAS_WORKSPACE_CONFIG": CUBLAS_WORKSPACE_CONFIG,
        "NVIDIA_TF32_OVERRIDE": "0",
    }

    with _temporary_environment(common_env):
        with _temporary_environment({"CUDA_VISIBLE_DEVICES": None}):
            roformer_download = subprocess.run(
                cli + ["--model_filename", BS_ROFORMER_MODEL, "--download_model_only"],
                capture_output=True,
                text=True,
                check=False,
            )
        demucs_env = dict(DEMUCS_SINGLE_THREAD_ENV)
        with _temporary_environment(demucs_env):
            demucs_download = subprocess.run(
                cli + ["--model_filename", DEMUCS_6S_MODEL, "--download_model_only"],
                capture_output=True,
                text=True,
                check=False,
            )

    if roformer_download.returncode != 0:
        raise RuntimeError(f"RoFormer prefetch failed: {roformer_download.stderr[-2000:]}")
    if demucs_download.returncode != 0:
        raise RuntimeError(f"Demucs prefetch failed: {demucs_download.stderr[-2000:]}")

    model_dir = _model_dir()
    roformer_path = model_dir / BS_ROFORMER_MODEL
    demucs_weight = model_dir / EXPECTED_DEMUCS_WEIGHT_FILENAME
    demucs_config = model_dir / EXPECTED_DEMUCS_CONFIG_FILENAME
    for path in (roformer_path, demucs_weight, demucs_config):
        if not path.is_file() or path.stat().st_size <= 0:
            raise RuntimeError(f"model artifact missing: {path}")

    identity = {
        "roformerWeightSha256": _sha256_file(roformer_path),
        "roformerWeightBytes": int(roformer_path.stat().st_size),
        "demucsWeightSha256": _sha256_file(demucs_weight),
        "demucsWeightBytes": int(demucs_weight.stat().st_size),
        "demucsConfigSha256": _sha256_file(demucs_config),
        "demucsConfigBytes": int(demucs_config.stat().st_size),
    }
    if identity["roformerWeightSha256"] != EXPECTED_ROFORMER_WEIGHT_SHA256:
        raise RuntimeError(f"RoFormer weight identity changed: {identity}")
    if identity["demucsWeightSha256"] != EXPECTED_DEMUCS_WEIGHT_SHA256:
        raise RuntimeError(f"Demucs weight identity changed: {identity}")
    if identity["demucsConfigSha256"] != EXPECTED_DEMUCS_CONFIG_SHA256:
        raise RuntimeError(f"Demucs config identity changed: {identity}")
    return identity


def _read_child_result(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"{label} child result missing: {path}")
    result = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict) or result.get("completed") is not True:
        raise RuntimeError(f"{label} exact Demucs child failed: {result}")
    output = Path(str(result.get("path") or ""))
    if not output.is_file() or output.stat().st_size <= 0:
        raise RuntimeError(f"{label} child output missing: {output}")
    result["outputPath"] = str(output)
    return result


def _read_trace(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


def _read_runtime(path: Path) -> dict[str, Any] | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _assert_exact_demucs_runtime(runtime: dict[str, Any] | None, label: str) -> None:
    if not isinstance(runtime, dict):
        raise RuntimeError(f"{label} Demucs runtime trace missing")
    env = runtime.get("environment") or {}
    if (
        runtime.get("mkldnnEnabled") is not False
        or int(runtime.get("torchNumThreads", 0)) != 1
        or int(runtime.get("torchNumInteropThreads", 0)) != 1
        or str(runtime.get("torchCpuCapability") or "").upper() != "DEFAULT"
        or env.get("V143_DEMUCS_DISABLE_MKLDNN") != "1"
        or env.get("OMP_NUM_THREADS") != "1"
        or env.get("MKL_NUM_THREADS") != "1"
        or env.get("MKL_CBWR") != "COMPATIBLE"
    ):
        raise RuntimeError(f"{label} exact CPU runtime invariant changed: {runtime}")


@app.function(image=image, gpu="L4", cpu=2.0, timeout=1800, memory=8192)
def probe(source_audio: bytes, suffix: str = ".m4a") -> dict[str, Any]:
    import soundfile as sf
    import torch

    from v143_production_separator import normalize_input_audio, separate_roformer_instrumental
    from v143_seeded_separator import (
        CUBLAS_WORKSPACE_CONFIG,
        SEPARATOR_SEED,
        _temporary_environment,
        seeded_audio_separator_cli,
    )
    from v143_view_level_demucs_child import run_exact_demucs_child

    source_sha = _sha256_bytes(source_audio)
    if source_sha != APPROVED_AUDIO_SHA256:
        raise RuntimeError(f"approved fixture SHA changed: {source_sha}")
    if not torch.cuda.is_available():
        raise RuntimeError("view-level concurrency probe requires L4 RoFormer execution")

    temp = tempfile.TemporaryDirectory(prefix="v143-view-level-concurrency-")
    root = Path(temp.name)
    summary: dict[str, Any] = {}

    try:
        source = root / f"source{suffix if suffix.startswith('.') else '.audio'}"
        source.write_bytes(source_audio)
        normalized = normalize_input_audio(source, root / "normalized")
        normalized_sha = _sha256_file(normalized)
        if normalized_sha != EXPECTED_NORMALIZED_SHA256:
            raise RuntimeError(f"normalized exact anchor changed: {normalized_sha}")

        info = sf.info(str(normalized))
        if int(info.samplerate) != 44100 or int(info.channels) != 2:
            raise RuntimeError(f"normalized format changed: {info}")

        cli = seeded_audio_separator_cli()
        model_identity = _prefetch_models(cli)

        direct_shift = root / "direct-shift.txt"
        direct_runtime_path = root / "direct-runtime.json"
        direct_result_path = root / "direct-result.json"
        cascade_shift = root / "cascade-shift.txt"
        cascade_runtime_path = root / "cascade-runtime.json"
        cascade_result_path = root / "cascade-result.json"

        ctx = multiprocessing.get_context("spawn")
        direct_process = ctx.Process(
            target=run_exact_demucs_child,
            args=(
                str(normalized),
                str(root / "direct"),
                str(direct_shift),
                str(direct_runtime_path),
                str(direct_result_path),
            ),
            name="v143-direct-exact-demucs",
        )

        concurrency_started = time.monotonic()
        direct_started = time.monotonic()
        direct_process.start()

        common_env = {
            "PYTHONHASHSEED": SEPARATOR_SEED,
            "V143_SEPARATOR_SEED": SEPARATOR_SEED,
            "CUBLAS_WORKSPACE_CONFIG": CUBLAS_WORKSPACE_CONFIG,
            "NVIDIA_TF32_OVERRIDE": "0",
        }
        roformer_started = time.monotonic()
        with _temporary_environment(common_env):
            with _temporary_environment({"CUDA_VISIBLE_DEVICES": None}):
                roformer = separate_roformer_instrumental(
                    seeded_audio_separator_cli(),
                    normalized,
                    root / "roformer",
                )
        roformer_wall = time.monotonic() - roformer_started

        roformer_path = Path(str(roformer["path"]))
        roformer_bytes = roformer_path.read_bytes()
        roformer_pcm = _decode_pcm_identity(roformer_bytes)
        if _sha256_bytes(roformer_bytes) != EXPECTED_ROFORMER_SHA256:
            raise RuntimeError("RoFormer intermediate WAV identity changed")
        if roformer_pcm["pcmSha256"] != EXPECTED_ROFORMER_PCM_SHA256:
            raise RuntimeError("RoFormer intermediate PCM identity changed")

        cascade_process = ctx.Process(
            target=run_exact_demucs_child,
            args=(
                str(roformer_path),
                str(root / "cascade"),
                str(cascade_shift),
                str(cascade_runtime_path),
                str(cascade_result_path),
            ),
            name="v143-cascade-exact-demucs",
        )
        cascade_started = time.monotonic()
        cascade_process.start()

        direct_process.join(timeout=1200)
        if direct_process.is_alive():
            direct_process.terminate()
            direct_process.join(timeout=10)
            raise RuntimeError("direct exact Demucs child exceeded concurrency deadline")
        if direct_process.exitcode != 0:
            raise RuntimeError(f"direct exact Demucs child exitCode={direct_process.exitcode}")
        direct_wall = time.monotonic() - direct_started

        cascade_process.join(timeout=1200)
        if cascade_process.is_alive():
            cascade_process.terminate()
            cascade_process.join(timeout=10)
            raise RuntimeError("cascade exact Demucs child exceeded concurrency deadline")
        if cascade_process.exitcode != 0:
            raise RuntimeError(f"cascade exact Demucs child exitCode={cascade_process.exitcode}")
        cascade_wall = time.monotonic() - cascade_started
        concurrent_wall = time.monotonic() - concurrency_started

        direct_result = _read_child_result(direct_result_path, "direct")
        cascade_result = _read_child_result(cascade_result_path, "cascade")
        direct_path = Path(str(direct_result["outputPath"]))
        cascade_path = Path(str(cascade_result["outputPath"]))
        direct_bytes = direct_path.read_bytes()
        cascade_bytes = cascade_path.read_bytes()
        direct_pcm = _decode_pcm_identity(direct_bytes)
        cascade_pcm = _decode_pcm_identity(cascade_bytes)

        direct_sha = _sha256_bytes(direct_bytes)
        cascade_sha = _sha256_bytes(cascade_bytes)
        direct_trace = _read_trace(direct_shift)
        cascade_trace = _read_trace(cascade_shift)
        direct_runtime = _read_runtime(direct_runtime_path)
        cascade_runtime = _read_runtime(cascade_runtime_path)

        if direct_sha != EXPECTED_DIRECT_GUITAR_SHA256:
            raise RuntimeError(f"direct concurrent Guitar identity changed: {direct_sha}")
        if direct_pcm["pcmSha256"] != EXPECTED_DIRECT_PCM_SHA256:
            raise RuntimeError(f"direct concurrent PCM identity changed: {direct_pcm['pcmSha256']}")
        if cascade_sha != EXPECTED_CASCADE_GUITAR_SHA256:
            raise RuntimeError(f"cascade concurrent Guitar identity changed: {cascade_sha}")
        if cascade_pcm["pcmSha256"] != EXPECTED_CASCADE_PCM_SHA256:
            raise RuntimeError(f"cascade concurrent PCM identity changed: {cascade_pcm['pcmSha256']}")
        if direct_trace != EXPECTED_SHIFT_TRACE or cascade_trace != EXPECTED_SHIFT_TRACE:
            raise RuntimeError(
                f"concurrent shift trace changed: direct={direct_trace}, cascade={cascade_trace}"
            )
        _assert_exact_demucs_runtime(direct_runtime, "direct")
        _assert_exact_demucs_runtime(cascade_runtime, "cascade")

        gpu_capability = torch.cuda.get_device_capability(0)
        stage_sum = float(direct_result.get("elapsedSeconds") or 0.0) + float(
            roformer.get("elapsedSeconds") or 0.0
        ) + float(cascade_result.get("elapsedSeconds") or 0.0)
        contextual_speedup = (
            HISTORICAL_SEQUENTIAL_STAGE_SUM_SECONDS / concurrent_wall
            if concurrent_wall > 0
            else None
        )

        summary = {
            "schemaVersion": 1,
            "gate": "v143-view-level-concurrency",
            "sourceSha256": source_sha,
            "normalizedWavSha256": normalized_sha,
            "modelIdentity": model_identity,
            "runtime": {
                "modalGpu": "L4",
                "modalCpuRequested": 2.0,
                "torchVersion": str(torch.__version__),
                "torchCudaVersion": None if torch.version.cuda is None else str(torch.version.cuda),
                "cudaDeviceName": str(torch.cuda.get_device_name(0)),
                "cudaComputeCapability": [int(gpu_capability[0]), int(gpu_capability[1])],
                "demucsExecutionDevice": "cpu",
                "demucsCpuThreadsPerChild": 1,
                "childProcessStartMethod": "spawn",
            },
            "schedule": {
                "directStartsBeforeRoformer": True,
                "cascadeStartsAfterRoformer": True,
                "intraDemucsParallelism": False,
                "unchangedExactDemucsInvocation": True,
                "crossRequestPersistence": False,
            },
            "roformerInstrumentalSha256": _sha256_bytes(roformer_bytes),
            "roformerInstrumentalPcmInt16Sha256": roformer_pcm["pcmSha256"],
            "directGuitarSha256": direct_sha,
            "directPcmInt16Sha256": direct_pcm["pcmSha256"],
            "cascadeGuitarSha256": cascade_sha,
            "cascadePcmInt16Sha256": cascade_pcm["pcmSha256"],
            "directShiftTrace": direct_trace,
            "cascadeShiftTrace": cascade_trace,
            "directChildRuntime": direct_runtime,
            "cascadeChildRuntime": cascade_runtime,
            "roformerElapsedSeconds": roformer.get("elapsedSeconds"),
            "directDemucsElapsedSeconds": direct_result.get("elapsedSeconds"),
            "cascadeDemucsElapsedSeconds": cascade_result.get("elapsedSeconds"),
            "roformerWallSeconds": round(roformer_wall, 3),
            "directProcessWallSeconds": round(direct_wall, 3),
            "cascadeProcessWallSeconds": round(cascade_wall, 3),
            "concurrentSeparationWallSeconds": round(concurrent_wall, 3),
            "sumOfConcurrentStageElapsedSeconds": round(stage_sum, 3),
            "historicalSequentialStageSumSeconds": round(HISTORICAL_SEQUENTIAL_STAGE_SUM_SECONDS, 3),
            "crossRunContextualSpeedup": round(contextual_speedup, 3) if contextual_speedup else None,
            "exactDirectParityPassed": True,
            "exactCascadeParityPassed": True,
            "exactRoformerParityPassed": True,
            "referenceFree": True,
            "referenceFacingAccuracyScored": False,
            "referenceScoreCalls": 0,
            "qualityVerdictMade": False,
            "gpuDemucsRequested": False,
            "gpuPerformanceComparisonPerformed": False,
            "productionWorkerChanged": False,
            "productionBridgeChanged": False,
            "vercelChanged": False,
            "mainMergePerformed": False,
        }
    finally:
        temp.cleanup()

    if root.exists():
        raise RuntimeError(f"view-level concurrency cleanup failed: {root}")
    summary["cleanupPassed"] = True
    summary["rawAudioRetained"] = False
    summary["stemBytesRetained"] = False
    summary["allPassed"] = bool(
        summary.get("exactDirectParityPassed")
        and summary.get("exactCascadeParityPassed")
        and summary.get("exactRoformerParityPassed")
        and summary.get("cleanupPassed")
        and summary.get("referenceScoreCalls") == 0
    )
    return summary


if __name__ == "__main__":
    pass
