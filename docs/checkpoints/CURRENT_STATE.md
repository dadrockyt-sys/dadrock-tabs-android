# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **S6 MODEL EXPERIMENT EXPLICITLY AUTHORIZED — SOURCE FREEZE IN PROGRESS; P1/P2/P3 SEALED**

## Standing authorization policy

Routine GitHub-only work is pre-authorized. Model execution, Codespaces, and potentially billable Vercel operations require explicit approval.

Stephen explicitly said **"I authorize"** for the frozen S6 model experiment.

## Frozen S6 execution boundary

- deterministic synthetic corpus: 294 clips / 588 s;
- exactly two models;
- identical shared encoder initialization;
- identical onset-head initialization;
- identical data arrays and 500-minibatch plan;
- control state head: Linear(128,126);
- intervention state head: Linear(128,128) -> ReLU -> Linear(128,126);
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

Record exact source identities and authorization, launch S6 exactly once, inspect the single run, freeze the result, then stop model work.
