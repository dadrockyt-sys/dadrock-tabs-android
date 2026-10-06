# GuitarSet missing-event diagnostic V1 — decision brief

Date: 2026-10-06  
Branch: `astra-work`  
Authoritative run: `37431884091` — **SUCCESS**  
Artifact: `11397417142`  
Artifact digest: `sha256:9e28ac5a9316f858eeaf14e2006c2df81c3a5204443d7d890176fc0516eb29ca`  
Result JSON SHA-256: `c91c603d031c367ce7fd4fc3a5011f2f5a225e08ea15c523395247c27f71a89f`

## What was preserved

The exact frozen Basic Pitch candidate artifact from run `37426492061` was reused unchanged: artifact `11395810007`, digest `sha256:6568a6daaca594dc216d61268a80012da7c63f26a7e77f2d7826b1b5f3b73cc5`, freeze-manifest SHA-256 `db721bca5dd22e7dc04d9a00dd04996b2cb52ed59d12172b9d056b01ea608ccb`, 180 files, 33,327 candidate events, players 00/01/03. No threshold search or prediction mutation occurred.

The scorer remained the frozen preregistered implementation: 50 ms onset tolerance, maximum-cardinality onset-only matching followed by minimum total absolute onset error, with pitch never used to select primary pairs.

Reference transport used the pinned `jhartquist/guitarset` mirror revision `4aca25487bef5cb0d2c4ec146218f9145402a776` under the previously frozen provenance amendment. Runtime repairs before the successful score were transport/container-only: transient request retries, NumPy 1.26.4 for JAMS 0.3.4 compatibility, and valid JAMS file duration metadata. None changed note labels, scorer semantics, candidate predictions, tolerance, or gate.

## Authoritative result

Across 180 tracks, the scorer saw 33,849 reference events and matched 26,640 onsets (78.70% reference recall).

Pooled:
- unmatched references: **7,209**
- assignment-dependent wrong-pitch matches: **12,044**
- assignment-dependent exact pitch: **14,596 / 26,640 (54.79%)**
- ambiguity-stable pitch-error lower bound: **1,419**
- unmatched / assignment-dependent wrong-pitch ratio: **0.599**
- unmatched / ambiguity-stable pitch-error-lower-bound ratio: **5.080**

Per player, unmatched references were also below assignment-dependent wrong-pitch matches:
- player 00: **3,273 unmatched vs 5,264 wrong-pitch**
- player 01: **2,276 vs 3,519**
- player 03: **1,660 vs 3,261**

## Preregistered gate

The frozen replication rule was:

`unmatchedReferenceCount > assignmentDependentWrongPitchCount` pooled **and** separately for players 00/01/03.

Result:
- pooled pass: **false**
- all-players pass: **false**
- overall pass: **false**

Therefore the independently tested **missing/unsynchronized-event dominance hypothesis did not replicate under its preregistered decision rule**.

## Interpretation boundary

The ambiguity-stable pitch-error lower bound is much smaller than the assignment-dependent wrong-pitch count, so chord/onset assignment ambiguity remains scientifically important. That observation must not be used post hoc to redefine the preregistered gate or rescue the failed hypothesis.

Players 00/01/03 are now consumed evaluation material and are not fresh holdout.

## Decision

**Stop this hypothesis path.** Do not implement a missing-event recovery algorithm, tune thresholds, mutate predictions, or derive a new correction from this GuitarSet score.

Do not reopen Go My Way as an optimization source. Preserve the immutable 1065-event Go My Way quantized candidate and all previously frozen baselines. `main` remains unchanged.

Any future prediction-changing hypothesis must be separately motivated and preregistered on genuinely independent material; this result provides no automatic authorization for one.
