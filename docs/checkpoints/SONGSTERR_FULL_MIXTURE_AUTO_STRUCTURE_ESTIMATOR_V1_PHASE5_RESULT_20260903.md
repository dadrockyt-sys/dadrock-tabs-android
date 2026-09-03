# FULL_MIXTURE_AUTO_STRUCTURE_ESTIMATOR_V1 — PHASE 5 RESULT

Date: 2026-09-03 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **`PHASE5_REFERENCE_BLIND_WAVEFORM_ESTIMATOR_PASS / ROUTE_DISCONNECTED / NO_ACCURACY_CLAIM / NO_REFERENCE_SCORE`**

## Frozen methodology

Pre-implementation checkpoint:

`docs/checkpoints/SONGSTERR_FULL_MIXTURE_AUTO_STRUCTURE_ESTIMATOR_V1_PREIMPLEMENTATION_FREEZE_20260903.md`

Creation commit:

`5ee029dff31fdd52422f70cb6e4714d2339519b5`

The methodology, thresholds and A1–A12 synthetic cases were fixed before implementation.

## Implementation

- `204ecd14e0a5165b199fd5693673cd498e7532e2` — `analyzer/full_mixture_auto_structure_estimator_v1.py`;
- `c2dd059720f0be45cd0e06874e6ca6a06797eecc` — deterministic synthetic waveform verifier;
- `ac9158b26c3302a129ba0ba3ed1689bee4573f6f` — branch workflow integration and safety evidence enforcement.

The estimator operates from full-mixture waveform samples, not Basic Pitch/transcribed events or separated-carrier output. It performs deterministic onset novelty extraction, tempo periodicity scoring, conservative 3/4-vs-4/4 accent/downbeat inference, pickup phase estimation and straight/triplet subdivision evidence.

## Deterministic evidence

Workflow:

- run `33810847829`;
- job `100832069691`;
- tested head `ac9158b26c3302a129ba0ba3ed1689bee4573f6f`;
- conclusion **SUCCESS**.

Evidence bot commit:

`9e00d7b21ddca34d823169cddfb1c269604ca026`

Evidence file:

`debug/v143-contextual-prune/full-mixture-auto-structure-estimator-v1.json`

Evidence blob SHA:

`306891daa326a922bb3385f611d9310c63baca87`

A1–A12 all passed:

- A1 silence unresolved;
- A2 fewer than four clicks leaves tempo unresolved;
- A3 120 BPM quarter-note train resolved within frozen tolerance;
- A4 90 BPM quarter-note train resolved within frozen tolerance;
- A5 accented 4/4 resolved as 4/4;
- A6 accented 3/4 resolved as 3/4;
- A7 ambiguous unaccented train left meter unresolved;
- A8 one-beat pickup resolved within frozen tolerance;
- A9 straight subdivision evidence resolved `straight`;
- A10 triplet subdivision evidence resolved `triplet`;
- A11 no subdivision evidence left feel unresolved;
- A12 trusted full-mixture/reference-blind provenance and no forbidden authorization fields.

## What this establishes

For the first time in the DadRock research lineage, Auto structure mechanics can be derived from the **full-mixture waveform itself** rather than transcribed-note events or a separated guitar carrier.

This is the missing signal-side component required by the Phase 3/4 dual-context architecture.

It is still a synthetic mechanics result only. It is **not** evidence of accuracy on real songs.

## Safety evidence

The recorded evidence explicitly asserts:

- `referenceBlind=true`;
- `referenceScoreAuthorized=false`;
- `syntheticWaveformsOnly=true`;
- `externalAudioAssetsUsed=false`;
- `basicPitchEventsUsed=false`;
- `separatedCarrierUsed=false`;
- `guitarSetRead=false`;
- `splitMySongRead=false`;
- `goatRestrictedBytesRead=false`;
- `modalInvoked=false`;
- `gpuUsed=false`;
- `routeEstimatorConnected=false`;
- `productModified=false`;
- `productionModified=false`;
- `productionPromotionAuthorized=false`.

## Route/Product state

Phase 5 did **not** connect this estimator to `/api/analyze-audio-tab` or any PDF path. Phase 3 still receives `mixtureObservation: null` in current product routing.

The next scientifically clean step is a separately frozen CPU waveform-file adapter that can read an already normalized full-mixture WAV and call this estimator. That adapter must be validated synthetically before any analyzer/runtime wiring.
