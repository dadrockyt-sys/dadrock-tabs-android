# Songsterr Fresh — Reference Evidence Derivation Replay Review V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: REVIEW COMPLETE / FUNCTIONAL DERIVATION GAP CONFIRMED

## Scope

Review the complete synthetic software identity chain through:

1. Reference Calibration Package Provenance V1;
2. Capture Manifest V2.3 Structural-Audit Input Binding;
3. Structural Audit V1.2 Capture-Population Binding;
4. Structural Audit Population Completeness V1.

The question is narrow: does the current chain prove that the exact raw independent `pitchEvidence` and `birthEvidence` bytes declared for each admitted capture are deterministically decoded by the exact package-bound decoder code/configuration into the exact `pitchLatch` and `birth` structural byte streams later accepted by V1.2?

This is review/documentation only. It does not authorize real hardware, real calibration, real holdout capture, Basic Pitch, V6, correctness, protected-song execution, reserved Guitar Fretboard Notes sources, customer delivery, or archived V143/Gomyway work.

## Authority reviewed

- Reference Calibration Package Provenance V1 implementation/result, including package decoder code/config identities and raw/derived package file validation;
- Capture Manifest V2.3 implementation/result and `reference.structuralAuditInputs` binding;
- Structural Audit V1.2 implementation/result;
- Structural Audit Population Completeness V1 result checkpoint `ad2d9405793f41c20c74328f3abddd22256c686b`;
- Stage-0 Contact Replay V1 implementation `scripts/songsterr-fresh/stage0_contact_replay_v1.py`.

## What is already proven

### Provenance V1

Provenance V1 hash-verifies package files and commits the package binding to:

- decoder ID and software version;
- decoder code file SHA-256;
- decoder configuration file SHA-256;
- calibration/package/firewall identities.

The validator establishes immutable decoder **identity**. It does not execute the decoder.

Its synthetic fixture makes this distinction explicit: `decoder/decoder.py` is only `# synthetic decoder identity fixture`, and synthetic derived package outputs are created independently. Thus current synthetic Provenance V1 intentionally proves package/file identity, not executable derivation semantics.

### Capture Manifest V2.3

For every admitted reference, V2.3 commits one canonical `structuralAuditInputs` object containing both:

- raw-source lineage identities such as `pitchEvidenceSha256` and `birthEvidenceSha256`; and
- future decoded structural stream identities such as `pitchLatchStreamSha256` and `birthStreamSha256`;
- package binding and decoder configuration identity.

V2.3 validates that these declarations are internally consistent with the already-frozen capture/package declarations. It deliberately does not open raw evidence or structural output files and does not execute a decoder.

### Structural Audit V1.2

V1.2 hash-verifies the actual structural `hardware`, `birth`, `pitchLatch`, and `clockSync` byte streams and requires their hashes/declarations to equal the V2.3 binding for the admitted attempt. It also verifies the successful Provenance V1 result and package/decoder configuration identity.

V1.2 does not consume the raw admitted pitch/birth evidence bytes and does not execute the decoder.

### Population Completeness V1

Population Completeness V1 proves exact set equality between all V2.3 admitted bindings and all successful immutable V1.2 results. It operates on result bytes only and therefore cannot establish raw-evidence derivation semantics.

### Stage-0 Contact Replay V1 is not this proof

`stage0_contact_replay_v1.py` is explicitly a `NON_HOLDOUT_STAGE0` contact-topology replay over configuration, fixture, and scan-log byte streams. It validates contact-vector topology behavior. It never consumes an admitted holdout attempt's `pitchEvidence`/`birthEvidence`, package decoder code/configuration, or V2.3-bound `pitchLatch`/`birth` output streams.

It therefore cannot close the admitted raw-evidence -> decoded-structural-stream derivation chain.

## Confirmed gap

All current software contracts can pass while the following substitution remains logically possible:

1. an admitted attempt declares legitimate raw independent pitch/birth evidence SHAs;
2. the same V2.3 binding declares arbitrary but structurally valid `pitchLatch`/`birth` stream SHAs;
3. V1.2 receives byte streams matching those declared decoded SHAs and passes all structural checks;
4. the package/provenance chain names a legitimate decoder code/configuration identity;
5. no contract ever proves that executing that decoder on the admitted raw evidence reproduces those decoded stream bytes.

Thus co-declaration + byte identity + structural validity is not yet a functional derivation proof.

This is the final identified software lineage gap. It is not a correctness/model threshold and does not question the already-frozen physical-reference semantics.

## Decision

Add one final **Reference Evidence Derivation Replay Population V1** gate rather than another per-attempt bridge plus another aggregator.

The replay gate should consume the already-complete population result as upstream structural authority and perform the missing functional replay for the full admitted set in one contract.

This keeps responsibilities separated:

- Provenance V1: which decoder/package bytes are authoritative;
- V2.3: which raw evidence and decoded target byte identities belong to each admitted performance;
- V1.2: whether the exact decoded bytes are structurally valid;
- Population Completeness V1: whether every admitted performance has exactly one successful V1.2 result;
- Derivation Replay Population V1: whether the exact package-bound decoder, when run on every admitted raw pitch/birth evidence pair, reproduces the exact decoded `pitchLatch`/`birth` target identities.

## Required replay inputs for later preregistration

The final replay gate should consume, hash-before-parse where applicable:

1. one successful Capture Manifest V2.3 validation-result byte stream + expected SHA;
2. one successful Structural Audit Population Completeness V1 result byte stream + expected SHA;
3. one successful Provenance V1 validation-result byte stream + expected SHA;
4. the exact decoder code bytes whose SHA equals the Provenance V1 package binding's decoder code SHA;
5. the exact decoder configuration bytes whose SHA equals the package binding's decoder configuration SHA;
6. for every V2.3 admitted binding:
   - the full canonical `structuralAuditInputs` object + expected canonical SHA;
   - exact raw pitch-evidence bytes;
   - exact raw birth-evidence bytes.

The replay gate does not need the already-audited structural output bytes as inputs. Its generated output hashes can be compared directly to the binding's `pitchLatchStreamSha256` and `birthStreamSha256`; V1.2 has already proven that the audited structural bytes carry those same identities.

## Required cross-binding

Before decoder execution, the later contract should require:

- V2.3 result PASS and closed authorization;
- Population Completeness V1 PASS and closed authorization;
- completeness result names the same V2.3 result SHA and admitted-population SHA;
- Provenance V1 result PASS and closed authorization;
- each V2.3 binding's package binding SHA equals Provenance V1 `packageBindingSha256`;
- each V2.3 binding's `derivationConfigurationSha256` equals Provenance V1 decoder configuration SHA;
- actual decoder code/configuration byte SHAs equal Provenance V1 decoder code/configuration identities;
- every supplied binding canonical SHA matches exactly one V2.3 admitted binding entry;
- supplied attempt set equals the complete V2.3/completeness admitted set;
- each raw pitch-evidence byte SHA equals its binding `pitchEvidenceSha256`;
- each raw birth-evidence byte SHA equals its binding `birthEvidenceSha256`.

No raw-evidence semantic parsing is required by the replay validator itself before the decoder. Raw inputs are authoritative by byte identity.

## Frozen decoder runtime interface must be defined before implementation

The current package contract identifies decoder code/configuration bytes but does not define an executable runtime interface. Therefore the replay preregistration must freeze a deterministic execution interface before code.

Recommended minimal interface for the purpose-built pipeline:

- decoder artifact: UTF-8 Python source already hash-bound by Provenance V1;
- runtime: ordinary GitHub CPU Python 3.12 for synthetic qualification; real execution version must later be frozen with the real package before capture;
- invocation performed in an isolated temporary working directory with no network dependency;
- arguments supplied as exact filesystem paths:
  - `--pitch-evidence <path>`
  - `--birth-evidence <path>`
  - `--configuration <path>`
  - `--pitch-latch-output <path>`
  - `--birth-output <path>`
- exit code must be zero;
- exactly both required output files must exist;
- replay validator hashes output bytes without modifying/canonicalizing them;
- output SHA-256 must exactly equal V2.3 binding `pitchLatchStreamSha256` / `birthStreamSha256`.

Synthetic CI must use an executable synthetic decoder fixture. Do **not** mutate the already-completed Provenance V1 synthetic result to pretend its identity-only decoder fixture is executable. Instead construct a new synthetic package valid under the existing Provenance V1 contract whose decoder code actually implements this frozen replay interface, then validate that package with the unchanged Provenance V1 validator.

## Population-wide result identity

The final replay result should commit to:

- verified V2.3 result SHA;
- V2.3 admitted-population SHA;
- verified Population Completeness V1 result SHA and population-completeness SHA;
- verified Provenance V1 result SHA and package binding SHA;
- decoder code/configuration SHAs;
- sorted per-attempt rows containing:
  - attempt ID;
  - structural binding SHA;
  - raw pitch evidence SHA;
  - raw birth evidence SHA;
  - reproduced pitch-latch output SHA;
  - reproduced birth output SHA.

Population derivation replay may PASS only if every admitted attempt is present exactly once and both generated output identities match the V2.3 targets for every attempt.

## What the replay gate must not do

It must not:

- inspect evaluated DI/audio;
- invoke Basic Pitch or V6;
- compute correctness;
- modify/tune decoder code/configuration from replay observations;
- tolerate output normalization or approximate equality;
- substitute package synthetic calibration sources for admitted holdout evidence;
- change the 0.025 s timing rule or any structural rule;
- authorize real calibration/capture or customer delivery.

## Required next order

1. Commit this review before replay implementation.
2. Update the canonical current-state checkpoint with Population Completeness V1 completion and this confirmed functional derivation gap.
3. Freeze Reference Evidence Derivation Replay Population V1 preregistration, including the decoder runtime interface, before code.
4. Implement synthetic executable decoder/package fixture plus replay validator/tests.
5. Run ordinary GitHub CPU tests-first CI only, with at least two admitted attempts.
6. Freeze run/job/artifact/result identities.
7. Perform a final no-gap software-lineage review. If replay closes the chain and no new concrete gap is found, stop creating software gates; physical procurement/calibration/capture remains the next objectively necessary route and remains budget-paused.

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
