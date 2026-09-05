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
- Exact stage-cache diagnostics GREEN/CLOSED; generic view-level concurrency diagnostic GREEN/CLOSED. Do not rerun closed lanes absent demonstrated regression/fingerprint/runtime-policy change.
- Persistent production cache remains **`BLOCKED_BY_RETENTION_POLICY`**.
- No persistent user-audio/stem/result retention without an explicit allowed retention boundary.
- No production bridge/worker/Vercel/UI change or `main` merge until promotion gates are satisfied.

## Production — unchanged

- Vercel/web `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`.
- Integration merge in that lineage: `ceeccfbbb17968c097bb56136487e7ddeaf1a5a4`.
- Deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, READY.
- Bridge `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`.
- Routing proven `usingV143RhythmAnalyzer=true`.
- Production worker/bridge/Vercel remains untouched by this branch-only scheduler work.

## Seeded scheduler candidate

- Implementation commit `6772a0ca1d700ea6861cd4401b51e093144c8d26`.
- `analyzer/v143_seeded_separator.py` candidate blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Prior serialized blob `250534e516cad36e49cae35b6eab2b88654be2d3` remains the pre-candidate provenance anchor.
- Schedule: normalize → spawn direct deterministic CPU Demucs child → unchanged parent RoFormer → spawn cascade deterministic CPU Demucs child → join/validate → copy unchanged outputs → unchanged public return contract.
- Fail-closed cleanup terminates/joins children and closes all pipe endpoints.

Pinned branch helper/source blobs:

- `v143_modal_http_endpoint.py` `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`
- `v143_modal_live_endpoint.py` `111bf14a8f91045d3478901f8e36b88a2e7f181a`
- `v143_vercel_audio_request_adapter.py` `6d1787f34a3b7ca781ced8e5695993a3777406a8`
- `v143_rhythm_deterministic_stem_provider.py` `3c6dcf9b8e7360ba1dd886810f3c14c05ac0579b`
- `v143_rhythm_stem_provider.py` `cd180bfb35e8110f031504035af5f11e502c3dc6`
- `v143_deterministic_separator.py` `28b3e6fe0eb761178b142cf7dcbda533f0bf918d`
- `v143_seeded_audio_separator_cli.py` `645f324c207d67b32c6d279657805ff8f25c3aa0`
- `v143_production_separator.py` `05ae1978fa02f8c84ccc1e44547fc4e4cea9798b`

## Frozen approved fixture

Repository-owned `public/gomywayfullaitest.m4a`:

- source SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`;
- normalized SHA `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- direct Guitar WAV SHA `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`;
- direct PCM-int16 SHA `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`;
- direct shift trace `0,22050,6026`;
- oneDNN off; Torch intra/inter-op = 1.
- Frozen RoFormer WAV/PCM prefixes `ce7ae8...` / `16e0a1...`; cascade WAV/PCM prefixes `546e51...` / `75c0fe...`. Full values remain in dedicated checkpoints and must be recovered before Gate 2 execution.

## Prior closed diagnostics

### Exact stage-cache — GREEN / CLOSED

- Direct run `33938289895`, job `101230445238`, artifact `9961088259`.
- Cascade run `33939561555`, job `101234177608`, artifact `9961570152`.

### Zero-retention generic view-level concurrency — GREEN / CLOSED

- `analyzer/v143_view_level_demucs_child.py` blob `7ffdf5183360f18ef2e356a12d1112d3f651ccbf`.
- `analyzer/v143_view_level_concurrency_modal.py` blob `ef14db309500c262d59a50bfaaec4d8ffa9b570a`.
- Actions run `33940555992`, job `101237009458`, artifact `9961880403`, `allPassed=true`.
- Exact identities unchanged; multiprocessing `spawn`; deterministic CPU Demucs; reference score calls `0`; quality verdict `false`; no raw audio/stem persistence.
- Contextual concurrency wall `773.381s` versus historical sequential stage sum `1487.706s`, contextual speedup `1.924x`; not a same-run paired benchmark.
- **Do not rerun this generic proof merely to validate the new scheduler.**

## Promotion Gate 1 — STRUCTURAL / GREEN / CLOSED

- Gate source `analyzer/v143_seeded_scheduler_structure_gate.py` blob `f31b5cc7742696975534081c535c0301911c6b87`.
- Gate source commit `4afd35b0c198982c603f0d375140e53be1862498`.
- Branch-only workflow `.github/workflows/v143-seeded-scheduler-structure.yml`.
- Workflow trigger commit `c9f8d0cb2f62d6e6bebda400665b3b2e094225f5`.
- Actions run `33942915753`: **SUCCESS**; job `101243642285`: **SUCCESS**.
- Log result: `gate=v143-seeded-scheduler-structure`, `allPassed=true`.
- Verified ordering: direct start line 112 < RoFormer line 126 < cascade start line 136 < direct join line 140 < cascade join line 146 < first copy line 155 < return line 159.
- Verified pinned live/helper blobs, literal `spawn`, deterministic child environments, parent RoFormer GPU visibility, fail-closed child cleanup, pipe closure, output names, and public return keys.
- `referenceFacingInputs=0`; `scoreCalls=0`; `qualityVerdictMade=false`.
- Source/AST only: no audio/model execution, no secrets, no deployment.

## Promotion Gate 2 — APPROVED FIXTURE RUNTIME / ARMED, NOT YET RUN

Run exactly one implementation-specific runtime seam through the current `build_seeded_v143_stems()` path after recovering all full frozen expected hashes. Requirements:

- approved source + normalized identity;
- exact direct WAV + PCM and deterministic shift trace;
- exact frozen RoFormer WAV + PCM;
- exact frozen cascade WAV + PCM;
- unchanged public output contract;
- request-scoped zero-retention cleanup;
- `referenceFacingInputs=0`, `scoreCalls=0`, `qualityVerdictMade=false`;
- no rerun of the CLOSED generic concurrency diagnostic.

## NEXT STEP

1. Recover full frozen RoFormer/cascade hashes and reuse the prior Modal proof only as infrastructure reference.
2. Wire and execute exactly one implementation-specific approved-fixture Gate 2 run.
3. If Gate 2 is GREEN, checkpoint immediately. At that point the normal-routing E2E pipeline test is unlocked/justified.
4. If Gate 2 fails after model execution, fail closed and diagnose before any rerun.

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
