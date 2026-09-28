# Astra V2 Stage-A polyphony-safe pitch admission design V2

Date: 2026-09-28  
Status: **PROSPECTIVE NEW MEASUREMENT VERSION — ORIGINAL STAGE-A V1 FAILURE PRESERVED**

## Motivation

The original Stage-A V1 admission failed only because four per-event fundamental estimates in simultaneous chord rows exceeded ±15 cents.

Post-hoc source review established that the frozen estimator searched for the largest spectral peak in a mixed chord waveform over a ±15% band (about +242/-281 cents), so another simultaneous chord tone can win the search.

The original Stage-A result remains failed. This V2 design does not reinterpret or overwrite it.

## Scientific configuration unchanged

Unchanged:
- V2 parameter manifest and hash;
- selected Stage-A rows;
- V2 waveform renderer equations;
- all marginal ranges/distributions;
- per-note deterministic substreams;
- frontend/CQT;
- labels/references/timing;
- ±15-cent pitch tolerance;
- all non-pitch Stage-A criteria;
- total waveform render ceiling <=112;
- audio/time/storage ceilings;
- no models/inference/optimizer;
- no P1/P2/P3.

Only the **measurement waveform used for simultaneous-event pitch validation** changes.

## Pitch-validity rule V2

### Non-simultaneous attacked events

Use the original Stage-A acoustic estimator unchanged:
- stable sustain window;
- FFT magnitude;
- target-centered search used by the existing helper;
- absolute error must be <= **15 cents**.

### Simultaneous attacked events

An attacked event is simultaneous when at least one other attacked event in the same template has the same start time within **1 microsecond**.

Do not estimate that event's pitch from the mixed chord waveform.

Instead create one deterministic **event-isolated shadow render**:

- preserve the original template ID;
- preserve the original variant;
- preserve the original event index;
- preserve the original event's string/fret/start/end/attack/palm/soft fields;
- preserve the exact V2 clip-level manifest override;
- preserve the exact per-note V1 substream keyed by original event index;
- generate only that event's oscillator/component contribution;
- apply the same source-domain post chain:
  - coloration filters;
  - static nonlinear wet mix;
  - deterministic broadband noise/hum;
  - body filter;
  - peak normalization;
  - resample to 22,050 Hz.

Then run the same frozen acoustic fundamental estimator and require:
- absolute error <= **15 cents**.

The shadow waveform is a **measurement fixture only**. It is never inserted into train/validation/test datasets.

## Shadow-render implementation invariants

The shadow helper must:
1. call the same frozen component generator and parameter functions used by V1 source-domain rendering;
2. use the original template ID and original event index when deriving note/component RNG state;
3. use the manifest override exactly as Stage-A V1 did;
4. not alter oscillator frequency;
5. not alter event timing;
6. not alter any stored label/reference;
7. not modify the main source-domain renderer.

Focused tests must verify:
- event-index preservation;
- active/inactive hum contract unchanged;
- shadow output deterministic;
- a single-event nonnegative template's shadow component path agrees with the corresponding ordinary-render pitch within the same ±15-cent criterion;
- no dataset write occurs.

## Frozen Stage-A sample

Exactly the same 28 V2 rows:
- training positions 0 and 29 in each family;
- primary-challenge positions 0 and 5 in each family;
- paired clean controls.

No row substitution.

## Render accounting

Base Stage-A V1 pattern:
- 28 clean controls;
- 28 V2 rows;
- 28 V2 deterministic rerenders;
- total **84** waveform render operations.

Selected chord rows contain 24 attacked events across the four chord rows.

V2 adds:
- exactly **24 event-isolated shadow renders**.

Total:
- **108 waveform render operations**;
- **216 synthetic audio seconds** at 2 s/render.

Frozen ceiling remains:
- <=112 waveform renders;
- <=224 synthetic audio seconds;
- <=20 minutes;
- <=150 MB persisted artifacts.

No extra retries.

## Full Stage-A V2 gates

All must pass:

1. deterministic V2 rerender identity;
2. exact state identity;
3. exact onset identity;
4. exact reference identity;
5. finite waveform/CQT;
6. peak <0.999;
7. pitch validity:
   - non-simultaneous attacked events: original mixed-row estimator <=15 cents;
   - simultaneous attacked events: event-isolated shadow estimator <=15 cents;
8. no unlabeled transient injection;
9. every positive selected V2 row changes prepared CQT vs paired control;
10. exact frozen manifest binding;
11. exact selected rows;
12. render/audio/time/storage ceilings.

The mixed-waveform chord per-event estimates from the original method remain report-only diagnostics and do not gate V2, because V2 prospectively defines them as source-confounded.

## Failure handling

If any V2 gate fails:
- freeze failure;
- no retry;
- no row substitution;
- no threshold relaxation;
- no Stage B;
- no model work.

## Success handling

If all gates pass:
- freeze Stage-A V2 pass;
- Stage B may then be implemented/executed model-free under the already-frozen 35/35 coverage gate;
- no model training follows automatically.

## Decision

**GO for one separately versioned synthetic/model-free Stage-A V2 measurement execution.**
