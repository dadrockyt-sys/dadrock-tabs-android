# Songsterr Fresh — Purpose-Built Reference-Blind Structural Audit Preregistration V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **FROZEN BEFORE REAL PURPOSE-BUILT CALIBRATION OR HOLDOUT MEDIA**

## Purpose

This preregistration freezes the structural audit that sits between the purpose-built V2.1 capture-manifest declaration gate and any future Basic Pitch/V6/correctness execution.

The audit exists to answer one question only:

> Is the independently captured physical reference structurally coherent enough to serve as immutable note-level onset + pitch truth without inspecting evaluated DI audio or any model/correctness output?

A pass may establish only `authoritativeStructuralSuitabilityEstablished:true` for the audited reference population. It does **not** itself authorize Basic Pitch, V6, correctness, product validation completion, customer eligibility or delivery.

## Forbidden inputs

The audit MUST NOT accept or open:

- evaluated magnetic DI audio;
- any other evaluated audio view;
- Basic Pitch output/activations;
- V6 output/classes;
- correctness matches;
- precision/recall/model-score data;
- model-informed edits, repairs or retake decisions.

There is intentionally no evaluated-audio CLI parameter.

## Required independent inputs

For each admitted performance the audit consumes four immutable JSON byte streams plus their expected SHA-256 identities:

1. **hardware/reference configuration** — physical string/fret mapping, tuning, frozen calibration identity and timing bound;
2. **birth/dynamics stream** — independently sensed note births with onset and release timestamps plus physical string channel;
3. **pitch-latch stream** — physical fret-position observations latched to birth-event IDs, with their own timestamps/string/fret;
4. **clock/sync proof** — independent timing-domain proof with frozen maximum absolute error and explicit no-sync-loss declaration.

The exact file bytes are SHA-256 checked before semantic audit. A hash mismatch is a structural failure.

## Frozen timing bound

The maximum permitted independent-reference timing uncertainty is **0.025 seconds**.

This is inherited from the already-declared V2 reference-calibration/clock bound and is frozen before real holdout use. The audit does not optimize or sweep this value.

For each note birth, the absolute time difference between the birth event and its latched physical pitch observation must be <= `0.025 s`.

## Hardware configuration contract

Required fields:

- `contract = songsterr-fresh-purpose-built-reference-hardware-v1`
- non-empty `configurationId`
- non-empty `calibrationId`
- `calibrationUsedHoldoutData = false`
- `calibrationUsedModelOutputs = false`
- `calibrationDerivedFromEvaluatedAudio = false`
- `maxAbsoluteReferenceTimingErrorSeconds <= 0.025`
- `openStringMidi`: exactly six integer MIDI values, strictly increasing, each within 0..127
- `maxFret`: integer 1..36
- `eventSemanticsVersion = physical-reference-semantics-v1`

Pitch identity is derived deterministically as:

`midi = openStringMidi[stringNumber - 1] + fret`

No pitch detector is consulted.

## Birth/dynamics stream contract

Contract: `songsterr-fresh-purpose-built-birth-stream-v1`.

Each event must contain:

- unique non-empty `birthEventId`;
- finite nonnegative `onsetSeconds`;
- finite `releaseSeconds` strictly greater than onset;
- integer `stringNumber` in 1..6;
- `usedModelOutputs = false`;
- `derivedFromEvaluatedAudio = false`.

Events must be strictly increasing by `onsetSeconds` in file order. Duplicate/nonmonotonic onsets are a structural failure; simultaneous chord events therefore require distinct hardware timestamps rather than a post-hoc shared quantized time.

A repeated attack on the same physical pitch is a new note **only** when it has a distinct independently sensed birth event. Slides/bends/fret motion without a new birth event cannot create a new note identity.

## Pitch-latch stream contract

Contract: `songsterr-fresh-purpose-built-pitch-latch-stream-v1`.

Each record must contain:

- unique non-empty `pitchLatchId`;
- exactly one non-empty `birthEventId` link;
- finite nonnegative `timestampSeconds`;
- integer `stringNumber` in 1..6;
- integer `fret` in 0..`maxFret`;
- `state = UNAMBIGUOUS`;
- `usedModelOutputs = false`;
- `derivedFromEvaluatedAudio = false`.

Records must be strictly increasing by `timestampSeconds` in file order.

Every birth must have exactly one pitch-latch record; every pitch-latch record must resolve to exactly one birth. String channels must agree. Absolute timestamp delta must be <= 0.025 s.

Any ambiguous physical state is a blocker. It may not be resolved by listening to DI, viewing a waveform/spectrogram, consulting a score, consulting the model, or manually choosing the more plausible fret.

## Clock/sync proof contract

Contract: `songsterr-fresh-purpose-built-clock-sync-v1`.

Required:

- non-empty `syncId` and `clockDomainId`;
- `syncLost = false`;
- `usedModelOutputs = false`;
- `derivedFromEvaluatedAudio = false`;
- finite nonnegative `maxAbsoluteErrorSeconds <= 0.025`.

Loss of sync or exceeded bound is a structural blocker, not a repair opportunity.

## Derived note events

For each one-to-one birth + pitch-latch pair, derive exactly one immutable note event:

- `eventId = birthEventId`
- `stringNumber`
- `fret`
- derived integer `midi`
- `onsetSeconds = birth onset`
- `releaseSeconds = birth release`
- source IDs/timestamps preserved.

Derived MIDI must be in the frozen V6 evaluated range **40..88**. Out-of-range events are structural blockers for this holdout rather than silently dropped evidence.

## Zero-anomaly structural gates

The population is structurally suitable only if all counts below equal zero:

- malformed/invalid configuration or calibration declarations;
- source SHA-256 mismatch;
- clock/sync loss or timing bound violation;
- nonmonotonic birth timestamps;
- nonmonotonic pitch-latch timestamps;
- duplicate birth IDs;
- duplicate pitch-latch IDs;
- unmatched births;
- unmatched pitch-latches;
- multiple pitch-latches bound to one birth;
- physical string mismatch between birth and pitch latch;
- ambiguous pitch states;
- birth-to-pitch-latch timestamp delta > 0.025 s;
- invalid fret/string or derived MIDI outside 40..88;
- **same-string overlap:** a new note on one physical string begins before the preceding note on that string releases;
- **same-key overlap:** two derived note events with the same integer MIDI overlap in time, regardless of string;
- forbidden model/audio-derived provenance declaration.

No anomaly may be repaired, dropped, relabeled or excluded after real holdout inspection. Any nonzero blocker produces `datasetStructurallySuitable:false` for the audited population.

## Output authority

A successful audit returns:

- `contractValid:true`
- exact source SHA-256 identities;
- deterministic derived note-event count and population SHA-256;
- zero blocker counts;
- `datasetStructurallySuitable:true`
- `authoritativeStructuralSuitabilityEstablished:true`

Even on PASS it MUST return:

- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

A later, separate population-binding/governance gate must explicitly authorize the one official correctness path.

## Failure disposition

If a real admitted purpose-built population fails this structural audit:

- do not listen to evaluated DI to diagnose truth;
- do not repair/drop the offending event;
- do not replace an admitted transport-valid take because its music/reference structure is inconvenient;
- do not tune thresholds from the failure;
- do not run Basic Pitch/V6/correctness on that failed population.

A future protocol redesign would require a new preregistration and new untouched population, not a rescue of the failed holdout.

## Synthetic qualification before acquisition

Before any real purpose-built calibration or holdout recording is necessary, implementation must pass synthetic tests covering at minimum:

1. nominal one-to-one physical reference PASS;
2. source hash mismatch FAIL;
3. sync loss / excessive sync error FAIL;
4. ambiguous pitch latch FAIL;
5. unmatched birth FAIL;
6. unmatched pitch latch FAIL;
7. multiple latches for one birth FAIL;
8. birth/latch string mismatch FAIL;
9. timestamp-delta bound FAIL;
10. nonmonotonic birth and latch streams FAIL;
11. same-string overlap FAIL;
12. same-key overlap FAIL;
13. out-of-range MIDI FAIL;
14. audio/model-derived provenance FAIL;
15. PASS still leaves Basic Pitch/V6/correctness/customer/delivery unauthorized.

Only after that synthetic CI passes does hardware/procurement/calibration capture become an objectively necessary next step.
