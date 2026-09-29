# V2B Fresh Calibration-Development Set Design

Date: 2026-09-28  
Status: **DESIGN FROZEN — COLLECTION NOT YET AUTHORIZED**

## Purpose

Create a fresh real-domain calibration-development set that is completely separate from the sealed V1.1 evaluation set.

This set exists only to diagnose calibration/domain-transfer behavior and, if later explicitly authorized, support bounded threshold calibration experiments.

## Independence rules

V2B must not include:
- any of the 24 V1.1 clips;
- any crop, duplicate, remix, alternate encoding, or near-duplicate of those clips;
- P1, P2, or P3;
- prior synthetic renders;
- any audio already inspected with candidate-model output;
- any audio selected after seeing candidate-model behavior.

## Minimum collection

At least:
- 16 clips total;
- 12 positive guitar clips;
- 4 negative-only clips;
- 60 seconds positive audio;
- 20 seconds negative audio.

## Required positive coverage

Across the 12 positive clips:
- at least 2 creators or capture chains;
- at least 2 clean clips;
- at least 2 distorted/overdriven clips;
- at least 4 primarily single-note clips;
- at least 3 repeated-attack clips;
- at least 2 legato/bend/slide clips;
- at least 2 chordal/polyphonic clips.

Clip duration:
- 4–10 seconds each.

## Negative coverage

At least four non-guitar clips from at least three categories among:
- speech;
- typing/mechanical transients;
- percussion;
- crowd/applause;
- environmental noise.

Negative clips must contain no target guitar.

## Labels

Before any candidate-model output on V2B:
- freeze clip SHA-256;
- freeze crop boundaries;
- freeze pitch/onset reference landmarks for monophonic/single-note material;
- mark polyphonic clips as onset/activity-only unless exhaustive human pitch transcription is available;
- mark annotation confidence high/medium/low;
- do not assert string/fret unless unambiguous.

## Candidate and runtime

Use the already pinned S9 30-voicing intervention checkpoint only.

No candidate selection is permitted after V2B results.

The historical runtime mismatch remains a known limitation. V2B may use the same local runtime as V1.1 for comparative diagnosis, but must not be represented as exact historical reproduction.

## Phase boundary

This V2B design does **not** authorize:
- web scraping/downloading;
- model inference;
- threshold search;
- threshold changes;
- calibration fitting;
- retraining/fine-tuning;
- decoder/frontend/gain tuning.

A separate explicit authorization is required before actual V2B data collection begins.

## Required intake package

Before model inference on V2B, freeze:
- `docs/astra/V2B_CALIBRATION_DEVELOPMENT_INTAKE.json`
- clip hashes/durations/source metadata;
- overlap declaration against V1.1/P1/P2/P3;
- annotations and confidence;
- candidate/runtime pins;
- pure intake validator result;
- zero-inference verification receipt.

## Stop rule

If independence cannot be established, stop. Do not replace questionable clips after viewing model output.
