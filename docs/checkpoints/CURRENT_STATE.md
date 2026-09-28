# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **S7 MODEL EXPERIMENT EXPLICITLY AUTHORIZED — SOURCE FREEZE IN PROGRESS; P1/P2/P3 SEALED**

## Standing authorization policy

Routine GitHub-only work is pre-authorized. Model execution, Codespaces, and potentially billable Vercel operations require explicit approval.

Stephen explicitly said **"I authorize"** for the frozen S7 model experiment.

## Frozen S7 execution boundary

- deterministic synthetic corpus: 294 clips / 588 s;
- exactly two models;
- control state path = Linear(128,126);
- intervention = identical base Linear(128,126) plus nonlinear residual;
- residual output layer initialized exactly zero;
- shared encoder, onset head, base state head and pre-update state/onset logits must match exactly;
- state active weight 9.0;
- onset pos_weight 8.0;
- onset loss multiplier 4.0;
- onset-aware sampler;
- lr 0.003;
- 500 optimizer steps/model;
- thresholds 0.50/0.50;
- zero threshold search/retuning;
- zero automatic retries;
- no P1/P2/P3;
- no Codespaces or Vercel.

### Exact next task

Record exact source identities and authorization, launch S7 exactly once, inspect the single run, freeze the result, then stop model work.
