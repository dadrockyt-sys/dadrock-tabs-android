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
- No persistent user-audio/stem retention without an explicit allowed retention boundary.
- No production bridge/worker/Vercel/UI change or `main` merge until the cache promotion gates are satisfied.

## Production — unchanged

- `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`.
- deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, READY.
- bridge `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`.
- routing proven `usingV143RhythmAnalyzer=true`; Deployment Protection preserved.
- Production worker/bridge/Vercel unchanged by cache diagnostics.

## Frozen exact CPU direct anchor — GREEN

Repository-owned `public/gomywayfullaitest.m4a`:

- source SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`;
- normalized SHA `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- direct Guitar SHA `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`;
- direct PCM-int16 SHA `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`;
- shift trace `0,22050,6026`;
- exact anchor run `33914759546`, job `101159244192`, call `fc-01M1Q0MFR88FXWAQ1R47TSX77Z`, artifact `9953064061`;
- oneDNN off; Torch intra/inter-op = 1; exact parity GREEN.

## Direct exact stage-cache — GREEN / CLOSED

Structural gate:

- `analyzer/v143_exact_stage_cache.py`;
- `analyzer/v143_exact_stage_cache_probe.py`;
- `.github/workflows/v143-exact-stage-cache-structural.yml`;
- run `33936373413`, job `101224995003`, artifact `9960303358`;
- exact miss/populate, hit-skips-compute, fingerprint mismatch, corruption fallback, invalid output, cleanup all GREEN.

Real-audio gate implementation:

- `analyzer/v143_exact_stage_cache_real_audio_modal.py` — `9c1abfb30ef074c22a086d3852fbccab3791a0a6`;
- `.github/scripts/v143_exact_stage_cache_real_audio_collect.py` — `1c49adb34085f56a2bf8da9c3667ed7add94d22f`;
- `.github/workflows/v143-exact-stage-cache-real-audio.yml` — `1ce79b41507e8c7db43059e5f2826ffad62b1b09`.

Terminal evidence:

- run `33938289895` SUCCESS; job `101230445238` SUCCESS;
- Modal call `fc-01M1QN9N9M6NGRTJTFA2DQ3ZA2`;
- collector wall `665.688s`; separator `649.633s`; cold miss `649.970s`; warm hit `0.118718s`; measured isolated speedup `5474.898x`;
- separator compute calls `1`; corruption sentinel fallback calls `1`;
- cache key `b9b66d2b4e193681e31f5ee6a924f09f6377ce73b24c663d1c7e492c9d6e559b`;
- miss + hit direct Guitar and PCM hashes exactly match frozen anchor;
- model weights `5c90dfd2-34c22ccb.th`, SHA `34c22ccb381c6f9fdbf324f04e1e2fe21aaaf293f5ded163a162697ff9a02ddd`, bytes `54996327`;
- config `htdemucs_6s.yaml`, SHA `207405151270af8fd81c2373c25d27950916682ac91dca7884a11ce13dad6f58`, bytes `21`;
- artifact `9961088259`, ZIP SHA `5f6d40aaf7a4850b1f6c1bc172c0793306d369aaad37f17456b46a5aa5d8d3b3`;
- cleanup GREEN; no raw/stem retention; reference score calls `0`; no quality verdict; production untouched.

**Do not rerun this direct cache gate without a demonstrated regression or changed fingerprint policy.**

## Full two-view separator identity — authenticated current-regime evidence found

Live Rhythm uses both:

1. direct Demucs6s Guitar;
2. BS-RoFormer Instrumental → Demucs6s Guitar cascade.

Historical August Section-3 L4 evidence (`9cc3ca2cf9cdb02a0fa82e1f4fba56bc729e7484`, later cross-container record `066fa791bcad0217663d853e06bd792ffd28d8cc`) is useful provenance but **not** the current anchor: it produced direct file SHA `afd1037bc7d62572ac9b99644d13d95b8593e25b4f442aa4a8f85c1111d97c78` and cascade `44e0fe8874b07bcd4bca7e28f4a512b61214061f6bbf8771426c1b1237ffa201` on L4 workers, so those bytes must not be mixed with the later exact CPU regime.

The current oneDNN-off direct regime was established by commit `34471c7cdd061dbbc5ed807ba473bb2e156bc5f8`, which records the same direct anchor now frozen above.

Crucially, later cold exact proof `debug/v143-contextual-prune/repaired-timing-precision-cold-exact-proof.json`, recorded by commit `dd1b32a9ba250cbf1520d01411a298c865e88e6d`, contains **two independent passes** with:

- source SHA exactly `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`;
- normalized SHA exactly `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- direct Guitar SHA exactly `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c` on both passes;
- **cascade Guitar SHA `546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41` on both passes**;
- `firstStageHashMismatch=null`, `invariantFailures=[]`, `passed=true`;
- protected pipeline unchanged; production not modified.

Therefore the cascade **WAV/file identity** is authenticated for the same direct execution regime as the frozen current anchor. This avoids inventing a new cascade baseline.

## Cascade exact stage-cache — IMPLEMENTED / RUNNING

Isolated cascade-only implementation now exists:

- `analyzer/v143_exact_cascade_cache_real_audio_modal.py` — commit `15cb4d019a66b4da3ccc37814e07b854567d3df2`, blob `9ceda1afa6824529a1e58ffbdbd11cdd808d30ee`;
- `.github/scripts/v143_exact_cascade_cache_real_audio_collect.py` — commit `e591bc43b8957db3dc727ce3b62ed132f0f68c4a`, blob `2fd68ab2c1087039ebf1f51efb460ed7f2b78633`;
- `.github/workflows/v143-exact-cascade-cache-real-audio.yml` — commit `e1d31e3e397aeefdebf8fc9c407242602f450de2`.

Current Actions execution:

- run `33939561555`;
- job `101234177608`;
- state at this checkpoint: **IN PROGRESS**.

Scope/safety:

- only repository-owned Gomyway input;
- cascade-only compute: BS-RoFormer Instrumental → exact CPU Demucs Guitar;
- direct Demucs compute count is required to stay `0`; the closed direct cache gate is not rerun;
- RoFormer runs on the CUDA-capable L4 path because that is the source-proven live cascade path; this is identity/cache validation, **not** a GPU performance comparison;
- actual BS-RoFormer model bytes are prefetched through the same CLI and SHA-256 fingerprinted before cache lookup;
- Demucs weight/config hashes are pinned to the already-authenticated exact direct regime;
- authenticated current-regime cascade WAV SHA required: `546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41`;
- the run will additionally capture RoFormer intermediate WAV/PCM identity and cascade PCM-int16 identity;
- cold miss must execute RoFormer once and cascade Demucs once, then populate only after exact cascade WAV/runtime/shift invariants pass;
- immediate warm hit must skip both expensive compute stages and reproduce exact cascade WAV/PCM bytes;
- mismatch/corruption are fail-closed without a second expensive cascade execution;
- cache/audio/stems are confined to `TemporaryDirectory` and must be deleted at run end;
- no reference-facing score, no quality verdict, no production changes, no persistent retention.

Do not promote or generalize the cascade cache until this run is terminal GREEN with inspectable aggregate evidence.

## Production source mapping — RESOLVED

On this branch:

- `v143_modal_http_endpoint.py` → live app `dadrock-v143-ai-tab-live/rhythm_v143_request`;
- `v143_modal_live_endpoint.py` → `v143_rhythm_stem_provider.rhythm_v143_stem_provider(...)`;
- `v143_rhythm_stem_provider.py` → `build_shadow_deterministic_stems(...)`;
- `v143_rhythm_deterministic_stem_provider.py` → `build_deterministic_v143_stems(...)`;
- `v143_deterministic_separator.py` → `build_seeded_v143_stems(...)`;
- `v143_seeded_separator.py` is the source-proven separator seam.

`app/api/analyze-audio-tab/route.js` remains forwarding/anti-leakage only, not the cache insertion point.

## Retention boundary — STILL BLOCKING PERSISTENT CACHE

- `v143_vercel_audio_request_adapter.py` uses request-scoped `TemporaryDirectory(...)` and removes source/stems after each request.
- No explicit `/ai-tab` policy/config/code authorizes separated stems to persist across requests.
- Existing Backing Track Studio retention rules do not authorize AI-tab.
- A deterministic non-audio result seam exists after analysis, but no explicit cross-request `/ai-tab` result-persistence authorization has been found either.

Therefore persistent production stem caching remains **`BLOCKED_BY_RETENTION_POLICY`**. Derived-result caching is design-only unless an explicit allowed persistence boundary is found.

## User authorization / intent

- User authorizes continued non-reference-facing V143 performance/cache work and repository-owned Gomyway audio.
- User asked to save `docs/checkpoints/CURRENT_STATE.md` often on this branch.
- Authorization does not relax exact-parity, anti-leakage, sealed-asset, reference, or retention gates.

## NEXT STEPS

1. Finish cascade Actions run `33939561555`; inspect/download the aggregate artifact and record actual RoFormer weight hash, intermediate WAV/PCM hashes, cascade WAV/PCM hashes, cache key, timings, compute counts, cleanup, run/job/call/artifact IDs, and verdict here.
2. If the cascade run fails, fix only the demonstrated isolated diagnostic issue; do not rerun the closed direct gate and do not change production.
3. If cascade GREEN, treat direct + cascade exact stage cache semantics as proven **only in ephemeral diagnostics**. Persistent production caching remains blocked by retention policy.
4. Then determine whether an explicitly non-persistent/request-scoped reuse mechanism provides useful savings, or whether explicit product/privacy authorization is needed before any cross-request cache design can proceed.
5. No production bridge/worker/Vercel/UI changes or `main` merge merely to test.

### Hard stops

- No reference-facing scoring or quality verdict.
- No GOAT restricted bytes.
- No sealed GuitarSet `00/01/03` access.
- No SplitMySong reopening.
- No GPU performance rerun.
- No split-parallel rerun.
- No direct cache rerun absent regression/fingerprint change.
- No weakening exact parity/fail-closed criteria.
- No persistent user-audio/stem retention without explicit permission.
- No production change or `main` merge until promotion gates pass.
