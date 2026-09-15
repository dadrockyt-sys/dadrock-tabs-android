# Songsterr Fresh — Structural Audit Population Completeness Review V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: REVIEW COMPLETE / MULTI-ATTEMPT COMPLETENESS GAP CONFIRMED

## Scope

Review the full software identity chain through Capture Manifest V2.3 and Structural Audit V1.2 and determine whether a V1.2 PASS is sufficient to establish structural suitability for an entire admitted V2.3 population when more than one attempt is admitted.

This is review/documentation only. It does not authorize real hardware, calibration, holdout capture, Basic Pitch, V6, correctness, protected-song execution, reserved Guitar Fretboard Notes sources, customer delivery, or archived V143/Gomyway work.

## Authority reviewed

- Capture Manifest V2.3 preregistration commit `c79fbd1d728a9d3dac86f036998108cb9765628e`;
- Capture Manifest V2.3 result checkpoint `3ba759566258a49c2fd9b198f686bb1d9a6edc5d`;
- Structural Audit V1.2 preregistration commit `617cdc71be4fea6ccdafec1aadf47c13d66726cb`;
- Structural Audit V1.2 result checkpoint `f4c63134f8b49723f342f5ba5f648498af317f73`.

## What V2.3 establishes

V2.3 validates a capture manifest that may contain multiple admitted attempts. Its result exposes:

- `structuralAuditInputBindingCount`;
- `structuralAuditInputBindings`, a list of admitted `{attemptId, structuralAuditInputsSha256}` entries;
- one population-wide `admittedPopulationManifestSha256` that commits to all admitted structural-binding rows.

Thus V2.3 defines a population-wide admitted set.

## What V1.2 establishes

V1.2 deliberately consumes:

- one full `structuralAuditInputs` object for **one audited admitted attempt**;
- one binding SHA;
- the V2.3 population SHA;
- one V2.3 validation-result byte stream;
- one set of four structural source streams;
- one Provenance V1 result stream.

Its preregistration explicitly permits other V2.3 binding-map entries and requires only exactly one matching entry for the audited attempt.

Its result exposes one `attemptId`, `slotId`, `underlyingPerformanceId`, binding SHA and per-attempt final structural population SHA.

Therefore V1.2 proves exact structural-byte/population membership for one admitted performance at a time.

## Confirmed gap

For a V2.3 population with N admitted attempts where N > 1, the current software contracts do not yet prove all of the following population-wide properties:

1. every V2.3 admitted structural binding received a V1.2 audit;
2. no admitted binding is missing;
3. no admitted binding was audited more than once and counted twice;
4. no V1.2 result exists for an attempt outside the V2.3 admitted binding set;
5. every included V1.2 result hash was verified before parse;
6. every included V1.2 result is successful (`contractValid:true`, `datasetStructurallySuitable:true`, `authoritativeStructuralSuitabilityEstablished:true`, zero bridge violations and zero inherited blockers);
7. every V1.2 result names the same V2.3 validation-result SHA and V2.3 admitted-population SHA;
8. every V1.2 result's `attemptId` and `structuralAuditInputsSha256` match exactly one V2.3 binding-map entry;
9. the final population-level structural identity commits to the complete set of successful V1.2 result identities, not just one attempt.

A single V1.2 result may truthfully be a PASS while other admitted attempts remain unaudited. Therefore a single per-attempt V1.2 `datasetStructurallySuitable:true` must not be interpreted as a population-wide all-attempt completeness proof.

This is a completeness/aggregation gap only. The per-attempt identity chain itself is closed.

## Decision

Add one separate **Reference-Blind Structural Audit Population Completeness V1** aggregator after V1.2.

Do not create V1.3 by changing per-attempt V1.2 semantics. V1.2 should remain the immutable per-attempt audit result. The aggregator should consume immutable result bytes and prove exact set equality/completeness against V2.3.

## Required aggregator semantics for preregistration

The later frozen aggregator should:

1. accept the V2.3 validation-result raw bytes plus expected SHA-256 and hash-before-parse them;
2. require successful exact V2.3 result contract, semantic guard, `errors:[]`, and false/zero downstream authorization;
3. read the complete V2.3 `structuralAuditInputBindings` admitted set and binding count;
4. accept a collection of V1.2 validation-result raw byte streams, each with expected SHA-256, and hash every stream before parsing any V1.2 semantic fields;
5. require exact V1.2 result contract and successful structural suitability for every result;
6. require every V1.2 result to name the same verified V2.3 result SHA and admitted-population SHA;
7. require exact set equality between V2.3 `(attemptId, structuralAuditInputsSha256)` entries and V1.2 `(attemptId, structuralAuditInputsSha256)` results;
8. reject duplicate V1.2 attempt IDs, duplicate result hashes, missing admitted attempts, and extra/non-admitted attempts;
9. require all included V1.2 downstream authorization false/zero;
10. require every included V1.2 `capturePopulationBindingViolationCount == 0` and all inherited structural blockers/bridge violations zero;
11. compute a deterministic population-completeness SHA over the verified V2.3 result SHA, V2.3 admitted-population SHA, and sorted rows containing each attempt ID, binding SHA, V1.2 result SHA, and V1.2 derived population SHA;
12. expose a population-wide structural suitability flag only when set equality and all per-attempt V1.2 results pass.

## Important naming boundary

The aggregator's population-wide success field should be clearly distinct from a per-attempt V1.2 result. Recommended fields:

- `populationStructurallySuitable`;
- `populationStructuralCompletenessEstablished`.

This avoids treating one V1.2 attempt result as if it already covered all admitted performances.

## What the aggregator must not do

It must not:

- open structural source files;
- re-run V1/V1.1/V1.2 note-event logic;
- inspect evaluated audio;
- invoke Basic Pitch or V6;
- alter timing/MIDI/overlap/calibration rules;
- infer missing results;
- repair or drop failed attempts;
- authorize correctness or delivery.

## Required next order

1. Commit this review before aggregator code.
2. Update the canonical current-state checkpoint.
3. Freeze Population Completeness V1 preregistration before implementation.
4. Implement/test on synthetic multi-attempt fixtures, including at least one two-admitted-attempt PASS.
5. Run ordinary GitHub CPU tests-first CI only.
6. Freeze run/job/artifact/result identities.
7. Update canonical checkpoint and repeat completeness review. If no further software declaration/completeness gap remains, stop software gate creation and record the physical route as the next objectively necessary step, still budget-paused.

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
