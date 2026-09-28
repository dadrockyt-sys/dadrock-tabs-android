# Astra — current handoff

Updated: 2026-09-28 UTC (2026-09-27 America/Toronto)
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **S5 FAILED; OFFLINE REVIEW COMPLETE; S6 STATE-HEAD CAPACITY HYPOTHESIS FROZEN — MODEL EXECUTION NOT AUTHORIZED; P1/P2/P3 SEALED**

## Standing authorization policy

Routine GitHub-only code/tests/docs/metadata work is pre-authorized.

Explicit approval is required for model execution, Codespaces, and potentially billable Vercel operations.

## S5 conclusion retained

Canonical S5 run **36375196849** / job **108779493106**:
- weight 6 onset F1 **0.7196**, recall **0.5969**, state admission **0.3333**
- weight 9 onset F1 **0.7364**, recall **0.6279**, state admission **0.3333**
- joint admission **0.3178 -> 0.3333**
- repeated recall **0.5952 -> 0.6190**
- onset+offset F1 **0.4821 -> 0.5470**
- precision remained high **0.9059 -> 0.8901**
- frozen gate **7 / 14 passed; S5 FAIL**

Weight 9 is not supported as a sufficient state-side fix, and further automatic state-weight escalation is rejected.

## Offline S5 review

At weight 9, exact positive-reference state statistics still show strong silence competition:
- median true-state probability **~0.1478**
- median silence probability **~0.5387**
- median strongest incorrect active probability **~0.0395**
- median true-minus-silence margin **~-0.3248**

The current state branch is only a linear projection from the 128-dimensional shared encoder.

Analysis:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S5_FAILURE_ANALYSIS_V1.md`

## Frozen S6 design

- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S6_DESIGN_V1.md`

Exactly two models with identical shared encoder and onset head initialization:

1. control state head: **Linear(128,126)**
2. intervention state head: **Linear(128,128) -> ReLU -> Linear(128,126)**

Everything else fixed:
- state active weight 9
- onset pos_weight 8
- onset multiplier 4
- onset-aware sampler
- lr 0.003
- 500 steps/model
- thresholds 0.50/0.50
- decoder V2
- identical data and minibatches
- no threshold search.

Because the state-head architectures differ, whole-model pre-update state logits are not required to match. Shared encoder and onset-head initialization plus pre-update onset logits must match exactly.

## Exact next step

**Do not execute S6 yet.**

S6 is a model experiment and requires fresh explicit authorization.

No P1/P2/P3, Codespaces, Vercel, deployment, main mutation, threshold rescue, or extra optimizer steps are authorized.
