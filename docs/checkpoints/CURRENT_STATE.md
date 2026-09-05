# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 00:40 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet prospective `00/01/03` sealed.
- Current quality verdict: **NO QUALITY VERDICT — PERFORMANCE/IDENTITY/ROUTING DIAGNOSTICS ONLY**.
- GPU Demucs promotion CLOSED; native intra-Demucs split-parallel CPU promotion CLOSED.
- Exact stage-cache diagnostics GREEN/CLOSED; generic view-level concurrency diagnostic GREEN/CLOSED.
- Persistent production cache remains **`BLOCKED_BY_RETENTION_POLICY`**.
- No persistent user-audio/stem/result retention without an explicit allowed retention boundary.
- No production bridge/worker/Vercel/UI change or `main` merge until the normal-routing promotion boundary is closed.

## Production — unchanged

- Vercel/web `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`.
- Integration merge: `ceeccfbbb17968c097bb56136487e7ddeaf1a5a4`.
- Deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, READY.
- Bridge `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`.
- Routing previously proven `usingV143RhythmAnalyzer=true`.
- Production worker/bridge/Vercel untouched by branch-only scheduler/gate work.

## Seeded scheduler candidate

- Implementation commit `6772a0ca1d700ea6861cd4401b51e093144c8d26`.
- `analyzer/v143_seeded_separator.py` blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Schedule: normalize → spawn direct deterministic CPU Demucs child → unchanged parent RoFormer → spawn cascade deterministic CPU Demucs child → join/validate → copy unchanged outputs → unchanged public return contract.
- Fail-closed cleanup terminates/joins children and closes all pipe endpoints.

Pinned normal-routing source blobs:

- `app/api/analyze-audio-tab/route.js` `06234db3e1cc1680b18fd62a765862b213ede3db`
- `analyzer/v143_modal_http_endpoint.py` `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`
- `analyzer/v143_modal_live_endpoint.py` `111bf14a8f91045d3478901f8e36b88a2e7f181a`
- `analyzer/v143_vercel_audio_request_adapter.py` `6d1787f34a3b7ca781ced8e5695993a3777406a8`
- `analyzer/v143_modal_rhythm_router.py` `7849f33cd3b849283ccebfda9f721cc40704231e`
- `analyzer/v143_rhythm_deterministic_stem_provider.py` `3c6dcf9b8e7360ba1dd886810f3c14c05ac0579b`
- `analyzer/v143_rhythm_stem_provider.py` `cd180bfb35e8110f031504035af5f11e502c3dc6`
- `analyzer/v143_deterministic_separator.py` `28b3e6fe0eb761178b142cf7dcbda533f0bf918d`

## Frozen approved fixture identities

Repository-owned `public/gomywayfullaitest.m4a`:

- source SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`;
- normalized WAV SHA256 `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- direct Guitar WAV SHA256 `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`;
- direct PCM-int16 SHA256 `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`;
- RoFormer Instrumental WAV SHA256 `ce7ae8c6c57e00e1e191b8c15a8c4f39627cbcdf3b7a75ac7ca4c246f6f64b14`;
- RoFormer PCM-int16 SHA256 `16e0a16a54ab1b007d15647d293900ecfbfabceccfa886f004a86162d4a454dd`;
- cascade Guitar WAV SHA256 `546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41`;
- cascade PCM-int16 SHA256 `75c0feefb416d8438641ceebe903253f935bd19c550e97e9ef0a90426e7727ba`;
- direct/cascade shifts each `0,22050,6026`;
- RoFormer weight SHA256 `5b84f37e8d444c8cb30c79d77f613a41c05868ff9c9ac6c7049c00aefae115aa`;
- Demucs weight SHA256 `34c22ccb381c6f9fdbf324f04e1e2fe21aaaf293f5ded163a162697ff9a02ddd`;
- Demucs config SHA256 `207405151270af8fd81c2373c25d27950916682ac91dca7884a11ce13dad6f58`.

## Promotion Gate 1 — STRUCTURAL / GREEN / CLOSED

- Gate source `analyzer/v143_seeded_scheduler_structure_gate.py` blob `f31b5cc7742696975534081c535c0301911c6b87`.
- Run `33942915753`, job `101243642285`: **SUCCESS**, `allPassed=true`.
- Verified scheduler order, literal `spawn`, deterministic child environments, parent RoFormer GPU visibility, fail-closed cleanup, pipe closure, outputs/public keys, and pinned helper blobs.
- `referenceFacingInputs=0`; `scoreCalls=0`; `qualityVerdictMade=false`.

## Promotion Gate 2 — APPROVED FIXTURE RUNTIME / GREEN / CLOSED

- Authoritative run #1 `33943100948`, job `101244148835`: **SUCCESS**.
- Artifact `9962641557`, `allPassed=true`.
- Actual current `build_seeded_v143_stems()` path completed; `runtimeSeconds=795.954`; L4; scheduler start method `spawn`.
- `exactParityPassed=true`, `publicContractPassed=true`, `runtimeInvariantPassed=true`, `cleanupPassed=true`, `safetyBoundaryPassed=true`.
- Exact frozen source/normalized/model/WAV/PCM identities matched; shift traces matched exactly.
- `referenceFacingInputs=0`; `referenceScoreCalls=0`; `qualityVerdictMade=false`; no raw/stem persistence.
- Run #2 `33943117001` failed only because two workflow executions shared one isolated Modal app; historical logs proved run #1 completed and its cleanup cancelled overlapping run #2. This was an orchestration race, not scheduler parity evidence.
- Gate 2 remains **GREEN/CLOSED**; no rerun justified.

## Gate 2 dormant-workflow hardening — COMPLETE

- Runtime workflow is now manual-only `workflow_dispatch`, serialized (`cancel-in-progress: false`), and per-run isolated.
- Per-run Modal app identity: `dadrock-v143-seeded-scheduler-runtime-gate-${github.run_id}-${github.run_attempt}`.
- Deploy, collector and cleanup share only that run's app identity.
- Hardening commits produced zero approved-fixture executions.

## Promotion Gate 3A — NORMAL-ROUTING COMPOSITION E2E / IN PROGRESS

Recovered chain:

1. Vercel `route.js` selects `ANALYZER_API_URL_V143` only for Rhythm and leaves Lead/Bass on legacy analyzer.
2. HTTP bridge forwards Rhythm to Modal app `dadrock-v143-ai-tab-live`, function `rhythm_v143_request`.
3. Live worker invokes `process_vercel_audio_request(...)` with `build_deterministic_rhythm_stem_bundle`.
4. Request adapter owns request-scoped `TemporaryDirectory`, download/normalization, then routes normalized audio.
5. Rhythm router calls the supplied stem provider only for Rhythm; Lead/Bass delegate to legacy analyzer.
6. Deterministic provider → authoritative stem-bundle layer → deterministic wrapper → already-proven seeded scheduler candidate.
7. Vercel fail-closed anti-leakage fields remain `referenceFree=true`, `professionalReferenceUsed=false`, `referenceRuntimeInputUsed=false`, `runtimeLabelsRequired=false`.

Gate implementation:

- `analyzer/v143_normal_routing_e2e_structure_gate.py` hardened commit `1db06d0d52109ddb9b99fa8222a6d38a5a72e6e5`; current blob `cd5be6b27718187d5a2bc7b21e81356a6be67b79`.
- `.github/workflows/v143-normal-routing-e2e-structure.yml` commit `c6925ee09ff5158e6d562147fda05f7adc3cc1c8`.
- Gate is Python-stdlib/source/AST only; exact Git-blob pins; no project-module import, audio, fixture, model, Modal, GPU, secrets, scoring, or quality verdict.
- Workflow run `33945157629`, job `101249801382`: **IN PROGRESS** at this checkpoint.
- Evidence target: `debug/v143-contextual-prune/normal-routing-e2e-structure/summary.json` aggregate booleans/identities only.

## PROMOTION STATUS

- Gate 1 structural: **GREEN / CLOSED**.
- Gate 2 approved-fixture runtime: **GREEN / CLOSED**.
- Gate 2 dormant workflow: **HARDENED / MANUAL-ONLY / SERIALIZED / PER-RUN ISOLATED**.
- Gate 3A normal-routing composition E2E: **IN PROGRESS**.
- Production: **UNCHANGED**.

## NEXT STEP

1. Observe Gate 3A run `33945157629` to terminal state.
2. If GREEN, inspect aggregate artifact and checkpoint Gate 3A CLOSED/GREEN.
3. Evaluate whether any model-bearing normal-route E2E adds evidence not already supplied by Gate 3A + authoritative Gate 2; do **not** run one merely to repeat Gate 2.

### Hard stops

- No reference-facing scoring or quality verdict.
- No GOAT restricted bytes.
- No sealed GuitarSet `00/01/03` access.
- No SplitMySong reopening.
- No GPU Demucs performance rerun.
- No intra-Demucs split-parallel rerun.
- No direct/cascade cache rerun absent regression/fingerprint change.
- No generic view-level concurrency diagnostic rerun absent regression/fingerprint/runtime-policy change.
- No Gate-2 approved-fixture rerun: existing run #1 is authoritative GREEN.
- No Gate-3 model-bearing run until Gate 3A closes and incremental evidentiary value is demonstrated.
- No weakening exact parity/fail-closed criteria.
- No persistent user-audio/stem/result retention without explicit permission.
- No production bridge/worker/Vercel/UI change or `main` merge until the normal-routing promotion boundary is closed.
