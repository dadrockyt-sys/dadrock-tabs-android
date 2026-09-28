# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **S6 FAILED; OFFLINE REVIEW COMPLETE; S7 ZERO-INITIALIZED STATE-RESIDUAL HYPOTHESIS FROZEN — MODEL EXECUTION NOT AUTHORIZED; P1/P2/P3 SEALED**

## Standing authorization policy

Routine GitHub-only code/tests/docs/metadata work is pre-authorized.

Explicit approval is required for model execution, Codespaces, and potentially billable Vercel operations.

## Canonical S6 result

- run **36376438006**
- job **108783145192**
- launch head `d8472f0731e8ffb0c8c56ebe804756ec25ae8002`
- workflow conclusion **SUCCESS**
- artifact **10950664804**
- artifact digest `sha256:c89284c3937018a6b871eab2c29d3154c0ac0e9bd24f625c9d030cf2aad8ac48`
- focused tests **3 / 3 passed**
- 294 clips / 588 s
- optimizer **500 + 500 = 1,000**
- no threshold search/retuning
- no automatic retry
- no P1/P2/P3, Codespaces, or Vercel

Frozen result:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S6_RESULT_V1.json`

### Linear control vs nonlinear state head

Control:
- state admission **0.3178**
- joint admission **0.3101**
- recall **0.5659**
- F1 **0.7053**
- precision **0.9359**
- repeated recall **0.5714**
- median true-state probability **0.0942**
- median silence probability **0.6330**

Nonlinear:
- state admission **0.3798**
- joint admission **0.3256**
- recall **0.6047**
- F1 **0.7123**
- precision **0.8667**
- repeated recall **0.5238**
- median true-state probability **0.2180**
- median silence probability **0.4812**

Key deltas:
- state admission **+0.0620**
- joint admission **+0.0155**
- recall **+0.0388**
- F1 **+0.0070**

S6 failed its frozen gate. Extra state-specific nonlinear capacity is promising but insufficient as a replacement head.

## Offline S6 review

S6 moved the state bottleneck more clearly than S5, but the replacement architecture changed the state pathway from the first step.

A cleaner next test preserves the exact control state path and adds nonlinear capacity only as a zero-initialized residual correction.

Analysis:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S6_FAILURE_ANALYSIS_V1.md`

## Frozen S7 design

- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S7_DESIGN_V1.md`

Control:
- state logits = Linear(128,126)

Intervention:
- same base Linear(128,126)
- plus Linear(128,128) -> ReLU -> Linear(128,126) residual
- residual output layer initialized exactly zero
- final state logits = base + residual

Thus both arms must have exactly identical state and onset logits before optimization.

Everything else remains fixed at state weight 9 / onset pos_weight 8 / onset-aware sampler / lr 0.003 / 500 steps / thresholds 0.50.

## Exact next step

**Do not execute S7 yet.**

S7 is a model experiment and requires fresh explicit authorization.

No P1/P2/P3, Codespaces, Vercel, deployment, main mutation, threshold rescue, or extra optimizer steps are authorized.
