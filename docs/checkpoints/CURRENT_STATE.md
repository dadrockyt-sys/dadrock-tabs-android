# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **S9 MODEL EXPERIMENT EXPLICITLY AUTHORIZED — SOURCE FREEZE IN PROGRESS; P1/P2/P3 SEALED**

## Standing authorization policy

Routine GitHub-only work is pre-authorized. Model execution, Codespaces, and potentially billable Vercel operations require explicit approval.

Stephen explicitly said **"I authorize"** for the frozen S9 model experiment.

## Frozen S9 execution boundary

- exactly two 294-clip synthetic datasets / 588 s each;
- exactly 30 train chord clips per arm;
- control: 10 unique chord voicings x 3 variants;
- intervention: 30 unique voicings with paired original timbre RNG keys;
- validation/test bit-identical;
- all non-chord data bit-identical;
- sampler strata and 500 minibatch indices identical;
- exactly two identical S6 nonlinear-state-head models;
- state weight 9, onset pos_weight 8, onset multiplier 4;
- 500 optimizer steps/model;
- thresholds 0.50/0.50;
- zero threshold search/retuning;
- zero automatic retries;
- no P1/P2/P3;
- no Codespaces or Vercel.

### Exact next task

Record exact source identities and authorization, launch S9 exactly once, inspect that single run, freeze the result, then stop model work.
