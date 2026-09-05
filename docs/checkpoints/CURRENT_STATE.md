# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 08:51 America/Toronto  
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

Vercel/web remains unchanged by async work:

- `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`;
- production deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM` unchanged;
- production route blob still `06234db3e1cc1680b18fd62a765862b213ede3db`, synchronous `maxDuration=150`;
- no `main` merge and no production Vercel promotion yet.

Promoted L4 worker remains unchanged:

- app/function `dadrock-v143-ai-tab-live/rhythm_v143_request`;
- live endpoint blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`;
- seeded scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`;
- no worker/model/scheduler modification in async work.

**Production HTTP bridge has now been deliberately promoted to the backward-compatible async candidate:**

- current bridge blob `e0cecefacead73d69a905fd6bfb2049b21c87bc3`;
- protocol blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`;
- prior/rollback bridge blob `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`;
- existing synchronous `analyze` path and Lead/Bass fallback remain present;
- added Rhythm-only `start/status/ack` and transient result Queue `dadrock-v143-async-results`.

## Breakthrough diagnosis — CLOSED

- synchronous production request run `33965269193` / job `101304165477` / artifact `9969253856`: HTTP `504` at `150.66095s`;
- prior equivalent ~`150.931s`;
- log-only run `33965453476` / job `101304658150` proved scheduler concurrency live: direct Demucs `0.306s`, RoFormer `0.319s`, RoFormer done/cascade start `84.079s`;
- **scheduler breakthrough YES; synchronous product breakthrough NO** — async handoff is the current breakthrough path.

## Async architecture

Plan: `docs/checkpoints/V143_ASYNC_JOB_ARCHITECTURE_PLAN.md`, commit `e0aef99dcdf931b66c0e1a081160e3cc5c6cb3c2`.

Rhythm start -> immediate HMAC-signed opaque token -> browser polls Vercel -> Vercel polls bridge -> transient structured-result Modal Queue -> existing Vercel V143 anti-leakage/product pipeline -> browser receives tab -> ACK clears partition. TTL `900s` fallback. Lead/Bass remain synchronous.

Branch candidates:

- bridge commit `24bc086848b3903cb26c7032349fd5f3f289bae0`, blob `e0cecefa...`;
- Vercel route commit `4c94ae0e8bf88f8c0f7f0053c0dec5ad32522b79`, blob `742954146a86aa36485d0bbdb3fbd6691a64a712`;
- `/ai-tab` polling page commit `d07b08545296c579dbdb0faf2efc0843cc45d24e`, blob `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.

## Async evidence — GREEN

### Current protocol source gate

- run `33966778940`: **SUCCESS**;
- artifact `9969677990`, digest `sha256:b239317ee7ec9c4c6146567658140d4f0459c14ef77218ad4b61585673d666ef`.

### Current Vercel wiring/composition gate

- repin commit `16f50a4c8908f975006d58070990f5bab1f296e3`;
- run `33966794524`: **SUCCESS**;
- artifact `9969683328`, digest `sha256:9b22f8cdce8816814dfd6f414cb9fe72b27e727e342f06061c18a9a984225bf3`.

### Vercel preview build

- run `33966323815`, job `101306988163`: **SUCCESS**;
- artifact `9969549184`, digest `sha256:810c8c3c3012cb43a37d3b463735b9fc4dcbd2a06a4d2c7fd2407c03e2402a5f`;
- build only; no deployment/model/audio.

### Isolated Modal bridge smoke

- run `33966816672`, job `101308290865`: **SUCCESS**;
- artifact `9969693296`, digest `sha256:5a00636970d7426f5c83c4f498e84a4bc6b200700836e94184fd7f272b0d0b53`;
- isolated app `dadrock-v143-http-bridge-async-gate`, isolated Queue `dadrock-v143-async-results-gate`;
- token/HMAC true; Queue roundtrip true; Queue cleared true; TTL 900;
- raw audio/stems queued false; model/audio executed false; production bridge/worker targeted false;
- isolated app stopped after smoke.

Prior isolated failures `33966600313` and `33966716295` were fail-closed diagnostics only and invoked no model/audio.

### Production async bridge deploy + synthetic smoke — GREEN/CLOSED

Workflow `.github/workflows/v143-deploy-async-http-bridge.yml`, trigger commit `f0f1ef1b16b6cf954e663416a8cd0f474d920770`.

- Actions run `33967130980`, job `101309120073`: **SUCCESS**;
- exact source boundary passed before deployment;
- `modal deploy --env main analyzer/v143_modal_http_endpoint.py` completed against `dadrock-v143-http-bridge` only;
- production worker and Vercel were not deployment targets;
- production bridge `async_protocol_smoke` then passed against Queue `dadrock-v143-async-results`;
- token verified, Queue write/read/decode/clear passed, TTL 900;
- no raw audio/stem Queue content, no audio read, no worker/model execution, no reference-facing input/scoring/quality verdict;
- artifact `9969786854`, digest `sha256:fb1d8267a3241fe4d09343b50a286ce0635f705374326b36ea8e9732c276fdf5`.

## Legacy closed scheduler gate note

Bridge commit `24bc086...` auto-triggered old seeded scheduler structure run `33966778906`, job `101308192747`, which failed solely because that closed gate intentionally pins the old HTTP bridge blob `9a550f0a...`. Logs show `e0cecefa... != 9a550f0a...`; scheduler/worker source was unchanged. This is expected stale-pin behavior after the authorized bridge architecture change, not a scheduler regression. Do not rerun/repin that closed gate merely to bless the bridge.

## ASYNC PROMOTION STATUS

- Protocol source/current pins: **GREEN/CLOSED**.
- Vercel route/UI composition/current pins: **GREEN/CLOSED**.
- Branch preview build: **GREEN**.
- Isolated bridge smoke: **GREEN/CLOSED**.
- Production bridge async protocol: **PROMOTED + SYNTHETIC SMOKE GREEN/CLOSED**.
- Production Vercel: **UNCHANGED**.
- Vercel async preview deployment/no-model protocol check: **NEXT**.
- Model-bearing async preview E2E: **NOT YET RUN**.

## NEXT STEP

1. Deploy the already-built async route/UI candidate to a **Vercel preview only**; do not promote production.
2. Run no-model preview protocol checks proving the preview route reaches the new production bridge and fails closed on an invalid signed job token without spawning a worker.
3. Verify `/ai-tab` preview loads and polling wiring is present.
4. If GREEN, checkpoint exact preview deployment/URL and authorize exactly one model-bearing async Rhythm preview E2E.
5. Breakthrough criterion: initial `start` returns well below 150s, polling survives beyond 150s, one real result returns through existing V143 safety/product pipeline, and ACK clears transient result.
6. Production Vercel promotion only after that preview E2E is GREEN.

### Hard stops

- No model-bearing test before preview async E2E.
- No model/scheduler changes as part of async wiring.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async result storage.
- No async result TTL above 15 minutes; no persistent result cache.
- No whole-branch merge to `main`.
- No production Vercel promotion before preview protocol/E2E proof.
- No weakening exact parity/fail-closed criteria or retention boundaries.
