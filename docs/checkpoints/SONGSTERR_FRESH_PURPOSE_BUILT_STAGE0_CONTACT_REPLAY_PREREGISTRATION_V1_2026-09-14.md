# Songsterr Fresh — Purpose-Built Stage-0 Contact Replay Preregistration V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **FROZEN BEFORE REAL STAGE-0 CONTACT BENCH DATA / SYNTHETIC + NON-HOLDOUT BENCH ONLY**

Parent budget boundary: `docs/checkpoints/SONGSTERR_FRESH_BUDGET_CONSTRAINT_SOFTWARE_ONLY_ROUTE_2026-09-14.md`
Parent staged decision: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_MINIMUM_BOM_AND_STAGE0_PROCUREMENT_DECISION_V1_2026-09-14.md`

## 1. Purpose

Freeze the exact software-side evidence contract used to decide whether a physical six-string contact topology reproduces known NON_HOLDOUT mechanical/electrical fixture states without hidden cross-string coupling or guessed truth.

This is **not** a holdout reference decoder and does not establish future guitar-note correctness. It is a low-level Stage-0 topology replay test that can be fully implemented and exercised with synthetic fixtures now, while the real bench remains paused by budget.

## 2. Exactly three immutable input byte streams

The validator consumes exactly three UTF-8 JSON byte streams plus expected SHA-256 identities:

1. `configuration` — logger/topology/sense-line mapping;
2. `fixture` — independently known mechanical/electrical contact states deliberately imposed during Stage-0 tests;
3. `scanLog` — raw binary contact observations and monotonic logger ticks captured by the contact logger.

Every exact byte stream must be SHA-256 verified against its expected identity **before any JSON parsing or semantic validation**. Any missing, extra, non-byte or hash-mismatched source fails closed.

No evaluated DI, guitar audio, pitch detector, Basic Pitch, V6 output, correctness match, model score or model output is an input.

## 3. Configuration contract

Contract string:
`songsterr-fresh-purpose-built-stage0-contact-configuration-v1`

Required fields:
- `configurationId`: non-empty string;
- `loggerFirmwareId`: non-empty string;
- `topologyId`: non-empty string;
- `stage`: exactly `NON_HOLDOUT_STAGE0`;
- `stringCount`: exactly integer `6`;
- `fretNumbers`: non-empty list of unique, strictly increasing integers in `1..36`;
- `phaseOrder`: exactly `[1,2,3,4,5,6]`;
- `sampleEncoding`: exactly `BINARY_CONTACT_VECTOR_V1`;
- `usedEvaluatedAudio`: exactly `false`;
- `usedModelOutputs`: exactly `false`;
- `derivedFromEvaluatedAudio`: exactly `false`.

For V1, each raw sense vector has one binary element per `fretNumbers` entry. `1` means electrical/contact evidence was observed on that configured sense line during that driven-string phase; `0` means it was not observed. Boolean JSON values are not accepted in place of integer `0`/`1`.

Any comparator/threshold required to produce that binary raw state belongs to the NON_HOLDOUT bench configuration and must later be bound by `configurationId`; V1 does not infer it from audio.

## 4. Fixture contract

Contract string:
`songsterr-fresh-purpose-built-stage0-contact-fixture-v1`

Required top-level fields:
- `fixtureId`: non-empty string;
- `configurationId`: exact match to configuration;
- `topologyId`: exact match to configuration;
- `stage`: exactly `NON_HOLDOUT_STAGE0`;
- `usedEvaluatedAudio`: exactly `false`;
- `usedModelOutputs`: exactly `false`;
- `cycles`: non-empty list.

Each fixture cycle requires:
- `cycleSequence`: integer beginning at `0` and increasing by exactly `1`;
- `strings`: exactly six records, one for each `stringNumber` `1..6` in ascending order;
- each string record contains `expectedActiveFrets`: a sorted unique list whose values are members of configuration `fretNumbers`.

`expectedActiveFrets=[]` means intentional OPEN/no-contact state.
One expected fret means an unambiguous intended contact.
More than one expected fret is an intentional ambiguity/multi-contact challenge fixture, not automatically a failure; the raw scan must reproduce the deliberately imposed active set exactly.

Fixture truth must come from deterministic physical switch/jumper/contact setup or another independently known Stage-0 engineering fixture. It may not be created by listening to or interpreting evaluated audio.

## 5. Raw scan-log contract

Contract string:
`songsterr-fresh-purpose-built-stage0-contact-scan-log-v1`

Required top-level fields:
- `loggerId`: non-empty string;
- `configurationId`: exact match to configuration;
- `topologyId`: exact match to configuration;
- `fixtureId`: exact match to fixture;
- `stage`: exactly `NON_HOLDOUT_STAGE0`;
- `clockDomainId`: non-empty string;
- `usedEvaluatedAudio`: exactly `false`;
- `usedModelOutputs`: exactly `false`;
- `derivedFromEvaluatedAudio`: exactly `false`;
- `records`: non-empty list.

Each record requires:
- `cycleSequence`: integer `>=0`;
- `phaseSequence`: integer `0..5`;
- `tick`: integer `>=0`;
- `driveStringNumber`: exactly the configured `phaseOrder[phaseSequence]`;
- `rawSenseValues`: list whose length equals `len(fretNumbers)` and whose values are integers exactly `0` or `1`;
- `healthStatus`: exactly `OK` for a V1 topology PASS fixture.

V1 sequence rules:
- records are ordered by `(cycleSequence, phaseSequence)`;
- each fixture cycle has exactly six scan records;
- every cycle contains phase sequences `0..5` exactly once;
- `cycleSequence` starts at `0` and advances without gaps;
- `tick` is strictly increasing across every successive scan record;
- no extra scan cycle may exist beyond the fixture declaration and no fixture cycle may be missing.

A non-`OK` hardware status fails the Stage-0 topology replay. It is preserved as evidence, not repaired.

## 6. Deterministic decode

For each scan record:
1. find every `rawSenseValues[i] == 1`;
2. map each active index `i` to `fretNumbers[i]`;
3. output that ascending list as `observedActiveFrets` for `driveStringNumber` in that cycle;
4. classify the observed physical contact state:
   - zero active frets -> `OPEN`;
   - exactly one active fret -> `UNAMBIGUOUS_FRET`;
   - more than one active fret -> `AMBIGUOUS_MULTI_CONTACT`.

The decoder may not choose a “most likely,” highest, nearest or musically plausible fret when multiple sense lines are active.

## 7. Exact fixture comparison

For every `(cycleSequence, stringNumber)` pair, compare the deterministic `observedActiveFrets` set with the fixture's exact `expectedActiveFrets` set.

Count separately:
- each expected fret absent from observed as one `missingExpectedContactCount`;
- each observed fret absent from expected as one `unexpectedContactCount`.

An unexpected active fret is the key Stage-0 signal for cross-string/electrical crosstalk or topology ambiguity. It may not be reclassified as harmless because a musically plausible fret is also present.

A deliberately expected multi-contact fixture passes only when the complete expected set is reproduced exactly.

## 8. Frozen blocker counts

The validator must report all of these integer blocker counts:
- `invalidConfigurationDeclarationCount`;
- `sourceSha256MismatchCount`;
- `invalidFixtureDeclarationCount`;
- `invalidScanLogDeclarationCount`;
- `sequenceViolationCount`;
- `nonmonotonicTickCount`;
- `driveStringMismatchCount`;
- `missingExpectedContactCount`;
- `unexpectedContactCount`;
- `healthStatusViolationCount`;
- `forbiddenAudioOrModelProvenanceCount`.

Stage-0 replay PASS requires **every blocker count exactly zero**.

## 9. PASS meaning

A PASS may establish only:
- `stage0ReplayContractValid:true`;
- `stage0ContactTopologyReplayPass:true`.

It does not establish:
- real-guitar fret sensing qualification;
- excitation-plane qualification;
- hardware clock qualification;
- structural suitability of a holdout;
- Basic Pitch authorization;
- V6 authorization;
- correctness authorization;
- model validation;
- customer eligibility;
- delivery advancement.

The result must always keep:
- `basicPitchAuthorized:false`;
- `v6Authorized:false`;
- `correctnessAuthorized:false`;
- `modelValidationComplete:false`;
- `customerEligibleEvents:0`;
- `mayAdvanceDelivery:false`.

## 10. Minimum synthetic tests before any future bench data

Synthetic CI must cover at least:
1. nominal isolated-contact PASS;
2. SHA-256 mismatch before JSON parse;
3. missing/extra source rejection;
4. malformed JSON after matching hash fails closed;
5. invalid configuration identity/provenance;
6. invalid fixture sequence/string ordering;
7. invalid scan phase sequence/order;
8. nonmonotonic/equal ticks;
9. drive-string mismatch;
10. missing expected contact;
11. unexpected/crosstalk contact;
12. deliberately expected multi-contact PASS;
13. health-status failure;
14. forbidden audio/model provenance;
15. deterministic byte-identical canonical result for identical inputs;
16. PASS still leaves every downstream authorization false.

## 11. Budget-aware authority boundary

The user has stated that additional hardware budget is not currently available. Therefore:
- implementation + synthetic CI may proceed now;
- no Stage-0 physical bench purchase is assumed;
- no real Stage-0 scan log should be expected until the budget constraint changes or equivalent hardware becomes available at no additional cost.

No real holdout exists. Archived V143/Gomyway remains untouched and closed.
