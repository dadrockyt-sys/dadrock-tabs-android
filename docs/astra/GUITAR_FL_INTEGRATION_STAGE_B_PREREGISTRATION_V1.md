# Guitar-FL integration Stage B preregistration V1

Date: 2026-10-06
Branch: `astra-work`
Status: **PREREGISTERED DESIGN — NO CAPTURE / SPENDING / EMPIRICAL EXECUTION AUTHORIZED**

## Objective

Determine whether replacing only the generic-guitar note-event producer with the frozen `guitar-fl.pth` front end materially improves end-to-end Astra guitar transcription on a new purpose-built, independently referenced real-guitar holdout.

Comparator and intervention must share the exact same downstream pipeline.

## Frozen systems

### Comparator

- Basic Pitch 0.4.0
- historical frozen defaults used by Astra
- no threshold search
- no prediction mutation

### Intervention

- `guitar-fl.pth`
- SHA-256 `50d93dba89bdd3401849bc735614478e83d9f46d21fa3f71d8aca5acc0a52028`
- source commit `96f6797881e9497cbfc8f8e5deccea9c1f2f7adc`
- effective onset threshold 0.3
- effective offset threshold 0.3
- effective frame threshold 0.1
- 16 kHz / 100 fps
- Stage-A adapter `astra_backend/guitarFlNoteEventAdapter.mjs`
- no threshold search
- no optimizer steps

### Downstream equality requirement

Both paths must use the same frozen:
- evaluated DI audio;
- role declaration supplied by the capture plan;
- structure-map construction;
- V4-origin timing authority;
- structure snapping / quantization;
- contextual rhythm spelling;
- fretboard path optimizer and weights;
- product-shell/evaluator code;
- scorer.

Only the generic note-event producer may differ.

## Holdout architecture

Every admitted performance must contain:

1. clean guitar DI for model evaluation;
2. independent physical string/fret-state reference;
3. independent excitation/event-birth reference;
4. shared hardware clock or frozen hardware-sync markers.

No reference event may be derived from evaluated DI, spectrograms, onset detectors, pitch detectors, score-to-audio alignment, model activations, or manual waveform adjustment.

## Population

Freeze a minimum population of:

- **6 distinct performers**;
- **5 content categories**: `chords`, `scales`, `singlenotes`, `techniques`, `music`;
- at least **2 admitted underlying performances per performer/category cell**;
- therefore at least **60 admitted underlying performances**;
- at least **3,000 independent reference note births pooled**;
- at least **300 reference note births per performer**;
- at least **400 reference note births per category**.

Multiple microphones, reamps, channel views, renders, crops, or effects of one take count as **one** underlying performance and may not multiply the population.

Calibration performances are permanently excluded.

## Role declaration

The front end has no role authority.

Each capture slot must be preregistered as exactly one of:
- `lead`
- `rhythm`

The role label comes from the frozen capture plan / performer instruction, never from either front end.

The study does not evaluate bass.

Both comparator and intervention receive the identical frozen role declaration for each take.

## Content constraints

- no Go My Way;
- no protected-song material;
- prefer original, commissioned-cleared, or public-domain exercises/music;
- content identity fixed before capture;
- no slot replacement based on model output or musical difficulty.

## Capture admission / anti-cherry-picking

For each frozen slot:

- attempts receive stable IDs;
- only objective transport/hardware QA may justify a retake;
- the **first transport-valid attempt is admitted**;
- an admitted take cannot be discarded for playing quality, model output, difficulty, mistakes, or aesthetics;
- capture personnel cannot view comparator/intervention results;
- failed attempts and objective reason codes remain logged;
- no player/category/slot substitutions after capture begins.

## Candidate generation blinding

For both front ends:

- candidate generation may read admitted DI audio only;
- reference channels/files must be unavailable to candidate-generation jobs;
- candidates are frozen with per-file SHA-256 manifests before reference decoding;
- no prediction changes after freeze.

## Reference decoding

The physical-reference decoder must be frozen on non-holdout calibration material before the first holdout take.

It must deterministically define:
- picked/re-picked note births;
- hammer-ons;
- pull-offs;
- taps;
- slides;
- bends/vibrato nominal-MIDI projection;
- chord per-string births;
- releases/termination fields.

No reference decoder changes after holdout capture begins.

## Primary metrics

All onset comparisons use a frozen **50 ms** tolerance unless the physical-clock preregistration freezes a stricter tolerance before capture.

### Front-end pitch+onset
- exact pitch+onset precision;
- exact pitch+onset recall;
- exact pitch+onset F1;
- prediction/reference event-count ratio;
- unmatched prediction/reference counts.

### End-to-end tablature
Using the same downstream pipeline:
- exact string+fret+onset precision;
- exact string+fret+onset recall;
- exact string+fret+onset F1;
- string/fret assignment coverage;
- fretboard-path unresolved rate.

### Integration invariants
- adapter input/output event count;
- exact source MIDI preservation;
- exact source onset preservation;
- exact source offset preservation where available;
- source-event identity preservation;
- events promoted despite role abstention;
- timing displacement introduced by the adapter itself.

## Frozen advancement gate

**Every condition below must pass.**

### A. Pitch+onset improvement

Intervention pooled pitch+onset:
- F1 >= comparator F1 + **0.15**
- F1 >= **0.70**
- precision >= comparator precision + **0.15**
- precision >= **0.65**
- recall >= comparator recall - **0.03**
- recall >= **0.68**

### B. Event density

Intervention prediction/reference ratio:
- >= **0.80**
- <= **1.25**

### C. End-to-end string/fret improvement

Intervention pooled exact string+fret+onset:
- F1 >= comparator F1 + **0.10**
- F1 >= **0.55**
- precision >= comparator precision + **0.10**
- recall >= comparator recall - **0.05**

### D. Performer robustness

For every frozen performer:
- intervention pitch+onset F1 >= comparator pitch+onset F1 - **0.05**
- intervention string+fret+onset F1 >= comparator string+fret+onset F1 - **0.05**

### E. Category robustness

For every frozen category:
- intervention pitch+onset macro F1 >= comparator macro F1 - **0.05**
- intervention string+fret+onset macro F1 >= comparator macro F1 - **0.05**

Across all five categories:
- intervention category-macro pitch+onset F1 >= comparator + **0.10**
- intervention category-macro string+fret+onset F1 >= comparator + **0.08**

### F. Fretboard-path stability

- intervention unresolved fretboard-path rate <= comparator rate + **0.02**
- intervention unresolved fretboard-path rate <= **0.10**

### G. Integration integrity

Required exactly:
- source-event identity corruption count = **0**
- adapter MIDI corruption count = **0**
- adapter onset corruption count = **0**
- adapter offset corruption count = **0**
- adapter-created role labels = **0**
- adapter-created confidence values = **0**
- adapter-created string/fret values = **0**
- events promoted through an abstained role path = **0**
- optimizer steps = **0**
- threshold searches = **0**
- reference-derived prediction mutations = **0**

No aggregate score may override an invariant failure.

## Decision rule

`passed = A && B && C && D && E && F && G`

If any condition fails:
- Stage B fails;
- stop;
- do not tune thresholds;
- do not change adapter semantics;
- do not change fretboard weights;
- do not remove hard performers/categories;
- do not retry scientifically on the same holdout;
- the holdout becomes consumed.

If all conditions pass:
- record only that the frozen intervention is technically supported for a separately authorized product-readiness phase;
- do not change Production or `main` automatically.

## Rights gate

Before capture authorization, every performer/session/content item must have:
- explicit product-validation recording/use permission;
- recording ownership/use grant;
- composition/content provenance;
- protected-song exclusion;
- immutable rights-document ID + SHA-256.

Failure to complete the rights manifest blocks capture.

## Product-rights blocker for the model

Even a Stage-B technical pass does not authorize customer use of `guitar-fl.pth`.

A separate checkpoint-training-lineage review must resolve the François-Leduc substrate rights sufficiently for the intended commercial/product use before Production adoption can be considered.

## Current authority

No capture, performer contact, spending, procurement, real-audio inference, holdout reference generation, or scoring is authorized.

The next step may only prepare:
- capture-plan/manifest schemas;
- synthetic guards/tests;
- rights-manifest schema;
- hardware/reference architecture decision packet.

Those preparation steps themselves require no holdout media and must not contact performers or vendors.
