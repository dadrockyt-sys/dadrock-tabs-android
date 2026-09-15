# Songsterr Fresh — Purpose-Built Capture Manifest V2.2 Calibration-Package Bridge Preregistration

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: FROZEN BEFORE IMPLEMENTATION / SYNTHETIC CI ONLY

## Purpose

Freeze one narrow additive version over capture-manifest V2.1 so a future admitted capture population can be immutably linked to the already-frozen Reference Calibration Package Provenance V1 canonical package identity.

This preregistration responds only to the identity-linkage gap documented in:
`docs/checkpoints/SONGSTERR_FRESH_CAPTURE_MANIFEST_CALIBRATION_PACKAGE_BRIDGE_REVIEW_V1_2026-09-14.md`.

V2.2 does not redesign calibration, reference decoding, capture chronology, retry semantics, acquisition QA, structural audit, V6, scoring, policy, or customer delivery.

No real hardware, real calibration, real holdout capture, Basic Pitch, V6, correctness, protected-song material, reserved Guitar Fretboard Notes source, archived V143/Gomyway material, network retrieval, or evaluated-audio-derived truth is authorized.

## Frozen authority

V2.2 inherits without weakening:
- capture-manifest V2.1 implementation and semantics;
- physical-reference semantics commit `ea5f50212cd1cd3794c65cb648a4d781e49e4082`;
- inherited timing bound `0.025 s`;
- Reference Calibration Package Provenance V1 contract commit `cbd99714f655d859af2410374c3245a4afe6b056`;
- completed Provenance V1 result checkpoint commit `c57156fec7c5000563552c8cb128366956b8c95b`;
- bridge review commit `abfd10ea953e2be313f847f626c405a2f3607dad`.

## Contract identity

Top-level V2.2 contract literal:
`songsterr-fresh-purpose-built-capture-manifest-v2.2`

Calibration-package contract literal:
`songsterr-fresh-purpose-built-reference-calibration-package-v1`

V2.2 is declaration-only. It must not open evaluated audio, raw reference streams, calibration-package files, provenance-result files, or any external corpus. It must not use network access or model output.

## Frozen additive corpus field

A V2.2 manifest must contain `corpus.referenceCalibrationPackage` as an object with exactly these required semantic members:

- `contract`: exact calibration-package contract literal above;
- `validationResultPath`: nonempty safe relative POSIX path identifying the already-produced provenance validation-result artifact;
- `validationResultSha256`: lowercase 64-hex SHA-256 of that validation-result artifact;
- `packageBindingSha256`: lowercase 64-hex canonical package-binding SHA-256 produced by Provenance V1;
- `packageBinding`: the canonical semantic binding object from the successful Provenance V1 result.

The bridge validator does not read `validationResultPath`; the path/hash pair is immutable identity plumbing for later byte verification. `validationResultPath` must reject absolute paths, backslashes, empty/`.`/`..` components, and traversal semantics.

## Frozen canonical package-binding verification

V2.2 must compute:

`SHA256(canonical_json(packageBinding))`

using sorted keys, compact separators, UTF-8, no NaN, and require exact equality with `packageBindingSha256`.

The package binding object must minimally expose compatible identity fields already frozen by Provenance V1:
- exact `contract` literal;
- nonempty `calibrationId`;
- `usedHoldoutData:false`;
- `usedModelOutputs:false`;
- `derivedFromEvaluatedAudio:false`;
- finite nonnegative `maxAbsoluteOnsetErrorSeconds <= 0.025`;
- `hardwareConfiguration.configurationId` nonempty;
- `hardwareConfiguration.sha256` valid SHA-256;
- `instrumentSetupSha256` valid SHA-256;
- `decoder.decoderId` nonempty;
- `decoder.softwareVersion` nonempty;
- `decoder.code.sha256` valid SHA-256;
- `decoder.configuration.sha256` valid SHA-256.

V2.2 does not duplicate the full provenance-package validator. It verifies only the canonical binding identity plus the shared compatibility fields required to link capture-manifest declarations to that already-validated package.

## Frozen cross-contract compatibility checks

The V2.2 bridge must fail closed unless all are true:

1. `packageBinding.calibrationId` equals `corpus.referenceCalibration.calibrationId`.
2. `packageBinding.hardwareConfiguration.configurationId` equals `corpus.hardware.configuration.configurationId`.
3. `packageBinding.hardwareConfiguration.sha256` equals `corpus.hardware.configuration.sha256`.
4. `packageBinding.instrumentSetupSha256` equals `corpus.hardware.instrumentSetup.setupSha256`.
5. `packageBinding.maxAbsoluteOnsetErrorSeconds` equals `corpus.referenceCalibration.maxAbsoluteOnsetErrorSeconds` exactly as a numeric value.
6. Both timing declarations remain finite, nonnegative and `<= 0.025` through inherited and bridge validation.
7. Package firewall declarations remain exactly false.

No new physical timing threshold is introduced.

## Frozen admitted-reference bridge

Every admitted attempt's `reference` object must add:
- `calibrationPackageBindingSha256`.

It must equal `corpus.referenceCalibrationPackage.packageBindingSha256` exactly.

Every admitted attempt's existing `reference.derivationConfigurationSha256` must equal `packageBinding.decoder.configuration.sha256`.

This is the frozen link from the per-take deterministic reference derivation to the decoder configuration already committed by the package binding.

No separate per-take decoder-code field is added. The per-take package-binding SHA commits to decoder code/configuration transitively and avoids duplicating the package contract.

## Frozen population identity change

V2.2 must recompute the admitted-population manifest SHA-256 using the same deterministic admitted-row ordering as V2/V2.1, while adding these fields to each admitted population row:
- `calibrationPackageBindingSha256`;
- `calibrationPackageValidationResultSha256`.

The V2.2 result must expose a population identity version literal:
`capture-manifest-v2.2-calibration-package-bridge-v1`.

The inherited V2/V2.1 admitted population identity may be retained as diagnostic metadata, but the V2.2 `admittedPopulationManifestSha256` must be the augmented V2.2 identity.

## Frozen inherited behavior

All V2.1 rules remain authoritative, including:
- same-slot retry continuity and cross-slot underlying-performance uniqueness;
- acquisition-QA vocabulary and machine-verifiable failure evidence;
- first-PASS/admission chronology;
- hardware independence declarations;
- pitch/birth evidence hash binding;
- clock-sync identity and timing bound;
- declared structural blocker behavior;
- reference-blind structural audit as the only next possible stage after a clean declaration contract;
- all policy/correctness/customer authorization remaining closed.

V2.2 must call/inherit V2.1 validation rather than reimplementing those rules.

## Frozen result fields

A deterministic V2.2 validation result must include at least:
- `contract`;
- `contractValid`;
- sorted `errors`;
- `packageBridgeValid`;
- `calibrationPackageBindingSha256`;
- `calibrationPackageValidationResultSha256`;
- `calibrationPackageDecoderId`;
- `calibrationPackageDecoderSoftwareVersion`;
- `calibrationPackageDecoderCodeSha256`;
- `calibrationPackageDecoderConfigurationSha256`;
- `populationIdentityVersion`;
- augmented `admittedPopulationManifestSha256`;
- inherited admitted population count and underlying-performance count;
- `mayAdvanceToReferenceBlindStructuralAudit` only when inherited V2.1 validation and all V2.2 bridge checks pass and no inherited structural blocker prevents advance;
- all inherited downstream authorization fields forced false/zero.

## Synthetic contract tests before official harness

Tests must run before official synthetic harness execution and cover at minimum:

1. a complete V2.2 synthetic manifest passes;
2. V2.1 valid fixture projected to V2.2 fails until the new bridge fields are added;
3. canonical package-binding hash mismatch fails;
4. malformed package binding SHA fails;
5. malformed validation-result SHA fails;
6. unsafe validation-result path fails;
7. package contract mismatch fails;
8. package firewall violation fails;
9. package calibration ID mismatch fails;
10. package hardware configuration ID mismatch fails;
11. package hardware configuration SHA mismatch fails;
12. package instrument setup SHA mismatch fails;
13. package timing declaration mismatch fails;
14. package timing above `0.025` fails;
15. missing decoder identity/version fails;
16. malformed decoder code SHA fails;
17. malformed decoder configuration SHA fails;
18. admitted reference missing/mismatched `calibrationPackageBindingSha256` fails;
19. admitted reference derivation configuration mismatch to package decoder configuration fails;
20. failed/non-admitted attempts are not required to carry the admitted-reference bridge;
21. same-slot retry/cross-slot uniqueness inherited from V2.1 remains enforced;
22. V2.2 augmented population SHA changes if package binding or validation-result SHA identity changes;
23. canonical validation output is byte-deterministic;
24. all authorization fields remain false/zero.

## Synthetic official harness

The ordinary GitHub CPU workflow must:
1. compile implementation/tests;
2. run all synthetic contract tests first;
3. only if tests pass, validate the frozen generated V2.2 synthetic manifest;
4. print canonical bridge/population hashes and closed authorization summary;
5. upload the canonical validation result artifact.

No network data acquisition or external corpus access is permitted.

## Interpretation boundary

A synthetic V2.2 PASS proves only that the capture-manifest declaration can immutably link admitted reference declarations/population identity to an already-validated calibration package binding under the frozen synthetic fixture.

It does not prove:
- that a real calibration package exists;
- that a provenance validation-result artifact has yet been byte-verified by the structural audit;
- physical decoder accuracy;
- sensor accuracy or hardware qualification;
- real calibration PASS;
- real holdout capture authority;
- structural suitability;
- Basic Pitch/V6 correctness;
- customer eligibility or delivery authority.

After V2.2 is complete, a separate review must determine whether the existing reference-blind structural audit needs an additive bridge to hash-before-parse verify the bound provenance validation-result bytes. Do not implement that audit change until reviewed and preregistered separately.

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

Reserved GFN `deb` / `ele_natural` remain untouched. Archived V143/Gomyway remains closed.

## Execution order

1. Commit this preregistration before implementation.
2. Update the canonical current-state checkpoint.
3. Implement V2.2 strictly as frozen here.
4. Add synthetic tests before official harness execution.
5. Add ordinary GitHub CPU workflow with tests first.
6. Freeze run/job/artifact/result identities in a dedicated V2.2 result checkpoint.
7. Update the canonical current-state checkpoint again.
