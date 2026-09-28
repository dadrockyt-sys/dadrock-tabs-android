# Astra synthetic data diversity S3 design V1

Date: 2026-09-27
Status: **DESIGN FROZEN — NOT AUTHORIZED FOR EXECUTION**

## Question

With the S2 weight-6 state setting and the S1 onset-aware sampler held fixed, does increasing only onset BCE positive-token weight from 8 to 16 materially improve exact onset admission, event recall, and repeated-note recall without unacceptable precision, state, offset, or negative-audio degradation?

## Evidence motivating the single variable

S2 weight 6.0 test:
- onset precision 0.8675;
- onset recall 0.5581;
- onset F1 0.67925;
- onset+offset F1 0.5561;
- repeated-note recall 0.5000;
- exact onset admission 0.5736;
- exact state admission 0.3101;
- exact joint admission 0.3023.

Changing state weight 1.5 -> 6.0 improved state/joint admission and event recall but left exact onset admission unchanged at 0.5736 and repeated-note recall unchanged at 0.5000.

Under the frozen 32/32/32/32 sampler, positive onset tokens are expected to be about 5.119% of string/onset tokens in a minibatch. Current pos_weight 8 makes them about 30.15% of expected weighted onset-loss mass; pos_weight 16 makes them about 46.33%.

## Fixed data and identity controls

If later authorized, regenerate the exact deterministic synthetic development corpus:
- root seed 20260927;
- 98 template identities x 3 timbre variants = 294 clips;
- 588 seconds total;
- train/validation/test = 210 / 42 / 42;
- 22.05 kHz frozen 192-bin CQT;
- no external samples/IRs;
- no P1/P2/P3.

Before optimizer work:
- write uncompressed array-content hashes for all generated arrays;
- precompute the exact same 500 minibatch indices for both arms;
- hash the batch plan;
- assert identical model initialization hash across arms.

The S0/S1/S2 test split has already informed this design and remains development evidence, not an untouched holdout.

## Models

Exactly two identical five-frame temporal models:

5 x 192 input -> Linear(960,128) -> ReLU -> identical state/onset heads.

Both arms use:
- S1 onset-aware 32/32/32/32 frame sampler;
- active-state token weight **6.0**;
- onset loss multiplier **4.0**;
- Adam lr **0.003**;
- batch size **128**;
- exactly **500** optimizer steps;
- state threshold **0.50**;
- onset threshold **0.50**;
- decoder V2;
- no threshold search or retuning.

Only changed variable:
- control onset BCE `pos_weight = 8`;
- intervention onset BCE `pos_weight = 16`.

## Required measurements

For validation and test, both arms must report:
- pitch-onset TP/FP/FN, precision, recall, F1;
- pitch-onset+offset F1;
- repeated-note numerator/denominator/recall;
- family-level onset precision/recall/F1;
- negative-only FP events/second;
- exact positive-reference onset admission;
- exact positive-reference correct-state admission;
- exact joint onset+state admission;
- onset probability/logit summaries at exact positive references;
- for repeated-note references specifically: onset-admission numerator/denominator and preceding-frame onset probability distribution;
- state true-vs-silence and strongest-incorrect margins;
- optimizer steps/runtime;
- generated-array hashes, initialization hash, and batch-plan hash.

No post-result threshold selection.

## Frozen S3 success criteria

The pos_weight-16 intervention supports the onset-weighting hypothesis only if **all** are true:

1. exact-reference onset-admission gain versus pos_weight 8 >= **+0.10**;
2. test pitch-onset recall gain >= **+0.08**;
3. test pitch-onset F1 gain >= **+0.05**;
4. repeated-note recall gain >= **+0.10**;
5. absolute test onset recall >= **0.65**;
6. absolute test onset F1 >= **0.72**;
7. absolute repeated-note recall >= **0.60**;
8. test onset precision >= **0.82**;
9. exact state-admission decline versus control <= **0.05**;
10. exact joint-admission decline versus control <= **0.05**;
11. onset+offset F1 decline versus control <= **0.05**;
12. negative-only FP rate <= **0.10 events/s**;
13. no supported family loses more than **0.15 onset F1** versus control;
14. both arms complete <=500 steps, all metrics finite, identical data/init/batch plan, and zero threshold search.

These are S3 diagnostic gates. They do not rewrite failed S0/S1/S2 gates.

## Decision branches

- **All criteria pass:** remaining onset-positive underweighting is supported as a meaningful contributor. Stop and design a separate synthetic competence gate; do not open P1/P2 automatically.
- **Onset admission/recall improve but repeated-note floor fails:** onset weighting helps general attacks but does not solve repeated-attack separation; next review should isolate temporal peak/rising-edge behavior rather than increase weight again automatically.
- **Precision or negative specificity fails:** reject pos_weight 16 under this sampler.
- **State/joint admission degrades beyond the guard:** reject the intervention as harmful to joint decoding.
- **No material onset-admission gain:** reject onset positive-token underweighting as the next primary lever under this setup.
- **Any preparation/runtime/identity failure:** freeze and stop; zero automatic retry.

## Hard execution ceiling if later authorized

- exactly 294 clips / 588 s;
- exactly 2 five-frame models;
- 500 optimizer steps/model, 1,000 total;
- render <=20 CPU min;
- fit/eval <=60 CPU min;
- $0 paid compute;
- zero automatic retries;
- no threshold tuning;
- no external audio assets;
- no P1/P2/P3;
- no deployment, main mutation, or customer delivery.

## Authorization boundary

This document does **not** authorize execution.

Fresh explicit authorization is required before S3 rendering or optimizer work.
