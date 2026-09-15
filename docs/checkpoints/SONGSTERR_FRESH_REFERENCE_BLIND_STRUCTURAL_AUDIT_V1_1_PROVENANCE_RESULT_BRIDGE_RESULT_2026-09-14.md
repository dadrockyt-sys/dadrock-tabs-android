# Songsterr Fresh — Reference-Blind Structural Audit V1.1 Provenance-Result Bridge Result

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: SYNTHETIC CONTRACT PASS / PROVENANCE BYTE BRIDGE COMPLETE

## Authority

Gap review:
`docs/checkpoints/SONGSTERR_FRESH_REFERENCE_BLIND_STRUCTURAL_AUDIT_PROVENANCE_BRIDGE_REVIEW_V1_2026-09-14.md`
commit `66b1d3d19913e5218c3f1a71a88b399241ea5350`.

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_REFERENCE_BLIND_STRUCTURAL_AUDIT_V1_1_PROVENANCE_RESULT_BRIDGE_PREREGISTRATION_2026-09-14.md`
commit `d69defc153d06afe69ad6d1a9eb681f2ba1ff24a`.

Pre-implementation preregistration correction:
`docs/checkpoints/SONGSTERR_FRESH_REFERENCE_BLIND_STRUCTURAL_AUDIT_V1_1_PREREGISTRATION_CORRECTION_1_2026-09-14.md`
commit `3839d43dae9881fb2c98a5cac7c6f0b634eb944c`.

The correction changed only the exact accepted Provenance V1 result contract literal to the already-frozen actual contract:
`songsterr-fresh-purpose-built-reference-calibration-package-v1`.
No V1.1 implementation or result ran before that correction.

## Accepted implementation / tests / workflow

Implementation:
- file `scripts/songsterr-fresh/purpose_built_reference_blind_structural_audit_v1_1.py`;
- commit `5bf98194cdc2045c99903d3f9229443061deec2d`;
- blob/content SHA `77ef2959d3c277e020cbddea9a9943a5ed8fb292`.

Synthetic tests:
- file `scripts/songsterr-fresh/test_purpose_built_reference_blind_structural_audit_v1_1.py`;
- commit `a05cb02b674572144af637dfc43fe989a54934c8`;
- blob/content SHA `c8bd28064296daa0a44160140eccbbbe58692d5a`.

Workflow:
- file `.github/workflows/songsterr-fresh-purpose-built-reference-blind-structural-audit-v1-1.yml`;
- integration head `ee3a4d64ec506e8342333ff2c0c218b6b40ad7f9`;
- blob/content SHA `a25bd14f69b591200be49c0fc4f82ce00f1766f0`.

## Official GitHub CPU run

- workflow run `34918145384`;
- job `104220137547` (`synthetic-reference-blind-structural-audit-v11`);
- head SHA `ee3a4d64ec506e8342333ff2c0c218b6b40ad7f9`;
- conclusion `success`;
- Python `3.12.14` on ordinary GitHub-hosted Ubuntu CPU;
- compile: PASS;
- synthetic tests executed before official harness;
- test result: **27/27 PASS**;
- synthetic V1 reference-stream generation: PASS;
- synthetic Provenance V1 result generation: PASS;
- official V1.1 validator: PASS;
- result summary: PASS;
- artifact upload: PASS.

Artifact:
- name `songsterr-fresh-purpose-built-reference-blind-structural-audit-v1-1`;
- artifact ID `10376674616`;
- uploaded ZIP size `1,439` bytes;
- uploaded ZIP SHA-256 `7b47cbd2a641579915a0627328a9183444b227b9d7cd97595e11e928124e3387`;
- canonical result JSON SHA-256 `11667ec86bbe22a14a22d7bfa46e96596cb07694fc58152d39591c5cf932f34d`.

## Frozen synthetic result

Top-level:
- `contract`: `songsterr-fresh-purpose-built-reference-blind-structural-audit-v1.1`;
- `contractValid:true`;
- `datasetStructurallySuitable:true`;
- `authoritativeStructuralSuitabilityEstablished:true` for the frozen synthetic fixture only;
- `calibrationProvenanceBridgeViolationCount:0`;
- `errors:[]`;
- all inherited V1 blocker counts `0`;
- `derivedNoteEventCount:2`.

Original four V1 source hashes all matched before V1 parsing:
- hardware SHA `b6b9d8a58f2dc5adc7659d81477e8af7829d99f1b393431e7a4ffa62eb5d96c4`;
- birth SHA `d2ae5e0c4d8080cb59a86c13651649e7b4dc587323ae3df36939db29c0885dac`;
- pitch-latch SHA `62328b8a8345737e62c4f802cf9a91124d57a64d42d6d671241025de8c477f96`;
- clock-sync SHA `e573bee10c30ad12de5b1a405fe9c8b01894a7cd389152278b0f6ea4149b487b`.

Fifth provenance result stream:
- expected SHA `4fd62e62a855031bd3c189253bc04f004d271d53bf2b636c586c15b93e59e98f`;
- actual SHA `4fd62e62a855031bd3c189253bc04f004d271d53bf2b636c586c15b93e59e98f`;
- `matches:true`;
- parsed contract `songsterr-fresh-purpose-built-reference-calibration-package-v1`;
- parsed successful package binding SHA `735d276afc5bac7cd8e0e905ae42f8d4dc4bfae835ae013403ccdc31c4cf857c`.

Verified bound decoder identity:
- decoder ID `synthetic-decoder-v1`;
- software version `1.0.0-synthetic`;
- decoder code SHA `56aecaa4ece3411f6833274c0323aafae0ffdbeb52ee2a1ad57903f216573aaf`;
- decoder configuration SHA `3c9850cdd5085c2dc5230211b18d3362b7f0cef2d23be19b9af3b456df9a2777`.

Population identity:
- inherited V1 derived population SHA `98ed182a3cf13c5263eb564e801ed7066eb6df3f4d6ddb28426e914a4e6ca4f5`;
- V1.1 population identity version `reference-blind-structural-audit-v1.1-provenance-bridge-v1`;
- augmented V1.1 derived population SHA `603f69c1fa716784e23767255b4305b82eb6bde6187859db645a883694ff08b6`.

The new population SHA commits to the unchanged V1 structural note population plus the verified Provenance V1 result SHA and verified canonical calibration-package binding SHA. It does not alter note events, onset/pitch semantics, the 0.025 s timing bound, MIDI rules, overlap blockers, or any V1 zero-anomaly rule.

## What the 27 tests establish

The accepted test suite covers the frozen contract including:
- complete V1.1 PASS;
- unchanged V1 source hashes, note-event count, V1 population SHA and blocker semantics;
- fifth-stream bytes/type/expected-hash gates;
- fifth-stream hash mismatch short-circuit before provenance JSON parse;
- malformed/mismatched V2.2 provenance/package declarations;
- invalid UTF-8/JSON after successful hash;
- provenance result contract, `contractValid`, and empty-error enforcement;
- parsed package-binding SHA validity, V2.2 identity equality and canonical binding hash equality;
- package firewall declarations;
- inherited <=0.025 s package timing bound;
- calibration ID and decoder identity/version/code/configuration SHA validity;
- original V1 source hash mismatch and original V1 structural blockers still fail independently;
- augmented population SHA changes with provenance-result or package-binding identity while inherited V1 population SHA stays unchanged;
- canonical output determinism;
- downstream authorization remains false/zero on PASS.

## Interpretation boundary

This PASS closes the **structural-audit -> V2.2-bound provenance-result byte identity** gap in synthetic software. It proves that the frozen synthetic audit:

1. preserves the original four reference-blind V1 byte streams and structural checks;
2. hash-verifies the fifth Provenance V1 result stream before parsing it;
3. verifies that the parsed successful provenance result commits to the same canonical package binding declared by V2.2;
4. binds both provenance identities into the structural population identity.

It does not prove physical sensing accuracy, real calibration validity, real hardware qualification, real holdout authority, structural suitability of a real captured population, Basic Pitch/V6 correctness, model validation, customer eligibility, or delivery authority.

## Authorization boundary

Unchanged after synthetic PASS:
- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched. Archived V143/Gomyway remains closed.
