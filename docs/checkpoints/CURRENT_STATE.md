# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 08:43 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO REFERENCE-FACING QUALITY VERDICT** — performance/identity/routing/product-health diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`.
- Async authorization is limited to transient structured-result handoff: no raw-audio/stem/model persistence, no long-term result cache, result partition TTL <= 900 seconds.

## Production baseline — STILL UNCHANGED BY ASYNC WORK

- Vercel/web `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`.
- Production deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, unchanged.
- Production route blob `06234db3e1cc1680b18fd62a765862b213ede3db`, `maxDuration = 150`.
- Production HTTP bridge blob `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`, unchanged.
- Promoted worker remains `dadrock-v143-ai-tab-live/rhythm_v143_request`, live endpoint blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`, scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- No `main` merge; no worker/model/scheduler modification in async work.

## Breakthrough diagnosis — CLOSED

- Synchronous production run `33965269193` / job `101304165477` / artifact `9969253856`: HTTP `504`, `150.66095s`.
- Prior equivalent request ~`150.931s`; Vercel synchronous ceiling remains the product blocker.
- Log-only run `33965453476` / job `101304658150` / artifact `9969270692` proved concurrency live: direct Demucs `0.306s`, RoFormer `0.319s`, RoFormer done/cascade start `84.079s`.
- **Scheduler breakthrough YES; synchronous product breakthrough NO.**

## Async plan

Plan `docs/checkpoints/V143_ASYNC_JOB_ARCHITECTURE_PLAN.md`, commit `e0aef99dcdf931b66c0e1a081160e3cc5c6cb3c2`.

Rhythm start -> immediate HMAC-signed opaque job token -> browser polls Vercel -> Vercel polls Modal bridge -> bridge reads transient structured-result Queue partition -> existing Vercel anti-leakage/product pipeline -> browser receives tab -> ACK clears partition. TTL `900s` fallback. Lead/Bass remain synchronous.

## Current async candidates — BRANCH ONLY

- Protocol `analyzer/v143_async_job_protocol.py`: commit `1b139994b9bf8572093e6644a61b6fde8c14cd89`, blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`.
- Bridge `analyzer/v143_modal_http_endpoint.py`: **current commit `24bc086848b3903cb26c7032349fd5f3f289bae0`, blob `e0cecefacead73d69a905fd6bfb2049b21c87bc3`**.
- Vercel route `app/api/analyze-audio-tab/route.js`: commit `4c94ae0e8bf88f8c0f7f0053c0dec5ad32522b79`, blob `742954146a86aa36485d0bbdb3fbd6691a64a712`.
- `/ai-tab` page: polling commit `d07b08545296c579dbdb0faf2efc0843cc45d24e`, blob `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.

Current bridge properties:

- default production resource names unchanged; isolated gate names can be supplied at deploy time;
- deploy-resolved app/Queue names are baked into `http_image` via `legacy.image.env(...)` **before** local-source mounts, satisfying Modal image build ordering;
- default synchronous `analyze` and Lead/Bass fallback preserved;
- Rhythm `start/status/ack` added;
- lightweight orchestrator calls unchanged promoted worker;
- result-only Queue partition, zlib/chunked, TTL 900, ACK clear;
- bounded generic failures only; no credential-bearing exception persistence;
- synthetic `async_protocol_smoke()` performs HMAC + Queue write/read/decode/clear with tiny fake tab and no audio/model.

## Source/build evidence

### Protocol source gate

- Last fully authoritative pre-image-order run: `33966541875`, job `101307557030`, artifact `9969602450`, digest `sha256:92eb21640ac52f7fa16fea7916fa534687aa462e7dbe56ff086292854009df85` — GREEN.
- Current bridge change automatically requires a fresh source-gate run; no production deployment is authorized until current pins return GREEN.

### Vercel composition gate

- Route/page semantics were GREEN in run `33966433579`, artifact `9969569077`.
- Current gate has been repinned to bridge blob `e0cecefa...` in commit `16f50a4c8908f975006d58070990f5bab1f296e3`; fresh current-pin result pending at this checkpoint.

### Vercel preview build

- run `33966323815`, job `101306988163`: **SUCCESS**;
- artifact `9969549184`, digest `sha256:810c8c3c3012cb43a37d3b463735b9fc4dcbd2a06a4d2c7fd2407c03e2402a5f`;
- preview environment pulled and `vercel build` succeeded locally; no deployment/model/audio execution.

## Isolated Modal smoke history — FAIL-CLOSED DIAGNOSIS

### Attempt 1 — run `33966600313`, job `101307715834`

- exact source boundary and isolated app deployment succeeded;
- synthetic Queue/HMAC logic itself returned `tokenVerified=true`, `queueRoundtrip=true`, `queueCleared=true`, TTL 900, no audio/model;
- **failed isolation assertion** because remote container resolved default `appName=dadrock-v143-http-bridge` / `queueName=dadrock-v143-async-results` rather than runner overrides;
- no worker/model/audio call occurred; only a random synthetic Queue partition was used and cleared;
- cleanup initially lacked noninteractive confirmation.

Diagnosis: runner environment selected the isolated app at deploy time, but the override names were not present when the remote module initialized.

### Attempt 2 — run `33966716295`, job `101308026027`

- stale isolated app was successfully stopped using `--yes` before deployment;
- deployment failed before any function invocation because Modal forbids build step `.env()` after `add_local_*` mounts;
- synthetic smoke was skipped; no audio/model activity;
- final isolated-app cleanup reports app already stopped.

Correction now landed:

- bridge blob `e0cecefa...` moves `.env({...})` **before** `.add_local_python_source(...)`, matching Modal's required image ordering;
- Vercel composition gate repinned to this blob;
- isolated workflow repinned in commit `c65614896f32a60fddca75d4a2dc3453484c6eda`, with stale pre-stop and final `--yes` cleanup.

## NEXT STEP

1. Observe fresh current-pin protocol/Vercel source gates and isolated smoke from the ordering-fixed bridge; no model/audio invocation.
2. Isolated smoke must prove remote `appName=dadrock-v143-http-bridge-async-gate`, `queueName=dadrock-v143-async-results-gate`, HMAC true, Queue roundtrip true, Queue cleared true, TTL 900, audio/model false, then stop isolated app.
3. Only after all are GREEN: checkpoint and deploy backward-compatible bridge candidate to production; run the same synthetic/no-model smoke there.
4. Then Vercel preview deploy + no-model protocol check + exactly one model-bearing async preview E2E proving completion past 150 seconds.
5. Production Vercel promotion only after preview E2E GREEN.

### Hard stops

- No model-bearing test before preview async E2E.
- No model/scheduler changes as part of async wiring.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async result storage.
- No async result TTL above 15 minutes; no persistent result cache.
- No whole-branch merge to `main`.
- No production bridge deployment until current isolated smoke + current source pins are GREEN.
- No production Vercel promotion before preview protocol/E2E proof.
