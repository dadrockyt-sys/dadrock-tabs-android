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
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; MAIN MERGE/BUILD/DEPLOY GREEN; PRODUCTION V143 RHYTHM ROUTING PROVEN ACTIVE; FROZEN V143 MODAL L4 WORKER + HTTP BRIDGE RESTORED GREEN; CORRECT BRIDGE LIVE IN PRODUCTION; DOWNLOAD-AUTH FIX GATE GREEN; NEXT = REDEPLOY PATCHED V143 L4 WORKER + REAL-AUDIO SMOKE; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

## Closed green foundation

- Phases 1–13 reference-blind V143 chain: **GREEN**. Phase 13 run `33833707924`, job `100901804298`, structured renderer `v143-structured-rhythm`, malformed analysis 400, reference score calls 0.
- Protected real-Vercel Preview: run `33843200741`, job `100929522781`, deployment `dpl_6pXryC9R7M5mJwZA7cUt2qh3bBsp`, `/ai-tab` 200, structured PDF 200, Deployment Protection preserved, reference score calls 0.
- Detailed histories remain under `docs/checkpoints/`.

## User-authorized merge to `main` — COMPLETE

- authorization received 2026-09-04 to merge V143 and begin testing with existing “Are You Gonna Go My Way” audio;
- resolved two-parent merge `ceeccfbbb17968c097bb56136487e7ddeaf1a5a4` preserved newer BTS/SEO/payment/site work while overlaying tested V143 Phase 1–13 path;
- full combined build run `33844133380`, job `100932278526`: **SUCCESS**;
- current `main` source SHA remains **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`**.

## Authorized existing Gomyway audio

- `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`;
- blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`;
- 3,464,988 bytes.

## Production real-audio diagnostics

1. Product static URL returned 404 before analyzer: run `33844432185`, job `100933164743`.
2. Raw-GitHub URL reached Production but legacy analyzer was selected because V143 env was absent: run `33844704674`, job `100933970052`, runtime `usingV143RhythmAnalyzer: false`; route 502.
3. Production V143 env restored and exact current `main` rebuilt/redeployed: run `33879884350`, job `101056165576`; deployment `dpl_CojGzPaq77YRh5mLpbVTEseuWjrg`.
4. Protected authenticated smoke proved V143 selected but obsolete Modal URL returned 404: run `33880271454`, job `101057491176`, runtime `usingV143RhythmAnalyzer: true`.
5. Frozen Modal topology restored from exact SHA `379ca54cce0f7f962c1e22caebfd6f49b8e4edb9`: run `33884039647`, job `101059368271`; L4 dependency smoke green; bridge unauthenticated POST = 401; reference score calls = 0.
6. Correct bridge env update required non-interactive `vercel env update --yes`; exact current `main` rebuilt and deployed successfully in run **`33884535351`**, job **`101060978549`**.

### Current Production deployment

- deployment: **`dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`**;
- source: exact unchanged `main` **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`**;
- target/status: Production / Ready;
- aliases include `dadrocktabs.com` and `www.dadrocktabs.com`;
- protected authenticated `/ai-tab`: **200**;
- Deployment Protection remained enabled.

### Restored-bridge Gomyway attempt — correct V143 stack reached, then 502 download failure

Run `33884535351`, job `101060978549`:

- Production V143 URL = restored bridge `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`;
- exact current `main` build/deploy: **SUCCESS**;
- protected `/ai-tab`: **200**;
- Gomyway Rhythm analysis: **502**;
- safe aggregate error: **`The analyzer could not download the audio file.`**;
- exact Production runtime:

```text
usingV143RhythmAnalyzer: true
analyzerData: { detail: 'The analyzer could not download the audio file.' }
```

Aggregate artifact only: `v143-production-restored-bridge-gomyway-v2`, artifact id `9941326017`. Raw analyzer output/tab/PDF was not retained. Preview was skipped because analysis was not 200.

## Download-auth repair — IMPLEMENTED / PREDEPLOY GATE GREEN

Root cause candidate in the restored worker was cross-origin forwarding of `BLOB_READ_WRITE_TOKEN`: `_download_blob_to_path` attached `Authorization: Bearer <blob token>` to every URL, including public raw GitHub audio.

### Patch on `v143-contextual-prune-lobo`

- `analyzer/v143_audio_download_auth.py` added as a pure policy module;
- Blob bearer authorization is emitted **only** for HTTPS `blob.vercel-storage.com` or `*.blob.vercel-storage.com`;
- public/non-Blob origins (including `raw.githubusercontent.com`) receive **no Authorization header**;
- deceptive suffix/lookalike hosts and HTTP Blob URLs receive no credential;
- `analyzer/v143_modal_live_endpoint.py` now uses the policy;
- V143 Modal image includes `v143_audio_download_auth`;
- `liveV143.referenceRuntimeInputUsed = false` is now explicitly emitted so current `main` can verify the complete four-flag anti-leakage contract.

Patch commits:

- policy module: `60888a515de3d53efa0f6bdd38cfa1e4bab727ef`;
- pure test script: `8f766b5962a75935e83be32342096e990dab8318`;
- worker wiring/runtime flag: `e79bb924f447c308ce035c38e2fb15032d296a96`;
- gate workflow: `266232f907e79422033bba21fafcfc7123b3ad11`.

### Green gate

Workflow `V143 Audio Download Auth Fix Gate`:

- run: **`33889340784`**;
- job: **`101076898337`**;
- result: **SUCCESS**;
- pure auth policy tests: **PASS**;
- worker wiring + runtime safety metadata verification: **PASS**;
- changed Python compile: **PASS**;
- reference-facing score calls: **0**;
- restricted reference bytes read: **0**;
- Production deployment changed by this gate: **false**;
- Modal deployment changed by this gate: **false**.

Test coverage includes raw GitHub, Vercel public Blob, Vercel private Blob, Vercel Blob API host, deceptive suffix host, lookalike host, HTTP Blob URL, empty token, malformed URL, and uppercase/trailing-dot normalization.

## Fresh-chat authorization — EXPLICIT

The user explicitly authorized continuation of the non-reference-facing Production work. Authorization covers exact V143 Modal worker/bridge restoration and narrowly scoped fixes required to exercise the existing reference-free pipeline with the repository-owned Gomyway audio, Vercel env correction/redeploy as required, workflow edits/reruns, preview/PDF contract checks with raw outputs discarded, and GitHub Actions/Vercel log inspection.

It **does not** authorize reference-facing accuracy scoring, restricted GOAT access, sealed GuitarSet prospective access, reopening SplitMySong terminal work, or weakening fail-closed/safety boundaries.

## Safety/accounting now

- merge to `main`: authorized and complete;
- current `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`;
- Production deployment: `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM` READY;
- Production V143 Rhythm route selection: **ACTIVE / PROVEN**;
- correct HTTP bridge: **ACTIVE / PROVEN**;
- current deployed L4 worker: frozen restored version, dependency smoke green;
- patched L4 worker: **PREDEPLOY GATE GREEN / NOT YET DEPLOYED**;
- Deployment Protection: **preserved**;
- reference-facing score calls: **0**;
- GOAT restricted bytes: **0**;
- GuitarSet prospective sealed reads: **0**;
- raw Gomyway transcription/PDF retained: **false**;
- current real-audio verdict: **NO PIPELINE QUALITY VERDICT YET — PATCH READY TO RESTORE PUBLIC-AUDIO INGEST**.

## NEXT SAFE ACTION — AUTHORIZED

1. Deploy only patched `analyzer/v143_modal_live_endpoint.py` + included policy module from current `v143-contextual-prune-lobo` head to Modal environment `main`; do not redeploy/change the HTTP bridge.
2. Re-run `rhythm_dependency_smoke`; require NVIDIA L4, seed 143, reference-free true, required imports true.
3. Re-run authenticated aggregate-only Production Gomyway Rhythm smoke against current Production deployment; no Vercel redeploy is required because the bridge URL is unchanged.
4. Require Production runtime `usingV143RhythmAnalyzer: true`, analysis HTTP 200, response `rhythmCanaryActive: true`, and all four runtime flags (`referenceFree=true`, `professionalReferenceUsed=false`, `referenceRuntimeInputUsed=false`, `runtimeLabelsRequired=false`).
5. If analysis reaches 200, generate Production structured preview; retain only aggregate quality/placement/PDF contract metadata and delete raw transcription/PDF/request outputs.
6. Report only internal signs of success; **reference-facing accuracy remains unarmed**.
