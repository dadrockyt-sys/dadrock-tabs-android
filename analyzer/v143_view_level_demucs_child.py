from __future__ import annotations

import json
from pathlib import Path


def run_exact_demucs_child(
    input_audio: str,
    output_dir: str,
    shift_trace_path: str,
    runtime_trace_path: str,
    result_path: str,
) -> None:
    """Run one unchanged exact-CPU Demucs invocation in an isolated process."""
    from v143_production_separator import separate_demucs_guitar
    from v143_seeded_separator import (
        CUBLAS_WORKSPACE_CONFIG,
        DEMUCS_SINGLE_THREAD_ENV,
        SEPARATOR_SEED,
        _temporary_environment,
        seeded_audio_separator_cli,
    )

    result_file = Path(result_path)
    payload: dict[str, object]
    try:
        common_env = {
            "PYTHONHASHSEED": SEPARATOR_SEED,
            "V143_SEPARATOR_SEED": SEPARATOR_SEED,
            "CUBLAS_WORKSPACE_CONFIG": CUBLAS_WORKSPACE_CONFIG,
            "NVIDIA_TF32_OVERRIDE": "0",
        }
        demucs_env = dict(DEMUCS_SINGLE_THREAD_ENV)
        demucs_env["V143_DEMUCS_SHIFT_TRACE_PATH"] = str(shift_trace_path)
        demucs_env["V143_DEMUCS_RUNTIME_TRACE_PATH"] = str(runtime_trace_path)

        with _temporary_environment(common_env):
            with _temporary_environment(demucs_env):
                result = separate_demucs_guitar(
                    seeded_audio_separator_cli(),
                    Path(input_audio),
                    Path(output_dir),
                )

        output = Path(str(result["path"]))
        if not output.is_file() or output.stat().st_size <= 0:
            raise RuntimeError(f"exact Demucs child output missing: {output}")

        payload = {
            "completed": True,
            "path": str(output),
            "elapsedSeconds": result.get("elapsedSeconds"),
        }
    except BaseException as exc:
        payload = {
            "completed": False,
            "terminalType": type(exc).__name__,
            "message": str(exc)[:2000],
        }

    result_file.parent.mkdir(parents=True, exist_ok=True)
    result_file.write_text(json.dumps(payload, allow_nan=False) + "\n", encoding="utf-8")


__all__ = ["run_exact_demucs_child"]
