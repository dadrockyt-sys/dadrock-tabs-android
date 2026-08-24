from __future__ import annotations

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
    """Seed RNGs and force deterministic Torch execution for separator inference.

    This is a reference-free execution boundary only. Model choices, Demucs
    shifts/overlap/segment size, RoFormer batch size, and all musical rules remain
    unchanged. CPU Demucs uses one Torch/native math thread; accelerated components
    keep deterministic Torch/cuDNN/cuBLAS controls.
    """
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


def install_dedicated_demucs_shift_rng(seed: int = SEED) -> None:
    """Give Demucs' shift trick a private RNG whose state nothing else can consume.

    audio-separator's bundled Demucs `apply_model` intentionally calls
    `random.randint` for each shift. Seeding Python at process start is not a
    sufficient isolation boundary if unrelated imports/model setup consume the
    process-global RNG first. Replacing only that module's `random` handle keeps
    shifts=1 and the exact Demucs algorithm while making its shift sequence depend
    solely on V143_SEPARATOR_SEED. This path contains no song/reference data.

    When V143_DEMUCS_SHIFT_TRACE_PATH is set, the wrapper records only the randint
    bounds and selected integer so a research probe can prove whether this hook was
    actually exercised. The trace switch is off by default and changes no inference
    setting or musical behavior.
    """
    from audio_separator.separator.uvr_lib_v5.demucs import apply as demucs_apply

    demucs_apply.random = _DedicatedRandom(int(seed))


if __name__ == "__main__":
    seed_separator_runtime()
    from audio_separator.utils.cli import main

    if os.environ.get("V143_DEMUCS_FIXED_SHIFT_RNG") == "1":
        install_dedicated_demucs_shift_rng()
    main()
