# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **P1/P2 TRANSFER COMPLETE — FAILED 0/5; SYNTHETIC CANDIDATE REJECTED FOR REAL DEVELOPMENT; P3 SEALED**

## Standing policy

Routine GitHub work and bounded inexpensive synthetic GitHub model runs remain pre-authorized.

P1/P2/P3 real-data access remains a separate boundary.

## Canonical P1/P2 transfer run

- run **36381769369**
- job **108798822867**
- head `b9f9109c22152ea23613d829b74c59b5ddc6dcf6`
- workflow **SUCCESS**
- artifact **10953563527**
- digest `sha256:ef571953b8872902407e375b0f673d3590fe96534e2d77a1c3be0fb6a0c67aae`
- candidate synthetic training: exactly 500 steps
- evaluation optimizer steps: 0
- thresholds fixed 0.50 / 0.50
- P1 accessed: yes
- P2 accessed: yes
- P3 opened: **no**
- automatic retry: no

Frozen result:
- `docs/astra/P1_P2_TRANSFER_EVALUATION_RESULT_V1.json`

## Result

P1 baseline:
- TP/FP/FN **16 / 7 / 0**
- F1 **0.8205**
- recall **1.0**

P1 synthetic candidate:
- TP/FP/FN **0 / 10 / 16**
- F1 **0**

P2 baseline:
- TP/FP/FN **0 / 0 / 15**
- F1 **0**

P2 synthetic candidate:
- TP/FP/FN **0 / 1 / 15**
- F1 **0**

Transfer gate: **FAILED 0/5**.

## Interpretation

The synthetic candidate failed on both real P1 and P2.

Because the historical V3 baseline remains strong on P1, this is not merely a P1-to-P2 performer-shift failure. It is a broader synthetic-to-real transfer failure for the current candidate.

Do not:
- threshold-rescue;
- select another seed after seeing P1/P2;
- reopen synthetic tuning against these eight examples;
- open P3.

Analysis:
- `docs/astra/P1_P2_TRANSFER_FAILURE_ANALYSIS_V1.md`

## Next proposal

A zero-optimizer domain diagnostic is designed at:
- `docs/astra/SYNTHETIC_REAL_DOMAIN_DIAGNOSTIC_PROPOSAL_V1.md`

It would compare fixed synthetic/P1/P2 feature and activation distributions without changing weights or thresholds.

**Do not execute it yet. New P1/P2 access requires fresh explicit authorization.**

P3 remains sealed.

## Repository note

After the completed run, the workflow/auth source pins were hardened to add a focused-test-before-real-access step. That hardening did not rerun the transfer and is not retroactively claimed as part of run 36381769369.
