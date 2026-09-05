# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-04 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet prospective `00/01/03` sealed.
- Current quality verdict: **NO QUALITY VERDICT — PERFORMANCE/IDENTITY DIAGNOSTICS ONLY**.
- GPU promotion CLOSED; do not rerun GPU or weaken exact parity.
- Native split-parallel CPU promotion CLOSED; do not rerun or promote its faster non-identical hash.
- No production bridge/worker/Vercel/UI change or `main` merge until the exact cache promotion gates below are satisfied.

## Production — unchanged

- `main`: **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`**.
- deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, READY.
- bridge `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`.
- routing proven `usingV143RhythmAnalyzer=true`; Deployment Protection preserved.
- Production worker/bridge/Vercel unchanged by diagnostics/cache work.

## Frozen exact CPU anchor — GREEN

Repository-owned fixture `public/gomywayfullaitest.m4a`:

- source SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`;
- normalized SHA `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- Guitar SHA `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`;
- PCM-int16 SHA `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`;
- shift trace `0,22050,6026`;
- run `33914759546`, job `101159244192`, call `fc-01M1Q0MFR88FXWAQ1R47TSX77Z`;
- client wall **666.404s**; oneDNN off; Torch intra/inter-op = 1; exact parity GREEN;
- artifact `9953064061`; cleanup GREEN.

## Closed performance branches

### GPU — TERMINAL / CLOSED

- run `33916705535`, job `101165425904`, call `fc-01M1Q1ZA6GFSF1NZTPFF2GQA9P`;
- separation **42.404s**, client wall **51.663s**, **12.899x** faster;
- runtime invariants passed but exact CPU parity failed;
- Guitar SHA `5820375b67d6d3ad38386c267f8e21b721a06446ba9d8b4de14260d832d2f5a4`;
- PCM SHA `376c33be95e277f811f1edc2bea14a4d6287f4ad7ae4e8eca2c5c84134b9341b`;
- artifact `9953451993`; cleanup GREEN.

### Native split-parallel CPU — TERMINAL / CLOSED

- wrapper `analyzer/v143_demucs_split_parallel_cli.py`;
- probe `analyzer/v143_demucs_split_parallel_probe.py`;
- collector `.github/scripts/v143_demucs_split_parallel_collect.py`;
- workflow `.github/workflows/v143-demucs-split-parallel.yml`;
- run `33917237702`, job `101167122276`, call `fc-01M1Q2AZTBAM6NC7WVQQVAF1YR`;
- separation **149.928s**, client wall **158.720s**, **4.199x** faster;
- runtime invariants passed but exact CPU parity failed;
- Guitar SHA `52a781bcab05335636c5bfb99168b8c01a9d627c34f1a59acf00f01512a41630`;
- PCM SHA `1f5665f8deceda3b13a9e8a4ac4b561a548530a7bf671f605998139cfc133c2e`;
- artifact `9953701945`; isolated cleanup GREEN; `productionAppTouched=false`.

## Exact stage-cache structural gate — GREEN

Isolated branch-local implementation is now present and structurally proven:

- primitive `analyzer/v143_exact_stage_cache.py`;
- synthetic probe `analyzer/v143_exact_stage_cache_probe.py`;
- workflow `.github/workflows/v143-exact-stage-cache-structural.yml`;
- commits:
  - `54e8af3f429c5129418e2f8e5ff8fa860b43349c` — isolated exact cache primitive;
  - `8c9bee773d81c66bd700d83f450b53c16c4d7ff4` — miss/hit fallback semantics;
  - `351d430b601c83578d385aa162dc971b04d1b310` — structural tests;
- CI run `33936373413`, job `101224995003`, conclusion **SUCCESS**;
- artifact `9960303358`, `v143-exact-stage-cache-structural`, digest `e6ff4e789edf959d59b2299f9fe916ea6ea21ff83a395bd738f86bb1441468f2`.

Proven without audio/model execution:

- empty miss;
- deterministic content-addressed key;
- exact compute on miss;
- best-effort populate;
- cache hit returns exact stored bytes and skips compute;
- any fingerprint mismatch changes key and misses;
- corruption is rejected and falls back to exact compute;
- invalid compute bytes are not hidden;
- cleanup succeeds.

Fingerprint is fail-closed and includes normalized-source SHA, separator/model identity, weights SHA, Demucs parameters, shift policy, sample rate/channels, Torch/OMP/MKL controls, oneDNN state, and code-policy version.

The helper deliberately has **no production default cache root** and does **not** authorize stem retention.

## Source-of-truth wiring boundary

- `app/api/analyze-audio-tab/route.js` only forwards requests to the selected analyzer and enforces the V143 anti-leakage response contract. It does not own normalized audio identity or separator bytes, so it is **not** the cache insertion point.
- Exact repository search for the known live bridge name `dadrock-v143-http-bridge` produced zero checked-in code matches.
- The checked-in repository therefore still lacks a source-proven implementation corresponding to the live production bridge insertion point.
- Do not fabricate a production insertion point or persist user stems merely because the structural gate is GREEN.

## User authorization / intent

- User has authorized continued non-reference-facing V143 performance/cache work and use of repository-owned Gomyway audio.
- User explicitly said to **complete the wiring** and then asked to save the next steps here for a fresh chat.
- That authorization does not relax the frozen anti-leakage, exact-parity, sealed-asset, or privacy/retention gates.

## Fresh-chat handoff — NEXT STEPS

Start by reading this file on `v143-contextual-prune-lobo`. The branch tip immediately before this handoff save was **`62282c807eb4c1bdee606205cc06700c9bcff754`** (`docs: checkpoint V143 exact cache structural gate`). Verify the new handoff commit is now the branch tip before making further edits.

1. **Build the isolated real-audio cache diagnostic.** Reuse `analyzer/v143_exact_stage_cache.py`; do not change production code. Wire an isolated diagnostic wrapper to the existing exact CPU separator path only.
2. **Use only `public/gomywayfullaitest.m4a`.** First execution must be a true cache miss and run the unchanged exact CPU path. Assert source SHA, normalized SHA, shift trace, Guitar SHA, and PCM SHA all match the frozen GREEN anchor above before accepting/populating the entry.
3. **Immediately exercise the cache-hit path.** Re-run with the identical full fingerprint and prove the separator compute callback is not invoked. Assert returned Guitar/PCM bytes hash exactly to the same frozen GREEN values.
4. **Exercise fail-closed invalidation without extra expensive variants where possible.** Change one fingerprint field and prove it misses. Corrupt a cached artifact and prove corruption is rejected. These checks must fall through safely; never accept ambiguous/stale bytes.
5. **Keep diagnostic retention ephemeral.** Use a temporary/isolated cache root and delete it at the end of the run. This real-audio gate does not authorize persistent user stem retention.
6. **Record performance/identity only.** Capture miss wall time, hit wall time, hit speedup, exact hashes, cache key/fingerprint summary, whether separator compute was invoked, and cleanup result. Make no quality/accuracy claims and perform no reference-facing comparison.
7. **Checkpoint immediately after the diagnostic implementation commit and again after the run.** Save workflow/run/job/artifact IDs, hashes, timing, cleanup, and verdict into this file.
8. **In parallel with repository inspection, finish source mapping for production wiring.** Search checked-in workflows/scripts/history for Modal app construction/deploy commands and the live worker invocation. If the actual bridge/worker source remains absent, explicitly retain `BLOCKED_BY_SOURCE_BOUNDARY`; do not guess.
9. **Resolve retention before persistent production caching.** Locate an explicit existing policy/config/code path that permits storage of deterministic separated stems. If no clear permission exists, do not persist stems; investigate a downstream non-audio derived-feature/result cache that still preserves exact semantics.
10. **Production promotion gate.** Only consider production bridge/worker wiring after: (a) real-audio miss and hit are byte-identical to the exact CPU anchor, (b) mismatch/corruption fail closed, (c) cleanup/retention is acceptable, (d) the true bridge/worker insertion point is source-proven, and (e) routing/anti-leakage semantics remain unchanged. Otherwise keep the cache isolated and document the blocker.
11. **Do not merge to `main` merely to test.** Keep all diagnostic/cache wiring on `v143-contextual-prune-lobo` until the promotion gate is satisfied.

### Hard stops for the fresh chat

- No reference-facing scoring or quality verdict.
- No GOAT restricted bytes.
- No sealed GuitarSet `00/01/03` access.
- No SplitMySong reopening.
- No GPU rerun.
- No split-parallel rerun.
- No weakening exact parity or fail-closed criteria.
- No persistent user-audio/stem retention without an explicit allowed retention boundary.
- No fabricated production bridge insertion point.
- No production bridge/worker/Vercel/UI changes or `main` merge until the promotion gate passes.
