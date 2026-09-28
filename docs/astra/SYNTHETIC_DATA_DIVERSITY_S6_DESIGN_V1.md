# Astra synthetic data diversity S6 design V1

Date: 2026-09-27
Status: **DESIGN FROZEN — NOT AUTHORIZED FOR MODEL EXECUTION**

## Question

With the S5 weight-9 loss setting fixed, does adding one state-only nonlinear hidden layer improve exact state/joint admission and event transcription while leaving the onset path stable?

This tests one variable: **state-head nonlinear capacity**.

## Motivation

S5 weight 9 crossed the approximate equal-mass point for weighted active-state loss but exact state admission remained 0.3333.

At exact positive test references under weight 9:
- median true-state probability: about 0.1478;
- median silence probability: about 0.5387;
- median strongest incorrect active probability: about 0.0395;
- median true-minus-silence margin: about -0.3248.

The correct active fret often loses to silence, and increasing state-loss weight did not change the exact admission fraction.

## Fixed data

If explicitly authorized:
- deterministic synthetic corpus only;
- root seed 20260927;
- 98 template identities x 3 variants = 294 clips;
- 588 seconds;
- train/validation/test 210 / 42 / 42;
- frozen 22.05 kHz / 192-bin CQT;
- no external audio assets;
- no P1/P2/P3.

The synthetic test split is development evidence, not an untouched holdout.

Before optimization:
- freeze uncompressed array hashes;
- freeze one 500-minibatch plan and use it for both arms;
- initialize shared encoder identically across arms;
- initialize onset head identically across arms;
- verify pre-update onset logits are exactly identical;
- report exact parameter counts.

## Models

Both arms share:

Shared encoder:
- 5 x 192 input = 960
- Linear(960,128)
- ReLU

Onset head:
- Linear(128,6)

Training:
- ordinary shared multitask backpropagation;
- active-state loss weight **9.0**;
- onset BCE pos_weight **8.0**;
- onset loss multiplier **4.0**;
- onset-aware 32/32/32/32 sampler;
- Adam lr **0.003**;
- batch size **128**;
- exactly **500 optimizer steps**;
- state threshold **0.50**;
- onset threshold **0.50**;
- decoder V2;
- zero threshold search/retuning.

Only changed variable:

### Control — linear state head
- Linear(128, 6 x 21)

### Intervention — nonlinear state head
- Linear(128,128)
- ReLU
- Linear(128, 6 x 21)

No other architectural change.

## Required measurements

For validation and test:
- pitch-onset TP/FP/FN, precision, recall, F1;
- pitch-onset+offset F1;
- repeated-note recall numerator/denominator;
- family-level onset metrics;
- negative-only FP events/second;
- exact onset admission;
- exact state admission;
- exact joint admission;
- true-state probability;
- silence probability;
- true-minus-silence margin;
- strongest incorrect active probability and margin;
- repeated-reference onset admission;
- optimizer steps/runtime;
- exact generated-array hashes;
- exact batch-plan hash;
- shared-encoder and onset-head initialization hashes;
- total and state-head parameter counts.

No post-result threshold selection.

## Frozen S6 success criteria

The nonlinear state head supports the capacity hypothesis only if **all** are true:

1. exact state-admission gain versus linear control >= **+0.08**;
2. exact joint-admission gain >= **+0.08**;
3. test onset recall gain >= **+0.04**;
4. test onset F1 gain >= **+0.03**;
5. absolute exact state admission >= **0.42**;
6. absolute test onset recall >= **0.67**;
7. absolute test onset F1 >= **0.76**;
8. repeated-note recall >= **0.62**;
9. test onset precision >= **0.84**;
10. exact onset-admission decline <= **0.05**;
11. onset+offset F1 decline <= **0.03**;
12. negative-only FP rate <= **0.10 events/s**;
13. no supported family loses > **0.15 onset F1** versus control;
14. both arms finish <=500 steps with finite metrics, identical data/batches/shared encoder/onset-head initialization, fixed thresholds, and zero threshold search.

These are S6 development criteria only. They do not revise S0-S5 gates.

## Decision branches

- **All pass:** state-head nonlinear capacity is supported as a meaningful contributor. Stop and design a separate synthetic competence confirmation; do not open P1/P2 automatically.
- **State/joint improve but event floors fail:** added capacity helps representation but is insufficient; stop before considering further architecture.
- **No material state/joint gain:** reject the extra state-only hidden layer as the next primary lever.
- **Onset/precision/family stability degrades beyond guards:** reject the intervention.
- **Any identity/runtime failure:** freeze and stop; zero automatic model retry.

## Hard ceiling if later authorized

- 294 clips / 588 s;
- exactly 2 models;
- 500 optimizer steps/model, 1,000 total;
- <=20 CPU minutes rendering;
- <=60 CPU minutes fit/evaluation;
- $0 paid compute;
- zero automatic model retries;
- no threshold tuning;
- no P1/P2/P3;
- no Codespaces;
- no Vercel;
- no deployment/main/customer delivery.

## Authorization boundary

This document does **not** authorize model execution.

S6 requires fresh explicit authorization.
