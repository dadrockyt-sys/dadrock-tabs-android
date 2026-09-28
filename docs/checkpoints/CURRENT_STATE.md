# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **S8 MODEL EXPERIMENT EXPLICITLY AUTHORIZED — SOURCE FREEZE IN PROGRESS; P1/P2/P3 SEALED**

## Standing authorization policy

Routine GitHub-only work is pre-authorized. Model execution, Codespaces, and potentially billable Vercel operations require explicit approval.

Stephen explicitly said **"I authorize"** for the frozen S8 model experiment.

## Frozen S8 execution boundary

- 294 deterministic synthetic clips / 588 s;
- exactly two identical S6 nonlinear-state-head models;
- 500 optimizer steps/model;
- state weight 9, onset pos_weight 8, onset multiplier 4;
- 32/32/32/32 sampler;
- only positive-stratum probability differs;
- control positive frames sampled uniformly;
- intervention positive frames sampled proportional to onset-string multiplicity;
- paired-identical non-positive indices;
- identical model initialization and pre-update logits;
- thresholds 0.50/0.50, no threshold search;
- zero automatic retries;
- no P1/P2/P3, Codespaces, or Vercel.

### Exact next task

Record exact source identities and authorization, launch S8 exactly once, inspect that single run, freeze the result, then stop model work.
