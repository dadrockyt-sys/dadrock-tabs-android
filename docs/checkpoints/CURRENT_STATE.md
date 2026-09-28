# Astra — current handoff

Updated: 2026-09-28 UTC (2026-09-27 America/Toronto)
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **S4 COMPLETE — FULL ONSET-GRADIENT DETACH REJECTED; FROZEN GATE FAILED; OFFLINE REVIEW NEXT; P1/P2/P3 SEALED**

## Standing authorization policy

Routine GitHub-only code/tests/docs/metadata work is pre-authorized.

Explicit approval is required for:
- model execution;
- Codespaces;
- potentially billable Vercel operations.

## Canonical S4 execution

- run **36374576717**
- job **108777670719**
- launch head `66bd45674bff2b23a75b97338d64f1d7a8b52982`
- workflow conclusion **SUCCESS**
- artifact **10949743734**
- artifact digest `sha256:3285576d3c58c150aa99d58bc40c7e0a7318f3d40dcb359bcf8c0ccdcf3ecc47`
- gradient-contract tests **3 / 3 passed**
- 294 synthetic clips / 588 s
- optimizer steps **500 + 500 = 1,000**
- threshold search **none**
- automatic retry **0**
- P1/P2/P3 **not accessed**
- Codespaces/Vercel **not used**

Frozen result:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S4_RESULT_V1.json`

The two earlier S4 launch failures were pre-model failures with **0 optimizer steps** and remain preserved in Git history and their receipts.

## Gradient contract

Before optimization:
- control onset -> encoder grad norm **0.3063**
- detached onset -> encoder grad norm **0.0000**
- both onset-head grad norms **0.1389**
- both state -> encoder grad norms **0.6286**
- pre-update forward logits identical.

The intervention therefore isolated the intended variable.

## Scientific result — S4 FAIL

Control:
- onset precision **0.8764**
- recall **0.6047**
- F1 **0.7156**
- onset+offset F1 **0.5351**
- repeated recall **0.5476**
- onset admission **0.6279**
- state/joint admission **0.3411**

Detached onset-gradient intervention:
- onset precision **0.4828**
- recall **0.6512**
- F1 **0.5545**
- onset+offset F1 **0.3323**
- repeated recall **0.6905**
- onset admission **0.5581**
- state/joint admission **0.3411**

Key deltas:
- state admission **+0.0000**
- joint admission **+0.0000**
- recall **+0.0465**
- F1 **-0.1611**
- repeated recall **+0.1429**
- onset admission **-0.0698**
- onset+offset F1 **-0.2028**

Only **5 / 14** frozen S4 criteria passed. `s4GatePassed=false`.

The repeated-recall increase is not a clean win: test onset false positives rose from **11 to 90**, collapsing precision below 0.50.

## Interpretation

Full onset-gradient detachment is rejected under this setup.

It did not improve the state/joint bottleneck and sharply degraded precision, F1, onset+offset quality, and family stability.

This does **not** prove shared-encoder gradient competition is absent. It shows that fully removing onset supervision from the shared encoder is not supported as the primary remedy.

## Exact next step

Only offline review/design is authorized automatically.

Do not run another model, P1/P2 transfer, P3, Codespaces, Vercel, threshold rescue, or extra optimizer steps without the required explicit authorization.

Historical checkpoints remain available in Git history.
