# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 09:01 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO REFERENCE-FACING QUALITY VERDICT** — performance/identity/routing/product-health diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`.
- Async authorization is limited to transient structured-result handoff only: no raw-audio/stem/model persistence, no long-term result cache, Queue partition TTL <= 900 seconds.

## Production state

Production Vercel remains unchanged:

- `main` `bb992d901e78ab19645f8edc8e330d5a142ebd8e`;
- production deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`;
- production route blob `06234db3e1cc1680b18fd62a765862b213ede3db`, synchronous `maxDuration=150`;
- no `main` merge and no production Vercel promotion.

Promoted L4 worker unchanged:

- `dadrock-v143-ai-tab-live/rhythm_v143_request`;
- live endpoint blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`;
- scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.

Production HTTP bridge is the backward-compatible async bridge candidate:

- current bridge blob `e0cecefacead73d69a905fd6bfb2049b21c87bc3`;
- protocol blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`;
- rollback bridge blob `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`;
- synchronous `analyze` + Lead/Bass preserved;
- Rhythm `start/status/ack` + transient Queue `dadrock-v143-async-results` enabled.

## Breakthrough diagnosis — CLOSED

- synchronous production run `33965269193` / job `101304165477` / artifact `9969253856`: HTTP `504` at `150.66095s`;
- prior equivalent ~`150.931s`;
- log-only run `33965453476` / job `101304658150` proved live scheduler overlap: direct Demucs `0.306s`, RoFormer `0.319s`, RoFormer done/cascade start `84.079s`;
- **scheduler breakthrough YES; synchronous product breakthrough NO**.

## Async architecture

Plan `docs/checkpoints/V143_ASYNC_JOB_ARCHITECTURE_PLAN.md`, commit `e0aef99dcdf931b66c0e1a081160e3cc5c6cb3c2`.

Rhythm start -> immediate signed token -> browser polls Vercel -> Vercel polls bridge -> transient structured-result Modal Queue -> existing V143 safety/product pipeline -> browser gets result -> ACK clears Queue partition. TTL `900s`. Lead/Bass stay synchronous.

Current branch source pins:

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

## Authoritative async Vercel Preview

Duplicate preview attempts were collapsed with concurrency:

- run `33967223069`: CANCELLED by newer run;
- run `33967258052`: CANCELLED;
- authoritative run `33967294781`, job `101309569318`;
- exact source boundary/build/deploy all SUCCESS;
- immutable Preview deployment ID `dpl_8QZKRzPCAiDBauHmkX1SyasHn82s`;
- URL `https://dadrock-tabs-android-r0h3rn5la-stephen-mcnally-s-projects.vercel.app`;
- Vercel state READY, production alias untouched;
- route/page/bridge pins exactly `74295414...` / `de39f271...` / `e0cecefa...`;
- artifact `9969859750`, digest `sha256:fe28c076faf646087f67b71892b71968f545f0a5ad3e8fa45ed3edeb01edb68a`;
- no model/audio/reference-facing activity.

Its workflow concluded FAILURE only because `/ai-tab` returned 403 from Vercel Deployment Protection after successful deploy. Do not redeploy or weaken protection.

## Protected Preview access diagnosis

Historical known-good evidence exists:

- run `33843200741`, job `100929522781`: SUCCESS;
- same Vercel CLI `59.11.2` and `VERCEL_TOKEN` environment;
- sequence was `vercel inspect <preview> --wait --token=...` then ordinary `vercel curl ... --deployment <preview>`;
- `/ai-tab` returned 200 with 38,016 bytes while Deployment Protection remained enabled;
- artifact `9925639186`.

First current immutable-preview protocol attempt:

- workflow commit `c2c2572916d95cbd9313bfe676e535950cd4a2f5`;
- run `33967515872`, job `101310124066`: FAILURE;
- **diagnostic only**: it did not actually test auth because command syntax `vercel --token ... curl` caused native curl to receive `--token` and abort (`curl: option --token: is unknown`);
- no model/audio/worker spawn and no useful result artifact.

Corrected protocol workflow:

- commit `3342f1012cd10bf8a800d81b1285cbb258bcc761`;
- current run `33967633461`, job `101310442042`: IN PROGRESS;
- exact historical protected Preview access shape restored: inspect first, then env-token `vercel curl`;
- test is no-model: GET `/ai-tab` plus POST `status` with deliberately invalid signed token; expected page 200 and invalid token 400; worker spawn unauthorized/impossible from invalid token.

If this exact historical access sequence still fails due Deployment Protection, next permitted diagnostic is GitHub Actions trusted-source OIDC (`id-token: write` + `x-vercel-trusted-oidc-idp-token`) without changing any Vercel protection setting.

## Legacy closed scheduler gate note

Old scheduler structure run `33966778906` failed solely on its frozen pre-async HTTP bridge pin (`9a550f0a...` vs authorized `e0cecefa...`). Worker/scheduler unchanged. Do not reopen or repin that closed gate.

## ASYNC PROMOTION STATUS

- Protocol/source: **GREEN/CLOSED**.
- Route/UI composition: **GREEN/CLOSED**.
- Production async bridge: **PROMOTED + SYNTHETIC GREEN/CLOSED**.
- Immutable Vercel Preview: **READY / NOT PRODUCTION**.
- Corrected protected-preview no-model protocol run: **IN PROGRESS**.
- Model-bearing async preview E2E: **NOT YET RUN**.
- Production Vercel: **UNCHANGED**.

## NEXT STEP

1. Observe run `33967633461` to terminal; do not retrigger.
2. If GREEN, capture aggregate artifact and checkpoint page 200 + invalid token 400 + zero worker/model/audio.
3. If still protected, use GitHub Actions trusted-source OIDC without changing Deployment Protection.
4. Once no-model preview protocol is GREEN, authorize exactly one model-bearing async Rhythm Preview E2E on immutable deployment `dpl_8QZKRzPCAiDBauHmkX1SyasHn82s`.
5. Breakthrough criterion: start returns far below 150s, polling remains alive beyond old synchronous boundary if processing continues that long, completed result passes existing V143 safety/product path, and ACK clears transient Queue result.
6. Production Vercel promotion only after E2E GREEN.

### Hard stops

- No second preview deployment.
- No model-bearing request before protected Preview protocol is GREEN.
- No Deployment Protection weakening/disablement.
- No model/scheduler change.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async result storage.
- No TTL above 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.
- No production Vercel promotion before async Preview E2E GREEN.
