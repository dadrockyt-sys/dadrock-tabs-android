# Astra P1/P2 transfer evaluation proposal V1

Date: 2026-09-28
Status: **PROPOSAL ONLY — P1/P2 ACCESS NOT AUTHORIZED**

## Purpose

Determine whether the strongest bounded synthetic lessons transfer at all to the existing P1/P2 real-development partitions.

This is not a production evaluation and not a P3 evaluation.

## Why now

The synthetic sequence is closed after S11:
- onset-aware positive sampling was useful;
- state-weight escalation beyond the bounded range was insufficient;
- full onset-gradient detach was rejected;
- nonlinear replacement state capacity showed partial benefit;
- chord-voicing diversity showed directionally consistent gains across three seeds but failed the robustness magnitude gate;
- further tuning on the same synthetic development split is not justified.

## Proposed transfer question

Evaluate **one frozen integrated configuration** against the already-established real-development baseline on P1 and P2 only.

The proposal must not use P3.

No threshold search, threshold retuning, architecture sweep, model-selection loop, or automatic synthetic retraining is permitted from the transfer result.

## Candidate integrated configuration

Use the conservative S9/S11 architecture/training recipe:
- five-frame input;
- shared encoder Linear(960,128) -> ReLU;
- nonlinear state head Linear(128,128) -> ReLU -> Linear(128,126);
- onset head Linear(128,6);
- state active weight 9;
- onset pos_weight 8;
- onset loss multiplier 4;
- onset-aware uniform 32/32/32/32 sampler;
- 30-unique-voicing synthetic chord construction;
- state/onset thresholds fixed at 0.50/0.50;
- decoder V2.

Do **not** use the S10 width-192 intervention.

## Before any P1/P2 access

A separate authorization must explicitly allow:
- reading P1/P2 real-development assets;
- any required model training/inference needed for the transfer check;
- the exact compute ceiling.

The authorization must explicitly keep P3 sealed.

## Proposed evidence

For P1 and P2 separately and pooled:
- evaluator V2 pitch-onset precision/recall/F1;
- pitch onset+offset F1;
- repeated-note recall where supported;
- false positives/second on negative/non-guitar regions where defined;
- unresolved/ambiguous event counts;
- exact model/data/source identities.

## Decision discipline

This transfer evaluation answers only whether the frozen synthetic configuration shows evidence of transfer.

It must not:
- tune thresholds against P1/P2;
- pick a seed after seeing P1/P2 results;
- reopen P3;
- make a production-readiness claim.

If transfer is weak or inconsistent, freeze that result and reconsider the training formulation offline rather than iterating directly on P1/P2.
