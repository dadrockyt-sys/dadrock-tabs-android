from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np
import torch
import torch.nn.functional as F


@dataclass(frozen=True)
class V9AugmentConfig:
    gain_db_max_abs: float = 3.0
    noise_snr_db_min: float = 30.0
    noise_snr_db_max: float = 50.0
    tilt_db_per_octave_max_abs: float = 1.5
    mask_span_frames_max: int = 4
    mask_span_count_max: int = 2


FROZEN_CONFIG = V9AugmentConfig()


def _validate_feature_array(feat: np.ndarray) -> np.ndarray:
    arr = np.asarray(feat, dtype=np.float32)
    if arr.ndim != 2 or arr.shape[0] != 192:
        raise ValueError("expected 192 x T feature array")
    if arr.shape[1] < 8:
        raise ValueError("feature array is too short")
    if not np.isfinite(arr).all():
        raise ValueError("feature array contains non-finite values")
    return arr


def make_training_view(feat: np.ndarray, seed: int, cfg: V9AugmentConfig = FROZEN_CONFIG) -> np.ndarray:
    """Create one deterministic, label-preserving training-side feature view.

    No pitch shift, time stretch, label mutation, reference access, or
    target-conditioned behavior is permitted here.
    """
    x = _validate_feature_array(feat).copy()
    rng = np.random.default_rng(int(seed))

    gain_db = float(rng.uniform(-cfg.gain_db_max_abs, cfg.gain_db_max_abs))
    x *= np.float32(10.0 ** (gain_db / 20.0))

    # Frequency-response tilt in feature-bin space, centered to preserve scale.
    # 192 bins span a fixed monotone frequency axis in the existing feature
    # representation. This changes only training-side feature amplitude.
    bins = np.linspace(-1.0, 1.0, x.shape[0], dtype=np.float32)
    tilt = float(rng.uniform(-cfg.tilt_db_per_octave_max_abs, cfg.tilt_db_per_octave_max_abs))
    tilt_gain = np.power(10.0, (tilt * bins) / 20.0).astype(np.float32)
    x *= tilt_gain[:, None]

    rms = float(np.sqrt(np.mean(np.square(x), dtype=np.float64)))
    if rms > 0.0:
        snr_db = float(rng.uniform(cfg.noise_snr_db_min, cfg.noise_snr_db_max))
        noise_rms = rms / (10.0 ** (snr_db / 20.0))
        x += rng.normal(0.0, noise_rms, size=x.shape).astype(np.float32)

    span_count = int(rng.integers(0, cfg.mask_span_count_max + 1))
    for _ in range(span_count):
        width = int(rng.integers(1, cfg.mask_span_frames_max + 1))
        start = int(rng.integers(0, max(1, x.shape[1] - width + 1)))
        x[:, start:start + width] = 0.0

    if not np.isfinite(x).all():
        raise RuntimeError("augmentation produced non-finite values")
    return x


def paired_training_views(feat: np.ndarray, seed: int, cfg: V9AugmentConfig = FROZEN_CONFIG):
    return (
        make_training_view(feat, seed * 2 + 1, cfg),
        make_training_view(feat, seed * 2 + 2, cfg),
    )


def symmetric_kl_consistency(logits_a: torch.Tensor, logits_b: torch.Tensor) -> torch.Tensor:
    if logits_a.shape != logits_b.shape:
        raise ValueError("paired logits must have identical shape")
    if logits_a.ndim < 2:
        raise ValueError("logits must include a class dimension")
    log_pa = F.log_softmax(logits_a, dim=-1)
    log_pb = F.log_softmax(logits_b, dim=-1)
    pa = log_pa.exp()
    pb = log_pb.exp()
    kl_ab = F.kl_div(log_pa, pb, reduction="batchmean")
    kl_ba = F.kl_div(log_pb, pa, reduction="batchmean")
    return 0.5 * (kl_ab + kl_ba)
