# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 00:44 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet prospective `00/01/03` sealed.
- **NO QUALITY VERDICT** — performance/identity/routing diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`.
- No persistent user-audio/stem/result retention without explicit permission.

## Production — unchanged

- Vercel/web `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`.
- Integration merge: `ceeccfbbb17968c097bb56136487e7ddeaf1a5a4`.
- Deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, READY.
- Bridge `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`.
- Production worker/bridge/Vercel remain untouched by branch-only scheduler/gate work.

## Candidate

- Scheduler implementation commit `6772a0ca1d700ea6861cd4401b51e093144c8d26`.
- `analyzer/v143_seeded_separator.py` blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Schedule: normalize → spawn direct deterministic CPU Demucs → parent RoFormer → spawn cascade deterministic CPU Demucs → join/validate → unchanged outputs/public contract.
- Fail-closed cleanup terminates/joins children and closes pipe endpoints.

## Promotion evidence

### Gate 1 — STRUCTURAL / GREEN / CLOSED

- Run `33942915753`, job `101243642285`: SUCCESS, `allPassed=true`.
- Exact scheduler blob above; literal `spawn`; scheduler ordering; deterministic child envs; parent RoFormer GPU visibility; fail-closed cleanup; frozen output/public contract.
- Reference inputs `0`; score calls `0`; quality verdict `false`.

### Gate 2 — APPROVED FIXTURE RUNTIME / GREEN / CLOSED

- Authoritative run `33943100948`, job `101244148835`, artifact `9962641557`: SUCCESS, `allPassed=true`.
- Exact scheduler executed on approved fixture on L4; `runtimeSeconds=795.954`.
- Exact frozen source/normalized/model/WAV/PCM identities and direct/cascade deterministic shift traces matched.
- Exact parity/public-contract/runtime-invariant/cleanup/safety gates all passed.
- Reference inputs `0`; score calls `0`; quality verdict `false`; no raw/stem persistence.
- Failed sibling run `33943117001` was diagnosed as duplicate-run shared-app cleanup race; no Gate-2 rerun justified.
- Dormant Gate-2 workflow is manual-only, serialized, and per-run isolated.

### Gate 3A — NORMAL-ROUTING COMPOSITION / GREEN / CLOSED

- Gate source `analyzer/v143_normal_routing_e2e_structure_gate.py` blob `cd5be6b27718187d5a2bc7b21e81356a6be67b79`.
- Workflow run `33945157629`, job `101249801382`: SUCCESS.
- Artifact `9963085825`, digest `sha256:9084a0d17ca44154e66a89f78546b6e210e3a302110e9e560c99b9f20a39ad09`, `allPassed=true`.
- All 9 pinned source Git-blob identities matched.
- Proven chain: Vercel Rhythm-only selection/private Blob handoff/fail-closed runtime safety → HTTP bridge → live Rhythm worker → request adapter → Rhythm-only router → deterministic stem provider → independent direct/cascade stem bundle → deterministic wrapper → exact Gate-2-proven scheduler blob.
- Lead/Bass legacy fallback preserved; restricted/reference-scoring import hits none.
- Fixture/model/Modal/GPU activity `0`; reference inputs `0`; score calls `0`; quality verdict `false`; persistence `false`.

## Normal-routing promotion evidence decision — GREEN / CLOSED

Decision record: `docs/checkpoints/V143_NORMAL_ROUTING_PROMOTION_DECISION.md`, commit `08c9a98f38b1ca0e23bd9408b8a15bf0713fd7ff`.

**Decision: `MODEL_BEARING_E2E_NOT_JUSTIFIED`.**

Gate 1 proves candidate structure, Gate 2 proves exact model/runtime behavior for that scheduler blob, and Gate 3A proves the exact normal-routing source composition reaches that same scheduler while preserving Lead/Bass and anti-leakage boundaries. Another pre-deploy model-bearing run would repeat Gate-2 computation; its only genuinely new properties would be deployment/environment/network/Blob reachability, which belong to the actual integration/deployment verification boundary.

Therefore:

- Gate 1: GREEN/CLOSED
- Gate 2: GREEN/CLOSED
- Gate 3A: GREEN/CLOSED
- Additional pre-deploy model-bearing E2E: NOT JUSTIFIED / DO NOT RUN
- **Normal-routing pre-production promotion evidence boundary: GREEN / CLOSED**

## NEXT STEP — production integration planning only

1. Compare `v143-contextual-prune-lobo` against the current production/main baseline and enumerate the exact candidate files/commits that would be integrated.
2. Define deployment order, rollback points, and no-model deployment smoke/routing checks.
3. Do not merge or deploy merely as part of planning; checkpoint the plan first.

### Hard stops

- No reference-facing scoring or quality verdict.
- No GOAT restricted bytes; no sealed GuitarSet `00/01/03`; no SplitMySong reopening.
- No closed performance/cache/concurrency reruns absent a demonstrated invalidating change.
- No Gate-2 approved-fixture rerun.
- No additional model-bearing normal-route run absent a demonstrated unique property.
- No weakening exact parity/fail-closed criteria.
- No persistent user-audio/stem/result retention without explicit permission.
- **No production bridge/worker/Vercel/UI change or `main` merge until the exact integration/deploy plan is checkpointed.**
