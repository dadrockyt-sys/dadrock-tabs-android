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
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; RESOLVED MAIN INTEGRATION BUILD GREEN; PRODUCTION MERGE/DEPLOY READY; FIRST REAL-AUDIO ATTEMPT BLOCKED BY STATIC-ASSET 404; SECOND REAL-AUDIO ATTEMPT REACHED PRODUCTION ROUTE BUT EXPOSED V143 ANALYZER ENV MISCONFIGURATION; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

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

Authoritative corrected exact-SHA protected Preview gate:

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

PR #22 could not be merged directly because the long-lived V143 branch and current `main` had materially diverged. A blind history merge was rejected as unsafe because it could overwrite newer BTS/SEO/payment/site work.

A focused true two-parent resolved merge was therefore constructed from prior `main` plus the tested V143 head:

- prior `main`: `68cd39c7b5901f533f2b0d570567cb15c79c66da`;
- V143 checkpoint head used as second parent: `b83c3eef6bbb6911863d467aa97e2b24d1576cc3`;
- resolved merge commit: **`ceeccfbbb17968c097bb56136487e7ddeaf1a5a4`**;
- temporary validation branch: `v143-main-integration-20260904`;
- full combined Next.js production build run `33844133380`, job `100932278526`: **SUCCESS**.

The resolved integration preserved current `main` BTS/SEO/payment/site wiring and overlaid the tested V143 Phase 1–13 analysis/conditioning/Product-placement path plus hardened structured Rhythm renderer internals.

`main` was then fast-forwarded through the validated integration lineage. A main checkpoint commit triggered the normal Production deployment:

- deployed main SHA: **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`**;
- Production deployment: **`dpl_6wzaPcM1eM5o42WmrssZu966sdSs`**;
- state / readyState: **READY**;
- target: **production**;
- canonical aliases include `dadrocktabs.com` and `www.dadrocktabs.com`.

Production merge/deployment was explicitly authorized by the user. No reference-facing score was authorized or run by this merge.

## “Are You Gonna Go My Way” real-audio smoke — diagnostics

The authorized test audio exists in the repository on both the V143 branch and current `main`:

- path: `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`;
- blob SHA: **`4dd709e3fa177b4daeed71ca97f0199757729d4b`**;
- size: **3,464,988 bytes**.

### Attempt 1 — static Production URL

Workflow `.github/workflows/v143-production-gomyway-smoke.yml`, run `33844432185`, job `100933164743`, stopped at the precondition GET because `https://dadrocktabs.com/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a` returned Vercel **404 NOT_FOUND** despite the file existing in GitHub `main`.

Verdict: **NO PIPELINE VERDICT — STATIC ASSET 404 PRECONDITION**. No analyzer call, reference score, generated tab, or PDF evidence was preserved.

### Attempt 2 — raw GitHub URL

The non-Production integration branch was updated to use:

`https://raw.githubusercontent.com/dadrockyt-sys/dadrock-tabs-android/main/public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`

- integration branch head: `8fd6fa9a6eafcf38c97a5811eb6fb4075c221a88`;
- workflow run: **`33844704674`**;
- job: **`100933970052`**;
- Production `/api/analyze-audio-tab` response: **502**;
- safe aggregate error: **`The analyzer could not download the audio file.`**;
- raw analysis/tab/PDF was not uploaded; only aggregate summary artifact was retained;
- reference score calls = **0**.

Most important Production runtime-log finding for exact deployment `dpl_6wzaPcM1eM5o42WmrssZu966sdSs`:

```text
Modal analyzer error: {
  transcriptionType: 'rhythm',
  usingV143RhythmAnalyzer: false,
  analyzerData: { detail: 'The analyzer could not download the audio file.' }
}
```

Therefore the merged V143 route code is live, but the exact Production deployment is **not selecting the V143 Rhythm analyzer**. The current `app/api/analyze-audio-tab/route.js` selects V143 Rhythm only when `process.env.ANALYZER_API_URL_V143` is present. Production fell back to the legacy analyzer and that legacy analyzer then failed to download the raw GitHub asset.

This means Attempt 2 is **not a V143 transcription-quality verdict**. It is a Production analyzer-selection/configuration diagnostic.

## Fresh-chat authorization — EXPLICIT

On 2026-09-04 the user explicitly asked to save next steps to `CURRENT_STATE.md` with authorization for a fresh chat to continue. That authorization remains active for the non-reference-facing Production diagnostics described here, including workflow edits/reruns, Production Rhythm route calls using the existing repository-owned Gomyway audio, preview/PDF contract checks with raw outputs discarded, and reading GitHub Actions/Vercel logs.

This authorization **does not** arm or authorize any reference-facing accuracy score, restricted GOAT access, sealed GuitarSet prospective asset access, reopening SplitMySong terminal work, or weakening any existing fail-closed/safety boundary.

## Safety / accounting through this checkpoint

- merge to `main`: **authorized and complete**;
- Production deployment: **authorized and READY**;
- current Production aliases: expected canonical aliases only;
- reference-facing accuracy score calls during this work: **0**;
- GOAT restricted bytes read: **0**;
- GuitarSet prospective sealed assets read: **0**;
- SplitMySong terminal path reopened: **false**;
- raw real-audio transcription/PDF preserved to artifacts: **false**;
- Attempt 1 reached analyzer: **false**;
- Attempt 2 reached Production analysis route: **true**;
- Attempt 2 selected V143 Rhythm analyzer: **false**;
- current real-audio verdict: **NO V143 PIPELINE VERDICT — PRODUCTION V143 ANALYZER ENV/SELECTION NOT ACTIVE**.

## NEXT SAFE ACTION — AUTHORIZED

1. Identify the previously validated V143 analyzer deployment/endpoint from branch checkpoints/deployment history without exposing or changing unrelated secrets.
2. Verify whether Production has `ANALYZER_API_URL_V143`; current runtime evidence says it is absent/unavailable to the deployed function.
3. Restore the already-tested V143 Rhythm analyzer selection in Production using the existing V143 endpoint/configuration, preserving legacy Lead/Bass behavior and all fail-closed safety contracts.
4. Redeploy Production only if required for the environment change to take effect.
5. Re-run the aggregate-only Gomyway smoke. Confirm runtime logs show `usingV143RhythmAnalyzer: true` before accepting any pipeline interpretation.
6. If the V143 analyzer itself cannot fetch the raw GitHub asset, diagnose its download path separately; do not weaken URL/network safety broadly.
7. Only after a 200 analysis response, pass structured events through Production preview and record aggregate quality/placement and PDF contract metadata while deleting raw transcription/PDF outputs.
8. Report only **internal signs of success**; reference-facing accuracy remains unarmed.
