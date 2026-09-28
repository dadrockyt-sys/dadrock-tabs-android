# Astra synthetic data diversity S4 design V1

Date: 2026-09-27
Status: **DESIGN FROZEN — NOT AUTHORIZED FOR MODEL EXECUTION**

## Question

Does preventing onset-loss gradients from updating the shared encoder improve joint/state admission and event-level transcription while preserving useful onset admission?

This tests one bounded hypothesis: **shared-encoder negative transfer between onset and state objectives**.

It does not assume that gradient competition is already proven.

## Evidence motivating the experiment

S3 increased onset BCE positive weight from 8 to 16.

The intervention raised exact onset admission from 0.5891 to 0.6744, but:
- event recall stayed 0.5814;
- event F1 fell from 0.7075 to 0.6977;
- state/joint admission fell from 0.3333 to 0.2868;
- repeated-note recall fell from 0.5714 to 0.5238.

S2 had shown the complementary direction: stronger state weighting improved state/joint admission and event recall.

This opposite movement is compatible with shared-representation task competition and merits a direct coupling intervention.

## Fixed development data

If later explicitly authorized for model execution:

- regenerate the exact deterministic synthetic corpus;
- root seed 20260927;
- 98 template identities x 3 variants = 294 clips;
- 588 seconds;
- train/validation/test = 210 / 42 / 42;
- same 22.05 kHz, 192-bin CQT;
- no external audio assets;
- no P1/P2/P3.

The synthetic test split has been used repeatedly for development and is not an untouched holdout.

Before optimizer work:
- freeze uncompressed array hashes;
- freeze one 500-minibatch plan;
- use that exact plan for both arms;
- assert identical initialization hashes.

## Models

Exactly two models with identical parameters and forward architecture:

5 x 192 -> Linear(960,128) -> ReLU -> state head + onset head.

Both arms use:
- active-state weight **6.0**;
- onset BCE pos_weight **8.0**;
- onset loss multiplier **4.0**;
- onset-aware 32/32/32/32 sampler;
- Adam lr **0.003**;
- batch size **128**;
- exactly **500 optimizer steps**;
- state threshold **0.50**;
- onset threshold **0.50**;
- decoder V2;
- no threshold search.

Only changed variable:

### Control — shared multitask gradient

The shared encoder receives gradients from both:
- weighted state CE;
- weighted onset BCE.

### Intervention — onset gradient detached from encoder

- state loss updates encoder + state head;
- onset loss updates onset head;
- onset head receives the same encoder activation values in the forward pass, but those values are detached for the onset branch so onset loss contributes **zero gradient to encoder parameters**.

No extra encoder, no extra hidden units, no frozen encoder, no change in parameter count.

## Required implementation checks before any model run

The future runner must fail closed unless synthetic code checks establish:

1. control onset loss produces nonzero encoder gradients on a positive-onset fixture;
2. detached intervention onset loss produces exactly zero encoder gradients while producing nonzero onset-head gradients;
3. state loss produces equivalent encoder gradients in both arms before the onset term is added;
4. both arms have identical initial parameter tensors;
5. both arms consume identical minibatch indices;
6. forward logits are identical between arms before the first optimizer update.

These focused checks execute model operations, so under Stephen's standing policy they are part of the future explicitly authorized model workflow, not an ordinary pre-authorized GitHub test.

## Required measurements

Report validation and test for both arms:

- pitch-onset TP/FP/FN, precision, recall, F1;
- pitch-onset+offset F1;
- repeated-note numerator/denominator/recall;
- family-level onset metrics;
- negative-only FP events/second;
- exact onset admission;
- exact state admission;
- exact joint admission;
- repeated-reference onset admission;
- true-state vs silence and strongest-incorrect margins;
- onset probability summaries;
- per-step or aggregate encoder gradient norm contributions from state and onset objectives on a fixed diagnostic minibatch at initialization and after the final step;
- exact data/init/batch identities;
- runtime and optimizer-step counts.

Gradient measurements are descriptive diagnostics; do not use them to change training mid-run.

## Frozen S4 success criteria

The detached-onset intervention supports harmful onset-to-encoder coupling only if **all** are true:

1. test state-admission gain versus control >= **+0.08**;
2. test joint-admission gain >= **+0.08**;
3. test onset F1 gain >= **+0.04**;
4. test onset recall gain >= **+0.05**;
5. repeated-note recall gain >= **+0.05**;
6. absolute test onset F1 >= **0.74**;
7. absolute test onset recall >= **0.63**;
8. absolute repeated-note recall >= **0.62**;
9. exact onset-admission decline versus control <= **0.05**;
10. onset precision >= **0.85**;
11. onset+offset F1 decline versus control <= **0.03**;
12. negative-only FP rate <= **0.10 events/s**;
13. no supported family loses > **0.15 onset F1** versus control;
14. both arms finish <=500 steps with finite metrics, identical arrays/init/batches, frozen thresholds, and zero threshold search.

These are S4 development criteria only. They do not revise prior gates.

## Decision branches

- **All criteria pass:** onset-to-encoder negative transfer is supported as a meaningful contributor. Stop; design a separate synthetic competence confirmation before any real-data transfer.
- **State/joint improve but onset/event floors fail:** coupling matters but detaching onset is not a sufficient training strategy. Do not automatically add a second encoder or more steps.
- **Onset collapses:** reject full onset-gradient detachment under this setup.
- **No material state/joint gain:** shared onset-to-encoder gradient is not supported as the next primary bottleneck.
- **Any identity/gradient-contract/runtime failure:** freeze and stop; no automatic model retry.

## Hard ceiling if later authorized

- 294 synthetic clips / 588 s;
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

Stephen's standing GitHub authorization permits source/docs/metadata work, but S4 requires explicit authorization because it executes models.
