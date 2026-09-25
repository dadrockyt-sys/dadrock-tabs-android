#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import random
import tempfile
from pathlib import Path

import numpy as np
import torch

from guitartechs_training_v2 import train_v2 as base
from guitartechs_training_v5.model import (
    NUM_CLASSES,
    NUM_PITCHES,
    NUM_STRINGS,
    TemporalTabCNNV5,
)
from guitartechs_training_v5.objective_decoder import (
    count_active_runs,
    decode_multitask,
    v5_sequence_loss,
)

SEED = 20260921


def setup():
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(4)


def clone_state(state):
    return {k: v.detach().cpu().clone() for k, v in state.items()}


def rng_state():
    return {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch": torch.get_rng_state().clone(),
    }


def restore_rng(state):
    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.set_rng_state(state["torch"])


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


def new_model(source_root):
    model = TemporalTabCNNV5(source_root)
    optimizer = torch.optim.Adadelta(model.parameters(), lr=1.0)
    return model, optimizer


def synthetic_batch():
    feat = np.random.RandomState(SEED).normal(0, 1, size=(192, 260)).astype(np.float32)
    windows = base.sequence_windows(feat, 20, 220)
    x = torch.from_numpy(windows[None, :, None, :, :])
    labels = np.random.RandomState(SEED + 1).randint(
        0,
        NUM_CLASSES,
        size=(1, NUM_STRINGS, 200),
        dtype=np.int64,
    )
    y = torch.from_numpy(labels)
    return x, y


def check_shapes_and_gradients(source_root):
    setup()
    model, _ = new_model(source_root)
    x, y = synthetic_batch()
    outputs = model(x)
    if outputs["tablature"].shape != (1, 200, NUM_STRINGS * NUM_CLASSES):
        raise RuntimeError("V5 tablature head shape mismatch")
    if outputs["onset"].shape != (1, 200, NUM_STRINGS):
        raise RuntimeError("V5 onset head shape mismatch")
    if outputs["activity"].shape != (1, 200, NUM_STRINGS):
        raise RuntimeError("V5 activity head shape mismatch")
    if outputs["pitch"].shape != (1, 200, NUM_PITCHES):
        raise RuntimeError("V5 pitch head shape mismatch")
    loss, parts = v5_sequence_loss(outputs, y, content_weight=1.0)
    if not torch.isfinite(loss):
        raise RuntimeError("V5 loss is non-finite")
    loss.backward()
    required = ("state", "onset", "activity", "pitch", "continuity", "identityMargin")
    for key in required:
        if not torch.isfinite(parts[key]):
            raise RuntimeError(f"V5 non-finite loss component: {key}")
    if model.onset_head.weight.grad is None or model.activity_head.weight.grad is None:
        raise RuntimeError("V5 auxiliary heads did not receive gradients")
    if model.pitch_head.weight.grad is None or model.state_head.weight.grad is None:
        raise RuntimeError("V5 pitch/state heads did not receive gradients")
    if model.task_log_vars.grad is None or not torch.all(torch.isfinite(model.task_log_vars.grad)):
        raise RuntimeError("V5 learned task weighting did not receive finite gradients")
    print("V5_FINITE_GRADIENT_PASS")


def check_temporal_context(source_root):
    setup()
    model, _ = new_model(source_root)
    model.eval()
    x, _ = synthetic_batch()
    a = x[:, :6].clone()
    b = a.clone()
    b[:, 0] = b[:, 0] + 0.25
    with torch.no_grad():
        out_a = model(a)["tablature"]
        out_b = model(b)["tablature"]
    # Same acoustic input at frame 1+, different prior frame. A causal temporal
    # model must allow the later state to depend on that history.
    difference = torch.max(torch.abs(out_a[:, 1] - out_b[:, 1])).item()
    if difference <= 1e-10:
        raise RuntimeError("V5 temporal head did not propagate prior-frame context")
    print("V5_TEMPORAL_CONTEXT_PASS")


def check_decoder():
    state = np.zeros((8, NUM_STRINGS, NUM_CLASSES), dtype=np.float64)
    state[..., 20] = 1.0
    onset = np.zeros((8, NUM_STRINGS), dtype=np.float64)
    activity = np.zeros((8, NUM_STRINGS), dtype=np.float64)
    for t in range(2, 7):
        state[t, 0, :] = 0.0
        state[t, 0, 20] = 0.10
        state[t, 0, 4] = 0.90
        activity[t, 0] = 0.90

    without_onset = decode_multitask(state, onset, activity)
    if count_active_runs(without_onset) != 0:
        raise RuntimeError("V5 decoder admitted state/activity evidence without onset")

    onset[2, 0] = 0.90
    with_onset = decode_multitask(state, onset, activity)
    if not np.all(with_onset[2:7, 0] == 4) or count_active_runs(with_onset) != 1:
        raise RuntimeError("V5 decoder failed onset-gated continuation")

    # A one-frame onset/state spike is still removed by the frozen minimum-run rule.
    spike_state = np.zeros((5, NUM_STRINGS, NUM_CLASSES), dtype=np.float64)
    spike_state[..., 20] = 1.0
    spike_onset = np.zeros((5, NUM_STRINGS), dtype=np.float64)
    spike_activity = np.zeros((5, NUM_STRINGS), dtype=np.float64)
    spike_state[2, 0, :] = 0.0
    spike_state[2, 0, 20] = 0.10
    spike_state[2, 0, 4] = 0.90
    spike_onset[2, 0] = 0.90
    spike_activity[2, 0] = 0.90
    spike = decode_multitask(spike_state, spike_onset, spike_activity)
    if count_active_runs(spike) != 0:
        raise RuntimeError("V5 decoder failed singleton suppression")
    print("V5_DECODER_SELF_TEST_PASS")


def check_resume(source_root):
    x, y = synthetic_batch()

    def step(model, optimizer):
        py_scale = random.random()
        np_scale = float(np.random.random())
        jitter = torch.rand_like(x) * 1e-5
        xx = x * (1.0 + (py_scale + np_scale) * 1e-6) + jitter
        optimizer.zero_grad(set_to_none=True)
        outputs = model(xx)
        loss, _ = v5_sequence_loss(outputs, y, content_weight=1.0)
        loss.backward()
        optimizer.step()

    setup()
    continuous, continuous_opt = new_model(source_root)
    for _ in range(4):
        step(continuous, continuous_opt)
    continuous_model = clone_state(continuous.state_dict())
    continuous_optimizer = copy.deepcopy(continuous_opt.state_dict())
    continuous_rng = rng_state()

    setup()
    split, split_opt = new_model(source_root)
    for _ in range(2):
        step(split, split_opt)

    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "v5-resume.pt"
        torch.save({
            "model": clone_state(split.state_dict()),
            "optimizer": split_opt.state_dict(),
            "rng": rng_state(),
        }, path)

        setup()
        resumed, resumed_opt = new_model(source_root)
        payload = torch.load(path, map_location="cpu")
        resumed.load_state_dict(payload["model"])
        resumed_opt.load_state_dict(payload["optimizer"])
        restore_rng(payload["rng"])
        for _ in range(2):
            step(resumed, resumed_opt)

    if not nested_equal(continuous_model, resumed.state_dict()):
        raise RuntimeError("V5 resumed model diverged")
    if not nested_equal(continuous_optimizer, resumed_opt.state_dict()):
        raise RuntimeError("V5 resumed optimizer diverged")
    if not nested_equal(continuous_rng, rng_state()):
        raise RuntimeError("V5 resumed RNG state diverged")
    print("V5_RESUME_SELF_TEST_PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    args = parser.parse_args()
    check_shapes_and_gradients(args.source_root)
    check_temporal_context(args.source_root)
    check_decoder()
    check_resume(args.source_root)
    print("V5_SYNTHETIC_VERIFICATION_PASS")


if __name__ == "__main__":
    main()
