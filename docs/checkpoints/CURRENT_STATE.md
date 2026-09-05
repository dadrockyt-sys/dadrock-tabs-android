# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — fresh-chat handoff  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## FROZEN BOUNDARIES

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO REFERENCE-FACING QUALITY VERDICT** — performance/identity/routing/product-health diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`.
- Async storage authorization: transient structured result + non-sensitive FunctionCall control metadata only; no raw audio/stems/model bytes; TTL <= 900 seconds; no persistent result cache.

## PRODUCTION BASELINE

- Vercel `main` remains `bb992d901e78ab19645f8edc8e330d5a142ebd8e`, production deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, synchronous route blob `06234db3e1cc1680b18fd62a765862b213ede3db`, `maxDuration=150`.
- No production Vercel promotion and no whole-branch merge.
- L4 worker remains `dadrock-v143-ai-tab-live/rhythm_v143_request`, live blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`, seeded scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Hardened HTTP bridge source previously deployed GREEN: bridge blob `36584355d9b060fc7b7e20acc62524fbc7bf9005`, protocol blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`; deploy run `33981874155` / job `101348420851`, artifact `9973991338`.

## ASYNC ARCHITECTURE / BRANCH PINS

Plan: `docs/checkpoints/V143_ASYNC_JOB_ARCHITECTURE_PLAN.md`, commit `e0aef99dcdf931b66c0e1a081160e3cc5c6cb3c2`.

Intended Rhythm path:

`start -> signed opaque token -> browser polls Vercel -> Vercel polls bridge -> transient Modal Queue/control -> existing V143 safety/product pipeline -> result -> ACK clears transient state`

Lead/Bass remain synchronous.

Branch UI/API pins from async wiring:

- route blob `742954146a86aa36485d0bbdb3fbd6691a64a712`;
- `/ai-tab` page blob `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.

## CLOSED ASYNC PROOFS BEFORE CURRENT REGRESSION REPORT

The following were GREEN before the new user-observed Modal behavior:

- async protocol source gate `33965969177` / job `101306044525`, artifact `9969426651`, digest `sha256:e37ea0c100d7f1b487669ab018cc336e5e756c2d2d672cb637518a42b7d8def3`;
- forced multi-chunk structured-result roundtrip GREEN;
- HMAC signed-token roundtrip/tamper/wrong-secret rejection GREEN;
- 15-minute TTL and no-binary-payload boundary GREEN;
- source-level preservation of synchronous Lead/Bass fallback GREEN;
- prior hardened one-shot fail-fast proofs `33981347482`, `33981493357`, `33981664796` GREEN;
- production bridge deploy/smoke `33981874155` GREEN;
- fresh Vercel Preview `dpl_F6ksguDvc1nVAt33jNxxoVTmyyJA` Ready;
- Trusted GitHub OIDC Deployment Protection access GREEN: `33982502347` and refreshability proof `33982582372`; each minted token TTL 300s and protected Preview returned HTTP 200.

## NEW USER-REPORTED REGRESSION SIGNAL — MODAL `oneshot` LOOPING / FAILING TO START

**Fresh user observation:** Modal is reporting the `oneshot` looping and failing to start.

This supersedes the earlier assumption that the one-shot lifecycle is fully settled. Treat the async model-bearing breakthrough E2E as **BLOCKED / NOT AUTHORIZED TO START** until this live behavior is understood.

Important uncertainty:

- prior checkpoint recorded model/audio start requests = 0 before the planned breakthrough E2E;
- after this new Modal report, the current actual start-attempt count is **UNKNOWN until logs/history are inspected**;
- do **not** assume the one remaining model-bearing budget is untouched;
- do **not** launch another model/audio request while diagnosing.

The current symptom could be in the bridge `start` endpoint, the lightweight async orchestrator/one-shot FunctionCall, control-state publication, Modal spawn lifecycle, app/container startup, or a duplicate/retry trigger. Do not guess which layer without evidence.

## FRESH-CHAT NEXT STEPS — DIAGNOSTIC ONLY FIRST

### 1. Establish the exact live failure without starting audio/model work

- Read current Modal app history/logs for the hardened HTTP bridge and any async orchestrator/`oneshot` function.
- Identify exact function-call IDs/container IDs and timestamps for the loop/fail-to-start events.
- Determine whether Modal is repeatedly creating new FunctionCalls, retrying the same FunctionCall, repeatedly cold-starting a container, or failing before the worker is invoked.
- Confirm whether `rhythm_v143_request` was ever actually invoked during the reported loop.
- Count actual model/audio starts from logs rather than relying on the old checkpoint count.

### 2. Verify deployment/source identity before changing code

- Confirm deployed bridge app still corresponds to bridge blob `36584355d9b060fc7b7e20acc62524fbc7bf9005` and protocol blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`.
- Confirm live worker remains blob `111bf14a8f91045d3478901f8e36b88a2e7f181a` with scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Check whether any later workflow/deploy unintentionally changed the bridge or created a duplicate app/function target.

### 3. Inspect async control/queue state without invoking the worker

- Inspect only metadata/status for the transient control/result partitions involved in the looping job(s).
- Verify whether FunctionCall IDs are being stored once or overwritten/recreated.
- Verify `start` is idempotent for a single browser action and cannot recursively invoke itself.
- Verify `status` performs lookup/poll only and cannot call `start`/`spawn`.
- Verify browser polling does not resend the original analysis body in a way that the route interprets as a fresh `start`.
- Verify failed/dead FunctionCall status becomes terminal instead of returning `processing` forever.

### 4. Reproduce only with a no-model synthetic one-shot if needed

If logs/source inspection alone cannot isolate it, create an isolated synthetic async one-shot that sleeps/returns a tiny JSON object and uses the same start/status/control mechanics but **never calls `rhythm_v143_request`, never reads audio, and never touches the production result partition**.

Require:

- exactly one FunctionCall created;
- start returns once;
- status transitions pending/processing -> completed or bounded failed;
- no recursive/repeated spawn;
- ACK/control cleanup works;
- no model/audio execution.

### 5. Fix the narrow lifecycle bug, then re-run source/synthetic gates

- Do not modify the seeded scheduler/model path for this symptom.
- Do not weaken HMAC, TTL, anti-leakage, or cleanup rules.
- Checkpoint exact root cause and the narrow fix before any deployment.
- Deploy only the bridge/control layer if that is the faulty layer.

### 6. Only after one-shot lifecycle is GREEN again

Then return to the previously planned single async breakthrough E2E:

1. Use fresh Preview `dpl_F6ksguDvc1nVAt33jNxxoVTmyyJA` or create a new preview only if source changed.
2. Mint fresh Trusted GitHub OIDC token.
3. POST exactly one Rhythm start using approved source `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`, Git blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`.
4. Require HTTP 202 + signed `v143a1.*` job token.
5. Poll only the same token; mint a fresh OIDC token per protected request.
6. Allow total analysis time >150s while each Vercel request stays short.
7. Require terminal HTTP 200 + generated tab + V143 reference-free safety/product contract.
8. ACK once and require result/control cleanup.
9. Persist aggregate evidence only; delete request/token/result files.
10. If that single model-bearing job fails after it truly starts, **do not launch another**; diagnose first.

## HARD STOPS FOR NEXT CHAT

- **Do not start the planned model-bearing breakthrough E2E until the Modal `oneshot` loop/fail-start report is diagnosed and lifecycle gate is GREEN again.**
- Do not assume model/audio start budget remains 1 until current Modal logs prove actual start count.
- No duplicate model-bearing request.
- No production Vercel promotion/change while diagnosing.
- No Deployment Protection weakening/disablement.
- No scheduler/model change for an async lifecycle symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL above 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.
