# Guitar-FL front-end integration study design V1

Date: 2026-10-06  
Branch: `astra-work`  
Status: **DESIGN FROZEN — EMPIRICAL INTEGRATION NOT AUTHORIZED**

## Purpose

Test whether the frozen François-Leduc-trained guitar front end can replace Basic Pitch **only at Astra's generic guitar note-event boundary** while preserving the existing role-evidence, structure/timing, rhythm-spelling, and fretboard contracts.

This is not a Production replacement plan. It is a bounded integration study.

## Evidence motivating the study

Fresh-front-end feasibility V1 passed every prospectively frozen gate on the consumed GAPS v1.1 test population:

- Basic Pitch pooled F1: **0.481443**
- `guitar-fl.pth` pooled F1: **0.837591**
- absolute pooled F1 gain: **+0.356148**
- Basic Pitch precision / recall: **0.420768 / 0.562565**
- guitar-fl precision / recall: **0.834848 / 0.840352**
- all 27 performer floors passed
- zero training, threshold search, or reference-derived mutation

This supports front-end/representation quality as a major bottleneck, but does not prove end-to-end tab quality.

## Frozen intervention identity

The integration candidate must remain exactly:

- package/source: `xavriley/hf_midi_transcription`
- source commit: `96f6797881e9497cbfc8f8e5deccea9c1f2f7adc`
- checkpoint: `guitar-fl.pth`
- checkpoint SHA-256: `50d93dba89bdd3401849bc735614478e83d9f46d21fa3f71d8aca5acc0a52028`
- effective inference family: non-piano `Regress_onset_offset_frame_velocity_CRNN`
- effective onset threshold: **0.3**
- effective offset threshold: **0.3**
- effective frame threshold: **0.1**
- sample rate: **16 kHz**
- frame rate: **100 Hz**
- no optimizer steps
- no threshold search

The wrapper-key packaging repair (`instrument="guitar"` with the explicit frozen `guitar-fl.pth` checkpoint path) is operational only and does not change model identity.

## Integration boundary

The candidate may replace Basic Pitch only as the producer of generic guitar note events.

Normalize each frozen model note event into the existing deterministic note-event shape:

- `midi`: integer 0–127
- `start`: source onset seconds
- `end`: source offset seconds when available
- `duration`: derived only as `end - start`
- immutable source-event index / provenance
- front-end provenance must identify the frozen checkpoint SHA

No confidence value may be invented from MIDI velocity or treated as calibrated probability.

### Explicitly unchanged downstream components

The study must not modify:

- stereo/spatial role-evidence logic;
- lead/rhythm/bass role semantics;
- role abstention behavior;
- structure-map construction;
- V4-origin timing authority;
- structure snapping / quantization rules;
- contextual rhythm spelling;
- fretboard path optimization;
- string/fret objective or weights;
- separator identity;
- bass path;
- thresholds of any existing downstream evaluator;
- Production or `main`.

The front end itself must **not** infer lead versus rhythm. For requested lead/rhythm output, existing role evidence must still be complete; abstention remains fail-closed.

## Stage A — model-free adapter contract

Before any real-audio integration run, freeze an adapter that converts previously frozen guitar-fl event JSON/MIDI into the exact generic event contract consumed by `runFreshDeterministicPipeline`.

Required tests:

1. event count preserved;
2. MIDI pitch preserved exactly;
3. onset preserved exactly to parser precision;
4. offset preserved when available;
5. source ordering deterministic;
6. duplicate simultaneous pitches are not silently deduplicated;
7. no role label is invented;
8. no string/fret is invented upstream of the fretboard optimizer;
9. no confidence is synthesized from velocity;
10. adapter is reference-blind and performs no network/model access.

Stage A may use synthetic fixtures and previously frozen candidate JSON only. It must not use GAPS references or Go My Way reference labels.

## Stage B — fresh integration evaluation

Any empirical Stage B requires a new explicit authorization and a new fresh evaluation source.

### Evaluation-source requirements

The source must:

- be rights-cleared for the intended development evaluation;
- contain real guitar audio;
- be fresh with respect to the current project;
- exclude the consumed GAPS v1.1 test set;
- exclude Go My Way;
- exclude consumed GuitarSet populations;
- exclude Guitar-TECHS material already used for development/training/diagnosis;
- contain independent note pitch+onset truth;
- preferably contain independent string/fret truth if the study will score final tablature;
- have source identities/split/hashes frozen before inference.

If no qualifying source with independent string/fret truth exists, Stage B must be limited to **integration invariants plus note/onset quality** and may not claim final-tab validation.

## Comparator and intervention

Comparator:
- current frozen Basic Pitch 0.4.0 note-event front end;
- exact current downstream pipeline.

Intervention:
- frozen `guitar-fl.pth` note-event front end;
- exact same downstream pipeline.

Only the front-end note-event producer may differ.

## Required measurements

At minimum:

### Front-end preservation
- note/onset precision, recall, F1;
- prediction/reference ratio;
- unmatched prediction/reference counts.

### Integration integrity
- event count entering downstream pipeline;
- event count after structure mapping;
- source-event identity preservation rate;
- timing delta introduced downstream;
- fraction of events assigned string/fret;
- fretboard optimizer abstentions/failures;
- role-evidence complete/abstained counts;
- any events promoted despite role abstention: must be **0**.

### End-to-end musical quality, only if valid truth exists
- exact pitch+onset;
- exact string+fret+onset;
- measure-level completeness;
- rhythm-position accuracy under the frozen timing map.

## Prospective gate principles

Exact numerical gates must be frozen after a fresh evaluation source is identified and before reference-facing scoring.

The gate must require all of:

1. intervention retains a material front-end advantage over Basic Pitch;
2. zero violation of role-abstention semantics;
3. zero source-event identity corruption;
4. no material timing regression introduced by the adapter/downstream path;
5. no increase in catastrophic fretboard-path failures;
6. if string/fret truth exists, a prospectively defined material end-to-end improvement;
7. zero training;
8. zero threshold search;
9. zero reference-derived prediction mutation.

A strong note/onset score alone cannot override an integration-contract failure.

## Rights / product boundary

The public model/code repository is MIT-labeled, but that does **not** by itself establish commercial rights for every underlying François-Leduc training substrate.

Existing Astra review of the François Leduc Guitar Dataset records:
- original distribution restrictions/research-use history;
- third-party score/audio provenance;
- newer MIT-labeled packaging that does not, by itself, resolve all underlying rights.

Therefore:

- internal research/development evaluation may be designed separately under an explicit authorization;
- **customer/Production integration remains blocked pending a dedicated checkpoint-training-lineage rights review**;
- a passed integration study cannot override this rights blocker.

## Stop rules

If Stage B fails its frozen gate:

- stop;
- do not tune thresholds;
- do not modify downstream quantization/fretboard weights to rescue the candidate;
- do not use the failed evaluation source for iterative parameter selection;
- do not mutate Go My Way;
- do not change Production or `main`.

If Stage B passes:

- record only that the frozen front end is technically supported for a separately authorized product-readiness phase;
- do not promote automatically.

## Current authorization boundary

This document authorizes **no empirical integration execution**.

The next permissible work is:
1. model-free Stage-A adapter implementation + unit tests, **only after explicit authorization**;
2. metadata/rights search for a fresh Stage-B evaluation source;
3. dedicated training-lineage rights review.

No real-audio inference, fresh-reference inspection, scoring, model download for a new run, Production mutation, or `main` change is authorized by this design.
