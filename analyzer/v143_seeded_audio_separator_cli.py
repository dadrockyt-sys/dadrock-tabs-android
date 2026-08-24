from __future__ import annotations

import os
import random


SEED = int(os.environ.get("V143_SEPARATOR_SEED", "143"))


def seed_separator_runtime(seed: int = SEED) -> None:
    """Seed RNGs and force deterministic Torch CUDA behavior for separator inference.

    This remains a reference-free execution boundary. It does not alter model
    choices, Demucs shift count/overlap/segment size, RoFormer batch size, or any
    musical selection rule. The only purpose is to make identical audio + model
    inputs produce identical separator bytes across genuinely fresh processes.
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

        torch.manual_seed(value)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(value)

        # Determinism is required because downstream event identity must not
        # depend on CUDA/cuDNN/cuBLAS kernel scheduling. CUBLAS_WORKSPACE_CONFIG
        # is exported by the parent before this interpreter starts.
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
        # Do not silently downgrade a requested deterministic Torch runtime.
        # If Torch is importable but deterministic configuration fails, surface
        # the error rather than producing a falsely "deterministic" stem.
        try:
            import torch  # noqa: F401
        except Exception:
            return
        raise


if __name__ == "__main__":
    seed_separator_runtime()
    from audio_separator.utils.cli import main

    main()
