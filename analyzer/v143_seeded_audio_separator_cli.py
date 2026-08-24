from __future__ import annotations

import os
import random


SEED = int(os.environ.get("V143_SEPARATOR_SEED", "143"))


def seed_separator_runtime(seed: int = SEED) -> None:
    """Seed RNGs and force deterministic Torch execution for separator inference.

    This is a reference-free execution boundary only. Model choices, Demucs
    shifts/overlap/segment size, RoFormer batch size, and all musical rules remain
    unchanged. CPU Demucs is forced to one Torch thread so reduction order cannot
    vary across fresh hosts; GPU controls remain deterministic for components that
    use acceleration.
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

        # Set CPU thread topology before separator/model inference begins.
        torch.set_num_threads(1)
        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            # May already be fixed by Torch initialization; one process executes
            # this boundary only once before audio-separator import.
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


if __name__ == "__main__":
    seed_separator_runtime()
    from audio_separator.utils.cli import main

    main()
