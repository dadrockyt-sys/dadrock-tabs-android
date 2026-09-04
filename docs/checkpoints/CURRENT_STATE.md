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
- CPU thread-count tuning path is **CLOSED / DO NOT REOPEN**.

Frozen Production Demucs execution remains CPU-only, one-thread, oneDNN-disabled/conservative ISA, `htdemucs_6s`, Guitar, shifts=1, overlap=.10, segment=6, seed=143.

## Exact deterministic CPU identity — GREEN

Historical/fresh exact anchor:

- normalized WAV SHA256 `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- direct Guitar SHA256 `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`;
- decoded PCM-int16 SHA256 `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`;
- shift trace `0,22050,6026`;
- fixture duration 211.44s; historical separation ~623s.

Fresh reproduction:

- run **`33914759546`**, job **`101159244192`**, SUCCESS;
- function call `fc-01M1Q0MFR88FXWAQ1R47TSX77Z`;
- Modal `cpu=1.0`, no GPU; client wall **666.404s**;
- exact source/normalized/Guitar/PCM/shift parity = GREEN;
- PyTorch `2.13.0+cu130`, oneDNN disabled, intra/inter-op = 1;
- artifact `9953064061`;
- cleanup GREEN; Production untouched; reference calls 0.

This is the fail-closed reference-free output identity anchor.

## Historical CUDA evidence — FAIL-CLOSED

- strict three-L4 cross-container result commit `626263e890d44099b1877286f38e594268f9b140`: direct PCM not exact across workers;
- later startup-determinism cold proof result `faa12c1031fd740842e2c30c3e36ea6dc56246f3`: source/normalized/BS-RoFormer exact, direct Demucs split between two hashes; `allSeparatorHashesExact=false`.

## Final current-controls L4 exact-parity gate — TERMINAL / FAIL-CLOSED

Files:

- `analyzer/v143_demucs_gpu_exact_probe.py` initial commit `56fbba4ee1794b8232a1b5ca42a18f430381e1bb`;
- explicit private-shift correction commit `383c34c71eebb48b2b7f9597cdeb34aa61269ddd`;
- collector `.github/scripts/v143_demucs_gpu_exact_collect.py` commit `7556688eb94de1ef66f0bf76ff489ad9ca0ebb61`;
- workflow retry trigger commit `9c6b8a47bb1742b46d2d6e41b0426359c3ee5123`.

Retry result:

- run **`33916705535`**, job **`101165425904`**;
- preflight/setup/deploy: GREEN;
- function call **`fc-01M1Q1ZA6GFSF1NZTPFF2GQA9P`**;
- device: **NVIDIA L4**; PyTorch `2.13.0+cu130`;
- completed normally well inside 300s deadline;
- client wall **51.663s**;
- direct Demucs separation **42.404s** (`42.405s` measured wall);
- total remote **43.158s**;
- speedup vs exact CPU anchor: **12.899x**;
- source SHA exact;
- normalized WAV SHA exact;
- private deterministic shift trace exact: `0,22050,6026`;
- output dimensions exact: 44.1kHz, 9,324,544 frames, 2 channels, 37,298,220 bytes;
- GPU direct Guitar SHA256 **`5820375b67d6d3ad38386c267f8e21b721a06446ba9d8b4de14260d832d2f5a4`**;
- GPU decoded PCM-int16 SHA256 **`376c33be95e277f811f1edc2bea14a4d6287f4ad7ae4e8eca2c5c84134b9341b`**;
- exact CPU Guitar anchor is `0ac47da6...0189c`; exact CPU PCM anchor is `2c22f040...36bed`;
- `runtimeInvariantsPassed=true`;
- **`exactCpuParityPassed=false`**;
- artifact **`9953451993`** uploaded successfully;
- isolated app cleanup GREEN; `productionAppTouched=false`;
- reference-facing score calls 0; raw audio/stem retention false; Production/Vercel unchanged.

### Decisive interpretation

GPU solves the speed bottleneck but changes the frozen exact Demucs output identity. Under the current fail-closed exact-output contract, **GPU PROMOTION IS CLOSED / DO NOT RETEST OR WEAKEN PARITY TO FORCE A PASS**. No second L4 repeatability run is warranted because the first current-controls candidate already fails the required CPU identity.

The next acceleration direction must preserve the exact CPU numerical path while changing execution architecture, not model/settings/numerical backend. The most promising untested class is exact parallelization of Demucs' existing internal split/chunk workload with deterministic ordered reduction, if repository/upstream implementation evidence confirms that can be done without changing output math/order.

## Authorization

User explicitly authorized continuation of non-reference-facing V143 Production/performance work, including repository-owned Gomyway audio, isolated Modal diagnostics, narrowly scoped worker/bridge fixes/deploys, and aggregate-only Product/PDF checks. This does **not** authorize reference-facing scoring, GOAT access, sealed GuitarSet access, SplitMySong reopening, or weakening fail-closed boundaries.

## NEXT SAFE ACTION

1. **Do not run more GPU or CPU-thread-count probes.**
2. Perform read-only source/history inspection of Demucs/audio-separator split execution to determine whether its 40-chunk CPU work can be parallelized while preserving exact per-chunk math and the original deterministic overlap-add/reduction order.
3. If structurally feasible, build a reference-free diagnostic implementation/gate first; require exact CPU Guitar + PCM hash parity before considering performance.
4. If exact split-parallel execution is not feasible, record that terminally and move to another architecture that preserves exact CPU output (for example reusable source-hash stage caching), without changing musical/numerical settings.
5. Production/bridge/Vercel/UI remain unchanged until an exact deterministic structural gate passes.
6. Reference-facing accuracy remains unarmed.
