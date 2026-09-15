# Songsterr Fresh — Purpose-Built Capture Manifest V2.3 Structural-Audit Input Binding Preregistration

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: FROZEN BEFORE IMPLEMENTATION / SYNTHETIC CI ONLY

## Purpose

Freeze one narrow additive version over accepted capture-manifest V2.2 so each admitted capture reference and the admitted-population identity commit to the exact future reference-blind structural-audit input byte identities for that same admitted performance.

This preregistration responds only to the end-to-end identity gap documented in:
`docs/checkpoints/SONGSTERR_FRESH_END_TO_END_REFERENCE_DECLARATION_IDENTITY_REVIEW_V1_2026-09-14.md`, commit `e3e1759b576831128ff0b95ee237b6d131a2fe51`.

V2.3 does not create structural truth, decode reference evidence, open structural-audit files, inspect evaluated audio, change calibration, change retry/acquisition QA, or authorize correctness. It is declaration identity plumbing only.

No real hardware, real calibration, real holdout capture, Basic Pitch, V6, correctness, protected-song material, reserved Guitar Fretboard Notes source, archived V143/Gomyway material, network retrieval, or evaluated-audio-derived truth is authorized.

## Frozen authority

V2.3 inherits without weakening:

- capture-manifest V2.1 retry/acquisition semantics and software gate;
- accepted V2.2 preregistration commit `9596bfc745a5acdbb47b403eb3d39688ceb20ebd`;
- accepted V2.2 implementation commit `e3e3ae05ab0ab4a94a77e6c6e5be2466f618cf46`;
- V2.2 result checkpoint commit `7d2d05ec365bbdb1aced574f7caf1865795fbc23`;
- Provenance V1 result checkpoint `c57156fec7c5000563552c8cb128366956b8c95b`;
- physical-reference semantics commit `ea5f50212cd1cd3794c65cb648a4d781e49e4082`;
- inherited timing bound `0.025 s`.

## Contract identities

Top-level V2.3 contract literal:
`songsterr-fresh-purpose-built-capture-manifest-v2.3`

Per-admitted structural-input binding contract literal:
`songsterr-fresh-purpose-built-structural-audit-input-binding-v1`

V2.3 population identity version literal:
`capture-manifest-v2.3-structural-audit-input-binding-v1`

Frozen structural event-semantics literal:
`physical-reference-semantics-v1`

## Additive admitted-reference fields

Every admitted attempt's existing `reference` object must add exactly these V2.3 fields:

- `structuralAuditInputs`: object defined below;
- `structuralAuditInputsSha256`: lowercase 64-hex SHA-256 equal to `SHA256(canonical_json(structuralAuditInputs))`.

Canonical JSON uses sorted keys, compact separators, UTF-8, and rejects NaN/non-finite JSON values.

Failed/non-admitted attempts must not carry either `structuralAuditInputs` or `structuralAuditInputsSha256`. V2.3 does not permit post-failure structural output declaration for a take that was never admitted.

## Frozen `structuralAuditInputs` object

For each admitted attempt the object must contain all fields below.

### Binding contract and admitted-performance identity

- `contract`: exact structural-input binding contract literal;
- `attemptId`: exact enclosing admitted attempt ID;
- `slotId`: exact enclosing slot ID;
- `underlyingPerformanceId`: exact enclosing underlying-performance ID;
- `playerId`: exact enclosing player ID;
- `exerciseId`: exact enclosing exercise ID;
- `category`: exact enclosing category.

### Exact future structural-audit byte identities

All are lowercase 64-hex SHA-256 identities for the exact future raw byte streams that Structural Audit V1.2 is expected to consume:

- `hardwareSourceSha256`;
- `birthStreamSha256`;
- `pitchLatchStreamSha256`;
- `clockSyncSourceSha256`.

V2.3 does not open those files and does not claim they are the same bytes as raw sensor evidence.

### Hardware / instrument identity

- `configurationId`: exact `corpus.hardware.configuration.configurationId`;
- `configurationSha256`: exact `corpus.hardware.configuration.sha256`;
- `instrumentSetupSha256`: exact `corpus.hardware.instrumentSetup.setupSha256`;
- `openStringMidi`: exact six-value `corpus.hardware.instrumentSetup.openStringMidi` list; each value integer 0..127; exact order preserved.

### Calibration / clock / semantics identity

- `calibrationId`: exact `corpus.referenceCalibration.calibrationId`;
- `clockSyncId`: exact `corpus.clockSync.syncId`;
- `eventSemanticsVersion`: exact literal `physical-reference-semantics-v1`, and equal to the enclosing admitted `reference.eventSemanticsVersion`.

No equality between `clockSyncSourceSha256` and `corpus.clockSync.sha256` is required because the frozen contracts do not establish that the capture clock artifact and structural-audit clock JSON stream are the same byte object. They are linked semantically through `clockSyncId`.

### Source-evidence lineage

- `pitchEvidenceSha256`: exact enclosing admitted `reference.pitchEvidenceSha256`, which already equals the admitted attempt `pitchEvidence.sha256` under inherited V2/V2.2 validation;
- `birthEvidenceSha256`: exact enclosing admitted `reference.birthEvidenceSha256`, which already equals the admitted attempt `birthEvidence.sha256`;
- `referenceArtifactSha256`: exact enclosing admitted `reference.sha256`.

These fields distinguish raw independent evidence/reference identities from later deterministic decoded structural streams.

### Package / decoder lineage

- `calibrationPackageBindingSha256`: exact enclosing admitted `reference.calibrationPackageBindingSha256`, which under V2.2 equals `corpus.referenceCalibrationPackage.packageBindingSha256`;
- `derivationConfigurationSha256`: exact enclosing admitted `reference.derivationConfigurationSha256`, which under V2.2 equals the bound package decoder-configuration SHA.

## Frozen V2.3 cross-checks

V2.3 must inherit/call V2.2 first. It must then fail closed unless every admitted attempt has a valid structural binding and every binding field matches the already-validated V2.2 declaration exactly.

V2.3 must not repair, infer, normalize, or derive a missing identity from evaluated audio or later structural-audit results.

The four new structural source SHA values are declarations of future deterministic output bytes. They are not validated by opening files in V2.3. Their later byte verification belongs to Structural Audit V1.2.

## Frozen admitted-population identity

V2.3 preserves V2.2's admitted-population SHA as:

`inheritedV22AdmittedPopulationManifestSha256`.

For every admitted attempt, create one V2.3 structural-binding row containing exactly:

- `attemptId`;
- `slotId`;
- `underlyingPerformanceId`;
- `structuralAuditInputsSha256`.

Sort rows by `(slotId, attemptId)` as strings.

Compute the new V2.3 admitted-population SHA as:

`SHA256(canonical_json({
  "populationIdentityVersion": "capture-manifest-v2.3-structural-audit-input-binding-v1",
  "inheritedV22AdmittedPopulationManifestSha256": <V2.2 SHA>,
  "structuralAuditInputBindings": <sorted rows>
}))`

Expose that new SHA as V2.3 `admittedPopulationManifestSha256`.

This makes the admitted capture population commit to the exact canonical structural-input binding for each admitted performance without changing any existing V2.2 population field.

## Frozen result fields

A deterministic V2.3 result must include at least:

- `contract`;
- `contractValid`;
- sorted `errors`;
- inherited V2.2 package/provenance/decoder identity fields unchanged;
- `structuralAuditInputBindingContract`;
- `structuralAuditInputBindingCount`;
- `populationIdentityVersion`;
- `inheritedV22AdmittedPopulationManifestSha256`;
- new V2.3 `admittedPopulationManifestSha256`;
- `mayAdvanceToReferenceBlindStructuralAudit` true only when V2.2 passes and all V2.3 admitted bindings pass;
- all downstream authorization false/zero.

V2.3 may expose a deterministic sorted map/list of admitted attempt IDs to `structuralAuditInputsSha256` for audit handoff, but it must not include evaluated-audio bytes or model/correctness data.

## Synthetic contract tests before official harness

Tests must run before official synthetic harness execution and cover at minimum:

1. complete V2.3 synthetic manifest PASS;
2. valid V2.2 projection FAILS V2.3 until admitted structural binding is present;
3. missing/mismatched structural binding contract FAIL;
4. missing/malformed `structuralAuditInputsSha256` FAIL;
5. canonical structural binding hash mismatch FAIL;
6. malformed each of the four structural source SHA identities FAIL;
7. admitted attempt/slot/underlying-performance identity mismatch FAIL;
8. admitted player/exercise/category identity mismatch FAIL;
9. hardware configuration ID mismatch FAIL;
10. hardware configuration SHA mismatch FAIL;
11. instrument-setup SHA mismatch FAIL;
12. `openStringMidi` mismatch or invalid shape/value FAIL;
13. calibration ID mismatch FAIL;
14. clock-sync ID mismatch FAIL;
15. event-semantics value not exact frozen literal or mismatch to reference FAIL;
16. pitch-evidence SHA mismatch FAIL;
17. birth-evidence SHA mismatch FAIL;
18. reference-artifact SHA mismatch FAIL;
19. calibration-package binding SHA mismatch FAIL;
20. derivation-configuration SHA mismatch FAIL;
21. failed/non-admitted attempt carrying structural binding FAIL;
22. inherited V2.2 package/reference rules remain enforced;
23. V2.3 population SHA changes when any admitted structural source SHA changes;
24. V2.3 population SHA changes when an admitted binding identity changes;
25. inherited V2.2 admitted-population SHA remains unchanged when only V2.3 structural output hashes change;
26. canonical V2.3 validation output is byte-deterministic;
27. all downstream authorization remains false/zero on PASS.

## Official synthetic harness

Ordinary GitHub CPU workflow must:

1. compile V2.3 implementation/tests;
2. run all synthetic tests first;
3. only after tests pass, generate one frozen V2.3 synthetic manifest from the accepted V2.2 fixture plus deterministic synthetic future structural source SHA declarations;
4. run V2.3 validator;
5. print inherited V2.2 population SHA, admitted structural binding SHA(s), V2.3 population SHA, package/provenance identity summary, and closed authorization state;
6. upload the canonical V2.3 result artifact.

No network access, media acquisition, model execution, or external corpus access is permitted.

## Interpretation boundary

A synthetic V2.3 PASS proves only that an admitted synthetic capture/reference declaration and its population identity now commit to exact future structural-audit byte identities and the relevant configuration/calibration/setup/clock/evidence/package/decoder lineage.

It does not prove those future structural files exist, that their contents are structurally valid, that physical sensing works, that real calibration passes, or that correctness/customer delivery is authorized.

Only after V2.3 is complete may a separately frozen Structural Audit V1.2 consume actual structural bytes and prove they match this binding.

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
2. Update canonical current-state checkpoint.
3. Implement V2.3 strictly as an additive wrapper over accepted V2.2.
4. Add synthetic tests before official harness execution.
5. Add ordinary GitHub CPU workflow with tests first.
6. Freeze run/job/artifact/result identities in a dedicated V2.3 result checkpoint.
7. Update canonical current-state checkpoint.
8. Only then preregister Structural Audit V1.2 against the exact frozen V2.3 shape.
