# Songsterr Fresh V6 — Proposed Purpose-Built V2 Schema + Synthetic-Test Plan

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **PROPOSAL ONLY / NON-AUTHORITATIVE / NO CAPTURE AUTHORITY**
Parent design: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_HOLDOUT_EXPANDED_DESIGN_2026-09-14.md`
Reference semantics: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_PHYSICAL_REFERENCE_SEMANTICS_V1_2026-09-14.md`
Gate matrix: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_CAPTURE_QA_STRUCTURAL_GATE_MATRIX_V1_2026-09-14.md`
Canonical state: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## 1. Purpose

Translate the paper-only physical-reference semantics and gate matrix into a concrete **proposed** shape for a future versioned manifest/capture-plan contract and its synthetic tests.

This document does not modify `purpose_built_capture_manifest_contract_v1.py`, `purpose_built_capture_manifest_semantic_guard_v1.py`, `purpose_built_capture_preregistration_binding_v1.py`, or any currently authoritative governance layer.

No V2 code is authoritative merely because it is described here. A future implementation must be separately reviewed, synthetic-tested, Git-bound, and integrated into the already-passed governance chain before it could authorize even a reference-blind structural audit.

## 2. Design rule: extend v1, do not weaken it

V2 should preserve all v1 protections unless a prospectively documented stronger invariant supersedes them:

- exact capture-plan binding;
- frozen slot roster;
- immutable slot identity across attempts;
- objective closed acquisition-failure vocabulary;
- frozen failure criteria;
- first acquisition-QA PASS must be admitted;
- no attempts after first PASS;
- strict attempt chronology;
- distinct evaluated-audio/reference identities;
- `derivedFromEvaluatedAudio:false`;
- fail-closed policy boundary;
- no model/correctness observations in manifest/plan;
- governance can authorize at most a reference-blind structural audit.

V2 should add explicit physical-reference provenance and hardware-clock semantics; it should not rewrite the passed Git/GitHub artifact-proof boundary.

## 3. Proposed contract identifiers

Names are proposals only:

- manifest contract: `songsterr-fresh-purpose-built-capture-manifest-v2`
- capture-plan contract: `songsterr-fresh-purpose-built-capture-plan-v2`
- physical-reference profile: `songsterr-fresh-physical-reference-profile-v1`
- structural-audit profile: `songsterr-fresh-purpose-built-structural-audit-profile-v1`

The profile identifiers should be explicit and versioned so semantics cannot drift while a generic “v2” label stays unchanged.

## 4. Proposed corpus-level manifest additions

Retain existing v1 corpus identity, rights, preregistration, and hardware fields, then add explicit structures equivalent to the following.

### 4.1 `referenceArchitecture`

Conceptual fields:

- `profileId`
- `profileDocumentPath`
- `profileDocumentSha256`
- `evaluatedAudioPathId`
- `physicalPitchReferencePathId`
- `eventBirthReferencePathId`
- `clockReferencePathId`
- `evaluatedAudioExcludedFromTruthDerivation: true`
- `modelOutputsExcludedFromTruthDerivation: true`
- `rawReferencePreservationRequired: true`

Required invariants:

- evaluated-audio identity must not equal any authoritative physical-reference identity;
- physical pitch and event-birth functions must be semantically declared even if one future physical device transports both signals;
- if one transport contains multiple logical planes, the configuration must identify distinct logical channels/records and preserve their raw provenance;
- model/evaluated-audio exclusions are exact required booleans, not optional declarations.

### 4.2 `referenceDecoder`

Conceptual fields:

- `decoderId`
- `implementationPath`
- `implementationBlobSha256` or other exact immutable source identity bound by the established Git proof model;
- `configurationSha256`
- `semanticProfileSha256`
- `calibrationBundleId`
- `calibrationBundleSha256`
- `deterministic: true`
- `evaluatedAudioInputAllowed: false`
- `modelInputAllowed: false`
- `manualPerEventEditingAllowed: false`

### 4.3 `clockArchitecture`

Conceptual fields:

- `clockMode`: enum such as `SHARED_HARDWARE_CLOCK` or `HARDWARE_SYNC_MARKERS`;
- `configurationSha256`;
- `mappingAlgorithmId`;
- `mappingConfigurationSha256`;
- `audioContentAlignmentAllowed: false`;
- `modelAlignmentAllowed: false`;
- `manualAlignmentAllowed: false`;
- prospective QA threshold identities rather than mutable inline values where useful.

V2 should reject any unrecognized clock mode.

### 4.4 `structuralAuditProfile`

Conceptual fields:

- `profileId`
- `documentPath`
- `documentSha256`
- `rejectionScopePolicyId`
- `toleranceConfigurationSha256`
- `repairAllowed: false`
- `retakeAfterAdmissionAllowed: false`
- `evaluatedAudioTruthInspectionAllowed: false`
- `modelInspectionAllowed: false`

## 5. Proposed capture-plan additions

### 5.1 Frozen reference capability profile

The capture plan should declare which physical techniques the frozen reference design can truthfully support.

Conceptual fields:

- `supportedTechniqueSemanticClasses`
- `prospectivelyExcludedTechniqueSemanticClasses`
- `referenceProfileId`
- `referenceProfileSha256`

Every planned slot must be compatible with that frozen capability declaration. Unsupported technique classes must be excluded prospectively, not dropped after capture.

### 5.2 Frozen hardware/configuration identities

The plan should bind:

- hardware configuration SHA;
- allowed firmware/software versions or exact identities;
- reference decoder/configuration SHA;
- calibration bundle SHA;
- clock/sync configuration SHA;
- acquisition-QA profile SHA;
- structural-audit profile SHA.

### 5.3 V2 acquisition-failure vocabulary

The plan may contain only a closed code vocabulary from the implemented V2 contract. A proposed superset, subject to later exact review, is:

Existing v1-compatible classes:

- `ABSENT_REFERENCE_CHANNEL`
- `CLIPPING_LIMIT_EXCEEDED`
- `DEVICE_DISCONNECT`
- `MISSING_OR_CORRUPT_FILE`
- `TRANSPORT_FAILURE`
- `WRONG_SAMPLE_RATE_OR_FORMAT`

Physical-reference classes proposed by the gate matrix:

- `MISSING_HARDWARE_SYNC_EVIDENCE`
- `CLOCK_DRIFT_LIMIT_EXCEEDED`
- `CLOCK_JITTER_LIMIT_EXCEEDED`
- `REFERENCE_SENSOR_DROPOUT_LIMIT_EXCEEDED`
- `REFERENCE_SENSOR_SATURATION_LIMIT_EXCEEDED`
- `REFERENCE_SENSOR_STUCK_STATE`
- `REFERENCE_STREAM_MALFORMED`
- `CONFIGURATION_IDENTITY_MISMATCH`
- `CALIBRATION_IDENTITY_MISMATCH`
- `REQUIRED_RAW_REFERENCE_STREAM_MISSING`

`MALFORMED_MIDI_STREAM` should not automatically carry forward as an authoritative physical-reference concept unless V2 still contains a separately justified MIDI transport. If retained for an optional/non-authoritative stream, its role must be explicit and cannot substitute for raw physical truth.

Every enabled code must have an exact frozen criterion. Plans may use a subset of the implemented closed vocabulary but cannot invent new strings.

### 5.4 Criterion representation

Free-text criteria alone are insufficient for machine-verifiable numeric conditions. Proposed V2 direction:

Each enabled code should bind a criterion object with:

- `criterionId`
- `criterionVersion`
- `criterionDocumentSha256`
- optional machine-readable scalar limits with explicit units when appropriate;
- `evaluationImplementationId`/SHA if machine evaluated;
- `observablePlane` enum;
- `modelOrCorrectnessDependencyAllowed: false`.

For example, clock drift criteria should bind units and a frozen numerical threshold rather than only saying “too much drift.”

The exact numeric values remain TBD until prospective non-holdout calibration planning.

## 6. Proposed attempt-level manifest additions

For each attempt, retain v1 attempt/slot/player/exercise/category/chronology/acquisition-QA fields and add immutable physical-reference identities.

### 6.1 `evaluatedAudio`

Retain path + SHA and add, where useful:

- `pathId`/logical source identity;
- format/sample-rate/channel metadata required by the frozen technical QA profile;
- capture configuration ID.

### 6.2 `physicalPitchReferenceRaw`

Required on every admitted V2 take:

- `path`
- `sha256`
- `format`
- `logicalPathId`
- `configurationSha256`
- `calibrationId`
- raw clock identity/tick unit.

### 6.3 `eventBirthReferenceRaw`

Required on every admitted V2 take:

- `path`
- `sha256`
- `format`
- `logicalPathId`
- `configurationSha256`
- `calibrationId`
- raw clock identity/tick unit.

If pitch and birth evidence share one transport file, V2 must still bind distinct logical stream/channel identities and prove the decoder uses the intended independent semantics. Sharing a container must not collapse the semantic planes.

### 6.4 `clockSyncRaw`

Required when not inherent in a shared hardware clock:

- `path`
- `sha256`
- `format`
- `clockMode`
- `configurationSha256`.

### 6.5 `derivedReference`

For admitted takes, conceptual fields:

- `path`
- `sha256`
- `format`
- `decoderId`
- `decoderImplementationSha256`
- `decoderConfigurationSha256`
- `semanticProfileSha256`
- `calibrationId`
- `clockMappingConfigurationSha256`
- `rawPitchReferenceSha256`
- `rawBirthReferenceSha256`
- `rawClockReferenceSha256` where applicable;
- `derivedFromEvaluatedAudio: false`
- `derivedFromModelOutput: false`
- `manualPerEventEditing: false`.

The V2 validator should reject a derived reference whose declared raw hashes do not exactly match the attempt's authoritative raw objects.

## 7. Proposed acquisition-QA result structure

Instead of only `{status, reason}`, V2 can retain that simple compatibility layer while binding objective evidence:

- `status`: `PASS` or `FAIL`
- `reason`: frozen code or empty on PASS
- `criterionId` when FAIL
- `criterionConfigurationSha256`
- `machineEvidence` object limited to frozen technical observables;
- `evaluatedAtUtc`
- `evaluatorImplementationSha256` when machine-generated.

The schema must forbid model/correctness keys anywhere inside `machineEvidence`.

A PASS must still be admitted. A FAIL may not be admitted. The first PASS ends the slot chronology.

## 8. Proposed sensor/clock evidence constraints

Machine evidence should use closed field vocabularies per criterion rather than arbitrary JSON blobs where feasible.

Examples of acceptable prospective observables:

- missing stream boolean;
- file hash/schema validation result;
- hardware clock lock status;
- sync-marker count;
- drift in explicitly declared units;
- jitter/residual in explicitly declared units;
- dropout sample/tick count or fraction;
- saturation count/fraction;
- stuck-state duration/ticks;
- actual versus expected configuration/calibration identity.

Explicitly forbidden as acquisition-QA evidence:

- note correctness;
- pitch agreement with expected score;
- onset agreement with audio;
- Basic Pitch/V6 outputs;
- precision/recall/TP/FP/FN;
- waveform/spectrogram judgement;
- subjective performance quality;
- “hard take”/“bad feel”/“play again” operator flags.

## 9. Proposed population identity expansion

The deterministic admitted-population identity hash should include enough reference provenance to make later substitution detectable.

At minimum, each admitted row should bind:

- attempt/slot/player/exercise/category;
- attempt number;
- evaluated DI path/SHA;
- raw pitch-reference path/SHA;
- raw event-birth-reference path/SHA;
- raw clock/sync path/SHA when applicable;
- decoder implementation/config SHA;
- semantic profile SHA;
- calibration ID/SHA;
- hardware configuration SHA;
- derived reference path/SHA.

Sorted canonical population serialization remains deterministic.

A view/effect/reamp ID may be stored as non-counting metadata, but cannot create another admitted population row for the same underlying performance.

## 10. Proposed forbidden observation vocabulary expansion

The v1 forbidden observation scanner should remain and be expanded if V2 adds flexible nested evidence objects.

Potential normalized forbidden keys include existing model/correctness keys plus terms such as:

- `modelagreement`
- `basicpitchagreement`
- `audioonset`
- `spectralonset`
- `waveformalignment`
- `dynamictimewarping`
- `dtwalignment`
- `manualonsetcorrection`
- `precision`
- `recall`
- `f1`
- `truepositive`
- `falsepositive`
- `falsenegative`
- `correctnessdecision`

Key scanning alone is not a security boundary; schema whitelisting of acquisition evidence is stronger and preferred.

## 11. Proposed authority outputs

Even a perfect V2 contract/binding/provenance pass should emit only fail-closed authority equivalent to:

- `manifestContractValid:true/false`
- `planBindingValid:true/false`
- `physicalReferenceProfileBound:true/false`
- `clockProfileBound:true/false`
- `calibrationBound:true/false`
- `rosterExactlyBound:true/false`
- `gitPreregistrationBindingEstablished:true/false` only at the existing appropriate provenance layer;
- `hostedArtifactProofEstablished:true/false` only at the existing appropriate governance layer;
- `mayAdvanceToReferenceBlindStructuralAudit:true/false`
- `authoritativeStructuralSuitabilityEstablished:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- frozen policy boundary with `modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`.

No manifest contract alone can assert that physical sensors measured reality correctly. It can prove declarations, identities, chronology, provenance, and governance prerequisites; the reference-blind structural audit remains separate.

## 12. Synthetic-test plan — baseline compatibility

Future V2 implementation must prove all v1 protections remain effective.

Required positive tests:

- minimal valid V2 manifest/plan passes declaration/binding layers while remaining model/correctness unauthorized;
- multiple failed attempts followed by first objective PASS admits exactly that first PASS;
- exact roster/identity match succeeds;
- deterministic population hash stable across object-key ordering.

Required negative tests:

- PASS marked unadmitted fails;
- FAIL marked admitted fails;
- later attempt after first PASS fails;
- duplicate attempt number fails;
- timestamp chronology reversal fails;
- slot player/exercise/category mutation fails;
- plan slot missing from manifest fails;
- unplanned manifest slot fails;
- changed failure-reason vocabulary fails;
- missing criterion for enabled failure code fails;
- model/correctness observation field anywhere forbidden fails;
- policy boundary change fails.

## 13. Synthetic-test plan — physical reference separation

Required negative fixtures:

- evaluated DI path/hash reused as raw pitch reference -> fail;
- evaluated DI path/hash reused as event-birth reference -> fail;
- derived reference declares `derivedFromEvaluatedAudio:true` -> fail;
- derived reference declares model dependency -> fail;
- manual-per-event editing flag true -> fail;
- missing raw pitch reference on admitted take -> fail;
- missing raw event-birth reference on admitted take -> fail;
- missing clock stream when clock mode requires one -> fail;
- pitch raw hash cited by derived reference differs from attempt raw hash -> fail;
- birth raw hash mismatch -> fail;
- clock raw hash mismatch -> fail;
- decoder/config/calibration mismatch -> fail;
- reference logical path IDs collapse to evaluated-audio ID -> fail;
- unrecognized physical-reference profile -> fail.

Positive fixture:

- one container file carrying separately identified raw pitch and excitation channels is allowed only if the frozen profile explicitly allows that transport and distinct logical channel identities/provenance validate. It must not be accepted merely because file hashes differ or match.

## 14. Synthetic-test plan — acquisition failure anti-relabeling

For every implemented V2 failure code:

- code absent from plan vocabulary -> manifest using it fails;
- criterion missing -> fail;
- criterion ID/config differs from plan -> fail;
- evidence uses unapproved field -> fail;
- evidence contains model/correctness field -> fail;
- threshold units missing/invalid for numeric criterion -> fail;
- FAIL reason does not correspond to machine evidence under deterministic evaluator -> fail where the contract can verify it;
- PASS carrying a failure reason -> fail;
- FAIL after a previous PASS in same slot -> fail because later attempt forbidden.

Cross-stage anti-relabel tests:

- semantic ambiguity labeled `REFERENCE_SENSOR_DROPOUT_LIMIT_EXCEEDED` without objective dropout evidence -> fail;
- expected-score mismatch labeled transport failure -> fail;
- Basic Pitch disagreement labeled sensor failure -> fail;
- post-admission structural defect inserted as an acquisition-QA reason by mutating manifest -> fails hash/chronology/provenance binding.

## 15. Synthetic-test plan — clock/sync

Positive tests:

- shared-clock profile with required identity and no separate sync file passes declaration layer;
- hardware-sync-marker profile with bound raw sync file/config passes declaration layer.

Negative tests:

- sync-marker mode without sync file -> fail;
- audio-content alignment flag true -> fail;
- model alignment flag true -> fail;
- manual alignment flag true -> fail;
- unrecognized clock mode -> fail;
- clock configuration mismatch -> fail;
- declared hardware-only mapping algorithm identity mismatch -> fail;
- threshold changed between plan and manifest -> fail.

The declaration layer should not compute a real holdout time transform; raw-byte structural/alignment audit remains a later separate phase.

## 16. Synthetic-test plan — provenance and immutable population

Required negatives:

- rights document SHA mismatch -> fail;
- protected-song exclusion false -> fail;
- calibration bundle missing/mismatched -> fail;
- semantic-profile document hash mismatch -> fail;
- structural-audit-profile hash mismatch -> fail;
- hardware configuration changed mid-population without prospectively allowed identity in plan -> fail;
- same underlying take duplicated under a second view ID -> fail if the population identity/underlying-take key reveals duplication;
- derived reference output swapped between attempts -> fail;
- raw reference swapped between attempts -> fail;
- population row omitted after capture -> roster/binding fail.

## 17. Proposed underlying-performance identity

To harden anti-inflation, V2 should consider a required `underlyingPerformanceId` frozen at slot/attempt capture and included in population identity.

Rules:

- every admitted slot has exactly one underlying performance ID;
- different encodings/views/effects of one take share that ID;
- only one admitted independent-evidence row may count per underlying performance ID;
- `underlyingPerformanceId` cannot be reassigned after capture;
- ID construction must not rely on model/correctness output.

This would make the “one real take, many files” rule machine-verifiable rather than purely documentary.

## 18. Proposed session and instrument identity

V2 should bind stable pseudonymous IDs for diversity/strata provenance without exposing unnecessary personal data:

- `sessionId`
- `playerId`
- `instrumentSetupId`
- optional frozen tuning/capo/setup identity permitted by plan.

Exact personally identifying details should live only where necessary for rights/administration, not in the validation artifact if pseudonymous linkage suffices.

The future scoring strata remain the already-frozen player/category rules; this schema does not add a new statistical gate.

## 19. Proposed capture-finalization artifact

Before the reference-blind structural audit, a future deterministic finalization step could emit a declaration-only artifact containing:

- contract/plan/profile identities;
- all attempt chronologies;
- exact admitted roster;
- population SHA;
- raw source SHAs;
- decoder/calibration/configuration identities;
- acquisition-QA evidence/results;
- rights/provenance bindings;
- explicit fail-closed policy boundary;
- `mayAdvanceToReferenceBlindStructuralAudit` only.

The existing hosted-attestation/artifact-proof pattern can then bind this artifact without altering its trust-boundary architecture.

No correctness/model output belongs in this artifact.

## 20. Implementation sequencing if code is later authorized by project state

Coding itself is allowed as ordinary work under the current project authority, but V2 must remain non-authoritative until all prospective semantics are sufficiently frozen. Recommended sequence:

1. finalize paper-only field names/enums and unresolved threshold placeholders;
2. write isolated V2 schema/validator modules without changing v1;
3. add synthetic fixtures/tests for every positive/negative invariant above;
4. run ordinary local/GitHub CPU synthetic tests only;
5. audit for any path that could authorize more than structural audit;
6. bind exact V2 code/workflow blobs through the existing provenance pattern;
7. update documentation/checkpoint;
8. **still stop before real procurement/contact/calibration/capture unless the user explicitly authorizes those actions.**

V1 should remain available and unchanged as historical governance evidence; V2 should be a new versioned path, not an in-place semantic rewrite.

## 21. Items intentionally unresolved before V2 coding becomes authoritative

- exact hardware/sensor implementation;
- exact numeric QA thresholds;
- exact machine-readable criterion schema details;
- exact allowable technique set;
- exact clock mapping algorithm implementation;
- exact structural rejection/tolerance scope;
- exact capture-plan population size/player matrix;
- exact rights form text;
- exact storage system.

These do not prevent writing a **synthetic non-authoritative prototype** that fails closed around placeholders, but no real capture plan may use unresolved placeholders.

## 22. Standing authority boundary

Current state remains `DESIGN_ONLY` / proposal only.

This document authorizes none of:

- spending/procurement;
- vendor/performer contact;
- hiring;
- calibration recording;
- holdout recording;
- data acquisition;
- candidate-media access;
- Basic Pitch/V6 correctness;
- Modal/Vercel heavy-GPU/L4;
- Production/customer promotion.

Fail-closed policy remains:

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected-song embargoed

The next low-risk expansion is either (a) further paper refinement of unresolved V2 schema items or (b) an isolated **synthetic-only, non-authoritative V2 validator prototype** with no real media access and no change to v1 authority.
