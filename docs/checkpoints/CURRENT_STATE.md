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

- `main`: **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`**;
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
- CPU intra-op/thread-count tuning path is **CLOSED / DO NOT REOPEN**.

Frozen Production Demucs execution remains CPU-only, one-thread, oneDNN-disabled/conservative ISA, `htdemucs_6s`, Guitar, shifts=1, overlap=.10, segment=6, seed=143.

## Exact deterministic CPU identity — GREEN

- normalized WAV SHA256 `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- direct Guitar SHA256 `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`;
- decoded PCM-int16 SHA256 `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`;
- shift trace `0,22050,6026`;
- fresh run **`33914759546`**, job `101159244192`, function call `fc-01M1Q0MFR88FXWAQ1R47TSX77Z`;
- Modal `cpu=1.0`, no GPU; client wall **666.404s**;
- exact source/normalized/Guitar/PCM/shift parity GREEN;
- PyTorch `2.13.0+cu130`, oneDNN disabled, intra/inter-op = 1;
- artifact `9953064061`; cleanup GREEN; Production/reference boundaries untouched.

This is the fail-closed reference-free output identity anchor.

## Final current-controls L4 gate — TERMINAL / FAIL-CLOSED

- run **`33916705535`**, job **`101165425904`**, function call `fc-01M1Q1ZA6GFSF1NZTPFF2GQA9P`;
- NVIDIA L4; client wall **51.663s**; separation **42.404s**; speedup **12.899x**;
- source, normalized WAV, dimensions and private shift trace exact;
- GPU Guitar SHA `5820375b67d6d3ad38386c267f8e21b721a06446ba9d8b4de14260d832d2f5a4`;
- GPU PCM SHA `376c33be95e277f811f1edc2bea14a4d6287f4ad7ae4e8eca2c5c84134b9341b`;
- `runtimeInvariantsPassed=true`, **`exactCpuParityPassed=false`**;
- artifact `9953451993`; cleanup GREEN; Production/reference boundaries untouched.

**GPU PROMOTION IS CLOSED.** Do not rerun GPU or weaken exact identity for speed.

## Exact split-parallel CPU architecture — SOURCE FEASIBILITY GREEN / UNTESTED

Read-only inspection of the exact installed dependency source (`nomadkaraoke/python-audio-separator` tag `v0.44.5`) found a native architecture-level acceleration path that is materially different from the already-closed intra-op thread-count experiments:

1. `audio_separator/separator/architectures/demucs_separator.py` calls bundled `apply_model(...)` but does **not** pass `num_workers`, so it defaults to 0.
2. Bundled `audio_separator/separator/uvr_lib_v5/demucs/apply.py` defines `apply_model(..., num_workers=0, pool=None)`.
3. If `num_workers > 0` and `device.type == "cpu"`, it creates `ThreadPoolExecutor(num_workers)`.
4. In split mode it submits each existing Demucs segment/chunk to the pool concurrently.
5. Crucially, it stores futures in original offset order and later iterates `for future, offset in futures`, calls `future.result()`, and performs the existing weighted overlap-add in that **same original deterministic offset order** before the unchanged final `out /= sum_weight`.
6. Recursive chunk calls have `split=False`; model/settings/chunk boundaries/weights/reduction formula are unchanged.

This means a diagnostic can test **chunk-level concurrency with per-op Torch threads still fixed at 1**, rather than changing intra-op numerical threading. The exact reduction order is preserved by the dependency itself. This is therefore structurally eligible for an exact-hash gate.

Safest implementation strategy: diagnostic-only child CLI wrapper that monkeypatches the architecture module's imported `apply_model` symbol to inject `num_workers=4`, while reusing the existing seeded child runtime, private shift RNG, oneDNN-off controls and `separate_demucs_guitar` path. Do not modify Production code until exact parity is proven.

## Authorization

User explicitly authorized continuation of non-reference-facing V143 Production/performance work, including repository-owned Gomyway audio, isolated Modal diagnostics, narrowly scoped worker/bridge fixes/deploys, and aggregate-only Product/PDF checks. This does **not** authorize reference-facing scoring, GOAT access, sealed GuitarSet access, SplitMySong reopening, or weakening fail-closed boundaries.

## NEXT SAFE ACTION

1. Build one isolated **CPU split-parallel `num_workers=4`** direct-Demucs diagnostic using the existing 211.44s exact-anchor fixture.
2. Modal resource request may be `cpu=4.0`, but Torch intra/inter-op/MKL/OMP must remain exactly **1**; concurrency exists only across Demucs' already-defined split chunks.
3. Require exact normalized/Guitar/PCM/shift parity against the CPU anchor; mismatch fails closed.
4. Bound collection to ~360s with remote cancellation and `always()` isolated-app cleanup; retain aggregate timing/hashes only.
5. If exact parity passes with material speedup, run one second independent exact repeatability call before any Production change.
6. If it fails exact parity or speed, close split-parallel promotion and move to exact source-hash stage caching architecture.
7. Production/bridge/Vercel/UI remain unchanged; reference-facing accuracy remains unarmed.
