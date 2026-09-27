# Next chat: start here

Repository: `dadrockyt-sys/dadrock-tabs-android`, branch `astra-work`.
Updated: 2026-09-27.

Read `AGENTS.md`, then the **GPT-5.6 handoff review — 2026-09-27 — READ THIS FIRST** section at the top of `docs/checkpoints/CURRENT_STATE.md`.

## Current active task

The combined offline diagnostic package requested by the handoff review has been implemented. **Do not run real media yet.**

First inspect the automatic workflow **Astra P1-P2 combined diagnostic offline tests v1** for the package commit. If it fails, repair only offline code/tests and re-run synthetic verification. If it passes, freeze a synthetic-verification receipt and update the checkpoint.

After a green synthetic receipt, the next step is to present `docs/astra/P1_P2_COMBINED_DIAGNOSTIC_AUTHORIZATION_REQUEST_V1.json` for explicit user authorization. There is intentionally no authorization artifact and no launch artifact yet.

## Boundaries

- no P1/P2 media access until explicit authorization;
- no optimizer steps or fitting;
- no threshold search/change;
- no P3 access;
- no full V1-V5 restart;
- no production/deployment mutation;
- no customer-readiness claim.

The future diagnostic ceiling remains eight frozen P1/P2 captures, 200 frames each, frozen V3 model, 0 optimizer steps, thresholds 0.50/0.50, <=90-minute CPU job, zero retries, zero paid compute, P3 sealed.

Frozen V3 artifact 10918434248 expires 2026-10-03T23:51:34Z. Preserve durable authorized evidence before expiry; never retrain merely to recreate it.
