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
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; MAIN MERGE/BUILD/DEPLOY GREEN; PRODUCTION V143 RHYTHM ROUTING ACTIVE; CORRECT HTTP BRIDGE ACTIVE; DOWNLOAD-AUTH FIX GREEN AND DEPLOYED; REAL-AUDIO NOW PASSES THE PRIOR IMMEDIATE DOWNLOAD-FAILURE WINDOW BUT HITS THE 150-SECOND VERCEL FUNCTION LIMIT; NEXT = DIRECT L4 COMPLETION/TIMING SMOKE; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

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
- Deployment Protection remains enabled.

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

**Interpretation boundary:** this is not yet a transcription-quality verdict. It is strong evidence that the public-audio download blocker was cleared and the next bottleneck is request duration/orchestration. Direct worker completion must be proven before changing the Vercel time budget.

## Fresh-chat authorization — EXPLICIT

The user explicitly authorized continuation of the non-reference-facing Production work. Authorization covers narrowly scoped V143 worker/bridge fixes and deploys, workflow diagnostics, Vercel configuration/redeploy if required, the existing repository-owned Gomyway audio, and aggregate-only Product/PDF contract checks with raw outputs discarded.

It **does not** authorize reference-facing accuracy scoring, restricted GOAT access, sealed GuitarSet prospective access, reopening SplitMySong terminal work, or weakening fail-closed/safety boundaries.

## Safety/accounting now

- `main`: unchanged and verified;
- Production V143 routing: ACTIVE;
- patched V143 worker: DEPLOYED / dependency smoke GREEN;
- public-audio immediate download failure: **no longer observed**;
- current blocker: **HTTP 504 at the route's 150-second duration boundary**;
- Deployment Protection: preserved;
- reference-facing score calls: 0;
- GOAT restricted bytes: 0;
- GuitarSet prospective sealed reads: 0;
- raw Gomyway transcription/PDF retained: false;
- current real-audio verdict: **NO QUALITY VERDICT — ANALYSIS OUTLIVES CURRENT VERCEL REQUEST WINDOW**.

## NEXT SAFE ACTION — AUTHORIZED

1. Invoke deployed `dadrock-v143-ai-tab-live / rhythm_v143_request` directly from a GitHub Actions diagnostic using the same public Gomyway URL and empty Blob token, bypassing only the Vercel request-duration layer.
2. Measure wall-clock completion and retain only aggregate metadata: completed/error, generatedTab present, event count, placement-related counts available in the worker result, and the four `liveV143` anti-leakage flags. Delete the raw worker response immediately after aggregation.
3. If the L4 worker completes successfully, choose the smallest supported Vercel duration/orchestration adjustment based on measured runtime; do not weaken analyzer/reference safety.
4. If the worker itself fails, diagnose that exact downstream stage before changing Vercel duration.
5. Only after Production analysis returns 200 should the structured preview be generated and aggregate quality/PDF contract metadata recorded.
6. Report internal signs of success only; **reference-facing accuracy remains unarmed**.
