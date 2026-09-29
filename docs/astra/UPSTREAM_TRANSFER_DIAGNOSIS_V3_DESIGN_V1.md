# V3 Upstream Transfer Diagnosis Design V1

Date: 2026-09-28  
Status: **DESIGN FROZEN — EMPIRICAL EXECUTION NOT YET AUTHORIZED**

## Purpose

V2C showed that lowering state/onset thresholds does not restore meaningful real-guitar admission and substantially increases false positives. The next diagnostic question is therefore upstream of calibration:

> Does the transfer failure primarily arise because real-audio frontend features occupy a materially different distribution from the synthetic training features, or because the frozen model representation fails even when feature statistics are brought into synthetic-like range?

This V3 project is designed to separate those explanations without tuning on the sealed V1.1 evaluation set.

## Data roles

### Sealed evaluation evidence

V1.1 remains sealed. It may not be used for feature normalization fitting, threshold selection, frontend tuning, representation tuning, or candidate selection.

### Calibration-development evidence

V2B may be used only for the bounded diagnostic measurements explicitly frozen here.

No new model training is authorized by this design.

## V3A — frontend distribution audit

Using the exact frozen frontend math, compute for:
- historical synthetic training/evaluation arrays already present in the project;
- V2B real calibration clips.

Compare, without changing the frontend:
- per-CQT-bin mean;
- per-CQT-bin standard deviation;
- robust median and MAD;
- zero / floor occupancy;
- dynamic-range percentiles;
- framewise L2 norm distribution;
- temporal-difference norm distribution;
- context-window norm distribution.

Report aggregate distances:
- standardized mean difference by bin;
- median absolute standardized difference;
- Wasserstein distance summaries;
- fraction of bins with |SMD| >= 1 and >= 2;
- global feature-range overlap.

No model inference is required for V3A.

## V3B — frozen affine diagnostic transforms

Only if V3A shows substantial real-vs-synthetic feature shift.

Prospectively define exactly three diagnostic transforms, fitted from **V2B and historical synthetic feature statistics only**:

1. **identity** — no change;
2. **global affine** — one scalar shift and scale applied to all feature bins;
3. **per-bin affine** — independent shift and scale per CQT bin.

Transforms may match real feature mean/std toward synthetic mean/std.

Hard rules:
- no clipping choices tuned from model output;
- no nonlinear transform search;
- no gain search;
- no threshold changes;
- no decoder changes;
- no use of V1.1 for transform fitting.

## V3C — representation probe

For each frozen transform, run the pinned S9 checkpoint on V2B at the historical 0.50/0.50 thresholds only.

Primary diagnostic outputs:
- trusted landmark joint-admission rate;
- state-only pass rate;
- onset-only pass rate;
- both-gates-fail rate;
- negative-only FP events/sec.

No threshold grid.

### Interpretation rule

A transform is diagnostically interesting only if all are true:
- trusted landmark joint-admission improves by at least **+0.20 absolute** over identity;
- at least **25%** of high-confidence landmarks pass jointly;
- negative-only FP rate remains <= **0.10 events/sec**.

This is not a product gate and does not authorize adoption.

If no transform meets those diagnostic conditions, conclude that simple first/second-moment frontend distribution alignment is insufficient to explain the transfer collapse.

## V3D — fresh holdout requirement

Even if a transform is diagnostically interesting on V2B, do not evaluate it on V1.1.

A fresh holdout set would be required before any claim of real-transfer improvement.

## Hard boundaries

Do not:
- train or fine-tune model weights;
- lower thresholds;
- modify decoder semantics;
- tune frontend parameters from V1.1;
- perform arbitrary normalization search;
- select transforms after inspecting V1.1;
- open P1/P2/P3;
- open A2;
- mutate main/Production.

## Exact next action

If V3 empirical work is explicitly authorized:
1. run V3A frontend distribution audit first;
2. freeze its result;
3. only if substantial shift is observed, instantiate the three already-declared V3B transforms;
4. run V3C once;
5. freeze result and stop.

Generic continuation does not authorize V3 empirical execution.
