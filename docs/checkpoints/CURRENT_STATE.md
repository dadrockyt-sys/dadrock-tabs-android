# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **S10 MODEL EXPERIMENT EXPLICITLY AUTHORIZED — SOURCE FREEZE IN PROGRESS; P1/P2/P3 SEALED**

## Standing authorization policy

Routine GitHub-only work is pre-authorized. Model execution, Codespaces, and potentially billable Vercel operations require explicit approval.

Stephen explicitly said **"I authorize"** for the frozen S10 model experiment.

## Frozen S10 execution boundary

- exact S9 30-voicing synthetic dataset, 294 clips / 588 s;
- exactly two models;
- control nonlinear state hidden width 128;
- intervention width 192;
- first 128 hidden units/output columns copied exactly from control;
- extra 64 hidden units deterministic and nonzero;
- extra 64 output columns exactly zero at initialization;
- pre-update state/onset logits must be bit-identical;
- identical data and 500-minibatch plan;
- state weight 9, onset pos_weight 8, onset multiplier 4;
- lr 0.003;
- 500 optimizer steps/model;
- thresholds 0.50/0.50;
- zero threshold search/retuning;
- zero automatic retries;
- no P1/P2/P3;
- no Codespaces or Vercel.

### Exact next task

Record exact source identities and authorization, launch S10 exactly once, inspect that single run, freeze the result, then stop model work.
