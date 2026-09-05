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
- Integration merge: `ceeccfbbb17968c097bb56136487e7ddeaf1a5a4`.
- Deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, READY.
- Bridge `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`.
- Routing proven `usingV143RhythmAnalyzer=true`.
- Production worker/bridge/Vercel untouched by this branch-only scheduler work.

## Seeded scheduler candidate

- Implementation commit `6772a0ca1d700ea6861cd4401b51e093144c8d26`.
- `analyzer/v143_seeded_separator.py` blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Prior serialized blob `250534e516cad36e49cae35b6eab2b88654be2d3` remains pre-candidate provenance.
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
- direct/cascade deterministic shift trace each `0,22050,6026`;
- RoFormer weight SHA256 `5b84f37e8d444c8cb30c79d77f613a41c05868ff9c9ac6c7049c00aefae115aa`;
- Demucs weight SHA256 `34c22ccb381c6f9fdbf324f04e1e2fe21aaaf293f5ded163a162697ff9a02ddd`;
- Demucs config SHA256 `207405151270af8fd81c2373c25d27950916682ac91dca7884a11ce13dad6f58`;
- oneDNN off; Torch intra/inter-op = 1.

## Prior closed diagnostics

- Exact direct stage-cache run `33938289895`, job `101230445238`, artifact `9961088259` — GREEN/CLOSED.
- Exact cascade stage-cache run `33939561555`, job `101234177608`, artifact `9961570152` — GREEN/CLOSED.
- Generic zero-retention view-level concurrency run `33940555992`, job `101237009458`, artifact `9961880403`, `allPassed=true` — GREEN/CLOSED.
- Generic proof preserved exact identities, `spawn`, deterministic CPU Demucs, reference score calls `0`, quality verdict `false`, no raw audio/stem persistence; contextual speedup `1.924x` only, not same-run paired.
- **Do not rerun the generic concurrency proof merely to validate this scheduler.**

## Promotion Gate 1 — STRUCTURAL / GREEN / CLOSED

- Gate source `analyzer/v143_seeded_scheduler_structure_gate.py` blob `f31b5cc7742696975534081c535c0301911c6b87`.
- Gate commit `4afd35b0c198982c603f0d375140e53be1862498`.
- Workflow `.github/workflows/v143-seeded-scheduler-structure.yml`; trigger commit `c9f8d0cb2f62d6e6bebda400665b3b2e094225f5`.
- Actions run `33942915753`: **SUCCESS**; job `101243642285`: **SUCCESS**; `allPassed=true`.
- Verified scheduler ordering, literal `spawn`, deterministic child environments, parent RoFormer GPU visibility, fail-closed cleanup, pipe closure, outputs, public keys, and pinned helper blobs.
- `referenceFacingInputs=0`; `scoreCalls=0`; `qualityVerdictMade=false`.

## Promotion Gate 2 — APPROVED FIXTURE RUNTIME / IN PROGRESS

Implementation-specific one-shot harness is branch-local and does **not** import/reuse the CLOSED generic concurrency helper:

- `analyzer/v143_seeded_scheduler_runtime_modal.py` blob `94ce232eb2a86bafb95815ee693e19c5c38af1b7`;
- `.github/scripts/v143_seeded_scheduler_runtime_collect.py` blob `dea00bc99f5cf06b8e1d1ab60643840c6924968d`;
- workflow `.github/workflows/v143-seeded-scheduler-runtime.yml`;
- workflow trigger commit `855dc46a87a75f9c8b11f1eaf71a76319e99af1b`;
- Actions run `33943117001`: **IN PROGRESS** at checkpoint time.

Gate invokes current `build_seeded_v143_stems()` exactly once against the approved fixture and requires:

- all frozen source/normalized/model/WAV/PCM identities above;
- two exact deterministic Demucs shift events (`0,22050,6026` each);
- deterministic CPU runtime trace (oneDNN disabled, Torch intra/inter-op 1, ATen DEFAULT, MKL COMPATIBLE);
- unchanged top-level return keys, model map, settings map, and output filenames;
- request-scoped `TemporaryDirectory` removed before evidence return;
- aggregate evidence only; no audio/stem bytes retained or uploaded;
- `referenceFacingInputs=0`, `referenceScoreCalls=0`, `qualityVerdictMade=false`;
- isolated Modal app `dadrock-v143-seeded-scheduler-runtime-gate`, stopped in workflow cleanup; production app is not a deployment target.

If this completed model execution fails, **do not casually rerun it**: fail closed, inspect evidence, and diagnose first.

## NEXT STEP

1. Observe Actions run `33943117001` to terminal state.
2. If GREEN, checkpoint Gate 2 as CLOSED/GREEN; the normal-routing E2E pipeline test is then unlocked/justified.
3. If failed after model execution, checkpoint failure and diagnose before deciding whether any rerun is justified.

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
