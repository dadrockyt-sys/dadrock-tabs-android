# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 08:56 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO REFERENCE-FACING QUALITY VERDICT** — performance/identity/routing/product-health diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`.
- Async authorization is limited to transient structured-result handoff: no raw-audio/stem/model persistence, no long-term result cache, Queue partition TTL <= 900 seconds.

## Production state

Production Vercel/web remains unchanged by async work:

- `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`;
- production deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM` unchanged;
- production route blob still `06234db3e1cc1680b18fd62a765862b213ede3db`, synchronous `maxDuration=150`;
- no `main` merge and no production Vercel promotion yet.

Promoted L4 worker remains unchanged:

- `dadrock-v143-ai-tab-live/rhythm_v143_request`;
- live endpoint blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`;
- seeded scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.

Production HTTP bridge is the backward-compatible async candidate:

- bridge blob `e0cecefacead73d69a905fd6bfb2049b21c87bc3`;
- protocol blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`;
- rollback bridge blob `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`;
- synchronous `analyze` and Lead/Bass fallback preserved;
- Rhythm `start/status/ack` enabled with transient Queue `dadrock-v143-async-results`.

## Breakthrough diagnosis — CLOSED

- synchronous production run `33965269193` / job `101304165477` / artifact `9969253856`: HTTP `504` at `150.66095s`;
- prior equivalent ~`150.931s`;
- log-only run `33965453476` / job `101304658150` proved live scheduler overlap: direct Demucs `0.306s`, RoFormer `0.319s`, RoFormer done/cascade start `84.079s`;
- **scheduler breakthrough YES; synchronous product breakthrough NO**.

## Async architecture

Plan `docs/checkpoints/V143_ASYNC_JOB_ARCHITECTURE_PLAN.md`, commit `e0aef99dcdf931b66c0e1a081160e3cc5c6cb3c2`.

Rhythm start -> immediate HMAC-signed token -> browser polls Vercel -> Vercel polls bridge -> transient structured-result Modal Queue -> existing Vercel V143 safety/product pipeline -> browser receives tab -> ACK clear. TTL `900s`. Lead/Bass remain synchronous.

Current branch candidates:

- route blob `742954146a86aa36485d0bbdb3fbd6691a64a712`;
- `/ai-tab` page blob `de39f2715c6875d757ef730c9e3182ccd4aa00a4`;
- bridge blob `e0cecefacead73d69a905fd6bfb2049b21c87bc3`;
- worker/scheduler unchanged as pinned above.

## Async gates — GREEN

- Protocol source current-pin run `33966778940`: SUCCESS; artifact `9969677990`, digest `sha256:b239317ee7ec9c4c6146567658140d4f0459c14ef77218ad4b61585673d666ef`.
- Vercel wiring/composition run `33966794524`: SUCCESS; artifact `9969683328`, digest `sha256:9b22f8cdce8816814dfd6f414cb9fe72b27e727e342f06061c18a9a984225bf3`.
- Vercel preview build run `33966323815`, job `101306988163`: SUCCESS; artifact `9969549184`, digest `sha256:810c8c3c3012cb43a37d3b463735b9fc4dcbd2a06a4d2c7fd2407c03e2402a5f`.
- Isolated Modal smoke run `33966816672`, job `101308290865`: SUCCESS; artifact `9969693296`, digest `sha256:5a00636970d7426f5c83c4f498e84a4bc6b200700836e94184fd7f272b0d0b53`; HMAC/Queue/clear/TTL=900 all GREEN; no production worker/model/audio.
- Production bridge deploy/synthetic smoke run `33967130980`, job `101309120073`: SUCCESS; artifact `9969786854`, digest `sha256:fb1d8267a3241fe4d09343b50a286ce0635f705374326b36ea8e9732c276fdf5`; no worker/model/audio execution.

## Authoritative async Vercel Preview — DEPLOYED / ACCESS CHECK PENDING

Preview workflow was reduced to one authoritative deployment using concurrency `cancel-in-progress=true`:

- earlier run #1 `33967223069`: CANCELLED by newer run;
- run #2 `33967258052`: CANCELLED before execution;
- authoritative run #3 `33967294781`, job `101309569318`;
- exact source boundary + branch build + prebuilt preview deployment all SUCCESS;
- immutable preview deployment ID `dpl_8QZKRzPCAiDBauHmkX1SyasHn82s`;
- immutable preview URL `https://dadrock-tabs-android-r0h3rn5la-stephen-mcnally-s-projects.vercel.app`;
- Vercel state READY; target is Preview (`target=null`), production alias untouched;
- route/page/bridge pins exactly `74295414...` / `de39f271...` / `e0cecefa...`;
- aggregate deployment artifact `9969859750`, digest `sha256:fe28c076faf646087f67b71892b71968f545f0a5ad3e8fa45ed3edeb01edb68a`;
- no model/audio/reference-facing activity occurred.

The workflow's `/ai-tab` check returned **403** after successful deployment. Job logs show this is Vercel Deployment Protection from the `vercel curl` access path; it is not a build/app execution failure. Do not disable or weaken preview protection. The immutable preview remains READY.

## Legacy closed scheduler gate note

Old scheduler structure run `33966778906` failed solely because its frozen HTTP-bridge pin expects `9a550f0a...` instead of the authorized new bridge `e0cecefa...`. Scheduler/worker source unchanged. Do not reopen/repin that closed gate.

## ASYNC PROMOTION STATUS

- Protocol/current source: **GREEN/CLOSED**.
- Route/UI composition: **GREEN/CLOSED**.
- Production async bridge: **PROMOTED + SYNTHETIC GREEN/CLOSED**.
- Authoritative Vercel Preview: **READY / NOT PRODUCTION**.
- Protected preview runtime access: **403 DIAGNOSIS REQUIRED; no code failure demonstrated**.
- Model-bearing async preview E2E: **NOT YET RUN**.
- Production Vercel: **UNCHANGED**.

## NEXT STEP

1. Use the immutable preview `dpl_8QZKRzPCAiDBauHmkX1SyasHn82s`; do not deploy another preview.
2. Run a no-model protected-preview protocol check using an explicit authenticated/trusted access method without changing Deployment Protection.
3. Check `/ai-tab` 200 and POST invalid async token -> fail closed (expected 400) through `/api/analyze-audio-tab`; this must not spawn the worker.
4. If GREEN, checkpoint and authorize exactly one model-bearing async Rhythm preview E2E.
5. E2E breakthrough criterion: start returns far below 150s, polling remains alive beyond the old 150s boundary, completed result traverses the existing V143 safety/product pipeline, and ACK clears the transient Queue partition.
6. Only after E2E GREEN may production Vercel be promoted.

### Hard stops

- No second preview deployment.
- No model-bearing test before protected preview protocol check is GREEN.
- No Deployment Protection weakening/disablement.
- No model/scheduler changes.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async result storage.
- No async result TTL above 15 minutes; no persistent result cache.
- No whole-branch merge to `main`.
- No production Vercel promotion before preview E2E GREEN.
