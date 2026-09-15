# Songsterr Fresh — Reference-Blind Structural Audit Population Completeness V1 Preregistration

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: FROZEN BEFORE IMPLEMENTATION / SYNTHETIC CI ONLY

## Purpose

Freeze one result-only population aggregator after Structural Audit V1.2. The aggregator proves that every admitted Capture Manifest V2.3 structural binding has exactly one successful immutable V1.2 result and that no extra/duplicate result is counted.

Authority:
- population-completeness review commit `9c85176001a62031299a036594f6d3273fb7b759`;
- Capture Manifest V2.3 result checkpoint `3ba759566258a49c2fd9b198f686bb1d9a6edc5d`;
- Structural Audit V1.2 result checkpoint `f4c63134f8b49723f342f5ba5f648498af317f73`.

This contract does not open structural sources, evaluated audio, calibration sources, or model output. It does not re-run V1/V1.1/V1.2 note-event logic. It aggregates immutable validation-result bytes only.

## Contract identities

Aggregator result contract:
`songsterr-fresh-purpose-built-reference-blind-structural-audit-population-completeness-v1`

Accepted V2.3 result contract:
`songsterr-fresh-purpose-built-capture-manifest-v2.3`

Accepted V2.3 population identity version:
`capture-manifest-v2.3-structural-audit-input-binding-v1`

Accepted V1.2 result contract:
`songsterr-fresh-purpose-built-reference-blind-structural-audit-v1.2`

Population-completeness identity version:
`reference-blind-structural-audit-population-completeness-v1`

## Inputs and hash-before-parse boundary

The aggregator receives:
1. exact V2.3 validation-result raw bytes plus expected lowercase 64-hex SHA-256;
2. a collection of V1.2 validation-result raw byte streams, each paired with its expected lowercase 64-hex SHA-256.

For every input stream independently:
- raw value must be bytes;
- expected SHA must be valid lowercase 64-hex;
- actual SHA-256 must equal expected SHA;
- no JSON decode or semantic parse may occur before that stream's hash gate passes.

A hash/type/expected-SHA failure is fail-closed. No result may be inferred, repaired, skipped, or substituted.

At least one admitted V2.3 binding and at least one V1.2 result are required.

## Frozen V2.3 result checks

After V2.3 hash verification, require:
- top-level object;
- exact V2.3 contract;
- `contractValid:true`;
- `errors:[]`;
- `v23SemanticGuardPassed:true`;
- `mayAdvanceToReferenceBlindStructuralAudit:true`;
- exact V2.3 population identity version;
- valid lowercase 64-hex `admittedPopulationManifestSha256`;
- exact structural binding contract `songsterr-fresh-purpose-built-structural-audit-input-binding-v1`;
- `structuralAuditInputBindings` list;
- integer `structuralAuditInputBindingCount` equal to list length and >=1;
- every binding-map entry has nonempty unique `attemptId` and valid lowercase 64-hex `structuralAuditInputsSha256`;
- no duplicate `(attemptId, structuralAuditInputsSha256)` rows;
- all downstream authorization false/zero.

The complete verified set of V2.3 admitted keys is:
`{(attemptId, structuralAuditInputsSha256)}`.

## Frozen V1.2 result checks

Only after each V1.2 stream's own hash verification may it be parsed. Every included V1.2 result must require:
- top-level object;
- exact V1.2 result contract;
- `contractValid:true`;
- `errors:[]`;
- `datasetStructurallySuitable:true`;
- `authoritativeStructuralSuitabilityEstablished:true`;
- `capturePopulationBindingViolationCount == 0`;
- inherited `calibrationProvenanceBridgeViolationCount == 0`;
- inherited `blockerCounts` object with every value integer zero;
- nonempty `attemptId`;
- valid lowercase 64-hex `structuralAuditInputsSha256`;
- valid lowercase 64-hex `captureManifestV23ValidationResultSha256` equal to the verified V2.3 result SHA;
- valid lowercase 64-hex `captureManifestV23AdmittedPopulationSha256` equal to the verified V2.3 admitted-population SHA;
- valid lowercase 64-hex `derivedPopulationSha256`;
- all downstream authorization false/zero.

Duplicate V1.2 expected/actual result hashes are forbidden. Duplicate V1.2 attempt IDs are forbidden. Duplicate `(attemptId, structuralAuditInputsSha256)` keys are forbidden.

## Exact population set equality

Define the verified V1.2 audited set as:
`{(attemptId, structuralAuditInputsSha256)}`.

Population completeness succeeds only when:

`verified V1.2 audited set == verified V2.3 admitted binding set`

exactly.

Therefore all fail closed:
- missing admitted attempt;
- extra/non-admitted attempt;
- duplicate attempt;
- duplicate result hash;
- binding SHA mismatch for an admitted attempt;
- zero V1.2 results;
- any failed V1.2 result.

## Frozen population-completeness identity

For each verified V1.2 result create one row:
- `attemptId`;
- `structuralAuditInputsSha256`;
- `v12ValidationResultSha256` = verified exact V1.2 result byte SHA;
- `v12DerivedPopulationSha256`.

Sort rows by `(attemptId, structuralAuditInputsSha256)` as strings.

Compute:

`SHA256(canonical_json({
  "populationIdentityVersion": "reference-blind-structural-audit-population-completeness-v1",
  "captureManifestV23ValidationResultSha256": <verified V2.3 result SHA>,
  "captureManifestV23AdmittedPopulationSha256": <verified V2.3 admitted-population SHA>,
  "verifiedAttemptResults": <sorted rows>
}))`

Expose as `populationStructuralCompletenessSha256` only when all checks pass; otherwise null.

## Frozen result fields

Deterministic result includes at least:
- `contract`;
- `contractValid`;
- sorted `errors`;
- `captureManifestV23ValidationSourceSha256` expected/actual/matches;
- `captureManifestV23ValidationResultSha256`;
- `captureManifestV23AdmittedPopulationSha256`;
- `admittedBindingCount`;
- `verifiedV12ResultCount`;
- sorted `admittedBindingKeys`;
- sorted `verifiedV12BindingKeys`;
- sorted `verifiedAttemptResults` rows;
- `populationIdentityVersion`;
- `populationStructuralCompletenessSha256`;
- `populationStructurallySuitable`;
- `populationStructuralCompletenessEstablished`;
- all downstream authorization false/zero.

Population-wide success fields may be true only when `contractValid:true`, exact set equality holds, all V1.2 results pass, and no duplicate/missing/extra identity exists.

## Synthetic tests before official harness

Tests must execute before official harness and cover at minimum:
1. one-admitted-attempt PASS;
2. two-admitted-attempt PASS;
3. V2.3 raw value not bytes FAIL;
4. malformed V2.3 expected SHA FAIL;
5. V2.3 hash mismatch short-circuits before V2.3 parse;
6. invalid V2.3 UTF-8/JSON after successful hash FAIL;
7. V2.3 contract/PASS/semantic/may-advance failures FAIL;
8. V2.3 errors nonempty FAIL;
9. V2.3 population version/SHA invalid FAIL;
10. V2.3 binding contract mismatch FAIL;
11. V2.3 binding count mismatch/zero FAIL;
12. malformed V2.3 binding entry FAIL;
13. duplicate V2.3 attempt ID or binding key FAIL;
14. V2.3 downstream authorization open FAIL;
15. V1.2 raw value not bytes FAIL;
16. malformed V1.2 expected SHA FAIL;
17. V1.2 hash mismatch short-circuits before that V1.2 parse;
18. invalid V1.2 UTF-8/JSON after successful hash FAIL;
19. V1.2 contract/PASS/suitability failures FAIL;
20. V1.2 errors nonempty FAIL;
21. nonzero V1.2 capture/provenance bridge violation FAIL;
22. nonzero inherited V1 blocker FAIL;
23. V1.2 V2.3 result SHA mismatch FAIL;
24. V1.2 V2.3 population SHA mismatch FAIL;
25. malformed V1.2 attempt/binding/derived-population identities FAIL;
26. V1.2 downstream authorization open FAIL;
27. duplicate V1.2 result hash FAIL;
28. duplicate V1.2 attempt ID/key FAIL;
29. missing admitted V1.2 result FAIL;
30. extra/non-admitted V1.2 result FAIL;
31. admitted attempt binding-SHA mismatch FAIL;
32. zero V1.2 results FAIL;
33. completeness SHA changes when an included valid V1.2 result byte identity changes;
34. completeness SHA changes under a different valid two-attempt admitted population;
35. input ordering does not change canonical completeness SHA;
36. canonical output is byte-deterministic;
37. all downstream authorization remains false/zero on PASS.

## Official synthetic harness

Ordinary GitHub CPU only:
1. compile implementation/tests;
2. run all tests first;
3. generate a frozen synthetic V2.3 result with **two admitted bindings**;
4. generate two successful V1.2 result byte streams bound to that same V2.3 result/population;
5. run the aggregator over those immutable result bytes/hashes;
6. print verified counts, set-equality summary, population-completeness SHA and closed authorization state;
7. upload canonical result artifact.

No network access, structural-source reading by the aggregator, evaluated audio, model execution, correctness execution, or external corpus access.

## Interpretation boundary

A synthetic PASS proves only population-wide software completeness: every admitted synthetic V2.3 binding has exactly one successful immutable V1.2 audit result and the final completeness identity commits to the complete set.

It does not prove physical sensing accuracy, real calibration validity, real holdout capture, correctness, model validation, customer eligibility, or delivery authority.

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
2. Update canonical checkpoint.
3. Implement result-only aggregator.
4. Add tests before official harness.
5. Add ordinary GitHub CPU workflow with tests first.
6. Freeze run/job/artifact/result identities.
7. Update canonical checkpoint and perform a final completeness review, including the raw-evidence -> decoded-structural functional derivation question; do not invent another gate without a confirmed gap.
