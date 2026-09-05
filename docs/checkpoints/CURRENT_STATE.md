# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 12:19 America/Toronto  
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

## Preview routing correction — GREEN / NO MODEL

Original Preview was invalid for V143 Rhythm because Preview `ANALYZER_API_URL_V143` was absent. Narrow correction was authorized.

Replacement-routing workflow:

- commit `0c023bdf0e395ddf98501317472ea59e99a00eeb`;
- run `33968019067`, job `101311460970`: **SUCCESS**;
- exact source/scope boundary, Preview-only env add, build/deploy, and bad-HMAC bridge-path proof all succeeded;
- no production Vercel promotion and no model/audio request in that workflow.

## Modal “oneshot” start-loop diagnosis — NARROWED

User reported Modal showing a `oneshot` repeatedly looping/failing to start. Model-bearing E2E remains paused.

Read-only startup diagnosis:

- bridge+worker diagnosis workflow commits `476c22d10b68e532c685dd35c7cea0238098bb34` and `169a112552e79b763fb35a285decf63bc33fa10b`;
- runs `33980341926` / job `101344336671` and `33980388754` / job `101344455300`: **SUCCESS / diagnostic only**;
- production bridge history shows current v3 deployed `2026-09-05 12:49:53Z`;
- live worker history shows current v6 deployed `2026-09-05 04:45:23Z` from worker promotion commit `86f83f6`;
- no running Modal containers were present during diagnosis;
- recent bridge and worker app logs were empty;
- diagnosis itself invoked no audio/model/worker and changed no deployment.

### Exact L4 cold-start discriminator — GREEN

A single no-audio dependency call was made to the already-deployed worker function `rhythm_dependency_smoke` specifically to distinguish a general L4 startup failure from the async spawn/orchestration issue:

- workflow `.github/workflows/v143-live-worker-startup-smoke.yml`;
- commit `bf6ef7009085d52e5dc7a1c20927c99de48670a2`;
- run `33980499498`, job `101344748201`: **SUCCESS**;
- artifact `9973612728`, digest `sha256:cd94f62f54c0321fe57ee34f7b8547f445c529bf640ccc7c50efc0f0308b7a32`;
- cold-start + import wall `43.032s`;
- `cudaAvailable=true`, `deviceName=NVIDIA L4`;
- Basic Pitch and deterministic provider imports GREEN;
- deterministic separator seed `143`; `referenceFree=true`;
- `audioRead=false`, `separatorModelExecuted=false`, `referenceFacingInputs=0`, `referenceScoreCalls=0`, `qualityVerdictMade=false`.

**Conclusion:** the deployed L4 image/container can cold-start successfully. The reported Modal `oneshot` loop is **not a general worker/GPU startup failure**. Together with the already-GREEN bridge `async_protocol_smoke`, this narrows the defect to the additional async spawned-orchestrator execution path (or another ephemeral oneshot invocation), not the base bridge image and not the base L4 worker image.

Current async start path of interest:

`HTTP start -> run_rhythm_async_job.spawn(job_id, payload) -> orchestrator container -> _worker_handle().remote(payload) -> Queue result`

The next discriminator must exercise the **spawned orchestrator container + Queue write** with a synthetic result while never calling the L4 worker. That will distinguish `spawn`/oneshot startup from the nested worker call.

## NEXT STEP

1. Reuse the existing isolated bridge deployment mechanism with isolated app/Queue names.
2. Add a diagnostic-only synthetic spawned function using the same `http_image`; it writes a tiny structured completion envelope to the isolated Queue and invokes no worker/audio/model.
3. Spawn it exactly once, poll the isolated Queue, verify completion/clear, and capture startup logs.
4. If synthetic spawn fails/loops, fix the orchestrator/spawn layer only. If synthetic spawn is GREEN, inspect the nested cross-app worker-call handoff without audio/model before resuming E2E.
5. Checkpoint the exact cause before any production bridge redeploy.

### Hard stops

- No model-bearing async E2E while oneshot startup failure is unresolved.
- No duplicate model/audio request.
- No Production Vercel environment change or promotion yet.
- No Deployment Protection weakening/disablement.
- No model/scheduler change.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async result storage.
- No TTL above 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.
