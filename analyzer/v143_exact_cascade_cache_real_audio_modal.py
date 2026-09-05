from __future__ import annotations

import hashlib
import importlib.metadata
import io
import json
import os
import platform
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import modal

from v143_ai_tab_gpu_worker import image as separator_image


APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EXPECTED_NORMALIZED_SHA256 = "ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f"
EXPECTED_CASCADE_GUITAR_SHA256 = "546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41"
EXPECTED_SHIFT_TRACE = ["0,22050,6026"]
EXPECTED_DEMUCS_WEIGHT_FILENAME = "5c90dfd2-34c22ccb.th"
EXPECTED_DEMUCS_WEIGHT_SHA256 = "34c22ccb381c6f9fdbf324f04e1e2fe21aaaf293f5ded163a162697ff9a02ddd"
EXPECTED_DEMUCS_CONFIG_FILENAME = "htdemucs_6s.yaml"
EXPECTED_DEMUCS_CONFIG_SHA256 = "207405151270af8fd81c2373c25d27950916682ac91dca7884a11ce13dad6f58"

MODULES = (
    "v143_ai_tab_gpu_worker",
    "v143_production_separator",
    "v143_seeded_separator",
    "v143_seeded_audio_separator_cli",
    "v143_exact_stage_cache",
)

app = modal.App("dadrock-v143-exact-cascade-cache-real-audio")
image = separator_image.add_local_python_source(*MODULES)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "missing"


def _code_policy_version() -> str:
    import v143_production_separator
    import v143_seeded_audio_separator_cli
    import v143_seeded_separator

    digest = hashlib.sha256()
    for module in (
        v143_production_separator,
        v143_seeded_separator,
        v143_seeded_audio_separator_cli,
    ):
        module_path = Path(str(module.__file__))
        digest.update(module_path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(module_path.read_bytes())
        digest.update(b"\0")

    return (
        "v143-exact-cascade-policy-1"
        f";python={platform.python_version()}"
        f";audio-separator={_package_version('audio-separator')}"
        f";torch={_package_version('torch')}"
        f";numpy={_package_version('numpy')}"
        f";soundfile={_package_version('soundfile')}"
        f";code={digest.hexdigest()}"
    )


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


def _download_model(cli: list[str], model_filename: str, env: dict[str, str | None]) -> None:
    from v143_seeded_separator import _temporary_environment

    with _temporary_environment(env):
        run = subprocess.run(
            cli + ["--model_filename", model_filename, "--download_model_only"],
            check=False,
            text=True,
            capture_output=True,
        )
    if run.returncode != 0:
        raise RuntimeError(
            "model prefetch failed: "
            f"model={model_filename}, returnCode={run.returncode}, stderr={run.stderr[-2000:]}"
        )


def _prefetch_model_identity(cli: list[str]) -> dict[str, Any]:
    from v143_production_separator import BS_ROFORMER_MODEL, DEMUCS_6S_MODEL
    from v143_seeded_separator import (
        CUBLAS_WORKSPACE_CONFIG,
        DEMUCS_SINGLE_THREAD_ENV,
        SEPARATOR_SEED,
    )

    common_env = {
        "PYTHONHASHSEED": SEPARATOR_SEED,
        "V143_SEPARATOR_SEED": SEPARATOR_SEED,
        "CUBLAS_WORKSPACE_CONFIG": CUBLAS_WORKSPACE_CONFIG,
        "NVIDIA_TF32_OVERRIDE": "0",
    }
    roformer_env = dict(common_env)
    roformer_env["CUDA_VISIBLE_DEVICES"] = None
    demucs_env = dict(common_env)
    demucs_env.update(DEMUCS_SINGLE_THREAD_ENV)

    _download_model(cli, BS_ROFORMER_MODEL, roformer_env)
    _download_model(cli, DEMUCS_6S_MODEL, demucs_env)

    model_dir = _model_dir()
    roformer_path = model_dir / BS_ROFORMER_MODEL
    demucs_weight = model_dir / EXPECTED_DEMUCS_WEIGHT_FILENAME
    demucs_config = model_dir / EXPECTED_DEMUCS_CONFIG_FILENAME
    for path in (roformer_path, demucs_weight, demucs_config):
        if not path.is_file() or path.stat().st_size <= 0:
            raise RuntimeError(f"expected separator model artifact missing: {path}")

    identity = {
        "roformerModelFilename": BS_ROFORMER_MODEL,
        "roformerWeightSha256": _sha256_file(roformer_path),
        "roformerWeightBytes": int(roformer_path.stat().st_size),
        "demucsConfigFilename": EXPECTED_DEMUCS_CONFIG_FILENAME,
        "demucsConfigSha256": _sha256_file(demucs_config),
        "demucsConfigBytes": int(demucs_config.stat().st_size),
        "demucsWeightFilename": EXPECTED_DEMUCS_WEIGHT_FILENAME,
        "demucsWeightSha256": _sha256_file(demucs_weight),
        "demucsWeightBytes": int(demucs_weight.stat().st_size),
    }
    if identity["demucsWeightSha256"] != EXPECTED_DEMUCS_WEIGHT_SHA256:
        raise RuntimeError(f"Demucs weight identity changed: {identity}")
    if identity["demucsConfigSha256"] != EXPECTED_DEMUCS_CONFIG_SHA256:
        raise RuntimeError(f"Demucs config identity changed: {identity}")
    return identity


def _gpu_runtime_identity() -> dict[str, Any]:
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("cascade probe requires the frozen RoFormer CUDA-capable execution path")
    capability = torch.cuda.get_device_capability(0)
    return {
        "torchVersion": str(torch.__version__),
        "torchCudaVersion": None if torch.version.cuda is None else str(torch.version.cuda),
        "cudaDeviceName": str(torch.cuda.get_device_name(0)),
        "cudaComputeCapability": [int(capability[0]), int(capability[1])],
        "cudaDeviceCount": int(torch.cuda.device_count()),
    }


def _composite_weight_sha(model_identity: dict[str, Any]) -> str:
    material = {
        "roformer": model_identity["roformerWeightSha256"],
        "demucs": model_identity["demucsWeightSha256"],
    }
    return _sha256_bytes(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def _fingerprint(
    normalized_sha256: str,
    model_identity: dict[str, Any],
    runtime_identity: dict[str, Any],
    sample_rate: int,
    channels: int,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "normalized_source_sha256": normalized_sha256,
        "separator_model": "bsroformer-instrumental->htdemucs6s-guitar",
        "separator_weights_sha256": _composite_weight_sha(model_identity),
        "demucs_parameters": {
            "roformer": {
                "model_filename": model_identity["roformerModelFilename"],
                "weight_sha256": model_identity["roformerWeightSha256"],
                "single_stem": "Instrumental",
                "batch_size": 1,
                "execution_device": "cuda-auto",
            },
            "demucs": {
                "config_filename": model_identity["demucsConfigFilename"],
                "config_sha256": model_identity["demucsConfigSha256"],
                "weight_sha256": model_identity["demucsWeightSha256"],
                "single_stem": "Guitar",
                "shifts": 1,
                "overlap": 0.10,
                "segment_size": 6,
                "use_soundfile": True,
                "execution_device": "cpu",
            },
        },
        "shift_policy": {
            "mode": "private_rng_exact",
            "seed": 143,
            "expected_cascade_trace": list(EXPECTED_SHIFT_TRACE),
        },
        "audio_format": {
            "sample_rate_hz": int(sample_rate),
            "channels": int(channels),
        },
        "runtime_controls": {
            "torch_intraop_threads": 1,
            "torch_interop_threads": 1,
            "omp_num_threads": 1,
            "mkl_num_threads": 1,
            "onednn_enabled": False,
            "roformer_torch_version": runtime_identity["torchVersion"],
            "roformer_cuda_version": runtime_identity["torchCudaVersion"],
            "roformer_cuda_device": runtime_identity["cudaDeviceName"],
            "roformer_cuda_compute_capability": runtime_identity["cudaComputeCapability"],
        },
        "code_policy_version": _code_policy_version(),
    }


@app.function(image=image, gpu="L4", timeout=1800, memory=8192)
def probe(source_audio: bytes, suffix: str = ".m4a") -> dict[str, Any]:
    import soundfile as sf

    from v143_exact_stage_cache import ExactStageCache, cache_key
    from v143_production_separator import (
        normalize_input_audio,
        separate_demucs_guitar,
        separate_roformer_instrumental,
    )
    from v143_seeded_separator import (
        CUBLAS_WORKSPACE_CONFIG,
        DEMUCS_SINGLE_THREAD_ENV,
        SEPARATOR_SEED,
        _temporary_environment,
        seeded_audio_separator_cli,
    )

    source_sha = _sha256_bytes(source_audio)
    if source_sha != APPROVED_AUDIO_SHA256:
        raise RuntimeError(f"approved fixture SHA changed: {source_sha}")

    temp = tempfile.TemporaryDirectory(prefix="v143-exact-cascade-cache-real-audio-")
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
            raise RuntimeError(
                f"normalized format changed: sampleRate={info.samplerate}, channels={info.channels}"
            )

        cli = seeded_audio_separator_cli()
        model_identity = _prefetch_model_identity(cli)
        runtime_identity = _gpu_runtime_identity()
        fingerprint = _fingerprint(
            normalized_sha,
            model_identity,
            runtime_identity,
            int(info.samplerate),
            int(info.channels),
        )

        cache = ExactStageCache(root / "cache")
        key = cache_key(fingerprint)
        initial_miss = cache.lookup(fingerprint) is None
        if not initial_miss:
            raise RuntimeError("ephemeral cascade cache unexpectedly warm")

        compute_calls = {"count": 0}
        roformer_calls = {"count": 0}
        cascade_demucs_calls = {"count": 0}
        exact_details: dict[str, Any] = {}

        def exact_compute() -> dict[str, bytes]:
            compute_calls["count"] += 1
            if compute_calls["count"] != 1:
                raise RuntimeError("cascade exact compute invoked more than once")

            common_env = {
                "PYTHONHASHSEED": SEPARATOR_SEED,
                "V143_SEPARATOR_SEED": SEPARATOR_SEED,
                "CUBLAS_WORKSPACE_CONFIG": CUBLAS_WORKSPACE_CONFIG,
                "NVIDIA_TF32_OVERRIDE": "0",
            }

            roformer_trace = root / "roformer-runtime-trace.json"
            roformer_env = {
                "CUDA_VISIBLE_DEVICES": None,
                "V143_DEMUCS_RUNTIME_TRACE_PATH": str(roformer_trace),
            }
            with _temporary_environment(common_env):
                with _temporary_environment(roformer_env):
                    roformer_calls["count"] += 1
                    roformer = separate_roformer_instrumental(
                        seeded_audio_separator_cli(),
                        normalized,
                        root / "roformer",
                    )

                roformer_path = Path(str(roformer["path"]))
                roformer_bytes = roformer_path.read_bytes()
                roformer_pcm = _decode_pcm_identity(roformer_bytes)

                shift_trace = root / "cascade-demucs-shift-trace.txt"
                demucs_runtime_trace = root / "cascade-demucs-runtime-trace.json"
                demucs_env = dict(DEMUCS_SINGLE_THREAD_ENV)
                demucs_env["V143_DEMUCS_SHIFT_TRACE_PATH"] = str(shift_trace)
                demucs_env["V143_DEMUCS_RUNTIME_TRACE_PATH"] = str(demucs_runtime_trace)
                with _temporary_environment(demucs_env):
                    cascade_demucs_calls["count"] += 1
                    cascade = separate_demucs_guitar(
                        seeded_audio_separator_cli(),
                        roformer_path,
                        root / "cascade",
                    )

            cascade_path = Path(str(cascade["path"]))
            cascade_bytes = cascade_path.read_bytes()
            cascade_sha = _sha256_bytes(cascade_bytes)
            cascade_pcm = _decode_pcm_identity(cascade_bytes)
            trace_lines = (
                shift_trace.read_text(encoding="utf-8").splitlines()
                if shift_trace.exists()
                else []
            )
            demucs_runtime = (
                json.loads(demucs_runtime_trace.read_text(encoding="utf-8"))
                if demucs_runtime_trace.exists()
                else None
            )
            roformer_runtime = (
                json.loads(roformer_trace.read_text(encoding="utf-8"))
                if roformer_trace.exists()
                else None
            )

            if cascade_sha != EXPECTED_CASCADE_GUITAR_SHA256:
                raise RuntimeError(f"cascade Guitar anchor changed: {cascade_sha}")
            if trace_lines != EXPECTED_SHIFT_TRACE:
                raise RuntimeError(f"cascade exact shift trace changed: {trace_lines}")
            if int(cascade_pcm["sampleRate"]) != 44100 or int(cascade_pcm["pcmChannels"]) != 2:
                raise RuntimeError(f"cascade Guitar format changed: {cascade_pcm}")
            if not isinstance(demucs_runtime, dict):
                raise RuntimeError("cascade Demucs runtime trace missing")
            denv = demucs_runtime.get("environment") or {}
            if (
                demucs_runtime.get("mkldnnEnabled") is not False
                or int(demucs_runtime.get("torchNumThreads", 0)) != 1
                or int(demucs_runtime.get("torchNumInteropThreads", 0)) != 1
                or str(demucs_runtime.get("torchCpuCapability") or "").upper() != "DEFAULT"
                or denv.get("V143_DEMUCS_DISABLE_MKLDNN") != "1"
                or denv.get("OMP_NUM_THREADS") != "1"
                or denv.get("MKL_NUM_THREADS") != "1"
                or denv.get("MKL_CBWR") != "COMPATIBLE"
            ):
                raise RuntimeError(f"cascade exact CPU runtime invariant changed: {demucs_runtime}")

            exact_details.update(
                {
                    "roformerElapsedSeconds": roformer.get("elapsedSeconds"),
                    "cascadeDemucsElapsedSeconds": cascade.get("elapsedSeconds"),
                    "roformerInstrumentalSha256": _sha256_bytes(roformer_bytes),
                    "roformerInstrumentalPcmInt16Sha256": roformer_pcm["pcmSha256"],
                    "roformerInstrumentalBytes": len(roformer_bytes),
                    "roformerSampleRate": roformer_pcm["sampleRate"],
                    "roformerPcmFrames": roformer_pcm["pcmFrames"],
                    "roformerPcmChannels": roformer_pcm["pcmChannels"],
                    "cascadeGuitarSha256": cascade_sha,
                    "cascadePcmInt16Sha256": cascade_pcm["pcmSha256"],
                    "cascadeBytes": len(cascade_bytes),
                    "cascadeSampleRate": cascade_pcm["sampleRate"],
                    "cascadePcmFrames": cascade_pcm["pcmFrames"],
                    "cascadePcmChannels": cascade_pcm["pcmChannels"],
                    "cascadeDemucsShiftTrace": trace_lines,
                    "roformerChildRuntime": roformer_runtime,
                    "cascadeDemucsChildRuntime": demucs_runtime,
                }
            )
            return {"bsroformer-demucs6s-guitar.wav": cascade_bytes}

        miss_started = time.monotonic()
        first = cache.resolve(fingerprint, exact_compute)
        miss_wall = time.monotonic() - miss_started
        first_bytes = first.payloads.get("bsroformer-demucs6s-guitar.wav", b"")
        first_pcm = _decode_pcm_identity(first_bytes)
        miss_passed = bool(
            first.cache_hit is False
            and first.cache_write_succeeded is True
            and compute_calls["count"] == 1
            and roformer_calls["count"] == 1
            and cascade_demucs_calls["count"] == 1
            and _sha256_bytes(first_bytes) == EXPECTED_CASCADE_GUITAR_SHA256
        )
        if not miss_passed:
            raise RuntimeError("cascade cold miss/populate gate failed")

        hit_started = time.monotonic()
        second = cache.resolve(fingerprint, exact_compute)
        hit_wall = time.monotonic() - hit_started
        second_bytes = second.payloads.get("bsroformer-demucs6s-guitar.wav", b"")
        second_pcm = _decode_pcm_identity(second_bytes)
        hit_passed = bool(
            second.cache_hit is True
            and second.cache_write_succeeded is None
            and compute_calls["count"] == 1
            and roformer_calls["count"] == 1
            and cascade_demucs_calls["count"] == 1
            and second_bytes == first_bytes
            and _sha256_bytes(second_bytes) == EXPECTED_CASCADE_GUITAR_SHA256
            and second_pcm["pcmSha256"] == first_pcm["pcmSha256"]
        )
        if not hit_passed:
            raise RuntimeError("cascade warm-cache replay gate failed")

        mismatch = json.loads(json.dumps(fingerprint))
        mismatch["demucs_parameters"]["roformer"]["batch_size"] = 2
        mismatch_miss = cache.lookup(mismatch) is None
        mismatch_key_changed = cache_key(mismatch) != key
        if not mismatch_miss or not mismatch_key_changed:
            raise RuntimeError("cascade fingerprint mismatch did not fail closed")

        payload_path = cache.entry_path(fingerprint) / "bsroformer-demucs6s-guitar.wav"
        payload_path.write_bytes(b"intentional-v143-cascade-cache-corruption")
        corruption_lookup_rejected = cache.lookup(fingerprint) is None
        corruption_fallback_calls = {"count": 0}

        class CorruptCacheFallbackReached(RuntimeError):
            pass

        def corruption_fallback() -> dict[str, bytes]:
            corruption_fallback_calls["count"] += 1
            raise CorruptCacheFallbackReached("corrupt cascade cache reached exact-compute boundary")

        corruption_fallback_reached = False
        try:
            cache.resolve(fingerprint, corruption_fallback)
        except CorruptCacheFallbackReached:
            corruption_fallback_reached = True

        corruption_passed = bool(
            corruption_lookup_rejected
            and corruption_fallback_reached
            and corruption_fallback_calls["count"] == 1
            and compute_calls["count"] == 1
        )
        if not corruption_passed:
            raise RuntimeError("corrupt cascade cache did not fail closed")

        summary = {
            "schemaVersion": 1,
            "gate": "v143-exact-cascade-stage-cache-real-audio",
            "sourceSha256": source_sha,
            "normalizedWavSha256": normalized_sha,
            "historicalCurrentRegimeCascadeAnchorSha256": EXPECTED_CASCADE_GUITAR_SHA256,
            "cacheKey": key,
            "fingerprint": fingerprint,
            "modelIdentity": model_identity,
            "roformerParentRuntime": runtime_identity,
            "initialMissPassed": initial_miss,
            "missPopulatePassed": miss_passed,
            "warmHitPassed": hit_passed,
            "fingerprintMismatchMissPassed": mismatch_miss,
            "fingerprintMismatchChangesKeyPassed": mismatch_key_changed,
            "corruptionLookupRejectedPassed": corruption_lookup_rejected,
            "corruptionFallbackReachedPassed": corruption_fallback_reached,
            "computeCalls": compute_calls["count"],
            "roformerComputeCalls": roformer_calls["count"],
            "cascadeDemucsComputeCalls": cascade_demucs_calls["count"],
            "directDemucsComputeCalls": 0,
            "corruptionFallbackCalls": corruption_fallback_calls["count"],
            "missWallSeconds": round(miss_wall, 3),
            "hitWallSeconds": round(hit_wall, 6),
            "hitSpeedup": round(miss_wall / hit_wall, 3) if hit_wall > 0 else None,
            **exact_details,
            "warmHitCascadeGuitarSha256": _sha256_bytes(second_bytes),
            "warmHitCascadePcmInt16Sha256": second_pcm["pcmSha256"],
            "referenceFree": True,
            "referenceFacingAccuracyScored": False,
            "referenceScoreCalls": 0,
            "qualityVerdictMade": False,
            "gpuPerformanceComparisonPerformed": False,
            "productionWorkerChanged": False,
            "productionBridgeChanged": False,
            "vercelChanged": False,
            "mainMergePerformed": False,
        }
    finally:
        temp.cleanup()

    if root.exists():
        raise RuntimeError(f"ephemeral cascade diagnostic cleanup failed: {root}")

    summary["cleanupPassed"] = True
    summary["rawAudioRetained"] = False
    summary["stemBytesRetained"] = False
    summary["allPassed"] = bool(
        summary.get("initialMissPassed")
        and summary.get("missPopulatePassed")
        and summary.get("warmHitPassed")
        and summary.get("fingerprintMismatchMissPassed")
        and summary.get("fingerprintMismatchChangesKeyPassed")
        and summary.get("corruptionLookupRejectedPassed")
        and summary.get("corruptionFallbackReachedPassed")
        and summary.get("computeCalls") == 1
        and summary.get("roformerComputeCalls") == 1
        and summary.get("cascadeDemucsComputeCalls") == 1
        and summary.get("directDemucsComputeCalls") == 0
        and summary.get("cleanupPassed")
    )
    if not summary["allPassed"]:
        raise RuntimeError(f"cascade exact-cache gate failed: {summary}")
    return summary


if __name__ == "__main__":
    pass
