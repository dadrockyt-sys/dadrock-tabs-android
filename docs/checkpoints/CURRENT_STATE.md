# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-04 (America/Toronto)  
Branch checkpoint: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## Global scientific state — unchanged

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**
- GOAT restricted bytes admitted/read = **0**; V168 prospective reference-facing score calls = **0**.
- SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`; never rerun/score/weaken/interpolate.
- GuitarSet V3/V4/V5 remain terminal; prospective players `00/01/03` remain sealed; prospective score calls = **0**.
- No reference-facing accuracy scoring has been run during Production/Modal performance work.

**Project Progress Score: 80%.**  
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; MAIN MERGE/BUILD/DEPLOY GREEN; PRODUCTION V143 ROUTING ACTIVE; DOWNLOAD-AUTH FIX GREEN; FULL GOMYWAY WORKER TIMES OUT AT 1200S; 725.802S STAGE GATE LOCALIZES BOTTLENECK TO FIRST DIRECT DEMUCS CPU/SINGLE-THREAD PASS; SINGLE 6S FROZEN BASELINE CLEANLY TIMES OUT AT 300S; CPU THREAD-COUNT TWEAK PATH CLOSED; EXPLICIT `cpu=1.0` NO-GPU FULL-FIXTURE ANCHOR GREEN WITH EXACT HASH PARITY AT 666.404S WALL; HISTORICAL STRICT/COLD CUDA PROOFS SHOW NON-EXACT CROSS-CONTAINER DEMUCS OUTPUTS; FINAL ONE-PASS L4 + PRIVATE-SHIFT + CPU-EXACT-PARITY GATE RUN 33916548691 ARMED; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

## Stable Production state

- current `main`: **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`** (re-verified before GPU gate);
- Production deployment: **`dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`**, READY;
- aliases include `dadrocktabs.com` / `www.dadrocktabs.com`;
- V143 bridge: `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`;
- Deployment Protection remains enabled;
- Production runtime has proven `usingV143RhythmAnalyzer=true`;
- **Production worker, bridge, and Vercel configuration have not been changed by the performance/identity diagnostics below.**

## Authorized Gomyway sources

- current bounded source: `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`, blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`, 3,464,988 bytes;
- approved reference-free identity fixture: `public/gomywayfullaitest.m4a`, SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`;
- raw diagnostic clips/stems remain ephemeral only.

## Decisive performance evidence

### Full direct worker — terminal timeout

- run `33890279981`, job `101079989844`;
- direct `dadrock-v143-ai-tab-live / rhythm_v143_request` call;
- worker timeout: **1200 seconds**;
- client wall including queue/startup: **1744.461 seconds**;
- reference score calls: 0; raw outputs retained: false.

### Stage localization — terminal

- run `33893769468`, job `101091458986`: bounded diagnostic SUCCESS;
- wall **725.802 seconds**;
- last decisive marker `separator.direct-demucs.start` at ~0.248 s;
- no `separator.direct-demucs.done` before the diagnostic window ended;
- bottleneck is the first direct Demucs6s CPU/single-thread pass.

Frozen Production Demucs policy remains CPU-only, one-thread, deterministic, oneDNN-disabled/conservative ISA, `htdemucs_6s`, Guitar, shifts=1, overlap=.10, segment=6, seed=143.

### Single 6-second frozen baseline — terminal clean timeout

- run **`33913842713`**, job **`101156325246`**;
- exactly one frozen call on a 6.0-second authorized clip;
- function call `fc-01M1Q00SSQNTHAQM8AAKXZWG2J`;
- hard deadline **300 seconds** -> `TimeoutError`;
- `call.cancel(terminate_containers=True)` succeeded;
- artifact **`9952542047`** uploaded;
- isolated app cleanup succeeded; Production untouched.

**Interpretation:** CPU thread-count tuning is closed. Structural acceleration only.

## Exact deterministic CPU identity — TERMINAL / GREEN

Historical oneDNN-off CPU anchor on `public/gomywayfullaitest.m4a`:

- historical run **`32692461330`**, job **`97328477497`**;
- result commit **`34471c7cdd061dbbc5ed807ba473bb2e156bc5f8`**;
- normalized WAV SHA256 **`ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`**;
- direct Guitar SHA256 **`0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`**;
- decoded PCM-int16 SHA256 **`2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`**;
- deterministic shift trace `0,22050,6026`;
- fixture duration **211.44 seconds**;
- historical Demucs separation **10:23** (~623s).

Fresh exact-anchor reproduction:

- workflow `.github/workflows/v143-demucs-explicit-cpu-anchor.yml`;
- trigger commit `391ef75d5cf0c4f50a9b9536126cd7a70bdf447f`;
- run **`33914759546`**, job **`101159244192`**, SUCCESS;
- function call **`fc-01M1Q0MFR88FXWAQ1R47TSX77Z`**;
- Modal `cpu=1.0`, memory 8192, no GPU;
- client wall **666.404 seconds**;
- source, normalized WAV, Guitar, decoded PCM and shift trace all reproduced exactly;
- PyTorch `2.13.0+cu130`; CPU capability DEFAULT; intra/inter-op threads 1; oneDNN disabled;
- `structuralInvariantsPassed=true`;
- `exactParityPassed=true`;
- artifact **`9953064061`** uploaded;
- diagnostic app cleanup succeeded;
- Production/Vercel untouched; reference calls 0; raw outputs retained false.

This is now the trustworthy reference-free deterministic identity anchor.

## Historical GPU/CUDA evidence — TERMINAL / FAIL-CLOSED

Read-only history inspection found two relevant classes of prior L4 evidence.

### Strict CUDA cross-container gate (August 21)

- trigger commit **`3a0693effd8125647411014a6ff01ea851deaf01`**;
- compact result commit **`626263e890d44099b1877286f38e594268f9b140`**;
- three concurrent L4 workers used seed 143, `CUBLAS_WORKSPACE_CONFIG=:4096:8`, Torch deterministic algorithms, cuDNN deterministic, TF32 disabled;
- normalized input was exact across all workers;
- direct Demucs PCM was **not exact across workers**;
- workers 2/3 matched one another but worker 1 differed;
- `directStemPcmExactAcrossWorkers=false`;
- Production/reference boundaries remained untouched.

### Later CUDA cold-session proof after startup determinism hardening (August 24)

- deterministic startup controls were added by `a89c6235bf862fd84576a246690a1c58f66eb0b7` and `f08641244b5a1f96a03e2563c601cffd14482e3e`;
- cold proof result commit **`faa12c1031fd740842e2c30c3e36ea6dc56246f3`**;
- three independent passes had exact source + normalized WAV + BS-RoFormer identity;
- direct Demucs Guitar hashes split between `5820375b...` and `41ad8bc3...`;
- cascade Demucs hashes also split;
- `allSeparatorHashesExact=false`;
- first mismatch remained direct Demucs.

These historical CUDA failures predate the final private-shift + exact oneDNN-off CPU anchor combination. They block any assumption that GPU is deterministic, but justify one final narrowly scoped current-controls GPU identity test.

## Final one-pass L4 exact-CPU-parity gate — ARMED / RUNNING

New isolated diagnostic:

- app source `analyzer/v143_demucs_gpu_exact_probe.py`, commit **`56fbba4ee1794b8232a1b5ca42a18f430381e1bb`**;
- collector `.github/scripts/v143_demucs_gpu_exact_collect.py`, commit **`7556688eb94de1ef66f0bf76ff489ad9ca0ebb61`**;
- workflow `.github/workflows/v143-demucs-gpu-exact-probe.yml`, trigger commit **`f53fab02c96ee64d6cab3caff54c468a0f43b9d6`**;
- GitHub Actions run **`33916548691`**, job **`101164931468`**;
- exactly one L4 direct-Demucs pass on the anchored full fixture;
- current final controls preserved: seed 143, private shift RNG, CUBLAS deterministic workspace, Torch deterministic algorithms, TF32 disabled, oneDNN disabled for CPU-side helpers, one CPU thread for helpers;
- musical settings unchanged: `htdemucs_6s`, Guitar, shifts=1, overlap=.10, segment=6;
- hard client deadline **300 seconds**;
- cancellation uses `call.cancel(terminate_containers=True)`;
- aggregate-only hash/timing output;
- exact CPU Guitar SHA + decoded PCM SHA + normalized SHA + shift trace are mandatory for a GREEN result;
- mismatch fails closed and is **not** promotion evidence;
- `always()` cleanup stops only `dadrock-v143-demucs-gpu-exact-probe`;
- Production/Vercel/reference state untouched.

## Fresh-chat authorization — EXPLICIT

The user explicitly authorized continuation of non-reference-facing Production work. Authorization covers narrowly scoped V143 worker/bridge fixes and deploys, workflow diagnostics, Vercel configuration/redeploy if required, repository-owned Gomyway audio, and aggregate-only Product/PDF contract checks with raw outputs discarded.

It **does not** authorize reference-facing accuracy scoring, restricted GOAT access, sealed GuitarSet prospective access, reopening SplitMySong terminal work, or weakening fail-closed/safety boundaries.

## Safety/accounting now

- `main`: unchanged at `bb992d901e78ab19645f8edc8e330d5a142ebd8e`;
- Production V143 routing: ACTIVE;
- Deployment Protection: preserved;
- reference-facing score calls: 0;
- GOAT restricted bytes: 0;
- GuitarSet prospective sealed reads: 0;
- raw Gomyway transcription/PDF/stems retained: false;
- current quality verdict: **NO QUALITY VERDICT — PERFORMANCE/IDENTITY DIAGNOSTICS ONLY**.

## NEXT SAFE ACTION — AUTHORIZED

1. Read terminal run/artifact for GPU gate `33916548691` and confirm isolated-app cleanup.
2. If GPU fails exact CPU identity, close GPU promotion under the current exact-output contract; do not weaken parity to force a speedup.
3. If GPU unexpectedly passes exact CPU identity, run one additional independent L4 call before any Production change to establish cross-container repeatability.
4. Only after exact identity + repeatability may a Production worker resource/execution change be considered; bridge/Vercel/UI remain unchanged unless independently required.
5. Do not reopen CPU thread-count tuning, oneDNN-enabled promotion, reference-facing scoring, or protected holdouts.
