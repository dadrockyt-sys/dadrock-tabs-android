# V4 Synthetic-to-Real Rendering Adequacy Design V1

Date: 2026-09-28  
Status: **DESIGN FROZEN — EMPIRICAL EXECUTION NOT YET AUTHORIZED**

## Why V4 exists

V2C ruled out a useful threshold-only rescue. V3 found a substantial synthetic-vs-real frontend distribution shift, but simple global/per-bin affine alignment recovered only 1/56 trusted landmarks and did not satisfy the negative false-positive constraint.

The next question is therefore narrower:

> Is the current synthetic renderer missing real-audio acoustic/timbral structure that the model needs in order to learn a transferable representation?

V4 tests rendering adequacy before considering fresh real-domain training.

## Data roles

- **V1.1:** sealed evaluation evidence; never used to fit or select V4 renderer variants.
- **V2B:** development/diagnostic data. It may be used for model-free renderer-distribution comparison and later bounded development-model evaluation.
- **P1/P2/P3:** closed.
- **Fresh V4 holdout:** required before any transfer-improvement claim.

## Frozen renderer families

Keep the original S9 note/chord/event templates, labels, split membership, sampling plan, model architecture, loss, optimizer, step count, thresholds, and decoder fixed.

Change only waveform rendering through exactly four declared arms:

### R0 — S9 baseline

Original S9 synthetic renderer unchanged.

### R1 — amplifier / cabinet coloration

Apply one fixed deterministic guitar-like coloration chain:
- pre-emphasis/high-pass below the useful guitar band;
- smooth mid emphasis;
- upper-frequency rolloff;
- soft saturation;
- no room/reverb.

Parameters are fixed prospectively and shared across all clips; no V2B-driven parameter search.

### R2 — room / capture variation

Start from R1 and add deterministic bounded capture variation:
- short early-reflection/reverb response;
- small microphone-position-style spectral tilt;
- low-level broadband recording noise.

Variant choice is deterministically paired to the existing synthetic variant index. No new label or split changes.

### R3 — full bounded realism package

Start from R2 and additionally add:
- deterministic mild dynamic compression;
- pick/transient-level variation;
- low-frequency hum/noise floor on a bounded subset;
- limited per-example output-level variation before the existing frozen RMS normalization.

No pitch shifting, time stretching, label jitter, new notes, or decoder/frontend changes.

## V4A — model-free renderer screen

For R0/R1/R2/R3, generate synthetic features under one common runtime and compare each arm against V2B using the already-defined V3A distribution metrics.

Primary model-free score:
1. median absolute SMD;
2. fraction of bins with |SMD| >= 1;
3. median Wasserstein distance;
4. median robust range overlap.

### Frozen model-free advancement rule

A non-baseline renderer may advance to training only if all are true relative to R0:
- median absolute SMD improves by at least **15%**;
- fraction |SMD| >=1 improves by at least **20% relative**;
- median Wasserstein distance improves by at least **10%**;
- median robust range overlap does not decline by more than **0.02 absolute**.

At most the **best two** non-baseline renderers may advance.

If none qualify, V4 stops before training.

Tie-break order:
1. lower median absolute SMD;
2. lower fraction |SMD| >=1;
3. lower median Wasserstein;
4. higher range overlap;
5. lower renderer complexity (R1 before R2 before R3).

## V4B — bounded synthetic retraining

Only if V4A advances one or two renderers.

Train:
- one R0 baseline reproduction;
- each advancing renderer arm;
- maximum **3 total models**.

Freeze:
- same S9 model architecture;
- same initialization policy;
- same training sampler;
- same optimizer;
- same 500 optimizer steps/model;
- same state/onset loss;
- same 0.50/0.50 thresholds;
- same decoder.

Maximum optimizer work: **1500 total steps**.

No threshold search or model retry.

## V4C — V2B development transfer test

Evaluate R0 and advancing renderer-trained models on V2B only.

Primary metrics:
- high+medium trusted pitch-landmark joint hit rate;
- high-confidence landmark joint hit rate;
- negative-only FP events/sec.

A renderer-trained model is **development-interesting** only if, versus R0 trained in the same run:
- trusted joint hit-rate gain >= **+0.20 absolute**;
- high-confidence joint hit rate >= **25%**;
- negative FP <= **0.10 events/sec**.

No V1.1 access.

If none pass, stop.

## V4D — fresh holdout

If and only if a renderer passes V4C:
- collect a fresh real-audio holdout prospectively;
- do not tune after seeing it;
- confirm the frozen V4C-selected renderer/model exactly once.

V1.1 remains sealed and is not repurposed as the confirmation set.

## Scientific interpretation

V4 can support:
- whether added synthetic rendering realism moves frontend distributions toward real development audio;
- whether that renderer change improves V2B transfer under fixed model/training/decoder conditions.

V4 cannot by itself prove:
- production readiness;
- general real-world accuracy;
- that rendering realism is the only remaining cause;
- that any specific acoustic effect is causal unless isolated in a later experiment.

## Hard boundaries

Do not:
- fit renderer parameters by arbitrary search against V2B;
- use V1.1 for renderer selection;
- add real audio to training;
- change model architecture;
- change thresholds or decoder;
- exceed 3 trained models / 1500 optimizer steps;
- open P1/P2/P3;
- open A2;
- mutate main/Production.

## Exact next action

If V4 empirical execution is explicitly authorized:
1. implement the four renderer arms and deterministic identity checks;
2. run V4A only;
3. freeze V4A result;
4. continue to V4B/V4C only if the frozen advancement rule is met;
5. freeze result and stop before any fresh holdout collection.

Generic continuation does not authorize empirical V4 execution.
