"""Pre-optimizer H1 prepared-array semantic checks; no media decoding or training.

Runs after frozen manifest/file hashes. Uses read-only mmap and bounded chunks.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

FEATURE_BINS = 192
STRINGS = 6
MAX_FRET = 19
MASK = -100
SILENCE = -1
CHUNK_FRAMES = 4096


def verify_prepared_pair(feature_path, label_path, frames):
    """Reject noncanonical dtype/shape, corrupt features or invalid note classes.

    The frozen preparation routine writes native float32 CQT and int16 string
    labels. All observations are read-only; no tensors or weights are exported.
    """
    if type(frames) is not int or frames < 200:
        raise RuntimeError("H1_PREPARED_FRAME_COUNT_INVALID")
    try:
        x = np.load(Path(feature_path), mmap_mode="r", allow_pickle=False)
        y = np.load(Path(label_path), mmap_mode="r", allow_pickle=False)
    except (OSError, ValueError, TypeError) as exc:
        raise RuntimeError("H1_PREPARED_NPY_DECODE_ERROR") from exc
    if x.shape != (FEATURE_BINS, frames) or y.shape != (STRINGS, frames):
        raise RuntimeError("H1_PREPARED_SHAPE_MISMATCH")
    if x.dtype != np.dtype("float32") or y.dtype != np.dtype("int16"):
        raise RuntimeError("H1_PREPARED_DTYPE_MISMATCH")
    for lo in range(0, frames, CHUNK_FRAMES):
        hi = min(lo + CHUNK_FRAMES, frames)
        if not np.isfinite(x[:, lo:hi]).all():
            raise RuntimeError("H1_PREPARED_NONFINITE_FEATURE")
        chunk = y[:, lo:hi]
        allowed = (chunk == MASK) | (chunk == SILENCE) | ((chunk >= 0) & (chunk <= MAX_FRET))
        if not allowed.all():
            raise RuntimeError("H1_PREPARED_INVALID_LABEL_CLASS")
    return {"verifiedFrames": frames, "featureDtype": "float32", "labelDtype": "int16"}
