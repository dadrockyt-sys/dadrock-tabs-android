# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 08:38 America/Toronto  
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
- Promoted worker remains `dadrock-v143-ai-tab-live/rhythm_v143_request` with live endpoint blob `111bf14a8f91045d3478901f8e36b88a2e7f181a` and scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- No `main` merge; no worker/model/scheduler modification in async work.

## Breakthrough diagnosis — CLOSED

- Post-promotion synchronous production test run `33965269193`, job `101304165477`, artifact `9969253856`: HTTP `504`, `analysisEndToEndSeconds=150.66095`.
- Prior equivalent request ~`150.931s`; synchronous Vercel ceiling remains the blocker.
- Log-only run `33965453476`, job `101304658150`, artifact `9969270692` proved concurrency live: direct Demucs start `0.306s`, RoFormer start `0.319s`, RoFormer done/cascade start `84.079s`.
- **Scheduler breakthrough YES; synchronous product breakthrough NO.**

## Async architecture — PLAN CHECKPOINTED

Plan: `docs/checkpoints/V143_ASYNC_JOB_ARCHITECTURE_PLAN.md`, commit `e0aef99dcdf931b66c0e1a081160e3cc5c6cb3c2`.

Flow: Rhythm start -> immediate opaque signed job token -> browser polls Vercel -> Vercel polls Modal bridge -> bridge reads transient structured-result Queue partition -> existing Vercel V143 safety/product pipeline -> browser receives tab -> browser ACK clears partition. TTL `900s` is fallback cleanup. Lead/Bass remain synchronous.

## Current async source candidates — BRANCH ONLY

### Protocol

- `analyzer/v143_async_job_protocol.py`
- commit `1b139994b9bf8572093e6644a61b6fde8c14cd89`
- blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`
- HMAC-SHA256 job tokens; random job ids; JSON-only fail-closed result boundary; zlib transport; chunk `700000`; max TTL `900s`.

### Bridge candidate

- `analyzer/v143_modal_http_endpoint.py`
- commit `a4590088f2d3838ba0de5a58df3e42eb36916899`
- blob `c512516d47e79df86a780cb8a77bd528fe2a517a`
- default app/queue remain `dadrock-v143-http-bridge` / `dadrock-v143-async-results`;
- environment overrides `V143_HTTP_APP_NAME` and `V143_ASYNC_RESULT_QUEUE_NAME` permit isolated deployment testing without touching production;
- default synchronous `operation=analyze` and Lead/Bass fallback preserved;
- async Rhythm `start/status/ack` added;
- lightweight orchestrator calls unchanged promoted worker;
- Queue partition is result-only, zlib/chunked, TTL 900; ACK clears partition;
- bounded failure envelope avoids persisting credential-bearing traceback/error repr;
- `async_protocol_smoke()` exercises real HMAC + Queue write/read/decode/clear using a tiny synthetic tab, with **no audio/model call**;
- oversized/non-JSON completed results fail closed to a bounded failure result instead of leaving browser polling indefinitely.

### Vercel route candidate

- `app/api/analyze-audio-tab/route.js`
- commit `4c94ae0e8bf88f8c0f7f0053c0dec5ad32522b79`
- blob `742954146a86aa36485d0bbdb3fbd6691a64a712`
- Rhythm defaults async `start`; Lead/Bass remain synchronous `analyze`;
- start/status/ack control plane added;
- status/ack do not require Blob credentials;
- completed async worker result still passes the existing V143 anti-leakage contract and Jimmy-Paige/conditioning/mixture/dual-context/canary/product-placement pipeline before returning to browser.

### `/ai-tab` client candidate

- `app/ai-tab/page.js`
- async polling commit `d07b08545296c579dbdb0faf2efc0843cc45d24e`
- blob `de39f2715c6875d757ef730c9e3182ccd4aa00a4`
- Rhythm 202 response is polled at ~1.5-5s cadence, with a 21-minute browser processing window;
- job token remains in component/request memory only (not localStorage/sessionStorage/URL);
- browser ACK occurs only after a valid completed tab crosses the browser boundary; ACK failure is non-fatal because TTL cleanup remains active;
- existing preview/PDF/payment flow continues to await `requestTabAnalysis()` and therefore receives the same completed data shape.

## Async source/build gates

### Protocol gate — GREEN / CURRENT

- gate `analyzer/v143_async_job_protocol_gate.py` current commit `f6619218b773d1cefc126fd14ca8f776ba9d5a21`, blob `38e8976d89a662051e2168fb36a92519ac0af28a`;
- run `33966541875`, job `101307557030`: **SUCCESS**;
- artifact `9969602450`, digest `sha256:92eb21640ac52f7fa16fea7916fa534687aa462e7dbe56ff086292854009df85`;
- proved token roundtrip/tamper/wrong-secret failure, forced multi-chunk exact roundtrip, binary payload rejection, TTL/chunk boundaries, isolated resource names, synthetic Modal-smoke definition, async Rhythm-only boundary, synchronous fallback and Lead/Bass preservation;
- `modelExecuted=false`, `audioRead=false`, reference inputs/score calls `0`, quality verdict `false`.

### Vercel composition gate — GREEN / CURRENT RUNTIME PINS

- gate `analyzer/v143_async_vercel_wiring_gate.py` current commit `2febdb9501698a64f7b57230d1580a4d4b8a85df`, blob `80352557462a568dde653f8ed5e49d7439b02639`;
- run `33966433579`: **SUCCESS**;
- artifact `9969569077`, digest `sha256:69cd291d72688a5a6fb3d01b77ace5dabb18181d432070116b6448478e4a7835`;
- exact runtime pins: worker `111bf14a...`, scheduler `fc9b4c45...`, bridge `c512516d...`, protocol `1bd55017...`;
- proved Rhythm async default, Lead/Bass synchronous path, HTTP 202 processing, final result through existing safety/product pipeline, no client-side token persistence, ACK after browser receipt, no model code in Vercel.

### Vercel preview build gate — GREEN

- workflow commit `52ce441440e7aa09d8f35ec5a7bbd4741296a00f`;
- run `33966323815`, job `101306988163`: **SUCCESS**;
- artifact `9969549184`, digest `sha256:810c8c3c3012cb43a37d3b463735b9fc4dcbd2a06a4d2c7fd2407c03e2402a5f`;
- Vercel CLI `59.11.2` pulled preview environment and `vercel build` succeeded locally;
- deployment performed: false; model/audio execution: false.

## NEXT STEP — isolated Modal control-plane smoke only

1. Deploy current bridge blob `c512516d...` under isolated app `dadrock-v143-http-bridge-async-gate` and isolated Queue `dadrock-v143-async-results-gate` using environment overrides.
2. Invoke only `async_protocol_smoke()`; require HMAC verification + Queue roundtrip + Queue clear + TTL 900, while `modelExecuted=false` and `audioRead=false`.
3. Stop isolated app and checkpoint exact run/artifact before any production bridge deployment.
4. If GREEN, deploy the backward-compatible bridge candidate to production and run the same **synthetic/no-model** smoke.
5. Then create/deploy Vercel preview, run no-model route protocol checks, and perform exactly one model-bearing async preview E2E proving the request can survive past 150 seconds and eventually return a tab.
6. Production Vercel promotion only after that preview E2E is GREEN.

### Hard stops

- No duplicate model-bearing test before preview async E2E.
- No model/scheduler change as part of async wiring.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async result storage.
- No async result TTL above 15 minutes; no persistent result cache.
- No whole-branch merge to `main`.
- No production Vercel promotion before preview protocol/E2E proof.
- No weakening exact parity/fail-closed criteria or retention boundaries.
