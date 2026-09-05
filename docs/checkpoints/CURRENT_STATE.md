# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-04 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet prospective `00/01/03` sealed.
- Current quality verdict: **NO QUALITY VERDICT — PERFORMANCE/IDENTITY DIAGNOSTICS ONLY**.
- GPU Demucs promotion CLOSED; native intra-Demucs split-parallel CPU promotion CLOSED.
- Do not rerun either CLOSED Demucs lane or weaken exact parity.
- No persistent user-audio/stem/result retention without an explicit allowed retention boundary.
- No production bridge/worker/Vercel/UI change or `main` merge until promotion gates are satisfied.

## Production — unchanged

- Vercel/web `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e` (`checkpoint: record V143 main merge`).
- integration merge in that lineage: `ceeccfbbb17968c097bb56136487e7ddeaf1a5a4`.
- deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, READY.
- bridge `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`.
- routing proven `usingV143RhythmAnalyzer=true`; Deployment Protection preserved.
- Production worker/bridge/Vercel unchanged by cache/concurrency diagnostics.

### Source-provenance distinction

The Vercel/web `main` SHA and the independently deployed Modal worker source are separate provenance anchors. Fetching the V143 Modal module paths at `main@bb992...` does not resolve them; the live Modal source modules are retained on `v143-contextual-prune-lobo` and were deployed independently. Do **not** use `bb992...` as the Modal worker source fingerprint.

Current branch source blobs for the live Modal/separator chain:

- `analyzer/v143_modal_http_endpoint.py` blob `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`;
- `analyzer/v143_modal_live_endpoint.py` blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`;
- `analyzer/v143_vercel_audio_request_adapter.py` blob `6d1787f34a3b7ca781ced8e5695993a3777406a8`;
- `analyzer/v143_rhythm_deterministic_stem_provider.py` blob `3c6dcf9b8e7360ba1dd886810f3c14c05ac0579b`;
- `analyzer/v143_rhythm_stem_provider.py` blob `cd180bfb35e8110f031504035af5f11e502c3dc6`;
- `analyzer/v143_deterministic_separator.py` blob `28b3e6fe0eb761178b142cf7dcbda533f0bf918d`;
- `analyzer/v143_seeded_separator.py` blob `250534e516cad36e49cae35b6eab2b88654be2d3`;
- `analyzer/v143_seeded_audio_separator_cli.py` blob `645f324c207d67b32c6d279657805ff8f25c3aa0`;
- `analyzer/v143_production_separator.py` blob `05ae1978fa02f8c84ccc1e44547fc4e4cea9798b`.

## Exact direct anchor — GREEN / frozen

Repository-owned `public/gomywayfullaitest.m4a`:

- source SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`;
- normalized SHA `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- direct Guitar WAV SHA `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`;
- direct PCM-int16 SHA `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`;
- shift trace `0,22050,6026`;
- anchor run `33914759546`, job `101159244192`, call `fc-01M1Q0MFR88FXWAQ1R47TSX77Z`, artifact `9953064061`;
- oneDNN off; Torch intra/inter-op = 1.

## Exact stage-cache diagnostics — GREEN / CLOSED

Direct:
- run `33938289895`, job `101230445238`, call `fc-01M1QN9N9M6NGRTJTFA2DQ3ZA2`, artifact `9961088259`;
- separator `649.633s`; cold miss `649.970s`; warm hit `0.118718s`; isolated speedup `5474.898x`;
- exact parity/mismatch/corruption/cleanup GREEN.

Cascade:
- RoFormer WAV `ce7ae8c6c57e00e1e191b8c15a8c4f39627cbcdf3b7a75ac7ca4c246f6f64b14`;
- RoFormer PCM `16e0a16a54ab1b007d15647d293900ecfbfabceccfa886f004a86162d4a454dd`;
- cascade Guitar WAV `546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41`;
- cascade Guitar PCM `75c0feefb416d8438641ceebe903253f935bd19c550e97e9ef0a90426e7727ba`;
- shift trace `0,22050,6026`;
- run `33939561555`, job `101234177608`, call `fc-01M1QPTKH7K3VAZH9RSGRBY0Q0`, artifact `9961570152`;
- cold miss `838.734s`; warm hit `0.127996s`; isolated speedup `6552.829x`;
- RoFormer `90.044s`; cascade Demucs `748.029s`;
- exact parity/mismatch/corruption/cleanup GREEN.

Persistent production cache remains **`BLOCKED_BY_RETENTION_POLICY`**.

## Zero-retention view-level concurrency — GREEN / CLOSED

Implementation:

- `analyzer/v143_view_level_demucs_child.py`: commit `b1700b47cb01e34ac04399293255c0f1d68438c0`, blob `7ffdf5183360f18ef2e356a12d1112d3f651ccbf`;
- `analyzer/v143_view_level_concurrency_modal.py`: blob `ef14db309500c262d59a50bfaaec4d8ffa9b570a`;
- collector commit `9664c618d4e4e40687126b4f76241fef6ba8f4cc`, blob `d3bcaeec638a3fc078515c0139390b2a4947e53c`;
- workflow head `161aec43026fe0ec6634a72685b5f51c4664ec8b`.

Terminal evidence:

- Actions run `33940555992`: **SUCCESS**;
- job `101237009458`: **SUCCESS**;
- Modal call `fc-01M1QR3EFJWQB655HFBAJHFMMR`;
- artifact `9961880403`;
- artifact digest `sha256:60b4b7e208e84c9bc3d8cffd38b53613bc2b3a88fb81f236563142723939eb67`;
- collector wall `815.325s`;
- `allPassed=true`.

Exact identity — all GREEN:

- normalized SHA `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- RoFormer WAV/PCM exactly match `ce7ae...` / `16e0...` anchors;
- direct WAV/PCM exactly match `0ac47...` / `2c22...` anchors;
- cascade WAV/PCM exactly match `546e...` / `75c0...` anchors;
- both shift traces exactly `0,22050,6026`.

Runtime/safety — all GREEN:

- multiprocessing start method `spawn`;
- direct Demucs and cascade Demucs remain unchanged exact invocations;
- no intra-Demucs parallelism;
- both child traces hard-asserted `mkldnnEnabled=false`, Torch threads `1/1`, CPU capability `DEFAULT`, and exact MKL/OMP deterministic env;
- reference score calls `0`; quality verdict made `false`;
- raw audio retained `false`; stem bytes retained `false`; cleanup passed;
- production app/worker/bridge/Vercel/main untouched.

Performance:

- RoFormer `79.660s`;
- direct Demucs `717.756s` (process wall `718.353s`);
- cascade Demucs `692.879s` (process wall `693.460s`);
- concurrent separation wall `773.381s`;
- same-run summed stage elapsed `1490.295s`;
- historical sequential stage sum `1487.706s`;
- contextual speedup `1.924x`;
- **`1.924x` is cross-run/contextual only; no same-run paired sequential benchmark was performed.**

Verdict: **view-level concurrency is proven exact and materially useful as an isolated zero-retention performance candidate.** Do not rerun absent demonstrated regression/fingerprint/runtime-policy change.

## Scheduler source map — RESOLVED

Current serialized call chain:

`v143_modal_http_endpoint.py` → `dadrock-v143-ai-tab-live/rhythm_v143_request` → `process_vercel_audio_request(...)` → `build_deterministic_rhythm_stem_bundle(...)` → `build_rhythm_stem_bundle(...)` → `build_deterministic_v143_stems(...)` → `build_seeded_v143_stems(...)`.

The exact scheduler seam is `build_seeded_v143_stems()` in blob `250534e...`. It currently performs:

1. separator-level normalization;
2. direct exact Demucs;
3. BS-RoFormer Instrumental;
4. cascade exact Demucs;
5. copies frozen outputs to the existing output names;
6. returns the existing direct/cascade result contract.

The smallest safe candidate is therefore **scheduler-only inside the seeded separator boundary**:

1. preserve the existing normalization and exact model CLI helpers unchanged;
2. after normalized input exists, start direct exact Demucs in an isolated spawned CPU child;
3. run unchanged RoFormer in the current L4 parent;
4. after RoFormer exists, start cascade exact Demucs in an isolated spawned CPU child;
5. join both children before copying outputs or returning;
6. on any exception, terminate/join both children before propagating failure;
7. preserve all output filenames, return keys, deterministic settings, model parameters, and downstream bundle contract.

Why no cleanup/lifetime change is required:

- `process_vercel_audio_request()` owns `TemporaryDirectory(prefix="dadrock-v143-")` around normalization, routing, stem generation, downstream enrichment, and result construction;
- `build_rhythm_stem_bundle()` deliberately writes `v143-rhythm-stems` beside the normalized request file so stem paths remain alive for the whole router call;
- therefore children can safely use those paths **only if they are joined/terminated before the separator returns**;
- no cross-request files, persistent volumes, cache, or retention authorization is needed.

Do **not** move concurrency into the Vercel adapter, router, bundle provider, or technique enrichers. The exact seam is the seeded separator scheduler.

## NEXT STEPS

1. Build a branch-only scheduler implementation candidate at the seeded-separator seam, preserving the current public function/output contract and exact helper invocations.
2. Add a structural/fail-closed gate that pins all source blobs above and proves spawn/join/terminate/cleanup behavior without reference inputs.
3. Because this will be a materially new integration implementation, run one implementation-specific exact approved-fixture gate only after the structural gate passes; do not rerun the already-CLOSED generic concurrency diagnostic.
4. Require frozen WAV/PCM/shift/runtime identities and zero-retention behavior before any promotion consideration.
5. Persistent cache remains independently `BLOCKED_BY_RETENTION_POLICY`.
6. No production deploy or `main` merge until the implementation-specific promotion gate is GREEN.

### Hard stops

- No reference-facing scoring or quality verdict.
- No GOAT restricted bytes.
- No sealed GuitarSet `00/01/03` access.
- No SplitMySong reopening.
- No GPU Demucs performance rerun.
- No intra-Demucs split-parallel rerun.
- No direct/cascade cache rerun absent regression/fingerprint change.
- No generic view-level concurrency diagnostic rerun absent regression/fingerprint/runtime-policy change.
- No weakening exact parity/fail-closed criteria.
- No persistent user-audio/stem/result retention without explicit permission.
- No production bridge/worker/Vercel/UI change or `main` merge until promotion gates pass.
