# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **S9 COMPLETE — STRONG 14/16 NEAR-PASS; CHORD DIVERSITY SUPPORTED BUT STATE GATE MISSED; S10 IDENTITY-PRESERVING STATE-WIDTH DESIGN FROZEN — MODEL EXECUTION NOT AUTHORIZED; P1/P2/P3 SEALED**

## Standing authorization policy

Routine GitHub-only code/tests/docs/metadata work is pre-authorized. Explicit approval is required for model execution, Codespaces, and potentially billable Vercel operations.

## Canonical corrected S9 execution

- run **36379258174**
- job **108791402806**
- launch head `4e6f92c9cb4f2dc56bc9b983ed33c8e97c3f5810`
- workflow **SUCCESS**
- artifact **10952098012**
- artifact digest `sha256:30b4596731c0445e6c38e046c4e628f75dbd55562a97901966746b2e99d7b596`
- focused tests **5/5 passed**
- 2 x 294-clip synthetic datasets / 588 s each
- optimizer 500 + 500
- no threshold search/retry/P1/P2/P3/Codespaces/Vercel

Frozen result:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S9_RESULT_V1.json`

The earlier S9 launch failure had 0 optimizer steps and no scientific result.

## S9 scientific result

10-voicing control -> 30-voicing intervention:
- chord F1 **0.4906 -> 0.6769**
- chord recall **0.3611 -> 0.6111**
- onset recall **0.6047 -> 0.7364**
- onset F1 **0.7123 -> 0.7917**
- precision **0.8667 -> 0.8559**
- repeated recall **0.5238 -> 0.6429**
- onset+offset F1 **0.6079 -> 0.6265**
- joint admission **0.3256 -> 0.3953**
- state admission **0.3798 -> 0.4109**

S9 passed **14 / 16** criteria but remains a formal **FAIL**.

Only failures:
- state-admission gain **+0.0310 < +0.05**
- absolute state admission **0.4109 < 0.42**

Chord voicing diversity is strongly supported development evidence, but P1/P2 remain sealed.

## Offline S9 review

Preserve the successful 30-voicing dataset.

Analysis:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S9_RESULT_ANALYSIS_V1.md`

## Frozen S10 design

- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S10_DESIGN_V1.md`

S10 changes only state-head hidden width:
1. control = 128 hidden units;
2. intervention = 192 hidden units.

Identity-preserving widening:
- first 128 units and their output weights copy control exactly;
- extra 64 hidden units deterministic;
- extra 64 output columns initialize zero;
- pre-update state and onset logits must be bit-identical.

Both arms use the same S9 30-voicing dataset, identical batches, state weight 9, onset weight 8, fixed thresholds and 500 steps/model.

## Exact next step

**Do not execute S10 yet.**

Fresh explicit model authorization is required.

No P1/P2/P3, Codespaces, Vercel, threshold rescue, deployment or main mutation.
