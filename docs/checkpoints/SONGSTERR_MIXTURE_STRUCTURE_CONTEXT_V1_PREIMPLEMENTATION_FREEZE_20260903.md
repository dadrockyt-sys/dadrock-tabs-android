# MIXTURE_STRUCTURE_CONTEXT_V1 — PRE-IMPLEMENTATION FREEZE

Date: 2026-09-03 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **`REFERENCE-BLIND MIXTURE-CONTEXT IMPLEMENTATION AUTHORIZED / CARRIER STRUCTURE BORROWING FORBIDDEN / REFERENCE SCORING NOT AUTHORIZED`**

## Purpose

Freeze the next independently motivated dual-context component before code: a deterministic resolver that combines explicit user structure priors with a future trusted **full-mixture** structure observation, while refusing to silently use role/separated-carrier structure as global measure context.

This directly operationalizes the public Songsterr-inspired hypothesis that full-mixture context may matter for measure structure even when source separation is used for local note evidence.

It is not a reconstruction of Songsterr's private system.

## Scientific boundary

Allowed:

- deterministic server-side/reference-blind JS;
- existing normalized `StructurePriorV1`;
- synthetic trusted full-mixture observations;
- strict provenance validation;
- research-only response metadata;
- field-by-field resolution with explicit user override precedence.

Forbidden:

- reference corpus reads/scores;
- accepting GuitarSet/SplitMySong/GOAT information as mixture structure observation;
- using V143/separated-carrier note output as an implicit structure observation;
- guessing missing tempo/meter/pickup/feel;
- changing analyzer selection or V143 safety gates;
- changing generated tab/PDF output;
- GPU/CUDA/Modal;
- Production promotion.

## Frozen name

`MIXTURE_STRUCTURE_CONTEXT_V1`

Suggested response member:

`mixtureStructureContext`

## Inputs — FROZEN

```js
buildAiTabMixtureStructureContextV1({
  structurePrior,
  mixtureObservation,
  mixtureSource,
})
```

- `structurePrior`: already server-normalized Conditioning V1 structure prior.
- `mixtureObservation`: optional trusted full-mixture observation; `null` means no mixture estimator is connected.
- `mixtureSource`: server-owned provenance for the request/full-mixture audio identity.

The current Phase 3 route integration must pass `mixtureObservation=null`. This intentionally prevents current analyzers/carriers from gaining structure authority before a separately frozen full-mixture estimator adapter exists.

## Trusted mixture observation schema — FROZEN

```json
{
  "version": 1,
  "provenance": {
    "sourceKind": "full-mixture",
    "sourceIdentity": "request-audio",
    "referenceBlind": true,
    "referenceRuntimeInputUsed": false
  },
  "tempoBpm": {
    "value": 120,
    "confidence": 0.8,
    "method": "future-full-mixture-estimator"
  },
  "timeSignature": {
    "value": {"numerator": 4, "denominator": 4},
    "confidence": 0.7,
    "method": "future-full-mixture-estimator"
  },
  "pickupBeats": {
    "value": 0,
    "confidence": 0.6,
    "method": "future-full-mixture-estimator"
  },
  "feel": {
    "value": "straight",
    "confidence": 0.6,
    "method": "future-full-mixture-estimator"
  }
}
```

Observation fields may be omitted or `null`. Missing fields remain unresolved unless the user prior is explicit.

### Provenance gate

A non-null mixture observation is trusted only when all are exact:

- `version === 1`;
- `provenance.sourceKind === "full-mixture"`;
- `provenance.sourceIdentity === "request-audio"`;
- `provenance.referenceBlind === true`;
- `provenance.referenceRuntimeInputUsed === false`.

Any other source kind—including `instrument-carrier`, `separated-stem`, `v143-rhythm-carrier`, or absent provenance—must fail closed rather than being silently accepted.

## Observation value validation — FROZEN

Use the same value ranges as Conditioning V1:

- tempo: finite `[20,400]`;
- meter numerator integer `[1,32]`;
- meter denominator one of `1,2,4,8,16,32`;
- pickup finite `[0,32]`;
- feel one of `straight`, `triplet` for a concrete observation. `auto` is not an observation value.

For each non-null observation field:

- confidence must be finite `[0,1]`;
- method must be a non-empty sanitized string no longer than 120 characters.

Invalid observation values fail closed.

## Resolution precedence — FROZEN

Resolve independently per field.

### Tempo

1. explicit `structurePrior.tempoBpm`;
2. trusted `mixtureObservation.tempoBpm.value`;
3. unresolved `null`.

### Time signature

1. explicit `structurePrior.timeSignature`;
2. trusted `mixtureObservation.timeSignature.value`;
3. unresolved `null`.

### Pickup

1. explicit `structurePrior.pickupBeats`, including explicit `0`;
2. trusted `mixtureObservation.pickupBeats.value`, including observed `0`;
3. unresolved `null`.

### Feel

1. explicit prior when prior feel is `straight` or `triplet`;
2. trusted mixture feel observation;
3. unresolved `auto`.

An explicit user value is authoritative even if a mixture observation disagrees. This phase does not score disagreements.

## Per-field source/provenance — FROZEN

Each resolved field must report one of:

- `user-prior`;
- `full-mixture-observation`;
- `unresolved`.

User-prior confidence is represented as `null` rather than manufactured `1.0`; it is an instruction/override, not a model confidence.

Full-mixture observation confidence/method are preserved.

Unresolved confidence/method are null.

## Context output — FROZEN

```json
{
  "contextContract": {
    "name": "mixture-structure-context",
    "version": 1,
    "referenceBlind": true,
    "referenceScoreAuthorized": false,
    "carrierStructureBorrowingAllowed": false,
    "productionEligible": false
  },
  "mixtureSource": {
    "kind": "full-mixture",
    "source": "request-audio"
  },
  "observationStatus": "NOT_CONNECTED|TRUSTED_FULL_MIXTURE_OBSERVATION",
  "resolved": {
    "tempoBpm": null,
    "timeSignature": null,
    "pickupBeats": null,
    "feel": "auto"
  },
  "fieldSources": {
    "tempoBpm": {"source":"unresolved","confidence":null,"method":null},
    "timeSignature": {"source":"unresolved","confidence":null,"method":null},
    "pickupBeats": {"source":"unresolved","confidence":null,"method":null},
    "feel": {"source":"unresolved","confidence":null,"method":null}
  },
  "completeForMeasureProjection": false,
  "feelResolved": false
}
```

`completeForMeasureProjection=true` only when resolved tempo, time signature and pickup are all non-null. Feel is tracked separately because Phase 2 allows measure placement with Auto feel but refuses to guess subdivisions.

## Current route integration — FROZEN

During this Phase 3 implementation:

```js
const mixtureStructureContext =
  buildAiTabMixtureStructureContextV1({
    structurePrior: conditioning.structurePrior,
    mixtureObservation: null,
    mixtureSource: conditioningContract.provenance.mixtureSource,
  });
```

The route may append `mixtureStructureContext` as research metadata only.

It must **not**:

- pass `analyzerData.tempo`, `analyzerData.timeSignature`, V143 `measureGrid`, carrier events or any other current analyzer field as a mixture observation;
- replace Conditioning V1;
- replace Phase 2 `conditioningShadowProjection`;
- influence PDF routes;
- alter product tab fields.

This deliberate `null` observation is evidence that the architecture reserves the full-mixture channel without falsely claiming it has already been connected.

## Frozen deterministic tests

### M1 — no observation + all Auto
All fields unresolved; observation status `NOT_CONNECTED`; completeForMeasureProjection false.

### M2 — explicit user values resolve without observation
Explicit tempo/meter/pickup/feel are preserved with source `user-prior`.

### M3 — trusted mixture fills Auto tempo only
Auto tempo receives observation value/confidence/method; other unresolved fields remain unresolved.

### M4 — field-by-field mixture filling
Trusted mixture can fill meter/pickup/feel independently without inventing absent fields.

### M5 — explicit user values override disagreeing mixture observation
Every explicit prior wins; mixture disagreement is not scored or used to retune.

### M6 — explicit/observed zero pickup preserved
`0` must never collapse into null/Auto.

### M7 — carrier/separated source rejected
Observation with sourceKind other than exact `full-mixture` fails closed.

### M8 — reference provenance rejected
Observation with `referenceBlind !== true` or `referenceRuntimeInputUsed !== false` fails closed.

### M9 — invalid observation confidence/value/method rejected
Out-of-range confidence, invalid musical value, empty method, or unsupported version fails closed.

### M10 — route/product isolation
Route integration passes `mixtureObservation: null` in this phase, appends research metadata only, PDFs do not consume it, and existing product fields/V143 gates remain untouched.

## Safety accounting — FROZEN

Result evidence must assert:

- `referenceBlind=true`;
- `referenceScoreAuthorized=false`;
- `carrierStructureBorrowingAllowed=false`;
- `productionEligible=false`;
- current route mixture observation connected=false;
- reference score calls=0;
- GuitarSet read=false;
- SplitMySong read=false;
- GOAT restricted bytes read=false;
- Modal invoked=false;
- GPU used=false;
- Production modified=false;
- Production promotion authorized=false.

## Promotion/evaluation state

`implementationAllowed=true`  
`syntheticContractTestsAllowed=true`  
`currentFullMixtureEstimatorConnected=false`  
`referenceFacingScoreAllowed=false`  
`productOutputMutationAllowed=false`  
`productionPromotionAuthorized=false`

The next valid action is to implement this resolver and its M1–M10 tests exactly as frozen, append only research metadata, and leave the actual Auto full-mixture observation channel explicitly unconnected until a future estimator is independently frozen.
