# Astra synthetic data diversity S10 design V1

Date: 2026-09-28
Status: **DESIGN FROZEN — NOT AUTHORIZED FOR MODEL EXECUTION**

## Question

On the successful 30-unique-voicing S9 training dataset, can an identity-preserving widening of the nonlinear state head from 128 to 192 hidden units close the remaining exact state-admission gap without sacrificing event performance?

Only changed variable: **state-head hidden width**.

## Fixed dataset

Both arms use the S9 intervention dataset:
- 294 clips / 588 s;
- 30 unique training chord voicings;
- 30 training chord clips;
- deterministic paired timbre construction from S9;
- same validation/test;
- same non-chord examples;
- no P1/P2/P3.

Regenerate this exact dataset from frozen S9 source and verify:
- intervention signature hash `de7a34d3dc51afa5ef5adc9105fe8796b00724ac5fceac61ab8083ea34dbda1d`;
- 30 unique train chord signatures;
- same train/validation/test counts 210/42/42.

## Fixed model/training

Both arms:
- shared encoder Linear(960,128) -> ReLU;
- onset head Linear(128,6);
- state active weight 9.0;
- onset BCE pos_weight 8.0;
- onset loss multiplier 4.0;
- original uniform 32/32/32/32 onset-aware sampler;
- Adam lr 0.003;
- batch size 128;
- exactly 500 optimizer steps;
- thresholds 0.50 / 0.50;
- decoder V2;
- identical data and 500-minibatch plan;
- zero threshold search/retuning.

## Only changed variable

### Control state head
- Linear(128,128)
- ReLU
- Linear(128,126)

### Intervention state head
- Linear(128,192)
- ReLU
- Linear(192,126)

## Identity-preserving widening contract

Fail closed unless before optimization:

1. shared encoder tensors are identical;
2. onset-head tensors are identical;
3. intervention hidden units 0:128 exactly equal control hidden units;
4. intervention output columns 0:128 exactly equal control output weights;
5. intervention output bias exactly equals control output bias;
6. extra hidden units 128:192 are deterministically initialized and nonzero;
7. intervention output columns 128:192 are exactly zero;
8. pre-update state logits are bit-identical for paired inputs;
9. pre-update onset logits are bit-identical;
10. batch indices are identical.

The extra units start as an exact no-op but can learn after optimization begins.

## Required measurements

Report validation/test:
- overall pitch-onset precision/recall/F1;
- onset+offset F1;
- repeated recall;
- chord precision/recall/F1;
- every family onset F1;
- negative-only FP/sec;
- exact onset/state/joint admission;
- true-state and silence probabilities/margins;
- optimizer steps/runtime;
- initialization/data/batch hashes;
- extra-64 hidden/output parameter norms after training.

## Frozen S10 success criteria

All must pass:

1. exact state-admission gain >= **+0.04**;
2. exact joint-admission gain >= **+0.03**;
3. absolute state admission >= **0.44**;
4. absolute joint admission >= **0.42**;
5. overall onset recall >= **0.72**;
6. overall onset F1 >= **0.78**;
7. chord F1 >= **0.62**;
8. chord recall >= **0.55**;
9. repeated recall >= **0.60**;
10. onset precision >= **0.83**;
11. onset F1 decline versus control <= **0.02**;
12. onset+offset F1 decline <= **0.03**;
13. negative-only FP <= **0.10 events/s**;
14. no supported family loses > **0.15 F1** versus control;
15. extra 64-unit pathway has nonzero parameter norm after training;
16. both arms finish <=500 steps with finite metrics, exact pre-update state/onset logit identity, identical data/batches, fixed thresholds and zero threshold search.

These are S10 development criteria only.

## Decision branches

- **All pass:** the diversified data + widened state head is supported. Stop and design one separate synthetic competence confirmation before P1/P2.
- **State improves but event preservation fails:** reject width 192 as the integrated configuration.
- **No material state gain:** reject state-head widening as the next primary lever.
- **Any identity/runtime failure:** freeze and stop; zero automatic model retry.

## Hard ceiling if later authorized

- one deterministic 294-clip / 588 s synthetic dataset regenerated once;
- exactly 2 models;
- 500 optimizer steps/model, 1,000 total;
- render <=20 CPU minutes;
- fit/eval <=60 CPU minutes;
- $0 paid compute;
- zero automatic retries;
- no threshold tuning;
- no P1/P2/P3;
- no Codespaces;
- no Vercel;
- no deployment/main/customer delivery.

## Authorization boundary

S10 requires fresh explicit authorization before model execution.
