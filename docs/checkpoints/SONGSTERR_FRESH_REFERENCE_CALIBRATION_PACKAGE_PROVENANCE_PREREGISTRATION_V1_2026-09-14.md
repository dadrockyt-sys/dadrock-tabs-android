# Songsterr Fresh — Reference Calibration Package Provenance Preregistration V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: FROZEN SOFTWARE CONTRACT / SYNTHETIC CI ONLY

## Purpose

Freeze the zero-additional-cost software contract that a future NON_HOLDOUT physical-reference calibration package must satisfy before it can be bound into any future purpose-built holdout capture manifest.

This closes a specific provenance gap. Capture-manifest V2/V2.1 already requires a `calibrationId`, calibration SHA, hardware-configuration SHA, clock-sync ID, derivation-configuration SHA and evidence hashes for admitted takes. The bench-qualification authority additionally requires the calibration package itself to preserve and bind hardware/configuration identity, calibration-fixture identity, raw calibration sources, deterministic decoder/configuration identity, derived calibration outputs and the calibration information-firewall declarations. This V1 contract freezes that package-level binding without performing real calibration.

No real hardware, bench capture, holdout capture, Basic Pitch, V6, correctness scoring, protected-song material, reserved Guitar Fretboard Notes source, archived V143/Gomyway material, or evaluated-audio-derived truth is authorized.

## Frozen authority

This contract derives only from already-frozen purpose-built authority:
- expanded purpose-built design commit `e37d2b4662db949157d2cf4797370f05648b6940`;
- physical-reference semantics commit `ea5f50212cd1cd3794c65cb648a4d781e49e4082`;
- capture-QA / structural gate matrix commit `2b191b39f2f1c19564f1353381779acbc96fbeda`;
- hardware/calibration necessity + bench qualification gate commit `a0279b8c48c51176678229abfa92576b1d1c0c95`;
- capture-manifest V2.1 implementation commit `72e8861f50680f45e586eb1e1352db59bda1f0ae`;
- synthetic hardware-marker clock-map result checkpoint commit `79293a7632915fc67f5b7ee0ac2242466ec83ea7`.

The inherited structural timing bound remains exactly `0.025 s`. This contract does not create empirical drift, jitter, dropout, debounce, hysteresis, saturation or other physical thresholds.

## Contract identity

Top-level contract literal:
`songsterr-fresh-purpose-built-reference-calibration-package-v1`

The validator is declaration-and-file-integrity software. It may read only explicitly supplied calibration-package files. In current CI all such files must be synthetic fixtures generated inside CI. It must not use network access, candidate/holdout media, evaluated song audio, model output or external corpora.

## Required package fields

A package declaration must contain all of the following.

### Core identity and firewall
- nonempty `calibrationId`;
- `usedHoldoutData:false`;
- `usedModelOutputs:false`;
- `derivedFromEvaluatedAudio:false`;
- finite nonnegative `maxAbsoluteOnsetErrorSeconds` not greater than the inherited `0.025 s` bound.

### Hardware/configuration binding
- nonempty `hardwareConfiguration.configurationId`;
- valid SHA-256 `hardwareConfiguration.sha256`;
- nonempty `hardwareConfiguration.path`;
- nonempty `hardwareConfiguration.firmwareVersion`;
- valid SHA-256 `instrumentSetupSha256`;
- nonempty `hardwareIdentities` list; each entry has nonempty `componentId`, nonempty `immutableIdentity`, and nonempty `role`; component IDs and immutable identities are unique within the package;
- `wiringTopology` with nonempty `topologyId`, nonempty `path`, valid SHA-256 `sha256`.

The validator must verify the declared SHA-256 for every readable package file against its actual bytes.

### Calibration fixture identity
`calibrationFixture` must contain nonempty `fixtureId`, nonempty `path`, valid SHA-256 `sha256`, with the file hash verified from bytes.

### Deterministic decoder/configuration identity
`decoder` must contain:
- nonempty `decoderId`;
- nonempty `softwareVersion`;
- nonempty `code.path` + valid/verified `code.sha256`;
- nonempty `configuration.path` + valid/verified `configuration.sha256`.

The decoder/configuration hashes are immutable identity plumbing only. Synthetic CI does not prove a future real decoder is physically correct.

### Raw calibration source inventory
`rawSources` must be a nonempty list. Every entry contains:
- nonempty unique `sourceId`;
- nonempty `path`;
- valid/verified `sha256`;
- nonempty `roles` list using only the frozen role vocabulary:
  - `physical_pitch_state`
  - `event_birth`
  - `clock_sync`
  - `sensor_health`

Across the package, role coverage must include at least `physical_pitch_state`, `event_birth`, and `clock_sync`. A single preserved raw file may legitimately carry multiple roles; the contract therefore does not invent a one-file-per-role requirement.

Every raw source must declare `nonHoldout:true`, `usedModelOutputs:false`, and `derivedFromEvaluatedAudio:false`.

### Derived calibration output inventory
`derivedOutputs` must be a nonempty list. Every entry contains nonempty unique `outputId`, nonempty `path`, valid/verified `sha256`, and exactly one frozen output role:
- `physical_string_fret_mapping`
- `event_birth_calibration`
- `hardware_timing_proof`
- `technique_capability_matrix`
- `acquisition_qa_configuration`

All five output roles are required exactly once. The contract binds the artifact identities; it does not manufacture physical PASS evidence in synthetic CI.

## File-path and integrity rules

- Paths must be relative POSIX-style paths rooted beneath an explicitly supplied package root.
- Absolute paths, `..` traversal, empty components and paths resolving outside the package root fail closed.
- A declared package path may be referenced only once across hardware configuration, wiring topology, calibration fixture, decoder code/configuration, raw sources and derived outputs. This prevents one byte artifact from silently masquerading as multiple provenance objects.
- Every declared SHA-256 must be lowercase 64-hex and must match actual file bytes.
- Missing/unreadable files fail closed.

## Canonical package binding

After successful validation, the validator must produce a deterministic canonical binding object containing only the validated semantic declaration and the verified file SHA-256 values, sorted deterministically. It must report `packageBindingSha256 = SHA256(canonical_json(binding_object))`.

The canonical binding must not contain absolute local filesystem paths, timestamps generated at validation time, random IDs, environment-specific paths or nondeterministic ordering. Identical package declarations and identical file bytes must produce byte-identical validation JSON and the same `packageBindingSha256`.

This package binding is the software identity intended for future capture-manifest integration. V1 does not modify the existing capture-manifest contract and does not authorize holdout capture.

## Fail-closed semantic prohibitions

The package fails if any declaration asserts or implies:
- use of holdout data;
- use of Basic Pitch/V6/model output;
- derivation from evaluated audio for authoritative reference calibration;
- missing physical-pitch/event-birth/clock-sync raw provenance;
- missing decoder/configuration identity;
- missing required derived-calibration identity;
- hash mismatch or unsafe path;
- duplicate component/source/output identity where uniqueness is required.

The validator must never inspect musical correctness or use evaluated audio to rescue an invalid package.

## Synthetic contract tests before any real package use

CI must use generated synthetic text/binary fixtures only and enforce at minimum:
1. a complete valid synthetic package passes;
2. output is byte-deterministic across repeated validation;
3. package binding is independent of the absolute temporary directory;
4. every required top-level firewall declaration fails closed when violated;
5. timing error above `0.025 s` fails closed and equality is allowed;
6. malformed/mismatched hashes fail closed;
7. missing files fail closed;
8. absolute/path-traversal escapes fail closed;
9. duplicate package paths fail closed;
10. duplicate hardware/source/output identities fail closed;
11. missing required raw roles fails closed;
12. forbidden/unknown raw role fails closed;
13. missing or duplicate derived-output role fails closed;
14. decoder code/configuration identity is mandatory;
15. hardware/configuration, fixture, topology and instrument-setup identities are mandatory;
16. downstream authorization fields remain false/zero.

## Frozen interpretation

A synthetic CI PASS proves only that the package-provenance software contract is deterministic and fail-closed on the frozen synthetic fixtures. It does not prove a real calibration package exists, a physical apparatus qualifies, the reference decoder is physically accurate, empirical acquisition-QA thresholds are valid, a real holdout can begin, V6 is correct, or customer delivery is authorized.

Real calibration remains paused by the budget boundary. When physical calibration eventually becomes separately authorized and exists, this same frozen contract may validate its package identity without changing the contract from holdout observations.

## Downstream authorization boundary

Must remain:
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

## Execution order

1. Commit this preregistration before implementation/result observation.
2. Update the canonical current-state checkpoint with this frozen contract and exact next order.
3. Implement the validator without changing the frozen semantics.
4. Add synthetic tests before official harness execution.
5. Add ordinary GitHub CPU workflow; tests run before the official synthetic fixture validation.
6. Freeze run/job/artifact/result identities in a dedicated result checkpoint.
7. Update the canonical current-state checkpoint again.
