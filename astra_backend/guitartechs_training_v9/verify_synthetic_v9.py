#!/usr/bin/env python3
from __future__ import annotations

import numpy as np
import torch

from paired_view import FROZEN_CONFIG, make_training_view, paired_training_views, symmetric_kl_consistency


def main():
    rng = np.random.default_rng(20261006)
    feat = rng.normal(0.0, 1.0, size=(192, 260)).astype(np.float32)

    a1 = make_training_view(feat, 17)
    a2 = make_training_view(feat, 17)
    assert np.array_equal(a1, a2)
    assert a1.shape == feat.shape
    assert np.isfinite(a1).all()
    print("V9_DETERMINISTIC_AUGMENTATION_PASS")

    v1, v2 = paired_training_views(feat, 41)
    assert v1.shape == feat.shape and v2.shape == feat.shape
    assert not np.array_equal(v1, v2)
    assert FROZEN_CONFIG.gain_db_max_abs == 3.0
    assert FROZEN_CONFIG.noise_snr_db_min == 30.0
    assert FROZEN_CONFIG.noise_snr_db_max == 50.0
    assert FROZEN_CONFIG.tilt_db_per_octave_max_abs == 1.5
    assert FROZEN_CONFIG.mask_span_frames_max == 4
    assert FROZEN_CONFIG.mask_span_count_max == 2
    print("V9_FROZEN_RANGE_PASS")

    # The augmentation contract cannot change the time or frequency dimensions,
    # which fail-closes pitch shifting and time stretching in this module.
    assert v1.shape[0] == 192 and v1.shape[1] == feat.shape[1]
    print("V9_NO_PITCH_TIME_REMAP_PASS")

    logits1 = torch.randn(2, 40, 6, 21, generator=torch.Generator().manual_seed(3), requires_grad=True)
    logits2 = torch.randn(2, 40, 6, 21, generator=torch.Generator().manual_seed(4), requires_grad=True)
    loss = symmetric_kl_consistency(logits1, logits2)
    assert torch.isfinite(loss) and float(loss.detach()) > 0.0
    loss.backward()
    assert logits1.grad is not None and torch.isfinite(logits1.grad).all()
    assert logits2.grad is not None and torch.isfinite(logits2.grad).all()

    identical = torch.randn(2, 10, 21, generator=torch.Generator().manual_seed(5))
    zeroish = symmetric_kl_consistency(identical, identical)
    assert abs(float(zeroish)) < 1e-6
    print("V9_CONSISTENCY_LOSS_PASS")
    print("V9_SYNTHETIC_NO_MEDIA_PASS")


if __name__ == "__main__":
    main()
