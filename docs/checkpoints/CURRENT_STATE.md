# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 12:26 America/Toronto  
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

- replacement-routing commit `0c023bdf0e395ddf98501317472ea59e99a00eeb`;
- run `33968019067`, job `101311460970`: **SUCCESS**;
- Preview-only env add, build/deploy, and bad-HMAC bridge-path proof all GREEN;
- no production Vercel promotion and no model/audio request.

## Modal “oneshot” start-loop diagnosis — STRONGLY NARROWED

User reported Modal showing a `oneshot` repeatedly looping/failing to start. Model-bearing E2E remains paused.

### Base app/image diagnostics — GREEN

- read-only bridge+worker diagnosis runs `33980341926` / `101344336671` and `33980388754` / `101344455300`: GREEN / diagnostic only;
- no running production bridge/worker containers were present at read time and recent app logs were empty;
- deployed L4 no-audio cold-start smoke run `33980499498`, job `101344748201`, artifact `9973612728`, digest `sha256:cd94f62f54c0321fe57ee34f7b8547f445c529bf640ccc7c50efc0f0308b7a32`: **GREEN**;
- exact worker cold-start + imports `43.032s`, NVIDIA L4/CUDA GREEN, seed 143/reference-free GREEN; no audio or separator execution.

### Exact `.spawn()`/oneshot discriminator — GREEN

An isolated app now reproduces only the Modal primitive under suspicion:

- diagnostic source `analyzer/v143_async_spawn_smoke_modal.py`, initial commit `96ad6909cc1630fe1e2ecbd52ad0f7be022878f1`;
- workflow `.github/workflows/v143-async-spawn-smoke.yml`, initial trigger commit `bf3bacb5e9adf26ec1e34bc4893710ef3ae40718`;
- run `33980754694`, job `101345414660`: **SUCCESS**;
- artifact `9973684032`, digest `sha256:f26d418d084fea8b6719dd28f1efe7399307bdbbf0744a9881ee2c389f977164`;
- parent called `.spawn()` exactly once; spawned oneshot child published a synthetic structured result to an isolated Queue; parent decoded it; Queue cleared;
- complete spawned handoff `5.123s`;
- `spawnCallIdPresent=true`, `spawnedResultCompleted=true`, `queueCleared=true`, TTL `900s`;
- `workerInvoked=false`, `audioRead=false`, `modelExecuted=false`, reference inputs/scores `0`.

**Conclusion:** Modal `.spawn()` and the lightweight oneshot container itself are healthy. The production issue is not a generic spawn failure.

### Diagnostic cleanup defect found and corrected

The first isolated spawn workflow's cleanup command used `modal app stop ...` without confirmation bypass. Modal 1.5.5 aborted in non-interactive CI with: `Rerun with --yes (-y) to skip confirmation`, temporarily leaving two diagnostic containers running.

- cleanup correction commit `e5c8b0b0d61635f82971a53521d07082821c5d52`;
- rerun `33980862345`: **SUCCESS** with noninteractive `--yes` cleanup;
- this defect applies to diagnostic cleanup only, not the production async request path, but it can create misleading lingering oneshot/container activity in the Modal dashboard.

### Remaining seam under test

Current production start path:

`HTTP start -> run_rhythm_async_job.spawn(job_id, payload) -> orchestrator oneshot -> modal.Function.from_name(dadrock-v143-ai-tab-live/rhythm_v143_request).remote(payload) -> Queue result`

Base bridge image GREEN + `.spawn()` GREEN + L4 worker cold-start GREEN. The only unproven startup/wiring seam is now **spawned orchestrator -> nested cross-app worker call**.

A no-audio nested test has been created:

- `analyzer/v143_async_nested_worker_smoke_modal.py` commit `35c06ec544998838b3187a792d2a084b408c432a`;
- workflow `.github/workflows/v143-async-nested-worker-smoke.yml` trigger commit `62859bd65ad83f361240c278101fd6734e9f26ec`;
- run `33980891422`, job `101345785629` currently in progress;
- it spawns an orchestrator with production-like `memory=4096`, then calls only deployed `rhythm_dependency_smoke` across the app boundary and publishes a synthetic Queue result;
- it reads no audio and executes no separator/model.

## NEXT STEP

1. Observe nested-worker smoke run `33980891422` to terminal state; do not duplicate it.
2. If GREEN, the async orchestration/start topology is healthy end-to-end without audio; the reported dashboard loop must then be tied to the real `rhythm_v143_request` execution/payload path or stale diagnostic activity, not startup wiring.
3. If FAILED, use its isolated logs to fix only the nested cross-app handoff/resource seam.
4. Keep model-bearing Preview E2E paused until this discriminator is closed.

### Hard stops

- No model-bearing async E2E while nested-worker discriminator is unresolved.
- No duplicate model/audio request.
- No Production Vercel environment change or promotion yet.
- No Deployment Protection weakening/disablement.
- No model/scheduler change.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async result storage.
- No TTL above 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.
