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
- Production worker/bridge/Vercel unchanged by cache/concurrency diagnostics and by the branch-only scheduler candidate below.

### Source-provenance distinction

The Vercel/web `main` SHA and the independently deployed Modal worker source are separate provenance anchors. Do **not** use `bb992...` as the Modal worker source fingerprint.

Current branch source blobs for the live Modal/separator chain, except the intentionally modified branch-only seeded scheduler candidate:

- `analyzer/v143_modal_http_endpoint.py` blob `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`;
- `analyzer/v143_modal_live_endpoint.py` blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`;
- `analyzer/v143_vercel_audio_request_adapter.py` blob `6d1787f34a3b7ca781ced8e5695993a3777406a8`;
- `analyzer/v143_rhythm_deterministic_stem_provider.py` blob `3c6dcf9b8e7360ba1dd886810f3c14c05ac0579b`;
- `analyzer/v143_rhythm_stem_provider.py` blob `cd180bfb35e8110f031504035af5f11e502c3dc6`;
- `analyzer/v143_deterministic_separator.py` blob `28b3e6fe0eb761178b142cf7dcbda533f0bf918d`;
- `analyzer/v143_seeded_separator.py` candidate blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8` at commit `6772a0ca1d700ea6861cd4401b51e093144c8d26`;
- prior serialized seeded-separator blob `250534e516cad36e49cae35b6eab2b88654be2d3` remains the pre-candidate provenance anchor;
- `analyzer/v143_seeded_audio_separator_cli.py` blob `645f324c207d67b32c6d279657805ff8f25c3aa0`;
- `analyzer/v143_production_separator.py` blob `05ae1978fa02f8c84ccc1e44547fc4e4cea9798b`.

## Exact direct anchor — GREEN / frozen

Repository-owned `public/gomywayfullaitest.m4a`:

- source SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`;
- normalized SHA `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- direct Guitar WAV SHA `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`;
- direct PCM-int16 SHA `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`;
- shift trace `0,22050,6026`;
- oneDNN off; Torch intra/inter-op = 1.

## Exact stage-cache diagnostics — GREEN / CLOSED

- Direct exact parity/mismatch/corruption/cleanup GREEN; run `33938289895`, job `101230445238`, artifact `9961088259`.
- Cascade exact parity/mismatch/corruption/cleanup GREEN; run `33939561555`, job `101234177608`, artifact `9961570152`.
- Frozen RoFormer WAV/PCM `ce7ae8...` / `16e0a1...`; cascade WAV/PCM `546e51...` / `75c0fe...`.
- Persistent production cache remains **`BLOCKED_BY_RETENTION_POLICY`**.

## Zero-retention view-level concurrency — GREEN / CLOSED

Validated proof artifacts:

- `analyzer/v143_view_level_demucs_child.py` blob `7ffdf5183360f18ef2e356a12d1112d3f651ccbf`;
- `analyzer/v143_view_level_concurrency_modal.py` blob `ef14db309500c262d59a50bfaaec4d8ffa9b570a`;
- Actions run `33940555992`: **SUCCESS**; job `101237009458`: **SUCCESS**; artifact `9961880403`; `allPassed=true`.

Frozen proof conclusions:

- multiprocessing start method `spawn`;
- direct and cascade Demucs exact identities unchanged;
- RoFormer exact identity unchanged;
- both Demucs children remain CPU-only/single-thread with oneDNN disabled and deterministic env;
- concurrent separation wall `773.381s` vs historical sequential stage sum `1487.706s`, contextual speedup `1.924x`;
- **`1.924x` is cross-run/contextual only; no same-run paired sequential benchmark was performed.**
- reference score calls `0`; quality verdict made `false`; no raw audio/stem persistence.

Verdict: **view-level concurrency is proven exact and materially useful as an isolated zero-retention performance candidate.** Do not rerun the generic proof absent demonstrated regression/fingerprint/runtime-policy change.

## Seeded scheduler candidate — IMPLEMENTED / NOT YET PROMOTABLE

Commit `6772a0ca1d700ea6861cd4401b51e093144c8d26` changes only `analyzer/v143_seeded_separator.py` at the requested scheduler seam. The public `build_seeded_v143_stems()` return keys, output filenames, model constants, deterministic settings, normalization helper, RoFormer helper, and Demucs helper remain unchanged.

Candidate schedule now is:

1. normalize exactly as before;
2. create a `multiprocessing.get_context("spawn")` scheduler;
3. start direct exact Demucs in an isolated child **before** RoFormer, with the existing deterministic CPU environment present at process start;
4. run unchanged `separate_roformer_instrumental(...)` in the current parent with GPU visibility restored;
5. after the RoFormer intermediate exists, start cascade exact Demucs in a second isolated child with the same deterministic CPU environment;
6. join/validate direct then cascade before copying or returning;
7. on any scheduling/helper/child exception, terminate + join both child processes before propagating failure;
8. close all parent/child pipe endpoints in `finally`;
9. copy the same three frozen output filenames and return the same result object shape.

Implementation intentionally keeps the child target inside `v143_seeded_separator.py`; this avoids adding the probe-only `v143_view_level_demucs_child` module to the live endpoint module list and keeps the candidate scheduler-only at the resolved seam.

No persistent cache, reference corpus, score call, production deploy, staging change, UI change, or `main` merge occurred.

## Scheduler source map — RESOLVED

Call chain remains:

`v143_modal_http_endpoint.py` → `dadrock-v143-ai-tab-live/rhythm_v143_request` → `process_vercel_audio_request(...)` → `build_deterministic_rhythm_stem_bundle(...)` → `build_rhythm_stem_bundle(...)` → `build_deterministic_v143_stems(...)` → `build_seeded_v143_stems(...)`.

`process_vercel_audio_request()` still owns the request `TemporaryDirectory`, so all candidate child work remains request-scoped and both children must be joined/terminated before the seeded separator returns.

## Seeded scheduler structural gate — ADDED / NOT YET RUN

- Gate source: `analyzer/v143_seeded_scheduler_structure_gate.py` blob `f31b5cc7742696975534081c535c0301911c6b87`.
- Gate commit: `4afd35b0c198982c603f0d375140e53be1862498`.
- Pure stdlib/source/AST gate only: no model invocation, audio execution, reference input, or scorer call.
- Pins the candidate separator plus the resolved live routing/helper source blobs.
- Requires literal `spawn` scheduling and exact lexical order: direct child start < RoFormer parent call < cascade child start < direct join < cascade join < output copy < return.
- Requires both child `Process` targets to remain `_run_demucs_child`, both starts inside `DEMUCS_SINGLE_THREAD_ENV`, and RoFormer inside the GPU-visibility parent environment.
- Requires `BaseException` cleanup to terminate+join both process handles, re-raise, and close all four pipe endpoints in `finally`.
- Requires helper-level fail-closed checks (`join`, `is_alive`, `exitcode`, result `poll`/`recv`) plus exact output filenames and public return keys.
- Rejects active scorer/reference-corpus/sealed-dataset symbols and emits `referenceFacingInputs=0`, `scoreCalls=0`, `qualityVerdictMade=false`.

## NEXT STEPS

1. Wire/run the branch-only pure source/AST scheduler gate. No reference-facing scoring or hidden targets.
2. If the static gate fails, fix only the scheduler/gate defect and rerun the static gate; do not spend an approved-fixture runtime yet.
3. Only after that gate is GREEN, run one implementation-specific exact approved-fixture runtime seam gate, requiring the frozen WAV/PCM/shift/runtime identities and zero-retention behavior.
4. Do **not** rerun the already-CLOSED generic concurrency diagnostic.
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
