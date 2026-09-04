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
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; MAIN MERGE/BUILD/DEPLOY GREEN; PRODUCTION V143 RHYTHM ROUTING ACTIVE; CORRECT HTTP BRIDGE ACTIVE; DOWNLOAD-AUTH FIX GREEN AND DEPLOYED; REAL-AUDIO CLEARS PRIOR DOWNLOAD FAILURE; DIRECT L4 GOMYWAY HITS WORKER 1200-SECOND TIMEOUT; NEXT = STAGE-TIMING INSTRUMENTATION BEFORE ANY EXECUTION-POLICY CHANGE; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

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

## Gomyway after download-auth fix — DOWNLOAD FAILURE CLEARED; VERCEL TIMEOUT OBSERVED

Workflow `.github/workflows/v143-production-gomyway-after-download-fix.yml`:

- workflow commit: **`6f9ed2fa38542a691565a93052bb2be5862f3cf7`**;
- run: **`33889779953`**;
- job: **`101078353122`**;
- exact current `main` reverified before request;
- protected `/ai-tab`: **200**;
- Gomyway analysis began around 15:30:10 UTC and returned **HTTP 504** around 15:32:41 UTC, approximately 151 seconds later;
- current Production route declares `export const maxDuration = 150`;
- prior download failure returned in about 13 seconds, so the patched worker clearly moved beyond the old ingest failure;
- preview skipped because analysis did not return 200;
- raw analysis/request/PDF cleanup: SUCCESS;
- aggregate-only artifact id **`9943447301`**;
- reference-facing score calls: **0**.

## Direct L4 Gomyway timing — TERMINAL TIMEOUT

Workflow `.github/workflows/v143-direct-l4-gomyway-timing.yml`:

- workflow commit: **`dca32a608a62021336542d67179a89253746de32`**;
- run: **`33890279981`**;
- job: **`101079989844`**;
- same exact repository-owned Gomyway asset;
- direct `modal.Function.from_name('dadrock-v143-ai-tab-live', 'rhythm_v143_request').remote(...)`;
- Blob token deliberately empty because source is public raw GitHub;
- safety/source preflight: PASS;
- direct call terminal result: **FAILED / FunctionTimeoutError**;
- measured client wall time: **1744.461 seconds**;
- Modal worker execution limit reached: **1200 seconds**;
- bounded aggregate error: `Task's current input ... hit its timeout of 1200s`;
- generated tab/event metadata unavailable because worker never returned;
- aggregate artifact: `v143-direct-l4-gomyway-timing`, id **`9944617862`**;
- reference-facing score calls: 0;
- raw transcription/PDF retained: false.

### Timing interpretation

- Vercel 150 seconds is not the root cause; it only hides the longer worker problem.
- Standard Vercel Pro Fluid Compute up to 800 seconds would still be insufficient for this observed path.
- The worker itself exhausts 1200 execution seconds, so async Vercel orchestration alone is not enough yet.
- No reason exists to raise Vercel duration until the worker stage bottleneck is measured and addressed.

## Strong code-level bottleneck candidate — must be timed before modification

`analyzer/v143_seeded_separator.py` currently runs the frozen separator graph in this order:

1. direct Demucs6s Guitar;
2. BS-RoFormer Instrumental;
3. cascade Demucs6s Guitar over the RoFormer result.

Both Demucs calls run under `DEMUCS_SINGLE_THREAD_ENV`, which explicitly sets:

- `CUDA_VISIBLE_DEVICES=''`;
- `OMP_NUM_THREADS=1`;
- `MKL_NUM_THREADS=1`;
- oneDNN disabled / conservative CPU ISA controls.

Thus the L4 worker deliberately executes both Demucs passes CPU-only and single-threaded for previously-proven deterministic repeatability, while RoFormer is allowed GPU execution. This is a strong latency candidate, but changing it would alter the frozen execution policy, so no acceleration change is authorized by inference alone.

## Fresh-chat authorization — EXPLICIT

The user explicitly authorized continuation of the non-reference-facing Production work. Authorization covers narrowly scoped V143 worker/bridge fixes and deploys, workflow diagnostics, Vercel configuration/redeploy if required, the existing repository-owned Gomyway audio, and aggregate-only Product/PDF contract checks with raw outputs discarded.

It **does not** authorize reference-facing accuracy scoring, restricted GOAT access, sealed GuitarSet prospective access, reopening SplitMySong terminal work, or weakening fail-closed/safety boundaries.

## Safety/accounting now

- `main`: unchanged and verified;
- Production V143 routing: ACTIVE;
- patched V143 worker: DEPLOYED / dependency smoke GREEN;
- public-audio immediate download failure: no longer observed;
- direct worker completion: **TIMEOUT at 1200 execution seconds**;
- Deployment Protection: preserved;
- reference-facing score calls: 0;
- GOAT restricted bytes: 0;
- GuitarSet prospective sealed reads: 0;
- raw Gomyway transcription/PDF retained: false;
- current real-audio verdict: **NO QUALITY VERDICT — WORKER RUNTIME BOTTLENECK MUST BE LOCALIZED**.

## NEXT SAFE ACTION — AUTHORIZED

1. Add non-musical timing markers only around worker stages: download, normalize, separator/router; inside separator: input normalization, direct Demucs, RoFormer, cascade Demucs; optionally downstream candidate/transcription stages if separator completes.
2. Compile/test instrumentation to prove it does not change separator settings, seeds, reference-free flags, or musical data flow.
3. Redeploy only the instrumented V143 worker; do not change Vercel or HTTP bridge.
4. Run one aggregate/log-only Gomyway diagnostic using `Function.spawn()` so the Modal call ID is known; collect only bounded `V143_STAGE` timing markers and terminal error metadata, never raw tab/events.
5. Use measured stage timing to choose the smallest performance repair. Do **not** move Demucs to GPU, relax determinism, or increase timeouts until stage evidence supports the change and a dedicated gate protects deterministic/reference-free behavior.
6. Only after the worker itself returns successfully should async Production orchestration or Vercel duration changes be implemented.
7. Reference-facing accuracy remains unarmed.
