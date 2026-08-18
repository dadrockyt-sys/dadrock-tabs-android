from __future__ import annotations

import os
import random


SEED = int(os.environ.get("V143_SEPARATOR_SEED", "143"))


def seed_separator_runtime(seed: int = SEED) -> None:
    """Seed every RNG family that can affect separator inference.

    Demucs' shift trick uses Python's random module for the time-shift offset.
    NumPy/Torch are seeded as well so this wrapper is a conservative deterministic
    boundary for diagnostic use. It does not change the frozen Demucs shift count,
    overlap, segment size, model, or the BS-RoFormer -> Demucs cascade.
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
    except Exception:
        pass


if __name__ == "__main__":
    seed_separator_runtime()
    from audio_separator.utils.cli import main

    main()
