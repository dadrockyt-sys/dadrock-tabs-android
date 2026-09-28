# Astra synthetic data diversity S7 design V1

Date: 2026-09-28
Status: **DESIGN FROZEN — NOT AUTHORIZED FOR MODEL EXECUTION**

## Question

Can a zero-initialized nonlinear residual correction improve state/joint admission while preserving the proven linear state path and identical pre-training outputs?

This tests one variable: **learnable nonlinear residual state capacity**.

## Motivation

S6's replacement nonlinear state head increased exact state admission from 0.3178 to 0.3798 and materially reduced silence dominance, but joint/event gains were too small and repeated-note recall declined.

Unlike S6, S7 preserves the exact linear control path and adds nonlinear capacity as an initially-zero residual. This removes pre-training state-logit differences as a confound.

## Fixed data and training

If explicitly authorized:
- deterministic synthetic corpus only;
- root seed 20260927;
- 294 clips / 588 seconds;
- train/validation/test 210 / 42 / 42;
- same 22.05 kHz / 192-bin CQT;
- no external audio assets;
- no P1/P2/P3.

Both arms:
- shared encoder: Linear(960,128) -> ReLU;
- onset head: Linear(128,6);
- active-state weight 9.0;
- onset BCE pos_weight 8.0;
- onset loss multiplier 4.0;
- onset-aware 32/32/32/32 sampler;
- Adam lr 0.003;
- batch size 128;
- exactly 500 optimizer steps;
- state/onset thresholds 0.50 / 0.50;
- decoder V2;
- zero threshold search/retuning.

## Only changed variable

### Control
State logits:
- Linear(128,126)

### Intervention
State logits:
- base = the exact same Linear(128,126)
- residual = Linear(128,128) -> ReLU -> Linear(128,126)
- output = base + residual

Initialization contract:
- base linear state head exactly identical to control;
- residual first layer uses deterministic initialization;
- residual final layer weights and bias are exactly zero;
- therefore intervention state logits are bit-identical to control before the first optimizer update.

## Required preflight identity checks

Before optimization, fail closed unless:
1. generated array hashes match across arms;
2. minibatch plan is identical;
3. shared encoder tensors are identical;
4. onset head tensors are identical;
5. base linear state-head tensors are identical;
6. residual final layer is exactly zero;
7. pre-update state logits are exactly identical;
8. pre-update onset logits are exactly identical;
9. total/state-head parameter counts are recorded.

## Required measurements

For validation and test:
- pitch-onset TP/FP/FN, precision, recall, F1;
- pitch-onset+offset F1;
- repeated-note recall;
- family-level onset metrics;
- negative-only FP/sec;
- exact onset/state/joint admission;
- true-state probability and silence probability;
- true-minus-silence margin;
- strongest incorrect active probability and margin;
- repeated-reference onset admission;
- optimizer steps/runtime;
- array/init/batch hashes;
- residual branch parameter norm at end of training to verify it actually learned.

No post-result threshold selection.

## Frozen S7 success criteria

The residual intervention supports the hypothesis only if **all** are true:

1. exact state-admission gain >= **+0.07**;
2. exact joint-admission gain >= **+0.06**;
3. test onset recall gain >= **+0.04**;
4. test onset F1 gain >= **+0.03**;
5. absolute exact state admission >= **0.40**;
6. absolute test onset recall >= **0.64**;
7. absolute test onset F1 >= **0.74**;
8. repeated-note recall >= **0.60**;
9. onset precision >= **0.85**;
10. onset-admission decline <= **0.04**;
11. onset+offset F1 decline <= **0.03**;
12. negative-only FP rate <= **0.10 events/s**;
13. no supported family loses > **0.15 onset F1**;
14. residual parameter norm after training > **0**;
15. both arms finish <=500 steps with finite metrics, exact pre-update state/onset logit identity, fixed thresholds, and zero threshold search.

These are S7 development criteria only and do not revise S0-S6 gates.

## Decision branches

- **All pass:** zero-initialized nonlinear state residual is supported. Stop and design a separate synthetic competence confirmation before any P1/P2 transfer.
- **State/joint improve but event floors fail:** state representation improves but another bottleneck remains; stop.
- **No material state/joint gain:** reject this residual-capacity hypothesis.
- **Onset/precision/family stability degrades:** reject the intervention.
- **Any identity/runtime failure:** freeze and stop; zero automatic model retry.

## Hard ceiling if later authorized

- exactly 294 clips / 588 s;
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

S7 requires fresh explicit authorization.
