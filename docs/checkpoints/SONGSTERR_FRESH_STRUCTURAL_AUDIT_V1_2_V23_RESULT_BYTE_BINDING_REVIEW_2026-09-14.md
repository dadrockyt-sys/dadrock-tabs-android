# Songsterr Fresh — Structural Audit V1.2 / V2.3 Result-Byte Binding Review

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: REVIEW COMPLETE / V2.3 RESULT-BYTE VERIFICATION REQUIRED

## Scope

Capture Manifest V2.3 now binds each admitted performance to one canonical `structuralAuditInputsSha256` and binds those hashes into its admitted-population identity. Before freezing Structural Audit V1.2, this review asks whether V1.2 may safely accept only copied V2.3 metadata, or whether it must also verify the exact successful V2.3 validation-result bytes.

No real hardware, calibration, holdout capture, Basic Pitch, V6, correctness, protected-song execution, reserved Guitar Fretboard Notes source, customer delivery, or archived V143/Gomyway work is authorized.

## Authority reviewed

- end-to-end declaration identity review commit `e3e1759b576831128ff0b95ee237b6d131a2fe51`;
- Capture Manifest V2.3 preregistration commit `c79fbd1d728a9d3dac86f036998108cb9765628e`;
- accepted V2.3 implementation commit `ae320ced78ebc5ce2cac15cc90a4564a9fa24502`;
- V2.3 result checkpoint commit `3ba759566258a49c2fd9b198f686bb1d9a6edc5d`;
- Structural Audit V1.1 result checkpoint commit `96bb0aec9b02f16cb82ba78f16d3164af78474ec`.

## Finding

Metadata-only handoff is insufficient for the final identity bridge.

If V1.2 accepted only:
- a copied `structuralAuditInputs` object;
- its claimed `structuralAuditInputsSha256`;
- a claimed V2.3 admitted-population SHA;

then V1.2 could verify that its actual structural streams match that copied object, but it could not prove that the copied binding was actually accepted by a successful V2.3 validation result or that the claimed population SHA was the output of that validated V2.3 declaration.

That would leave one final substitution opportunity between the capture-manifest gate and the structural audit.

## Decision

Structural Audit V1.2 must hash-before-parse verify the exact V2.3 validation-result bytes, in addition to accepting the full per-admitted `structuralAuditInputs` binding needed for field-level comparisons.

V1.2 must require:

1. raw V2.3 validation-result bytes;
2. an expected lowercase 64-hex SHA-256 for those exact bytes;
3. the full canonical per-admitted `structuralAuditInputs` object;
4. its expected `structuralAuditInputsSha256`;
5. the expected V2.3 admitted-population SHA-256.

The V2.3 result stream must be hashed before decoding/parsing. After successful hash verification, V1.2 must require:

- result contract exactly `songsterr-fresh-purpose-built-capture-manifest-v2.3`;
- `contractValid:true`;
- `errors:[]`;
- `v23SemanticGuardPassed:true`;
- `mayAdvanceToReferenceBlindStructuralAudit:true`;
- `populationIdentityVersion` exactly `capture-manifest-v2.3-structural-audit-input-binding-v1`;
- parsed `admittedPopulationManifestSha256` equals the expected V2.3 population SHA;
- parsed `structuralAuditInputBindingContract` equals `songsterr-fresh-purpose-built-structural-audit-input-binding-v1`;
- parsed `structuralAuditInputBindings` contains exactly one matching entry for the audited `attemptId` with the supplied canonical binding SHA for the single-attempt synthetic contract; a later real multi-attempt orchestration may audit each admitted attempt separately while preserving one shared V2.3 population SHA;
- parsed package binding SHA and decoder configuration SHA remain compatible with the V1.1-verified provenance/package identities.

V1.2 must independently canonical-hash the supplied full `structuralAuditInputs` object and require equality to the binding SHA referenced by the verified V2.3 result.

## Structural-byte comparisons still required

After the V2.3 result bytes and full binding are verified, V1.2 must compare:

- actual/expected V1 hardware raw SHA to `hardwareSourceSha256`;
- actual/expected V1 birth raw SHA to `birthStreamSha256`;
- actual/expected V1 pitch-latch raw SHA to `pitchLatchStreamSha256`;
- actual/expected V1 clock-sync raw SHA to `clockSyncSourceSha256`;
- parsed structural hardware `configurationId` to V2.3 `configurationId`;
- parsed structural hardware `calibrationId` to V2.3 `calibrationId`;
- parsed structural hardware `openStringMidi` to V2.3 `openStringMidi`;
- parsed structural hardware `eventSemanticsVersion` to V2.3 `eventSemanticsVersion`;
- parsed structural clock `syncId` to V2.3 `clockSyncId`.

Because Structural V1 hardware does not currently carry upstream `configurationSha256` or `instrumentSetupSha256` fields, V1.2 must not invent byte equality for absent fields. Those identities remain committed by the verified V2.3 binding/package chain and are exposed in the V1.2 result as declaration lineage. A future structural-hardware schema revision would be required before those SHA identities could also be embedded inside the structural hardware stream itself.

## Population identity decision

V1.2 must preserve V1.1 `derivedPopulationSha256` as `inheritedV11DerivedPopulationSha256` and compute a new structural population identity over at least:

- V1.1 structural population SHA;
- verified V2.3 validation-result SHA;
- verified V2.3 admitted-population SHA;
- audited attempt ID;
- slot ID;
- underlying-performance ID;
- verified `structuralAuditInputsSha256`.

This closes the exact admitted-performance/population identity chain without changing any structural note event.

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

## Required next order

1. Commit this review before V1.2 preregistration/implementation.
2. Freeze Structural Audit V1.2 Capture-Population Binding preregistration before code.
3. Implement only as an additive wrapper over V1.1.
4. Tests before official synthetic harness.
5. Freeze run/job/artifact/result identities.
6. Update the canonical current-state checkpoint.
