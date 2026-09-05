# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 12:36 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO REFERENCE-FACING QUALITY VERDICT** — performance/identity/routing/product-health diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`.
- Async storage authorization: transient structured result + non-sensitive control metadata only; no raw audio/stems/model bytes; TTL <= 900 seconds; no persistent result cache.

## Production — unchanged while hardening is proven

Vercel production remains:

- `main` `bb992d901e78ab19645f8edc8e330d5a142ebd8e`;
- deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`;
- production route blob `06234db3e1cc1680b18fd62a765862b213ede3db`, synchronous `maxDuration=150`;
- no production Vercel promotion / no whole-branch merge.

Promoted L4 worker remains unchanged:

- `dadrock-v143-ai-tab-live/rhythm_v143_request`;
- live endpoint blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`;
- scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.

Currently deployed production HTTP bridge remains pre-hardening async candidate:

- deployed bridge blob `e0cecefacead73d69a905fd6bfb2049b21c87bc3`;
- protocol blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`;
- rollback sync bridge blob `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`.

Branch-only hardened bridge candidate:

- hardening commit `e682e6faf0aa5fe9175684561ea584e9fad8bf9e`;
- hardened bridge blob `365843550fa6ee67f3d22a6b4536261f9dc46dba`;
- **not deployed yet**.

## Breakthrough diagnosis — CLOSED

- production synchronous request run `33965269193` / job `101304165477`: HTTP 504 at `150.66095s`;
- previous equivalent ~`150.931s`;
- log-only run `33965453476` proved direct Demucs and RoFormer overlap (`0.306s` / `0.319s`), RoFormer done/cascade start `84.079s`;
- scheduler breakthrough YES; synchronous product breakthrough NO.

## Async architecture

Plan `docs/checkpoints/V143_ASYNC_JOB_ARCHITECTURE_PLAN.md`, commit `e0aef99dcdf931b66c0e1a081160e3cc5c6cb3c2`.

Rhythm: start -> signed opaque token -> browser polls Vercel -> Vercel polls bridge -> transient Modal Queue -> existing V143 safety/product pipeline -> result -> ACK clear. Lead/Bass stay synchronous.

Current branch Vercel/UI pins:

- route blob `742954146a86aa36485d0bbdb3fbd6691a64a712`;
- `/ai-tab` page blob `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.

## Previously closed async evidence — GREEN

- Protocol run `33966778940`, artifact `9969677990`.
- Vercel composition run `33966794524`, artifact `9969683328`.
- Preview build `33966323815` / job `101306988163`, artifact `9969549184`.
- Isolated bridge smoke `33966816672` / job `101308290865`, artifact `9969693296`.
- Production bridge synthetic smoke `33967130980` / job `101309120073`, artifact `9969786854`.
- Preview routing correction `33968019067` / job `101311460970`: GREEN / no model/audio.

## Modal `oneshot` report — STARTUP ROOT CAUSE RULED OUT

User reported Modal showing an apparent looping/failing `oneshot`. Model-bearing E2E was paused.

No-audio discriminators all GREEN:

- deployed L4 cold-start `33980499498` / `101344748201` / artifact `9973612728`: 43.032s, NVIDIA L4/CUDA, no model/audio;
- isolated `.spawn()` primitive `33980754694` / `101345414660` / artifact `9973684032`: spawned handoff 5.123s;
- spawned orchestrator -> deployed L4 dependency smoke `33980891422` / `101345785629` / artifact `9973722881`: 17.639s;
- exact deployed production orchestrator + exact deployed `rhythm_v143_request` fail-before-download `33981009987` / `101346107709` / artifact `9973751225`: FunctionCall `fc-01M1S9SEY1YY29VYHVWWSSSMX6`, lifecycle 9.061s, bounded failure queued, no audio/model.

Therefore the exact production oneshot **does start**. The dashboard symptom is not a generic bridge startup, `.spawn()`, cross-app lookup, or L4 startup failure.

A separate diagnostic cleanup defect was found: `modal app stop` without `--yes` left isolated diagnostic containers alive. Commit `e5c8b0b0d61635f82971a53521d07082821c5d52` corrected noninteractive cleanup. This could create misleading lingering oneshot activity but does not explain product request state by itself.

## Actual robustness gap — BRANCH FIX IMPLEMENTED

Pre-hardening bridge discarded the `FunctionCall` returned by `.spawn()`. Empty Queue therefore meant `processing` even if the orchestrator had already crashed before publishing a result.

Hardened branch candidate now:

- stores only opaque orchestrator FunctionCall ID in `control-{job_id}` partition, TTL `900s`;
- returns no job token unless control tracking was written; best-effort cancels an untrackable spawn;
- status reads result first, then `modal.FunctionCall.from_id(...).get(timeout=0)`;
- `modal.exception.TimeoutError` = genuinely processing;
- remote/completed failure = immediate bounded failed state, never infinite polling;
- completed-call/result race is closed by re-reading Queue;
- ACK clears result + control partitions;
- safe aggregate-only logs: `orchestrator.start`, `worker_call.start/done`, `result_queue.done`;
- no URL/token/job-id/audio/tab/reference data logged;
- worker/scheduler/model unchanged.

### Fail-closed source/protocol gate — GREEN

First hardening gate run `33981289216` failed only because the test incorrectly forbade the generic substring `result`, matching harmless `async_result_queue`; bridge source parsed successfully. Gate assertion was narrowed in commit `cc8c9fd82611445a29e8f087bb27645e7eb8e52f`.

Corrected authoritative gate:

- run `33981347482`;
- job `101347008342`: **SUCCESS**;
- artifact `9973838904`;
- digest `sha256:a74c088f9a6e412deba9b47f400dc221bf2c992021ca48d2185ec2f7addab9d5`;
- proves result/control TTL 900, metadata-only control record, FunctionCall tracking/nonblocking poll/fail-closed failure, ACK clears control, aggregate-only logging, multi-chunk result transport, signed-token tamper rejection, Lead/Bass/synchronous fallback preservation;
- `audioRead=false`, `modelExecuted=false`, reference inputs/scores `0`, quality verdict false.

Older source-pin gates that still expect the pre-hardening bridge blob may fail on this intentional bridge change. Those failures are source-pin mismatches, not scheduler/model regressions; do not weaken or rerun closed model gates. Update only legitimate composition pins after the hardened bridge is dynamically proven.

## NEXT STEP

1. Deploy hardened bridge blob `36584355...` to the existing isolated bridge app/Queue only.
2. Dynamically prove control tracking: immediate status while a spawned fail-before-download worker call is running must report true processing via FunctionCall; terminal state must become bounded failed; ACK must clear both partitions.
3. Capture isolated logs/evidence and stop isolated app with `--yes`.
4. If GREEN, checkpoint then consider bridge-only production redeploy; Vercel production remains untouched.
5. Model-bearing Preview E2E remains paused until hardened production bridge is deployed and fail-fast status behavior is GREEN.

### Hard stops

- No model-bearing async E2E until dynamic control-tracking proof is GREEN.
- No duplicate model/audio request.
- No Production Vercel environment change/promotion yet.
- No Deployment Protection weakening.
- No model/scheduler change.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL above 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.
