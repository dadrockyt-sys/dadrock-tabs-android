#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import sys
import time

import numpy as np
import torch
import torch.nn.functional as F

NUM_STRINGS = 6
NUM_CLASSES = 21
DIM_IN = 192
FRAME_WIDTH = 9
EFFECTIVE_BATCH = 32
SEQUENCE_FRAMES = 200
SEED = 20260921


def masked_loss(logits, labels):
    batch, frames = labels.shape[0], labels.shape[-1]
    x = logits.reshape(batch, frames, NUM_STRINGS, NUM_CLASSES)
    target = labels.transpose(1, 2).contiguous()
    flat = F.cross_entropy(
        x.reshape(-1, NUM_CLASSES),
        target.reshape(-1),
        reduction="none",
    ).reshape(batch, frames, NUM_STRINGS)
    return flat.mean()


def state_sha256(model):
    h = hashlib.sha256()
    for name, value in sorted(model.state_dict().items()):
        t = value.detach().cpu().contiguous()
        h.update(name.encode()); h.update(b"\0")
        h.update(t.numpy().tobytes())
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--microbatch", type=int, required=True)
    parser.add_argument("--measured-steps", type=int, default=2)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if args.microbatch <= 0 or EFFECTIVE_BATCH % args.microbatch:
        raise SystemExit("microbatch must divide effective batch 32")

    sys.path.insert(0, args.source_root)
    from amt_tools.models.tabcnn import TabCNN
    from amt_tools.tools.instrument import GuitarProfile
    from amt_tools.tools.constants import KEY_TABLATURE

    torch.manual_seed(SEED)
    np.random.seed(SEED)
    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))
    torch.use_deterministic_algorithms(True)

    model = TabCNN(
        dim_in=DIM_IN,
        profile=GuitarProfile(tuning=["E2","A2","D3","G3","B3","E4"], num_frets=19),
        device="cpu",
    )
    optimizer = torch.optim.Adadelta(model.parameters(), lr=1.0)
    accumulation = EFFECTIVE_BATCH // args.microbatch

    rng = np.random.RandomState(SEED)
    timings = []
    losses = []

    # One unmeasured warm-up effective step.
    total_steps = args.measured_steps + 1
    for step in range(total_steps):
        optimizer.zero_grad(set_to_none=True)
        t0 = time.perf_counter()
        step_loss = 0.0
        for _ in range(accumulation):
            feats = rng.normal(
                0, 1, size=(args.microbatch, SEQUENCE_FRAMES, 1, DIM_IN, FRAME_WIDTH)
            ).astype(np.float32)
            labels = rng.randint(
                0, NUM_CLASSES, size=(args.microbatch, NUM_STRINGS, SEQUENCE_FRAMES), dtype=np.int64
            )
            logits = model(torch.from_numpy(feats))[KEY_TABLATURE]
            loss = masked_loss(logits, torch.from_numpy(labels)) / accumulation
            loss.backward()
            step_loss += float(loss.detach())
        optimizer.step()
        elapsed = time.perf_counter() - t0
        if step:
            timings.append(elapsed)
            losses.append(step_loss)

    receipt = {
        "schema": "astra-guitar-techs-v2-synthetic-cpu-benchmark-v1",
        "microbatchSequences": args.microbatch,
        "gradientAccumulationSteps": accumulation,
        "effectiveBatchSequences": EFFECTIVE_BATCH,
        "sequenceFrames": SEQUENCE_FRAMES,
        "supervisedFramePositionsPerEffectiveStep": EFFECTIVE_BATCH * SEQUENCE_FRAMES,
        "measuredEffectiveSteps": args.measured_steps,
        "effectiveStepSeconds": timings,
        "medianEffectiveStepSeconds": float(np.median(timings)),
        "meanEffectiveStepSeconds": float(np.mean(timings)),
        "maxRssKiB": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        "torchVersion": torch.__version__,
        "numpyVersion": np.__version__,
        "threads": torch.get_num_threads(),
        "finalStateSha256": state_sha256(model),
        "guards": {
            "usesRealMedia": False,
            "p3Opened": False,
            "paidComputeUsed": False,
            "customerDeliveryEligible": False,
        },
    }
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
