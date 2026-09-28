# Astra — current handoff

Updated: 2026-09-28 UTC (2026-09-27 America/Toronto)
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **S4 FAILED; OFFLINE REVIEW COMPLETE; S5 STATE-WEIGHT 6→9 HYPOTHESIS FROZEN — MODEL EXECUTION NOT AUTHORIZED; P1/P2/P3 SEALED**

## Standing authorization policy

Routine GitHub-only code/tests/docs/metadata work is pre-authorized.

Explicit approval is required for:
- model execution;
- Codespaces;
- potentially billable Vercel operations.

## S4 conclusion retained

Canonical S4:
- run **36374576717**
- job **108777670719**
- control F1 **0.7156**, recall **0.6047**, precision **0.8764**
- detached-onset F1 **0.5545**, recall **0.6512**, precision **0.4828**
- state/joint admission **0.3411 → 0.3411**
- repeated recall **0.5476 → 0.6905**
- false positives **11 → 90**
- frozen gate **5 / 14 passed; S4 FAIL**

Gradient isolation was verified exactly. Full onset-gradient detachment is rejected as the primary remedy.

Frozen result:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S4_RESULT_V1.json`

## Offline S4 review

S2-S4 now support one narrower remaining hypothesis:

- S2: state active-weight 1.5 → 6 improved state/joint admission and event metrics.
- S3: stronger onset weighting increased onset admission but did not improve event recall.
- S4: removing onset gradients from the encoder did not improve state/joint admission and collapsed precision.

Under the frozen onset-aware sampler, active state tokens are about **10.4414%** of state tokens.

Expected weighted active-state loss share:
- weight 6: **~41.16%**
- equal-mass crossover: **~8.58**
- weight 9: **~51.20%**

Weight 9 is therefore the smallest integer weight above equal-mass contribution.

Analysis:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S4_FAILURE_ANALYSIS_V1.md`

## Frozen S5 design

- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S5_DESIGN_V1.md`

Exactly two identical five-frame models:
1. control active-state weight **6.0**
2. intervention active-state weight **9.0**

Everything else fixed:
- ordinary shared multitask backprop
- onset-aware 32/32/32/32 sampler
- onset pos_weight 8
- onset loss multiplier 4
- lr 0.003
- 500 optimizer steps/model
- thresholds 0.50/0.50
- decoder V2
- identical generated arrays, initialization, and minibatch plan
- no threshold search

## Exact next step

**Do not execute S5 yet.**

S5 is a model experiment and requires fresh explicit authorization.

No P1/P2/P3, Codespaces, Vercel, deployment, main mutation, threshold rescue, or extra optimizer steps are authorized.
