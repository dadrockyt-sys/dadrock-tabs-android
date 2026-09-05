# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — async lifecycle GREEN; fresh-Preview preflight BLOCKED on historical breakthrough-run check only  
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

## DRY GUARD REVIEW — 2026-09-05 — SOURCE/SUCCESS PATH GREEN; FAILURE-PATH PATCH PLANNED; HISTORICAL-RUN CHECK OPEN

- No `V143 Fresh Preview Async Breakthrough E2E` model-bearing run has been dispatched by this continuation.
- Live workflow blob before any planned repair: `bab50f03b26d728084fe898097b02c2470de2d2e`.
- All seven workflow source pins have been re-verified against the live branch and match exactly: route `742954146a86aa36485d0bbdb3fbd6691a64a712`, `/ai-tab` page `de39f2715c6875d757ef730c9e3182ccd4aa00a4`, bridge `36584355d9b060fc7b7e20acc62524fbc7bf9005`, protocol `1bd55017e16a4e1d8b14c7429492f811a43a28d8`, worker `111bf14a8f91045d3478901f8e36b88a2e7f181a`, scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`, approved audio `4dd709e3fa177b4daeed71ca97f0199757729d4b`.
- The earlier continuation read that surfaced stale `ANALYZE_ROUTE_SHA=877722150399048cec431769718664507767894c` was not the live workflow now on this branch. The stale-pin stop inference is **withdrawn**.
- Success-path guard audit is GREEN: fresh protected Preview only; no production promotion; protected `/ai-tab` HTTP-200 gate before model work; exactly one Rhythm POST start with `MODEL_BEARING_START_BUDGET=1` and `PREVIOUS_E2E_MODEL_STARTS=0`; require HTTP 202 + `v143a1.*` token; status-only polling of that same token; no second start; completed/generated-tab/runtime-contract checks; exactly one DELETE ACK on success; aggregate-only artifact intent; runner cleanup trap removes request/token/status/full-result material.
- Failure-path issue is **confirmed**: current terminal-`failed` handling writes `evidence/summary-pre-ack.json` and exits before the success-only DELETE ACK/final summary. A failed model-bearing job would therefore rely on TTL cleanup and would not preserve the intended final aggregate artifact.
- Backend semantics support the repair without touching model/runtime behavior: route DELETE can ACK the same signed token, and bridge ACK clears transient result + FunctionCall-control state independent of whether terminal state was `completed` or `failed`.
- Branch-wide active/pre-start Actions check is GREEN at this checkpoint: `in_progress=0`, `queued=0`, `waiting=0`, `requested=0`, `pending=0`. There is no currently active hidden duplicate on this branch.
- Historical workflow-specific check is still open. This must prove whether `V143 Fresh Preview Async Breakthrough E2E` has ever run/model-started before, because the execution contract requires `PREVIOUS_E2E_MODEL_STARTS=0`. **Do not edit/arm the trigger workflow until that history check is conclusively GREEN.**

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

Because this workflow is push-triggered on changes to its own path, **the repair commit itself can be the single arming event**. Therefore no workflow edit is permitted until the historical run/model-start check is GREEN and the live trigger is re-read immediately before editing.

## NEXT — FIRST SINGLE MODEL-BEARING END-TO-END TEST

Use `.github/workflows/v143-fresh-preview-async-breakthrough-e2e.yml` because it builds a **fresh protected Vercel Preview only**, pins the exact route/page/bridge/protocol/worker/scheduler/audio blobs, and hard-codes `modelBearingStartRequestBudget=1` / `priorE2EModelStarts=0` / `productionEnvironmentTargeted=false` / `productionPromotionPerformed=false`.

Required execution contract:

1. Create a fresh protected Preview from `v143-contextual-prune-lobo`; do not promote it.
2. Verify protected `/ai-tab` returns HTTP 200 before model start.
3. POST exactly **one** Rhythm start using approved `gomyway-midterm-source.m4a`.
4. Require HTTP 202 + signed `v143a1.*` job token.
5. Poll only that same token; never send a second start.
6. Allow total analysis time >150s while each Vercel request remains bounded.
7. Require terminal HTTP 200 + completed job + generated tab + V143 reference-free safety/product contract.
8. ACK once; require `acknowledged=true` and transient result cleanup. On terminal failure, ACK/cleanup and aggregate evidence must still happen before the workflow fails.
9. Persist aggregate evidence only; delete request/token/result material on the runner.
10. If the single model-bearing job fails after it truly starts, **do not launch another**; diagnose the one failed run first.

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

1. Treat all seven exact source pins, the success-path guard audit, the backend failed-job ACK semantics, the workflow-only failure-path patch plan, and branch active/pre-start Actions counts as GREEN unless new branch changes invalidate them.
2. Conclusively determine historical `V143 Fresh Preview Async Breakthrough E2E` runs/model-bearing starts. If any run exists, inspect it before arming anything; if a model-bearing start already occurred, HARD STOP and do not launch another.
3. If historical start count is conclusively zero, re-read the live workflow trigger and exact current source pins immediately before editing.
4. Apply only the checkpointed workflow failure-path repair. The repair commit can be the single arming push; do not make a second trigger-workflow edit after arming.
5. Watch that single run through: fresh Preview Ready -> `/ai-tab` protected HTTP 200 -> exactly one Rhythm start returns HTTP 202 + `v143a1.*` token -> status polling only -> terminal result -> one ACK/cleanup -> aggregate artifact.
6. If terminal HTTP 200 succeeds, require completed analysis, generated tab, V143 runtime safety/product contract, then ACK once and verify transient cleanup. Record aggregate metrics/artifact IDs/digests only.
7. If the single model-bearing job fails **after worker/model execution begins**, stop after ACK/evidence. Do not retry. Pull GitHub/Modal logs for that exact call and diagnose before any second start.
8. Save every meaningful milestone/root cause/result back to `docs/checkpoints/CURRENT_STATE.md` on this branch before continuing.

Current authorization state for the fresh chat: **async lifecycle gate GREEN; exact source pins GREEN; success-path E2E guards GREEN; failure-path repair plan checkpointed; no active/pre-start branch Actions runs; first single fresh-Preview model-bearing E2E remains the next permitted model-bearing action, but dispatch stays BLOCKED until historical breakthrough-run/model-start status is conclusively resolved.**
