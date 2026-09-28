# Astra source-domain joint-coverage protocol V2

Date: 2026-09-28  
Status: **DESIGN ONLY — NO DATASET RENDER / NO MODEL EXECUTION**

## Purpose

Define an independent next-generation source-domain sampling protocol after V1 established a joint-coverage limitation.

This is **not a rescue of V1**. V1 remains failed and frozen.

V2 keeps every V1 marginal source-domain parameter range and distribution unchanged. The only proposed change is the deterministic **joint sampling design** used to assign source-domain parameters to synthetic rows.

No V1 model score is used to choose any range, threshold, architecture, loss, sampler or decoder setting.

## Frozen marginal priors — unchanged from V1

Continuous clip-level axes:
- attack base rise: log-uniform 0.0015 .. 0.050 s
- transient noise gain: uniform 0.00 .. 0.20
- transient decay: log-uniform 0.003 .. 0.020 s
- damping multiplier: log-uniform 0.60 .. 1.80
- brightness: uniform 0.55 .. 0.92
- pick position: uniform 0.08 .. 0.48
- low-pass cutoff: log-uniform 2800 .. 12000 Hz
- spectral tilt: uniform -6 .. +6 dB
- high-pass corner: uniform 20 .. 80 Hz
- nonlinear drive: uniform 1.0 .. 2.5
- nonlinear wet: uniform 0.00 .. 0.30
- broadband noise RMS relative: log-uniform 1e-5 .. 3e-3

Categorical/boolean priors:
- nonlinear active probability 0.50
- hum active probability 0.35
- hum fundamental 50/60 Hz equiprobable when represented

Per-note V1 distributions remain unchanged:
- attack-rise multiplier log-uniform 0.75 .. 1.35, clipped with final rise 0.001 .. 0.060 s
- damping multiplier log-uniform 0.85 .. 1.20
- amplitude log-normal sigma 0.18, clipped 0.55 .. 1.60

## V2 training coverage design

Keep the same **210 training rows: exactly 30 per musical family**.

For each family independently and each continuous clip-level axis:

1. create the 30 fixed quantile midpoints:
   `u_k = (k + 0.5) / 30`, k=0..29;
2. generate one deterministic SHA-256-seeded permutation of the 30 strata using namespace:
   `astra-source-domain-joint-v2|train|<family>|<axis>`;
3. assign the permuted `u_k` values one-to-one to the 30 family rows;
4. map each `u` through the exact V1 inverse CDF for that axis.

This is a deterministic Latin-hypercube-style construction:
- every family covers every marginal stratum exactly once per continuous axis;
- joint pairings are determined independently by named SHA-seeded permutations;
- no row is selected or modified using a model score.

### Boolean/categorical assignment

Use deterministic quantile/permutation assignments rather than Bernoulli draws:
- nonlinear active: exactly 15/30 rows per family;
- hum active: exactly 11/30 rows per family, the nearest upper integer representation of 0.35;
- hum fundamental: among active hum rows, 50/60 assignment differs by at most one row.

Assignment ordering is SHA-seeded with the same namespace plus the categorical axis name.

## Ordinary validation/test identity

Validation and ordinary test rows remain bit-identical to the frozen S9 control.

Labels, references, family, split and historical S9 metadata remain unchanged.

The historical fixed-width S9 training-chord string truncation is preserved byte-identically as before.

## Primary V2 held-out coverage challenge

The primary V2 source-domain challenge is a **held-out in-support space-filling challenge**, not the old V1 fixed corner.

There are exactly 42 test rows: six per family.

For each family and each continuous clip-level axis:
1. create six fixed quantile midpoints `u_k=(k+0.5)/6`;
2. independently permute them using namespace:
   `astra-source-domain-joint-v2|challenge|<family>|<axis>`;
3. map through the same unchanged V1 inverse CDF.

Categorical challenge assignments:
- nonlinear active: 3/6 rows per family;
- hum active: 2/6 rows per family;
- active hum 50/60 balanced 1/1 where possible.

Train and challenge use disjoint namespaces. Exact full parameter vectors must not duplicate.

This challenge asks whether training on systematic joint coverage generalizes to held-out combinations **inside the same prior support**.

## V1 fixed challenge retained as secondary stress diagnostic only

The original V1 fixed challenge profile remains frozen and may be evaluated later as a **secondary stress diagnostic**.

It must not:
- determine V2 pass/fail;
- be weakened;
- be used to select V2 parameter ranges;
- be used for threshold/model/seed selection.

This preserves continuity without retroactively changing the V1 experiment.

## Model-free V2 admission required before any training design

A future implementation must first prove:

1. exactly 30 training rows per family and six primary-challenge rows per family;
2. every continuous training axis occupies all 30 1/30 marginal strata exactly once within each family;
3. every continuous primary-challenge axis occupies all six 1/6 marginal strata exactly once within each family;
4. all mapped values stay inside the unchanged V1 ranges;
5. nonlinear/hum categorical counts match the fixed allocations;
6. no exact full parameter vector is shared between train and primary challenge;
7. deterministic reruns produce identical parameter manifests/hashes;
8. labels/references/splits are bit-identical to control;
9. no waveform/model work occurs during parameter-manifest admission;
10. historical S9 metadata remains preserved.

After parameter-manifest admission, waveform-level fixture and CQT admission must be separately frozen before training.

## Architecture boundary

No architecture change is part of V2 coverage protocol.

If V2 ever reaches a model experiment, the frozen S11 architecture would remain unchanged for that experiment so the only intervention is source-domain sampling/coverage.

Any architecture study must be separate and later.

## Execution boundary

This design authorizes:
- documentation;
- deterministic parameter-manifest implementation;
- model-free tests.

It does **not** authorize:
- waveform dataset rendering;
- optimizer steps;
- model loading/inference;
- threshold changes;
- P1/P2/P3 access;
- a training launch.

## Next action

Implement only the deterministic V2 parameter-manifest generator and its admission tests.

Do not render audio yet.
