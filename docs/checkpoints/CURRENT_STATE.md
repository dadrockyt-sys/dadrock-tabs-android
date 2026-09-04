# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-04 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints under `docs/checkpoints/` remain authoritative; omission here does not revoke frozen boundaries.

## Frozen scientific/safety boundaries — unchanged

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes read = **0**; prospective reference-facing score calls = **0**.
- SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`; do not reopen/weaken/interpolate.
- GuitarSet prospective players `00/01/03` remain sealed; prospective score calls = **0**.
- No reference-facing accuracy scoring has been run during current Production/performance work.
- Current quality verdict: **NO QUALITY VERDICT — PERFORMANCE/IDENTITY DIAGNOSTICS ONLY**.

## Stable Production — unchanged

- `main`: **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`** (re-verified before GPU gate);
- Production deployment: `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, READY;
- V143 bridge: `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`;
- Production routing has proven `usingV143RhythmAnalyzer=true`;
- Deployment Protection preserved;
- Production worker/bridge/Vercel have not been changed by these diagnostics.

## Authorized reference-free audio

- bounded source: `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`, blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`;
- exact identity fixture: `public/gomywayfullaitest.m4a`, SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`;
- raw diagnostic clips/stems remain ephemeral; aggregate hashes/timing only are retained.

## Decisive performance state

- full direct V143 worker: run `33890279981`, worker timeout **1200s**, client wall **1744.461s**;
- stage-localization run `33893769468`: **725.802s**, stopped inside first `separator.direct-demucs` pass;
- single frozen 6-second Demucs run `33913842713`: clean **300s `TimeoutError`**, remote cancellation + cleanup GREEN;
- CPU thread-count tuning path is **CLOSED / DO NOT REOPEN**.

Frozen Production Demucs execution remains CPU-only, one-thread, oneDNN-disabled/conservative ISA, `htdemucs_6s`, Guitar, shifts=1, overlap=.10, segment=6, seed=143.

## Exact deterministic CPU identity — GREEN

Historical oneDNN-off anchor:

- normalized WAV SHA256 `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- direct Guitar SHA256 `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`;
- decoded PCM-int16 SHA256 `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`;
- shift trace `0,22050,6026`;
- fixture duration 211.44s; historical separation ~623s.

Fresh reproduction:

- workflow `.github/workflows/v143-demucs-explicit-cpu-anchor.yml`;
- run **`33914759546`**, job **`101159244192`**, SUCCESS;
- function call `fc-01M1Q0MFR88FXWAQ1R47TSX77Z`;
- Modal `cpu=1.0`, no GPU; client wall **666.404s**;
- exact source/normalized/Guitar/PCM/shift parity = GREEN;
- PyTorch `2.13.0+cu130`, oneDNN disabled, intra/inter-op = 1;
- artifact `9953064061`;
- cleanup GREEN; Production untouched; reference calls 0.

This is the current fail-closed reference-free output identity anchor.

## Historical CUDA evidence — FAIL-CLOSED

Read-only branch history shows GPU Demucs has previously failed exact cold/cross-container determinism:

- strict three-L4 cross-container result commit `626263e890d44099b1877286f38e594268f9b140`: direct PCM not exact across workers;
- later startup-determinism cold proof result `faa12c1031fd740842e2c30c3e36ea6dc56246f3`: source/normalized/BS-RoFormer exact, direct Demucs split between two hashes; `allSeparatorHashesExact=false`;
- these runs used CUDA deterministic controls but predate the final current private-shift + exact oneDNN-off CPU-anchor combination.

Therefore GPU is not assumed safe; one final current-controls exact-CPU-parity test is justified.

## Current final L4 exact-parity gate

Files:

- `analyzer/v143_demucs_gpu_exact_probe.py` — initial commit `56fbba4ee1794b8232a1b5ca42a18f430381e1bb`;
- `.github/scripts/v143_demucs_gpu_exact_collect.py` — `7556688eb94de1ef66f0bf76ff489ad9ca0ebb61`;
- workflow `.github/workflows/v143-demucs-gpu-exact-probe.yml`.

Gate contract:

- exactly one L4 direct-Demucs pass on the full approved fixture;
- seed 143, private shift RNG, CUBLAS deterministic workspace, Torch deterministic algorithms, TF32 disabled;
- model/settings unchanged (`htdemucs_6s`, Guitar, shifts=1, overlap=.10, segment=6);
- 300s client deadline; `call.cancel(terminate_containers=True)` on failure/timeout;
- aggregate-only output; raw stem/audio not retained;
- exact CPU normalized/Guitar/PCM/shift parity required; mismatch fails closed;
- `always()` cleanup targets only `dadrock-v143-demucs-gpu-exact-probe`.

### First trigger — TERMINAL / PREFLIGHT-ONLY FAILURE

- trigger commit `f53fab02c96ee64d6cab3caff54c468a0f43b9d6`;
- run **`33916548691`**, job **`101164931468`**;
- failed in static boundary before Python/Modal install/deploy/audio execution;
- cause: private-shift flag was inherited via `DEMUCS_SINGLE_THREAD_ENV`, but the workflow intentionally required an explicit source-level `V143_DEMUCS_FIXED_SHIFT_RNG` declaration;
- no Modal app was deployed; no audio ran; no artifact was expected;
- Production untouched.

Harness correction:

- commit **`383c34c71eebb48b2b7f9597cdeb34aa61269ddd`** explicitly sets `gpu_env["V143_DEMUCS_FIXED_SHIFT_RNG"] = "1"` while still removing only `CUDA_VISIBLE_DEVICES` so L4 remains visible;
- no model/audio/parity/deadline change.

### Retry — ARMED / RUNNING

- workflow retrigger commit **`9c6b8a47bb1742b46d2d6e41b0426359c3ee5123`**;
- run **`33916705535`**, job **`101165425904`**;
- currently starting checkout/preflight;
- no second/parallel audio diagnostic is authorized while this run is active.

## Authorization

User explicitly authorized continuation of non-reference-facing V143 Production/performance work, including repository-owned Gomyway audio, isolated Modal diagnostics, narrowly scoped worker/bridge fixes/deploys, and aggregate-only Product/PDF checks. This does **not** authorize reference-facing scoring, GOAT access, sealed GuitarSet access, SplitMySong reopening, or weakening fail-closed boundaries.

## NEXT SAFE ACTION

1. Read terminal outcome/artifact for retry run **`33916705535`** and confirm isolated-app cleanup.
2. If GPU completes but mismatches exact CPU identity, close GPU promotion under the current exact-output contract; do not weaken parity for speed.
3. If GPU unexpectedly passes exact CPU identity, run exactly one additional independent L4 call to prove cross-container repeatability before any Production change.
4. Only exact identity + repeatability may justify a Production worker execution/resource change. Bridge/Vercel/UI remain unchanged unless independently required.
5. Reference-facing accuracy remains unarmed.
