# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 00:51 America/Toronto  
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
- HTTP bridge source blob `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`; bridge dynamically resolves worker app `dadrock-v143-ai-tab-live`.
- Live endpoint blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`.

## Candidate and rollback

- Scheduler implementation commit `6772a0ca1d700ea6861cd4401b51e093144c8d26`.
- Candidate scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Rollback commit `2ab73f0e445c1584fc6dce0112e3091985b4a575`: same live endpoint blob `111bf14a...`, prior serialized scheduler blob `250534e516cad36e49cae35b6eab2b88654be2d3`.

## Closed promotion evidence

- Gate 1 structural: run `33942915753` / job `101243642285` — **GREEN/CLOSED**.
- Gate 2 exact approved-fixture runtime: run `33943100948` / job `101244148835` / artifact `9962641557` — **GREEN/CLOSED**.
- Gate 3A normal-routing composition: run `33945157629` / job `101249801382` / artifact `9963085825` (`sha256:9084a0d17ca44154e66a89f78546b6e210e3a302110e9e560c99b9f20a39ad09`) — **GREEN/CLOSED**.
- `MODEL_BEARING_E2E_NOT_JUSTIFIED`; normal-routing pre-production evidence boundary **GREEN/CLOSED**.

## Production plan

- `docs/checkpoints/V143_SEEDED_SCHEDULER_PRODUCTION_PLAN.md`, commit `b84d7c05cac15bc2d3196278502029a196412541`.
- Whole-branch merge rejected (branch 139 ahead / 227 behind `main`).
- Worker-only Modal redeploy; no Vercel, HTTP bridge, or `main` change.
- Post-deploy verification: no-audio/no-separator-execution `rhythm_dependency_smoke` only.

## Production worker promotion — IN PROGRESS

Deliberate workflow trigger:

- commit `86f83f6bba33bbe7378ba1eed7294be884e30e45`;
- `.github/workflows/v143-deploy-patched-worker.yml` blob `39e44d4275578da20c9110ea29ce1a538ab3169f`;
- Actions run `33945389816`;
- job `101250418913`;
- serialized concurrency group `v143-deploy-patched-worker`, `cancel-in-progress: false`.

Current verified steps:

- checkout exact promotion branch head: **SUCCESS**;
- exact source/safety gate: **SUCCESS**;
- Python setup: **SUCCESS**;
- pinned Modal CLI install: **IN PROGRESS** at this checkpoint;
- authentication/deploy/dependency-smoke/evidence upload pending.

The pre-deploy source gate verified exact blobs before any Modal write:

- live endpoint `111bf14a8f91045d3478901f8e36b88a2e7f181a`
- scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`
- deterministic wrapper `28b3e6fe0eb761178b142cf7dcbda533f0bf918d`
- deterministic provider `3c6dcf9b8e7360ba1dd886810f3c14c05ac0579b`
- stem provider `cd180bfb35e8110f031504035af5f11e502c3dc6`
- request adapter `6d1787f34a3b7ca781ced8e5695993a3777406a8`
- Rhythm router `7849f33cd3b849283ccebfda9f721cc40704231e`.

Deployment scope remains only `modal deploy --env main analyzer/v143_modal_live_endpoint.py`. No approved fixture/model-bearing route call is part of this workflow.

## NEXT STEP

1. Observe run `33945389816` to terminal state without creating another trigger.
2. Inspect aggregate `v143-patched-worker-deploy` artifact.
3. GREEN → checkpoint production scheduler promotion CLOSED/GREEN. Failure → diagnose first; rollback only if candidate deployment is implicated.

### Hard stops

- No second deployment trigger while run `33945389816` is unresolved.
- No reference-facing scoring/quality verdict/restricted assets.
- No closed performance/cache/concurrency/Gate-2 reruns.
- No extra model-bearing normal-route execution absent unique demonstrated need.
- No Vercel/bridge/main change; no whole-branch merge.
- No weakening exact parity/fail-closed criteria or retention boundaries.
