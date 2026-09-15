# Songsterr Fresh — Reference Evidence Derivation Replay Population V1 Preregistration

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: FROZEN BEFORE IMPLEMENTATION / SYNTHETIC CI ONLY

## Purpose

Freeze the final software-lineage gate identified by review commit `0a50220a089f22733d7066e5772da7e73d71f557`.

For every attempt admitted by one verified Capture Manifest V2.3 population, replay the exact package-bound decoder code/configuration on the exact admitted raw independent pitch/birth evidence bytes and require the exact generated `pitchLatch` / `birth` output byte hashes to equal the V2.3-bound structural target identities already structurally audited by V1.2 and population-complete under Population Completeness V1.

This is functional lineage/reproducibility only. It does not inspect evaluated audio, invoke Basic Pitch/V6, compute correctness, alter structural semantics, or authorize real physical work/customer delivery.

## Frozen authority

Inherits without weakening:

- Reference Calibration Package Provenance V1 result contract `songsterr-fresh-purpose-built-reference-calibration-package-v1`;
- Capture Manifest V2.3 contract `songsterr-fresh-purpose-built-capture-manifest-v2.3`;
- Structural Audit Population Completeness V1 contract `songsterr-fresh-purpose-built-reference-blind-structural-audit-population-completeness-v1`;
- physical-reference semantics `physical-reference-semantics-v1`;
- derivation-gap review commit `0a50220a089f22733d7066e5772da7e73d71f557`.

No change to any V1/V1.1/V1.2 structural/timing/MIDI/overlap/calibration rule is permitted.

## Contract identities

Top-level result contract:
`songsterr-fresh-purpose-built-reference-evidence-derivation-replay-population-v1`

Replay population identity version:
`reference-evidence-derivation-replay-population-v1`

Accepted binding contract:
`songsterr-fresh-purpose-built-structural-audit-input-binding-v1`

Accepted V2.3 population identity version:
`capture-manifest-v2.3-structural-audit-input-binding-v1`

Accepted structural population completeness identity version:
`reference-blind-structural-audit-population-completeness-v1`

## Frozen decoder runtime interface

Synthetic qualification freezes this execution interface before implementation:

- decoder artifact is UTF-8 Python source bytes whose SHA-256 is bound by Provenance V1;
- runtime is CPython `3.12` on ordinary GitHub CPU for synthetic qualification; workflow must request Python `3.12` and result must expose the exact runtime version used;
- execution command uses the current interpreter with isolated mode: `python -I <decoder.py> ...`;
- one fresh temporary working directory per admitted attempt;
- deterministic argument interface exactly:
  - `--pitch-evidence <path>`
  - `--birth-evidence <path>`
  - `--configuration <path>`
  - `--pitch-latch-output <path>`
  - `--birth-output <path>`
- exact raw decoder configuration bytes are written unchanged to the configuration path;
- exact admitted raw pitch/birth evidence bytes are written unchanged to their paths;
- timeout: 10 seconds per admitted attempt;
- subprocess stdout/stderr captured, not used to determine output identity;
- nonzero exit, timeout, missing output, non-regular output, or unreadable output fails closed;
- replay validator performs no output normalization/canonicalization: it hashes the exact generated output bytes;
- exact output SHA equality is required, not semantic/approximate equality.

Synthetic CI must construct a **new executable synthetic package** valid under the unchanged Provenance V1 validator. The already-completed identity-only Provenance V1 synthetic decoder fixture must not be relabeled as executable proof.

## Inputs

### 1. Capture Manifest V2.3 validation result

- raw bytes;
- expected lowercase 64-hex SHA-256.

Hash before UTF-8 decode/JSON parse. Require exact successful V2.3 result, `errors:[]`, semantic guard true, structural-audit advance true, exact population identity version, valid admitted-population SHA, nonempty admitted binding map/count, and closed downstream authorization.

### 2. Structural Audit Population Completeness V1 result

- raw bytes;
- expected lowercase 64-hex SHA-256.

Hash before parse. Require exact result contract, `contractValid:true`, `errors:[]`, `populationStructurallySuitable:true`, `populationStructuralCompletenessEstablished:true`, valid population-completeness SHA and exact completeness identity version, and closed downstream authorization.

Require its V2.3 result SHA and V2.3 admitted-population SHA to equal the verified V2.3 result identities exactly. Its admitted/verified binding set must equal the V2.3 admitted binding set.

### 3. Provenance V1 validation result

- raw bytes;
- expected lowercase 64-hex SHA-256.

Hash before parse. Require exact successful Provenance V1 result, `errors:[]`, valid canonical `packageBinding` / `packageBindingSha256`, closed authorization, and decoder object containing nonempty decoder ID/version plus valid decoder code/configuration SHA identities.

Require V2.3 `calibrationPackageValidationResultSha256` to equal this verified Provenance V1 result SHA. Require V2.3 package-binding and decoder-configuration identities to equal the verified Provenance V1 package identities.

### 4. Decoder bytes

- exact decoder code bytes;
- exact decoder configuration bytes.

Require code bytes UTF-8-decodable before execution. Require actual code/configuration SHA-256 identities to equal the Provenance V1 package binding exactly.

No decoder code/configuration mutation, patching, templating, normalization, or tuning is allowed after hash verification.

### 5. Per-admitted-attempt replay inputs

For every admitted V2.3 attempt exactly once:

- full `structuralAuditInputs` object;
- expected canonical structural binding SHA-256;
- raw pitch-evidence bytes;
- raw birth-evidence bytes.

Before execution require:

- binding is an object and exact binding contract;
- `SHA256(canonical_json(binding))` equals supplied expected binding SHA;
- `(attemptId, bindingSha)` appears exactly once in V2.3 admitted binding map and Population Completeness admitted/verified sets;
- no duplicate attempt ID, binding key, or supplied binding SHA;
- binding package SHA equals verified Provenance package binding SHA;
- binding derivation-configuration SHA equals verified Provenance decoder configuration SHA;
- `pitchEvidenceSha256`, `birthEvidenceSha256`, `pitchLatchStreamSha256`, and `birthStreamSha256` are valid lowercase 64-hex;
- actual raw pitch evidence SHA equals binding `pitchEvidenceSha256`;
- actual raw birth evidence SHA equals binding `birthEvidenceSha256`.

The replay validator does not semantically parse raw evidence before decoder execution.

## Exact population completeness

Supplied replay attempt keys `(attemptId, structuralAuditInputsSha256)` must equal the full verified V2.3 admitted binding set exactly.

Reject:

- missing attempt;
- extra/non-admitted attempt;
- duplicate attempt ID;
- duplicate binding key;
- duplicate binding SHA submitted for multiple attempts when not present that way in the admitted set;
- zero replay attempts when V2.3 has admitted bindings;
- count mismatch to V2.3 binding count.

## Frozen execution / output checks

For each verified replay input, execute the exact verified decoder code/configuration under the frozen interface.

After successful execution:

- hash exact generated pitch-latch output bytes;
- require hash == binding `pitchLatchStreamSha256`;
- hash exact generated birth output bytes;
- require hash == binding `birthStreamSha256`.

Any one-attempt mismatch fails the entire population replay. No output may be repaired, reordered, canonicalized, or substituted.

## Frozen population replay identity

For every successful attempt build one row containing exactly:

- `attemptId`;
- `structuralAuditInputsSha256`;
- `pitchEvidenceSha256`;
- `birthEvidenceSha256`;
- `replayedPitchLatchStreamSha256`;
- `replayedBirthStreamSha256`.

Sort rows by `(attemptId, structuralAuditInputsSha256)`.

Compute:

`SHA256(canonical_json({
  "populationIdentityVersion": "reference-evidence-derivation-replay-population-v1",
  "captureManifestV23ValidationResultSha256": <verified V2.3 result SHA>,
  "captureManifestV23AdmittedPopulationSha256": <verified V2.3 population SHA>,
  "structuralPopulationCompletenessResultSha256": <verified completeness result SHA>,
  "structuralPopulationCompletenessSha256": <verified completeness identity>,
  "calibrationProvenanceResultSha256": <verified Provenance V1 result SHA>,
  "calibrationPackageBindingSha256": <verified package binding SHA>,
  "decoderCodeSha256": <verified decoder code SHA>,
  "decoderConfigurationSha256": <verified decoder config SHA>,
  "attemptReplays": <sorted rows>
}))`

Expose as `populationDerivationReplaySha256`.

It must be null on any hash, semantic, cross-binding, set-completeness, decoder-execution, timeout, or output-identity failure.

## Frozen result fields

Deterministic result must include at least:

- `contract`;
- `contractValid`;
- sorted `errors`;
- source expected/actual/matches reports for V2.3, completeness, and Provenance results;
- verified V2.3 result/population SHAs;
- verified completeness result/completeness SHAs;
- verified Provenance result/package binding SHAs;
- decoder ID/version/code/configuration SHAs;
- exact Python runtime version string;
- admitted binding count;
- submitted replay count;
- verified replay count;
- deterministic sorted per-attempt replay rows;
- `populationIdentityVersion`;
- `populationDerivationReplaySha256` or null;
- `populationDerivationReplayEstablished`;
- all downstream authorization false/zero.

`populationDerivationReplayEstablished` may be true only if every admitted attempt is replayed exactly once and every generated output identity matches exactly.

## Synthetic contract tests before official harness

Tests must run before official harness and cover at minimum:

1. two-admitted-attempt executable synthetic replay PASS;
2. one-admitted-attempt replay PASS;
3. V2.3 raw/result hash-before-parse failure boundaries;
4. completeness raw/result hash-before-parse failure boundaries;
5. Provenance raw/result hash-before-parse failure boundaries;
6. V2.3 contract/guard/population/binding/authorization failure;
7. completeness contract/pass/identity/V2.3-link/authorization failure;
8. Provenance contract/pass/errors/canonical package binding/authorization failure;
9. V2.3 provenance-result SHA mismatch to verified Provenance bytes;
10. V2.3 package binding mismatch to Provenance package binding;
11. V2.3 decoder configuration mismatch to Provenance decoder configuration;
12. decoder code bytes not UTF-8 FAIL;
13. decoder code SHA mismatch FAIL before execution;
14. decoder configuration SHA mismatch FAIL before execution;
15. malformed/non-object structural binding FAIL;
16. structural binding canonical SHA mismatch FAIL;
17. structural binding not present in V2.3/completeness admitted set FAIL;
18. binding package SHA mismatch FAIL;
19. binding derivation configuration SHA mismatch FAIL;
20. malformed raw/source/output SHA identity FAIL;
21. raw pitch evidence SHA mismatch FAIL before execution;
22. raw birth evidence SHA mismatch FAIL before execution;
23. missing admitted replay FAIL;
24. extra non-admitted replay FAIL;
25. duplicate replay attempt/key FAIL;
26. replay count mismatch FAIL;
27. decoder nonzero exit FAIL;
28. decoder timeout FAIL;
29. decoder missing pitch-latch output FAIL;
30. decoder missing birth output FAIL;
31. replayed pitch-latch output SHA mismatch FAIL;
32. replayed birth output SHA mismatch FAIL;
33. output bytes are hashed exactly without canonicalization (semantically equivalent but byte-different output FAIL);
34. population replay SHA changes if one valid raw evidence identity changes under a fully regenerated valid chain;
35. population replay SHA changes if verified completeness-result byte identity changes while semantics/set remain valid;
36. input attempt order does not change population replay SHA;
37. canonical replay result is byte-deterministic for fixed inputs/runtime;
38. all downstream authorization remains false/zero on PASS.

## Official synthetic harness

Ordinary GitHub CPU only, tests first:

1. request Python `3.12`;
2. compile replay validator/tests;
3. run all synthetic contract tests;
4. construct a new executable synthetic calibration package under the unchanged Provenance V1 contract;
5. validate that package with the unchanged Provenance V1 validator and freeze the resulting Provenance result bytes;
6. construct one V2.3 population with at least two admitted attempts whose raw evidence bytes are deliberately framed/different from their decoded outputs;
7. use the executable decoder to establish target decoded streams, then create V1.2 results and Population Completeness V1 result for that same V2.3 population;
8. run the replay validator from the original raw evidence bytes + exact bound decoder bytes;
9. require exact output identities for both admitted attempts;
10. print all population/package/decoder/completeness/replay identities and closed authorization;
11. upload canonical replay result artifact.

No network retrieval, external corpus access, evaluated audio, Basic Pitch, V6, correctness, protected-song material, or reserved GFN source access.

## Interpretation boundary

A synthetic PASS proves only that the frozen software contracts can execute an immutable package-bound decoder over exact admitted raw evidence and reproduce the exact decoded stream identities already structurally audited for every admitted synthetic attempt.

It does not prove the future real physical decoder is accurate, real sensors/calibration work, real holdout capture is authorized, Basic Pitch/V6 is correct, or customer delivery is safe.

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
3. Implement replay validator and executable synthetic fixture/tests without mutating earlier accepted validators.
4. Run tests-first ordinary GitHub CPU CI.
5. Freeze run/job/artifact/result identities.
6. Update canonical checkpoint.
7. Perform final no-gap software-lineage review. If no concrete gap remains, stop software gate creation and leave physical execution as the next necessary route, still budget-paused.
