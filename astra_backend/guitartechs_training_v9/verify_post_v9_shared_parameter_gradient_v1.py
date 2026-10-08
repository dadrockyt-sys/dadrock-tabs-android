#!/usr/bin/env python3
"""Prospective no-media V9 shared-parameter gradient audit. Never train or load checkpoints."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import torch

from guitartechs_training_v9.model import TemporalTabCNNV9
from guitartechs_training_v9.paired_view import paired_tensor_views, symmetric_kl_consistency
from guitartechs_training_v7.objective_decoder import v7_sequence_loss
from guitartechs_training_v9.verify_post_v9_synthetic_objective_audit_v1 import make_labels

SEED = 20261008
B, T, S, C = 1, 200, 6, 21
CONTENT_WEIGHT = 1.125
FROZEN_KL_WEIGHT = 0.10
COMPONENT_WEIGHTS = {
    "stateCE": 1.0, "continuity": 0.10, "identityMargin": 0.25,
    "activity": 0.25, "pitch": 0.20, "eventRank": 0.60,
}
SCENARIOS = (
    ("eval_identical_zero_kl_control", False, False),
    ("train_identical_dropout_only", True, False),
    ("train_original_paired_augmentation", True, True),
)
GROUPS = ("conv", "acoustic", "temporal", "onset_head", "activity_head",
          "pitch_head", "event_head", "routing", "state_head")


def number(tensor):
    out = float(tensor.detach().cpu().item())
    if not math.isfinite(out):
        raise AssertionError("nonfinite scalar in synthetic diagnostic")
    return out


def fingerprint(model):
    digest = hashlib.sha256()
    for name, value in model.state_dict().items():
        tensor = value.detach().cpu().contiguous()
        digest.update(name.encode())
        digest.update(str(tuple(tensor.shape)).encode())
        digest.update(tensor.numpy().tobytes())
    return digest.hexdigest()


def make_synthetic_features():
    # Precisely 1x200x1x192x9. These are invented abstract feature values.
    frame = torch.arange(T, dtype=torch.float32).view(1, T, 1, 1, 1)
    freq = torch.arange(192, dtype=torch.float32).view(1, 1, 1, 192, 1)
    win = torch.arange(9, dtype=torch.float32).view(1, 1, 1, 1, 9)
    data = 0.55 + 0.12 * torch.sin(0.08 * frame + 0.055 * freq) + 0.05 * torch.cos(0.17 * win + 0.01 * frame)
    assert data.shape == (B, T, 1, 192, 9)
    assert torch.isfinite(data).all()
    return data.contiguous()


def gradients(loss, params, retain):
    return torch.autograd.grad(loss, params, allow_unused=True, retain_graph=retain)


def gradient_stats(named, g_sup, g_kl):
    groups = {}
    combined_sq = [0.0, 0.0]
    for prefix in GROUPS:
        sq_sup = sq_kl = dot = 0.0
        count = 0
        for (name, p), sup, kl in zip(named, g_sup, g_kl):
            if not name.startswith(prefix + "."):
                continue
            count += p.numel()
            if sup is not None:
                sq_sup += float((sup.detach().double()**2).sum())
            if kl is not None:
                sq_kl += float((kl.detach().double()**2).sum())
            if sup is not None and kl is not None:
                dot += float((sup.detach().double() * kl.detach().double()).sum())
        a, b = math.sqrt(sq_sup), math.sqrt(sq_kl)
        if count == 0:
            raise AssertionError("missing frozen model parameter group: " + prefix)
        if not all(map(math.isfinite, (a, b, dot))):
            raise AssertionError("nonfinite parameter-gradient measurement")
        combined_sq[0] += sq_sup
        combined_sq[1] += sq_kl
        groups[prefix] = {
            "parameterCount": count,
            "supervisedGradientL2": a,
            "weightedOriginalKLGradientL2": b,
            "weightedPerPositionKLGradientL2Counterfactual": b/(T*S),
            "originalKLToSupervisedGradientNormRatio": b/a if a else None,
            "normalizedKLToSupervisedGradientNormRatioCounterfactual": b/(T*S*a) if a else None,
            "supervisedVsKLGradientCosine": dot/(a*b) if a > 0 and b > 0 else None,
        }
    total_param_count = sum(p.numel() for _, p in named)
    if sum(x["parameterCount"] for x in groups.values()) != total_param_count:
        raise AssertionError("model parameter groups not exhaustive")
    return {
        "parameterCount": total_param_count,
        "groups": groups,
        "totalSupervisedGradientL2": math.sqrt(combined_sq[0]),
        "totalWeightedOriginalKLGradientL2": math.sqrt(combined_sq[1]),
        "totalOriginalKLToSupervisedGradientNormRatio": (
            math.sqrt(combined_sq[1]/combined_sq[0]) if combined_sq[0] else None
        ),
    }


def scenario(model, input_features, labels, name, train_mode, augment):
    model.train(train_mode)
    # Control training-mode dropout randomness; no seed search or adaptive selection.
    torch.manual_seed(SEED + {"eval_identical_zero_kl_control": 0,
                              "train_identical_dropout_only": 1,
                              "train_original_paired_augmentation": 2}[name])
    if augment:
        first, second = paired_tensor_views(input_features, SEED)
    else:
        first, second = input_features.clone(), input_features.clone()
    if augment and torch.equal(first, second):
        raise AssertionError("frozen paired views unexpectedly identical")
    output_a = model(first)
    output_b = model(second)
    loss_a, parts_a = v7_sequence_loss(output_a, labels, content_weight=CONTENT_WEIGHT)
    loss_b, parts_b = v7_sequence_loss(output_b, labels, content_weight=CONTENT_WEIGHT)
    for loss, parts in ((loss_a, parts_a), (loss_b, parts_b)):
        reconstructed = CONTENT_WEIGHT * sum(parts[k]*v for k, v in COMPONENT_WEIGHTS.items())
        if not torch.allclose(loss, reconstructed, atol=2e-5, rtol=2e-5):
            raise AssertionError("V7 supervised component sum mismatch")
    supervision = 0.5*(loss_a + loss_b)
    logits_a = output_a["tablature"].reshape(B,T,S,C)
    logits_b = output_b["tablature"].reshape(B,T,S,C)
    raw_kl = symmetric_kl_consistency(logits_a, logits_b)
    weighted_kl = FROZEN_KL_WEIGHT*raw_kl
    total = supervision + weighted_kl

    named = list(model.named_parameters())
    params = tuple(p for _, p in named)
    grad_sup = gradients(supervision, params, retain=True)
    grad_kl = gradients(weighted_kl, params, retain=True)
    # Compare true composite derivative for a frozen named trunk/state subset.
    selected_indices = [
        i for i, (n, _) in enumerate(named)
        if n in ("conv.0.weight", "acoustic.0.weight", "temporal.weight_ih_l0", "state_head.weight")
    ]
    if len(selected_indices) != 4:
        raise AssertionError("expected four original shared-parameter tensors")
    grad_total = gradients(total, tuple(params[i] for i in selected_indices), retain=False)
    for i, gt in zip(selected_indices, grad_total):
        expected = (grad_sup[i] if grad_sup[i] is not None else torch.zeros_like(params[i]))
        expected = expected + (grad_kl[i] if grad_kl[i] is not None else torch.zeros_like(params[i]))
        if gt is None or not torch.allclose(expected, gt, atol=1e-5, rtol=1e-4):
            raise AssertionError("shared-parameter gradient additivity failed")

    stats = gradient_stats(named, grad_sup, grad_kl)
    loss_components = {
        k: number(0.5*(parts_a[k]+parts_b[k])) for k in COMPONENT_WEIGHTS
    }
    if name == "eval_identical_zero_kl_control":
        if abs(number(raw_kl)) > 1e-3 or stats["totalWeightedOriginalKLGradientL2"] > 1e-3:
            raise AssertionError("identical deterministic model input should have no KL gradient")
    return {
        "name": name,
        "trainingMode": train_mode,
        "augmentation": "frozen_v9_two_view" if augment else "same_synthetic_input",
        "supervisedLoss": number(supervision),
        "supervisedPartsMeanBeforeContentWeight": loss_components,
        "symmetricBatchmeanKL": number(raw_kl),
        "meanPerPositionKL": number(raw_kl)/(T*S),
        "weightedOriginalKL": number(weighted_kl),
        "weightedPerPositionKLCounterfactual": number(weighted_kl)/(T*S),
        "totalOriginalCompositeLoss": number(total),
        "sharedParameterGradients": stats,
        "gradientAdditivityFourSelectedParametersPassed": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(SEED)
    model = TemporalTabCNNV9(args.source_root)
    assert model.training is True
    before = fingerprint(model)
    inputs = make_synthetic_features()
    copied = inputs.clone()
    labels = make_labels()
    assert labels.shape == (B,S,T)
    assert int((labels>=0).sum()) > 0 and int((labels==-1).sum()) > 0
    assert int((labels==-100).sum()) > 0

    scenarios = []
    for name, mode, augment in SCENARIOS:
        scenarios.append(scenario(model, inputs, labels, name, mode, augment))
        print("POST_V9_SHARED_GRADIENT_SCENARIO=" + json.dumps({
            "name": name, "supervised": scenarios[-1]["supervisedLoss"],
            "originalWeightedKL": scenarios[-1]["weightedOriginalKL"],
            "trunkAcousticKLRatio": scenarios[-1]["sharedParameterGradients"]["groups"]["acoustic"]["originalKLToSupervisedGradientNormRatio"],
            "trunkTemporalKLRatio": scenarios[-1]["sharedParameterGradients"]["groups"]["temporal"]["originalKLToSupervisedGradientNormRatio"],
        }, sort_keys=True), flush=True)
    if fingerprint(model) != before:
        raise AssertionError("synthetic model weights changed despite zero optimizer steps")
    if not torch.equal(inputs, copied):
        raise AssertionError("input source feature mutated")
    report = {
        "schema": "astra-guitar-techs-post-v9-synthetic-shared-network-gradient-audit-v1",
        "date": "2026-10-08",
        "model": "untrained_exact_TemporalTabCNNV9",
        "syntheticInitializationSha256": before,
        "frozenInputDimensions": {"B":B,"T":T,"channel":1,"frequency":192,"window":9,"strings":S,"classes":C},
        "seed": SEED,
        "contentWeight": CONTENT_WEIGHT,
        "originalConsistencyWeight": FROZEN_KL_WEIGHT,
        "batchmeanToPerPositionFactor": T*S,
        "optimizerSteps": 0,
        "scenarios": scenarios,
        "guards": {
            "mediaAccess": False, "realLabels": False, "checkpointsOpened": False,
            "weightsModified": False, "weightsExported": False,
            "p3Opened": False, "protectedSongUsed": False,
            "stageBHoldoutUsed": False, "paidComputeUsed": False,
            "mainOrProductionModified": False,
        },
        "limits": [
            "All gradients are for an untrained randomly initialized network on artificial features/labels.",
            "Training-mode dropout may generate KL gradients even from identical features.",
            "Counterfactual per-position normalization is arithmetic only, not a trained candidate.",
            "Neither observed synthetic gradient dominance nor absence proves causality for prior V9 failure."
        ]
    }
    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print("POST_V9_SYNTHETIC_SHARED_PARAMETER_AUDIT_PASS", flush=True)


if __name__ == "__main__":
    main()
