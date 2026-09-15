# Songsterr Fresh — Reference-Blind Structural Audit Provenance-Result Bridge Review V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: REVIEW COMPLETE / NARROW BYTE-VERIFICATION GAP CONFIRMED

## Scope

This review follows completion of capture-manifest V2.2 calibration-package identity bridging. It asks only whether the existing reference-blind structural-audit V1 contract already hash-before-parse verifies the calibration-provenance validation-result bytes bound by V2.2, and whether it proves that the parsed provenance result commits to the same canonical calibration package identity as the admitted capture population.

This is review/documentation only. It does not authorize real calibration, real hardware, real holdout capture, Basic Pitch, V6, correctness, protected-song material, reserved Guitar Fretboard Notes sources, customer delivery, or archived V143/Gomyway work.

## Authority reviewed

- structural-audit V1 preregistration commit `067875e3aa1538ff5483b74cc9071b00e9e82b07`;
- structural-audit V1 implementation/test/workflow integration head `8f4b41ce2cff075a6e7be25032142a0e8288b7be`;
- structural-audit V1 synthetic evidence checkpoint commit `df7eb9edacb170ab24e2c200b1c0a8028625f87a`;
- capture-manifest V2.2 preregistration commit `9596bfc745a5acdbb47b403eb3d39688ceb20ebd`;
- accepted V2.2 implementation commit `e3e3ae05ab0ab4a94a77e6c6e5be2466f618cf46`;
- V2.2 result checkpoint commit `7d2d05ec365bbdb1aced574f7caf1865795fbc23`;
- Reference Calibration Package Provenance V1 result checkpoint commit `c57156fec7c5000563552c8cb128366956b8c95b`.

## What structural-audit V1 already guarantees

Structural-audit V1 is strongly reference-blind and fail-closed within its frozen scope:

- it accepts exactly four independent reference-side JSON byte streams: `hardware`, `birth`, `pitchLatch`, `clockSync`;
- it requires exactly one expected SHA-256 identity for each of those four streams;
- it hashes all four raw byte streams before any JSON parse;
- any source hash mismatch fails immediately;
- it has no evaluated-audio, Basic Pitch, V6, correctness, precision/recall, model-score, or model-output input path;
- it checks calibration/model/audio-derived provenance flags in the hardware/reference declarations;
- it checks the inherited `0.025 s` timing bound, clock sync, event identity, one-to-one birth/latch structure, physical string agreement, fret/MIDI validity, overlap blockers, and immutable derived-note population identity;
- a structural PASS still leaves Basic Pitch/V6/correctness/customer/delivery authorization false.

These properties remain authoritative and must not be weakened.

## What V2.2 newly binds

Capture-manifest V2.2 now commits each admitted reference and the augmented admitted-population identity to:

- a safe relative provenance validation-result path;
- the exact provenance validation-result SHA-256;
- the canonical calibration `packageBindingSha256`;
- the decoder configuration SHA-256 through each admitted reference's `derivationConfigurationSha256`;
- an augmented population SHA that includes both the provenance result SHA and package binding SHA.

The accepted synthetic V2.2 result bound:

- provenance result SHA-256 `4fd62e62a855031bd3c189253bc04f004d271d53bf2b636c586c15b93e59e98f`;
- package binding SHA-256 `735d276afc5bac7cd8e0e905ae42f8d4dc4bfae835ae013403ccdc31c4cf857c`.

## Confirmed gap

Structural-audit V1 predates Provenance V1 and capture-manifest V2.2. Its frozen contract explicitly consumes **exactly four** raw reference-side byte streams and its `SOURCE_NAMES` set is exactly:

- `hardware`;
- `birth`;
- `pitchLatch`;
- `clockSync`.

It rejects extra source names.

Therefore V1 cannot currently:

1. accept the V2.2-bound provenance validation-result byte stream;
2. verify its expected SHA-256 before parsing;
3. verify that the parsed result is the exact Provenance V1 result contract and has `contractValid:true` with `errors:[]`;
4. verify that the parsed result's `packageBindingSha256` equals the package binding SHA committed by the admitted capture population;
5. verify that the provenance-result SHA used by the audit equals the SHA committed by V2.2;
6. include those provenance identities in the structural-audit result/population binding.

Thus a capture-manifest V2.2 declaration and a structural-audit V1 PASS can each be internally valid while the structural auditor never byte-verifies the provenance result that V2.2 says is authoritative.

This is a narrow identity/provenance byte-verification gap. It is not a new physical threshold, reference-semantics, or correctness gap.

## Decision

A prospective **reference-blind structural-audit V1.1 provenance-result bridge** is required before any future real V2.2-bound population can use structural-audit PASS as an authoritative structural-suitability gate.

The bridge must be additive over V1. It must preserve V1's four original byte streams and all existing zero-anomaly structural rules exactly. It must add one separate provenance-result byte stream and its expected SHA-256, verify that fifth stream before parsing, and cross-bind the parsed provenance identity to the V2.2-declared package/result identities.

The bridge must not:

- change `0.025 s` timing bounds;
- change physical note-event semantics;
- change overlap, matching, range, clock, provenance, or zero-anomaly blocker rules;
- read evaluated DI/audio;
- use model output or correctness data;
- re-open calibration package files themselves;
- duplicate the Provenance V1 package validator;
- authorize Basic Pitch/V6/correctness/customer delivery.

## Required bridge semantics for preregistration

A separately frozen V1.1 preregistration should require, before implementation:

1. inherit/call structural-audit V1 for the original four streams;
2. accept a fifth raw byte stream named `calibrationProvenanceResult` plus expected SHA-256;
3. hash the fifth raw stream before any JSON parse and fail closed on mismatch;
4. require exact result contract `songsterr-fresh-purpose-built-reference-calibration-package-provenance-v1`;
5. require parsed `contractValid:true` and `errors:[]`;
6. require parsed `packageBindingSha256` to be a valid SHA-256 and equal the V2.2-declared package binding SHA;
7. require the fifth stream expected/actual SHA to equal the V2.2-declared provenance validation-result SHA;
8. require parsed package firewall/authorization-relevant declarations to remain compatible with reference-blind use; no holdout/model/evaluated-audio-derived calibration provenance may be accepted;
9. expose the verified provenance-result SHA and package binding SHA in the V1.1 result;
10. augment the structural derived-population identity with those two provenance identities without altering derived note events;
11. preserve all authorization false/zero even on PASS.

The V1.1 bridge may receive the two V2.2 expected identities as declaration parameters/metadata. It must not infer them from evaluated audio or correctness data.

## Required next order

1. Commit this review before any audit bridge implementation.
2. Update the canonical current-state checkpoint.
3. Freeze a V1.1 provenance-result bridge preregistration before code.
4. Implement as a narrow wrapper/additive validator over V1.
5. Add synthetic tests before official harness execution.
6. Run ordinary GitHub CPU synthetic CI only.
7. Freeze run/job/artifact/result identities in a dedicated checkpoint.
8. Update the canonical current-state checkpoint after meaningful stages.

## Authorization boundary

Unchanged:

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Reserved GFN `deb` / `ele_natural` remain untouched. Archived V143/Gomyway remains closed.
