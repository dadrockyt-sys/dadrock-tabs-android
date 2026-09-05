# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 00:28 America/Toronto  
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
- Generic proof used Modal envelope `gpu="L4"`, `cpu=2.0`, `memory=8192`, `timeout=1800`; collector wall `815.325s`, concurrent separation wall `773.381s`.
- Generic proof preserved exact identities, `spawn`, deterministic CPU Demucs, reference score calls `0`, quality verdict `false`, no raw audio/stem persistence; contextual speedup `1.924x` only, not same-run paired.
- **Do not rerun the generic concurrency proof merely to validate this scheduler.**

## Promotion Gate 1 — STRUCTURAL / GREEN / CLOSED

- Gate source `analyzer/v143_seeded_scheduler_structure_gate.py` blob `f31b5cc7742696975534081c535c0301911c6b87`.
- Gate commit `4afd35b0c198982c603f0d375140e53be1862498`.
- Workflow `.github/workflows/v143-seeded-scheduler-structure.yml`; trigger commit `c9f8d0cb2f62d6e6bebda400665b3b2e094225f5`.
- Actions run `33942915753`: **SUCCESS**; job `101243642285`: **SUCCESS**; `allPassed=true`.
- Verified scheduler ordering, literal `spawn`, deterministic child environments, parent RoFormer GPU visibility, fail-closed cleanup, pipe closure, outputs, public keys, and pinned helper blobs.
- `referenceFacingInputs=0`; `scoreCalls=0`; `qualityVerdictMade=false`.

## Promotion Gate 2 — APPROVED FIXTURE RUNTIME / GREEN / CLOSED

Implementation-specific one-shot harness is branch-local and does **not** import/reuse the CLOSED generic concurrency helper.

Proof-time blobs:

- `analyzer/v143_seeded_scheduler_runtime_modal.py` `94ce232eb2a86bafb95815ee693e19c5c38af1b7`;
- `.github/scripts/v143_seeded_scheduler_runtime_collect.py` `dea00bc99f5cf06b8e1d1ab60643840c6924968d`;
- scheduler proof blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.

### Authoritative GREEN execution

- Workflow-creation commit `bcd00fa4db238ab0efd6ae18212cac164e6c3f71` automatically launched Gate-2 **run #1** `33943100948` at `2026-09-05T03:53:44Z`.
- Job `101244148835`: **SUCCESS**; every workflow step including approved-fixture execution, aggregate evidence upload, and isolated app cleanup succeeded.
- Artifact `9962641557` (`sha256:0d88c498f4b1d31895399ee66c65a8efef90e0e69150092cfd8d0a91d7d427b1`): **GREEN**, `allPassed=true`.
- Function call `fc-01M1QV7RXNV2BZSF2688P5PKWY` completed the actual current `build_seeded_v143_stems()` scheduler path.
- Runtime evidence: `runtimeSeconds=795.954`, collector wall `810.5s`, Modal GPU `NVIDIA L4`, scheduler start method `spawn`.
- `exactParityPassed=true`, `publicContractPassed=true`, `runtimeInvariantPassed=true`, `cleanupPassed=true`, `safetyBoundaryPassed=true`.
- Exact frozen source/normalized/model/WAV/PCM identities all matched.
- Shift traces exactly direct=`0,22050,6026`, cascade=`0,22050,6026`.
- Demucs runtime invariant: CUDA unavailable in child, MKLDNN available but disabled, Torch CPU capability `DEFAULT`, Torch intra/inter-op threads `1`, ATen `default`, MKL `COMPATIBLE`, oneDNN/MKLDNN disabled.
- Public top-level keys, model map, settings map, and output filenames all matched the frozen contract.
- `referenceFacingInputs=0`; `referenceFacingAccuracyScored=false`; `referenceScoreCalls=0`; `qualityVerdictMade=false`.
- `rawAudioRetained=false`; `stemBytesRetained=false`; `crossRequestPersistence=false`.
- `productionWorkerChanged=false`; `productionBridgeChanged=false`; `vercelChanged=false`; `mainMergePerformed=false`.

### Run #2 race diagnosis

- Explicit trigger commit `855dc46a87a75f9c8b11f1eaf71a76319e99af1b` launched Gate-2 run #2 `33943117001` only ~25s after workflow creation.
- Both runs used the same fixed isolated Modal app.
- Historical Modal logs retrieved by diagnosis-only run `33943967529` prove run #1 returned GREEN while run #2 was still in cascade Demucs; run #1 cleanup then stopped the shared app and caused run #2 cancellation/`KeyboardInterrupt`/client `RemoteError`.
- Collector source calls the remote function exactly once per workflow execution.
- Therefore run #2 is a shared-app race artifact, not a scheduler parity regression.
- **Gate 2 is CLOSED/GREEN from run #1. No Gate-2 rerun is justified.**

## Gate 2 dormant-workflow hardening — COMPLETE / ZERO FIXTURE EXECUTIONS

The proof remains anchored to the proof-time blobs above. Post-proof harness hardening changes only future gate orchestration and does **not** alter the scheduler candidate blob.

1. Commit `d414f85288b7cbe6e2dd1c14792676c72c613e9c` changed `.github/workflows/v143-seeded-scheduler-runtime.yml` to **manual-only `workflow_dispatch`** and added a static concurrency group with `cancel-in-progress: false`.
2. Commit `6851b17e6294eed1adafedf28944414a1c115189` changed `analyzer/v143_seeded_scheduler_runtime_modal.py` so the Modal app name is required from `V143_SEEDED_SCHEDULER_RUNTIME_APP_NAME`; new blob `acbbee111ee4f8818b5b21f898253d7ea0625bec`.
3. Commit `4c050021134779f95c410fc460ebf413b470d683` changed the collector to require/use the same app-name environment variable; new blob `bd01ce7784c5b05d4b72bfde733342b838e9b30f`.
4. Commit `d2597deb7d710ea724c3110e67cf829ba9660aeb` finished workflow isolation: app name is `dadrock-v143-seeded-scheduler-runtime-gate-${github.run_id}-${github.run_attempt}`, exact helper blob pins were updated, deploy/collector/cleanup share that identity, and cleanup stops only that run's app. Workflow blob `ab6284332c0862d6d75a4088a22c8c6ab7f4a2a4`.

Verification:

- Pushes `d414f852...`, `6851b17e...`, `4c050021...`, and `d2597deb...` each produced **zero `V143 Seeded Scheduler Runtime Gate` executions**. The only Actions entry for each SHA was the unrelated `cleanup-tab-preview.yml` workflow.
- No approved fixture was invoked by hardening.
- No Modal production app was deployed/stopped by hardening.
- No production worker/bridge/Vercel code changed.
- No reference-facing input/scoring or quality verdict occurred.
- Future Gate-2 executions are deliberate, serialized, and per-run isolated; however Gate 2 is already closed and must not be rerun absent a demonstrated source/runtime-policy change that invalidates the proof.

## PROMOTION STATUS

- Gate 1 structural: **GREEN / CLOSED**.
- Gate 2 approved-fixture runtime: **GREEN / CLOSED**.
- Gate 2 dormant workflow: **HARDENED / MANUAL-ONLY / SERIALIZED / PER-RUN ISOLATED**.
- Normal-routing E2E pipeline verification is **UNLOCKED/JUSTIFIED**.
- Production remains unchanged until that next gate is designed and passes.

## NEXT STEP

1. Inspect prior checkpoints, routing helpers, existing branch-only harnesses/workflows, and current request path to recover the intended **normal-routing E2E** gate rather than inventing a broader test.
2. Define the narrowest gate that proves the current scheduler candidate is reached through the normal branch routing stack while preserving zero reference scoring and zero persistent audio/stem retention.
3. Prefer structural/static checks first; do not invoke an expensive approved-fixture/model path until the exact E2E boundary, app isolation, trigger policy, and evidence contract are pinned.
4. Checkpoint the E2E design before any model-bearing run.

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
- No weakening exact parity/fail-closed criteria.
- No persistent user-audio/stem/result retention without explicit permission.
- No production bridge/worker/Vercel/UI change or `main` merge until normal-routing E2E passes.
