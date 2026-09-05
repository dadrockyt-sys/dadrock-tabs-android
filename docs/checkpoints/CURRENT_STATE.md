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

## Direct real-audio exact-Demucs stage-cache gate — GREEN

Isolated implementation, production-disconnected:

- `analyzer/v143_exact_stage_cache_real_audio_modal.py` — commit `9c1abfb30ef074c22a086d3852fbccab3791a0a6`;
- `.github/scripts/v143_exact_stage_cache_real_audio_collect.py` — commit `1c49adb34085f56a2bf8da9c3667ed7add94d22f`;
- `.github/workflows/v143-exact-stage-cache-real-audio.yml` — commit `1ce79b41507e8c7db43059e5f2826ffad62b1b09`.

Terminal evidence:

- Actions run `33938289895` — **SUCCESS**;
- job `101230445238` — **SUCCESS**;
- Modal function call `fc-01M1QN9N9M6NGRTJTFA2DQ3ZA2`;
- collector wall **665.688s**;
- exact separator elapsed **649.633s**;
- cold miss/compute/populate wall **649.970s**;
- immediate warm hit wall **0.118718s**;
- measured miss→hit speedup **5474.898x** for this isolated stage-cache resolution;
- separator compute calls **1** total across miss + immediate hit;
- corruption sentinel fallback calls **1**;
- cache key `b9b66d2b4e193681e31f5ee6a924f09f6377ce73b24c663d1c7e492c9d6e559b`;
- artifact `9961088259`, `v143-exact-stage-cache-real-audio`;
- artifact ZIP SHA256 `5f6d40aaf7a4850b1f6c1bc172c0793306d369aaad37f17456b46a5aa5d8d3b3`;
- isolated Modal app cleanup step SUCCESS; `productionAppTouched=false`.

Exact identities on miss **and** hit:

- source SHA `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`;
- normalized SHA `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- direct Guitar SHA `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`;
- direct PCM-int16 SHA `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`;
- warm-hit Guitar SHA `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`;
- warm-hit PCM-int16 SHA `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`;
- shift trace `0,22050,6026`;
- direct bytes `37298220`; sample rate `44100`; frames `9324544`; channels `2`.

Actual model identity used in fingerprint:

- weights `5c90dfd2-34c22ccb.th`;
- weights SHA256 `34c22ccb381c6f9fdbf324f04e1e2fe21aaaf293f5ded163a162697ff9a02ddd`;
- weights bytes `54996327`;
- config `htdemucs_6s.yaml`;
- config SHA256 `207405151270af8fd81c2373c25d27950916682ac91dca7884a11ce13dad6f58`;
- config bytes `21`;
- code policy `v143-exact-cpu-policy-1;python=3.11.12;audio-separator=0.44.5;torch=2.13.0;numpy=2.4.6;soundfile=0.14.0;code=03e4f07486952d2a3e6c6a9e342fac8eb683ae3580b2f2181406c50b14cff026`.

All gate fields passed:

- `initialMissPassed=true`;
- `missPopulatePassed=true`;
- `warmHitPassed=true`;
- `fingerprintMismatchMissPassed=true`;
- `fingerprintMismatchChangesKeyPassed=true`;
- `corruptionLookupRejectedPassed=true`;
- `corruptionFallbackReachedPassed=true`;
- `cleanupPassed=true`;
- `exactAnchorParityPassed=true`;
- `cacheSemanticsPassed=true`;
- `safetyBoundaryPassed=true`;
- `allPassed=true`.

Safety remained frozen: `referenceFacingAccuracyScored=false`, `referenceScoreCalls=0`, `qualityVerdictMade=false`, `rawAudioRetained=false`, `stemBytesRetained=false`, production worker/bridge/Vercel unchanged, no `main` merge.

**Verdict:** the direct exact-Demucs stage cache is structurally and real-audio proven. This does **not** prove or authorize full V143 paired-stem bundle caching or production persistence.

## Production source mapping — SOURCE BOUNDARY RESOLVED

The earlier statement that the live bridge source was absent was caused by default-branch code search. On `v143-contextual-prune-lobo`, the source is present and source-proven:

- `analyzer/v143_modal_http_endpoint.py` defines `modal.App("dadrock-v143-http-bridge")` and dispatches rhythm requests to Modal app `dadrock-v143-ai-tab-live`, function `rhythm_v143_request`;
- `analyzer/v143_modal_live_endpoint.py` defines `modal.App("dadrock-v143-ai-tab-live")`; `rhythm_v143_request(...)` invokes `v143_rhythm_stem_provider.rhythm_v143_stem_provider(...)` before `analyze_v143_audio(...)`;
- `analyzer/v143_rhythm_stem_provider.py` calls `build_shadow_deterministic_stems(...)`;
- `analyzer/v143_rhythm_deterministic_stem_provider.py` calls `build_deterministic_v143_stems(...)`;
- `analyzer/v143_deterministic_separator.py` delegates to `build_seeded_v143_stems(...)`;
- `analyzer/v143_seeded_separator.py` is therefore the source-proven separator stage seam used by the live rhythm worker.

`app/api/analyze-audio-tab/route.js` remains only the Vercel forwarding/anti-leakage contract and is **not** the separator cache insertion point.

`docs/checkpoints/AI_TAB_END_TO_END_CONSTRUCTION.md` confirms Rhythm separation is a **deterministic two-view guitar separation** and that the product flow uses private upload. The live pair is direct Demucs Guitar plus BS-RoFormer Instrumental → Demucs Guitar cascade; both carriers are part of the current Rhythm contract.

Historical `V143_CODESPACE_MODAL_PROVENANCE.md` confirms both carrier filenames were preserved/restored for diagnostic reproducibility, but the fetched record does not supply authenticated full-pair WAV hashes suitable for inventing a new frozen cascade anchor. Do not manufacture one.

## Retention boundary — STILL BLOCKING PERSISTENT STEM CACHE

The source-proven live request path uses request-scoped temporary storage:

- `analyzer/v143_vercel_audio_request_adapter.py` creates `TemporaryDirectory(prefix="dadrock-v143-http-request-")`, downloads the request audio there, runs the stem/analyzer builder inside that root, then removes it at request completion.
- The direct exact-cache real-audio diagnostic likewise used only temporary storage and deleted it at the end.

No explicit `/ai-tab` policy/config/code path has been identified that authorizes deterministic separated Guitar/cascade stems to persist across requests. Existing retention behavior in another product (including Backing Track Studio) is not authorization for this path.

Therefore **persistent production stem caching remains `BLOCKED_BY_RETENTION_POLICY`** despite the GREEN direct cache gate.

A derived non-audio seam is technically available after the expensive stem/analyzer pipeline: the V143 result is deterministic JSON-like analysis (`generatedTab`, events, tempo/tempoMap, techniques, counts, assembly, optional routing), and the live worker adds request metadata. Prior V147 evidence also used derived artifacts without retaining raw/normalized audio. Those facts are design precedents only; no explicit cross-request `/ai-tab` derived-result persistence authorization has yet been found, so no persistent result cache is authorized either.

## User authorization / intent

- User has authorized continued non-reference-facing V143 performance/cache work and use of repository-owned Gomyway audio.
- User explicitly asked to continue the wiring work and to save this checkpoint often on `v143-contextual-prune-lobo`.
- That authorization does not relax frozen anti-leakage, exact-parity, sealed-asset, or privacy/retention gates.

## NEXT STEPS

1. Treat the **direct exact-Demucs stage-cache gate as GREEN / CLOSED**. Do not rerun it absent a demonstrated regression or changed fingerprint policy.
2. Do not overclaim full V143 separator-bundle caching: the live Rhythm path also requires the BS-RoFormer Instrumental → Demucs Guitar cascade carrier.
3. Before any full-bundle cache claim, establish an authenticated reference-free identity baseline for the RoFormer instrumental and cascade Guitar on repository-owned Gomyway audio, including actual model/weights/settings/runtime fingerprints and exact output hashes. Do not infer or invent cascade hashes from old cache metadata.
4. Prefer an isolated **ephemeral full-bundle identity/cache diagnostic** if further performance proof is needed; keep all audio/stems temporary and remove them at run end.
5. Preserve `BLOCKED_BY_RETENTION_POLICY` for any cross-request persistent audio/stem cache unless explicit `/ai-tab` retention authorization is source-proven.
6. Separately investigate whether an explicit allowed persistence boundary exists for deterministic non-audio derived analysis results. If none exists, keep derived-result caching design-only as well.
7. Production wiring requires exact identity/fail-closed semantics for every cached stage, acceptable retention, source-proven call graph, and unchanged routing/anti-leakage behavior.
8. Do not merge to `main` merely to test. Keep diagnostic/cache work on `v143-contextual-prune-lobo` until the promotion gate is satisfied.

### Hard stops

- No reference-facing scoring or quality verdict.
- No GOAT restricted bytes.
- No sealed GuitarSet `00/01/03` access.
- No SplitMySong reopening.
- No GPU rerun.
- No split-parallel rerun.
- No direct cache rerun without a demonstrated regression/fingerprint change.
- No weakening exact parity or fail-closed criteria.
- No persistent user-audio/stem retention without an explicit allowed retention boundary.
- No production bridge/worker/Vercel/UI changes or `main` merge until the promotion gate passes.
