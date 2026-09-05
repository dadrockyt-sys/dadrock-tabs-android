# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 09:06 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO REFERENCE-FACING QUALITY VERDICT** — performance/identity/routing/product-health diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`.
- Async authorization is transient structured-result handoff only: no raw-audio/stem/model persistence, no long-term result cache, Queue partition TTL <= 900 seconds.

## Production state

Production Vercel remains unchanged:

- `main` `bb992d901e78ab19645f8edc8e330d5a142ebd8e`;
- production deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`;
- production route blob `06234db3e1cc1680b18fd62a765862b213ede3db`, synchronous `maxDuration=150`;
- no `main` merge / no production Vercel promotion.

Promoted L4 worker unchanged:

- `dadrock-v143-ai-tab-live/rhythm_v143_request`;
- live endpoint blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`;
- scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.

Production HTTP bridge is the backward-compatible async bridge:

- bridge blob `e0cecefacead73d69a905fd6bfb2049b21c87bc3`;
- protocol blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`;
- rollback bridge blob `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`;
- sync `analyze` + Lead/Bass preserved;
- Rhythm `start/status/ack` + transient Queue `dadrock-v143-async-results` enabled.

## Breakthrough diagnosis — CLOSED

- synchronous production run `33965269193` / job `101304165477` / artifact `9969253856`: HTTP `504` at `150.66095s`;
- prior equivalent ~`150.931s`;
- log-only run `33965453476` / job `101304658150` proved live scheduler overlap: direct Demucs `0.306s`, RoFormer `0.319s`, RoFormer done/cascade start `84.079s`;
- **scheduler breakthrough YES; synchronous product breakthrough NO**.

## Async architecture

Plan `docs/checkpoints/V143_ASYNC_JOB_ARCHITECTURE_PLAN.md`, commit `e0aef99dcdf931b66c0e1a081160e3cc5c6cb3c2`.

Rhythm start -> immediate signed token -> browser polls Vercel -> Vercel polls bridge -> transient structured-result Modal Queue -> existing V143 safety/product pipeline -> browser gets result -> ACK clears Queue. TTL `900s`. Lead/Bass stay synchronous.

Current source pins:

- route blob `742954146a86aa36485d0bbdb3fbd6691a64a712`;
- `/ai-tab` page blob `de39f2715c6875d757ef730c9e3182ccd4aa00a4`;
- bridge blob `e0cecefacead73d69a905fd6bfb2049b21c87bc3`;
- worker/scheduler unchanged as above.

## Closed async evidence — GREEN

- Protocol current-pin run `33966778940`, artifact `9969677990`, digest `sha256:b239317ee7ec9c4c6146567658140d4f0459c14ef77218ad4b61585673d666ef`.
- Vercel wiring/composition run `33966794524`, artifact `9969683328`, digest `sha256:9b22f8cdce8816814dfd6f414cb9fe72b27e727e342f06061c18a9a984225bf3`.
- Preview build run `33966323815` / job `101306988163`, artifact `9969549184`, digest `sha256:810c8c3c3012cb43a37d3b463735b9fc4dcbd2a06a4d2c7fd2407c03e2402a5f`.
- Isolated Modal bridge smoke run `33966816672` / job `101308290865`, artifact `9969693296`, digest `sha256:5a00636970d7426f5c83c4f498e84a4bc6b200700836e94184fd7f272b0d0b53`; HMAC/Queue/clear/TTL 900 GREEN; no model/audio/production worker.
- Production bridge deploy + synthetic smoke run `33967130980` / job `101309120073`, artifact `9969786854`, digest `sha256:fb1d8267a3241fe4d09343b50a286ce0635f705374326b36ea8e9732c276fdf5`; no model/audio.

## Original async Vercel Preview — SOURCE GOOD / ENVIRONMENT INCOMPLETE

Duplicate Preview attempts were collapsed:

- `33967223069` CANCELLED;
- `33967258052` CANCELLED;
- source-authoritative Preview run `33967294781`, job `101309569318`;
- exact build/deploy succeeded;
- deployment ID `dpl_8QZKRzPCAiDBauHmkX1SyasHn82s`;
- URL `https://dadrock-tabs-android-r0h3rn5la-stephen-mcnally-s-projects.vercel.app`;
- READY / Preview only; production alias untouched;
- route/page/bridge blobs exactly `74295414...` / `de39f271...` / `e0cecefa...`;
- artifact `9969859750`, digest `sha256:fe28c076faf646087f67b71892b71968f545f0a5ad3e8fa45ed3edeb01edb68a`;
- no model/audio.

This deployment is now **invalidated as the final E2E target by a demonstrated Preview-environment omission**, not by source/build failure.

## Protected Preview diagnostics — NO MODEL/AUDIO

Historical protection access is known-good (`33843200741`, job `100929522781`): inspect then env-token `vercel curl` returned `/ai-tab` 200 with Deployment Protection enabled.

Current diagnostics:

1. `33967515872` / job `101310124066`: CLI syntax mistake only; no auth/model test.
2. `33967633461` / job `101310442042`: protected access worked; `/ai-tab` **200**; async status request **400 ~1.00s**; no worker/model/audio. Artifact `9969940088`, digest `sha256:f807e3a871932e493828c1c3ba0ad896b998fda1606e9c6e5dbc563b9a6e1c49`.
3. `33967744101` / job `101310731627`: `/ai-tab` **200**; structurally-valid bad-signature status request **400 in 0.427092s**; no worker/model/audio. Artifact `9969971331`, digest `sha256:27adcc38e1084132a098bb49742671d3580a97f6722f221d449491fc09d7a110`.
4. **Decisive environment diagnosis:** workflow commit `4d9aef11f4f0b07e52dd87445750e373e883ccaa`; run `33967838240`, job `101310981516`; artifact `9970000315`, digest `sha256:a891ad80fdb3e2695ea81cb4848fe1043b80e7a37187d0b30be84d3810222e1e`.

Decisive result:

- `requestErrorClass = v143_preview_url_not_selected`;
- Preview environment name `ANALYZER_API_URL_V143`: **ABSENT**;
- Preview environment name `ANALYZER_API_URL`: present;
- Preview environment name `ANALYZER_API_TOKEN`: present;
- no worker spawn, no model execution, no audio read, no reference inputs/scoring/verdict.

Therefore the current Preview's Rhythm async request is rejected by the Vercel route **before bridge/HMAC** because `usingV143RhythmAnalyzer=false`. This fully explains the repeated 400s and is a real Preview environment wiring defect.

The page-status result varied between 200 and 403 across beta `vercel curl` calls under Deployment Protection, but this is separate from the route diagnosis: prior current runs already proved page 200, and the environment-name + fixed error-class diagnosis is decisive.

## Required narrow wiring correction — AUTHORIZED

The missing variable is configuration, not model/scheduler code. The known production V143 bridge endpoint is:

`https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`

`ANALYZER_API_TOKEN` remains a separate secret and is already present in Preview. Add **only** `ANALYZER_API_URL_V143` to the Vercel Preview environment. Do not change Production environment values.

Because Vercel environment changes apply to future deployments, one replacement Preview is now justified despite the earlier no-second-preview stop: the original Preview is demonstrably incapable of selecting V143 Rhythm due missing configuration. The replacement must use the same exact route/page blobs and must remain Preview-only.

Before replacement deployment, verify Preview also contains `BLOB_READ_WRITE_TOKEN` by name (no value disclosure); it is required for real `start` requests.

## Legacy closed scheduler gate note

Old scheduler structure run `33966778906` failed solely on its frozen pre-async HTTP bridge pin (`9a550f0a...` vs authorized `e0cecefa...`). Worker/scheduler unchanged. Do not reopen/repin.

## ASYNC PROMOTION STATUS

- Protocol/source: **GREEN/CLOSED**.
- Route/UI composition: **GREEN/CLOSED**.
- Production async bridge: **PROMOTED + SYNTHETIC GREEN/CLOSED**.
- Original Preview source/build: **GREEN**, but environment is **INVALID FOR V143 RHYTHM** (`ANALYZER_API_URL_V143` absent).
- Narrow Preview environment correction: **NEXT**.
- Model-bearing async Preview E2E: **NOT YET RUN**.
- Production Vercel: **UNCHANGED**.

## NEXT STEP

1. Add `ANALYZER_API_URL_V143=https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run` to **Preview only** using Vercel CLI; verify `BLOB_READ_WRITE_TOKEN` name is also present; do not expose secret values.
2. Create exactly one replacement Preview from the same route/page/bridge source pins; production target must remain false.
3. Run no-model protected Preview protocol check: `/ai-tab` reachable and bad HMAC reaches bridge rejection; worker/model/audio remain zero.
4. If GREEN, checkpoint replacement Preview and authorize exactly one real async Rhythm Preview E2E.
5. Breakthrough criterion: `start` returns far below 150s; polling survives beyond the old 150s boundary if needed; completed result passes existing V143 safety/product path; ACK clears transient Queue partition.
6. Production Vercel promotion only after E2E GREEN.

### Hard stops

- No model-bearing request before replacement Preview no-model protocol is GREEN.
- No Production Vercel environment change or promotion yet.
- No Deployment Protection weakening/disablement.
- No model/scheduler change.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async result storage.
- No TTL above 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.
