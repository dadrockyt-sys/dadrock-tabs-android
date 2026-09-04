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

## Native split-parallel CPU — TERMINAL / CLOSED

Diagnostic-only implementation used exact dependency-native Demucs chunk-level `num_workers=4` concurrency while keeping Torch intra/inter-op, OMP and MKL at 1.

- wrapper `analyzer/v143_demucs_split_parallel_cli.py`;
- probe `analyzer/v143_demucs_split_parallel_probe.py`;
- collector `.github/scripts/v143_demucs_split_parallel_collect.py`;
- workflow `.github/workflows/v143-demucs-split-parallel.yml`;
- run **`33917237702`**, job **`101167122276`**, call **`fc-01M1Q2AZTBAM6NC7WVQQVAF1YR`**;
- Modal `cpu=4.0`, no GPU, memory 16GB;
- Torch intra/inter-op = 1; OMP=1; MKL=1; oneDNN disabled; private shift RNG exact;
- source SHA exact; normalized SHA exact; shift trace exact `0,22050,6026`;
- separation **149.928s**; client wall **158.720s**;
- speedup vs exact CPU anchor **4.199x**; material-speed gate PASS;
- runtime invariants PASS;
- Guitar SHA **`52a781bcab05335636c5bfb99168b8c01a9d627c34f1a59acf00f01512a41630`**;
- PCM SHA **`1f5665f8deceda3b13a9e8a4ac4b561a548530a7bf671f605998139cfc133c2e`**;
- **exact CPU parity FAIL**;
- artifact **`9953701945`** uploaded; isolated-app cleanup GREEN; `productionAppTouched=false`.

### Interpretation

The dependency-native split executor is materially faster, but concurrent CPU model execution changes the exact numerical output even though ordered overlap-add/reduction, chunk geometry, frozen model/settings, shift trace, single-threaded kernels and oneDNN-off controls were preserved.

Therefore **split-parallel promotion is CLOSED**. Do not rerun it, weaken exact parity, or promote the faster hash.

## Authorization / next action

User authorized non-reference-facing V143 performance work and repository-owned Gomyway audio. No authorization for reference-facing scoring, GOAT, sealed GuitarSet, SplitMySong reopening, or weakened fail-closed criteria.

1. Inspect current V143 request flow and storage for an **exact source-hash stage cache** architecture that can reuse previously computed exact deterministic separator outputs without changing their bytes.
2. Prefer caching normalized input identity and exact deterministic separator-stage artifacts/derived aggregate outputs keyed by source SHA + frozen execution-policy/version hashes; fail closed on any key mismatch.
3. Do not retain raw user audio beyond existing policy; determine whether exact deterministic stem cache is acceptable under current retention/privacy boundaries before implementing it. If stem retention is not acceptable, inspect downstream feature/cache boundaries that preserve exact behavior without stem persistence.
4. No new Demucs/GPU/split-parallel compute should start until cache architecture is understood.
5. Production/bridge/Vercel/UI remain unchanged until a reference-free exact structural gate passes.
6. Reference-facing accuracy remains unarmed.

## In-progress cache architecture inspection — 2026-09-04

- Resumed on `v143-contextual-prune-lobo` from this checkpoint.
- Re-read the frozen boundaries; authorized work remains cache architecture inspection/design only.
- Inspected `app/api/analyze-audio-tab/route.js`. The app-side API route forwards analysis requests to the remote live V143 analyzer bridge, so a reusable-byte cache should be placed at the analyzer/bridge stage where stable normalized audio identity and deterministic separator outputs are available, not in any reference-facing path.
- Branch-local analyzer/bridge source is being traced before any cache implementation.
- No Demucs/GPU/split-parallel runs, reference-facing scoring, analyzer semantic changes, production bridge changes, Vercel changes, or UI changes were made in this pass.
