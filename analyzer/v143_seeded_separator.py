from __future__ import annotations

import multiprocessing
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
DEMUCS_CHILD_TIMEOUT_SECONDS = 1200
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


def _run_demucs_child(
    input_audio: str,
    output_dir: str,
    result_connection: Any,
) -> None:
    """Run one exact seeded Demucs invocation in an isolated spawned process."""
    payload: dict[str, Any]
    try:
        result = separate_demucs_guitar(
            seeded_audio_separator_cli(),
            Path(input_audio),
            Path(output_dir),
        )
        output = Path(str(result["path"]))
        if not output.is_file() or output.stat().st_size <= 0:
            raise RuntimeError(f"seeded Demucs child output missing: {output}")
        payload = {
            "completed": True,
            "path": str(output),
            "model": result.get("model"),
            "elapsedSeconds": result.get("elapsedSeconds"),
        }
    except BaseException as exc:
        payload = {
            "completed": False,
            "terminalType": type(exc).__name__,
            "message": str(exc)[:2000],
        }

    try:
        result_connection.send(payload)
    finally:
        result_connection.close()


def _terminate_and_join(process: multiprocessing.Process | None) -> None:
    if process is None:
        return
    try:
        if process.is_alive():
            process.terminate()
    except (AssertionError, ValueError):
        pass
    try:
        process.join(timeout=10)
    except (AssertionError, ValueError):
        pass


def _close_connection(connection: Any | None) -> None:
    if connection is None:
        return
    try:
        connection.close()
    except (OSError, ValueError):
        pass


def _join_demucs_child(
    process: multiprocessing.Process,
    result_connection: Any,
    label: str,
) -> dict[str, Any]:
    process.join(timeout=DEMUCS_CHILD_TIMEOUT_SECONDS)
    if process.is_alive():
        raise RuntimeError(f"{label} exact Demucs child exceeded runtime deadline")
    if process.exitcode != 0:
        raise RuntimeError(f"{label} exact Demucs child exitCode={process.exitcode}")
    if not result_connection.poll(1.0):
        raise RuntimeError(f"{label} exact Demucs child result missing")

    payload = result_connection.recv()
    if not isinstance(payload, dict) or payload.get("completed") is not True:
        raise RuntimeError(f"{label} exact Demucs child failed: {payload}")

    output = Path(str(payload.get("path") or ""))
    if not output.is_file() or output.stat().st_size <= 0:
        raise RuntimeError(f"{label} exact Demucs child output missing: {output}")
    if payload.get("model") != DEMUCS_6S_MODEL:
        raise RuntimeError(
            f"{label} exact Demucs child model changed: {payload.get('model')}"
        )

    return {
        "path": output,
        "model": payload.get("model"),
        "elapsedSeconds": payload.get("elapsedSeconds"),
    }


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

    ctx = multiprocessing.get_context("spawn")
    direct_process: multiprocessing.Process | None = None
    cascade_process: multiprocessing.Process | None = None
    direct_receive: Any | None = None
    direct_send: Any | None = None
    cascade_receive: Any | None = None
    cascade_send: Any | None = None

    try:
        with _temporary_environment(common_env):
            direct_receive, direct_send = ctx.Pipe(duplex=False)
            direct_process = ctx.Process(
                target=_run_demucs_child,
                args=(
                    str(normalized_input),
                    str(work / "direct"),
                    direct_send,
                ),
                name="v143-direct-exact-demucs",
            )

            _stage("direct-demucs.start", started)
            with _temporary_environment(DEMUCS_SINGLE_THREAD_ENV):
                direct_process.start()
            _close_connection(direct_send)
            direct_send = None

            _stage("roformer.start", started)
            with _temporary_environment({"CUDA_VISIBLE_DEVICES": None}):
                roformer = separate_roformer_instrumental(
                    seeded_audio_separator_cli(),
                    normalized_input,
                    work / "roformer",
                )
            _stage("roformer.done", started)

            cascade_receive, cascade_send = ctx.Pipe(duplex=False)
            cascade_process = ctx.Process(
                target=_run_demucs_child,
                args=(
                    str(Path(roformer["path"])),
                    str(work / "cascade"),
                    cascade_send,
                ),
                name="v143-cascade-exact-demucs",
            )

            _stage("cascade-demucs.start", started)
            with _temporary_environment(DEMUCS_SINGLE_THREAD_ENV):
                cascade_process.start()
            _close_connection(cascade_send)
            cascade_send = None

            direct = _join_demucs_child(
                direct_process,
                direct_receive,
                "direct",
            )
            _stage("direct-demucs.done", started)

            cascade = _join_demucs_child(
                cascade_process,
                cascade_receive,
                "cascade",
            )
            _stage("cascade-demucs.done", started)
    except BaseException:
        _terminate_and_join(direct_process)
        _terminate_and_join(cascade_process)
        raise
    finally:
        _close_connection(direct_send)
        _close_connection(direct_receive)
        _close_connection(cascade_send)
        _close_connection(cascade_receive)

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
