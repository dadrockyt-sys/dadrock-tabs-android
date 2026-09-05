from __future__ import annotations

import hashlib
import io
import json
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
EXPECTED_SHIFT = "0,22050,6026"
EXPECTED_DEMUCS_WEIGHT_FILENAME = "5c90dfd2-34c22ccb.th"
EXPECTED_DEMUCS_WEIGHT_SHA256 = "34c22ccb381c6f9fdbf324f04e1e2fe21aaaf293f5ded163a162697ff9a02ddd"
EXPECTED_DEMUCS_CONFIG_FILENAME = "htdemucs_6s.yaml"
EXPECTED_DEMUCS_CONFIG_SHA256 = "207405151270af8fd81c2373c25d27950916682ac91dca7884a11ce13dad6f58"
EXPECTED_ROFORMER_WEIGHT_SHA256 = "5b84f37e8d444c8cb30c79d77f613a41c05868ff9c9ac6c7049c00aefae115aa"
EXPECTED_OUTPUT_NAMES = {
    "directGuitar": "direct-demucs6s-guitar.wav",
    "roformerInstrumental": "bsroformer-instrumental.wav",
    "cascadeGuitar": "bsroformer-demucs6s-guitar.wav",
}
EXPECTED_TOP_LEVEL_KEYS = {
    "directGuitar",
    "roformerInstrumental",
    "cascadeGuitar",
    "models",
    "settings",
    "referenceFree",
    "diagnosticOnly",
}

MODULES = (
    "v143_ai_tab_gpu_worker",
    "v143_production_separator",
    "v143_seeded_separator",
    "v143_seeded_audio_separator_cli",
)

RUNTIME_APP_NAME = os.environ.get("V143_SEEDED_SCHEDULER_RUNTIME_APP_NAME", "").strip()
if not RUNTIME_APP_NAME:
    raise RuntimeError("V143_SEEDED_SCHEDULER_RUNTIME_APP_NAME is required for isolated runtime gate deployment")

app = modal.App(RUNTIME_APP_NAME)
image = separator_image.add_local_python_source(*MODULES)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _decode_pcm_identity(path: Path) -> dict[str, Any]:
    import numpy as np
    import soundfile as sf

    wav_bytes = path.read_bytes()
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


def _prefetch_and_verify_models() -> dict[str, Any]:
    from v143_production_separator import BS_ROFORMER_MODEL, DEMUCS_6S_MODEL
    from v143_seeded_separator import (
        CUBLAS_WORKSPACE_CONFIG,
        DEMUCS_SINGLE_THREAD_ENV,
        SEPARATOR_SEED,
        _temporary_environment,
        seeded_audio_separator_cli,
    )

    cli = seeded_audio_separator_cli()
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
        with _temporary_environment(DEMUCS_SINGLE_THREAD_ENV):
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
        "demucsWeightSha256": _sha256_file(demucs_weight),
        "demucsConfigSha256": _sha256_file(demucs_config),
    }
    if identity["roformerWeightSha256"] != EXPECTED_ROFORMER_WEIGHT_SHA256:
        raise RuntimeError(f"RoFormer weight identity changed: {identity}")
    if identity["demucsWeightSha256"] != EXPECTED_DEMUCS_WEIGHT_SHA256:
        raise RuntimeError(f"Demucs weight identity changed: {identity}")
    if identity["demucsConfigSha256"] != EXPECTED_DEMUCS_CONFIG_SHA256:
        raise RuntimeError(f"Demucs config identity changed: {identity}")
    return identity


def _assert_runtime_trace(runtime: dict[str, Any]) -> None:
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
        raise RuntimeError(f"exact CPU runtime invariant changed: {runtime}")


@app.function(image=image, gpu="L4", cpu=2.0, timeout=1800, memory=8192)
def probe(source_audio: bytes, suffix: str = ".m4a") -> dict[str, Any]:
    import torch

    from v143_production_separator import BS_ROFORMER_MODEL, DEMUCS_6S_MODEL
    from v143_seeded_separator import _temporary_environment, build_seeded_v143_stems

    source_sha = _sha256_bytes(source_audio)
    if source_sha != APPROVED_AUDIO_SHA256:
        raise RuntimeError(f"approved fixture SHA changed: {source_sha}")
    if not torch.cuda.is_available():
        raise RuntimeError("seeded scheduler runtime gate requires L4 RoFormer execution")

    temp = tempfile.TemporaryDirectory(prefix="v143-seeded-scheduler-runtime-")
    root = Path(temp.name)
    started = time.monotonic()
    summary: dict[str, Any] = {
        "schemaVersion": 1,
        "gate": "v143-seeded-scheduler-runtime",
        "sourceSha256": source_sha,
        "completed": False,
        "referenceFree": True,
        "referenceFacingInputs": 0,
        "referenceFacingAccuracyScored": False,
        "referenceScoreCalls": 0,
        "qualityVerdictMade": False,
        "rawAudioRetained": False,
        "stemBytesRetained": False,
        "crossRequestPersistence": False,
        "productionWorkerChanged": False,
        "productionBridgeChanged": False,
        "vercelChanged": False,
        "mainMergePerformed": False,
    }

    try:
        source = root / f"source{suffix if suffix.startswith('.') else '.audio'}"
        output_root = root / "outputs"
        shift_trace_path = root / "demucs-shift-trace.txt"
        runtime_trace_path = root / "demucs-runtime-trace.json"
        source.write_bytes(source_audio)

        model_identity = _prefetch_and_verify_models()
        trace_env = {
            "V143_DEMUCS_SHIFT_TRACE_PATH": str(shift_trace_path),
            "V143_DEMUCS_RUNTIME_TRACE_PATH": str(runtime_trace_path),
        }
        with _temporary_environment(trace_env):
            result = build_seeded_v143_stems(source, output_root)

        if set(result) != EXPECTED_TOP_LEVEL_KEYS:
            raise RuntimeError(f"public return keys changed: {sorted(result)}")
        if result.get("referenceFree") is not True or result.get("diagnosticOnly") is not True:
            raise RuntimeError(f"public safety flags changed: {result}")
        if result.get("models") != {"demucs": DEMUCS_6S_MODEL, "bsRoformer": BS_ROFORMER_MODEL}:
            raise RuntimeError(f"public model contract changed: {result.get('models')}")

        settings = result.get("settings") or {}
        expected_settings = {
            "demucsSingleStem": "Guitar",
            "demucsShifts": 1,
            "demucsOverlap": 0.10,
            "demucsSegmentSize": 6,
            "demucsExecutionDevice": "cpu",
            "demucsCpuThreads": 1,
            "demucsShiftRng": "private-seed-143",
            "demucsAtenCpuCapability": "default",
            "demucsMklCbwr": "COMPATIBLE",
            "demucsMkldnnEnabled": False,
            "demucsOneDnnMaxCpuIsa": "SSE41",
            "demucsMklDynamic": False,
            "demucsOmpDynamic": False,
            "roformerSingleStem": "Instrumental",
            "roformerBatchSize": 1,
            "roformerExecutionDevice": "gpu-auto-proven-deterministic",
            "useSoundfile": True,
            "deterministicSeed": 143,
            "pythonHashSeedAtChildStartup": 143,
            "cublasWorkspaceConfig": ":4096:8",
            "tf32Disabled": True,
            "torchDeterministicAlgorithms": True,
        }
        if settings != expected_settings:
            raise RuntimeError(f"public settings contract changed: {settings}")

        paths = {key: Path(str(result[key])) for key in EXPECTED_OUTPUT_NAMES}
        for key, path in paths.items():
            if path.name != EXPECTED_OUTPUT_NAMES[key] or not path.is_file() or path.stat().st_size <= 0:
                raise RuntimeError(f"output contract changed for {key}: {path}")

        normalized = output_root / "_work" / "normalized" / "input-normalized.wav"
        if not normalized.is_file() or _sha256_file(normalized) != EXPECTED_NORMALIZED_SHA256:
            raise RuntimeError("normalized exact anchor changed")

        direct_sha = _sha256_file(paths["directGuitar"])
        roformer_sha = _sha256_file(paths["roformerInstrumental"])
        cascade_sha = _sha256_file(paths["cascadeGuitar"])
        direct_pcm = _decode_pcm_identity(paths["directGuitar"])
        roformer_pcm = _decode_pcm_identity(paths["roformerInstrumental"])
        cascade_pcm = _decode_pcm_identity(paths["cascadeGuitar"])

        if direct_sha != EXPECTED_DIRECT_GUITAR_SHA256:
            raise RuntimeError(f"direct Guitar WAV identity changed: {direct_sha}")
        if direct_pcm["pcmSha256"] != EXPECTED_DIRECT_PCM_SHA256:
            raise RuntimeError(f"direct Guitar PCM identity changed: {direct_pcm['pcmSha256']}")
        if roformer_sha != EXPECTED_ROFORMER_SHA256:
            raise RuntimeError(f"RoFormer WAV identity changed: {roformer_sha}")
        if roformer_pcm["pcmSha256"] != EXPECTED_ROFORMER_PCM_SHA256:
            raise RuntimeError(f"RoFormer PCM identity changed: {roformer_pcm['pcmSha256']}")
        if cascade_sha != EXPECTED_CASCADE_GUITAR_SHA256:
            raise RuntimeError(f"cascade Guitar WAV identity changed: {cascade_sha}")
        if cascade_pcm["pcmSha256"] != EXPECTED_CASCADE_PCM_SHA256:
            raise RuntimeError(f"cascade Guitar PCM identity changed: {cascade_pcm['pcmSha256']}")

        shift_lines = (
            shift_trace_path.read_text(encoding="utf-8").splitlines()
            if shift_trace_path.exists()
            else []
        )
        if shift_lines != [EXPECTED_SHIFT, EXPECTED_SHIFT]:
            raise RuntimeError(f"scheduler Demucs shift trace changed: {shift_lines}")
        if not runtime_trace_path.is_file():
            raise RuntimeError("scheduler Demucs runtime trace missing")
        runtime_trace = json.loads(runtime_trace_path.read_text(encoding="utf-8"))
        _assert_runtime_trace(runtime_trace)

        summary.update(
            {
                "completed": True,
                "terminalType": "Completed",
                "normalizedWavSha256": _sha256_file(normalized),
                "modelIdentity": model_identity,
                "directGuitarSha256": direct_sha,
                "directPcmInt16Sha256": direct_pcm["pcmSha256"],
                "roformerInstrumentalSha256": roformer_sha,
                "roformerInstrumentalPcmInt16Sha256": roformer_pcm["pcmSha256"],
                "cascadeGuitarSha256": cascade_sha,
                "cascadePcmInt16Sha256": cascade_pcm["pcmSha256"],
                "demucsShiftTrace": shift_lines,
                "directShiftTrace": [EXPECTED_SHIFT],
                "cascadeShiftTrace": [EXPECTED_SHIFT],
                "demucsRuntimeTrace": runtime_trace,
                "publicReturnKeys": sorted(result),
                "publicModels": result.get("models"),
                "publicSettings": settings,
                "outputNames": {key: path.name for key, path in paths.items()},
                "modalGpu": str(torch.cuda.get_device_name(0)),
                "schedulerStartMethod": "spawn",
                "runtimeSeconds": round(time.monotonic() - started, 3),
                "exactParityPassed": True,
                "publicContractPassed": True,
                "runtimeInvariantPassed": True,
            }
        )
    except BaseException as exc:
        summary.update(
            {
                "completed": False,
                "terminalType": type(exc).__name__,
                "message": str(exc)[:3000],
                "exactParityPassed": False,
            }
        )
    finally:
        temp.cleanup()

    cleanup_passed = not root.exists()
    summary["cleanupPassed"] = cleanup_passed
    summary["runtimeSeconds"] = round(time.monotonic() - started, 3)
    summary["allPassed"] = bool(
        summary.get("completed") is True
        and summary.get("exactParityPassed") is True
        and summary.get("publicContractPassed") is True
        and summary.get("runtimeInvariantPassed") is True
        and cleanup_passed
        and summary.get("referenceFree") is True
        and summary.get("referenceFacingInputs") == 0
        and summary.get("referenceScoreCalls") == 0
        and summary.get("qualityVerdictMade") is False
    )
    return summary
