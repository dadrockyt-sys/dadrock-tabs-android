# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 12:50 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO REFERENCE-FACING QUALITY VERDICT** — performance/identity/routing/product-health diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`.
- Async storage authorization: transient structured result + non-sensitive FunctionCall control metadata only; no raw audio/stems/model bytes; TTL <= 900 seconds; no persistent result cache.

## Production baseline — UNCHANGED

- Vercel `main` `bb992d901e78ab19645f8edc8e330d5a142ebd8e`, deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, synchronous route blob `06234db3e1cc1680b18fd62a765862b213ede3db` / `maxDuration=150`.
- No production Vercel promotion and no whole-branch merge.
- L4 worker unchanged: `dadrock-v143-ai-tab-live/rhythm_v143_request`, live blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`, scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Hardened production HTTP bridge deployed GREEN: bridge blob `36584355d9b060fc7b7e20acc62524fbc7bf9005`, protocol blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`; deploy run `33981874155` / job `101348420851`, artifact `9973991338`.

## Async architecture / branch pins

Plan `docs/checkpoints/V143_ASYNC_JOB_ARCHITECTURE_PLAN.md`, commit `e0aef99dcdf931b66c0e1a081160e3cc5c6cb3c2`.

Rhythm: start -> signed opaque token -> browser polls Vercel -> Vercel polls bridge -> transient Modal Queue -> existing V143 safety/product pipeline -> result -> ACK clears result + control. Lead/Bass stay synchronous.

- route blob `742954146a86aa36485d0bbdb3fbd6691a64a712`;
- `/ai-tab` page blob `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.

## Modal `oneshot` report — FIXED / PROVEN / DEPLOYED

Root robustness gap was pre-hardening loss of `.spawn()` FunctionCall state: an orchestrator dying before Queue publication could appear `processing` forever. Hardened bridge tracks opaque FunctionCall ID, polls with `FunctionCall.from_id(...).get(timeout=0)`, returns terminal bounded failure for dead calls, and ACK clears result + control partitions.

Proofs GREEN:

- source gate `33981347482` / `101347008342`, artifact `9973838904`;
- isolated hardened bridge `33981493357` / `101347398382`;
- decisive fail-fast transition `33981664796` / `101347836824`, artifact `9973957720`;
- hardened production bridge deploy/smoke `33981874155` / `101348420851`.

## Preview async breakthrough E2E — FIRST ATTEMPT STOPPED IN PREFLIGHT / ZERO MODEL STARTS

Workflow `.github/workflows/v143-preview-async-breakthrough-e2e.yml`, creation commit `27d9af18496888564eec32f8858b29c4b988e4c9`.

Run `33982105469`, job `101349042393`:

- exact route/page/bridge/protocol/worker/scheduler/audio source fingerprints: **SUCCESS**;
- Node/Vercel CLI setup: **SUCCESS**;
- old Preview deployment inspection: still exact ID `dpl_FzuFoFNsaZcaV73RXSTejoH6cLpz`, target `preview`, status `Ready`;
- protected `/ai-tab` access unexpectedly returned **HTTP 403** through `vercel curl` at `2026-09-05 17:49Z`;
- therefore Preview preflight step **FAILED** and model-bearing step 7 was **SKIPPED**;
- `modelBearingStartRequestCount=0` for this attempt;
- no audio read/model execution caused by this E2E attempt;
- no job token/result/transcription existed; cleanup completed;
- Production Vercel untouched.

The same old Preview had authenticated correctly about five hours earlier in run `33968019067`, so this is a stale/protection-access condition on that historical deployment, not evidence against async routing or the hardened Modal bridge.

## NEXT STEP — FRESH PREVIEW, STILL ONE MODEL START TOTAL

Do **not** weaken/disable Deployment Protection and do not use Production Vercel.

1. Modify the E2E workflow to pull current **Preview** branch environment, build the exact current branch source, and deploy a fresh protected Preview only (`vercel build` + `vercel deploy --prebuilt`, never `--prod`).
2. Require new deployment target `preview`, Ready, route/page/runtime source pins unchanged, and authenticated `vercel curl /ai-tab` = 200.
3. Only after that preflight succeeds, issue the **first and only model-bearing Rhythm start request**. The failed run launched zero starts, so the authorized model-start budget remains one.
4. Poll the same signed token beyond 150s if required; require terminal tab + V143 safety/product contract; ACK once; preserve aggregate-only evidence.
5. On any model-bearing failure, do not start again; diagnose first.

Approved source remains `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`, Git blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`.

### Hard stops

- **Exactly one model/audio start request total after successful fresh-Preview preflight.**
- No Production Vercel environment change/promotion.
- No Deployment Protection weakening/disablement.
- No model/scheduler change.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL above 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.
