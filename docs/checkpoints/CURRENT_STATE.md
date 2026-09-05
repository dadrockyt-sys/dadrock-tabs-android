# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — single guarded start returned HTTP 401; NO RETRY; auth-boundary diagnosis in progress  
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

## SINGLE ARMED RUN — EXACT CLIENT EVIDENCE

- Exactly one breakthrough run was created from the arming commit: run `33998283085`, job `101392517265`, conclusion **FAILURE**.
- Fresh Preview deployment: `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`, URL `https://dadrock-tabs-android-bx51iz9tr-stephen-mcnally-s-projects.vercel.app`, target **preview**, status **Ready**.
- Production promotion remained false; no `--prod` or promotion command executed.
- Protected Preview `/ai-tab` preflight succeeded: **HTTP 200**. The prior 403 blocker is resolved.
- The helper then sent **exactly one** Rhythm `operation=start` POST using the approved audio and a freshly minted trusted OIDC token.
- Aggregate artifact `9978732479` was downloaded and inspected. Exact retained values:
  - `modelBearingStartRequestCount = 1`
  - `startStatus = 401`
  - `startCurlExitCode = 0`
  - `startAccepted = false`
  - `terminalState = start-response-unusable`
  - `completed = false`
  - `acknowledged = false`
  - `transientResultCleared = false`
  - `productionEnvironmentChanged = false`
  - `productionPromotionPerformed = false`
  - `deploymentProtectionDisabled = false`
  - `referenceFacingInputs = 0`
  - `referenceScoreCalls = 0`
  - `qualityVerdictMade = false`.
- Artifact zip digest: `sha256:e245ae0a89d9c174ce1da14e47c31b252ad516b601d7793b2d982489efc16aa6`.
- Because no usable signed `v143a1.*` token returned, **no status poll and no ACK were attempted**. Runner cleanup deleted raw request/response/token/status/ACK files.

## AUTH-BOUNDARY DIAGNOSIS — CURRENT EVIDENCE

- Client transport itself succeeded (`curl exit 0`), so this was a real HTTP **401**, not a timeout/lost response.
- `app/api/analyze-audio-tab/route.js` validates required config first; missing analyzer URL/token/blob token would return **503**, not 401. Its downstream analyzer call propagates the Modal bridge's non-OK HTTP status.
- Hardened bridge `v143_modal_http_endpoint.py` maps `PermissionError("Unauthorized analyzer request.")` to HTTP **401**. `_start_rhythm_job()` performs `_authorize(payload, expected_token)` **before** creating a job ID, spawning `run_rhythm_async_job`, or writing orchestrator control.
- Therefore **if the 401 is confirmed to originate from the application/bridge path**, no Modal orchestrator/worker/model could have been spawned by this call.
- One ambiguity remains before declaring that proof final: Vercel Deployment Protection itself could theoretically return the 401 before the Next.js function. Runtime-log queries for this deployment/window returned no entries, so do not use absence of logs as proof either way.
- The fresh Preview build log also reported: `1 Secret value cannot be pulled from the preview Environment. Wrote "[SENSITIVE]" as a placeholder`. This is a strong lead for a locally prebuilt secret mismatch, but the exact variable has **not** yet been proven and no secret value has been inspected.

### MODEL-FREE DISAMBIGUATION ALLOWED

A safe next diagnostic may POST an intentionally invalid request to the **same protected Preview endpoint** using trusted GitHub OIDC, chosen so the Next.js route must return HTTP 400 **before any analyzer/bridge call** (for example an invalid `transcriptionType`). This tests whether protected Preview POST requests reach application code. It must contain no usable audio/model request and must preserve `modelBearingStartRequestCount=0` for the diagnostic itself.

If that malformed POST returns the route's expected 400, then Deployment Protection POST access is proven and the prior 401 is attributable to downstream bridge authorization. Because bridge `_authorize` precedes spawn, that would prove the single start call executed **zero Modal worker/model starts** despite consuming the client start-request budget.

## HARD STOP AFTER THE SINGLE START

- **Exactly one start POST has been sent. No second start is authorized.**
- **DO NOT RERUN `33998283085`. DO NOT EDIT THE breakthrough trigger workflow to arm again.**
- The terminal-failure ACK repair was not exercised because no signed job token was obtained.
- Even if diagnosis proves zero worker/model execution, do not issue another start until root cause + repair are checkpointed and the one-start authorization boundary is explicitly reconsidered.

## NEXT

1. Run only a model-free malformed-POST protected-Preview diagnostic to distinguish Deployment Protection 401 from application/bridge 401.
2. If application POST access is proven, record that the prior 401 came from Modal bridge authorization and therefore occurred before spawn.
3. Diagnose the likely locally-prebuilt sensitive environment mismatch without exposing secret values. Prefer metadata/presence/equality-proof mechanisms; never print tokens.
4. Propose/verify a repair without another model-bearing start. Do not modify scheduler/model/runtime behavior.
5. Save each meaningful diagnosis milestone back here.

## HARD STOPS

- No duplicate/second model-bearing start request.
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement.
- No scheduler/model change for async lifecycle symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **protected Preview GET access GREEN; single guarded start returned exact HTTP 401 with curl transport success; one client start request consumed; no signed token/poll/ACK; model execution remains unproven pending model-free POST disambiguation; NO RETRY.**
