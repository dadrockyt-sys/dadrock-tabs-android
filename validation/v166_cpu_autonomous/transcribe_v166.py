#!/usr/bin/env python3
"""V166 CPU transcriber with one frozen paired-window Guitar template change.

The exact V165 transcriber wrapper is identity-pinned and mechanically versioned
forward. The returned adapted module is then patched at exactly one global helper:
`three_frame_template` becomes a six-frame paired-window template using offsets
[-1, 0, 1, 2, 3, 4] and the adapted module's exact frozen `template_scores`.
No song/reference/scorer I/O occurs while constructing this module.
"""
from __future__ import annotations

import hashlib
import sys
import types
from pathlib import Path
from typing import Callable

import numpy as np

FROZEN_V165_TRANSCRIBER_BLOB = "45d595853302b077fbf4f3094e9a4922fba02435"
V166_TEMPLATE_FRAME_OFFSETS = (-1, 0, 1, 2, 3, 4)
V166_TEMPLATE_FRAME_COUNT = 6


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def paired_window_frames(frame: int, n_frames: int) -> list[int]:
    """Return exact preregistered paired-window frame indices with clipping."""
    if int(n_frames) <= 0:
        raise RuntimeError("V166 paired-window template requires positive frame count")
    center = int(frame)
    hi = int(n_frames) - 1
    return [int(np.clip(center + delta, 0, hi)) for delta in V166_TEMPLATE_FRAME_OFFSETS]


def paired_window_template_with(
    template_scores_fn: Callable,
    cqt: np.ndarray,
    freqs: np.ndarray,
    frame: int,
    midi_min: int,
    midi_max: int,
):
    """Apply an injected frozen template_scores callable to the exact six frames."""
    x = np.asarray(cqt)
    if x.ndim != 2 or x.shape[1] <= 0:
        raise RuntimeError("V166 paired-window template requires nonempty 2D CQT")
    frames = paired_window_frames(frame, x.shape[1])
    return template_scores_fn(cqt, freqs, frames, midi_min, midi_max)


def _build_versioned_v165_wrapper() -> types.ModuleType:
    repo = Path(__file__).resolve().parents[2]
    path = repo / "validation/v165_cpu_autonomous/transcribe_v165.py"
    if not path.is_file() or _git_blob_sha(path) != FROZEN_V165_TRANSCRIBER_BLOB:
        raise RuntimeError("V166 frozen V165 transcriber dependency identity mismatch")
    source = path.read_text().replace("v165", "v166").replace("V165", "V166")
    module = types.ModuleType("_dadrock_v166_versioned_v165_transcriber")
    module.__file__ = str(Path(__file__).resolve())
    module.__dict__["__builtins__"] = __builtins__
    parent = str(Path(__file__).resolve().parent)
    inserted = parent not in sys.path
    if inserted:
        sys.path.insert(0, parent)
    try:
        exec(compile(source, str(Path(__file__).resolve()), "exec"), module.__dict__)
    finally:
        if inserted:
            sys.path.remove(parent)
    return module


def _install_paired_window_template(module: types.ModuleType) -> types.ModuleType:
    frozen_template_scores = module.template_scores

    def _paired_window_template(cqt, freqs, frame, midi_min, midi_max):
        return paired_window_template_with(
            frozen_template_scores,
            cqt,
            freqs,
            frame,
            midi_min,
            midi_max,
        )

    module.three_frame_template = _paired_window_template
    module.V166_TEMPLATE_FRAME_OFFSETS = V166_TEMPLATE_FRAME_OFFSETS
    module.V166_TEMPLATE_FRAME_COUNT = V166_TEMPLATE_FRAME_COUNT
    module.V166_TEMPLATE_EVIDENCE_MODE = "paired-adjacent-six-frame"
    return module


_BASE = _build_versioned_v165_wrapper()


def build_adapted_module() -> types.ModuleType:
    return _install_paired_window_template(_BASE.build_adapted_module())


def main() -> int:
    return int(build_adapted_module().main())


# Expose mechanically versioned schemas/helpers for static and structural pinning.
for _name, _value in vars(_BASE).items():
    if _name.startswith("__") or _name in {"build_adapted_module", "main"}:
        continue
    globals().setdefault(_name, _value)


if __name__ == "__main__":
    raise SystemExit(main())
