# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 12:30 America/Toronto  
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

Production HTTP bridge currently deployed:

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

Current branch pins:

- route blob `742954146a86aa36485d0bbdb3fbd6691a64a712`;
- `/ai-tab` page blob `de39f2715c6875d757ef730c9e3182ccd4aa00a4`;
- bridge blob before hardening `e0cecefacead73d69a905fd6bfb2049b21c87bc3`;
- worker/scheduler unchanged as above.

## Closed async evidence — GREEN

- Protocol current-pin run `33966778940`, artifact `9969677990`, digest `sha256:b239317ee7ec9c4c6146567658140d4f0459c14ef77218ad4b61585673d666ef`.
- Vercel wiring/composition run `33966794524`, artifact `9969683328`, digest `sha256:9b22f8cdce8816814dfd6f414cb9fe72b27e727e342f06061c18a9a984225bf3`.
- Preview build run `33966323815` / job `101306988163`, artifact `9969549184`, digest `sha256:810c8c3c3012cb43a37d3b463735b9fc4dcbd2a06a4d2c7fd2407c03e2402a5f`.
- Isolated Modal bridge smoke run `33966816672` / job `101308290865`, artifact `9969693296`, digest `sha256:5a00636970d7426f5c83c4f498e84a4bc6b200700836e94184fd7f272b0d0b53`.
- Production bridge deploy + synthetic smoke run `33967130980` / job `101309120073`, artifact `9969786854`, digest `sha256:fb1d8267a3241fe4d09343b50a286ce0635f705374326b36ea8e9732c276fdf5`.
- Preview routing correction run `33968019067`, job `101311460970`: GREEN / Preview-only env add/build/deploy/bad-HMAC proof; no model/audio.

## Modal `oneshot` startup report — STARTUP TOPOLOGY GREEN / ROOT ROBUSTNESS GAP IDENTIFIED

User reported Modal showing a `oneshot` repeatedly looping/failing to start. Model-bearing E2E was paused and a sequence of no-audio discriminators was run.

### Base L4 startup — GREEN

- deployed worker no-audio cold-start run `33980499498`, job `101344748201`, artifact `9973612728`, digest `sha256:cd94f62f54c0321fe57ee34f7b8547f445c529bf640ccc7c50efc0f0308b7a32`;
- exact cold-start/import wall `43.032s`, NVIDIA L4/CUDA GREEN, seed 143/reference-free GREEN;
- no audio and no separator/model execution.

### Modal `.spawn()` oneshot primitive — GREEN

- isolated run `33980754694`, job `101345414660`, artifact `9973684032`, digest `sha256:f26d418d084fea8b6719dd28f1efe7399307bdbbf0744a9881ee2c389f977164`;
- one parent `.spawn()` -> one spawned child -> isolated Queue result -> decode -> clear;
- complete handoff `5.123s`, `spawnCallIdPresent=true`, `spawnedResultCompleted=true`;
- no worker/audio/model.

### Diagnostic cleanup bug — FOUND / FIXED

The first isolated smoke used `modal app stop` without `--yes`; Modal 1.5.5 aborted non-interactive cleanup and temporarily left two diagnostic containers running, which can create misleading lingering `oneshot` activity in the Modal dashboard.

- cleanup fix commit `e5c8b0b0d61635f82971a53521d07082821c5d52`;
- rerun `33980862345`: GREEN with `modal app stop ... --yes`.

### Spawned orchestrator -> cross-app L4 call — GREEN

- isolated nested source commit `35c06ec544998838b3187a792d2a084b408c432a`;
- workflow trigger `62859bd65ad83f361240c278101fd6734e9f26ec`;
- run `33980891422`, job `101345785629`: **SUCCESS**;
- artifact `9973722881`, digest `sha256:f205cc3c66a333018eb7e68153389ef72410566f001c4c03576b1f00469bcd1d`;
- production-shaped spawned orchestrator called deployed `dadrock-v143-ai-tab-live/rhythm_dependency_smoke`, received NVIDIA L4, queued synthetic result, and cleared Queue;
- elapsed `17.639s`; no audio/model.

### Exact deployed production oneshot + exact real worker function — GREEN

Strongest discriminator:

- workflow `.github/workflows/v143-production-oneshot-failfast-smoke.yml`;
- commit `65bf4355237ee95b43ab8fa382b0de157fec1093`;
- run `33981009987`, job `101346107709`: **SUCCESS**;
- artifact `9973751225`, digest `sha256:cc5b3cf3833ca17936c92818548e2cbfb5fbb706348f2a8875548f83edc7b3bf`;
- spawned the actual deployed `dadrock-v143-http-bridge/run_rhythm_async_job`;
- that actual oneshot called the actual deployed `dadrock-v143-ai-tab-live/rhythm_v143_request`;
- deliberately invalid non-URL caused the worker to reject before any download/audio/model work;
- FunctionCall ID `fc-01M1S9SEY1YY29VYHVWWSSSMX6`;
- exact lifecycle `9.061s`;
- bounded failure envelope queued; orchestrator returned `status=failed`, `resultQueued=true`; Queue cleared;
- `audioRead=false`, `separatorModelExecuted=false`, reference inputs/scores `0`.

**Conclusion:** the production oneshot is demonstrably able to start. The user-observed dashboard symptom is not caused by a generic bridge startup failure, `.spawn()` failure, cross-app lookup failure, L4 cold-start failure, or inability of the exact production orchestrator to call the exact worker function.

## Actual async robustness gap — FIX AUTHORIZED

Current `_start_rhythm_job()` discards the `modal.FunctionCall` returned by `run_rhythm_async_job.spawn(...)`. Current `_status_rhythm_job()` interprets an empty result Queue as `processing` without checking whether that orchestrator FunctionCall is still alive, finished, or crashed.

Therefore a real long-running orchestrator that terminates before publishing its result can look like an endless `processing`/oneshot loop to the browser/dashboard even though the underlying call has failed.

Authorized narrow hardening:

1. Persist only the non-sensitive orchestrator FunctionCall ID in a separate control partition of the same Modal Queue, TTL `900s`.
2. Start must write that control record before returning the signed job token; if control tracking cannot be written, start fails closed.
3. Status checks the result partition first; if empty, reconstructs `modal.FunctionCall.from_id(call_id)` and calls `.get(timeout=0)`.
4. `modal.exception.TimeoutError` means genuinely still processing; any completed failure/remote exception becomes an immediate bounded generic failure instead of polling forever.
5. ACK clears both result and control partitions.
6. Add safe aggregate stage markers only (`orchestrator.start`, `worker_call.start/done`, `result_queue.done`); never log URL, blob token, audio/tab content, labels, or reference-facing data.
7. Do not change worker/scheduler/model code.

Modal's current SDK documents `FunctionCall.from_id()` and `get(timeout=0)` specifically for re-instantiating and non-blockingly polling a spawned call.

## NEXT STEP

1. Implement branch-only control tracking + safe orchestrator stage markers in `v143_modal_http_endpoint.py`.
2. Strengthen source/no-model gates for control TTL, FunctionCall polling, ACK cleanup, and no-sensitive logging.
3. Prove in an isolated bridge deployment that a synthetic spawned success and a fail-fast real-worker call both transition status without indefinite polling.
4. Only after GREEN, checkpoint and consider a bridge-only production redeploy.
5. Model-bearing Preview E2E remains paused until the hardened bridge is deployed/proven.

### Hard stops

- No model-bearing async E2E until control tracking hardening is GREEN.
- No duplicate model/audio request.
- No Production Vercel environment change or promotion yet.
- No Deployment Protection weakening/disablement.
- No model/scheduler change.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL above 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.
