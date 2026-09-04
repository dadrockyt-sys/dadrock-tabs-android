# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-04 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet prospective `00/01/03` sealed.
- Current quality verdict: **NO QUALITY VERDICT — PERFORMANCE/IDENTITY DIAGNOSTICS ONLY**.

## Production — unchanged

- `main`: **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`**;
- deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, READY;
- bridge `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`;
- routing proven `usingV143RhythmAnalyzer=true`; Deployment Protection preserved;
- Production worker/bridge/Vercel unchanged by diagnostics.

## Exact CPU anchor — GREEN

Approved fixture `public/gomywayfullaitest.m4a` SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.

- normalized SHA `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- Guitar SHA `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`;
- PCM-int16 SHA `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`;
- shift `0,22050,6026`;
- fresh run `33914759546`, job `101159244192`, call `fc-01M1Q0MFR88FXWAQ1R47TSX77Z`;
- exact parity GREEN; client wall **666.404s**; oneDNN off; Torch intra/inter-op = 1;
- artifact `9953064061`; cleanup GREEN.

## GPU — TERMINAL / CLOSED

Current-controls L4 run `33916705535`, job `101165425904`, call `fc-01M1Q1ZA6GFSF1NZTPFF2GQA9P`:

- separation **42.404s**, client wall **51.663s**, **12.899x** faster;
- source/normalized/dimensions/private shift exact;
- Guitar SHA `5820375b67d6d3ad38386c267f8e21b721a06446ba9d8b4de14260d832d2f5a4`;
- PCM SHA `376c33be95e277f811f1edc2bea14a4d6287f4ad7ae4e8eca2c5c84134b9341b`;
- `runtimeInvariantsPassed=true`, **`exactCpuParityPassed=false`**;
- artifact `9953451993`; cleanup GREEN.

**GPU PROMOTION CLOSED. Do not rerun GPU or weaken exact parity.**

## Native exact split-parallel opportunity

Read-only inspection of exact dependency `python-audio-separator v0.44.5` established:

- architecture `demucs_separator.py` calls bundled `apply_model` without `num_workers`, defaulting to 0;
- bundled `apply_model(..., num_workers=0, pool=None)` natively creates `ThreadPoolExecutor(num_workers)` for CPU;
- existing Demucs chunks are submitted concurrently;
- futures are consumed in original offset order and weighted overlap-add/reduction occurs in that same original order;
- recursive chunk calls use `split=False`; model/settings/chunk boundaries/weights/reduction formula remain unchanged.

This is chunk-level concurrency, **not** the closed intra-op thread-count experiment.

## Split-parallel diagnostic — ARMED / RUNNING

Diagnostic-only implementation; Production code not changed:

- child wrapper `analyzer/v143_demucs_split_parallel_cli.py`, commit `1761f4dfc7231e285ac1b1678feab4b08f478579`;
- probe `analyzer/v143_demucs_split_parallel_probe.py`, commit `89f6cb26181dfb324c1467e9e3e058074588e8d0`;
- collector `.github/scripts/v143_demucs_split_parallel_collect.py`, commit `5d6219a0b00945e663cc0393159ca83e03331109`;
- workflow `.github/workflows/v143-demucs-split-parallel.yml`, trigger commit `6f58507c33a0973c80df2d1afe41ddfb582fcc4a`;
- run **`33917237702`**, job **`101167122276`** currently starting checkout/preflight.

Gate contract:

- Modal `cpu=4.0`, no GPU, memory 16GB;
- **Torch intra/inter-op = 1, OMP=1, MKL=1**;
- only Demucs split executor `num_workers=4`;
- existing model/seed/shifts/overlap/segment/private RNG/oneDNN-off path unchanged;
- exact source/normalized/Guitar/PCM/shift parity mandatory;
- minimum material speedup **1.5x** vs 666.404s anchor;
- client deadline 360s; terminate remote container on timeout/failure;
- aggregate-only evidence; raw audio/stems not retained;
- `always()` cleanup targets only `dadrock-v143-demucs-split-parallel-probe`.

## Authorization / next action

User authorized non-reference-facing V143 performance work and repository-owned Gomyway audio. No authorization for reference-facing scoring, GOAT, sealed GuitarSet, SplitMySong reopening, or weakened fail-closed criteria.

1. Read terminal result/artifact for run `33917237702` and confirm cleanup.
2. If exact parity + >=1.5x speedup pass, run one additional independent split-parallel call for exact repeatability before Production consideration.
3. If parity/speed fails, close split-parallel promotion and inspect exact source-hash stage caching architecture.
4. Production/bridge/Vercel/UI remain unchanged until an exact structural gate passes.
