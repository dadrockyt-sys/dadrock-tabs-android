# DUAL_CONTEXT_SHADOW_FUSION_V1 — PRE-IMPLEMENTATION FREEZE

Date: 2026-09-03 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **`REFERENCE-BLIND DUAL-CONTEXT FUSION IMPLEMENTATION AUTHORIZED / SHADOW ONLY / REFERENCE SCORING NOT AUTHORIZED`**

## Purpose

Freeze the next independently motivated DadRock dual-context step before code.

Phase 1 carries explicit structure + instrument configuration. Phase 2 can project copied analyzer events under a structure prior. Phase 3 creates a provenance-gated global **full-mixture structure context**, but Phase 2 still consumes the raw Conditioning V1 structure prior directly.

Phase 4 will add a shadow-only fusion adapter so the authoritative structure input to a copied-event projection is the **resolved `MIXTURE_STRUCTURE_CONTEXT_V1`**, while role/tuning/capo continue to come from `STRUCTURE_INSTRUMENT_CONDITIONING_V1`.

This makes the dual-context topology mechanically complete before any real Auto full-mixture estimator is connected.

It is not a reconstruction of Songsterr's private system.

## Scientific boundary

Allowed:

- deterministic server-side/reference-blind JS;
- copied normalized analyzer events;
- server-normalized Conditioning V1 instrument configuration;
- validated Phase 3 mixture structure context;
- existing Phase 2 shadow projector reused as a pure dependency;
- synthetic trusted full-mixture contexts in tests;
- research metadata only.

Forbidden:

- reference corpus reads/scores;
- GuitarSet/SplitMySong/GOAT information;
- borrowing structure from separated/V143/instrument carriers;
- current analyzer fields being relabeled as full-mixture structure;
- changing analyzer selection or V143 gates;
- changing `generatedTab`, product `events`, `renderEvents`, `measureGrid`, `analysisEngine`, preview/full PDF selection, payment or delivery behavior;
- GPU/CUDA/Modal;
- Production promotion.

## Frozen name

`DUAL_CONTEXT_SHADOW_FUSION_V1`

Suggested response member:

`dualContextShadowProjection`

## Inputs — FROZEN

```js
buildAiTabDualContextShadowFusionV1({
  events,
  conditioning,
  mixtureStructureContext,
})
```

- `events`: copied normalized product events only.
- `conditioning`: server-normalized Conditioning V1; its **instrumentConfig** is authoritative for role/tuning/capo.
- `mixtureStructureContext`: validated Phase 3 context; its **resolved structure** is authoritative for tempo/meter/pickup/feel.

The adapter must not use `conditioning.structurePrior` directly for projection once a Phase 3 context is supplied. Phase 3 has already resolved user-prior precedence versus trusted full-mixture observation field-by-field.

## Required mixture-context gate — FROZEN

Accept only exact context contract:

- `name === "mixture-structure-context"`;
- `version === 1`;
- `referenceBlind === true`;
- `referenceScoreAuthorized === false`;
- `carrierStructureBorrowingAllowed === false`;
- `productionEligible === false`;
- `mixtureSource.kind === "full-mixture"`;
- `mixtureSource.source === "request-audio"`.

Any failure is fail-closed.

The adapter must also validate the resolved structure values against Conditioning V1 ranges:

- tempo null or finite `[20,400]`;
- time signature null or numerator `[1,32]`, denominator `1,2,4,8,16,32`;
- pickup null or finite `[0,32]`;
- feel `auto|straight|triplet`.

## Frozen fusion rule

Create a new normalized conditioning copy for the Phase 2 projector:

```js
{
  version: 1,
  structurePrior: {
    tempoBpm: mixtureStructureContext.resolved.tempoBpm,
    timeSignature: mixtureStructureContext.resolved.timeSignature,
    pickupBeats: mixtureStructureContext.resolved.pickupBeats,
    feel: mixtureStructureContext.resolved.feel,
  },
  instrumentConfig: conditioning.instrumentConfig,
}
```

Then invoke the existing pure `buildAiTabConditionedShadowProjectionV1` with copied events + this fused conditioning.

No product field may be overwritten.

## Output — FROZEN

```json
{
  "fusionContract": {
    "name": "dual-context-shadow-fusion",
    "version": 1,
    "shadowOnly": true,
    "referenceBlind": true,
    "referenceScoreAuthorized": false,
    "carrierStructureBorrowingAllowed": false,
    "productionEligible": false
  },
  "structureAuthority": {
    "source": "mixture-structure-context-v1",
    "observationStatus": "NOT_CONNECTED|TRUSTED_FULL_MIXTURE_OBSERVATION",
    "completeForMeasureProjection": false,
    "feelResolved": false,
    "fieldSources": {}
  },
  "instrumentAuthority": {
    "source": "conditioning-v1",
    "role": "lead",
    "tuningMidi": [40,45,50,55,59,64],
    "capoFret": 0
  },
  "projection": {}
}
```

The nested projection must retain its own existing Phase 2 shadow contract. Phase 4 does not promote it.

## Current route integration — FROZEN

After creating Phase 3 `mixtureStructureContext`, the route may append:

```js
const dualContextShadowProjection =
  buildAiTabDualContextShadowFusionV1({
    events: structuredPayload.events,
    conditioning,
    mixtureStructureContext,
  });
```

This is research metadata only.

Current Phase 3 still passes `mixtureObservation: null`, so Phase 4 must not create any new Auto structure information. It simply ensures the correct authority path is ready.

## Frozen deterministic tests

### D1 — all Auto + no observation stays unresolved
Phase 3 all-Auto/NOT_CONNECTED context produces Phase 4 projection with unresolved structure; no defaults invented.

### D2 — explicit user structure flows through Phase 3 into projection
Explicit tempo/meter/pickup/feel produce the same deterministic structure math as Phase 2.

### D3 — trusted full-mixture tempo fills Auto and reaches fusion projection
Synthetic trusted observation supplies Auto tempo through Phase 3; Phase 4 projection uses it.

### D4 — field-by-field mixed authority
Some structure fields from user prior and others from trusted full mixture are fused exactly as Phase 3 resolved them.

### D5 — user override beats disagreeing mixture observation
Projection uses the Phase 3 resolved user value, not the raw observation.

### D6 — tuning/capo remain instrument authority
Mixture context cannot change tuning/capo; Drop D/capo decoding remains driven only by Conditioning V1 instrumentConfig.

### D7 — invalid/tampered mixture context rejected
Wrong contract flags/source/name/version or invalid resolved values fail closed.

### D8 — carrier borrowing remains impossible
A context claiming carrier borrowing allowed or non-full-mixture source fails closed.

### D9 — source events/product objects not mutated
Input events and conditioning remain deep-equal after fusion.

### D10 — route/PDF/product isolation
Route appends `dualContextShadowProjection` only after Phase 3 context creation; PDFs do not consume it; no product structured fields or analyzer-selection/V143 gates are altered.

## Safety accounting — FROZEN

Evidence must assert:

- `shadowOnly=true`;
- `referenceBlind=true`;
- `referenceScoreAuthorized=false`;
- `carrierStructureBorrowingAllowed=false`;
- `productionEligible=false`;
- Phase 3 real mixture observation connected=false;
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
`referenceFacingScoreAllowed=false`  
`productOutputMutationAllowed=false`  
`productionPromotionAuthorized=false`

The next valid action is to implement this exact fusion adapter, D1–D10 tests, route metadata wiring and existing workflow safety assertions. A real full-mixture estimator remains a separate future phase and is not authorized here.
