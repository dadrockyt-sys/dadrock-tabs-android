# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **S10 FAILED; WIDTH 192 REJECTED AS INTEGRATED CONFIGURATION; S11 MULTI-SEED S9 ROBUSTNESS CONFIRMATION FROZEN — MODEL EXECUTION NOT AUTHORIZED; P1/P2/P3 SEALED**

## Standing authorization policy

Routine GitHub-only code/tests/docs/metadata work is pre-authorized. Explicit approval is required for model execution, Codespaces, and potentially billable Vercel operations.

## Canonical S10 result

- run **36379983316**
- job **108793560697**
- launch head `c467a9ec3eab08262b43852a621d4e497c031ca8`
- workflow **SUCCESS**
- artifact **10952511057**
- artifact digest `sha256:82752c9f3b0067f4bdadc81e5aa3c7f8e50486a3590dbadad92a7d3713409a31`
- identity tests **3/3 passed**
- 294 clips / 588 s
- optimizer 500 + 500
- no threshold search/retry/P1/P2/P3/Codespaces/Vercel

Frozen result:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S10_RESULT_V1.json`

128 -> 192:
- state admission **0.2791 -> 0.3256** (+0.0465)
- joint admission **0.2791 -> 0.3256** (+0.0465)
- onset recall **0.5659 -> 0.6357**
- onset F1 **0.6759 -> 0.6979**
- chord F1 **0.3019 -> 0.3934**
- repeated recall **0.5952 -> 0.6429**
- precision **0.8391 -> 0.7736**
- onset+offset F1 **0.6250 -> 0.5892**

S10 gate **FAILED (7/16 passed)**.

Width 192 learned and helped state admission, but it did not preserve enough event quality. Do not continue automatic widening.

## Offline S10 review

The S10 128-unit control was much weaker than the earlier S9 30-voicing arm despite the same diversified dataset/training class. This exposes meaningful deterministic initialization sensitivity.

Analysis:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S10_RESULT_ANALYSIS_V1.md`

## Frozen S11 design

- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S11_DESIGN_V1.md`

S11 does not tune architecture. It repeats the S9 10-vs-30 chord-voicing comparison across exactly three deterministic seeds:
- 20260927
- 20260928
- 20260929

Exactly 6 models, 500 steps each. Within each seed, control/intervention data, initialization and minibatches are paired.

Purpose: determine whether the S9 chord-diversity effect is robust or seed-sensitive before any proposal to open P1/P2.

## Exact next step

**Do not execute S11 yet.**

Fresh explicit model authorization is required.

No P1/P2/P3, Codespaces, Vercel, threshold rescue, deployment or main mutation.
