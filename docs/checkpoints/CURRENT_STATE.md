# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — single guarded start sent; unusable start response; NO RETRY; exact server diagnosis next  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## FROZEN BOUNDARIES

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO REFERENCE-FACING QUALITY VERDICT** — performance/identity/routing/product-health diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`.
- Async storage: transient structured result + non-sensitive FunctionCall control metadata only; no raw audio/stems/model bytes; TTL <= 900s; no persistent result cache.
- No production Vercel promotion/change; no whole-branch merge while proving first E2E.
- Do not touch unrelated musical/reference issues or `core/engine/chord_mapping.py` octave folding.

## AUTHORITATIVE SOURCE PINS

- Production `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`; production deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`; synchronous route blob `06234db3e1cc1680b18fd62a765862b213ede3db`.
- V143 worker blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`; scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Hardened bridge `36584355d9b060fc7b7e20acc62524fbc7bf9005`; protocol `1bd55017e16a4e1d8b14c7429492f811a43a28d8`.
- Branch async route `742954146a86aa36485d0bbdb3fbd6691a64a712`; `/ai-tab` page `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.
- Approved audio `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`, blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`.

## LIFECYCLE GATE — GREEN / DO NOT REOPEN WITHOUT NEW EVIDENCE

- Startup diagnosis `33985149949` / job `101357179709` SUCCESS with no model/audio/reference-facing invocation.
- Isolated async control proof `33985474511` / job `101358067142` SUCCESS; artifact `9975020241`, digest `sha256:b701ad58e32d538336f21279289bb189aca4324ec5029242d1f08246d4e1a493`.
- Proven: one tracked start, deterministic terminal state, ACK clears result/control, TTL 900, no audio/model bytes in transient transport, reference-facing calls 0.

## HISTORICAL BREAKTHROUGH RUN — PRE-MODEL ONLY

- Historical trigger commit `58be9aa7b5606783a508917ce4531cfd512d66da` produced run `33982235357`, job `101349393362`.
- Source gate and fresh Preview deploy were GREEN; protected `/ai-tab` preflight returned **403**; model-bearing step was **SKIPPED**.
- Historical Preview deployment: `dpl_F6ksguDvc1nVAt33jNxxoVTmyyJA`; no production promotion. Do not rerun it.

## PROTECTED PREVIEW ACCESS — REPAIRED / GREEN

- Trusted GitHub OIDC proof `33982502347` returned protected Preview HTTP 200 using `x-vercel-trusted-oidc-idp-token` without weakening Deployment Protection.
- Refreshability proof `33982582372` GREEN; on-demand JWT TTL = **300s**.
- Armed workflow grants `id-token: write`, mints/masks fresh JWTs, and uses direct `curl` against the exact protected Preview. Vercel CLI is build/deploy/inspect only. No production target/promotion command was added.

## GUARDED HELPER / ARMED WORKFLOW

- Helper `.github/scripts/v143-fresh-preview-async-breakthrough-e2e.sh` commit `8d536121bb9a38f4a69add31cbf7515400441c5b`, blob `92d17ee0b01ff72f71abfac1a7a4b36ff7e02792`; exact bytes passed `bash -n` before staging.
- Single arming workflow commit: `0a07b393bb47123a1142fd46ea6d9a55b04f0486`, message `test: arm guarded OIDC async breakthrough E2E`.
- Armed workflow blob: `2a48af6aadda3b90a9c9ea24220ac524dbcb5b41`.
- Trigger remains workflow-path-only push on `v143-contextual-prune-lobo`; concurrency remains `v143-fresh-preview-async-breakthrough-e2e-single`, `cancel-in-progress: false`.
- Final pre-arm active-state check was clean: `in_progress=0`, `queued=0`, `waiting=0`, `requested=0`, `pending=0`.
- All authoritative route/page/bridge/protocol/worker/scheduler/audio/helper pins passed in the run before any Preview or start work.

## SINGLE ARMED RUN — STOPPED AFTER UNUSABLE START RESPONSE

- Exactly one breakthrough run was created from the arming commit: run `33998283085`, job `101392517265`, conclusion **FAILURE**.
- Fresh Preview deployment: `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`, URL `https://dadrock-tabs-android-bx51iz9tr-stephen-mcnally-s-projects.vercel.app`, target **preview**, status **Ready**.
- Production promotion remained false; no `--prod` or promotion command executed.
- Protected Preview `/ai-tab` preflight succeeded: **HTTP 200**. The prior 403 blocker is resolved.
- Immediately after that preflight, the helper sent **exactly one** Rhythm `operation=start` POST to the protected Preview `/api/analyze-audio-tab` endpoint using the approved audio and a freshly minted trusted OIDC token.
- That single start request **did not return a usable accepted async response** (`HTTP 202` + `analysisJob.status=processing` + signed `v143a1.*` token were not jointly satisfied).
- The helper fail-closed message was: `The one start request was sent but did not yield a usable accepted token. Do not send a second start; diagnose this request.`
- Because no usable signed job token was available, **no status poll and no ACK were attempted**. The helper intentionally exited with code 4 rather than issuing another start.
- Runner cleanup succeeded and removed start/status/ACK request/response/token material.
- Aggregate-only artifact upload succeeded: artifact `9978732479`, zip digest `sha256:e245ae0a89d9c174ce1da14e47c31b252ad516b601d7793b2d982489efc16aa6`, 937 bytes.
- The artifact summary is expected to retain only aggregate fields including `modelBearingStartRequestCount=1`, `startStatus`, `startCurlExitCode`, `startAccepted=false`, and `terminalState=start-response-unusable`; exact start status still requires artifact/server-log inspection.

### HARD STOP AFTER THIS RUN

- **Model-bearing start-request budget is now consumed/ambiguous: exactly one start POST was sent.**
- Whether the Modal orchestrator/worker/model actually began is **not yet proven**. Do not infer from the fast client failure.
- **DO NOT RERUN `33998283085`. DO NOT EDIT THE TRIGGER WORKFLOW TO ARM AGAIN. DO NOT SEND A SECOND START.**
- Since no token returned, cleanup of any possibly-created transient backend job cannot be driven from the runner; determine from exact server/bridge evidence whether a job was created. Any transient async state remains bounded by the existing <=900s TTL if it exists.
- The terminal-failure ACK repair was not exercised because the failure occurred before a usable signed job token was obtained.

## NEXT — DIAGNOSE THIS EXACT START ONLY

1. Read artifact `9978732479` if possible to recover aggregate `startStatus` / `startCurlExitCode`; do not recover or retain raw start response/token material.
2. Inspect Vercel logs for deployment `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD` around `2026-09-05T23:19:48Z`, endpoint `/api/analyze-audio-tab`, and determine the exact response status/error category without exposing secrets.
3. Determine whether the request reached the Modal bridge and whether `_start_rhythm_job` spawned/tracked an orchestrator/worker. Distinguish **pre-bridge configuration/request failure** from **bridge start failure** from **accepted job whose response was lost/malformed**.
4. If backend execution actually began, diagnose that exact call only. No retry.
5. If backend execution provably never began, still do not issue another start until the root cause and any proposed repair are checkpointed and the one-start authorization boundary is explicitly reconsidered.
6. Preserve production/no-reference/no-retention frozen boundaries and save each meaningful diagnosis milestone back here.

## HARD STOPS

- No duplicate/second model-bearing start request.
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement.
- No scheduler/model change for async lifecycle symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **OIDC protected access GREEN; exactly one guarded start request has been sent and is now the sole subject of diagnosis; start response was unusable and yielded no signed token; no poll/ACK/second start occurred; NO RETRY is authorized.**
