from __future__ import annotations

import os

from v143_seeded_audio_separator_cli import (
    install_dedicated_demucs_shift_rng,
    seed_separator_runtime,
    write_demucs_runtime_trace,
)


if __name__ == "__main__":
    # Preserve the frozen seed/deterministic setup first. The optional thread
    # override exists only for the separate diagnostic Modal app; Production
    # never sets V143_DIAGNOSTIC_TORCH_THREADS and never imports this module.
    seed_separator_runtime()

    threads = int(os.environ.get("V143_DIAGNOSTIC_TORCH_THREADS", "1"))
    if threads < 1 or threads > 16:
        raise RuntimeError("Diagnostic torch thread count must be between 1 and 16")

    import torch

    torch.set_num_threads(threads)
    try:
        torch.set_num_interop_threads(threads)
    except RuntimeError:
        pass

    write_demucs_runtime_trace()

    from audio_separator.utils.cli import main

    if os.environ.get("V143_DEMUCS_FIXED_SHIFT_RNG") == "1":
        install_dedicated_demucs_shift_rng()

    main()
