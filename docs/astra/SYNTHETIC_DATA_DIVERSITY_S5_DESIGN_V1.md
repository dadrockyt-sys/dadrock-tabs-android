# Astra synthetic data diversity S5 design V1

Date: 2026-09-27
Status: **DESIGN FROZEN — NOT AUTHORIZED FOR MODEL EXECUTION**

## Question

With the successful onset-aware sampler and standard shared multitask encoder retained, does a modest increase in active-state token weight from 6 to 9 improve state/joint admission and event-level recall without unacceptable precision or onset degradation?

## Motivation

S2 showed that increasing active-state weight from 1.5 to 6 improved state/joint admission and event metrics.

S3 and S4 did not support onset-side escalation or full onset-gradient detachment as the next remedy.

Under the frozen sampler, active state tokens are about 10.4414% of state tokens:
- weight 6 -> about 41.16% expected weighted state-loss mass;
- weight 9 -> about 51.20%.

Weight 9 is the smallest integer weight above the approximate equal-mass crossover (8.58).

## Fixed data

If explicitly authorized:
- deterministic synthetic corpus only;
- root seed 20260927;
- 98 template identities x 3 variants = 294 clips;
- 588 seconds;
- train/validation/test 210 / 42 / 42;
- 22.05 kHz, 192-bin frozen CQT;
- no external audio assets;
- no P1/P2/P3.

The synthetic test split is development evidence, not an untouched holdout.

Before optimizer work:
- freeze uncompressed array hashes;
- precompute one 500-minibatch plan;
- use identical minibatches for both arms;
- assert identical initial parameter tensors and pre-update logits.

## Models

Exactly two identical five-frame models:

5 x 192 -> Linear(960,128) -> ReLU -> state head + onset head.

Both arms:
- ordinary shared multitask backpropagation;
- onset-aware 32/32/32/32 sampler;
- onset BCE pos_weight **8.0**;
- onset loss multiplier **4.0**;
- Adam lr **0.003**;
- batch size **128**;
- exactly **500 optimizer steps**;
- state threshold **0.50**;
- onset threshold **0.50**;
- decoder V2;
- no threshold search or retuning.

Only changed variable:
- control active-state weight **6.0**;
- intervention active-state weight **9.0**.

## Required measurements

For validation and test:
- pitch-onset TP/FP/FN, precision, recall, F1;
- pitch-onset+offset F1;
- repeated-note numerator/denominator/recall;
- family-level onset precision/recall/F1;
- negative-only FP events/second;
- exact onset admission;
- exact state admission;
- exact joint admission;
- true-state vs silence and strongest-incorrect margins;
- repeated-reference onset admission;
- optimizer steps/runtime;
- exact array/init/batch identities.

No post-result threshold selection.

## Frozen S5 success criteria

Weight 9 supports the residual state-imbalance hypothesis only if **all** are true:

1. exact state-admission gain versus weight 6 >= **+0.06**;
2. exact joint-admission gain >= **+0.06**;
3. test onset recall gain >= **+0.05**;
4. test onset F1 gain >= **+0.04**;
5. absolute state admission >= **0.40**;
6. absolute test onset recall >= **0.65**;
7. absolute test onset F1 >= **0.74**;
8. repeated-note recall >= **0.60**;
9. test onset precision >= **0.82**;
10. exact onset-admission decline <= **0.05**;
11. onset+offset F1 decline <= **0.03**;
12. negative-only FP rate <= **0.10 events/s**;
13. no supported family loses > **0.15 onset F1** versus control;
14. both arms finish <=500 steps with finite metrics, identical data/init/batches, fixed thresholds, and zero threshold search.

These are S5 development criteria and do not revise S0-S4 gates.

## Decision branches

- **All pass:** residual state-token underweighting is supported. Stop and design a separate synthetic competence confirmation; do not open P1/P2 automatically.
- **State/joint improve but event floors fail:** state weighting helps but is insufficient; stop and consider a state-representation architectural hypothesis rather than further automatic weighting.
- **Precision/onset specificity degrades:** reject weight 9.
- **No material state/joint gain:** reject additional active-state weighting as the next primary lever.
- **Any identity/runtime failure:** freeze and stop; no automatic model retry.

## Hard ceiling if later authorized

- 294 clips / 588 s;
- exactly 2 models;
- 500 optimizer steps/model, 1,000 total;
- <=20 CPU minutes rendering;
- <=60 CPU minutes fitting/evaluation;
- $0 paid compute;
- zero automatic model retries;
- no threshold tuning;
- no P1/P2/P3;
- no Codespaces;
- no Vercel;
- no deployment/main/customer delivery.

## Authorization boundary

This document does **not** authorize model execution.

S5 requires fresh explicit authorization.
