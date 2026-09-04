# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-04 (America/Toronto)  
Branch checkpoint: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## Global scientific state — unchanged

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**
- GOAT restricted bytes admitted/read = **0**; V168 prospective reference-facing score calls = **0**.
- SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`; never rerun/score/weaken/interpolate.
- GuitarSet V3/V4/V5 remain terminal; prospective players `00/01/03` remain sealed; prospective score calls = **0**.
- No reference-facing score was run during merge/Production/Modal work.

**Project Progress Score: 78%.**  
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; MAIN MERGE/BUILD/DEPLOY GREEN; PRODUCTION V143 RHYTHM ROUTING ACTIVE; CORRECT HTTP BRIDGE ACTIVE; DOWNLOAD-AUTH FIX GREEN AND DEPLOYED; REAL-AUDIO CLEARS PRIOR DOWNLOAD FAILURE BUT EXCEEDS 150-SECOND VERCEL WINDOW; DIRECT L4 TIMING RUN IS STILL ACTIVE WELL BEYOND THAT WINDOW; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

## Closed green foundation

- Phases 1–13 reference-blind V143 chain: **GREEN**.
- Protected real-Vercel Preview: **GREEN**, Deployment Protection preserved.
- Current `main`: **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`**.

## Current Production web deployment — unchanged / verified

- deployment: **`dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`**;
- source: exact `main` `bb992d901e78ab19645f8edc8e330d5a142ebd8e`;
- target/state: Production / READY;
- aliases include `dadrocktabs.com` and `www.dadrocktabs.com`;
- V143 URL: `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`;
- Deployment Protection remains enabled;
- Vercel team plan verified as **Pro**.

## Authorized existing Gomyway audio

- `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`;
- blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`;
- 3,464,988 bytes;
- public diagnostic URL: raw GitHub `main` asset.

## V143 Modal topology — restored / active

- HTTP bridge app `dadrock-v143-http-bridge`, endpoint `analyze`;
- L4 worker app `dadrock-v143-ai-tab-live`, function `rhythm_v143_request`;
- bridge unauthenticated POST fails closed 401;
- Production runtime has proven `usingV143RhythmAnalyzer=true`.

## Download-auth repair — TESTED / DEPLOYED GREEN

The restored worker previously attached `BLOB_READ_WRITE_TOKEN` to every audio origin. The patch:

- adds `analyzer/v143_audio_download_auth.py`;
- sends Blob Authorization only to HTTPS `blob.vercel-storage.com` / `*.blob.vercel-storage.com`;
- sends no Blob credential to raw GitHub/public/non-Blob origins;
- rejects deceptive/lookalike hosts for credential forwarding;
- explicitly emits `liveV143.referenceRuntimeInputUsed=false` so current `main` can verify all four anti-leakage conditions.

Predeploy gate:

- run **`33889340784`**, job **`101076898337`**: **SUCCESS**;
- pure policy tests/wiring/compile: PASS;
- reference score calls: 0.

Patched worker deploy:

- branch workflow head **`d881994ec311846d08b3288a0c2b58548b937d14`**;
- run **`33889490536`**, job **`101077392412`**: **SUCCESS**;
- only L4 worker redeployed; bridge/Vercel unchanged;
- `rhythm_dependency_smoke`: **SUCCESS**;
- aggregate artifact id `9943252415`;
- reference score calls: 0.

## Gomyway after download-auth fix — DOWNLOAD FAILURE CLEARED; VERCEL TIMEOUT NOW BLOCKS

Workflow `.github/workflows/v143-production-gomyway-after-download-fix.yml`:

- workflow commit: **`6f9ed2fa38542a691565a93052bb2be5862f3cf7`**;
- run: **`33889779953`**;
- job: **`101078353122`**;
- exact current `main` reverified before request;
- protected `/ai-tab`: **200**;
- Gomyway analysis began around 15:30:10 UTC and returned **HTTP 504** around 15:32:41 UTC, approximately 151 seconds later;
- current Production route declares `export const maxDuration = 150`;
- prior download failure returned in about 13 seconds, so this run is materially different and is consistent with the patched worker progressing into long-running analysis before the Vercel request window expired;
- response body was non-JSON/empty at the runner, so no analyzer payload contract was available;
- preview was intentionally skipped because analysis did not return 200;
- raw analysis/request/PDF cleanup: **SUCCESS**;
- aggregate-only artifact id **`9943447301`**;
- reference-facing score calls: **0**.

## Direct L4 Gomyway timing — IN PROGRESS / IMPORTANT LATENCY EVIDENCE

Workflow `.github/workflows/v143-direct-l4-gomyway-timing.yml`:

- workflow commit: **`dca32a608a62021336542d67179a89253746de32`**;
- run: **`33890279981`**;
- job: **`101079989844`**;
- same exact repository-owned Gomyway asset;
- direct `modal.Function.from_name('dadrock-v143-ai-tab-live', 'rhythm_v143_request').remote(...)`;
- Blob token deliberately empty because the source is public raw GitHub;
- only Vercel request-duration is bypassed; analyzer/reference safeguards remain intact;
- safety/source preflight: PASS;
- Modal auth: PASS;
- direct worker call remains **IN PROGRESS** and has already outlived the 150-second Production route window by a wide margin;
- no aggregate result/artifact exists yet because the function call has not returned;
- reference-facing score calls: 0.

### Current duration/orchestration interpretation

- Vercel Pro team plan is confirmed.
- Current route is hard-coded to 150 seconds.
- Current Vercel documentation states Fluid Compute is configurable up to 800 seconds on Pro/Enterprise, with an extended 1,800-second duration available only in beta for supported runtimes.
- Because the direct Modal wall time is already many minutes and still unresolved, a modest `maxDuration` increase is not sufficient evidence-based remediation.
- If direct L4 finishes under a supported ceiling, a bounded long-duration smoke can prove the synchronous path; if it exceeds the supported ceiling or remains operationally excessive, move Rhythm to asynchronous submit/status orchestration rather than weakening analyzer logic.

**Interpretation boundary:** no transcription-quality verdict has been made. We are measuring infrastructure/runtime behavior only.

## Fresh-chat authorization — EXPLICIT

The user explicitly authorized continuation of the non-reference-facing Production work. Authorization covers narrowly scoped V143 worker/bridge fixes and deploys, workflow diagnostics, Vercel configuration/redeploy if required, the existing repository-owned Gomyway audio, and aggregate-only Product/PDF contract checks with raw outputs discarded.

It **does not** authorize reference-facing accuracy scoring, restricted GOAT access, sealed GuitarSet prospective access, reopening SplitMySong terminal work, or weakening fail-closed/safety boundaries.

## Safety/accounting now

- `main`: unchanged and verified;
- Production V143 routing: ACTIVE;
- patched V143 worker: DEPLOYED / dependency smoke GREEN;
- public-audio immediate download failure: **no longer observed**;
- current blocker: **synchronous request duration / unresolved direct worker latency**;
- Deployment Protection: preserved;
- reference-facing score calls: 0;
- GOAT restricted bytes: 0;
- GuitarSet prospective sealed reads: 0;
- raw Gomyway transcription/PDF retained: false;
- current real-audio verdict: **NO QUALITY VERDICT — DIRECT L4 COMPLETION/TIMING STILL PENDING**.

## NEXT SAFE ACTION — AUTHORIZED

1. Let run `33890279981` reach a terminal state and inspect only its aggregate timing/result artifact.
2. If the L4 worker completes successfully, use measured wall time to choose the smallest supported Production orchestration change; do not change analyzer/reference behavior.
3. If direct runtime is <=800 seconds and repeat/warm evidence supports it, a bounded Pro `maxDuration` smoke may be tested before redesigning the UI.
4. If direct runtime exceeds 800 seconds, hits Modal's own timeout, or is too variable for synchronous UX, implement an authenticated async Rhythm submit/status flow while preserving the existing Lead/Bass path and all four V143 anti-leakage checks.
5. Only after Production analysis returns 200 should the structured preview be generated and aggregate quality/PDF contract metadata recorded.
6. Report internal signs of success only; **reference-facing accuracy remains unarmed**.
