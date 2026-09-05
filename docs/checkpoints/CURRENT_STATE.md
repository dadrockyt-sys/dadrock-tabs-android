# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 00:42 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet prospective `00/01/03` sealed.
- Current quality verdict: **NO QUALITY VERDICT — PERFORMANCE/IDENTITY/ROUTING DIAGNOSTICS ONLY**.
- Exact stage-cache diagnostics and generic view-level concurrency diagnostic remain GREEN/CLOSED; do not rerun absent demonstrated regression/fingerprint/runtime-policy change.
- Persistent production cache remains **`BLOCKED_BY_RETENTION_POLICY`**.
- No persistent user-audio/stem/result retention without an explicit allowed retention boundary.
- No production bridge/worker/Vercel/UI change or `main` merge until the normal-routing promotion boundary is explicitly closed.

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

Pinned normal-routing blobs:

- `app/api/analyze-audio-tab/route.js` `06234db3e1cc1680b18fd62a765862b213ede3db`
- `v143_modal_http_endpoint.py` `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`
- `v143_modal_live_endpoint.py` `111bf14a8f91045d3478901f8e36b88a2e7f181a`
- `v143_vercel_audio_request_adapter.py` `6d1787f34a3b7ca781ced8e5695993a3777406a8`
- `v143_modal_rhythm_router.py` `7849f33cd3b849283ccebfda9f721cc40704231e`
- `v143_rhythm_deterministic_stem_provider.py` `3c6dcf9b8e7360ba1dd886810f3c14c05ac0579b`
- `v143_rhythm_stem_provider.py` `cd180bfb35e8110f031504035af5f11e502c3dc6`
- `v143_deterministic_separator.py` `28b3e6fe0eb761178b142cf7dcbda533f0bf918d`

## Promotion Gate 1 — STRUCTURAL / GREEN / CLOSED

- Run `33942915753`, job `101243642285`: **SUCCESS**, `allPassed=true`.
- Scheduler source `v143_seeded_separator.py` blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Verified scheduler order, literal `spawn`, deterministic child environments, parent RoFormer GPU visibility, fail-closed cleanup, pipe closure, outputs/public keys, and pinned helper blobs.
- `referenceFacingInputs=0`; `scoreCalls=0`; `qualityVerdictMade=false`.

## Promotion Gate 2 — APPROVED FIXTURE RUNTIME / GREEN / CLOSED

- Authoritative run #1 `33943100948`, job `101244148835`: **SUCCESS**; artifact `9962641557`; `allPassed=true`.
- Actual current `build_seeded_v143_stems()` path completed on L4; `runtimeSeconds=795.954`; scheduler start method `spawn`.
- `exactParityPassed=true`, `publicContractPassed=true`, `runtimeInvariantPassed=true`, `cleanupPassed=true`, `safetyBoundaryPassed=true`.
- Exact frozen source/normalized/model/WAV/PCM identities and direct/cascade shift traces matched.
- `referenceFacingInputs=0`; `referenceScoreCalls=0`; `qualityVerdictMade=false`; no raw/stem persistence.
- Run #2 `33943117001` was invalidated by a duplicate-run shared-app cleanup race; historical logs proved run #1 had completed successfully. No Gate-2 rerun is justified.

## Gate 2 dormant workflow — HARDENED

- Manual-only `workflow_dispatch`, serialized (`cancel-in-progress: false`), per-run isolated app identity `dadrock-v143-seeded-scheduler-runtime-gate-${github.run_id}-${github.run_attempt}`.
- Deploy/collector/cleanup share only their run's app identity.
- Hardening caused zero approved-fixture executions.

## Promotion Gate 3A — NORMAL-ROUTING COMPOSITION E2E / GREEN / CLOSED

- Gate source: `analyzer/v143_normal_routing_e2e_structure_gate.py`, hardening commit `1db06d0d52109ddb9b99fa8222a6d38a5a72e6e5`, blob `cd5be6b27718187d5a2bc7b21e81356a6be67b79`.
- Workflow: `.github/workflows/v143-normal-routing-e2e-structure.yml`, creation commit `c6925ee09ff5158e6d562147fda05f7adc3cc1c8`.
- Actions run `33945157629`, job `101249801382`: **SUCCESS**.
- Artifact `9963085825`, digest `sha256:9084a0d17ca44154e66a89f78546b6e210e3a302110e9e560c99b9f20a39ad09`.
- Aggregate evidence: `allPassed=true`.
- All 9 exact source Git-blob identities matched, including scheduler blob `fc9b4c45...`.
- Passed full chain: Vercel Rhythm-only V143 selection + private Blob handoff + fail-closed runtime safety → HTTP bridge worker identity and Lead/Bass legacy fallback → live worker normal adapter + deterministic provider → request-scoped tempdir/download-normalize-route order → Rhythm-only provider/router → independent direct/cascade stem bundle → deterministic wrapper → seeded scheduler with literal `spawn`.
- Restricted/reference-scoring import hits: none across the pinned Python routing chain.
- `approvedFixtureInvoked=false`; `audioBytesRead=false`; `modelExecutionPerformed=false`; `modalCalled=false`; `gpuUsed=false`.
- `referenceFacingInputs=0`; `referenceFacingAccuracyScored=false`; `referenceScoreCalls=0`; `qualityVerdictMade=false`.
- `rawAudioRetained=false`; `stemBytesRetained=false`; `crossRequestPersistence=false`.
- `productionWorkerChanged=false`; `productionBridgeChanged=false`; `vercelChanged=false`; `mainMergePerformed=false`.

## Evidence composition now available

- Gate 1 proves the scheduler candidate's static/process/fail-closed structure.
- Gate 2 proves that exact scheduler blob on the approved fixture under the required runtime and exact parity/public-contract/runtime/cleanup invariants.
- Gate 3A proves the exact normal routing source identities compose from Vercel Rhythm selection through the deterministic wrapper to that same Gate-2-proven scheduler blob, while preserving Lead/Bass legacy behavior and runtime anti-leakage boundaries.
- A further model-bearing normal-route execution would therefore need to demonstrate an **incremental property not already covered** by those three proofs before it is authorized; repeating the same separator/model computation is not sufficient justification.

## PROMOTION STATUS

- Gate 1 structural: **GREEN / CLOSED**.
- Gate 2 approved-fixture runtime: **GREEN / CLOSED**.
- Gate 2 dormant workflow: **HARDENED / MANUAL-ONLY / SERIALIZED / PER-RUN ISOLATED**.
- Gate 3A normal-routing composition E2E: **GREEN / CLOSED**.
- Production: **UNCHANGED**.
- Normal-routing promotion boundary: **EVIDENCE REVIEW NEXT; not yet explicitly closed in this checkpoint**.

## NEXT STEP

1. Evaluate the incremental evidentiary value of a model-bearing normal-route E2E against Gate 1 + Gate 2 + Gate 3A.
2. If no unique property requires another expensive/audio-bearing run, document `MODEL_BEARING_E2E_NOT_JUSTIFIED` and close the normal-routing promotion evidence boundary without rerunning models.
3. Only after that boundary is explicitly closed, prepare the narrow production integration/deploy plan; do not merge/deploy implicitly.

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
- No model-bearing normal-route run absent a demonstrated unique evidentiary property.
- No weakening exact parity/fail-closed criteria.
- No persistent user-audio/stem/result retention without explicit permission.
- No production bridge/worker/Vercel/UI change or `main` merge until the normal-routing promotion boundary is explicitly closed.
