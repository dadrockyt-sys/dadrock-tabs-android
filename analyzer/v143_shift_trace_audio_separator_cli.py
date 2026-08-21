from __future__ import annotations

import json
import os
from pathlib import Path

from v143_seeded_audio_separator_cli import seed_separator_runtime


TRACE_PATH = os.environ.get("V143_SHIFT_TRACE_PATH")
TRACE_STAGE = os.environ.get("V143_SHIFT_TRACE_STAGE", "unknown")


def _append_trace(payload: dict) -> None:
    if not TRACE_PATH:
        return
    path = Path(TRACE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def main() -> None:
    # Preserve the existing seeded research boundary exactly.
    seed_separator_runtime()

    # Patch only the Python randint call used by Demucs' shift trick. The wrapper
    # returns the original value unchanged, so the separator mathematics are not
    # altered. Logging is research-only and occurs in the child interpreter.
    from audio_separator.separator.uvr_lib_v5.demucs import apply as demucs_apply

    original_randint = demucs_apply.random.randint
    call_index = 0

    def traced_randint(a: int, b: int) -> int:
        nonlocal call_index
        value = int(original_randint(a, b))
        call_index += 1
        _append_trace(
            {
                "call": call_index,
                "stage": TRACE_STAGE,
                "a": int(a),
                "b": int(b),
                "value": value,
            }
        )
        return value

    demucs_apply.random.randint = traced_randint

    from audio_separator.utils.cli import main as separator_main

    separator_main()


if __name__ == "__main__":
    main()
