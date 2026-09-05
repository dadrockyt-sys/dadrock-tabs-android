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
EXPECTED_GUITAR_SHA256 = "0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c"
EXPECTED_PCM_SHA256 = "2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed"
EXPECTED_SHIFT_TRACE = ["0,22050,6026"]
EXPECTED_DEMUCS_WEIGHT_FILENAME = "5c90dfd2-34c22ccb.th"
EXPECTED_DEMUCS_CONFIG_FILENAME = "htdemucs_6s.yaml"

MODULES = (
    "v143_ai_tab_gpu_worker",
    "v143_production_separator",
    "v143_seeded_separator",
    "v143_seeded_audio_separator_cli",
    "v143_exact_stage_cache",
)

app = modal.App("dadrock-v143-exact-cache-real-audio")
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
        "v143-exact-cpu-policy-1"
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


def _prefetch_exact_demucs_model(cli: list[str]) -> dict[str, Any]:
    from v143_production_separator import DEMUCS_6S_MODEL
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
        with _temporary_environment(DEMUCS_SINGLE_THREAD_ENV):
            run = subprocess.run(
                cli
                + [
                    "--model_filename",
                    DEMUCS_6S_MODEL,
                    "--download_model_only",
                ],
                check=False,
                text=True,
                capture_output=True,
            )

    if run.returncode != 0:
        raise RuntimeError(
            "exact Demucs model prefetch failed: "
            f"returnCode={run.returncode}, stderr={run.stderr[-2000:]}"
        )

    model_dir = _model_dir()
    weight_path = model_dir / EXPECTED_DEMUCS_WEIGHT_FILENAME
    config_path = model_dir / EXPECTED_DEMUCS_CONFIG_FILENAME
    if not weight_path.is_file() or weight_path.stat().st_size <= 0:
        raise RuntimeError(f"expected Demucs weight missing: {weight_path}")
    if not config_path.is_file() or config_path.stat().st_size <= 0:
        raise RuntimeError(f"expected Demucs config missing: {config_path}")

    return {
        "weightSha256": _sha256_file(weight_path),
        "weightBytes": int(weight_path.stat().st_size),
        "configSha256": _sha256_file(config_path),
        "configBytes": int(config_path.stat().st_size),
    }


def _fingerprint(
    normalized_sha256: str,
    model_identity: dict[str, Any],
    sample_rate: int,
    channels: int,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "normalized_source_sha256": normalized_sha256,
        "separator_model": (
            f"{EXPECTED_DEMUCS_CONFIG_FILENAME}@sha256:{model_identity['configSha256']}"
        ),
        "separator_weights_sha256": model_identity["weightSha256"],
        "demucs_parameters": {
            "single_stem": "Guitar",
            "shifts": 1,
            "overlap": 0.10,
            "segment_size": 6,
            "use_soundfile": True,
            "execution_device": "cpu",
        },
        "shift_policy": {
            "mode": "private_rng_exact",
            "seed": 143,
            "expected_trace": list(EXPECTED_SHIFT_TRACE),
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
        },
        "code_policy_version": _code_policy_version(),
    }


@app.function(image=image, cpu=1.0, timeout=1800, memory=8192)
def probe(source_audio: bytes, suffix: str = ".m4a") -> dict[str, Any]:
    import soundfile as sf

    from v143_exact_stage_cache import ExactStageCache, cache_key
    from v143_production_separator import normalize_input_audio, separate_demucs_guitar
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

    temp = tempfile.TemporaryDirectory(prefix="v143-exact-cache-real-audio-")
    root = Path(temp.name)
    summary: dict[str, Any] = {}

    try:
        source = root / f"source{suffix if suffix.startswith('.') else '.audio'}"
        source.write_bytes(source_audio)
        normalized = normalize_input_audio(source, root / "normalized")
        normalized_sha = _sha256_file(normalized)
        if normalized_sha != EXPECTED_NORMALIZED_SHA256:
            raise RuntimeError(f"normalized exact anchor changed: {normalized_sha}")

        normalized_info = sf.info(str(normalized))
        if int(normalized_info.samplerate) != 44100 or int(normalized_info.channels) != 2:
            raise RuntimeError(
                "normalized audio format changed: "
                f"sampleRate={normalized_info.samplerate}, channels={normalized_info.channels}"
            )

        cli = seeded_audio_separator_cli()
        model_identity = _prefetch_exact_demucs_model(cli)
        fingerprint = _fingerprint(
            normalized_sha,
            model_identity,
            int(normalized_info.samplerate),
            int(normalized_info.channels),
        )

        cache = ExactStageCache(root / "cache")
        key = cache_key(fingerprint)
        initial_miss = cache.lookup(fingerprint) is None
        if not initial_miss:
            raise RuntimeError("ephemeral exact cache was unexpectedly warm")

        separator_compute_calls = {"count": 0}
        exact_details: dict[str, Any] = {}

        def exact_compute() -> dict[str, bytes]:
            separator_compute_calls["count"] += 1
            if separator_compute_calls["count"] != 1:
                raise RuntimeError("exact separator compute invoked more than once")

            shift_trace = root / "demucs-shift-trace.txt"
            runtime_trace = root / "demucs-runtime-trace.json"
            common_env = {
                "PYTHONHASHSEED": SEPARATOR_SEED,
                "V143_SEPARATOR_SEED": SEPARATOR_SEED,
                "CUBLAS_WORKSPACE_CONFIG": CUBLAS_WORKSPACE_CONFIG,
                "NVIDIA_TF32_OVERRIDE": "0",
            }
            demucs_env = dict(DEMUCS_SINGLE_THREAD_ENV)
            demucs_env["V143_DEMUCS_SHIFT_TRACE_PATH"] = str(shift_trace)
            demucs_env["V143_DEMUCS_RUNTIME_TRACE_PATH"] = str(runtime_trace)

            with _temporary_environment(common_env):
                with _temporary_environment(demucs_env):
                    direct = separate_demucs_guitar(
                        seeded_audio_separator_cli(),
                        normalized,
                        root / "direct",
                    )

            direct_path = Path(str(direct["path"]))
            guitar_bytes = direct_path.read_bytes()
            guitar_sha = _sha256_bytes(guitar_bytes)
            pcm = _decode_pcm_identity(guitar_bytes)
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

            if guitar_sha != EXPECTED_GUITAR_SHA256:
                raise RuntimeError(f"exact Guitar anchor changed: {guitar_sha}")
            if pcm["pcmSha256"] != EXPECTED_PCM_SHA256:
                raise RuntimeError(f"exact PCM anchor changed: {pcm['pcmSha256']}")
            if trace_lines != EXPECTED_SHIFT_TRACE:
                raise RuntimeError(f"exact shift trace changed: {trace_lines}")
            if int(pcm["sampleRate"]) != 44100 or int(pcm["pcmChannels"]) != 2:
                raise RuntimeError(f"exact Guitar format changed: {pcm}")
            if not isinstance(child_runtime, dict):
                raise RuntimeError("Demucs child runtime trace missing")
            runtime_env = child_runtime.get("environment") or {}
            if (
                child_runtime.get("mkldnnEnabled") is not False
                or int(child_runtime.get("torchNumThreads", 0)) != 1
                or int(child_runtime.get("torchNumInteropThreads", 0)) != 1
                or str(child_runtime.get("torchCpuCapability") or "").upper() != "DEFAULT"
                or runtime_env.get("V143_DEMUCS_DISABLE_MKLDNN") != "1"
                or runtime_env.get("OMP_NUM_THREADS") != "1"
                or runtime_env.get("MKL_NUM_THREADS") != "1"
                or runtime_env.get("MKL_CBWR") != "COMPATIBLE"
            ):
                raise RuntimeError(f"exact CPU runtime invariant changed: {child_runtime}")

            exact_details.update(
                {
                    "separatorElapsedSeconds": direct.get("elapsedSeconds"),
                    "directBytes": len(guitar_bytes),
                    "directGuitarSha256": guitar_sha,
                    "directPcmInt16Sha256": pcm["pcmSha256"],
                    "sampleRate": pcm["sampleRate"],
                    "pcmFrames": pcm["pcmFrames"],
                    "pcmChannels": pcm["pcmChannels"],
                    "demucsShiftTrace": trace_lines,
                    "childRuntime": child_runtime,
                }
            )
            return {"direct-demucs6s-guitar.wav": guitar_bytes}

        miss_started = time.monotonic()
        first = cache.resolve(fingerprint, exact_compute)
        miss_wall = time.monotonic() - miss_started
        first_bytes = first.payloads.get("direct-demucs6s-guitar.wav", b"")
        first_pcm = _decode_pcm_identity(first_bytes)

        miss_passed = bool(
            initial_miss
            and first.cache_hit is False
            and first.cache_write_succeeded is True
            and separator_compute_calls["count"] == 1
            and _sha256_bytes(first_bytes) == EXPECTED_GUITAR_SHA256
            and first_pcm["pcmSha256"] == EXPECTED_PCM_SHA256
        )
        if not miss_passed:
            raise RuntimeError("real-audio miss/populate gate failed")

        hit_started = time.monotonic()
        second = cache.resolve(fingerprint, exact_compute)
        hit_wall = time.monotonic() - hit_started
        second_bytes = second.payloads.get("direct-demucs6s-guitar.wav", b"")
        second_pcm = _decode_pcm_identity(second_bytes)

        hit_passed = bool(
            second.cache_hit is True
            and second.cache_write_succeeded is None
            and separator_compute_calls["count"] == 1
            and second_bytes == first_bytes
            and _sha256_bytes(second_bytes) == EXPECTED_GUITAR_SHA256
            and second_pcm["pcmSha256"] == EXPECTED_PCM_SHA256
        )
        if not hit_passed:
            raise RuntimeError("real-audio warm-cache replay gate failed")

        mismatch = json.loads(json.dumps(fingerprint))
        mismatch["runtime_controls"]["torch_intraop_threads"] = 2
        mismatch_miss_passed = cache.lookup(mismatch) is None
        mismatch_key_changed = cache_key(mismatch) != key
        if not mismatch_miss_passed or not mismatch_key_changed:
            raise RuntimeError("fingerprint mismatch did not fail closed")

        payload_path = cache.entry_path(fingerprint) / "direct-demucs6s-guitar.wav"
        payload_path.write_bytes(b"intentional-v143-cache-corruption")
        corruption_lookup_rejected = cache.lookup(fingerprint) is None

        corruption_fallback_calls = {"count": 0}

        class CorruptCacheFallbackReached(RuntimeError):
            pass

        def corruption_fallback() -> dict[str, bytes]:
            corruption_fallback_calls["count"] += 1
            raise CorruptCacheFallbackReached("corrupt cache reached exact-compute boundary")

        corruption_fallback_reached = False
        try:
            cache.resolve(fingerprint, corruption_fallback)
        except CorruptCacheFallbackReached:
            corruption_fallback_reached = True

        corruption_passed = bool(
            corruption_lookup_rejected
            and corruption_fallback_reached
            and corruption_fallback_calls["count"] == 1
            and separator_compute_calls["count"] == 1
        )
        if not corruption_passed:
            raise RuntimeError("corrupt cache did not fail closed")

        summary = {
            "schemaVersion": 1,
            "gate": "v143-exact-stage-cache-real-audio",
            "sourceSha256": source_sha,
            "normalizedWavSha256": normalized_sha,
            "cacheKey": key,
            "fingerprint": fingerprint,
            "modelIdentity": {
                "weightFilename": EXPECTED_DEMUCS_WEIGHT_FILENAME,
                "weightSha256": model_identity["weightSha256"],
                "weightBytes": model_identity["weightBytes"],
                "configFilename": EXPECTED_DEMUCS_CONFIG_FILENAME,
                "configSha256": model_identity["configSha256"],
                "configBytes": model_identity["configBytes"],
            },
            "initialMissPassed": initial_miss,
            "missPopulatePassed": miss_passed,
            "warmHitPassed": hit_passed,
            "fingerprintMismatchMissPassed": mismatch_miss_passed,
            "fingerprintMismatchChangesKeyPassed": mismatch_key_changed,
            "corruptionLookupRejectedPassed": corruption_lookup_rejected,
            "corruptionFallbackReachedPassed": corruption_fallback_reached,
            "separatorComputeCalls": separator_compute_calls["count"],
            "corruptionFallbackCalls": corruption_fallback_calls["count"],
            "missWallSeconds": round(miss_wall, 3),
            "hitWallSeconds": round(hit_wall, 6),
            "hitSpeedup": round(miss_wall / hit_wall, 3) if hit_wall > 0 else None,
            **exact_details,
            "warmHitGuitarSha256": _sha256_bytes(second_bytes),
            "warmHitPcmInt16Sha256": second_pcm["pcmSha256"],
            "referenceFree": True,
            "referenceFacingAccuracyScored": False,
            "referenceScoreCalls": 0,
            "qualityVerdictMade": False,
            "productionWorkerChanged": False,
            "productionBridgeChanged": False,
            "vercelChanged": False,
            "mainMergePerformed": False,
        }
    finally:
        temp.cleanup()

    cleanup_passed = not root.exists()
    if not cleanup_passed:
        raise RuntimeError(f"ephemeral diagnostic cleanup failed: {root}")

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
        and summary.get("separatorComputeCalls") == 1
        and summary.get("cleanupPassed")
    )
    if not summary["allPassed"]:
        raise RuntimeError(f"real-audio exact-cache gate failed: {summary}")
    return summary


if __name__ == "__main__":
    pass
