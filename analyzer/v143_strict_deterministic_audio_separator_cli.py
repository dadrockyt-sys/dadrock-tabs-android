from __future__ import annotations

import os
import random


SEED = int(os.environ.get("V143_SEPARATOR_SEED", "143"))

# These must be present before CUDA libraries perform their first GEMM selection.
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
os.environ.setdefault("PYTHONHASHSEED", str(SEED))


def configure_strict_determinism(seed: int = SEED) -> None:
    """Research-only strict CUDA determinism boundary for V143 separation.

    This preserves the frozen separator models and inference parameters while
    forcing deterministic algorithm selection wherever PyTorch exposes a switch.
    It is intentionally separate from the already-validated seeded CLI so the
    historical evidence remains unchanged until this stricter boundary is tested.
    """
    value = int(seed)
    random.seed(value)

    try:
        import numpy as np

        np.random.seed(value)
    except Exception:
        pass

    import torch

    torch.manual_seed(value)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(value)

    torch.use_deterministic_algorithms(True, warn_only=False)
    torch.set_float32_matmul_precision("highest")

    if hasattr(torch.backends, "cudnn"):
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True
        if hasattr(torch.backends.cudnn, "allow_tf32"):
            torch.backends.cudnn.allow_tf32 = False

    if hasattr(torch.backends, "cuda"):
        matmul = getattr(torch.backends.cuda, "matmul", None)
        if matmul is not None and hasattr(matmul, "allow_tf32"):
            matmul.allow_tf32 = False

        # Prefer the deterministic math implementation for scaled dot-product
        # attention when these controls exist. This does not change model weights.
        for name, value_to_set in (
            ("enable_flash_sdp", False),
            ("enable_mem_efficient_sdp", False),
            ("enable_math_sdp", True),
        ):
            fn = getattr(torch.backends.cuda, name, None)
            if callable(fn):
                fn(value_to_set)


if __name__ == "__main__":
    configure_strict_determinism()
    from audio_separator.utils.cli import main

    main()
