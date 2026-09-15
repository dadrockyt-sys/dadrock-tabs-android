# Songsterr Fresh — Reference-Blind Structural Audit V1.1 Provenance-Result Bridge Preregistration

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: FROZEN BEFORE IMPLEMENTATION / SYNTHETIC CI ONLY

## Purpose

Freeze one narrow additive version over the already-frozen reference-blind structural-audit V1 so the audit can hash-before-parse verify the calibration-provenance validation-result bytes bound by capture-manifest V2.2 and prove that those bytes commit to the same canonical calibration package identity as the admitted capture population.

This preregistration responds only to the confirmed gap documented in:
`docs/checkpoints/SONGSTERR_FRESH_REFERENCE_BLIND_STRUCTURAL_AUDIT_PROVENANCE_BRIDGE_REVIEW_V1_2026-09-14.md`, commit `66b1d3d19913e5218c3f1a71a88b399241ea5350`.

V1.1 must not redesign the V1 structural audit, calibration package, physical reference semantics, timing threshold, overlap rules, MIDI range, holdout governance, V6, scoring, policy, or customer delivery.

No real hardware, real calibration, real holdout capture, evaluated DI/audio, Basic Pitch, V6, correctness, protected-song material, reserved Guitar Fretboard Notes source, archived V143/Gomyway material, or model/correctness output is authorized.

## Frozen authority

V1.1 inherits without weakening:

- structural-audit V1 preregistration commit `067875e3aa1538ff5483b74cc9071b00e9e82b07`;
- structural-audit V1 implementation/test/workflow head `8f4b41ce2cff075a6e7be25032142a0e8288b7be`;
- structural-audit V1 evidence checkpoint commit `df7eb9edacb170ab24e2c200b1c0a8028625f87a`;
- physical-reference semantics commit `ea5f50212cd1cd3794c65cb648a4d781e49e4082`;
- inherited timing bound `0.025 s`;
- Reference Calibration Package Provenance V1 result checkpoint commit `c57156fec7c5000563552c8cb128366956b8c95b`;
- capture-manifest V2.2 result checkpoint commit `7d2d05ec365bbdb1aced574f7caf1865795fbc23`.

## Contract identity

Top-level V1.1 result contract literal:
`songsterr-fresh-purpose-built-reference-blind-structural-audit-v1.1`

Accepted calibration-provenance result contract literal:
`songsterr-fresh-purpose-built-reference-calibration-package-provenance-v1`

Structural population identity version literal:
`reference-blind-structural-audit-v1.1-provenance-bridge-v1`

## Original four-source V1 boundary — UNCHANGED

V1.1 must call/inherit V1 for the original exact source set:

- `hardware`;
- `birth`;
- `pitchLatch`;
- `clockSync`.

Each original source remains an immutable JSON byte stream with its expected SHA-256 identity. V1's behavior remains authoritative:

- hash all four original raw streams before any JSON parse;
- reject missing/extra original source names or expected hashes;
- reject any source hash mismatch before semantic parsing;
- preserve all zero-anomaly blockers, timing checks, physical-note derivation, overlap checks, MIDI range checks, provenance declarations and authorization boundaries exactly.

V1.1 must not change V1's `0.025 s` bounds, physical event semantics, derived note-event bytes/fields, blocker definitions, or V1-derived note population identity.

## Fifth provenance-result byte stream

V1.1 adds one independent byte stream supplied separately from the four-source V1 mapping:

- logical source name: `calibrationProvenanceResult`;
- raw value: bytes only;
- expected SHA-256: lowercase 64-hex.

V1.1 must hash the provenance-result raw bytes before any JSON decoding/parsing of that stream.

Fail closed before provenance semantic parsing if:

- the raw value is not bytes;
- the expected SHA-256 is malformed;
- the actual SHA-256 differs from the expected SHA-256.

The fifth stream is not inserted into V1's four-source mapping and must not weaken V1's rejection of extra original source names.

## V2.2 identity declarations supplied to V1.1

V1.1 receives exactly two already-bound declaration identities from the V2.2 capture-manifest layer:

- `declaredProvenanceResultSha256` — valid lowercase 64-hex;
- `declaredCalibrationPackageBindingSha256` — valid lowercase 64-hex.

These are metadata identities only. V1.1 must not open the capture manifest, evaluated audio, calibration package files, or any model/correctness output to obtain them.

The provenance stream expected SHA-256 must equal `declaredProvenanceResultSha256` exactly. A disagreement is a structural bridge failure.

## Frozen provenance-result semantic checks

Only after the fifth stream hash check succeeds may V1.1 UTF-8 decode and JSON parse it.

The parsed object must satisfy all of these:

1. top-level JSON object;
2. `contract` exactly `songsterr-fresh-purpose-built-reference-calibration-package-provenance-v1`;
3. `contractValid` exactly `true`;
4. `errors` exactly an empty list;
5. `packageBindingSha256` valid lowercase 64-hex;
6. parsed `packageBindingSha256` equals `declaredCalibrationPackageBindingSha256` exactly;
7. parsed `packageBinding` is an object;
8. `SHA256(canonical_json(packageBinding))` equals parsed `packageBindingSha256` exactly;
9. package binding firewall declarations `usedHoldoutData`, `usedModelOutputs`, and `derivedFromEvaluatedAudio` are all exactly `false`;
10. package binding `maxAbsoluteOnsetErrorSeconds` is finite, nonnegative and <= inherited `0.025 s`;
11. package binding has nonempty `calibrationId`;
12. package binding has a decoder object with nonempty `decoderId` and `softwareVersion` and valid SHA-256 identities at `decoder.code.sha256` and `decoder.configuration.sha256`.

V1.1 does not re-open or re-verify the package files listed by the provenance result. Provenance V1 remains the package-level validator. V1.1 verifies the immutable validation-result bytes and the canonical package identity they claim.

## Bridge blocker accounting

V1.1 adds one result blocker count:

- `calibrationProvenanceBridgeViolationCount`.

It increments for bridge/hash/parse/semantic/cross-identity failures from the fifth stream or V2.2 identity declarations. It does not replace or reinterpret any V1 blocker.

Any nonzero V1 blocker or nonzero `calibrationProvenanceBridgeViolationCount` forces:

- `contractValid:false`;
- `datasetStructurallySuitable:false`;
- `authoritativeStructuralSuitabilityEstablished:false`.

V1.1 must not repair/drop/ignore a V1 event or provenance bridge failure.

## Frozen result identity

V1.1 must preserve V1's original `derivedPopulationSha256` as diagnostic identity and expose it as:

- `inheritedV1DerivedPopulationSha256`.

V1.1 must compute a new structural population binding:

`SHA256(canonical_json({
  "populationIdentityVersion": "reference-blind-structural-audit-v1.1-provenance-bridge-v1",
  "inheritedV1DerivedPopulationSha256": <V1 SHA>,
  "calibrationProvenanceResultSha256": <verified fifth-stream SHA>,
  "calibrationPackageBindingSha256": <verified package binding SHA>
}))`

and expose it as V1.1 `derivedPopulationSha256`.

This augmentation binds provenance identity to the already-derived structural note population without altering any note event, onset, pitch, release, or V1 blocker semantics.

If V1 fails before producing a derived population SHA, V1.1 `derivedPopulationSha256` must be null.

## Frozen result fields

V1.1 deterministic result must include at least:

- `contract`;
- `contractValid`;
- sorted `errors`;
- inherited `sourceSha256` for the original four streams;
- `calibrationProvenanceSourceSha256` with expected/actual/matches;
- `calibrationProvenanceBridgeViolationCount`;
- `calibrationProvenanceResultContract` when parsed successfully;
- `calibrationProvenanceResultSha256` when verified;
- `calibrationPackageBindingSha256` when verified;
- `calibrationPackageDecoderId` when verified;
- `calibrationPackageDecoderSoftwareVersion` when verified;
- `calibrationPackageDecoderCodeSha256` when verified;
- `calibrationPackageDecoderConfigurationSha256` when verified;
- `populationIdentityVersion`;
- `inheritedV1DerivedPopulationSha256`;
- augmented V1.1 `derivedPopulationSha256`;
- inherited `derivedNoteEventCount` unchanged;
- inherited V1 blocker counts unchanged plus the bridge blocker count;
- `datasetStructurallySuitable` true only if both V1 and bridge pass;
- `authoritativeStructuralSuitabilityEstablished` true only if both V1 and bridge pass;
- all downstream authorization false/zero.

## Synthetic contract tests before official harness

Tests must run before official synthetic harness execution and cover at minimum:

1. complete V1.1 synthetic inputs PASS;
2. original V1 four-source nominal semantics still PASS through the wrapper;
3. provenance raw value not bytes FAIL;
4. malformed provenance expected SHA FAIL;
5. provenance raw-byte SHA mismatch FAIL before provenance parse;
6. malformed declared V2.2 provenance SHA FAIL;
7. malformed declared V2.2 package-binding SHA FAIL;
8. expected provenance SHA differs from declared V2.2 provenance SHA FAIL;
9. provenance bytes invalid UTF-8/JSON FAIL after successful hash;
10. provenance result contract mismatch FAIL;
11. `contractValid:false` provenance result FAIL;
12. nonempty provenance result `errors` FAIL;
13. malformed parsed package-binding SHA FAIL;
14. parsed package-binding SHA mismatch to V2.2 declaration FAIL;
15. parsed package-binding canonical hash mismatch FAIL;
16. any package firewall violation FAIL;
17. package timing above `0.025 s` FAIL;
18. missing calibration ID FAIL;
19. missing decoder ID/version FAIL;
20. malformed decoder code/configuration SHA FAIL;
21. original V1 hash mismatch still FAIL before V1 parsing;
22. original V1 structural blocker still fails even with valid provenance bridge;
23. V1.1 augmented population SHA changes when provenance-result SHA identity changes;
24. V1.1 augmented population SHA changes when package-binding identity changes;
25. original V1 derived population SHA remains unchanged by the bridge;
26. canonical validation output is byte-deterministic;
27. all authorization remains false/zero even on PASS.

## Official synthetic harness

The ordinary GitHub CPU workflow must:

1. compile V1.1 implementation/tests;
2. run all synthetic contract tests first;
3. only if tests pass, generate frozen nominal V1 raw reference streams and a frozen nominal Provenance V1 result byte stream;
4. call the V1.1 wrapper with exact expected hashes and V2.2-declared identities;
5. print canonical source/provenance/package/population hashes and closed authorization summary;
6. upload the canonical V1.1 validation result artifact.

No network access or external corpus/media acquisition is permitted.

## Interpretation boundary

A synthetic V1.1 PASS proves only that:

- the original reference-blind V1 structural checks still pass on the frozen synthetic fixture;
- the provenance validation-result bytes were hash-verified before parse;
- the parsed successful provenance result commits to the same package identity declared by V2.2;
- those provenance identities are cryptographically bound into the V1.1 structural population identity.

It does not prove:

- physical sensor accuracy;
- real calibration validity;
- real hardware qualification;
- real holdout authority;
- correctness of a real structural population;
- Basic Pitch/V6 correctness;
- model validation;
- customer eligibility or delivery authority.

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
3. Implement V1.1 strictly as an additive wrapper over V1.
4. Add synthetic tests before official harness execution.
5. Add ordinary GitHub CPU workflow with tests first.
6. Freeze run/job/artifact/result identities in a dedicated V1.1 result checkpoint.
7. Update the canonical current-state checkpoint again.
