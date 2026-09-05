# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 08:46 America/Toronto  
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

## Async architecture

Plan: `docs/checkpoints/V143_ASYNC_JOB_ARCHITECTURE_PLAN.md`, commit `e0aef99dcdf931b66c0e1a081160e3cc5c6cb3c2`.

Rhythm start -> immediate HMAC-signed opaque job token -> browser polls Vercel -> Vercel polls Modal bridge -> bridge reads transient structured-result Queue partition -> existing Vercel anti-leakage/product pipeline -> browser receives tab -> ACK clears partition. TTL `900s` fallback. Lead/Bass remain synchronous.

## Current async candidates — BRANCH ONLY

- Protocol `analyzer/v143_async_job_protocol.py`: blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`.
- Bridge `analyzer/v143_modal_http_endpoint.py`: commit `24bc086848b3903cb26c7032349fd5f3f289bae0`, blob `e0cecefacead73d69a905fd6bfb2049b21c87bc3`.
- Vercel route `app/api/analyze-audio-tab/route.js`: commit `4c94ae0e8bf88f8c0f7f0053c0dec5ad32522b79`, blob `742954146a86aa36485d0bbdb3fbd6691a64a712`.
- `/ai-tab` page: polling commit `d07b08545296c579dbdb0faf2efc0843cc45d24e`, blob `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.

Bridge properties:

- default production resource names unchanged; isolated gate names can be supplied at deploy time;
- deploy-resolved app/Queue names are baked into `http_image` via `legacy.image.env(...)` before local-source mounts, satisfying Modal image build ordering;
- default synchronous `analyze` and Lead/Bass fallback preserved;
- Rhythm `start/status/ack` added;
- lightweight orchestrator calls the unchanged promoted worker;
- result-only Queue partition, zlib/chunked, TTL 900, ACK clear;
- bounded generic failures only; no credential-bearing exception persistence;
- synthetic `async_protocol_smoke()` exercises HMAC + Queue write/read/decode/clear with tiny fake structured result and invokes no audio/model.

## Current-pin source/build evidence — GREEN

### Protocol source gate — GREEN/CLOSED

- run `33966778940` / workflow `V143 Async Job Protocol Gate`: **SUCCESS**;
- head/source commit `24bc086848b3903cb26c7032349fd5f3f289bae0`;
- artifact `9969677990`, digest `sha256:b239317ee7ec9c4c6146567658140d4f0459c14ef77218ad4b61585673d666ef`;
- current bridge blob `e0cecefa...` therefore has fresh source-only protocol evidence.

### Vercel wiring/composition gate — GREEN/CLOSED

- repin commit `16f50a4c8908f975006d58070990f5bab1f296e3`;
- run `33966794524` / workflow `V143 Async Vercel Wiring Gate`: **SUCCESS**;
- artifact `9969683328`, digest `sha256:9b22f8cdce8816814dfd6f414cb9fe72b27e727e342f06061c18a9a984225bf3`;
- route/page async semantics, V143 safety/product postprocessing, frozen worker/scheduler identities, and current bridge pin compose cleanly.

### Vercel preview build — GREEN

- run `33966323815`, job `101306988163`: **SUCCESS**;
- artifact `9969549184`, digest `sha256:810c8c3c3012cb43a37d3b463735b9fc4dcbd2a06a4d2c7fd2407c03e2402a5f`;
- preview environment pulled and `vercel build` succeeded locally; no deployment/model/audio execution.

## Isolated Modal bridge smoke — GREEN/CLOSED

Ordering-fixed isolated workflow source commit `c65614896f32a60fddca75d4a2dc3453484c6eda`.

- run `33966816672`, job `101308290865`: **SUCCESS**;
- artifact `9969693296`, digest `sha256:5a00636970d7426f5c83c4f498e84a4bc6b200700836e94184fd7f272b0d0b53`;
- exact bridge blob `e0cecefacead73d69a905fd6bfb2049b21c87bc3`;
- exact protocol blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`;
- frozen worker blob `111bf14a8f91045d3478901f8e36b88a2e7f181a` and scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8` recorded only as identity pins;
- remote `appName=dadrock-v143-http-bridge-async-gate`;
- remote `queueName=dadrock-v143-async-results-gate`;
- `tokenVerified=true`, `queueRoundtrip=true`, `queueCleared=true`, `resultTtlSeconds=900`;
- `rawAudioQueued=false`, `stemBytesQueued=false`, `modelExecuted=false`, `audioRead=false`;
- `referenceFacingInputs=0`, `referenceScoreCalls=0`, `qualityVerdictMade=false`;
- `productionBridgeTargeted=false`, `productionWorkerTargeted=false`;
- isolated app stopped successfully after smoke.

Prior isolated failures remain fail-closed diagnostic history only: run `33966600313` identified remote-name override initialization; run `33966716295` identified Modal `.env()` image ordering. Both invoked no model/audio.

## Legacy seeded-scheduler structural auto-run note

Bridge commit `24bc086...` also auto-triggered the already-closed legacy scheduler structural workflow: run `33966778906`, job `101308192747`, **FAILURE**. Logs show the sole failure is its intentionally frozen HTTP-bridge blob pin (`e0cecefa... != 9a550f0a...`). The scheduler/worker source was not changed. This is expected stale-pin behavior after the explicitly authorized bridge architecture change, **not a scheduler regression**, and the closed scheduler gate must not be rerun/repinned merely to bless unrelated bridge wiring.

## ASYNC PROMOTION STATUS

- Async protocol source gate: **GREEN/CLOSED on current bridge**.
- Vercel route/UI composition gate: **GREEN/CLOSED on current bridge**.
- Vercel branch preview build: **GREEN**.
- Isolated Modal Queue/HMAC bridge smoke: **GREEN/CLOSED**.
- Production bridge: **UNCHANGED so far**.
- Production Vercel: **UNCHANGED so far**.
- Model-bearing async preview E2E: **NOT YET RUN**.

## NEXT STEP

1. Deploy the backward-compatible bridge candidate `e0cecefa...` to the production bridge app only, with exact source pins and rollback to bridge blob `9a550f0a...` checkpointed.
2. Immediately run the bridge's synthetic/no-model protocol smoke against production resource names; it must prove token/Queue roundtrip/clear and no worker/model/audio invocation.
3. If GREEN, create/deploy a Vercel **preview** from the already-built async route/UI candidate; do not promote production.
4. Run no-model preview protocol checks.
5. Only then run exactly one model-bearing async Rhythm preview E2E proving a real result can arrive after the old 150-second boundary and be ACK-cleared.
6. Promote production Vercel only after preview E2E GREEN.

### Hard stops

- No model-bearing test before preview async E2E.
- No model/scheduler changes as part of async wiring.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async result storage.
- No async result TTL above 15 minutes; no persistent result cache.
- No whole-branch merge to `main`.
- No production Vercel promotion before preview protocol/E2E proof.
- No weakening exact parity/fail-closed criteria or retention boundaries.
