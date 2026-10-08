#!/usr/bin/env python3
"""Post-V9 exact-loss synthetic audit: no audio, model, reference, or optimization."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import torch

from guitartechs_training_v7.objective_decoder import v7_sequence_loss
from guitartechs_training_v9.paired_view import (
    FROZEN_CONFIG, make_tensor_training_view, symmetric_kl_consistency,
)

SEED = 20261008
B, T, S, C = 1, 200, 6, 21
KL_WEIGHT = 0.10
CONTENT_WEIGHT = 1.125
SPANS = (0.0, 0.05, 0.25, 0.75)
COMPONENT_WEIGHTS = {
    "stateCE": 1.0, "continuity": 0.10, "identityMargin": 0.25,
    "activity": 0.25, "pitch": 0.20, "eventRank": 0.60,
}


def make_labels():
    labels = torch.full((B, S, T), -1, dtype=torch.long)
    for s, st, end, fret in (
        (0, 4, 10, 3), (1, 24, 38, 5), (2, 56, 70, 7),
        (3, 94, 109, 4), (4, 137, 151, 1), (5, 174, 189, 2),
    ):
        labels[:, s, st:end] = fret
    labels[:, 1, 110:114] = -100
    labels[:, 0, 184:187] = -100
    return labels


def make_output(state_logits, generator):
    return {
        "tablature": state_logits.reshape(B, T, S*C),
        "activity": (0.15*torch.randn((B, T, S), generator=generator)).requires_grad_(),
        "pitch": (0.15*torch.randn((B, T, 44), generator=generator)).requires_grad_(),
        "event": (0.15*torch.randn((B, T, S), generator=generator)).requires_grad_(),
    }


def scalar(x):
    value = float(x.detach().cpu().item())
    if not math.isfinite(value):
        raise AssertionError("nonfinite audit measurement")
    return value


def paired_norm(pair):
    return scalar(torch.sqrt(sum(g.detach().square().sum() for g in pair)))


def verify_feature_units():
    assert FROZEN_CONFIG.gain_db_max_abs == 3.0
    assert FROZEN_CONFIG.tilt_db_per_octave_max_abs == 1.5
    # Frozen preprocessing is relative amplitude_dB/80 + 1. For a feature
    # value of .5, multiplying by linear +3dB gain is NOT a 3/80 additive
    # feature-coordinate increment. Relative-to-maximum dB has additional
    # normalization caveats; this is an algebraic comparison, not audio.
    original = 0.5
    multiplied = original*(10**(3/20))
    additive = original + 3/80
    assert abs(multiplied-additive) > 0.1
    # 192 monotone bins at 24 bins per octave span 191/24 octaves.
    # V9 'tilt_db_per_octave' parameter actually spans +/- tilt dB on
    # normalized endpoints, i.e. 2*tilt across nearly eight octaves.
    implied_tilt_db_per_octave = (2*FROZEN_CONFIG.tilt_db_per_octave_max_abs)/(191/24)
    assert not math.isclose(implied_tilt_db_per_octave, FROZEN_CONFIG.tilt_db_per_octave_max_abs)

    x = torch.linspace(0., 1., 192).reshape(1, 1, 1, 192, 1).expand(B, T, 1, 192, 9).clone()
    before = x.clone()
    view1 = make_tensor_training_view(x, seed=20261008)
    view2 = make_tensor_training_view(x, seed=20261008)
    assert torch.equal(view1, view2), "same seed must yield same tensor view"
    assert torch.equal(x, before), "input must not mutate"
    assert view1.shape == x.shape and torch.isfinite(view1).all()
    # A constant synthetic source is redundantly represented at
    # (window t, center) and (window t+1, offset 3). V9 window-level
    # independent noise/masking generally does not tie these values.
    mismatch = torch.count_nonzero(view1[:, :-1, :, :, 4] != view1[:, 1:, :, :, 3]).item()
    assert mismatch > 0
    return {
        "preprocessedFeatureExample": original,
        "featureMultiplierAtPlus3dB": multiplied,
        "hypotheticalPlus3dBFeatureAddend": additive,
        "impliedMaximumTiltDbPerOctave": implied_tilt_db_per_octave,
        "repeatedSourceFrameWindowMismatches": int(mismatch),
        "nonmutatingDeterministicAugmentation": True,
        "note": "Algebraic feature-space observations, not physical audio validation.",
    }


def audit_scenario(span, labels):
    generator = torch.Generator(device="cpu").manual_seed(SEED)
    shared = torch.randn((B, T, S, C), generator=generator)*0.17
    shared[..., C-1] += 0.25
    direction = torch.randn((B, T, S, C), generator=generator)
    a = (shared + 0.5*span*direction).detach().requires_grad_()
    b = (shared - 0.5*span*direction).detach().requires_grad_()
    out_a = make_output(a, generator)
    out_b = make_output(b, generator)

    sup_a, parts_a = v7_sequence_loss(out_a, labels, content_weight=CONTENT_WEIGHT)
    sup_b, parts_b = v7_sequence_loss(out_b, labels, content_weight=CONTENT_WEIGHT)
    for supervised, parts in ((sup_a, parts_a), (sup_b, parts_b)):
        reconstructed = CONTENT_WEIGHT * sum(
            parts[k]*weight for k, weight in COMPONENT_WEIGHTS.items()
        )
        assert torch.allclose(supervised, reconstructed, rtol=2e-5, atol=2e-5)

    supervised = 0.5 * (sup_a+sup_b)
    raw_kl = symmetric_kl_consistency(a, b)
    weighted_kl = KL_WEIGHT*raw_kl
    per_position_kl = raw_kl/(T*S)
    composite = supervised+weighted_kl

    grad_supervised = torch.autograd.grad(supervised, (a, b), retain_graph=True)
    grad_kl = torch.autograd.grad(weighted_kl, (a, b), retain_graph=True)
    grad_composite = torch.autograd.grad(composite, (a, b), retain_graph=True)
    for i in range(2):
        assert torch.allclose(
            grad_supervised[i]+grad_kl[i], grad_composite[i],
            rtol=2e-5, atol=2e-5)
    super_norm = paired_norm(grad_supervised)
    kl_norm = paired_norm(grad_kl)
    composite_norm = paired_norm(grad_composite)
    supervised_parts = {
        key: scalar(0.5*(parts_a[key]+parts_b[key])) for key in COMPONENT_WEIGHTS
    }
    if span > 0:
        assert math.isclose(
            scalar(raw_kl), (T*S)*scalar(per_position_kl),
            rel_tol=1e-5, abs_tol=1e-5)
        assert scalar(raw_kl) > 0

    return {
        "syntheticPairedLogitDifferenceScale": span,
        "supervisedMean": scalar(supervised),
        "supervisedPartsUnweighted": supervised_parts,
        "consistencySymmetricBatchmean": scalar(raw_kl),
        "perPositionMeanKL": scalar(per_position_kl),
        "weightedConsistency": scalar(weighted_kl),
        "weightedConsistencyIfPerPositionMeanDiagnosticOnly": KL_WEIGHT*scalar(per_position_kl),
        "totalComposite": scalar(composite),
        "stateLogitGradientNormSupervised": super_norm,
        "stateLogitGradientNormWeightedKL": kl_norm,
        "stateLogitGradientNormComposite": composite_norm,
        "stateLogitKLToSupervisedGradientNormRatio": kl_norm/super_norm if super_norm else None,
        "stateLogitKLToSupervisedLossMagnitudeRatio": (
            scalar(weighted_kl)/scalar(supervised) if scalar(supervised) else None),
        "gradientAdditivityProven": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    torch.set_num_threads(1)
    torch.manual_seed(SEED)
    labels = make_labels()
    assert labels.shape == (B,S,T)
    report = {
        "schema": "astra-post-v9-synthetic-objective-unit-gradient-audit-v1",
        "source": "Frozen v7_sequence_loss + symmetric_kl_consistency; V9 trainer composition unchanged",
        "syntheticSeed": SEED,
        "frozenDimensions": {"B": B, "T": T, "S": S, "C": C},
        "frozenConsistencyWeight": KL_WEIGHT,
        "illustrativeContentWeight": CONTENT_WEIGHT,
        "batchmeanToPerPositionMeanFactor": T*S,
        "weightedBatchmeanToPerPositionMeanFactor": KL_WEIGHT*T*S,
        "optimizerSteps": 0,
        "mediaAccess": False,
        "checkpointAccess": False,
        "features": verify_feature_units(),
        "scenarios": [audit_scenario(d, labels) for d in SPANS],
        "guards": {
            "noRealData": True, "noModelInstantiation": True,
            "noOptimizer": True, "noStageB": True, "noP3": True,
            "noProtectedSong": True, "noMainOrProductionMutation": True,
        },
        "interpretation": "Proves numerical scaling and gradient influence on fixed synthetic independent logits only. These are not V9 training model-parameter gradients, learned hidden representations, or causal attribution of the completed V9 failure.",
    }
    assert report["batchmeanToPerPositionMeanFactor"] == 1200
    assert report["weightedBatchmeanToPerPositionMeanFactor"] == 120
    assert len(report["scenarios"]) == 4
    target = Path(args.out)
    target.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print("POST_V9_SYNTHETIC_OBJECTIVE_AUDIT_PASS")
    print("SCENARIO_SUMMARY=" + json.dumps([{
        "span": row["syntheticPairedLogitDifferenceScale"],
        "supervised": row["supervisedMean"],
        "weightedKL": row["weightedConsistency"],
        "stateLogitGradientRatio": row["stateLogitKLToSupervisedGradientNormRatio"],
    } for row in report["scenarios"]], sort_keys=True))
    print("RESULT_JSON="+str(target))


if __name__ == "__main__":
    main()
