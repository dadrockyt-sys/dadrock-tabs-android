# Next chat: start here

Repository: `dadrockyt-sys/dadrock-tabs-android`, branch `astra-work`.
Updated: 2026-09-27.

## Current verified position

Basic Pitch Stage-A run **36337236022**, job **108670300164** was workflow GREEN but **scientifically FAILED** the frozen gate.

Frozen result:
- `docs/astra/PRETRAINED_NOTE_FRONT_END_FEASIBILITY_RESULT_V1.json`
- artifact **10938223666**
- aggregate pitch+onset precision / recall / F1: **0.342 / 0.871 / 0.491**
- P1 F1 **0.426**
- P2 F1 **0.571**
- scales pair macro F1 **0.741**
- chords **0.333**
- single notes **0.417**
- PalmMute **0.367**
- 27 TP / 52 FP / 4 FN
- optimizer 0, no threshold search, P3 sealed

Interpretation: pretrained note recall is strong, but precision is too poor at the frozen defaults. Do not tune Basic Pitch thresholds on these eight development crops.

## Exact next task

Offline design review only.

Compare exactly one alternative frozen/pretrained front-end path against one synthetic-pretraining/data-diversity path on feasibility, licensing/runtime, expected precision behavior and cost. Then select **one** materially different next hypothesis and freeze its design before any new real-media access or fitting.

Do not run both automatically. Do not start Stage-B string/fret fitting. P3 remains sealed.
