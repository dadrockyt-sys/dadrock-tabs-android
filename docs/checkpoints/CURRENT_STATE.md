# Astra — current handoff

Updated: 2026-09-28 UTC (2026-09-27 America/Toronto)
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **S5 MODEL EXPERIMENT EXPLICITLY AUTHORIZED — SOURCE FREEZE IN PROGRESS; P1/P2/P3 SEALED**

## Standing authorization policy

Routine GitHub-only work is pre-authorized. Model execution, Codespaces, and potentially billable Vercel operations require explicit approval.

Stephen explicitly said **"I authorize"** for the frozen S5 model experiment.

## Frozen S5 execution boundary

- deterministic synthetic corpus: 294 clips / 588 s;
- exactly two identical five-frame models;
- control active-state weight 6.0;
- intervention active-state weight 9.0;
- ordinary shared multitask backprop;
- onset-aware 32/32/32/32 sampler;
- onset pos_weight 8.0;
- onset loss multiplier 4.0;
- lr 0.003;
- 500 optimizer steps/model;
- identical data arrays, initialization and 500-minibatch plan;
- thresholds 0.50/0.50;
- zero threshold search/retuning;
- zero automatic retries;
- no P1/P2/P3;
- no Codespaces or Vercel.

### Exact next task

Record exact source identities and authorization, launch S5 exactly once, inspect that one run, freeze the result, then stop model work.
