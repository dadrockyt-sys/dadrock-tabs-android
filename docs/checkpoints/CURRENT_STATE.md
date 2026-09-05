# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-04 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet prospective `00/01/03` sealed.
- Current quality verdict: **NO QUALITY VERDICT — PERFORMANCE/IDENTITY DIAGNOSTICS ONLY**.
- GPU promotion CLOSED; do not rerun GPU Demucs or weaken exact parity.
- Native intra-Demucs split-parallel CPU promotion CLOSED; do not rerun or promote its faster non-identical hash.
- No persistent user-audio/stem/result retention without an explicit allowed retention boundary.
- No production bridge/worker/Vercel/UI change or `main` merge until the promotion gates are satisfied.

## Production — unchanged

- `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`.
- deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, READY.
- bridge `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`.
- routing proven `usingV143RhythmAnalyzer=true`; Deployment Protection preserved.
- Production worker/bridge/Vercel unchanged by cache/concurrency diagnostics.

## Exact direct anchor — GREEN / frozen

Repository-owned `public/gomywayfullaitest.m4a`:

- source SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`;
- normalized SHA `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- direct Guitar WAV SHA `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`;
- direct PCM-int16 SHA `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`;
- shift trace `0,22050,6026`;
- exact anchor run `33914759546`, job `101159244192`, call `fc-01M1Q0MFR88FXWAQ1R47TSX77Z`, artifact `9953064061`;
- oneDNN off; Torch intra/inter-op = 1; exact parity GREEN.

## Direct exact stage-cache — GREEN / CLOSED

- structural run `33936373413`, job `101224995003`, artifact `9960303358`;
- real-audio run `33938289895`, job `101230445238`, call `fc-01M1QN9N9M6NGRTJTFA2DQ3ZA2`, artifact `9961088259`;
- cold miss `649.970s`; warm hit `0.118718s`; isolated hit speedup `5474.898x`;
- separator compute calls `1`; corruption fallback calls `1`;
- model weight SHA `34c22ccb381c6f9fdbf324f04e1e2fe21aaaf293f5ded163a162697ff9a02ddd`;
- Demucs config SHA `207405151270af8fd81c2373c25d27950916682ac91dca7884a11ce13dad6f58`;
- miss/hit WAV + PCM exactly match frozen direct anchor; mismatch/corruption fail closed; cleanup GREEN; production untouched.

**Do not rerun absent demonstrated regression or changed fingerprint/runtime policy.**

## Cascade identity + exact stage-cache — GREEN / CLOSED

Authenticated current-regime cascade anchors:

- BS-RoFormer Instrumental WAV SHA `ce7ae8c6c57e00e1e191b8c15a8c4f39627cbcdf3b7a75ac7ca4c246f6f64b14`;
- BS-RoFormer Instrumental PCM SHA `16e0a16a54ab1b007d15647d293900ecfbfabceccfa886f004a86162d4a454dd`;
- cascade Guitar WAV SHA `546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41`;
- cascade Guitar PCM SHA `75c0feefb416d8438641ceebe903253f935bd19c550e97e9ef0a90426e7727ba`;
- cascade Demucs shift trace `0,22050,6026`.

Terminal cache evidence:

- run `33939561555` SUCCESS; job `101234177608` SUCCESS; call `fc-01M1QPTKH7K3VAZH9RSGRBY0Q0`;
- artifact `9961570152`, ZIP SHA `775e6443b85358fcdd4dfcf8cba65cc4108e10fcae01f1bed5defd63b6241125`;
- cold miss `838.734s`; warm hit `0.127996s`; isolated hit speedup `6552.829x`;
- RoFormer `90.044s`; cascade exact CPU Demucs `748.029s`;
- compute calls: RoFormer `1`, cascade Demucs `1`, direct Demucs `0`, corruption fallback `1`;
- BS-RoFormer weight SHA `5b84f37e8d444c8cb30c79d77f613a41c05868ff9c9ac6c7049c00aefae115aa`, bytes `639331213`;
- miss/hit exact anchors GREEN; mismatch/corruption fail closed; cleanup GREEN; raw/stem retention false; production untouched.

Verdict: **direct + cascade exact cache semantics are proven GREEN only for isolated ephemeral diagnostics.** Persistent production caching is not authorized.

**Do not rerun absent demonstrated regression or changed fingerprint/runtime policy.**

## Production source mapping — RESOLVED

- `v143_modal_http_endpoint.py` → live `dadrock-v143-ai-tab-live/rhythm_v143_request`.
- `v143_modal_live_endpoint.py` calls one `process_vercel_audio_request(...)` using `build_deterministic_rhythm_stem_bundle`.
- `v143_rhythm_stem_provider.py` builds the paired direct/cascade bundle once; downstream router/technique code reuses it.
- deterministic path reaches `v143_seeded_separator.py`, the source-proven separator seam.
- `app/api/analyze-audio-tab/route.js` is forwarding/anti-leakage only, not the separator optimization seam.

## Retention boundary — `BLOCKED_BY_RETENTION_POLICY`

- Live request adapter uses request-scoped `TemporaryDirectory(...)` and removes source/stems after each request.
- No explicit `/ai-tab` policy/config/code authorizes separated stems or generated results to persist across requests.
- Backing Track Studio retention rules do not authorize AI-tab.
- The live Rhythm bundle is built once per request, so a request-scoped stage cache would not remove duplicate separator work.

Therefore no persistent stem/result cache may be wired into production without an explicit allowed persistence boundary.

## Zero-retention view-level concurrency diagnostic — GREEN / CLOSED

Purpose: overlap independent frozen **views**, not chunks inside Demucs. This is separate from the CLOSED native split-parallel branch and leaves each Demucs invocation mathematically unchanged.

Implementation:

- `analyzer/v143_view_level_demucs_child.py` — commit `b1700b47cb01e34ac04399293255c0f1d68438c0`, blob `7ffdf5183360f18ef2e356a12d1112d3f651ccbf`;
- `analyzer/v143_view_level_concurrency_modal.py` — current blob `ef14db309500c262d59a50bfaaec4d8ffa9b570a` after cleanup hardening commit `9909cfe76f321658b5286de2954662c2e532fe15`;
- `.github/scripts/v143_view_level_concurrency_collect.py` — commit `9664c618d4e4e40687126b4f76241fef6ba8f4cc`, blob `d3bcaeec638a3fc078515c0139390b2a4947e53c`;
- `.github/workflows/v143-view-level-concurrency.yml` — commit/head `161aec43026fe0ec6634a72685b5f51c4664ec8b`.

Terminal evidence:

- Actions run `33940555992`: **SUCCESS**;
- job `101237009458`: **SUCCESS**;
- all workflow steps GREEN, including exact real-audio gate, artifact preservation, isolated-app shutdown, and post-job cleanup;
- Modal call `fc-01M1QR3EFJWQB655HFBAJHFMMR`;
- artifact `9961880403`;
- artifact ZIP digest `sha256:60b4b7e208e84c9bc3d8cffd38b53613bc2b3a88fb81f236563142723939eb67`;
- collector wall `815.325s`.

Exact identities — all GREEN:

- source SHA `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`;
- normalized WAV SHA `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- RoFormer WAV SHA `ce7ae8c6c57e00e1e191b8c15a8c4f39627cbcdf3b7a75ac7ca4c246f6f64b14`;
- RoFormer PCM SHA `16e0a16a54ab1b007d15647d293900ecfbfabceccfa886f004a86162d4a454dd`;
- direct Guitar WAV SHA `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`;
- direct Guitar PCM SHA `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`;
- cascade Guitar WAV SHA `546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41`;
- cascade Guitar PCM SHA `75c0feefb416d8438641ceebe903253f935bd19c550e97e9ef0a90426e7727ba`;
- direct shift trace `0,22050,6026`;
- cascade shift trace `0,22050,6026`;
- exact parity gate `true`.

Model/runtime identity — GREEN:

- RoFormer weight SHA `5b84f37e8d444c8cb30c79d77f613a41c05868ff9c9ac6c7049c00aefae115aa`, bytes `639331213`;
- Demucs weight SHA `34c22ccb381c6f9fdbf324f04e1e2fe21aaaf293f5ded163a162697ff9a02ddd`, bytes `54996327`;
- Demucs config SHA `207405151270af8fd81c2373c25d27950916682ac91dca7884a11ce13dad6f58`, bytes `21`;
- parent runtime Torch `2.13.0+cu130`, CUDA `13.0`, NVIDIA L4, capability `8.9`;
- Demucs device CPU; one thread per child; multiprocessing start method `spawn`;
- probe hard-asserted both child runtime traces before success: `mkldnnEnabled=false`, `torchNumThreads=1`, `torchNumInteropThreads=1`, CPU capability `DEFAULT`, `V143_DEMUCS_DISABLE_MKLDNN=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`.

Scheduling/performance:

- direct starts before RoFormer: `true`;
- cascade starts after RoFormer: `true`;
- intra-Demucs parallelism: `false`;
- unchanged exact Demucs invocation: `true`;
- cross-request persistence: `false`;
- RoFormer elapsed `79.660s`, wall `79.661s`;
- direct Demucs elapsed `717.756s`, process wall `718.353s`;
- cascade Demucs elapsed `692.879s`, process wall `693.460s`;
- concurrent separation wall `773.381s`;
- sum of same-run stage elapsed values `1490.295s`;
- historical sequential stage sum `1487.706s`;
- contextual speedup `1.924x`;
- **`1.924x` is explicitly cross-run/contextual only, not a same-run paired benchmark.**

Safety/cleanup — GREEN:

- `allPassed=true`;
- scheduling boundary `true`; safety boundary `true`;
- reference-free `true`; reference-facing accuracy scored `false`; reference score calls `0`; quality verdict made `false`;
- raw audio retained `false`; stem bytes retained `false`;
- probe `TemporaryDirectory` cleanup passed;
- isolated diagnostic app stop completed; production app touched `false`;
- GPU Demucs requested `false`; GPU performance comparison performed `false`;
- production worker changed `false`; production bridge changed `false`; Vercel changed `false`; main merge performed `false`.

Verdict: **view-level concurrency is proven exact and materially useful as an isolated zero-retention performance candidate.** The diagnostic itself is CLOSED; do not rerun absent demonstrated regression/fingerprint/runtime-policy change.

## NEXT STEPS

1. Source-map the smallest production-safe **scheduler-only** change that can overlap direct exact Demucs with RoFormer/cascade preparation while preserving the proven unchanged Demucs invocations.
2. Do not modify/deploy production merely to test; first pin the exact production seam and prove that no downstream lifetime/cleanup assumptions are changed.
3. Persistent cache remains independently `BLOCKED_BY_RETENTION_POLICY`; concurrency success does not authorize persistence.
4. Any implementation candidate must preserve the exact runtime assertions and request-scoped cleanup semantics proven above.
5. No reference-facing scoring or quality verdict is armed.

### Hard stops

- No reference-facing scoring or quality verdict.
- No GOAT restricted bytes.
- No sealed GuitarSet `00/01/03` access.
- No SplitMySong reopening.
- No GPU Demucs performance rerun.
- No intra-Demucs split-parallel rerun.
- No direct/cascade cache rerun absent regression/fingerprint change.
- No view-level concurrency diagnostic rerun absent regression/fingerprint/runtime-policy change.
- No weakening exact parity/fail-closed criteria.
- No persistent user-audio/stem/result retention without explicit permission.
- No production bridge/worker/Vercel/UI change or `main` merge until promotion gates pass.
