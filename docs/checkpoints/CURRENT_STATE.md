# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — async lifecycle GREEN; prior breakthrough run confirmed pre-model; next arm blocked on protected-Preview 403 repair  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## FROZEN BOUNDARIES

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO REFERENCE-FACING QUALITY VERDICT** — performance/identity/routing/product-health diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`.
- Async storage authorization: transient structured result + non-sensitive FunctionCall control metadata only; no raw audio/stems/model bytes; TTL <= 900 seconds; no persistent result cache.
- No production Vercel promotion/change and no whole-branch merge while proving the first E2E.
- Do not modify unrelated musical/reference issues: Keep the Wolves Away G# vs A, Tennessee Whiskey C# fret / E4 capo2 D-shape, or `core/engine/chord_mapping.py` octave folding.

## PRODUCTION BASELINE / SOURCE PINS

- Vercel `main` remains `bb992d901e78ab19645f8edc8e330d5a142ebd8e`, production deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, synchronous route blob `06234db3e1cc1680b18fd62a765862b213ede3db`, `maxDuration=150`.
- L4 worker remains `dadrock-v143-ai-tab-live/rhythm_v143_request`, live blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`, seeded scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Hardened HTTP bridge source blob `36584355d9b060fc7b7e20acc62524fbc7bf9005`; protocol blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`.
- Branch async route blob `742954146a86aa36485d0bbdb3fbd6691a64a712`; `/ai-tab` page blob `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.
- Approved first-E2E audio: `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`, Git blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`.

## ASYNC ARCHITECTURE

Plan: `docs/checkpoints/V143_ASYNC_JOB_ARCHITECTURE_PLAN.md`, commit `e0aef99dcdf931b66c0e1a081160e3cc5c6cb3c2`.

Intended Rhythm path:

`start -> signed opaque token -> browser polls Vercel -> Vercel polls bridge -> transient Modal Queue/control -> existing V143 safety/product pipeline -> result -> ACK clears transient state`

Lead/Bass remain synchronous.

## MODAL `oneshot` REGRESSION — DIAGNOSED / LIFECYCLE GATE GREEN

The user-reported Modal `oneshot` looping/failing-to-start signal was investigated before any model-bearing E2E.

### Read-only Modal evidence

A diagnostic-only GitHub Action was enabled for repeatable/manual use:

- workflow: `V143 Async Bridge Startup Diagnosis`;
- run `33985149949`, job `101357179709` — **SUCCESS**;
- no audio/model invocation by the diagnostic, no worker spawn by the diagnostic, no production deployment change, no reference-facing work.

The captured worker failures in the diagnostic window were immediate `ValueError: A valid audioUrl is required` failures before download/model work. They are explained by the deliberate production one-shot fail-fast smoke, which sends `audioUrl: INVALID-NO-AUDIO`; therefore the earlier interim inference that those logs proved a bridge bypass is **withdrawn**.

### Isolated async lifecycle proof

`.github/workflows/v143-async-control-tracking-smoke.yml` was made manually runnable. Its first new run `33985412250` / job `101357894752` stopped safely at the exact-source boundary because its expected bridge blob was stale. No Modal deploy/model/audio work occurred in that failed run.

The stale gate pin was corrected from `365843550fa6ee67f3d22a6b4536261f9dc46dba` to the authoritative hardened bridge blob `36584355d9b060fc7b7e20acc62524fbc7bf9005`. Protocol, worker, and scheduler pins were already correct.

Rerun:

- workflow: `V143 Async Control Tracking Smoke`;
- run `33985474511`, job `101358067142` — **SUCCESS**;
- artifact `9975020241`, zip digest `sha256:b701ad58e32d538336f21279289bb189aca4324ec5029242d1f08246d4e1a493`;
- isolated app `dadrock-v143-http-bridge-control-gate` and isolated queue `dadrock-v143-async-results-control-gate`;
- exact bridge/protocol/worker/scheduler blob boundary passed;
- `startStatus=processing` and `orchestratorTracked=true`;
- first status was already bounded terminal `failed`, elapsed `1.121s`;
- `terminalErrorBounded=true`;
- `resultCleared=true`, `controlCleared=true`, TTL `900`;
- `audioBytesDownloaded=0`, `audioRead=false`, `separatorModelExecuted=false`;
- `productionBridgeTargeted=false`, `productionWorkerDeploymentChanged=false`;
- `referenceFacingInputs=0`, `referenceScoreCalls=0`, `qualityVerdictMade=false`;
- isolated app stopped after the gate.

**Conclusion:** the same hardened start/status/FunctionCall-control/terminal/ACK lifecycle is now proven to terminate deterministically without recursive/repeated spawn. The specific lifecycle blocker for the first model-bearing E2E is cleared.

## CLOSED ASYNC PROOFS RETAINED

- async protocol source gate `33965969177` / job `101306044525`, artifact `9969426651`, digest `sha256:e37ea0c100d7f1b487669ab018cc336e5e756c2d2d672cb637518a42b7d8def3`;
- forced multi-chunk structured-result roundtrip GREEN;
- HMAC signed-token roundtrip/tamper/wrong-secret rejection GREEN;
- 15-minute TTL and no-binary-payload boundary GREEN;
- source-level preservation of synchronous Lead/Bass fallback GREEN;
- hardened one-shot fail-fast proofs `33981347482`, `33981493357`, `33981664796` GREEN;
- production bridge deploy/smoke `33981874155` GREEN;
- Trusted GitHub OIDC Deployment Protection access GREEN: `33982502347` and refreshability proof `33982582372`.

## DRY GUARD REVIEW / BREAKTHROUGH HISTORY — 2026-09-05

- No `V143 Fresh Preview Async Breakthrough E2E` model-bearing run has been dispatched by this continuation.
- Live workflow blob before any planned repair: `bab50f03b26d728084fe898097b02c2470de2d2e`.
- All seven workflow source pins have been re-verified against the live branch and match exactly: route `742954146a86aa36485d0bbdb3fbd6691a64a712`, `/ai-tab` page `de39f2715c6875d757ef730c9e3182ccd4aa00a4`, bridge `36584355d9b060fc7b7e20acc62524fbc7bf9005`, protocol `1bd55017e16a4e1d8b14c7429492f811a43a28d8`, worker `111bf14a8f91045d3478901f8e36b88a2e7f181a`, scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`, approved audio `4dd709e3fa177b4daeed71ca97f0199757729d4b`.
- The earlier continuation read that surfaced stale `ANALYZE_ROUTE_SHA=877722150399048cec431769718664507767894c` was not the live workflow now on this branch. The stale-pin stop inference is **withdrawn**.
- Success-path guard audit is GREEN: fresh protected Preview only; no production promotion; protected `/ai-tab` HTTP-200 gate before model work; exactly one Rhythm POST start with `MODEL_BEARING_START_BUDGET=1` and `PREVIOUS_E2E_MODEL_STARTS=0`; require HTTP 202 + `v143a1.*` token; status-only polling of that same token; no second start; completed/generated-tab/runtime-contract checks; exactly one DELETE ACK on success; aggregate-only artifact intent; runner cleanup trap removes request/token/status/full-result material.
- Failure-path issue is **confirmed**: current terminal-`failed` handling writes `evidence/summary-pre-ack.json` and exits before the success-only DELETE ACK/final summary. A failed model-bearing job would therefore rely on TTL cleanup and would not preserve the intended final aggregate artifact.
- Backend semantics support the repair without touching model/runtime behavior: route DELETE can ACK the same signed token, and bridge ACK clears transient result + FunctionCall-control state independent of whether terminal state was `completed` or `failed`.
- Branch-wide active/pre-start Actions check is GREEN: `in_progress=0`, `queued=0`, `waiting=0`, `requested=0`, `pending=0`.

### Historical breakthrough run — found and inspected; model-start budget remains unused

- The workflow path has exactly one historical source commit before this continuation's planned repair: `58be9aa7b5606783a508917ce4531cfd512d66da`, message `test: run single async E2E on fresh Preview`.
- That commit produced `V143 Fresh Preview Async Breakthrough E2E` run `33982235357`, job `101349393362`, conclusion **failure**.
- Exact job-step evidence: source boundary GREEN; fresh protected Preview build/deploy GREEN; `Verify protected Preview access before model start` **FAILED**; `Start exactly one Rhythm async job and poll same token` **SKIPPED**.
- Therefore historical model-bearing start requests from this workflow remain **0**. The one model-bearing start budget has not been consumed.
- The fresh deployment was Preview target/Ready, deployment `dpl_F6ksguDvc1nVAt33jNxxoVTmyyJA`; production promotion remained false.
- Root failure at the pre-start gate: `vercel curl /ai-tab --deployment ...` returned HTTP **403** instead of 200. Because the next start step was skipped, no audio/model invocation occurred.
- The prior run also exposed the expected aggregate-evidence weakness: `summary.json` did not exist when the pre-start gate failed, so artifact upload warned that no file was found.
- **Do not rerun `33982235357`** and do not arm another E2E yet. Diagnose/fix protected Preview access in the trigger workflow using the already-proven Trusted GitHub OIDC Deployment Protection access pattern; do not disable/weaken protection. Combine that access repair with the checkpointed failure-path ACK/evidence repair so only one future trigger-workflow commit is needed.

### Exact workflow-only failure-path repair plan — checkpointed before trigger edit

1. Poll until terminal `completed` or `failed` and record `terminal_state`; do not exit inside the `failed` branch.
2. Run generated-tab/runtime safety assertions only for terminal `completed`.
3. Build aggregate pre-ACK evidence for either terminal state; retain no request body, signed token, raw result, audio, stems, or model bytes.
4. DELETE-ACK exactly once using the same signed token for either `completed` or `failed`.
5. Require `acknowledged=true` and transient cleanup evidence (`resultCleared` / `controlCleared` where returned).
6. Write common final aggregate `evidence/summary.json` after ACK.
7. If `terminal_state=failed`, only then fail the GitHub job with an explicit **do not retry / diagnose this one model-bearing call** message.
8. Make aggregate evidence upload `if: always()` so terminal-failure evidence survives the intentional job failure.
9. Preserve the one-start budget and all existing Preview-only, source-pin, no-production, no-reference-facing, runner-cleanup, and sensitive-data boundaries.

Because this workflow is push-triggered on changes to its own path, **the repair commit itself can be the single arming event**. Therefore no workflow edit is permitted until the protected-Preview 403 access fix is derived from the already-GREEN OIDC proof and checkpointed, and the live trigger/source pins are re-read immediately before editing.

## NEXT — REUSE PROVEN PROTECTED-PREVIEW ACCESS, THEN ARM ONE MODEL-BEARING E2E

1. Inspect the successful Trusted GitHub OIDC Deployment Protection runs `33982502347` and `33982582372` / their workflow source to identify the exact protected-Preview authorization command/header/token exchange that returned authorized access without weakening Deployment Protection.
2. Plan the minimal breakthrough-workflow access patch and checkpoint it before editing the trigger workflow.
3. Re-check active/pre-start Actions status and exact source pins after the checkpoint-only commits.
4. Re-read the trigger block; then make exactly one trigger-workflow repair commit containing both: protected Preview access repair + terminal-failure ACK/evidence repair.
5. Treat that push as the single arming event. Do not make another trigger-workflow edit or rerun if model execution starts.
6. Require fresh Preview Ready -> protected `/ai-tab` HTTP 200 -> exactly one Rhythm start -> HTTP 202 + `v143a1.*` token -> same-token status-only polling -> terminal result -> one ACK/cleanup -> aggregate artifact.
7. If the single model-bearing job fails after it truly starts, stop after ACK/evidence. Do not retry. Diagnose that exact call first.

## HARD STOPS

- No duplicate model-bearing request.
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement.
- No scheduler/model change for an async lifecycle symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL above 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

## FRESH CHAT HANDOFF — START HERE

The next chat should **read this file first and continue on `v143-contextual-prune-lobo`**. Do not repeat the Modal lifecycle diagnosis unless new evidence contradicts the GREEN gate above.

Immediate next steps for the fresh chat:

1. Treat historical breakthrough model-start count as conclusively **0**: prior run `33982235357` failed on protected Preview `/ai-tab` HTTP 403; model-bearing step was skipped.
2. Inspect the successful Trusted GitHub OIDC Deployment Protection access/refreshability proofs and derive the exact minimal authorization change for the breakthrough workflow. Do not disable protection.
3. Checkpoint the access patch plan before touching `.github/workflows/v143-fresh-preview-async-breakthrough-e2e.yml`.
4. Re-check all active/pre-start Action states and seven source pins immediately before the trigger edit.
5. Apply one combined trigger-workflow commit: protected Preview access repair + already-checkpointed terminal-failure ACK/evidence repair. That commit is the next and only arming event.
6. Watch the single run through. If model execution starts and later fails, ACK/record aggregate evidence and STOP; do not retry.
7. Save every meaningful milestone/root cause/result back to `docs/checkpoints/CURRENT_STATE.md` on this branch before continuing.

Current authorization state: **async lifecycle GREEN; exact source pins GREEN; prior breakthrough run found but model-start count remains 0; failure-path repair plan checkpointed; protected Preview 403 is the only remaining pre-arm technical blocker.**
