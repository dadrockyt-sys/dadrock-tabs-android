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
- No production bridge/worker/Vercel/UI change or `main` merge until the cache/promotion gates are satisfied.

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

## Full two-view separator identity — authenticated current-regime evidence

Live Rhythm uses both:

1. direct Demucs6s Guitar;
2. BS-RoFormer Instrumental → Demucs6s Guitar cascade.

Historical August Section-3 L4 evidence (`9cc3ca2cf9cdb02a0fa82e1f4fba56bc729e7484`, later cross-container record `066fa791bcad0217663d853e06bd792ffd28d8cc`) is useful provenance but **not** the current anchor: it produced direct file SHA `afd1037bc7d62572ac9b99644d13d95b8593e25b4f442aa4a8f85c1111d97c78` and cascade `44e0fe8874b07bcd4bca7e28f4a512b61214061f6bbf8771426c1b1237ffa201` on L4 workers, so those bytes must not be mixed with the later exact CPU regime.

The current oneDNN-off direct regime was established by commit `34471c7cdd061dbbc5ed807ba473bb2e156bc5f8`, which records the same direct anchor now frozen above.

Cold exact proof `debug/v143-contextual-prune/repaired-timing-precision-cold-exact-proof.json`, recorded by commit `dd1b32a9ba250cbf1520d01411a298c865e88e6d`, contains two independent passes with:

- source SHA exactly `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`;
- normalized SHA exactly `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- direct Guitar SHA exactly `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c` on both passes;
- cascade Guitar SHA `546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41` on both passes;
- `firstStageHashMismatch=null`, `invariantFailures=[]`, `passed=true`;
- protected pipeline unchanged; production not modified.

Therefore the cascade WAV/file identity is authenticated for the same direct execution regime as the frozen current anchor.

## Cascade exact stage-cache — GREEN / CLOSED

Isolated cascade-only implementation:

- `analyzer/v143_exact_cascade_cache_real_audio_modal.py` — commit `15cb4d019a66b4da3ccc37814e07b854567d3df2`, blob `9ceda1afa6824529a1e58ffbdbd11cdd808d30ee`;
- `.github/scripts/v143_exact_cascade_cache_real_audio_collect.py` — commit `e591bc43b8957db3dc727ce3b62ed132f0f68c4a`, blob `2fd68ab2c1087039ebf1f51efb460ed7f2b78633`;
- `.github/workflows/v143-exact-cascade-cache-real-audio.yml` — commit `e1d31e3e397aeefdebf8fc9c407242602f450de2`.

Terminal evidence:

- run `33939561555` SUCCESS; job `101234177608` SUCCESS;
- Modal call `fc-01M1QPTKH7K3VAZH9RSGRBY0Q0`;
- collector wall `898.489s`;
- cold cascade-cache miss `838.734s`; warm hit `0.127996s`; measured isolated speedup `6552.829x`;
- RoFormer stage `90.044s`; cascade exact CPU Demucs stage `748.029s`;
- cache key `bf717808944bde35aed5b6094ba91520af8c3a8dc1bdda31d2db9c563495415d`;
- compute calls: composite `1`, RoFormer `1`, cascade Demucs `1`, **direct Demucs `0`**, corruption sentinel fallback `1`;
- BS-RoFormer model `model_bs_roformer_ep_317_sdr_12.9755.ckpt`, SHA `5b84f37e8d444c8cb30c79d77f613a41c05868ff9c9ac6c7049c00aefae115aa`, bytes `639331213`;
- Demucs weight/config identities exactly match the frozen direct regime;
- RoFormer Instrumental WAV SHA `ce7ae8c6c57e00e1e191b8c15a8c4f39627cbcdf3b7a75ac7ca4c246f6f64b14`;
- RoFormer Instrumental PCM-int16 SHA `16e0a16a54ab1b007d15647d293900ecfbfabceccfa886f004a86162d4a454dd`;
- cascade Guitar WAV SHA `546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41` on miss and hit;
- cascade Guitar PCM-int16 SHA `75c0feefb416d8438641ceebe903253f935bd19c550e97e9ef0a90426e7727ba` on miss and hit;
- RoFormer/cascade WAVs are 44.1 kHz, 2 channels, `9,324,544` frames, `37,298,220` bytes each;
- cascade Demucs shift trace exactly `0,22050,6026`;
- L4 RoFormer runtime: Torch `2.13.0+cu130`, CUDA `13.0`, device `NVIDIA L4`, compute capability `8.9`;
- miss/populate GREEN; warm hit skips both expensive cascade stages; fingerprint mismatch changes key/misses; corruption rejected and exact-compute fallback boundary reached;
- artifact `9961570152`, ZIP SHA `775e6443b85358fcdd4dfcf8cba65cc4108e10fcae01f1bed5defd63b6241125`;
- cleanup GREEN; `rawAudioRetained=false`; `stemBytesRetained=false`; reference score calls `0`; no quality verdict; no GPU performance comparison; production untouched; no `main` merge.

Verdict: **direct + cascade exact stage-cache semantics are proven GREEN for repository-owned real audio in isolated ephemeral diagnostics.** This does **not** authorize persistent production caching.

**Do not rerun the cascade cache gate without a demonstrated regression or changed fingerprint/runtime policy.**

## Production source mapping — RESOLVED

On this branch:

- `v143_modal_http_endpoint.py` → live app `dadrock-v143-ai-tab-live/rhythm_v143_request`;
- `v143_modal_live_endpoint.py` → one `process_vercel_audio_request(...)` call using `build_deterministic_rhythm_stem_bundle`;
- `v143_rhythm_stem_provider.py` builds the paired direct/cascade bundle once and downstream routing/technique enrichment reuses those paths;
- `v143_rhythm_deterministic_stem_provider.py` → deterministic separator;
- `v143_deterministic_separator.py` → `build_seeded_v143_stems(...)`;
- `v143_seeded_separator.py` is the source-proven separator seam.

`app/api/analyze-audio-tab/route.js` remains forwarding/anti-leakage only, not the cache insertion point.

## Retention boundary — STILL BLOCKING PERSISTENT CACHE

- `v143_vercel_audio_request_adapter.py` uses request-scoped `TemporaryDirectory(...)` and removes source/stems after each request.
- No explicit `/ai-tab` policy/config/code authorizes separated stems to persist across requests.
- Existing Backing Track Studio retention rules do not authorize AI-tab.
- A deterministic non-audio result seam exists after analysis, but no explicit cross-request `/ai-tab` result-persistence authorization has been found either.
- The live Rhythm call graph builds the paired stem bundle only once per request and reuses it downstream, so a request-scoped stage cache would not remove a duplicate expensive separator call.

Therefore persistent production stem caching remains **`BLOCKED_BY_RETENTION_POLICY`**. Derived-result caching is design-only unless an explicit allowed persistence boundary is found.

## Zero-retention performance direction — view-level concurrency candidate

Source/evidence now supports investigating a separate **isolated** performance diagnostic that overlaps the two already-frozen view computations without retaining data across requests:

- historical current-regime sequential evidence shows direct Demucs and cascade Demucs dominate wall time;
- direct and cascade are independent final views once the RoFormer Instrumental exists;
- safe candidate schedule: normalize → RoFormer Instrumental → run unchanged direct Demucs and unchanged cascade Demucs concurrently in **separate processes**, each retaining its existing deterministic child/runtime controls;
- do **not** parallelize Demucs chunks or alter Demucs math/order; that closed native split-parallel branch produced a non-identical hash;
- do **not** use concurrent threads that mutate the shared parent environment via `_temporary_environment`; independent processes are required for isolated environment state;
- exact direct/cascade WAV + PCM anchors above remain mandatory; any mismatch closes the candidate;
- this would remain request-scoped/ephemeral and therefore does not require persistent stem caching.

This is a diagnostic candidate only. No production concurrency wiring has been made.

## User authorization / intent

- User authorizes continued non-reference-facing V143 performance/cache work and repository-owned Gomyway audio.
- User asked to save `docs/checkpoints/CURRENT_STATE.md` often on this branch.
- Authorization does not relax exact-parity, anti-leakage, sealed-asset, reference, or retention gates.

## NEXT STEPS

1. Keep direct and cascade exact cache gates CLOSED/GREEN; do not rerun absent a demonstrated regression or changed fingerprint/runtime policy.
2. Persistent cross-request stem/result caching stays `BLOCKED_BY_RETENTION_POLICY`; do not wire it into production without an explicit allowed persistence boundary.
3. Build an **isolated view-level concurrency diagnostic** only: same repository-owned Gomyway input, same normalized SHA, unchanged RoFormer + unchanged exact direct/cascade Demucs invocations, independent process environments, ephemeral request-scoped files only.
4. Require exact direct Guitar WAV/PCM, cascade Guitar WAV/PCM, cascade shift trace, and RoFormer intermediate identity to match the now-frozen anchors. Record sequential-vs-concurrent wall only as performance/identity evidence; make no quality claim.
5. If view concurrency is byte-exact and materially faster, source-map the smallest production-safe scheduler change and checkpoint it; still do not merge/deploy merely to test.
6. If concurrency changes either view hash/runtime invariant or provides no useful wall improvement, close it and retain current production behavior.

### Hard stops

- No reference-facing scoring or quality verdict.
- No GOAT restricted bytes.
- No sealed GuitarSet `00/01/03` access.
- No SplitMySong reopening.
- No GPU Demucs performance rerun.
- No intra-Demucs split-parallel rerun.
- No direct/cascade cache rerun absent regression/fingerprint change.
- No weakening exact parity/fail-closed criteria.
- No persistent user-audio/stem/result retention without explicit permission.
- No production bridge/worker/Vercel/UI change or `main` merge until promotion gates pass.
