# Songsterr Fresh — End-to-End Reference Declaration Identity Review V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: REVIEW COMPLETE / PER-ADMITTED-PERFORMANCE IDENTITY GAP CONFIRMED

## Scope

This review follows the completed synthetic identity chain:

capture-manifest V2.2 -> Reference Calibration Package Provenance V1 -> reference-blind structural audit V1.1.

It asks whether the structural audit's exact four reference-side input byte streams and their hardware/calibration/clock declarations are themselves tied to the same admitted capture performance/population that V2.2 declares.

This is documentation/review only. It does not authorize real calibration, real hardware, real holdout capture, Basic Pitch, V6, correctness, protected-song material, reserved Guitar Fretboard Notes sources, customer delivery, or archived V143/Gomyway work.

## Authority reviewed

- capture-manifest V2/V2.1 implementation lineage, including `scripts/songsterr-fresh/purpose_built_capture_manifest_contract_v2.py`;
- capture-manifest V2.2 accepted implementation commit `e3e3ae05ab0ab4a94a77e6c6e5be2466f618cf46` and result checkpoint `7d2d05ec365bbdb1aced574f7caf1865795fbc23`;
- Provenance V1 result checkpoint `c57156fec7c5000563552c8cb128366956b8c95b`;
- structural-audit V1 preregistration commit `067875e3aa1538ff5483b74cc9071b00e9e82b07`;
- structural-audit V1.1 result checkpoint `96bb0aec9b02f16cb82ba78f16d3164af78474ec`.

## What is already linked correctly

Capture-manifest V2/V2.2 already establishes, for each admitted attempt:

- immutable attempt/slot/underlying-performance identity;
- evaluated-audio SHA;
- independent pitch-evidence SHA;
- independent birth-evidence SHA;
- reference artifact SHA;
- reference hardware-configuration SHA;
- reference calibration ID;
- reference clock-sync ID;
- source pitch/birth evidence SHA links;
- decoder derivation-configuration SHA;
- V2.2 calibration-package binding SHA.

V2.2 additionally cross-binds the verified package to capture-level:

- hardware configuration ID and SHA;
- instrument-setup SHA;
- calibration ID;
- inherited calibration timing declaration;
- decoder configuration identity.

Structural-audit V1.1 now correctly hash-before-parse verifies the Provenance V1 result and proves that its canonical package binding is the package identity declared through V2.2.

## Confirmed remaining gaps

### 1. Structural hardware IDs are not tied to the package/capture IDs

Structural-audit V1's hashed `hardware` stream requires only nonempty:

- `configurationId`;
- `calibrationId`.

V1/V1.1 never compares those values to the verified package binding or capture-manifest declarations. Therefore the structural hardware stream can name a different hardware configuration or calibration while V1.1 still passes.

### 2. Structural hardware lacks exact configuration/setup SHA identities

The capture/package chain binds:

- hardware configuration SHA-256;
- instrument-setup SHA-256.

The structural V1 `hardware` stream contains neither identity. It contains tuning values, but no field proving that its physical string/fret mapping/tuning declaration belongs to the same frozen hardware configuration and instrument setup used by the admitted capture.

A name-only equality patch would therefore be weaker than the existing upstream identity standard.

### 3. Structural clock identity is not tied to the admitted capture clock identity

Structural V1's `clockSync` stream requires a nonempty `syncId` and timing proof, but V1/V1.1 never compares that `syncId` to the capture-manifest `corpus.clockSync.syncId` / admitted-reference `clockSyncId`.

This review does **not** require raw SHA equality between the capture `clockSync.sha256` artifact and the structural-audit `clockSync` JSON stream because the current contracts do not establish that those are the same byte object. Semantic `syncId` linkage is justified; byte equality is not assumed.

### 4. Structural event-semantics/tuning declarations are not tied to the admitted reference declaration

Structural V1 freezes `eventSemanticsVersion = physical-reference-semantics-v1` and derives MIDI from its own `openStringMidi` values. Capture-manifest V2 requires an admitted reference event-semantics declaration and stores an instrument setup/tuning declaration, but the structural audit does not cross-check either against the admitted capture/reference declaration.

### 5. Most importantly: the four structural input stream hashes are not bound to the admitted attempt/population

Structural-audit V1/V1.1 receives exact hashes for:

- `hardware`;
- `birth`;
- `pitchLatch`;
- `clockSync`.

But capture-manifest V2.2 does not declare those four decoded structural-audit output hashes for an admitted attempt. Its admitted reference binds the raw pitch/birth evidence and one reference artifact SHA, not the exact four V1 structural input streams.

Consequently, the following can all pass independently while remaining unproven as the same admitted performance:

1. a valid V2.2 admitted capture population;
2. a valid Provenance V1 package;
3. a valid V1.1 structural audit over a different set of four reference-side streams produced under compatible package identities.

V1.1's augmented structural population SHA binds package/provenance identity, but it still does not bind the V2.2 `admittedPopulationManifestSha256`, `attemptId`, `slotId`, or `underlyingPerformanceId`.

This is the decisive end-to-end identity gap.

## Decision

A mere V1.2 comparison of `configurationId` and `calibrationId` is insufficient.

The next software-only bridge must first make the **exact structural-audit inputs a declared part of each admitted capture reference**, so the capture population identity commits to the exact bytes that a later structural audit will consume.

The clean additive order is:

1. **Capture Manifest V2.3 Structural-Audit Input Binding** — extend each admitted `reference` with a deterministic `structuralAuditInputs` declaration that binds the exact future structural-audit source hashes plus the relevant configuration/calibration/setup/clock/event-semantics identities, and include that binding in the admitted-population SHA.
2. **Structural Audit V1.2 Capture-Population Binding** — inherit V1.1, accept the V2.3 frozen per-attempt binding and admitted-population SHA as declaration metadata, require the four actual structural source hashes and parsed declarations to match that binding, and augment the structural population identity with the admitted attempt/population identity.

This is identity plumbing only. Neither step may modify physical note events, timing bounds, overlap/MIDI rules, decoder behavior, V6 rules, correctness gates, or policy.

## Required V2.3 declaration shape for later preregistration

For every admitted attempt, `reference.structuralAuditInputs` should be a deterministic object containing at minimum:

- contract/version identity;
- exact `hardwareSourceSha256`;
- exact `birthStreamSha256`;
- exact `pitchLatchStreamSha256`;
- exact `clockSyncSourceSha256`;
- hardware `configurationId`;
- hardware `configurationSha256`;
- `instrumentSetupSha256`;
- exact six-value `openStringMidi` declaration;
- `calibrationId`;
- `clockSyncId`;
- exact `eventSemanticsVersion`;
- source `pitchEvidenceSha256`;
- source `birthEvidenceSha256`;
- `calibrationPackageBindingSha256`;
- `derivationConfigurationSha256`.

V2.3 must cross-check those fields against the already-authoritative V2.2 corpus/reference declarations. It must not infer them from evaluated audio.

The V2.3 admitted-population identity must commit to the canonical structural-audit-input binding, either by including all fields or its canonical SHA-256.

Failed/non-admitted attempts need not carry future structural-audit inputs.

## Required later V1.2 behavior for review planning

A later separately preregistered V1.2 should:

- inherit/call V1.1 without weakening any original V1/V1.1 gate;
- require an exact V2.3 per-admitted-attempt structural-input binding plus its V2.3 admitted-population SHA;
- require V1's four expected/actual source hashes to equal the V2.3-declared four source hashes;
- compare parsed V1 hardware `configurationId`, `calibrationId`, tuning and event-semantics values to the V2.3 binding;
- require V1.2-specific structural hardware SHA fields, if frozen in the later preregistration, to match V2.3 configuration/setup SHA identities;
- compare parsed structural clock `syncId` to the V2.3 `clockSyncId`;
- require package binding / decoder configuration identities to remain consistent with V1.1 and V2.3;
- expose attempt/slot/underlying-performance identity and V2.3 admitted-population SHA in the V1.2 result;
- augment, not replace, V1.1's structural population identity.

No implementation of V1.2 should begin until V2.3's exact declaration contract is frozen and synthetically qualified.

## What is deliberately not claimed

This review does not claim:

- capture `clockSync.sha256` bytes are identical to structural `clockSync` JSON bytes;
- raw pitch/birth sensor evidence bytes are identical to decoded `pitchLatch`/`birth` structural streams;
- any existing real hardware or real capture is valid;
- V2.3/V1.2 can substitute for real calibration or untouched correctness validation.

The point of the proposed binding is precisely to distinguish raw evidence identities from deterministic decoded structural-audit output identities without conflating them.

## Required next order

1. Commit this review before new bridge code.
2. Update the canonical current-state checkpoint.
3. Freeze Capture Manifest V2.3 Structural-Audit Input Binding preregistration before implementation.
4. Implement/test V2.3 synthetically and freeze its result.
5. Only then preregister Structural Audit V1.2 against the exact V2.3 shape.
6. Keep all hardware/correctness/customer authorization closed throughout.

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
