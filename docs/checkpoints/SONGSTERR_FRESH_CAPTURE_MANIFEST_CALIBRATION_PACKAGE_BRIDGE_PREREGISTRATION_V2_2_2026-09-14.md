# Songsterr Fresh — Capture-Manifest Calibration-Package Bridge Preregistration V2.2

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: FROZEN BEFORE V2.2 IMPLEMENTATION / RESULT EXECUTION

## Purpose

Freeze a narrow additive V2.2 purpose-built capture-manifest contract that closes the already-confirmed identity-linkage gap between:

1. the existing V2.1 capture-manifest calibration/reference declarations; and
2. one already-validated Reference Calibration Package Provenance V1 canonical package identity.

This bridge is declaration-only software. It does not re-open or re-verify calibration-package files, does not create a second decoder schema, and does not alter any physical, acquisition, structural, V6, correctness, policy, chronology, retry, or timing rule.

The confirmed-gap review is:
`docs/checkpoints/SONGSTERR_FRESH_CAPTURE_MANIFEST_CALIBRATION_PACKAGE_BRIDGE_REVIEW_V1_2026-09-14.md`
commit `abfd10ea953e2be313f847f626c405a2f3607dad`.

## Frozen authority

V2.2 is additive over:
- capture-manifest V2.1 implementation `scripts/songsterr-fresh/purpose_built_capture_manifest_contract_v2_1.py`;
- inherited V2 implementation `scripts/songsterr-fresh/purpose_built_capture_manifest_contract_v2.py`;
- Reference Calibration Package Provenance V1 preregistration commit `cbd99714f655d859af2410374c3245a4afe6b056`;
- Provenance V1 implementation commit `3dd1140650070342ab9fc4e177870fd39940a4e0`;
- Provenance V1 result checkpoint commit `c57156fec7c5000563552c8cb128366956b8c95b`;
- physical-reference semantics commit `ea5f50212cd1cd3794c65cb648a4d781e49e4082`.

No V2.1 or earlier rule may be weakened.

## Contract identity

Top-level V2.2 contract literal:
`songsterr-fresh-purpose-built-capture-manifest-v2.2`

Frozen package contract literal:
`songsterr-fresh-purpose-built-reference-calibration-package-v1`

V2.2 must validate an otherwise identical declaration through V2.1 after projecting only the top-level contract literal to the V2.1 literal. All inherited V2.1/V2/V1 errors remain binding.

## New corpus-level object

V2.2 requires `corpus.referenceCalibrationPackage` with exactly the following semantic fields:

- `contract`: exactly `songsterr-fresh-purpose-built-reference-calibration-package-v1`;
- nonempty `calibrationId`;
- valid lowercase 64-hex `packageBindingSha256`;
- valid lowercase 64-hex `validationResultSha256` identifying the already-produced provenance validation-result artifact bytes;
- `packageBinding`: the inline canonical semantic package-binding object produced by Provenance V1.

The V2.2 validator remains declaration-only: it does not open package files or the provenance validation-result artifact. It verifies only the inline object and declared cryptographic identities.

## Canonical package-binding verification

The bridge must deterministically canonicalize the inline `packageBinding` with the exact existing canonical JSON function inherited from the capture-manifest stack and require:

`SHA256(canonical_json(packageBinding)) == packageBindingSha256`.

The inline binding must be an object and must satisfy all of the following linkage checks:

- `packageBinding.contract` equals the frozen Provenance V1 package contract literal;
- `packageBinding.calibrationId` equals `corpus.referenceCalibrationPackage.calibrationId`;
- `packageBinding.calibrationId` also equals the existing legacy `corpus.referenceCalibration.calibrationId`;
- `packageBinding.hardwareConfiguration.sha256` equals the existing `corpus.hardware.configuration.sha256`;
- `packageBinding.instrumentSetupSha256` equals the existing `corpus.hardware.instrumentSetup.setupSha256`;
- `packageBinding.usedHoldoutData` is exactly `false`;
- `packageBinding.usedModelOutputs` is exactly `false`;
- `packageBinding.derivedFromEvaluatedAudio` is exactly `false`;
- `packageBinding.maxAbsoluteOnsetErrorSeconds` is finite, nonnegative, and exactly equal to the existing legacy `corpus.referenceCalibration.maxAbsoluteOnsetErrorSeconds`;
- the inherited `0.025 s` maximum remains enforced by V2.1/V2; V2.2 creates no new timing threshold;
- `packageBinding.decoder` is an object with nonempty `decoderId` and `softwareVersion`;
- `packageBinding.decoder.code.sha256` and `packageBinding.decoder.configuration.sha256` are valid lowercase 64-hex SHA-256 values.

V2.2 does not duplicate validation of all raw-source, fixture, wiring, topology, or derived-output package semantics; Provenance V1 owns those rules. Their identities remain protected because they are already inside the canonical package-binding hash.

## Legacy calibration declaration remains required

The existing `corpus.referenceCalibration` object remains unchanged and must continue to satisfy V2.1/V2, including its legacy contract literal:
`songsterr-fresh-purpose-built-reference-calibration-v1`.

V2.2 does not replace, reinterpret, or weaken that declaration. It cryptographically links it to the richer Provenance V1 package identity through matching calibration ID, timing/firewall declarations, hardware identity and canonical package-binding hash.

## Per-admitted-reference binding

Every attempt with `admitted:true` must contain a reference object field:

- `calibrationPackageBindingSha256`

It must be a valid lowercase 64-hex SHA-256 and must exactly equal the corpus-level `referenceCalibrationPackage.packageBindingSha256`.

Non-admitted attempts are not required to carry this field, preserving existing retry/acquisition chronology semantics.

## Admitted-population identity

V2.2 must produce a new deterministic `admittedPopulationManifestSha256` rather than reusing V2.1's value.

Its population rows must preserve the V2/V2.1 admitted-row identity fields and additionally include:
- `calibrationPackageBindingSha256`.

Rows remain sorted by `(slotId, attemptId)` before canonical hashing.

The V2.2 result must also expose:
- `calibrationPackageBindingSha256` at top level when validly declared;
- `calibrationPackageValidationResultSha256` at top level when validly declared;
- `calibrationPackageBridgeVersion: "capture-manifest-calibration-package-bridge-v1"`.

No other admitted-population identity field may be removed.

## Inherited semantics that must remain unchanged

V2.2 must not change:
- V1/V2/V2.1 chronology rules;
- allowed retry count or retry ordering;
- same-slot underlying-performance continuity;
- cross-slot underlying-performance uniqueness;
- acquisition-QA vocabulary or machine-verifiable failure evidence rules;
- structural-blocker semantics;
- `mayAdvanceToReferenceBlindStructuralAudit` meaning;
- hardware path independence;
- reference pitch/birth evidence rules;
- clock-sync rules;
- inherited `0.025 s` timing bound;
- policy boundary;
- Basic Pitch/V6/correctness rules;
- customer or delivery authorization.

## Fail-closed behavior

V2.2 must reject at minimum:
- wrong top-level V2.2 contract;
- any inherited V2.1 error;
- missing/malformed `referenceCalibrationPackage`;
- wrong package contract literal;
- missing/malformed calibration ID, package binding SHA or validation-result SHA;
- package-binding canonical hash mismatch;
- package-binding contract mismatch;
- calibration-ID mismatch between package declaration, inline package binding and legacy calibration declaration;
- hardware-configuration SHA mismatch;
- instrument-setup SHA mismatch;
- package firewall declaration mismatch;
- package/legacy timing declaration mismatch;
- invalid/missing decoder identity or decoder code/configuration SHA;
- missing/invalid/mismatched per-admitted-reference `calibrationPackageBindingSha256`.

No error may be rescued using evaluated audio, model outputs, musical correctness, future holdout observations, or archived V143/Gomyway material.

## Synthetic fixture and contract tests

Before official synthetic harness execution, tests must cover at minimum:

1. valid V2.2 fixture passes;
2. same-slot failed attempt -> admitted retry continuity from V2.1 still passes;
3. V2.1 chronology/identity/structural/policy failures still fail closed;
4. wrong/missing package object and contract fail;
5. malformed package-binding SHA and validation-result SHA fail;
6. canonical package-binding hash mismatch fails;
7. calibration ID mismatch at every linkage boundary fails;
8. hardware-configuration SHA mismatch fails;
9. instrument-setup SHA mismatch fails;
10. package firewall mismatch fails;
11. package timing mismatch fails;
12. missing/invalid decoder identity/code/config hash fails;
13. admitted reference missing package-binding SHA fails;
14. admitted reference package-binding mismatch fails;
15. non-admitted attempt may omit package-binding SHA;
16. admitted population SHA changes when package binding SHA changes while all earlier identity fields are held constant;
17. population SHA is deterministic under identical declarations;
18. all downstream authorization remains false/zero.

Synthetic tests may reuse the existing V2/V2.1 valid fixture and the frozen synthetic Provenance V1 package-binding values/shape. They must not access real calibration, holdout media, external corpora, reserved GFN sources, or protected-song material.

## Official synthetic CI order

1. compile V2.2 validator and tests;
2. run synthetic tests first;
3. run official deterministic synthetic V2.2 fixture only if tests pass;
4. upload canonical validation-result JSON;
5. freeze run/job/artifact/result identities in a dedicated result checkpoint.

## Interpretation boundary

A synthetic V2.2 PASS proves only that the capture-manifest declaration is deterministically linked to one canonical calibration-package identity under the frozen synthetic fixture. It does not prove that a real calibration package exists, that its contents are physically correct, that hardware qualifies, that a holdout can begin, that structural suitability is established, that V6 is correct, or that customer delivery is allowed.

After V2.2 completion, separately review whether the existing reference-blind structural-audit contract must verify the provenance validation-result artifact bytes and package binding. Do not assume or implement that extension before review.

## Authorization boundary

Must remain:
- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Reserved GFN `deb` and `ele_natural` remain untouched. Archived V143/Gomyway remains closed.
