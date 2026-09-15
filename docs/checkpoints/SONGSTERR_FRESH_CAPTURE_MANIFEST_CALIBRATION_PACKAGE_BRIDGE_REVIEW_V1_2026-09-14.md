# Songsterr Fresh — Capture-Manifest / Calibration-Package Identity Bridge Review V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: REVIEW COMPLETE / NARROW IDENTITY GAP CONFIRMED

## Scope

This review follows completion of Reference Calibration Package Provenance V1. It asks only whether the existing purpose-built capture-manifest V2.1 contract can already bind an admitted future capture population to the new canonical calibration-package identity, or whether a prospective additive manifest version is required.

This is software/documentation review only. It does not authorize real calibration, real hardware, real holdout capture, Basic Pitch, V6, correctness, protected-song material, reserved Guitar Fretboard Notes sources, customer delivery, or archived V143/Gomyway work.

## Authority reviewed

- capture-manifest V2.1 implementation: `scripts/songsterr-fresh/purpose_built_capture_manifest_contract_v2_1.py`;
- inherited V2 implementation: `scripts/songsterr-fresh/purpose_built_capture_manifest_contract_v2.py`;
- V2 synthetic fixture/tests: `scripts/songsterr-fresh/test_purpose_built_capture_manifest_contract_v2.py`;
- physical-reference semantics commit `ea5f50212cd1cd3794c65cb648a4d781e49e4082`;
- Reference Calibration Package Provenance V1 preregistration commit `cbd99714f655d859af2410374c3245a4afe6b056`;
- provenance implementation commit `3dd1140650070342ab9fc4e177870fd39940a4e0`;
- frozen provenance result checkpoint commit `c57156fec7c5000563552c8cb128366956b8c95b`.

## What V2.1 already binds

At corpus level, V2.1/V2 binds:
- hardware configuration identity and SHA-256;
- instrument setup SHA-256;
- a legacy `referenceCalibration` declaration containing `calibrationId`, path, SHA-256, information-firewall declarations, and `maxAbsoluteOnsetErrorSeconds`;
- clock-sync identity and SHA-256.

For each admitted attempt, the reference declaration binds:
- hardware configuration SHA-256;
- calibration ID;
- clock-sync ID;
- pitch-evidence SHA-256;
- birth-evidence SHA-256;
- a derivation-configuration SHA-256;
- event-semantics version.

The admitted-population identity includes the calibration artifact SHA-256 and derivation-configuration SHA-256.

## What Provenance V1 newly binds

Reference Calibration Package Provenance V1 produces a canonical `packageBindingSha256` over a root-independent semantic package binding that includes verified identities for:
- hardware configuration;
- instrument setup;
- hardware component identities;
- wiring topology;
- calibration fixture;
- deterministic decoder ID/version, code SHA-256 and configuration SHA-256;
- preserved raw calibration source identities and roles;
- all required derived calibration output identities;
- calibration information-firewall declarations;
- inherited timing bound declaration.

The frozen synthetic result established canonical package binding SHA-256:
`735d276afc5bac7cd8e0e905ae42f8d4dc4bfae835ae013403ccdc31c4cf857c`.

## Confirmed gap

The package-level decoder/configuration identity gap is closed by Provenance V1 itself. A duplicate standalone decoder-identity contract is not required.

However, V2.1 has no field whose semantics require an admitted capture manifest or admitted per-take reference to bind the new `packageBindingSha256`.

Therefore two declarations can independently pass their current software contracts while remaining unlinked:
1. a valid calibration-provenance package with a canonical package binding; and
2. a valid V2.1 capture manifest carrying a legacy `referenceCalibration.sha256`, calibration ID, hardware configuration SHA and derivation-configuration SHA.

Nothing in V2.1 proves that the capture manifest's calibration/reference declarations refer to the same validated provenance package whose canonical package binding contains the decoder code/configuration, raw-source, fixture, wiring and derived-output identities.

This is a real identity-linkage gap, not a new physical-validation gap.

## Decision

A narrowly scoped prospective capture-manifest version bump is required before any future real capture authority can rely on the new calibration-package provenance contract.

The bridge must be additive over V2.1. It must not alter chronology, retry semantics, acquisition-QA rules, structural blockers, policy boundaries, timing thresholds, V6 rules or correctness rules.

The bridge should bind one already-validated calibration package at corpus level and require every admitted reference to cite that same canonical package binding SHA-256. The admitted-population identity must also include that package binding SHA-256.

To avoid duplicating the package contract, the bridge should not create a second decoder schema. It may inspect the inline canonical package-binding object only to verify:
- its canonical hash equals the declared `packageBindingSha256`;
- its package contract is the frozen Provenance V1 contract;
- `calibrationId` matches the capture manifest calibration ID;
- hardware configuration SHA-256 matches the capture manifest hardware configuration;
- instrument setup SHA-256 matches the capture manifest instrument setup;
- timing/firewall declarations remain compatible;
- decoder ID/version and decoder code/configuration SHA-256 identities are present and valid inside the bound package object.

The bridge should additionally bind the SHA-256 identity of the provenance validation-result artifact, but it remains declaration-only software and does not itself re-open or re-verify package files.

## Required next order

1. Freeze a V2.2 calibration-package bridge preregistration before implementation.
2. Implement V2.2 as a narrow wrapper/additive validator over V2.1.
3. Add synthetic tests before official harness execution.
4. Add ordinary GitHub CPU workflow with tests first.
5. Freeze run/job/artifact/result identities in a dedicated result checkpoint.
6. Update the canonical current-state checkpoint after each meaningful stage.
7. After V2.2, review whether the reference-blind structural audit needs a corresponding package-result byte-verification bridge; do not assume it without review.

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
