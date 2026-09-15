# Songsterr Fresh — Reference Calibration Package Provenance Result V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: COMPLETE / SYNTHETIC SOFTWARE EVIDENCE ONLY

## Frozen authority

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_REFERENCE_CALIBRATION_PACKAGE_PROVENANCE_PREREGISTRATION_V1_2026-09-14.md`
commit `cbd99714f655d859af2410374c3245a4afe6b056`.

Implementation commit: `3dd1140650070342ab9fc4e177870fd39940a4e0`.
Implementation blob: `b6be3c98ce5a7da9ce6c5f5c19d9472549e1029a`.
Initial test commit: `d322915ce7790ed036f709c56b40e0afe866c072`.
Final test-correction commit: `3ff9980cad1d16d2621ae5d3bb9fbc9d9fb5955a`.
Final test blob: `eaf39e7898d112bb4cb78fdb7d8a85c0425c2be8`.
Workflow integration commit: `17c273ff0986c89101d6ff5cf49cb1f2e61eb9ba`.
Workflow blob: `b54fa2f18dc27b202fe724cdc780f909dfd64b67`.

The first workflow run correctly failed before official harness execution because the valid-fixture test expected 13 verified files while the frozen fixture actually contains 14. The implementation/contract was not changed. Only that test bookkeeping assertion was corrected from 13 to 14 at commit `3ff9980cad1d16d2621ae5d3bb9fbc9d9fb5955a`.

## Official GitHub CPU execution

Workflow: `Songsterr Fresh Reference Calibration Package Provenance V1`.
Official clean run: `34916853723`.
Job: `104216245975` (`synthetic-calibration-package`).
Head SHA: `3ff9980cad1d16d2621ae5d3bb9fbc9d9fb5955a`.
Conclusion: SUCCESS.

Frozen execution order was preserved:
1. compile validator/tests;
2. run synthetic contract tests first;
3. run official generated synthetic package only after tests pass;
4. print deterministic summary;
5. upload canonical result.

Contract tests: 20/20 PASS.

Artifact:
- ID `10376481781`;
- name `songsterr-fresh-reference-calibration-package-provenance-v1`;
- uploaded size 1,919 bytes;
- ZIP SHA-256 `1a37a529b4c730315268bea21754275cbfb721a2c2238d4ae3fee6f54ad925e6`.

Canonical result JSON SHA-256:
`4fd62e62a855031bd3c189253bc04f004d271d53bf2b636c586c15b93e59e98f`.

Canonical synthetic package binding SHA-256:
`735d276afc5bac7cd8e0e905ae42f8d4dc4bfae835ae013403ccdc31c4cf857c`.

## Frozen result summary

Contract: `songsterr-fresh-purpose-built-reference-calibration-package-v1`.
`contractValid:true`.
`verifiedFileCount:14`.
`errors:[]`.

The synthetic package deterministically bound and byte-verified:
- hardware configuration identity;
- wiring topology identity;
- calibration fixture identity;
- decoder code identity;
- decoder configuration identity;
- four synthetic raw-source artifacts covering physical pitch state, event birth, clock sync and sensor health;
- five synthetic derived-output artifacts covering physical string/fret mapping, event-birth calibration, hardware timing proof, technique capability matrix and acquisition-QA configuration.

The valid fixture used the inherited `maxAbsoluteOnsetErrorSeconds = 0.025` boundary exactly. Synthetic tests separately confirmed values above `0.025` fail closed. No new physical timing threshold was created.

The synthetic tests also confirmed fail-closed behavior for firewall violations, malformed/mismatched hashes, missing files, absolute/traversal paths, duplicate package paths, duplicate hardware/raw identities, missing/unknown raw roles, missing/duplicate derived roles, missing decoder identity and missing hardware/fixture/topology/setup identity.

## Interpretation boundary

This result establishes only deterministic software behavior of the frozen calibration-package provenance contract on generated synthetic files. It shows that a future calibration package can be bound to a root-independent canonical identity while verifying declared package-file bytes and enforcing the already-frozen provenance firewall.

It does **not** establish:
- that any real calibration package exists;
- physical string/fret accuracy;
- physical event-birth accuracy;
- real clock drift/jitter/dropout performance;
- empirical acquisition-QA thresholds;
- hardware bench qualification;
- real calibration PASS;
- real holdout capture authority;
- external correctness;
- V6 readiness;
- customer eligibility or delivery authority.

Real calibration remains paused by the current budget checkpoint. The contract must not be changed from future holdout observations.

## Authorization boundary after result

Unchanged:
- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Reserved Guitar Fretboard Notes sources `deb` and `ele_natural` remain untouched. Archived V143/Gomyway remains closed.
