# STRUCTURE_CONDITIONED_SHADOW_PROJECTION_V1 — PRE-IMPLEMENTATION FREEZE

Date: 2026-09-03 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **`REFERENCE-BLIND SHADOW IMPLEMENTATION AUTHORIZED / PRODUCT OUTPUT MUTATION FORBIDDEN / REFERENCE SCORING NOT AUTHORIZED`**

## Purpose

Freeze Phase 2 before code so the Songsterr-inspired Conditioning V1 contract can influence a deterministic **shadow-only copied projection** of analyzer events without changing generated tablature, historical V143 output, PDF rendering or Production behavior.

This is an independently specified DadRock research adapter. It is not a reconstruction of Songsterr's private implementation.

## Scientific boundary

Allowed:

- pure deterministic JS;
- copied analyzer event input already present in the DadRock response boundary;
- explicit Conditioning V1 structure values;
- Conditioning V1 tuning/capo;
- synthetic/reference-blind fixtures;
- shadow metadata appended to the research-branch API response.

Forbidden:

- overwriting/mutating `generatedTab`;
- overwriting/mutating normalized `events`;
- overwriting/mutating V143 `renderEvents`;
- overwriting/mutating `measureGrid`;
- changing `analysisEngine`;
- changing analyzer selection;
- changing V143 safety gates;
- changing PDF renderer selection;
- GuitarSet/SplitMySong/GOAT reads or scores;
- GPU/CUDA/Modal invocation;
- Production promotion.

## Frozen name

`STRUCTURE_CONDITIONED_SHADOW_PROJECTION_V1`

Suggested response member:

`conditioningShadowProjection`

## Input — FROZEN

```js
buildAiTabConditionedShadowProjectionV1({
  events: structuredPayload.events,
  conditioning,
})
```

The adapter receives **copies** of already-normalized analyzer events and the server-normalized Conditioning V1 object.

Each input event may contain:

- `start` / `end` seconds;
- `midi` pitch;
- existing `stringIndex` / `fret`;
- other normalized metadata, which the shadow adapter must not mutate.

## Structure resolution — FROZEN

### Explicitness rule

No hidden default tempo, meter or pickup may be manufactured.

Structure placement is fully resolvable only when all three are explicit:

- `tempoBpm !== null`;
- `timeSignature !== null`;
- `pickupBeats !== null`.

Otherwise:

`structure.status = "UNRESOLVED_AUTO_STRUCTURE"`

and the adapter must leave measure/beat/projected timing fields `null` while still allowing independent tuning/capo shadow decoding.

This means `pickupBeats=0` is meaningfully different from `pickupBeats=null` (Auto).

### BPM convention

For this Phase 2 shadow contract, explicit `tempoBpm` is defined as **quarter-note BPM**.

```text
quarterSeconds = 60 / tempoBpm
signatureUnitSeconds = quarterSeconds * (4 / denominator)
measureSeconds = signatureUnitSeconds * numerator
pickupSeconds = pickupBeats * signatureUnitSeconds
```

`signatureUnitSeconds` is deliberately named after the denominator unit rather than claiming it is always the perceptual beat in compound meters such as 6/8.

### Pickup/bar phase

For explicit structure:

- events whose structure timestamp is `< pickupSeconds` belong to `measureNumber=0` and `pickup=true`;
- the first complete measure begins at `pickupSeconds` and is `measureNumber=1`;
- events exactly on `pickupSeconds` belong to measure 1.

For pickup events, beat/unit position is measured from time zero inside the pickup span. For complete measures, position is measured from `pickupSeconds`.

### Straight/triplet feel

`feel=straight`:

- quantization divisions per signature unit = 4.

`feel=triplet`:

- quantization divisions per signature unit = 3.

`feel=auto`:

- do **not** guess straight or triplet;
- explicit tempo/meter/pickup may still resolve measure/unit placement from the original source timestamp;
- `quantizationStatus="UNRESOLVED_AUTO_FEEL"`;
- `projectedStart = sourceStart`;
- `subdivisionIndex = null`.

For straight/triplet, quantize copied shadow onset to the nearest subdivision using deterministic half-up rounding for non-negative time:

```text
slot = floor((sourceStart / subdivisionSeconds) + 0.5)
projectedStart = slot * subdivisionSeconds
```

Then derive measure/unit placement from `projectedStart`.

The source event timing is always preserved separately as `sourceStart` / `sourceEnd`.

## Shadow musical position — FROZEN

For resolved structure, output at minimum:

- `measureNumber` (0 for pickup, otherwise 1-based);
- `signatureUnitNumber` (1-based within pickup/full measure);
- `signatureUnitFraction` in `[0,1)`;
- `pickup` boolean;
- `projectedStart`;
- `subdivisionIndex` when feel is explicit.

This Phase 2 contract intentionally avoids labeling denominator units as universal perceptual `beats`.

## Tuning/capo shadow decode — FROZEN

Conditioning V1 stores `tuningMidi` physical open strings **low-to-high**. Existing DadRock tab string indexes are **high-to-low** (`stringIndex=0` is the highest-pitched string).

Therefore the decoder must reverse the low-to-high tuning for string-index enumeration while leaving the Conditioning V1 stored tuning unchanged.

For each DadRock string index:

```text
physicalOpenMidi = reversed(tuningMidi)[stringIndex]
soundingOpenMidi = physicalOpenMidi + capoFret
fret = eventMidi - soundingOpenMidi
```

A playable candidate requires integer fret `[0,24]`.

If no candidate exists:

- `conditionedStringIndex=null`;
- `conditionedFret=null`;
- `playableUnderConditioning=false`;
- source string/fret remain untouched.

### Candidate scoring — frozen compatibility heuristic

This shadow decoder uses the existing DadRock legacy fingering preferences as an independently fixed compatibility rule, not a Songsterr claim and not a reference-tuned rule.

Target fret:

- Lead: 7;
- Rhythm: 3;
- Bass: 5.

Score:

```text
score = abs(fret - targetFret) * 0.35

if fret == 0:
  Rhythm/Bass: score += -1.0
  Lead:        score +=  1.25

if previous conditioned fret exists:
  distance = abs(fret - previousFret)
  score += distance * 1.15
  if distance > 5:
    score += (distance - 5) * 2.0

if previous conditioned string exists:
  distance = abs(stringIndex - previousStringIndex)
  score += distance * 0.8
  if distance > 2:
    score += (distance - 2) * 1.5
```

Deterministic tie break:

1. lower numeric score;
2. lower `stringIndex`;
3. lower fret.

Previous-state continuity updates only when an event receives a playable conditioned position.

## Output — FROZEN

```json
{
  "shadowContract": {
    "name": "structure-conditioned-shadow-projection",
    "version": 1,
    "shadowOnly": true,
    "referenceBlind": true,
    "referenceScoreAuthorized": false,
    "productionEligible": false
  },
  "structure": {
    "status": "EXPLICIT_STRUCTURE_RESOLVED",
    "quantizationStatus": "STRAIGHT|TRIPLET|UNRESOLVED_AUTO_FEEL|UNRESOLVED_AUTO_STRUCTURE",
    "tempoBpm": 120,
    "timeSignature": {"numerator": 4, "denominator": 4},
    "pickupBeats": 0,
    "quarterSeconds": 0.5,
    "signatureUnitSeconds": 0.5,
    "measureSeconds": 2.0,
    "pickupSeconds": 0.0
  },
  "eventCount": 1,
  "events": [
    {
      "sourceEventIndex": 0,
      "sourceStart": 0.5,
      "sourceEnd": 0.7,
      "projectedStart": 0.5,
      "measureNumber": 1,
      "signatureUnitNumber": 2,
      "signatureUnitFraction": 0,
      "subdivisionIndex": 4,
      "pickup": false,
      "midi": 64,
      "sourceStringIndex": 0,
      "sourceFret": 0,
      "conditionedStringIndex": 0,
      "conditionedFret": 0,
      "playableUnderConditioning": true
    }
  ]
}
```

Exact floating-point serialization may use stable rounding; the implementation must be deterministic.

## Frozen synthetic/reference-blind tests

### S1 — Auto structure does not invent placement
Default Conditioning V1 (`tempo=null`, `meter=null`, `pickup=null`) -> `UNRESOLVED_AUTO_STRUCTURE`; measure/projected fields null. Tuning/capo decode may still operate.

### S2 — 120 BPM 4/4 straight, pickup 0
Expected:

- quarter/signature unit = 0.5 s;
- measure = 2.0 s;
- straight subdivision = 0.125 s;
- deterministic nearest-slot projection and 1-based measure/unit positions.

### S3 — 120 BPM 6/8 straight, pickup 0
Expected:

- quarter = 0.5 s;
- signature denominator unit (eighth) = 0.25 s;
- measure = 1.5 s.

This test explicitly protects denominator-aware timing from an accidental hard-coded 4/4 assumption.

### S4 — explicit one-unit pickup
120 BPM 4/4, pickupBeats=1:

- pickupSeconds=0.5;
- event at 0.25 s -> measure 0 / pickup true;
- event at 0.5 s -> measure 1 / pickup false.

### S5 — triplet feel
120 BPM 4/4, pickup 0, triplet -> subdivision 0.5/3 seconds and deterministic nearest triplet slot.

### S6 — Auto feel does not guess subdivision
Explicit tempo/meter/pickup but `feel=auto` -> structure placement resolved from `sourceStart`, projectedStart equals sourceStart, subdivisionIndex null, `quantizationStatus=UNRESOLVED_AUTO_FEEL`.

### S7 — Drop D + capo changes playable decoding
Use physical Drop D `[38,45,50,55,59,64]` plus capo 2 and synthetic pitches whose deterministic conditioned positions can be asserted. Stored physical tuning must remain unchanged.

### S8 — impossible pitch fails shadow decode closed
Pitch with no conditioned string/fret in `[0,24]` -> conditioned position null; source string/fret unchanged.

### S9 — source/product payload immutability
Building the shadow projection must not mutate input events/conditioning. Route appends `conditioningShadowProjection` without replacing `generatedTab`, `events`, `renderEvents`, `measureGrid` or `analysisEngine`.

### S10 — safety accounting
Output/test evidence must assert:

- `shadowOnly=true`;
- `referenceBlind=true`;
- `referenceScoreAuthorized=false`;
- `productionEligible=false`;
- reference score calls 0;
- GuitarSet read false;
- SplitMySong read false;
- GOAT restricted bytes read false;
- Modal invoked false;
- GPU used false;
- Production modified false.

## Promotion/evaluation state

`shadowImplementationAllowed=true`  
`syntheticContractTestsAllowed=true`  
`referenceFacingScoreAllowed=false`  
`productOutputMutationAllowed=false`  
`productionPromotionAuthorized=false`

The next valid action is to implement exactly this frozen shadow contract on `v143-contextual-prune-lobo`, run only deterministic reference-blind tests, checkpoint the result, and leave user-visible tablature behavior untouched.
