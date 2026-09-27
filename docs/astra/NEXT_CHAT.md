# Next chat: start here

Repository: `dadrockyt-sys/dadrock-tabs-android`, branch `astra-work`.
Updated: 2026-09-27.

## Current verified position

The fixed temporal-triplet hypothesis failed its frozen advancement gate and is stopped.

The offline design review selected a materially different next path:
- `docs/astra/PRETRAINED_NOTE_FRONT_END_FEASIBILITY_DESIGN_V1.json`
- `docs/astra/PRETRAINED_NOTE_FRONT_END_FEASIBILITY_AUTHORIZATION_REQUEST_V1.json`

Preferred Stage A: zero-optimizer frozen **Basic Pitch** note-front-end feasibility on the same eight P1/P2 direct-input crops, scoring pitch/onset only before any string/fret assignment.

Frozen defaults: onset 0.5, frame 0.3, minimum note length 127.7 ms. No threshold tuning.

## Exact next task

Implement the adapter/scorer and synthetic tests **offline only**:
- exact capture/crop/source identity guards
- standard-tuning string/fret -> MIDI-pitch mapping
- duplicate same-pitch ambiguity accounting
- frozen crop-boundary scoring
- zero-optimizer / no-threshold-search guards
- exact Basic Pitch release/model identity pinning

Then run synthetic verification. Do not access real P1/P2 media until synthetic is green and Stephen separately explicitly authorizes the real feasibility run.

P3 remains sealed.
