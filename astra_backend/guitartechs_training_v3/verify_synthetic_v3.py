#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import os
from pathlib import Path
import random
import sys
import tempfile

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from guitartechs_training_v2.train_v2 import sequence_windows
from guitartechs_training_v3 import objective_decoder as v3

SEED = 20260921


def clone_state_dict(state):
    return {k: v.detach().cpu().clone() for k, v in state.items()}


def nested_equal(a, b):
    if torch.is_tensor(a) and torch.is_tensor(b):
        return torch.equal(a, b)
    if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
        return np.array_equal(a, b)
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(nested_equal(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, type(a)):
        return len(a) == len(b) and all(nested_equal(x, y) for x, y in zip(a, b))
    return a == b


def setup_determinism():
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))


def rng_state():
    return {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch": torch.get_rng_state().clone(),
    }


def restore_rng_state(state):
    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.set_rng_state(state["torch"])


def new_model_optimizer(source_root):
    sys.path.insert(0, source_root)
    from amt_tools.models.tabcnn import TabCNN
    from amt_tools.tools.instrument import GuitarProfile

    model = TabCNN(
        dim_in=192,
        profile=GuitarProfile(
            tuning=["E2", "A2", "D3", "G3", "B3", "E4"],
            num_frets=19,
        ),
        device="cpu",
    )
    optimizer = torch.optim.Adadelta(model.parameters(), lr=1.0)
    return model, optimizer


def build_fixture():
    feat = np.random.RandomState(SEED).normal(0, 1, size=(192, 260)).astype(np.float32)
    windows = sequence_windows(feat, 20, 220)
    labels = np.full((1, 6, 200), -1, dtype=np.int64)
    labels[0, 0, 20:90] = 5
    labels[0, 1, 40:130] = 7
    labels[0, 2, 100:175] = 9
    labels[0, 3, 30:55] = 3
    labels[0, 4, 140:190] = 10
    labels[0, 5, 65:110] = 12
    return (
        torch.from_numpy(windows[None, :, None, :, :]),
        torch.from_numpy(labels),
    )


def objective_self_test(source_root):
    setup_determinism()
    sys.path.insert(0, source_root)
    from amt_tools.tools.constants import KEY_TABLATURE

    model, _ = new_model_optimizer(source_root)
    x, y = build_fixture()
    logits = model(x)[KEY_TABLATURE]
    loss, parts = v3.v3_sequence_loss(logits, y, content_weight=1.0)
    if not torch.isfinite(loss):
        raise RuntimeError("V3 synthetic objective produced nonfinite loss")
    if float(parts["identityMargin"]) < 0 or float(parts["continuity"]) < 0:
        raise RuntimeError("V3 synthetic auxiliary loss is negative")
    loss.backward()
    print("V3_OBJECTIVE_SELF_TEST_PASS")


def resume_self_test(source_root):
    setup_determinism()
    sys.path.insert(0, source_root)
    from amt_tools.tools.constants import KEY_TABLATURE

    x, y = build_fixture()

    def step(model, optimizer):
        py_scale = random.random()
        np_scale = float(np.random.random())
        jitter = torch.rand_like(x) * 1e-5
        xx = x * (1.0 + (py_scale + np_scale) * 1e-6) + jitter
        optimizer.zero_grad(set_to_none=True)
        logits = model(xx)[KEY_TABLATURE]
        loss, _ = v3.v3_sequence_loss(logits, y, content_weight=1.0)
        loss.backward()
        optimizer.step()

    setup_determinism()
    continuous, continuous_opt = new_model_optimizer(source_root)
    for _ in range(4):
        step(continuous, continuous_opt)
    continuous_model = clone_state_dict(continuous.state_dict())
    continuous_optimizer = copy.deepcopy(continuous_opt.state_dict())
    continuous_rng = rng_state()

    setup_determinism()
    split, split_opt = new_model_optimizer(source_root)
    for _ in range(2):
        step(split, split_opt)

    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "v3-resume.pt"
        torch.save({
            "modelState": clone_state_dict(split.state_dict()),
            "optimizerState": copy.deepcopy(split_opt.state_dict()),
            "rngState": rng_state(),
        }, path)

        setup_determinism()
        resumed, resumed_opt = new_model_optimizer(source_root)
        payload = torch.load(path, map_location="cpu")
        resumed.load_state_dict(payload["modelState"])
        resumed_opt.load_state_dict(payload["optimizerState"])
        restore_rng_state(payload["rngState"])
        for _ in range(2):
            step(resumed, resumed_opt)

    if not nested_equal(continuous_model, resumed.state_dict()):
        raise RuntimeError("V3 resume self-test model state diverged")
    if not nested_equal(continuous_optimizer, resumed_opt.state_dict()):
        raise RuntimeError("V3 resume self-test optimizer state diverged")
    if not nested_equal(continuous_rng, rng_state()):
        raise RuntimeError("V3 resume self-test RNG state diverged")
    print("V3_RESUME_SELF_TEST_PASS")


def decoder_self_test():
    probs = np.zeros((16, 6, v3.NUM_CLASSES), dtype=np.float64)
    probs[..., v3.SILENCE_CLASS] = 1.0
    for t in range(3, 12):
        probs[t, 0, :] = 0.0
        probs[t, 0, v3.SILENCE_CLASS] = 0.1
        probs[t, 0, 4] = 0.9
    for t in (7, 8):
        probs[t, 0, :] = 0.0
        probs[t, 0, v3.SILENCE_CLASS] = 0.55
        probs[t, 0, 4] = 0.45
    probs[14, 0, :] = 0.0
    probs[14, 0, v3.SILENCE_CLASS] = 0.1
    probs[14, 0, 9] = 0.9

    naive = np.argmax(probs, axis=-1).astype(np.int16)
    naive[naive == v3.SILENCE_CLASS] = -1
    decoded = v3.decode_with_hysteresis(probs)
    if v3.count_active_runs(decoded) >= v3.count_active_runs(naive):
        raise RuntimeError("V3 temporal decoder did not reduce synthetic fragmentation")
    if not np.all(decoded[3:12, 0] == 4):
        raise RuntimeError("V3 temporal decoder failed to preserve/restore synthetic true run")
    if decoded[14, 0] != -1:
        raise RuntimeError("V3 temporal decoder failed to suppress synthetic singleton")
    print("V3_DECODER_SELF_TEST_PASS")


def content_balance_self_test():
    weights = v3.bounded_content_weights({
        "chords": 20,
        "scales": 20,
        "singlenotes": 4,
        "PalmMute": 1,
    })
    if not weights["PalmMute"] > weights["chords"]:
        raise RuntimeError("rare PalmMute class did not receive stronger bounded supervision")
    if not weights["singlenotes"] > weights["chords"]:
        raise RuntimeError("rare singlenote class did not receive stronger bounded supervision")
    if any(not (v3.CONTENT_WEIGHT_MIN <= w <= v3.CONTENT_WEIGHT_MAX) for w in weights.values()):
        raise RuntimeError("content weight escaped frozen bounds")
    print("V3_CONTENT_BALANCE_SELF_TEST_PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    args = parser.parse_args()

    objective_self_test(args.source_root)
    resume_self_test(args.source_root)
    decoder_self_test()
    content_balance_self_test()
    print("GUITAR_TECHS_P3_OPENED=false")
    print("OPTIMIZER_STEPS_AUTHORIZED=0")
    print("CUSTOMER_DELIVERY_ELIGIBLE=false")


if __name__ == "__main__":
    main()
