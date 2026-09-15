# Songsterr Fresh — Reference-Blind Structural Audit V1.2 Capture-Population Binding Preregistration

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: FROZEN BEFORE IMPLEMENTATION / SYNTHETIC CI ONLY

## Purpose

Freeze one narrow additive wrapper over accepted Structural Audit V1.1 so the exact structural bytes being audited are proven to belong to the exact admitted performance/binding/population accepted by Capture Manifest V2.3.

This preregistration follows:
- end-to-end identity review commit `e3e1759b576831128ff0b95ee237b6d131a2fe51`;
- V2.3 result checkpoint commit `3ba759566258a49c2fd9b198f686bb1d9a6edc5d`;
- V2.3 result-byte binding review commit `866c673bc7728a8e0943eb45b0109910c28a36f6`;
- Structural Audit V1.1 result checkpoint `96bb0aec9b02f16cb82ba78f16d3164af78474ec`.

V1.2 is identity plumbing only. It must not change V1/V1.1 physical note events, timing bounds, MIDI derivation, overlap rules, blocker semantics, calibration package semantics, V6 rules, correctness gates, or policy.

No real hardware, real calibration, real holdout capture, evaluated audio, Basic Pitch, V6, correctness, protected-song execution, reserved Guitar Fretboard Notes source, customer delivery, or archived V143/Gomyway work is authorized.

## Contract identities

Top-level V1.2 result contract:
`songsterr-fresh-purpose-built-reference-blind-structural-audit-v1.2`

Accepted V2.3 validation-result contract:
`songsterr-fresh-purpose-built-capture-manifest-v2.3`

Accepted structural-input binding contract:
`songsterr-fresh-purpose-built-structural-audit-input-binding-v1`

Accepted V2.3 population identity version:
`capture-manifest-v2.3-structural-audit-input-binding-v1`

V1.2 population identity version:
`reference-blind-structural-audit-v1.2-capture-population-binding-v1`

## Inherited V1.1 behavior — UNCHANGED

V1.2 must call/inherit Structural Audit V1.1 first with:
- the original four raw structural sources and expected hashes;
- the Provenance V1 result raw bytes and expected SHA;
- the declared provenance-result SHA;
- the declared calibration-package binding SHA.

All V1/V1.1 source-hash-before-parse behavior, zero-anomaly structural blockers, provenance-result verification, package binding verification, decoder identity, timing <= `0.025 s`, physical note derivation, MIDI range, overlap rules, and authorization boundaries remain authoritative.

V1.2 must not alter V1.1 `derivedNoteEventCount`, V1.1 source hashes, or V1.1 derived population SHA.

## New V2.3 result-byte input

V1.2 adds one separately supplied raw byte stream:
- logical source name `captureManifestV23ValidationResult`;
- raw value bytes only;
- expected lowercase 64-hex SHA-256.

V1.2 must hash these bytes before any UTF-8 decode or JSON parse.

Fail closed before V2.3 semantic parsing if:
- raw input is not bytes;
- expected SHA is malformed;
- actual SHA differs from expected SHA.

Only after this hash gate succeeds may V1.2 parse the V2.3 result.

## Supplied admitted structural binding

V1.2 receives:
- full `structuralAuditInputs` object for one audited admitted attempt;
- expected lowercase 64-hex `structuralAuditInputsSha256`;
- expected lowercase 64-hex V2.3 `admittedPopulationManifestSha256`.

V1.2 must canonical-hash the full supplied binding using sorted compact UTF-8 JSON with no NaN and require equality to the supplied binding SHA before field-level comparisons.

The supplied binding must have exact contract:
`songsterr-fresh-purpose-built-structural-audit-input-binding-v1`.

## Frozen V2.3 result semantic checks

After successful V2.3 result hash verification and parse, require:

1. top-level object;
2. exact V2.3 result contract;
3. `contractValid:true`;
4. `errors:[]`;
5. `v23SemanticGuardPassed:true`;
6. `mayAdvanceToReferenceBlindStructuralAudit:true`;
7. exact V2.3 population identity version;
8. parsed `admittedPopulationManifestSha256` valid and exactly equal supplied expected V2.3 population SHA;
9. parsed `structuralAuditInputBindingContract` exact;
10. `structuralAuditInputBindings` is a list containing exactly one entry whose `attemptId` equals supplied binding `attemptId` and whose `structuralAuditInputsSha256` equals the verified supplied binding SHA; duplicate entries for the audited attempt fail;
11. parsed `structuralAuditInputBindingCount` is an integer equal to list length;
12. parsed `calibrationPackageValidationResultSha256` equals the Provenance V1 result SHA verified by V1.1;
13. parsed `calibrationPackageBindingSha256` equals the package binding SHA verified by V1.1;
14. parsed `calibrationPackageDecoderConfigurationSha256` equals the decoder configuration SHA verified by V1.1;
15. parsed V2.3 downstream authorization remains false/zero.

Other admitted binding-map entries are permitted for a future multi-attempt population; exactly one matching entry for the audited attempt is required.

## Frozen binding-to-V1.1 source comparisons

V1.2 must fail closed unless the verified full binding matches the actual V1.1-audited source bytes:

- `hardwareSourceSha256` == V1.1 `sourceSha256.hardware.actual`;
- `birthStreamSha256` == V1.1 `sourceSha256.birth.actual`;
- `pitchLatchStreamSha256` == V1.1 `sourceSha256.pitchLatch.actual`;
- `clockSyncSourceSha256` == V1.1 `sourceSha256.clockSync.actual`.

Because V1.1 already requires each original expected SHA to equal actual bytes, this transitively proves the V2.3 binding names the exact bytes that V1.1 structurally audited.

## Frozen parsed structural declaration comparisons

V1.2 must compare the supplied binding to the parsed structural declarations whose bytes V1.1 already hash-verified:

Hardware stream:
- `configurationId` exact;
- `calibrationId` exact;
- `openStringMidi` exact six-value list;
- `eventSemanticsVersion` exact.

Clock stream:
- `clockSyncId` equals parsed `syncId`.

V1.2 must not invent equality to absent structural-hardware SHA fields. `configurationSha256` and `instrumentSetupSha256` remain upstream V2.3/package lineage declarations; expose them in the V1.2 result but do not pretend they are embedded in V1 hardware bytes.

## Frozen package / decoder linkage

The supplied binding must additionally satisfy:
- `calibrationPackageBindingSha256` equals V1.1 verified package binding SHA;
- `derivationConfigurationSha256` equals V1.1 verified decoder configuration SHA.

The V2.3 result's corresponding package/decoder identities must match the same V1.1 values as specified above.

## Admitted-performance identity

The supplied binding's nonempty:
- `attemptId`;
- `slotId`;
- `underlyingPerformanceId`;
- `playerId`;
- `exerciseId`;
- `category`

become the authoritative V1.2 declaration identity for the audited structural performance because the verified V2.3 result references that binding hash for the admitted attempt.

V1.2 must expose those fields unchanged in its result.

## New blocker count

V1.2 adds:
`capturePopulationBindingViolationCount`.

Any V1/V1.1 failure or any V1.2 V2.3-result/binding/source/declaration identity failure forces:
- `contractValid:false`;
- `datasetStructurallySuitable:false`;
- `authoritativeStructuralSuitabilityEstablished:false`.

No event may be dropped or repaired to satisfy this bridge.

## Frozen population identity

Preserve V1.1 population SHA as:
`inheritedV11DerivedPopulationSha256`.

When V1.1 and the V1.2 bridge both pass, compute V1.2 `derivedPopulationSha256` as:

`SHA256(canonical_json({
  "populationIdentityVersion": "reference-blind-structural-audit-v1.2-capture-population-binding-v1",
  "inheritedV11DerivedPopulationSha256": <V1.1 SHA>,
  "captureManifestV23ValidationResultSha256": <verified V2.3 result SHA>,
  "captureManifestV23AdmittedPopulationSha256": <verified V2.3 population SHA>,
  "attemptId": <binding attemptId>,
  "slotId": <binding slotId>,
  "underlyingPerformanceId": <binding underlyingPerformanceId>,
  "structuralAuditInputsSha256": <verified binding SHA>
}))`

If V1.1 does not produce a population SHA or any V1.2 bridge violation occurs, V1.2 `derivedPopulationSha256` must be null.

## Frozen result fields

V1.2 deterministic result must include at least:
- `contract`;
- `contractValid`;
- sorted `errors`;
- inherited V1.1 `sourceSha256` unchanged;
- inherited Provenance V1/package/decoder fields unchanged;
- `captureManifestV23ValidationSourceSha256` with expected/actual/matches;
- `captureManifestV23ValidationResultSha256`;
- `captureManifestV23AdmittedPopulationSha256`;
- `structuralAuditInputsSha256`;
- upstream lineage `configurationSha256` and `instrumentSetupSha256` from verified binding;
- audited attempt/slot/underlying-performance/player/exercise/category fields;
- `capturePopulationBindingViolationCount`;
- `populationIdentityVersion`;
- `inheritedV11DerivedPopulationSha256`;
- augmented V1.2 `derivedPopulationSha256`;
- inherited `derivedNoteEventCount` unchanged;
- inherited V1 blocker counts unchanged;
- `datasetStructurallySuitable` and `authoritativeStructuralSuitabilityEstablished` true only if V1.1 and V1.2 bridge both pass;
- all downstream authorization false/zero.

## Synthetic tests before official harness

Tests must run before official harness and cover at minimum:

1. complete V1.2 synthetic chain PASS;
2. V1.1 nominal source/provenance semantics remain unchanged;
3. V2.3 validation result raw value not bytes FAIL;
4. malformed V2.3 expected result SHA FAIL;
5. V2.3 result hash mismatch short-circuits before parse;
6. invalid V2.3 UTF-8/JSON after successful hash FAIL;
7. V2.3 result contract mismatch FAIL;
8. V2.3 `contractValid:false` FAIL;
9. nonempty V2.3 `errors` FAIL;
10. `v23SemanticGuardPassed:false` FAIL;
11. `mayAdvanceToReferenceBlindStructuralAudit:false` FAIL;
12. V2.3 population identity version mismatch FAIL;
13. malformed/mismatched V2.3 admitted-population SHA FAIL;
14. V2.3 structural-binding contract mismatch FAIL;
15. malformed binding object/SHA or canonical hash mismatch FAIL;
16. missing or duplicate matching V2.3 binding-map entry FAIL;
17. V2.3 binding count mismatch FAIL;
18. V2.3 provenance-result SHA mismatch to V1.1 FAIL;
19. V2.3 package-binding SHA mismatch to V1.1 FAIL;
20. V2.3 decoder-configuration SHA mismatch to V1.1 FAIL;
21. any V2.3 downstream authorization true/nonzero FAIL;
22. each of four binding structural source SHA mismatches FAIL;
23. structural hardware configuration ID mismatch FAIL;
24. structural hardware calibration ID mismatch FAIL;
25. structural tuning mismatch FAIL;
26. structural event-semantics mismatch FAIL;
27. structural clock-sync ID mismatch FAIL;
28. binding package SHA mismatch to V1.1 FAIL;
29. binding derivation-configuration SHA mismatch to V1.1 FAIL;
30. inherited V1.1 structural blocker still FAILS with otherwise valid V1.2 bridge;
31. V1.2 population SHA changes if V2.3 result SHA changes while semantic identities remain valid;
32. V1.2 population SHA changes if V2.3 population/binding identity changes under a valid regenerated chain;
33. inherited V1.1 population SHA remains unchanged by V1.2-only binding/result identity changes;
34. canonical V1.2 result is byte-deterministic;
35. all downstream authorization remains false/zero on PASS.

## Official synthetic harness

Ordinary GitHub CPU only:
1. compile V1.2 implementation/tests;
2. run all synthetic tests first;
3. generate V1 structural streams and align their configuration/calibration/tuning/clock identities to a synthetic V2.3 admitted binding;
4. generate a successful Provenance V1 result and use its exact SHA in the synthetic V2.3 manifest;
5. update the V2.3 structural binding's four source SHA fields to the exact generated V1 structural source bytes and recompute binding SHA;
6. validate that V2.3 manifest to produce exact V2.3 result bytes;
7. run V1.2 using those exact V1 sources, Provenance V1 result bytes, V2.3 result bytes, full binding, binding SHA and V2.3 population SHA;
8. print canonical chain/population hashes and closed authorization summary;
9. upload canonical V1.2 result artifact.

No network, media acquisition, external corpus, evaluated audio, model execution, or correctness execution.

## Interpretation boundary

A synthetic V1.2 PASS closes the software declaration chain from an admitted V2.3 capture performance/population through exact structural bytes and Provenance V1 package identity to a V1.1 structural PASS.

It still does not prove real physical sensor accuracy, real calibration validity, real holdout acquisition, correctness, model validation, customer eligibility, or delivery authority.

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
3. Implement V1.2 strictly as additive wrapper over V1.1.
4. Add synthetic tests before official harness.
5. Add ordinary GitHub CPU workflow with tests first.
6. Freeze run/job/artifact/result identities.
7. Update canonical current-state checkpoint.
