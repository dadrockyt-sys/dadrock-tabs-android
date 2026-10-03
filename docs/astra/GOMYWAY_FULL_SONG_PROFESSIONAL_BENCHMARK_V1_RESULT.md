# Go My Way Full-Song Professional Benchmark V1 — Result

Date: 2026-10-03  
Branch: `astra-work`

## Status

GitHub Actions run: `37094392537` — **success**  
Head commit: `b36c99a51fca367d288862dda351515457e6d3af`  
Artifact: `11262994060`  
Artifact digest: `sha256:ae73d963ef985beaf26cf9e7c1cbd1780e0bb1e4757e40f6ae3c85c3662045b0`

Source audio was pinned from `main`:
- commit `74dacf322bb979c26a47786e2380c59d2d40e364`
- `public/gomywayfullaitest.m4a`
- Git blob `5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`

Professional bass and lead PDFs were also identity-verified from that pinned `main` commit.

## Frozen inference path

- BS-Roformer-SW 6-stem FP16 ONNX
- Basic Pitch 0.4.0 / frozen TFLite identity
- no reference access during inference
- no threshold search
- no separator-output correction
- no note mutation
- exact MIDI + onset one-to-one scoring
- fixed 50 ms onset tolerance

Prediction streams produced:
- whole mix: **787 events**
- raw guitar stem: **1,065 events**
- raw bass stem: **701 events**

The guitar and bass event streams are cached in the workflow artifact for later reference scoring.

## Rhythm target

Full professional rhythm target spans measures **1–113**.

Pitched reference targets scored: **971**

Unpitched/dead-note reference events are intentionally excluded from this exact-MIDI score.

## Full-song rhythm result

### Whole-mix control

- predictions in scoring window: **766**
- targets: **971**
- true positives: **18**
- false positives: **748**
- false negatives: **953**
- precision: **0.02350**
- recall: **0.01854**
- F1: **0.02073** (**2.07%**)
- mean absolute onset error among matched notes: **30.55 ms**

### Raw BS-Roformer guitar stem

- predictions in scoring window: **1,025**
- targets: **971**
- true positives: **36**
- false positives: **989**
- false negatives: **935**
- precision: **0.03512**
- recall: **0.03708**
- F1: **0.03607** (**3.61%**)
- mean absolute onset error among matched notes: **22.83 ms**

Raw-guitar F1 improvement over whole mix:
- absolute: **+0.01535**
- relative to whole-mix F1: about **+74%**

Example strongest measure:
- measure 83: F1 **0.25**, 3 exact pitch/onset matches from 10 professional targets.

## Interpretation

The separator is helping: exact professional-reference matches doubled from 18 to 36 and matched timing became tighter.

However, the full-song exact-MIDI/onset agreement remains very low. The current frozen Basic Pitch path produces roughly the right order of event quantity but very few events land on the exact professional pitch at the correct onset.

This makes the transcription front end / musical-event interpretation a much larger remaining bottleneck than merely detecting that guitar is present.

Do not interpret 3.61% as a complete-tab quality percentage. This score covers only exact pitch/onset matching; it does not yet score:
- string/fret choice;
- duration/sustain;
- bends;
- slides;
- muting;
- picking direction;
- chord identity;
- role-specific lead vs rhythm assignment.

Those dimensions can only reduce complete-tab agreement unless a future representation improves them.

## Bass and lead

The full professional references are present on pinned `main/public`:

Bass:
- `public/Gomywaybassreference.pdf`
- SHA-256 `18e6822394980d22a960a1bd4d923aaddf677f3341b8cc1a2dbb29ea1e8771d0`
- measures 1–113

Lead:
- `public/Gomywayleadreference.pdf`
- SHA-256 `a11a2c04fdda73e667df16df99aedf9ae0a3ed7af85f62f3c1773b7784a97f56`
- measures 1–113

The raw bass and guitar prediction streams were cached, but bass/lead are not scored yet because equivalent fully normalized machine-readable note labels are not committed.

## Next step

Normalize bass and lead professional PDF structure/reference evidence without consulting the candidate predictions.

The prediction cache must remain frozen while that normalization is performed. Once normalized references are independently frozen, score:
- raw bass stem vs professional bass;
- raw guitar stem vs professional lead;
- raw guitar stem vs professional rhythm;
- optionally joint guitar evidence vs combined lead+rhythm to distinguish transcription failure from role-assignment failure.

No production promotion is authorized.
