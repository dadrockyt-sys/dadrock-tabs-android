# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-04 (America/Toronto)  
Branch checkpoint: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## Global scientific state — unchanged

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**
- GOAT Zenodo `15690894` / DOI `10.5281/zenodo.15690894` v1 access still awaits explicit owner approval/denial.
- Restricted GOAT bytes admitted/read = **0**; V168 prospective reference-facing score calls = **0**.
- SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`; never rerun/score/weaken/interpolate.
- GuitarSet V3/V4/V5 remain terminal; prospective players `00/01/03` remain sealed and prospective score calls = **0**.
- No new reference-facing score was run during merge/Production smoke work.

**Project Progress Score: 78%.**  
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; RESOLVED MAIN INTEGRATION BUILD GREEN; PRODUCTION MERGE/DEPLOY GREEN; PRODUCTION V143 RHYTHM SELECTION NOW PROVEN ACTIVE; REAL-AUDIO V143 VERDICT BLOCKED BY MISSING/SUPERSEDED MODAL HTTP ENDPOINT; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

## Phases 1–13 — CLOSED GREEN

- Phase 1–7 reference-blind conditioning/shadow/mixture/analyzer chain: frozen gates **SUCCESS**.
- Phase 8 server observation admission: run `33827081887`, job `100881934408`, **SUCCESS**; final branch gate `33827731955`, job `100883875983`, **SUCCESS**.
- Phase 9 admitted shadow effect: run `33828829026`, job `100887194463`, **SUCCESS**.
- Phase 10 Product-placement candidate: run `33829600963`, job `100889565032`, **SUCCESS**; synthetic placement 0% -> 100%, 7/7 exact.
- Phase 11 live candidate canary: run `33830896322`, job `100893491799`, **SUCCESS**.
- Phase 12 canonical Product/PDF placement: run `33831663771`, job `100895770003`, head `fdd54716641d2df73e5794cd3abadf06e78da208`, **SUCCESS**; renderer `v143-structured-rhythm`; PDF 1,665,393 bytes; placement 0 -> 7; exact 7/7.
- Phase 13 built-Next canonical HTTP gate: run `33833707924`, job `100901804298`, head `ed776202b60ee410beb455db16ee820e260ff17b`, **SUCCESS**; 95/95 static pages; analysis 200; promotion 0 -> 7 exact 7/7; Product/PDF 200; feature `v143-branch-preview-canary`; renderer `v143-structured-rhythm`; PDF 1,665,404 bytes; malformed analysis 400.

Detailed Phase 13 result: `docs/checkpoints/SONGSTERR_V143_BUILT_NEXT_CANONICAL_PROMOTION_HTTP_GATE_PHASE13_RESULT_20260903.md`.

## Protected real-Vercel Preview smoke — CLOSED GREEN

- workflow: `.github/workflows/v143-protected-preview-smoke.yml`;
- source commit: `12567e284d76b5c95240ad823628e311df3fc5e3`;
- run `33843200741`, job `100929522781`: **SUCCESS**;
- deployment `dpl_6pXryC9R7M5mJwZA7cUt2qh3bBsp`: **READY**, Preview/non-Production;
- `GET /ai-tab`: 200, 38,016 bytes;
- structured Product/PDF: 200, `application/pdf`, `%PDF`, renderer `v143-structured-rhythm`, 1,665,759 bytes;
- malformed analysis: 400 before analyzer;
- Deployment Protection remained enabled;
- reference score calls = 0.

Detailed result: `docs/checkpoints/SONGSTERR_V143_REAL_VERCEL_PROTECTED_PREVIEW_SMOKE_RESULT_20260904.md`.

## User-authorized merge to `main` — COMPLETE

Fresh explicit authorization was received on 2026-09-04 to merge V143 to `main` and begin testing the current pipeline with the existing “Are You Gonna Go My Way” audio.

PR #22 could not be merged directly because the long-lived V143 branch and current `main` had materially diverged. A focused true two-parent resolved merge preserved newer BTS/SEO/payment/site wiring while overlaying the tested V143 Phase 1–13 analysis/conditioning/Product-placement path and structured Rhythm renderer internals.

- prior `main`: `68cd39c7b5901f533f2b0d570567cb15c79c66da`;
- V143 merge parent: `b83c3eef6bbb6911863d467aa97e2b24d1576cc3`;
- resolved merge: `ceeccfbbb17968c097bb56136487e7ddeaf1a5a4`;
- integration branch: `v143-main-integration-20260904`;
- full combined Next production build run `33844133380`, job `100932278526`: **SUCCESS**;
- current/deployed `main` source SHA remains **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`**.

No reference-facing score was authorized or run by the merge.

## “Are You Gonna Go My Way” real-audio smoke — diagnostics

Authorized existing audio:

- `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`;
- blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`;
- 3,464,988 bytes.

### Attempt 1 — Product static URL

Run `33844432185`, job `100933164743`: `https://dadrocktabs.com/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a` returned Vercel 404 before analyzer.

Verdict: **NO PIPELINE VERDICT — STATIC ASSET 404 PRECONDITION**.

### Attempt 2 — raw GitHub URL, V143 env absent

Run `33844704674`, job `100933970052`: Production route returned 502 `The analyzer could not download the audio file.` Runtime log showed:

```text
usingV143RhythmAnalyzer: false
```

The route had fallen back to the legacy analyzer because `ANALYZER_API_URL_V143` was absent. Raw output/PDF was not preserved; reference score calls = 0.

### Attempt 3 — restore Production V143 selection and exact-main redeploy

Diagnostic workflow commit on `v143-main-integration-20260904`: `0c919f1dc1723750434ec1fd564d6c314a71b06d`.

- run `33879884350`, job `101056165576`;
- added/updated only Production `ANALYZER_API_URL_V143`;
- rebuilt exact current `main` SHA `bb992d901e78ab19645f8edc8e330d5a142ebd8e` with refreshed Production env;
- Production deploy/inspect passed;
- current Production deployment: **`dpl_CojGzPaq77YRh5mLpbVTEseuWjrg`**;
- generated deployment URL: `https://dadrock-tabs-android-icc2vvo6e-stephen-mcnally-s-projects.vercel.app`;
- canonical aliases include `dadrocktabs.com` / `www.dadrocktabs.com`;
- direct unauthenticated generated-URL smoke received 401 because Deployment Protection is enabled.

A follow-up canonical-domain attempt also received 403 unauthenticated. **Deployment Protection was not disabled or weakened.**

### Attempt 4 — authenticated protected Production smoke

Workflow `.github/workflows/v143-production-gomyway-postconfig-smoke.yml`, commit `71d69ba2716b55ff35c012bec054db7f5c042810` on `v143-main-integration-20260904` uses authenticated `vercel curl`, preserving Deployment Protection.

- run `33880271454`, job `101057491176`;
- protected `/ai-tab` access: **200**;
- Production `/api/analyze-audio-tab`: **502**;
- exact Production runtime proof on deployment `dpl_CojGzPaq77YRh5mLpbVTEseuWjrg`:

```text
Modal API returned 404 {}
Modal analyzer error: {
  transcriptionType: 'rhythm',
  usingV143RhythmAnalyzer: true,
  analyzerData: {}
}
```

This is decisive: **Production V143 Rhythm selection is now correctly configured and active.** The next failure is downstream at the configured Modal endpoint, which returned 404. No reference-facing score was run and raw transcription/PDF was not retained.

## Correct V143 Modal topology recovered from frozen history

An initial recovery used the older worker-app URL:

`https://dadrockyt--dadrock-v143-ai-tab-live-analyze.modal.run`

That URL is obsolete for the decoupled Production HTTP topology. Commit `d40f2a2eaecd05a7ac094ce31fa427a1a9eb3096` (`Point V143 HTTP smoke at lightweight bridge`) changed the validated HTTP smoke endpoint to:

**`https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`**

Frozen checkpoint-branch source confirms the architecture:

- `analyzer/v143_modal_live_endpoint.py`
  - worker Modal app: `dadrock-v143-ai-tab-live`;
  - frozen Rhythm GPU function: `rhythm_v143_request`;
  - L4 GPU, deterministic separator seed 143;
  - `liveV143.referenceFree = true`;
  - `professionalReferenceUsed = false`;
  - `runtimeLabelsRequired = false`.
- `analyzer/v143_modal_http_endpoint.py`
  - lightweight web app: `dadrock-v143-http-bridge`;
  - public endpoint function: `analyze`;
  - Lead/Bass stay on existing `modal_analyzer` behavior;
  - Rhythm is forwarded by `modal.Function.from_name('dadrock-v143-ai-tab-live', 'rhythm_v143_request')`;
  - request token check remains fail-closed;
  - no reference/scoring/evaluator payload is admitted by this bridge.

Therefore the next safe restoration target is the **decoupled HTTP bridge URL**, with the worker app restored only if its named function is also absent.

## Fresh-chat authorization — EXPLICIT

On 2026-09-04 the user explicitly asked to save next steps to `CURRENT_STATE.md` with authorization for a fresh chat to continue. Authorization remains active for non-reference-facing Production diagnostics, exact frozen V143 Modal worker/bridge restoration, workflow edits/reruns, Production Rhythm calls using the existing repository-owned Gomyway audio, preview/PDF contract checks with raw outputs discarded, and GitHub Actions/Vercel log inspection.

This authorization **does not** arm or authorize any reference-facing accuracy score, restricted GOAT access, sealed GuitarSet prospective asset access, reopening SplitMySong terminal work, or weakening any existing fail-closed/safety boundary.

## Safety / accounting through this checkpoint

- merge to `main`: **authorized and complete**;
- Production deployment: **authorized and READY**;
- Production V143 Rhythm routing: **ACTIVE / PROVEN**;
- Deployment Protection: **preserved**;
- reference-facing accuracy score calls during this work: **0**;
- GOAT restricted bytes read: **0**;
- GuitarSet prospective sealed assets read: **0**;
- SplitMySong terminal path reopened: **false**;
- raw real-audio transcription/PDF preserved to artifacts: **false**;
- current real-audio verdict: **NO V143 PIPELINE VERDICT — PRODUCTION ROUTING FIXED; DOWNSTREAM MODAL HTTP BRIDGE/WORKER RESTORATION REQUIRED**.

## NEXT SAFE ACTION — AUTHORIZED

1. Verify whether `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run` still exists; a live unauthorized request should fail closed at auth rather than 404.
2. If the bridge is absent, deploy exact frozen `analyzer/v143_modal_http_endpoint.py` from `v143-contextual-prune-lobo` using existing Modal GitHub secrets/environment `main`.
3. Verify the named worker `dadrock-v143-ai-tab-live / rhythm_v143_request`; if absent, deploy exact frozen `analyzer/v143_modal_live_endpoint.py` from the checkpoint branch first, then the HTTP bridge.
4. Change Production `ANALYZER_API_URL_V143` from the obsolete worker-app URL to the validated decoupled bridge URL; redeploy exact current `main` only if Vercel requires a new deployment for the environment change.
5. Run a fail-closed/no-reference bridge health smoke, then rerun the authenticated aggregate-only Gomyway Production smoke.
6. Accept a pipeline interpretation only if runtime proves `usingV143RhythmAnalyzer: true` and analysis returns 200 with `rhythmCanaryActive: true`.
7. Only then pass structured events through Production preview and record aggregate quality/placement/PDF contract metadata while deleting raw transcription/PDF outputs.
8. Report only **internal signs of success**; reference-facing accuracy remains unarmed.
