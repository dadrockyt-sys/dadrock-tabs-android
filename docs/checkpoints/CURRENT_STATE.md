# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 00:47 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO QUALITY VERDICT** — performance/identity/routing diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`; no persistent user-audio/stem/result retention without explicit permission.

## Production before candidate promotion

- Vercel/web `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`; route blob `06234db3e1cc1680b18fd62a765862b213ede3db`.
- Vercel deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, READY.
- HTTP bridge source blob `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`; bridge resolves worker app `dadrock-v143-ai-tab-live` dynamically.
- Live endpoint blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`.
- No Vercel/bridge change is required for scheduler promotion.

## Candidate

- Scheduler implementation commit `6772a0ca1d700ea6861cd4401b51e093144c8d26`.
- Candidate scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Immediate pre-candidate rollback commit `2ab73f0e445c1584fc6dce0112e3091985b4a575` has the same live endpoint blob `111bf14a...` and serialized scheduler blob `250534e516cad36e49cae35b6eab2b88654be2d3`.

## Closed promotion evidence

- Gate 1 structural: run `33942915753` / job `101243642285` — **GREEN/CLOSED**.
- Gate 2 exact approved-fixture runtime: run `33943100948` / job `101244148835` / artifact `9962641557` — **GREEN/CLOSED**; exact parity/public contract/runtime/cleanup/safety passed; no scoring/reference/persistence.
- Gate 3A normal-routing composition: run `33945157629` / job `101249801382` / artifact `9963085825` (`sha256:9084a0d17ca44154e66a89f78546b6e210e3a302110e9e560c99b9f20a39ad09`) — **GREEN/CLOSED**; all pinned source identities and full Rhythm-only chain passed.
- Decision `MODEL_BEARING_E2E_NOT_JUSTIFIED`; record `docs/checkpoints/V143_NORMAL_ROUTING_PROMOTION_DECISION.md` commit `08c9a98f38b1ca0e23bd9408b8a15bf0713fd7ff`.
- **Normal-routing pre-production promotion evidence boundary: GREEN/CLOSED.**

## Production integration/deploy plan — CHECKPOINTED / AUTHORIZED SCOPE

Plan: `docs/checkpoints/V143_SEEDED_SCHEDULER_PRODUCTION_PLAN.md`, commit `b84d7c05cac15bc2d3196278502029a196412541`.

The branch is 139 commits ahead and 227 behind `main`; whole-branch merge is explicitly rejected.

Promotion scope is **worker-only Modal redeploy** from the proven branch source:

- deploy only `analyzer/v143_modal_live_endpoint.py` to app `dadrock-v143-ai-tab-live`;
- exact pre-deploy pins required: live endpoint `111bf14a...`, scheduler `fc9b4c45...`, deterministic wrapper `28b3e6fe...`, deterministic provider `3c6dcf9b...`, stem provider `cd180bfb...`, request adapter `6d1787f3...`, router `7849f33c...`;
- no Vercel deploy/change;
- no HTTP bridge deploy/change;
- no `main` merge;
- no approved fixture or model execution during deployment verification;
- post-deploy verification is `rhythm_dependency_smoke` aggregate dependency/runtime identity only;
- rollback target is exact commit `2ab73f0e445c1584fc6dce0112e3091985b4a575` if candidate deployment is implicated in a failure.

The existing `.github/workflows/v143-deploy-patched-worker.yml` may now be hardened with exact pins; its workflow-file commit is the deliberate single production promotion trigger.

## NEXT STEP

1. Harden `.github/workflows/v143-deploy-patched-worker.yml` with exact blob pins and no-model worker-only verification.
2. That workflow-file commit deliberately triggers one serialized production worker deployment.
3. Observe terminal result and aggregate artifact.
4. GREEN → checkpoint production scheduler promotion CLOSED/GREEN. Failure → diagnose before rollback; rollback only if candidate deployment is implicated.

### Hard stops

- No reference-facing scoring/quality verdict/restricted assets.
- No closed performance/cache/concurrency/Gate-2 reruns.
- No additional model-bearing route run absent a unique demonstrated need.
- No Vercel or bridge production change; no whole-branch/main merge for this promotion.
- No weakening exact parity/fail-closed criteria or retention boundaries.
