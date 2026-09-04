from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from v143_seeded_audio_separator_cli import (
    install_dedicated_demucs_shift_rng,
    seed_separator_runtime,
    write_demucs_runtime_trace,
)


def install_split_parallel_workers() -> None:
    workers = int(os.environ.get("V143_DEMUCS_SPLIT_WORKERS", "0"))
    if workers <= 0:
        return

    import torch
    from audio_separator.separator.architectures import demucs_separator

    original_apply_model = demucs_separator.apply_model
    trace_path = os.environ.get("V143_DEMUCS_SPLIT_PARALLEL_TRACE_PATH")
    invocation_count = 0

    def apply_model_with_workers(*args: Any, **kwargs: Any):
        nonlocal invocation_count
        invocation_count += 1
        if "num_workers" in kwargs:
            raise RuntimeError("Diagnostic split worker injection would overwrite an explicit num_workers value")
        kwargs["num_workers"] = workers

        if trace_path:
            device = kwargs.get("device")
            payload = {
                "schemaVersion": 1,
                "gate": "v143-demucs-split-parallel-cli",
                "requestedSplitWorkers": workers,
                "architectureApplyModelInvocationCount": invocation_count,
                "device": None if device is None else str(device),
                "torchNumThreads": int(torch.get_num_threads()),
                "torchNumInteropThreads": int(torch.get_num_interop_threads()),
                "cudaAvailable": bool(torch.cuda.is_available()),
                "mkldnnEnabled": bool(torch.backends.mkldnn.enabled),
                "ompNumThreads": os.environ.get("OMP_NUM_THREADS"),
                "mklNumThreads": os.environ.get("MKL_NUM_THREADS"),
                "fixedShiftRng": os.environ.get("V143_DEMUCS_FIXED_SHIFT_RNG"),
            }
            path = Path(trace_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")

        return original_apply_model(*args, **kwargs)

    demucs_separator.apply_model = apply_model_with_workers


def main() -> None:
    seed_separator_runtime()
    write_demucs_runtime_trace()
    if os.environ.get("V143_DEMUCS_FIXED_SHIFT_RNG") == "1":
        install_dedicated_demucs_shift_rng()
    install_split_parallel_workers()

    from audio_separator.utils.cli import main as audio_separator_main

    audio_separator_main()


if __name__ == "__main__":
    main()
