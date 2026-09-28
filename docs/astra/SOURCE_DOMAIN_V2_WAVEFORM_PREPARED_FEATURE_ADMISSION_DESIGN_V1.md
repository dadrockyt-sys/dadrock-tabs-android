# Astra V2 waveform / prepared-feature admission design

Date: 2026-09-28  
Status: **PROSPECTIVE MODEL-FREE DESIGN FROZEN — NO RENDER EXECUTION / NO MODEL**

## Purpose

Define the next bounded model-free admission stage for the already-frozen source-domain joint-coverage V2 parameter manifest.

Inputs already frozen:
- `docs/astra/SOURCE_DOMAIN_JOINT_COVERAGE_PROTOCOL_V2.md`
- `docs/astra/SOURCE_DOMAIN_JOINT_COVERAGE_PROTOCOL_V2.json`
- `docs/astra/SOURCE_DOMAIN_JOINT_COVERAGE_MANIFEST_RESULT_V2.json`
- manifest content SHA-256 `2dc6e09c3c617ac55e84e386e6fc6ff26d0e68ed81016169cad5ce72c7d95469`

This design does not authorize model loading, inference, optimizer work, threshold work, P1/P2 access or P3 access.

## Scientific question

The zero-render V2 manifest proves parameter-space stratification only.

The next question is:

> Does the frozen V2 parameter plan survive the waveform renderer and frozen CQT frontend as a deterministic, label-preserving, musically valid source-domain coverage package whose held-out primary challenge is not an extreme feature-space outlier relative to V2 training?

This is a model-free admission question.

It does not ask whether a model improves.

## Frozen implementation boundary

The V2 renderer must reuse the existing V1 waveform equations and source-domain parameter semantics.

Allowed change:
- replace V1 clip-level independent random parameter draws with the exact frozen V2 manifest values.

Not allowed:
- change any V1 marginal range;
- change any waveform equation;
- change per-note jitter distributions;
- change label timing;
- change CQT/frontend code;
- alter V2 train or challenge manifests;
- substitute the old V1 fixed challenge for the V2 primary challenge;
- choose rows from model outcomes.

## Two-stage admission

### Stage A — small deterministic acoustic admission

Render exactly **28 V2 source-domain clips**:
- 14 training-manifest clips: exactly 2 per family;
- 14 primary-challenge clips: exactly 2 per family.

For each family, select rows independently of acoustic/model results:
- training sample: family-local manifest positions **0 and 29** after sorting by repository row index;
- challenge sample: family-local manifest positions **0 and 5** after sorting by repository row index.

These positions are frozen before rendering.

Also render the paired clean-control waveform for each selected row.

Total Stage-A waveform renders:
- 28 V2 source-domain;
- 28 clean controls;
- **56 renders total**;
- **112 synthetic audio seconds**.

No other fixture row may be substituted after seeing results.

### Stage A diagnostics

For each selected row save:
- control and V2 waveform SHA-256;
- peak magnitude;
- RMS;
- all attacked-event 10%–90% rise-time estimates;
- all attacked-event first-difference energy;
- stable-sustain fundamental-frequency error in cents relative to expected pitch;
- spectral centroid;
- frozen prepared-CQT SHA-256;
- labeled-onset positive CQT flux;
- row-level mean absolute CQT displacement from paired control;
- state/onset/reference hashes.

### Stage A hard admission

All must pass:

1. deterministic rerender:
   - every V2 selected waveform is byte-identical across two independent renders from the same manifest row;

2. exact label/reference identity:
   - state, onset and reference objects are exactly identical to paired control;

3. finite audio/features:
   - all waveform and CQT values finite;

4. clipping:
   - final absolute waveform peak < **0.999** for every V2 row;

5. fundamental preservation:
   - every measurable attacked-event stable fundamental is within **±15 cents** of the expected pitch;

6. no unlabeled transient injection:
   - renderer metadata may mark transient injection only for events whose frozen onset label is true;

7. CQT propagation:
   - every positive-note selected V2 row differs from its paired control in prepared CQT;
   - negative-only rows, when selected by the fixed positions, must remain unlabeled;

8. deterministic manifest binding:
   - exact manifest row parameters used for render must hash back to the frozen manifest content SHA-256;
   - no parameter is redrawn.

If Stage A fails, stop. Do not run Stage B and do not modify gates/ranges/sample rows.

## Stage B — full bounded model-free V2 preparation

Stage B is permitted only after Stage A passes.

Prepare three 294-row arms:

### Control
Exact frozen S9/S11 control.

### V2 intervention
- source-domain V2 renderer on exactly the 210 training rows;
- validation and ordinary test remain bit-identical to control.

### V2 primary challenge
- source-domain V2 challenge renderer on exactly the 42 test rows;
- train and validation remain bit-identical to control.

All non-feature arrays must be bit-identical across the three arms, including preservation of historical S9 fixed-width training-chord metadata.

The old V1 fixed challenge is **not** part of the V2 gate. It may be preserved as an optional secondary model-free diagnostic only if doing so does not increase the frozen render ceiling.

## Stage B model-free waveform descriptors

For each rendered V2 training/challenge row compute only source/prepared diagnostics:
- waveform RMS;
- spectral centroid;
- median attacked-event rise time;
- median attacked-event first-difference energy;
- median labeled-onset prepared-CQT positive flux;
- row-level mean absolute prepared-CQT displacement from paired control.

No model score or thresholded prediction may be computed.

## Stage B coverage admission

Coverage is evaluated **within each musical family**, using the 30 V2 training rows and 6 V2 primary-challenge rows.

For each of these five comparable descriptors:
1. waveform RMS;
2. spectral centroid;
3. attacked-event first-difference energy;
4. labeled-onset prepared-CQT positive flux;
5. row-level prepared-CQT displacement;

compute the empirical V2-training 5th and 95th percentiles per family.

For each family and descriptor, require:
- the **median** of the six primary-challenge rows to lie inside the inclusive training **5th–95th percentile interval**.

Rise time is reported separately because some family/event structures can produce missing or unreliable envelope estimates. It is not a Stage-B coverage gate beyond Stage-A physical validity.

This gives exactly:
- 7 families × 5 descriptors = **35 family/descriptor coverage checks**;
- required pass count = **35/35**.

The gate is deliberately based on generic central-support coverage, not on V1 model scores and not on matching the old V1 challenge.

### Additional Stage B identity/admission checks

All must pass:
- intervention changed-feature rows exactly equal the 210 train rows;
- primary-challenge changed-feature rows exactly equal the 42 test rows;
- intervention validation/test features bit-identical to control;
- primary-challenge train/validation features bit-identical to control;
- all non-feature arrays bit-identical;
- reconstructed state/onset match every row;
- held-out/non-S9 references exactly match;
- historical S9 training-chord truncated strings preserved byte-identically;
- feature arrays finite;
- exact row parameter binding to frozen manifest;
- repeated full preparation with the same deterministic runtime produces identical per-array content hashes.

## Optional secondary V1 stress description

The old V1 fixed challenge may be evaluated **model-free only** as a secondary continuity diagnostic if its already-frozen prepared arrays can be reused without new waveform rendering.

Permitted reporting:
- V1 challenge family median onset-flux percentile under V2 training prepared features;
- V1 challenge family median row-displacement percentile under V2 training prepared features.

These numbers:
- are diagnostic only;
- are not a V2 gate;
- cannot trigger parameter/range/challenge changes.

## Hard execution ceiling

Stage A:
- waveform renders <= **112** including deterministic rerenders and controls;
- synthetic audio <= **224 s**;
- wall time <= **20 min**;
- persisted artifacts <= **150 MB**.

Stage B:
- full source/control render operations <= **900**;
- synthetic audio <= **1,800 s**;
- wall time <= **45 min**;
- persisted artifacts <= **500 MB**.

Both stages:
- CPU only;
- $0 paid compute;
- model loads **0**;
- inference **false**;
- optimizer steps **0**;
- threshold search/retuning **false**;
- automatic retry **false**;
- P1/P2 access **false**;
- P3 access **false**;
- Codespaces/Vercel/main/Production mutation **false**.

## Failure handling

A failed admission is frozen as a design/representation failure.

Do not:
- replace failed sample rows;
- widen ranges;
- narrow ranges;
- change the primary V2 challenge;
- relax 5th–95th coverage gates;
- modify frontend;
- modify renderer equations;
- launch a model to “see if it still works”.

Any change requires a new design version.

## Success meaning

A full pass would establish only that:
- the V2 joint parameter plan maps deterministically into physically valid synthetic waveforms;
- labels/timing/pitch identity are preserved;
- the held-out primary V2 challenge lies within central training support on the frozen source/CQT diagnostics;
- V2 is ready for a separately frozen prospective training design.

It would not establish:
- real-guitar transfer;
- P1/P2 improvement;
- architectural adequacy;
- P3 readiness.

## Decision

**GO for offline implementation of Stage A only.**

Do not run Stage B until Stage A has passed and been frozen.

Do not train a model.
