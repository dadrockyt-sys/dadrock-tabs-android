#!/usr/bin/env python3
"""Deterministic synthetic backward/optimizer smoke for the pinned TabCNN source.

No Guitar-TECHS media is opened. No published model checkpoint is loaded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import resource
import sys
import time
from pathlib import Path

import librosa
import numpy as np
import scipy
import torch

SEED = 20260921
BATCH_SIZE = 32
NUM_FRAMES = 1
NUM_STRINGS = 6
NUM_CLASSES = 21
NUM_LOGITS = NUM_STRINGS * NUM_CLASSES
FEATURE_BINS = 192
FRAME_WIDTH = 9
MAX_WALL_SECONDS = 120.0
MAX_PEAK_RSS_MB = 2048.0


def state_sha256(model: torch.nn.Module) -> str:
    h = hashlib.sha256()
    for name, value in sorted(model.state_dict().items()):
        tensor = value.detach().cpu().contiguous()
        h.update(name.encode("utf-8"))
        h.update(b"\0")
        h.update(str(tensor.dtype).encode("ascii"))
        h.update(b"\0")
        h.update(",".join(str(x) for x in tensor.shape).encode("ascii"))
        h.update(b"\0")
        h.update(tensor.numpy().tobytes(order="C"))
    return h.hexdigest()


def make_features() -> torch.Tensor:
    total = BATCH_SIZE * NUM_FRAMES * FEATURE_BINS * FRAME_WIDTH
    values = torch.linspace(-1.0, 1.0, steps=total, dtype=torch.float32)
    return values.reshape(BATCH_SIZE, NUM_FRAMES, 1, FEATURE_BINS, FRAME_WIDTH)


def make_labels() -> torch.Tensor:
    labels = torch.empty((BATCH_SIZE, NUM_STRINGS, NUM_FRAMES), dtype=torch.long)
    for batch in range(BATCH_SIZE):
        for string in range(NUM_STRINGS):
            label = (batch + string) % NUM_CLASSES
            labels[batch, string, 0] = -1 if label == 20 else label
    return labels


def reset_seeds() -> None:
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)


def run_once(TabCNN, GuitarProfile, key_tablature: str) -> dict:
    reset_seeds()

    profile = GuitarProfile(num_frets=19)
    model = TabCNN(dim_in=FEATURE_BINS, profile=profile, device="cpu")
    model.train()
    optimizer = torch.optim.Adadelta(model.parameters(), lr=1.0)

    features = make_features()
    labels = make_labels()

    before = state_sha256(model)
    optimizer.zero_grad(set_to_none=True)
    output = model(features)[key_tablature]

    expected_shape = (BATCH_SIZE, NUM_FRAMES, NUM_LOGITS)
    if tuple(output.shape) != expected_shape:
        raise AssertionError(f"unexpected output shape {tuple(output.shape)} != {expected_shape}")

    loss = model.dense[-1].get_loss(output, labels)
    if not bool(torch.isfinite(loss)):
        raise AssertionError(f"non-finite loss: {loss}")

    loss.backward()

    grad_sq = 0.0
    grad_tensors = 0
    for parameter in model.parameters():
        if parameter.grad is None:
            continue
        if not bool(torch.all(torch.isfinite(parameter.grad))):
            raise AssertionError("non-finite gradient detected")
        grad_sq += float(torch.sum(parameter.grad.detach().double() ** 2))
        grad_tensors += 1

    grad_norm = math.sqrt(grad_sq)
    if grad_tensors == 0 or not math.isfinite(grad_norm) or grad_norm <= 0:
        raise AssertionError(f"invalid gradient norm: {grad_norm}")

    optimizer.step()
    after = state_sha256(model)
    if before == after:
        raise AssertionError("optimizer step did not change model parameters")

    return {
        "loss": float(loss.detach().cpu()),
        "gradNorm": grad_norm,
        "gradientTensorCount": grad_tensors,
        "stateBeforeSha256": before,
        "stateAfterSha256": after,
        "outputShape": list(output.shape),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--receipt-out", required=True)
    args = parser.parse_args()

    source_root = str(Path(args.source_root))
    sys.path.insert(0, source_root)
    try:
        from amt_tools.models.tabcnn import TabCNN
        from amt_tools.tools.instrument import GuitarProfile
        from amt_tools.tools.constants import KEY_TABLATURE
    finally:
        sys.path.pop(0)

    started = time.perf_counter()
    first = run_once(TabCNN, GuitarProfile, KEY_TABLATURE)
    second = run_once(TabCNN, GuitarProfile, KEY_TABLATURE)
    wall_seconds = time.perf_counter() - started

    for key in ("loss", "gradNorm", "gradientTensorCount", "stateBeforeSha256", "stateAfterSha256", "outputShape"):
        if first[key] != second[key]:
            raise AssertionError(f"determinism mismatch for {key}: {first[key]} != {second[key]}")

    peak_rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    if wall_seconds > MAX_WALL_SECONDS:
        raise AssertionError(f"wall time {wall_seconds:.3f}s exceeds {MAX_WALL_SECONDS}s")
    if peak_rss_mb > MAX_PEAK_RSS_MB:
        raise AssertionError(f"peak RSS {peak_rss_mb:.3f}MB exceeds {MAX_PEAK_RSS_MB}MB")

    receipt = {
        "schema": "astra-guitar-techs-synthetic-training-smoke-v1",
        "candidateId": "astra_guitartechs_tabcnn_v1",
        "guitarTechsMediaOpened": False,
        "publishedCheckpointLoaded": False,
        "modelInitialization": "random-only",
        "deterministicRepeatedRunsEqual": True,
        "sourceRevision": "f50309ad06dc734ddae5e3a0eda756fca221e2e7",
        "sourceBlobs": {
            "modelCommon": "84beb4cf251b9cb9274d10cf203318314181af31",
            "tabcnn": "e09856db2fffd77642e005ab509846acc894b886",
            "instrument": "eddc48a8b95de057035cd11ea2d1951e754ef349",
            "constants": "79666ea0c5b0214ca664da454069b8d286cc5c18",
        },
        "runtime": {
            "platform": "linux-x86_64",
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "librosa": librosa.__version__,
            "torch": torch.__version__,
        },
        "training": {
            "seed": SEED,
            "optimizer": "Adadelta",
            "learningRate": 1.0,
            "batchSize": BATCH_SIZE,
            "framesPerSample": NUM_FRAMES,
            "featureBins": FEATURE_BINS,
            "frameWidth": FRAME_WIDTH,
            "numStrings": NUM_STRINGS,
            "classesPerString": NUM_CLASSES,
            "totalLogits": NUM_LOGITS,
        },
        "result": first,
        "budget": {
            "maxWallSeconds": MAX_WALL_SECONDS,
            "observedWallSeconds": wall_seconds,
            "maxPeakRssMb": MAX_PEAK_RSS_MB,
            "observedPeakRssMb": peak_rss_mb,
        },
    }

    out = Path(args.receipt_out)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("GUITAR_TECHS_SYNTHETIC_TRAINING_SMOKE=" + json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
