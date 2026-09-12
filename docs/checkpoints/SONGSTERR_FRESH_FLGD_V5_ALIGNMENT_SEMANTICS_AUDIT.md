# Songsterr Fresh — FLGD V5 Alignment Semantics Audit

Status: **PREREGISTERED NON-SCORING AUDIT / BEFORE ANY FLGD CORRECTNESS RESULT**

Date: 2026-09-12 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Purpose

FLGD is described by its release card as containing audio and aligned MIDI, and the selected release contains one `syncpoints/<stem>-syncpoints.json` file per canonical performance. Stage B showed canonical MIDI uses a fixed 500,000 us/quarter tempo at PPQ 220, while syncpoint examples contain explicit audio-second coordinates and score-position coordinates. Before correctness scoring, the authoritative reference-onset mapping to audio seconds must be established rather than guessed.

This audit is non-scoring and does not modify V5 or the frozen 79-performance population.

## Authorized evidence

At exact FLGD revision `a38306c244b3ea81496ad58b4514622185e58211`, inspect only:
- repository text/support files (`README`, scripts, logs, metadata and other small non-media files);
- Git file paths and attributes;
- canonical syncpoint JSON structure/values;
- canonical MIDI structural ticks/measure-related metadata as needed to establish coordinate meaning;
- the cited public paper/demo/source documentation if needed.

The audit may search for code that creates or consumes `syncpoints` and may report formulas/coordinate conventions explicitly present in release/source material.

## Forbidden

Do not:
- run Basic Pitch, V5, Demucs or source separation;
- decode audio for pitch/onset analysis;
- compare model estimates to reference notes;
- compute precision/recall/correctness;
- select/exclude performances based on outcomes;
- use `test_set/` model-output MIDI as reference truth;
- touch the protected song or duration authority.

## Required outcome

Before any final scoring preregistration, produce one explicit alignment decision:
1. raw canonical MIDI seconds are already authoritative audio seconds; or
2. canonical MIDI ticks must be transformed by syncpoints, with the exact deterministic transform frozen; or
3. evidence is insufficient, in which case scoring remains blocked pending a further non-scoring alignment study.

Any transform must be derived from documented/release structural semantics, not from optimizing transcription correctness.

Authority remains `modelValidationComplete:false`, customer-eligible events `0`, `mayAdvanceDelivery:false`, duration unchanged.
