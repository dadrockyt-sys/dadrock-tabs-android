"""Minimal TabCNN preprocessing contract derived from pinned upstream source semantics.

This module performs no model loading or inference. It intentionally depends only on
NumPy/librosa and mirrors the frozen 22.05 kHz CQT -> dB -> [0,1] -> 9-frame window path.
"""

from __future__ import annotations

import hashlib
from typing import Any

import librosa
import numpy as np

SAMPLE_RATE_HZ = 22050
HOP_LENGTH_SAMPLES = 512
CQT_BINS = 192
BINS_PER_OCTAVE = 24
FMIN_NOTE = "C1"
GAMMA = 0
FRAME_CONTEXT = 9


def rms_normalize(audio: np.ndarray) -> np.ndarray:
    audio = np.asarray(audio)
    rms = np.sqrt(np.mean(audio ** 2))
    if rms > 0:
        audio = audio / rms
    return audio


def extract_cqt_features(audio: np.ndarray) -> np.ndarray:
    vqt = librosa.vqt(
        y=np.asarray(audio),
        sr=SAMPLE_RATE_HZ,
        hop_length=HOP_LENGTH_SAMPLES,
        fmin=librosa.note_to_hz(FMIN_NOTE),
        n_bins=CQT_BINS,
        bins_per_octave=BINS_PER_OCTAVE,
        gamma=GAMMA,
    )
    feats = np.abs(vqt)
    feats = librosa.core.amplitude_to_db(feats, ref=np.max)
    feats = feats / 80
    feats = feats + 1
    return np.expand_dims(feats, axis=0)


def framify_activations(
    activations: np.ndarray,
    win_length: int = FRAME_CONTEXT,
    hop_length: int = 1,
    pad: bool = True,
) -> np.ndarray:
    num_frames = activations.shape[-1]
    pad_length = win_length // 2
    if pad:
        num_frames_padded = num_frames + 2 * pad_length
    else:
        num_frames_padded = max(win_length, num_frames)

    activations = librosa.util.pad_center(activations, size=num_frames_padded)
    num_hops = (num_frames_padded - 2 * pad_length) // hop_length
    chunk_idcs = np.arange(0, num_hops) * hop_length
    chunks = [
        np.expand_dims(activations[..., i : i + win_length], axis=-2)
        for i in chunk_idcs
    ]
    return np.concatenate(chunks, axis=-2)


def assemble_model_windows(features: np.ndarray) -> np.ndarray:
    batched = np.expand_dims(features, axis=0)
    windowed = framify_activations(batched, FRAME_CONTEXT, pad=True)
    windowed = windowed.swapaxes(-2, -3)
    windowed = windowed.swapaxes(-3, -4)
    return windowed


def preprocess_waveform(audio: np.ndarray) -> dict[str, np.ndarray]:
    normalized = rms_normalize(audio)
    features = extract_cqt_features(normalized)
    model_windows = assemble_model_windows(features)
    return {
        "normalized_audio": normalized,
        "features": features,
        "model_windows": model_windows,
    }


def array_sha256(array: np.ndarray) -> str:
    contiguous = np.ascontiguousarray(array)
    h = hashlib.sha256()
    h.update(str(contiguous.dtype).encode("utf-8"))
    h.update(b"\0")
    h.update(",".join(str(x) for x in contiguous.shape).encode("ascii"))
    h.update(b"\0")
    h.update(contiguous.tobytes(order="C"))
    return h.hexdigest()


def describe_array(array: np.ndarray) -> dict[str, Any]:
    return {
        "shape": list(array.shape),
        "dtype": str(array.dtype),
        "min": float(np.min(array)),
        "max": float(np.max(array)),
        "sha256": array_sha256(array),
    }
