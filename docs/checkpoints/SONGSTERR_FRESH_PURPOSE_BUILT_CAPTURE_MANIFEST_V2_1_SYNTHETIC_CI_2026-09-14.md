# Songsterr Fresh — Purpose-Built Capture Manifest V2.1 Synthetic CI

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: synthetic declarations only; no candidate or holdout media; no Basic Pitch/V6/correctness.

## Decision

**PASS — V2.1 capture-manifest declaration gate is synthetic-CI qualified for the next reference-blind structural-audit tooling stage.**

This pass does **not** establish source truth, structural suitability, Basic Pitch authorization, V6 authorization, correctness authorization, model validation, customer eligibility, or delivery advancement.

## Authority / implementation chain

- Explicit user authorization to reopen/advance the purpose-built route is recorded in the canonical state at commit `9a464012b49a337cbd406badf290921ed0172f05`.
- Historical V2 implementation: `scripts/songsterr-fresh/purpose_built_capture_manifest_contract_v2.py`.
- V2.1 identity correction: `scripts/songsterr-fresh/purpose_built_capture_manifest_contract_v2_1.py`, commit `72e8861f50680f45e586eb1e1352db59bda1f0ae`.
- V2.1 synthetic tests: `scripts/songsterr-fresh/test_purpose_built_capture_manifest_contract_v2_1.py`, commit `ff5717a4aeb9b74e971694703f6d6cb785389845`.
- GitHub-hosted CPU workflow: `.github/workflows/songsterr-fresh-purpose-built-v2-1-synthetic.yml`.
- Final workflow-head commit: `3d7f1770a3b8df0018008a49defe189db306de39`.

## V2 contradiction found and disposition

The historical V2 validator rejects any repeated `underlyingPerformanceId` across attempts, while its own nominal valid fixture models a transport-failed first attempt followed by an admitted retry in the same frozen slot using the same underlying identity. That is internally inconsistent with retry continuity.

V2.1 preserves V2/V1 validation but replaces only that superseded global-duplicate rule with the intended semantics:

- attempts/retries within one frozen slot must retain the same `underlyingPerformanceId`;
- changing the underlying identity within a slot is invalid;
- reuse of the same underlying identity across distinct slots/population units is invalid;
- first-transport-valid-take chronology remains inherited from V1 and is not weakened.

The initial workflow run intentionally exposed the historical contradiction when it attempted to require the superseded V2 test suite to pass:

- run `34908849001`
- job `104191594458`
- conclusion `failure`
- failing stage: historical V1/V2/V2.1 combined synthetic tests.

The authoritative V2.1 CI gate was then corrected to test V1 plus V2.1, while V2 remains inherited implementation history rather than an independently authoritative contract. This is not a relaxation of the replacement rule; V2.1 adds explicit same-slot continuity and cross-slot uniqueness tests.

## Final synthetic CI result

- workflow: `Songsterr Fresh Purpose-Built V2.1 Synthetic`
- run ID: `34908936464`
- job ID: `104191861049`
- event: `push`
- head SHA: `3d7f1770a3b8df0018008a49defe189db306de39`
- conclusion: **success**

Successful stages included:

1. authoritative V1 and V2.1 synthetic contract tests;
2. explicit fail-closed authority assertion.

The fail-closed assertion requires a nominal V2.1 synthetic declaration to satisfy `contractValid:true` and `mayAdvanceToReferenceBlindStructuralAudit:true` while simultaneously requiring all of the following to remain false:

- `authoritativeStructuralSuitabilityEstablished`
- `basicPitchAuthorized`
- `v6Authorized`
- `correctnessAuthorized`

## Frozen meaning of this pass

V2.1 is now qualified only as a declaration/provenance gate preceding a future raw physical-reference structural audit. A real admitted holdout must still fail closed unless the independently captured pitch/birth evidence, clock/sync proof, hashes/configuration and event structure pass the separately frozen structural-audit contract.

No evaluated DI may be used to repair, disambiguate or tune physical reference truth. No model output may be used in acquisition QA, calibration, event reconstruction, structural rescue, or retake decisions.

## Next permitted action

Implement and synthetic-test the purpose-built **reference-blind physical-reference structural audit**. It must consume only frozen raw/reference declarations/streams and synchronization evidence, never evaluated audio or model/correctness output, and must fail closed on ambiguous/unmatched/impossible reference structure. Only after that tooling is frozen and synthetic-CI qualified should real calibration/procurement/acquisition become necessary.
