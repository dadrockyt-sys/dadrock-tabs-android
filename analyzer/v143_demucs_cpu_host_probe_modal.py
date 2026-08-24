from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_ai_tab_gpu_worker import image as separator_image


APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
PROTECTED_PIPELINE_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"

MODULES = (
    "v143_ai_tab_gpu_worker",
    "v143_production_separator",
    "v143_seeded_separator",
    "v143_seeded_audio_separator_cli",
)

app = modal.App("dadrock-v143-demucs-cpu-host-probe")
image = separator_image.add_local_python_source(*MODULES)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _host_fingerprint() -> dict[str, Any]:
    import torch

    cpuinfo = Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="replace") if Path("/proc/cpuinfo").exists() else ""
    model_name = None
    flags = None
    for line in cpuinfo.splitlines():
        if model_name is None and line.lower().startswith("model name"):
            model_name = line.split(":", 1)[-1].strip()
        if flags is None and line.lower().startswith(("flags", "features")):
            flags = line.split(":", 1)[-1].strip()
        if model_name and flags:
            break
    lscpu = subprocess.run(["lscpu"], capture_output=True, text=True, check=False)
    affinity = sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else []
    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpuModelName": model_name,
        "cpuFlags": flags,
        "lscpu": (lscpu.stdout or lscpu.stderr or "")[:12000],
        "affinityCpuCount": len(affinity),
        "osCpuCount": os.cpu_count(),
        "torchVersion": str(torch.__version__),
        "torchCudaAvailable": bool(torch.cuda.is_available()),
        "torchConfig": torch.__config__.show(),
        "mkldnnAvailable": bool(torch.backends.mkldnn.is_available()),
        "mkldnnEnabled": bool(torch.backends.mkldnn.enabled),
    }


@app.function(image=image, cpu=1.0, timeout=1800, memory=8192)
def probe(source_audio: bytes, suffix: str = ".m4a") -> dict[str, Any]:
    """Run only the earliest failing direct-Demucs stage with zero GPU request."""
    import numpy as np
    import soundfile as sf

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

    with tempfile.TemporaryDirectory(prefix="v143-demucs-cpu-host-probe-") as temp_dir:
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
        demucs_env = dict(DEMUCS_SINGLE_THREAD_ENV)
        demucs_env["V143_DEMUCS_SHIFT_TRACE_PATH"] = str(shift_trace)
        demucs_env["V143_DEMUCS_RUNTIME_TRACE_PATH"] = str(runtime_trace)

        host = _host_fingerprint()
        with _temporary_environment(common_env):
            with _temporary_environment(demucs_env):
                direct = separate_demucs_guitar(
                    seeded_audio_separator_cli(),
                    normalized,
                    root / "direct",
                )

        direct_path = Path(str(direct["path"]))
        if not direct_path.exists() or direct_path.stat().st_size <= 0:
            raise RuntimeError("direct Demucs output missing")

        pcm, sample_rate = sf.read(str(direct_path), dtype="int16", always_2d=True)
        pcm_le = np.asarray(pcm, dtype="<i2", order="C")
        trace_lines = shift_trace.read_text(encoding="utf-8").splitlines() if shift_trace.exists() else []
        child_runtime = json.loads(runtime_trace.read_text(encoding="utf-8")) if runtime_trace.exists() else None

        return {
            "schemaVersion": 2,
            "gate": "v143-demucs-cpu-host-probe",
            "sourceSha256": _sha256_bytes(source_audio),
            "normalizedWavSha256": _sha256_file(normalized),
            "directGuitarSha256": _sha256_file(direct_path),
            "directPcmInt16Sha256": _sha256_bytes(pcm_le.tobytes(order="C")),
            "directBytes": direct_path.stat().st_size,
            "sampleRate": int(sample_rate),
            "pcmFrames": int(pcm_le.shape[0]),
            "pcmChannels": int(pcm_le.shape[1]),
            "demucsShiftTrace": trace_lines,
            "expectedSeed143FirstShift": 6026,
            "host": host,
            "childRuntime": child_runtime,
            "settings": {
                "demucsSingleStem": "Guitar",
                "demucsShifts": 1,
                "demucsOverlap": 0.10,
                "demucsSegmentSize": 6,
                "demucsExecutionDevice": "cpu",
                "demucsCpuThreads": 1,
                "modalGpuRequested": False,
                "deterministicSeed": 143,
                "atenCpuCapability": DEMUCS_SINGLE_THREAD_ENV.get("ATEN_CPU_CAPABILITY"),
                "mklCbwr": DEMUCS_SINGLE_THREAD_ENV.get("MKL_CBWR"),
                "mklDynamic": DEMUCS_SINGLE_THREAD_ENV.get("MKL_DYNAMIC"),
                "ompDynamic": DEMUCS_SINGLE_THREAD_ENV.get("OMP_DYNAMIC"),
                "oneDnnMaxCpuIsa": DEMUCS_SINGLE_THREAD_ENV.get("ONEDNN_MAX_CPU_ISA"),
                "dnnlMaxCpuIsa": DEMUCS_SINGLE_THREAD_ENV.get("DNNL_MAX_CPU_ISA"),
            },
            "invariants": {
                "approvedFixture": _sha256_bytes(source_audio) == APPROVED_AUDIO_SHA256,
                "referenceFree": True,
                "modalGpuRequested": False,
                "productionModified": False,
                "protectedPipelineModified": False,
                "childRuntimeTracePresent": child_runtime is not None,
            },
        }


@app.local_entrypoint(name="approved_audio")
def approved_audio(
    audio_path: str = "public/gomywayfullaitest.m4a",
    output_path: str = "debug/v143-contextual-prune/demucs-cpu-host-probe.json",
) -> None:
    source = Path(audio_path)
    data = source.read_bytes()
    digest = _sha256_bytes(data)
    if digest != APPROVED_AUDIO_SHA256:
        raise RuntimeError(f"approved fixture SHA changed: {digest}")
    result = probe.remote(data, source.suffix)
    inv = result.get("invariants") or {}
    if inv.get("approvedFixture") is not True or inv.get("referenceFree") is not True:
        raise RuntimeError(f"probe invariant failure: {inv}")
    if inv.get("modalGpuRequested") is not False or inv.get("productionModified") is not False:
        raise RuntimeError(f"probe safety failure: {inv}")
    if inv.get("childRuntimeTracePresent") is not True:
        raise RuntimeError("Demucs child runtime trace missing")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    print(f"WROTE={output}")


if __name__ == "__main__":
    pass
