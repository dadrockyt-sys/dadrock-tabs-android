from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import Any


SEED = int(os.environ.get("V143_SEPARATOR_SEED", "143"))


class _DedicatedRandom:
    """Module-like RNG wrapper backed by one private deterministic generator."""

    def __init__(self, seed: int):
        self._rng = random.Random(int(seed))

    def randint(self, a: int, b: int) -> int:
        value = int(self._rng.randint(int(a), int(b)))
        trace_path = os.environ.get("V143_DEMUCS_SHIFT_TRACE_PATH")
        if trace_path:
            path = Path(trace_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(f"{int(a)},{int(b)},{value}\n")
        return value

    def __getattr__(self, name: str) -> Any:
        return getattr(self._rng, name)


def seed_separator_runtime(seed: int = SEED) -> None:
    """Seed RNGs and force deterministic Torch execution for separator inference."""
    value = int(seed)
    random.seed(value)

    try:
        import numpy as np
        np.random.seed(value)
    except Exception:
        pass

    try:
        import torch

        torch.set_num_threads(1)
        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass

        torch.manual_seed(value)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(value)

        torch.use_deterministic_algorithms(True, warn_only=False)
        if hasattr(torch, "set_float32_matmul_precision"):
            torch.set_float32_matmul_precision("highest")

        if hasattr(torch.backends, "cudnn"):
            torch.backends.cudnn.benchmark = False
            torch.backends.cudnn.deterministic = True
            if hasattr(torch.backends.cudnn, "allow_tf32"):
                torch.backends.cudnn.allow_tf32 = False

        if hasattr(torch.backends, "cuda") and hasattr(torch.backends.cuda, "matmul"):
            torch.backends.cuda.matmul.allow_tf32 = False
    except Exception:
        try:
            import torch  # noqa: F401
        except Exception:
            return
        raise


def write_demucs_runtime_trace() -> None:
    """Optional research trace proving what the Demucs child actually selected.

    Off by default. Records execution controls only; no audio, song, reference,
    scorer, model-output, or musical information is written.
    """
    trace_path = os.environ.get("V143_DEMUCS_RUNTIME_TRACE_PATH")
    if not trace_path:
        return

    import torch

    cpu_capability = None
    cpu_backend = getattr(torch.backends, "cpu", None)
    getter = getattr(cpu_backend, "get_cpu_capability", None)
    if callable(getter):
        cpu_capability = str(getter())

    payload = {
        "torchVersion": str(torch.__version__),
        "torchCpuCapability": cpu_capability,
        "torchCudaAvailable": bool(torch.cuda.is_available()),
        "mkldnnAvailable": bool(torch.backends.mkldnn.is_available()),
        "mkldnnEnabled": bool(torch.backends.mkldnn.enabled),
        "torchNumThreads": int(torch.get_num_threads()),
        "torchNumInteropThreads": int(torch.get_num_interop_threads()),
        "environment": {
            key: os.environ.get(key)
            for key in (
                "ATEN_CPU_CAPABILITY",
                "ONEDNN_MAX_CPU_ISA",
                "DNNL_MAX_CPU_ISA",
                "MKL_CBWR",
                "MKL_NUM_THREADS",
                "MKL_DYNAMIC",
                "OMP_NUM_THREADS",
                "OMP_DYNAMIC",
            )
        },
    }
    path = Path(trace_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")


def install_dedicated_demucs_shift_rng(seed: int = SEED) -> None:
    """Give Demucs' shift trick a private RNG whose state nothing else can consume."""
    from audio_separator.separator.uvr_lib_v5.demucs import apply as demucs_apply
    demucs_apply.random = _DedicatedRandom(int(seed))


if __name__ == "__main__":
    seed_separator_runtime()
    write_demucs_runtime_trace()
    from audio_separator.utils.cli import main

    if os.environ.get("V143_DEMUCS_FIXED_SHIFT_RNG") == "1":
        install_dedicated_demucs_shift_rng()
    main()
