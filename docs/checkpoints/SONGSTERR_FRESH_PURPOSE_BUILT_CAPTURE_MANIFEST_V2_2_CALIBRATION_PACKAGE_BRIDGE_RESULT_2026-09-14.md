# Songsterr Fresh — Purpose-Built Capture Manifest V2.2 Calibration-Package Bridge Result

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: SYNTHETIC CONTRACT PASS / IDENTITY BRIDGE COMPLETE

## Authority

Gap review:
`docs/checkpoints/SONGSTERR_FRESH_CAPTURE_MANIFEST_CALIBRATION_PACKAGE_BRIDGE_REVIEW_V1_2026-09-14.md`
commit `abfd10ea953e2be313f847f626c405a2f3607dad`.

Frozen preregistration:
`docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_CAPTURE_MANIFEST_V2_2_CALIBRATION_PACKAGE_BRIDGE_PREREGISTRATION_2026-09-14.md`
commit `9596bfc745a5acdbb47b403eb3d39688ceb20ebd`.

The accepted implementation was corrected for strict preregistration conformance before this official result was accepted. Earlier provisional implementation/test/workflow commits (`5eb956d4710f714a1cffe009859ef85470a1f4ea`, `517aedaaa1164e79d62b3c70037b6201e61d3c45`, `052a3d4e33d5b93900001c3c35d7efcd22bf5f1c`) are superseded as implementation history and are not the authority for this result.

Accepted implementation:
- file: `scripts/songsterr-fresh/purpose_built_capture_manifest_contract_v2_2.py`;
- commit: `e3e3ae05ab0ab4a94a77e6c6e5be2466f618cf46`;
- blob/content SHA: `ea9635fb9012b2b07783cb4ef35834b0debfcfb1`.

Accepted synthetic tests:
- file: `scripts/songsterr-fresh/test_purpose_built_capture_manifest_contract_v2_2.py`;
- commit: `8feb390fe2bf506c9d5676774b0584eb65b680a6`;
- blob/content SHA: `1406b07aeacb33c05aa5e03c1cc5aaed1aeb118d`.

Accepted workflow:
- file: `.github/workflows/songsterr-fresh-purpose-built-capture-manifest-v2-2.yml`;
- commit/head: `f07b86c2149133714646025aa31e21e0017db17b`;
- blob/content SHA: `03eea92a66972d5bfa40636a6861bfb600d2c4f9`.

## Official GitHub CPU run

- workflow run: `34917541786`;
- job: `104218329349` (`synthetic-capture-manifest-v22`);
- head SHA: `f07b86c2149133714646025aa31e21e0017db17b`;
- conclusion: `success`;
- Python: `3.12.14` on ordinary GitHub-hosted Ubuntu CPU;
- compile step: PASS;
- synthetic contract tests ran before the official harness;
- test result: **24/24 PASS**;
- official frozen synthetic V2.2 declaration generation: PASS;
- official validator: PASS;
- canonical result upload: PASS.

Artifact:
- artifact name: `songsterr-fresh-purpose-built-capture-manifest-v2-2`;
- artifact ID: `10376813179`;
- uploaded ZIP size: `1,235` bytes;
- uploaded ZIP SHA-256: `6af8efbb303df43e61154ec605b316a6940eb87072b9393ed99e01e4e76b19df`;
- canonical result JSON SHA-256: `f315b2000a6c2ef5d270d5340944f325f081b0b2ebc27bc06e8894bfe61165a2`.

## Frozen synthetic result

Top-level result:
- `contract`: `songsterr-fresh-purpose-built-capture-manifest-v2.2`;
- `contractValid:true`;
- `packageBridgeValid:true`;
- `errors:[]`;
- `populationIdentityVersion`: `capture-manifest-v2.2-calibration-package-bridge-v1`;
- `mayAdvanceToReferenceBlindStructuralAudit:true` under the synthetic declaration contract only.

Bound provenance identity:
- validation result path: `calibration/reference-calibration-package-provenance-v1-result.json`;
- validation result SHA-256: `4fd62e62a855031bd3c189253bc04f004d271d53bf2b636c586c15b93e59e98f`;
- canonical package binding SHA-256: `735d276afc5bac7cd8e0e905ae42f8d4dc4bfae835ae013403ccdc31c4cf857c`.

Bound decoder identity:
- decoder ID: `synthetic-decoder-v1`;
- software version: `1.0.0-synthetic`;
- decoder code SHA-256: `56aecaa4ece3411f6833274c0323aafae0ffdbeb52ee2a1ad57903f216573aaf`;
- decoder configuration SHA-256: `3c9850cdd5085c2dc5230211b18d3362b7f0cef2d23be19b9af3b456df9a2777`.

Population identities:
- inherited V2.1 admitted-population SHA-256: `cb21ea5d6880a6955e12ca224ea2ded795f2a29134b175ec5198e84c22330c3b`;
- augmented V2.2 admitted-population SHA-256: `6806913257deb635fa5dabae3622015ae9ae7ae9246ff499aaf55a1961197b2e`;
- admitted population count: `1`;
- admitted underlying-performance count: `1`.

The V2.2 population identity now commits to both the canonical calibration-package binding SHA and the provenance validation-result SHA, in addition to inherited V2.1 admitted-row identity fields.

## What the 24 tests establish

The accepted suite verifies the frozen preregistration categories, including:
- V2.1 projection fails until the V2.2 package bridge is present;
- canonical package-binding hash verification;
- validation-result path safety and SHA identity;
- package contract/firewall enforcement;
- calibration ID, hardware configuration ID/SHA, instrument setup SHA and timing compatibility;
- inherited `0.025 s` maximum timing bound;
- decoder ID/version/code/configuration identity validity;
- admitted-reference package-binding citation;
- admitted-reference derivation-configuration equality to the bound decoder configuration;
- non-admitted attempts do not require admitted-reference bridge fields;
- inherited same-slot retry continuity and cross-slot underlying-performance uniqueness remain enforced;
- augmented population SHA changes when either package-binding identity or validation-result SHA identity changes;
- canonical validation output is byte-deterministic;
- all downstream authorization remains false/zero.

## Interpretation boundary

This PASS closes the **capture-manifest -> canonical calibration-package identity** plumbing gap in synthetic software. It does not establish physical sensing accuracy, real calibration validity, real holdout authority, structural suitability of any real population, Basic Pitch/V6 correctness, protected-song authority, model validation, customer eligibility, or delivery authority.

The V2.2 declaration stores the provenance validation-result path/SHA but deliberately does not open that file. Therefore the next permitted step is the separately preregistered-by-review question from V2.2: review whether the existing reference-blind structural audit must add hash-before-parse verification of the bound provenance validation-result bytes. Do not implement such an audit change unless a separate review confirms the gap and a new preregistration is frozen first.

## Authorization boundary

Unchanged after the synthetic PASS:
- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched. Archived V143/Gomyway remains closed.
