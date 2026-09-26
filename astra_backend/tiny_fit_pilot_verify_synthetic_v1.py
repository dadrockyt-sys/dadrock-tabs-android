#!/usr/bin/env python3
"""Exact-runtime synthetic verification for Astra tiny-fit pilot V1.

No corpus, network, source archive or real optimizer work is performed here.
"""
from __future__ import annotations

import json
import math

import numpy as np
import torch

from evaluation.prepared_event_adapter_v1 import prepare_event_crop
from tiny_fit_pilot_v1 import (
    FEATURE_DIM,
    MAX_OPTIMIZER_STEPS,
    MAX_TRAIN_EVAL_SECONDS,
    decode_event_list,
    fit_tiny_model,
)


def main():
    frames = 40
    hop = 0.01
    prepared = prepare_event_crop(
        {"E": [(0.05, 0.16, 45), (0.16, 0.28, 45)]},
        capture_id="synthetic:P1:singlenotes:repeat",
        lag_ms=0,
        allowlist_lag_ms=0,
        crop_start_frame=0,
        frames=frames,
        hop_seconds=hop,
    )
    assert prepared["launchReady"] is True
    assert len(prepared["scorableEvents"]) == 2
    assert sum(v == 1 for v in prepared["onset"][0]) == 2

    features = np.zeros((1, frames, FEATURE_DIM), dtype=np.float32)
    state = np.asarray(prepared["state"], dtype=np.int16)[None, :, :]
    onset = np.asarray(prepared["onset"], dtype=np.int16)[None, :, :]
    for frame in range(frames):
        features[0, frame, 0] = 1.0
        features[0, frame, 1] = float(state[0, 0, frame] >= 0)
        features[0, frame, 2] = float(onset[0, 0, frame] == 1)
        features[0, frame, 3] = frame / frames

    model, fit = fit_tiny_model(
        features,
        state,
        onset,
        requested_steps=20,
        wall_seconds_limit=60,
    )
    assert fit["optimizerSteps"] == 20
    assert fit["optimizerSteps"] <= MAX_OPTIMIZER_STEPS
    assert fit["elapsedSeconds"] <= MAX_TRAIN_EVAL_SECONDS
    assert fit["finalLoss"]["total"] < fit["initialLoss"]["total"]
    assert all(math.isfinite(v) for side in ("initialLoss", "finalLoss") for v in fit[side].values())

    # Decoder proof is deliberately independent of optimizer luck: one continuous
    # same-fret state with two onset admissions must become two explicit events.
    state_logits = torch.full((10, 6, 21), -8.0)
    state_logits[:, :, 20] = 8.0
    state_logits[2:9, 0, 20] = -8.0
    state_logits[2:9, 0, 5] = 8.0
    onset_logits = torch.full((10, 6), -8.0)
    onset_logits[2, 0] = 8.0
    onset_logits[5, 0] = 8.0
    decoded = decode_event_list(state_logits.reshape(10, -1), onset_logits, hop_seconds=hop)
    s0 = [e for e in decoded if e.string == 0]
    assert len(s0) == 2 and [e.fret for e in s0] == [5, 5]

    # Extension attempts must fail closed.
    rejected = []
    for kwargs in (
        {"requested_steps": MAX_OPTIMIZER_STEPS + 1},
        {"wall_seconds_limit": MAX_TRAIN_EVAL_SECONDS + 1},
    ):
        try:
            fit_tiny_model(features, state, onset, **kwargs)
        except ValueError:
            rejected.append(True)
        else:
            rejected.append(False)
    assert all(rejected)

    out = {
        "schema": "astra-tiny-fit-pilot-synthetic-smoke-v1",
        "adapterRepeatedAttackPreserved": True,
        "decoderSameFretReattackPreserved": True,
        "finiteBackwardAndLossDecrease": True,
        "capExtensionRejected": True,
        "syntheticOptimizerStepsExecuted": fit["optimizerSteps"],
        "realOptimizerStepsExecuted": 0,
        "p1p2MediaAccessed": False,
        "p3Accessed": False,
        "customerDeliveryEligible": False,
    }
    print("TINY_FIT_SYNTHETIC_PASS=" + json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
