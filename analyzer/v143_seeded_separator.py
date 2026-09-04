from __future__ import annotations

import os
import shutil
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from v143_production_separator import (
    BS_ROFORMER_MODEL,
    DEMUCS_6S_MODEL,
    normalize_input_audio,
    separate_demucs_guitar,
    separate_roformer_instrumental,
)


SEPARATOR_SEED = "143"
CUBLAS_WORKSPACE_CONFIG = ":4096:8"
DEMUCS_SINGLE_THREAD_ENV = {
    "CUDA_VISIBLE_DEVICES": "",
    "V143_DEMUCS_FIXED_SHIFT_RNG": "1",
    "V143_DEMUCS_DISABLE_MKLDNN": "1",
    "OMP_NUM_THREADS": "1",
    "OMP_DYNAMIC": "FALSE",
    "MKL_NUM_THREADS": "1",
    "MKL_DYNAMIC": "FALSE",
    "MKL_CBWR": "COMPATIBLE",
    "OPENBLAS_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "TBB_NUM_THREADS": "1",
    # Common baseline research execution path. ATen DEFAULT removes AVX2/AVX512
    # DispatchStub selection; oneDNN is explicitly disabled in the Demucs child
    # because baseline probes still diverged across AMD microarchitectures while
    # oneDNN remained enabled. oneMKL stays in cross-vendor CNR mode. Musical
    # model/settings/input are unchanged.
    "ATEN_CPU_CAPABILITY": "default",
    "ONEDNN_MAX_CPU_ISA": "SSE41",
    "DNNL_MAX_CPU_ISA": "SSE41",
}


def _stage(name: str, started: float) -> None:
    """Emit bounded aggregate timing only; never emit audio or transcription data."""
    print(
        f"V143_STAGE separator.{name} elapsed={time.monotonic() - started:.3f}",
        flush=True,
    )


def seeded_audio_separator_cli() -> list[str]:
    return [sys.executable, "-m", "v143_seeded_audio_separator_cli"]


@contextmanager
def _temporary_environment(updates: dict[str, str | None]) -> Iterator[None]:
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


def build_seeded_v143_stems(
    input_audio: Path | str,
    output_dir: Path | str,
) -> dict[str, Any]:
    """Run the frozen V143 separator graph through deterministic child boundaries.

    The musical graph is unchanged: Demucs6s Guitar, shifts=1, overlap=.10,
    segment=6, plus BS-RoFormer Instrumental -> Demucs6s. BS-RoFormer is already
    byte-exact across cold sessions. Demucs is CPU-only/single-thread, its
    intentional shift trick uses a private RNG seeded only by V143_SEPARATOR_SEED,
    and the research child uses ATen DEFAULT with oneDNN disabled plus oneMKL CNR
    COMPATIBLE to remove host-kernel variation as far as the supported libraries
    allow. Model weights and all musical separator parameters remain identical.

    No song/reference labels, human targets, or scorer values enter this path.
    """
    input_path = Path(input_audio)
    root = Path(output_dir)
    if not input_path.exists() or input_path.stat().st_size <= 0:
        raise FileNotFoundError(input_path)

    started = time.monotonic()
    _stage("start", started)

    root.mkdir(parents=True, exist_ok=True)
    cli = seeded_audio_separator_cli()
    work = root / "_work"

    _stage("input-normalize.start", started)
    normalized_input = normalize_input_audio(
        input_path,
        work / "normalized",
    )
    _stage("input-normalize.done", started)

    common_env = {
        "PYTHONHASHSEED": SEPARATOR_SEED,
        "V143_SEPARATOR_SEED": SEPARATOR_SEED,
        "CUBLAS_WORKSPACE_CONFIG": CUBLAS_WORKSPACE_CONFIG,
        "NVIDIA_TF32_OVERRIDE": "0",
    }

    with _temporary_environment(common_env):
        _stage("direct-demucs.start", started)
        with _temporary_environment(DEMUCS_SINGLE_THREAD_ENV):
            direct = separate_demucs_guitar(
                cli,
                normalized_input,
                work / "direct",
            )
        _stage("direct-demucs.done", started)

        _stage("roformer.start", started)
        with _temporary_environment({"CUDA_VISIBLE_DEVICES": None}):
            roformer = separate_roformer_instrumental(
                cli,
                normalized_input,
                work / "roformer",
            )
        _stage("roformer.done", started)

        _stage("cascade-demucs.start", started)
        with _temporary_environment(DEMUCS_SINGLE_THREAD_ENV):
            cascade = separate_demucs_guitar(
                cli,
                Path(roformer["path"]),
                work / "cascade",
            )
        _stage("cascade-demucs.done", started)

    direct_out = root / "direct-demucs6s-guitar.wav"
    roformer_out = root / "bsroformer-instrumental.wav"
    cascade_out = root / "bsroformer-demucs6s-guitar.wav"
    shutil.copy2(direct["path"], direct_out)
    shutil.copy2(roformer["path"], roformer_out)
    shutil.copy2(cascade["path"], cascade_out)

    if (
        not direct_out.exists()
        or direct_out.stat().st_size <= 0
        or not roformer_out.exists()
        or roformer_out.stat().st_size <= 0
        or not cascade_out.exists()
        or cascade_out.stat().st_size <= 0
    ):
        raise RuntimeError("Seeded V143 separator outputs were not created correctly")

    _stage("done", started)

    return {
        "directGuitar": str(direct_out),
        "roformerInstrumental": str(roformer_out),
        "cascadeGuitar": str(cascade_out),
        "models": {
            "demucs": DEMUCS_6S_MODEL,
            "bsRoformer": BS_ROFORMER_MODEL,
        },
        "settings": {
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
            "cublasWorkspaceConfig": CUBLAS_WORKSPACE_CONFIG,
            "tf32Disabled": True,
            "torchDeterministicAlgorithms": True,
        },
        "referenceFree": True,
        "diagnosticOnly": True,
    }


__all__ = [
    "SEPARATOR_SEED",
    "CUBLAS_WORKSPACE_CONFIG",
    "DEMUCS_SINGLE_THREAD_ENV",
    "seeded_audio_separator_cli",
    "build_seeded_v143_stems",
]
