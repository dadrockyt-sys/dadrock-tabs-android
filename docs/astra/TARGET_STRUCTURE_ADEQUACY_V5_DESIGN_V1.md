# V5 Target-Structure Adequacy Design V1

Date: 2026-09-28  
Status: **DESIGN FROZEN — EMPIRICAL EXECUTION NOT YET AUTHORIZED**

## Why V5 exists

V4 showed that the R3 renderer materially improves synthetic-vs-real frontend similarity and lowers negative false positives after retraining, yet it restores **0/56 trusted V2B pitch landmarks**.

That leaves a narrower hypothesis:

> The frozen model may be learning an overly specific string/fret assignment task whose supervision is poorly aligned with the real-domain evidence, even when the underlying pitch is correct.

V5 tests that hypothesis while holding architecture and parameter count fixed.

## Core causal isolation

Do **not** change:
- encoder architecture;
- state-head architecture;
- onset-head architecture;
- parameter count;
- initialization;
- R3 renderer;
- synthetic examples;
- train/validation/test membership;
- sampler;
- batch indices;
- optimizer;
- learning rate;
- optimizer steps;
- onset loss;
- thresholds;
- decoder for the baseline arm.

Change only the **state supervision/objective**.

## Frozen arms

### T0 — exact-string/fret baseline

Same R3 synthetic dataset and frozen S9/S6-style model.

State objective remains the historical per-string exact-fret classification:
- each string predicts one of 20 frets or silence;
- only the labeled string/fret is treated as correct.

### T1 — pitch-equivalent state objective

Use the **same 6 x 21 state logits** and the same onset logits.

For each active synthetic target pitch on a frame:
- compute the set of all physically representable string/fret positions that yield that MIDI pitch;
- aggregate state probability across those compatible positions;
- reward the model when probability mass is assigned to **any compatible position**, rather than only the renderer's original labeled string.

For inactive pitches / silence:
- retain explicit suppression of unsupported active states.

The purpose is to relax string identity while preserving pitch identity.

No output units are added or removed.

### T2 — mixed exact + pitch-equivalent objective

Same architecture and outputs.

State loss is frozen prospectively as:
- **50% exact-string/fret state loss**
- **50% pitch-equivalent state loss**

This tests whether preserving some string specificity while allowing pitch-equivalent representations transfers better.

No weight search is allowed; 50/50 is the only mixed weighting.

## V5A — objective identity and synthetic sanity

Before real-domain evaluation:
1. verify T0/T1/T2 have identical model parameter tensors before optimization;
2. verify identical R3 feature arrays, targets, split arrays, and batch indices;
3. verify exactly 500 optimizer steps per arm;
4. verify all losses remain finite;
5. evaluate the frozen synthetic test set.

Synthetic sanity rule:
- T1/T2 may not lose more than **0.10 absolute pitch-onset F1** versus T0;
- onset recall may not decline by more than **0.10 absolute**;
- negative-only synthetic FP rate must remain <= **0.10 events/s**.

An arm failing synthetic sanity is not eligible for V2B evaluation.

## V5B — V2B pitch-transfer development test

Evaluate eligible arms on V2B at frozen state/onset thresholds **0.50 / 0.50**.

For T1/T2 real pitch-landmark scoring:
- a trusted landmark passes state admission if the aggregate probability of any physically compatible string/fret position for that pitch is >= 0.50;
- onset admission uses the maximum onset probability among compatible string positions and the frozen 0.50 onset threshold;
- joint admission requires both.

This diagnostic scorer does **not** alter production decoding.

Primary metrics:
- trusted high+medium joint-admission rate;
- high-confidence joint-admission rate;
- state-admission rate;
- onset-admission rate;
- negative-only decoded FP events/sec using the ordinary decoder.

## Frozen development-interest gate

T1 or T2 is development-interesting only if, versus same-run T0:
- trusted joint-admission gain >= **+0.20 absolute**;
- high-confidence joint-admission >= **25%**;
- negative-only decoded FP <= **0.10 events/sec**;
- onset-admission does not decline by more than **0.10 absolute**.

If neither T1 nor T2 passes, V5 stops.

## Interpretation

If T1/T2 materially improve V2B pitch admission while architecture, renderer, data, batches, and parameter count are fixed, that supports the narrower conclusion that **exact string/fret target structure contributes to the transfer failure**.

It does not prove:
- production readiness;
- correct string assignment;
- general real-world transcription accuracy;
- that target structure is the only remaining cause.

If T1/T2 do not improve transfer, the evidence shifts further toward representation/data-task inadequacy beyond simple string-assignment specificity.

## V5C — fresh confirmation requirement

Any V5B success requires a fresh prospectively collected holdout before adoption or broader claims.

Do not use V1.1 as the confirmation set.

## Compute ceiling

Exactly three training arms maximum:
- T0
- T1
- T2

Maximum:
- **500 optimizer steps per arm**
- **1500 optimizer steps total**
- no retries
- no additional loss weights
- no threshold search.

## Hard boundaries

Do not:
- alter architecture or parameter count;
- change renderer beyond frozen R3;
- change thresholds;
- change production decoder;
- search objective weights;
- add real audio to training;
- use V1.1 for selection;
- open P1/P2/P3;
- open A2;
- mutate main/Production.

## Exact next action

If V5 empirical execution is explicitly authorized:
1. implement the pitch-equivalent loss and diagnostic scorer;
2. add focused identity/math tests;
3. freeze source hashes;
4. train T0/T1/T2 once, max 500 steps each;
5. apply V5A synthetic sanity;
6. evaluate only sanity-eligible arms on V2B;
7. freeze result and stop before fresh holdout collection.

Generic continuation does not authorize empirical V5 execution.
