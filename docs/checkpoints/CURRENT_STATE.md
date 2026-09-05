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
- No production bridge/worker/Vercel/UI change or `main` merge until the exact-cache promotion gates below are satisfied.

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

Isolated branch-local implementation is structurally proven:

- primitive `analyzer/v143_exact_stage_cache.py`;
- synthetic probe `analyzer/v143_exact_stage_cache_probe.py`;
- workflow `.github/workflows/v143-exact-stage-cache-structural.yml`;
- commits `54e8af3f429c5129418e2f8e5ff8fa860b43349c`, `8c9bee773d81c66bd700d83f450b53c16c4d7ff4`, `351d430b601c83578d385aa162dc971b04d1b310`;
- CI run `33936373413`, job `101224995003`, conclusion **SUCCESS**;
- artifact `9960303358`, digest `e6ff4e789edf959d59b2299f9fe916ea6ea21ff83a395bd738f86bb1441468f2`.

Proven without audio/model execution: empty miss, deterministic key, exact compute on miss, best-effort populate, hit skips compute, fingerprint mismatch misses, corruption rejects/falls back to exact compute, invalid compute bytes are not hidden, cleanup succeeds.

Fingerprint is fail-closed and includes normalized-source SHA, separator/model identity, weights SHA, Demucs parameters, shift policy, sample rate/channels, Torch/OMP/MKL controls, oneDNN state, and code-policy version. The helper has **no production default cache root** and does **not** authorize stem retention.

## Real-audio exact-cache diagnostic — IMPLEMENTED / RUNNING

Implementation is isolated on this branch and does not edit production code:

- `analyzer/v143_exact_stage_cache_real_audio_modal.py` — commit `9c1abfb30ef074c22a086d3852fbccab3791a0a6`;
- `.github/scripts/v143_exact_stage_cache_real_audio_collect.py` — commit `1c49adb34085f56a2bf8da9c3667ed7add94d22f`;
- `.github/workflows/v143-exact-stage-cache-real-audio.yml` — commit `1ce79b41507e8c7db43059e5f2826ffad62b1b09`.

Current Actions execution:

- run `33938289895`;
- job `101230445238`;
- state at this checkpoint: **IN PROGRESS**, inside the single cold-miss exact CPU separation after checkout/boundary/Python/Modal/deploy steps all passed.

Diagnostic behavior:

- accepts only repository-owned `public/gomywayfullaitest.m4a` with the frozen source SHA;
- normalizes and asserts the frozen normalized SHA before cache lookup;
- reuses the unchanged exact path `separate_demucs_guitar(seeded_audio_separator_cli(), normalized, ...)` under frozen `DEMUCS_SINGLE_THREAD_ENV`;
- prefetches the exact Demucs model through the same seeded CLI with `--download_model_only`, then hashes the actual `5c90dfd2-34c22ccb.th` weight bytes and `htdemucs_6s.yaml` config bytes before constructing the full cache fingerprint;
- uses only an ephemeral `TemporaryDirectory` cache root;
- cold miss must invoke the real separator exactly once and assert frozen source/normalized/shift/Guitar/PCM/runtime invariants before population;
- immediate warm hit must return the exact stored WAV, reproduce frozen Guitar/PCM hashes, and leave separator compute count at `1`;
- fingerprint mismatch is tested as a miss without executing a second expensive separation;
- intentional cache corruption must be rejected and must reach the exact-compute fallback boundary; a sentinel callback proves fallback without running a second separation;
- cleanup must remove the temporary cache/audio/stem bytes;
- no reference-facing scoring, no quality verdict, no production changes.

The previously open `separator_weights_sha256` implementation detail is **RESOLVED**: the fingerprint hashes the actual downloaded model bytes, not a placeholder or filename-only identity.

## Production source mapping — SOURCE BOUNDARY RESOLVED

The earlier statement that the live bridge source was absent was caused by default-branch code search. On `v143-contextual-prune-lobo`, the source is present and source-proven:

- `analyzer/v143_modal_http_endpoint.py` defines `modal.App("dadrock-v143-http-bridge")` and dispatches rhythm requests to Modal app `dadrock-v143-ai-tab-live`, function `rhythm_v143_request`;
- `analyzer/v143_modal_live_endpoint.py` defines `modal.App("dadrock-v143-ai-tab-live")`; `rhythm_v143_request(...)` invokes `v143_rhythm_stem_provider.rhythm_v143_stem_provider(...)` before `analyze_v143_audio(...)`;
- `analyzer/v143_rhythm_stem_provider.py` calls `build_shadow_deterministic_stems(...)`;
- `analyzer/v143_rhythm_deterministic_stem_provider.py` calls `build_deterministic_v143_stems(...)`;
- `analyzer/v143_deterministic_separator.py` delegates to `build_seeded_v143_stems(...)`;
- `analyzer/v143_seeded_separator.py` is therefore the source-proven separator stage seam used by the live rhythm worker.

`app/api/analyze-audio-tab/route.js` remains only the Vercel forwarding/anti-leakage contract and is **not** the separator cache insertion point.

Do not guess about deployment identity beyond the source-proven names/call graph; production remains untouched until all promotion gates are satisfied.

## Retention boundary — STILL BLOCKING PERSISTENT STEM CACHE

The source-proven live request path uses request-scoped temporary storage:

- `analyzer/v143_vercel_audio_request_adapter.py` creates `TemporaryDirectory(prefix="dadrock-v143-http-request-")`, downloads the request audio there, runs the stem/analyzer builder inside that root, then removes it at request completion.
- The isolated real-audio cache diagnostic likewise uses only temporary storage and deletes it at the end.

No explicit `/ai-tab` policy/config/code path has yet been identified that authorizes deterministic separated Guitar/cascade stems to persist across requests. Existing retention behavior elsewhere in the product must not be treated as authorization for this path.

Therefore, even if the real-audio miss/hit gate turns GREEN, **persistent production stem caching remains `BLOCKED_BY_RETENTION_POLICY`** unless an explicit allowed boundary is found. A non-audio derived-feature/result cache may be investigated as the safer alternative if no stem-retention permission exists.

## User authorization / intent

- User has authorized continued non-reference-facing V143 performance/cache work and use of repository-owned Gomyway audio.
- User explicitly asked to continue the wiring work and to save this checkpoint often on `v143-contextual-prune-lobo`.
- That authorization does not relax frozen anti-leakage, exact-parity, sealed-asset, or privacy/retention gates.

## NEXT STEPS

1. Finish Actions run `33938289895`; record run/job/function-call/artifact IDs, actual model/config hashes, miss/hit timing/speedup, exact hashes, compute count, cleanup, and final verdict here.
2. If the run fails, change only the isolated diagnostic needed to repair the demonstrated issue; keep production untouched and rerun the same gate.
3. If GREEN, mark the **direct exact-Demucs stage-cache gate** proven. Do not overclaim full V143 separator-bundle caching: the live rhythm path also needs the RoFormer/cascade branch.
4. Preserve `BLOCKED_BY_RETENTION_POLICY` for any cross-request persistent stem cache unless explicit `/ai-tab` retention authorization is source-proven.
5. Map the smallest production-safe cache seam in `build_seeded_v143_stems(...)` and determine whether a non-audio derived-result cache can capture useful savings without retaining separated audio.
6. Before any production wiring, require exact identity/fail-closed semantics for every stage actually cached, acceptable cleanup/retention, source-proven call graph, and unchanged routing/anti-leakage behavior.
7. Do not merge to `main` merely to test. Keep diagnostic/cache work on `v143-contextual-prune-lobo` until the promotion gate is satisfied.

### Hard stops

- No reference-facing scoring or quality verdict.
- No GOAT restricted bytes.
- No sealed GuitarSet `00/01/03` access.
- No SplitMySong reopening.
- No GPU rerun.
- No split-parallel rerun.
- No weakening exact parity or fail-closed criteria.
- No persistent user-audio/stem retention without an explicit allowed retention boundary.
- No production bridge/worker/Vercel/UI changes or `main` merge until the promotion gate passes.
