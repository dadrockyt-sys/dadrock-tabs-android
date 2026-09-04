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
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; MAIN MERGE/BUILD/DEPLOY GREEN; PRODUCTION V143 RHYTHM ROUTING PROVEN ACTIVE; CORRECT HTTP BRIDGE LIVE; DOWNLOAD-AUTH FIX GATE GREEN; PATCHED V143 L4 WORKER DEPLOY + DEPENDENCY SMOKE GREEN; NEXT = REAL-AUDIO GOMYWAY PRODUCTION SMOKE; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

## Closed green foundation

- Phases 1–13 reference-blind V143 chain: **GREEN**. Phase 13 run `33833707924`, job `100901804298`, structured renderer `v143-structured-rhythm`, malformed analysis 400, reference score calls 0.
- Protected real-Vercel Preview: run `33843200741`, job `100929522781`, deployment `dpl_6pXryC9R7M5mJwZA7cUt2qh3bBsp`, `/ai-tab` 200, structured PDF 200, Deployment Protection preserved, reference score calls 0.
- Current `main`: **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`** (reverified after worker patch).

## Current Production web deployment — unchanged / verified

- Vercel deployment: **`dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`**;
- source: exact `main` `bb992d901e78ab19645f8edc8e330d5a142ebd8e`;
- state: **READY / production**;
- aliases include `dadrocktabs.com` / `www.dadrocktabs.com`;
- V143 analyzer URL points to restored decoupled bridge `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`;
- Deployment Protection remains enabled.

## Authorized existing Gomyway audio

- `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`;
- blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`;
- 3,464,988 bytes.

## Prior Production real-audio diagnostics

- static Product URL 404 before analyzer: run `33844432185`;
- raw GitHub with V143 env absent: legacy fallback, `usingV143RhythmAnalyzer=false`, 502;
- correct V143 bridge restored and selected: `usingV143RhythmAnalyzer=true`;
- restored-bridge Gomyway run `33884535351`, job `101060978549`: 502 `The analyzer could not download the audio file.`;
- raw analyzer/tab/PDF not retained; reference score calls 0.

## Download-auth repair — IMPLEMENTED / TESTED / DEPLOYED

Root cause candidate was cross-origin forwarding of `BLOB_READ_WRITE_TOKEN`: the worker attached the Blob bearer token to every audio URL, including raw GitHub.

Patch on `v143-contextual-prune-lobo`:

- `analyzer/v143_audio_download_auth.py` scopes Blob Authorization to HTTPS `blob.vercel-storage.com` / `*.blob.vercel-storage.com` only;
- raw GitHub and other public/non-Blob origins receive no Blob credential;
- deceptive/lookalike hosts, HTTP Blob URLs, malformed URLs and empty-token cases fail safe;
- worker now uses the policy;
- worker explicitly emits `liveV143.referenceRuntimeInputUsed=false` in addition to the existing anti-leakage flags.

### Predeploy gate — GREEN

- workflow: `V143 Audio Download Auth Fix Gate`;
- run **`33889340784`**, job **`101076898337`**;
- pure policy tests: PASS;
- worker wiring/runtime metadata: PASS;
- changed Python compile: PASS;
- Production/Modal changed by gate: false;
- reference score calls: 0.

### Patched L4 worker deploy — GREEN

- workflow: `.github/workflows/v143-deploy-patched-worker.yml`;
- workflow commit / deployed branch head: **`d881994ec311846d08b3288a0c2b58548b937d14`**;
- run: **`33889490536`**;
- job: **`101077392412`**;
- exact target app: `dadrock-v143-ai-tab-live` in Modal environment `main`;
- **only the worker was redeployed**; HTTP bridge and Vercel deployment were unchanged;
- deploy step: **SUCCESS**;
- `rhythm_dependency_smoke`: **SUCCESS**;
- required GPU/import/reference-free checks: **PASS**;
- aggregate artifact: `v143-patched-worker-deploy`, artifact id **`9943252415`**;
- reference score calls: **0**.

## Fresh-chat authorization — EXPLICIT

The user explicitly authorized continuation of the non-reference-facing Production work. Authorization covers narrowly scoped fixes required to exercise the existing reference-free pipeline with the repository-owned Gomyway audio, Modal worker/bridge deployment as required, workflow edits/reruns, preview/PDF contract checks with raw outputs discarded, and GitHub Actions/Vercel log inspection.

It **does not** authorize reference-facing accuracy scoring, restricted GOAT access, sealed GuitarSet prospective access, reopening SplitMySong terminal work, or weakening fail-closed/safety boundaries.

## Safety/accounting now

- `main`: unchanged and verified;
- Production web deployment: unchanged / READY;
- V143 HTTP bridge: restored / active;
- patched V143 L4 worker: **DEPLOYED / DEPENDENCY SMOKE GREEN**;
- Deployment Protection: **preserved**;
- reference-facing score calls: **0**;
- GOAT restricted bytes: **0**;
- GuitarSet prospective sealed reads: **0**;
- raw Gomyway transcription/PDF retained: **false**;
- current real-audio verdict: **NO PIPELINE QUALITY VERDICT YET — DOWNLOAD FIX IS LIVE; REAL-AUDIO RETEST IS NEXT**.

## NEXT SAFE ACTION — AUTHORIZED

1. Run authenticated aggregate-only Gomyway Rhythm smoke against current Production deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`; no Vercel redeploy is needed.
2. Require analysis HTTP 200, `rhythmCanaryActive=true`, and payload contract proof of all four anti-leakage conditions: reference-free true, professional reference not used, reference runtime input not used, runtime labels not required.
3. Record only aggregate event/quality/placement metadata; do not retain raw transcription/tab.
4. If analysis reaches 200, pass the structured response through Production preview and require HTTP 200, PDF content type, `%PDF`, and nontrivial byte size; delete PDF/request/raw analysis afterward.
5. Report internal signs of success only; **reference-facing accuracy remains unarmed**.
