# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — async lifecycle GREEN; prior breakthrough pre-model 403 diagnosed; combined one-shot repair planned  
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

- Diagnostic workflow `V143 Async Bridge Startup Diagnosis` run `33985149949`, job `101357179709` — SUCCESS; no model/audio/reference-facing invocation by the diagnostic.
- Isolated lifecycle proof `V143 Async Control Tracking Smoke` rerun `33985474511`, job `101358067142` — SUCCESS; artifact `9975020241`, digest `sha256:b701ad58e32d538336f21279289bb189aca4324ec5029242d1f08246d4e1a493`.
- Proven lifecycle: start tracked; bounded terminal state; ACK clears transient result/control; TTL `900`; audio/model bytes absent from queue/control; reference-facing inputs/scores remain 0.
- **Conclusion:** lifecycle gate GREEN; do not reopen unless new evidence contradicts it.

## CLOSED ASYNC PROOFS RETAINED

- async protocol source gate `33965969177` / job `101306044525`, artifact `9969426651`, digest `sha256:e37ea0c100d7f1b487669ab018cc336e5e756c2d2d672cb637518a42b7d8def3`;
- forced multi-chunk structured-result roundtrip GREEN;
- HMAC signed-token roundtrip/tamper/wrong-secret rejection GREEN;
- 15-minute TTL and no-binary-payload boundary GREEN;
- source-level preservation of synchronous Lead/Bass fallback GREEN;
- hardened one-shot fail-fast proofs `33981347482`, `33981493357`, `33981664796` GREEN;
- production bridge deploy/smoke `33981874155` GREEN;
- Trusted GitHub OIDC Deployment Protection access GREEN: `33982502347`; refreshability proof `33982582372` GREEN.

## DRY GUARD REVIEW / BREAKTHROUGH HISTORY — 2026-09-05

- No model-bearing breakthrough run has been dispatched by this continuation.
- Live trigger workflow blob before repair: `bab50f03b26d728084fe898097b02c2470de2d2e`.
- All seven source pins match: route `742954146a86aa36485d0bbdb3fbd6691a64a712`, page `de39f2715c6875d757ef730c9e3182ccd4aa00a4`, bridge `36584355d9b060fc7b7e20acc62524fbc7bf9005`, protocol `1bd55017e16a4e1d8b14c7429492f811a43a28d8`, worker `111bf14a8f91045d3478901f8e36b88a2e7f181a`, scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`, approved audio `4dd709e3fa177b4daeed71ca97f0199757729d4b`.
- Earlier stale `877722150399048cec431769718664507767894c` route-pin inference is withdrawn; it was not the live workflow.
- Success-path guards are GREEN: fresh Preview only; no promotion; pre-start HTTP-200 protection gate; one Rhythm start budget; signed `v143a1.*` token; same-token status-only polling; no second start; product/runtime checks; one ACK; aggregate-only evidence intent.
- Failure-path issue confirmed: the current workflow exits on terminal failure before ACK/final `summary.json`; a failed model-bearing job would rely on TTL cleanup. Backend ACK is safe for completed or failed terminal jobs and clears both transient result and FunctionCall-control partitions.
- Branch-wide active/pre-start Actions check was GREEN: `in_progress=0`, `queued=0`, `waiting=0`, `requested=0`, `pending=0`.

### Historical breakthrough run — inspected; model-start budget remains unused

- Historical trigger source commit `58be9aa7b5606783a508917ce4531cfd512d66da` produced run `33982235357`, job `101349393362`, conclusion failure.
- Source boundary and Preview build/deploy were GREEN; `Verify protected Preview access before model start` failed HTTP **403**; model-bearing start step was **SKIPPED**.
- Historical model-bearing start requests from this workflow therefore remain **0**.
- Preview deployment was `dpl_F6ksguDvc1nVAt33jNxxoVTmyyJA`; no production promotion occurred.
- Do not rerun `33982235357`.

### Exact workflow-only failure-path repair plan

1. Poll until terminal completed/failed; do not exit inside terminal-failed parsing.
2. Defer completed-product/runtime assertions until after ACK.
3. Build bounded aggregate pre-ACK evidence for either terminal state; retain no request body, signed token, full result, audio, stems, or model bytes.
4. ACK exactly once with the same signed token after any terminal response.
5. Require `acknowledged=true` and `resultCleared=true` (bridge also clears FunctionCall-control state).
6. Write common final aggregate `summary.json` after ACK.
7. If terminal state failed or completed-product assertions fail, fail the GitHub job only **after** cleanup/evidence with explicit do-not-retry guidance.
8. Upload aggregate evidence with `if: always()` and retain runner cleanup `if: always()`.
9. Preserve one-start budget, source pins, Preview-only/no-promotion, no-reference-facing, and retention boundaries.

### Protected Preview 403 repair — derived and checkpointed before trigger edit

Successful proof `33982502347` showed Vercel protected Preview access returns HTTP 200 when the GitHub Actions OIDC JWT is sent as `x-vercel-trusted-oidc-idp-token`. Refreshability proof `33982582372` established:

- workflow must grant `id-token: write` in addition to `contents: read`;
- the shell receives `ACTIONS_ID_TOKEN_REQUEST_URL` and `ACTIONS_ID_TOKEN_REQUEST_TOKEN`;
- mint a JWT on demand with an authenticated GET to `ACTIONS_ID_TOKEN_REQUEST_URL`, parse response field `value`, and immediately mask it with `::add-mask::`;
- JWT TTL is **300 seconds**;
- newly minted tokens repeatedly returned protected `/ai-tab` HTTP 200 without disabling/weaking Deployment Protection;
- do **not** persist JWTs to files/artifacts/environment across long polling;
- the breakthrough workflow must mint a fresh token for the pre-start `/ai-tab` check, the one start POST, each status poll, and the terminal ACK POST, passing it only in the `x-vercel-trusted-oidc-idp-token` request header;
- replace protected `vercel curl` requests with direct `curl` against the exact fresh `PREVIEW_DEPLOYMENT_URL` so the proven trusted-header path is explicit; Vercel CLI remains only for Preview build/deploy/inspect;
- no production environment target or promotion command is added.

**Arming rule:** because the workflow triggers on a push changing its own file, the combined OIDC + terminal-failure repair commit is itself the single arming event. Immediately before that edit, re-read branch HEAD, active Actions state, all seven source pins, and trigger/concurrency guards. If any active breakthrough run or pin drift exists, do not edit/arm.

## NEXT — ONE COMBINED REPAIR/ARMING COMMIT

1. Re-check current branch HEAD and active/queued/waiting/requested/pending Actions immediately before edit.
2. Re-verify all seven source pins and trigger/concurrency one-run guard.
3. Make exactly one change to `.github/workflows/v143-fresh-preview-async-breakthrough-e2e.yml` containing both OIDC protected-access repair and terminal-failure ACK/evidence repair. Treat the resulting push as the single arming event.
4. Watch that one run: fresh Preview Ready -> protected `/ai-tab` 200 -> exactly one Rhythm start -> 202 + `v143a1.*` token -> same-token status-only polling -> terminal -> one ACK/cleanup -> aggregate artifact.
5. If model execution starts and later fails, stop after ACK/evidence. **Do not retry.** Diagnose that exact call first.
6. Save every meaningful milestone/root cause/result back to this checkpoint.

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

Continue on `v143-contextual-prune-lobo` from this file. Do not repeat the lifecycle diagnosis. Historical model-start count is conclusively 0 because run `33982235357` failed at protected Preview HTTP 403 before its model-bearing step. The OIDC access repair and failure-path cleanup repair are both fully derived above; the next permitted workflow change is one combined arming commit only after immediate active-run/source-pin revalidation.

Current authorization state: **async lifecycle GREEN; exact source pins GREEN at last check; prior model-start count 0; protected-Preview OIDC repair plan checkpointed; terminal-failure ACK/evidence plan checkpointed; next step is immediate revalidation followed by one combined trigger-workflow repair/arming commit if still clean.**
