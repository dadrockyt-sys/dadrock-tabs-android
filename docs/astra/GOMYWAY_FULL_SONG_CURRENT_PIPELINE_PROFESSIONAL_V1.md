# Go My Way Full-Song Current Pipeline Professional Benchmark V1

Date: 2026-10-03
Branch: `astra-work`

## Purpose

Measure the current separator + frozen Basic Pitch stack against the real full-song Go My Way professional rhythm reference, using the exact audio in `main/public`.

This is existing-reference development evidence, not a sealed holdout.

## Frozen source

Main commit:
`74dacf322bb979c26a47786e2380c59d2d40e364`

Audio:
`public/gomywayfullaitest.m4a`

Git blob:
`5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`

The workflow verified the pinned main commit and source identities before inference.

## Inference

- separator: BS-Roformer-SW 6-stem FP16 ONNX
- separator SHA: `d3d2bac77a7023282cb5f35a5807179e34076b60589867b572275f1a8ec36444`
- transcriber: Basic Pitch 0.4.0
- onset threshold: 0.5
- frame threshold: 0.3
- minimum note length: 58 ms
- scoring tolerance: 50 ms
- no separator mutation
- no threshold search
- professional reference unavailable to inference

Prediction counts:
- whole mix: **787**
- raw guitar stem: **1065**
- raw bass stem: **701**

## Rhythm professional scorer

Complete measures 1-113:
- measures 1-16: professional intro fixture expanded under its frozen repeat contract
- measures 17-113: human-approved professional rhythm reference
- pitched targets: **971**
- dead/muted unpitched note entries excluded from pitch score: **71**

## Result

Whole mix exact MIDI + onset:
- TP: 18
- precision: **2.35%**
- recall: **1.85%**
- F1: **2.07%**

Raw guitar stem exact MIDI + onset:
- TP: 36
- precision: **3.51%**
- recall: **3.71%**
- F1: **3.61%**

Separator delta versus whole mix:
**+1.53 percentage points F1**

The separator therefore helps the rhythm score, but the absolute transcription accuracy remains far below professional-tab quality.

## GitHub Actions evidence

Run: `37094392537` - **success**
Head: `b36c99a51fca367d288862dda351515457e6d3af`

Artifact:
- id: `11262994060`
- digest: `sha256:ae73d963ef985beaf26cf9e7c1cbd1780e0bb1e4757e40f6ae3c85c3662045b0`

The artifact preserves the frozen Basic Pitch prediction streams for:
- whole mix
- raw guitar stem
- raw bass stem

Those cached predictions are reusable for scoring-only follow-ups without rerunning separator/transcriber inference.

## Boundary

This result does not score string/fret, technique, duration, or articulation emitted by the current Basic Pitch front end because Basic Pitch does not provide those tab-specific dimensions. It is an exact-pitch/onset benchmark.
