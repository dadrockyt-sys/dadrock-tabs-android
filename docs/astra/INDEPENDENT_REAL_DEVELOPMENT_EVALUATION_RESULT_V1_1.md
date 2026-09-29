# Independent Real-Development Evaluation V1.1 Result

Date: 2026-09-28  
Status: **COMPLETED — SINGLE BOUNDED RUN, NO TUNING**

## Frozen candidate

- Candidate: **S9 30-voicing intervention**
- checkpoint SHA-256: `8428e7ced49331153e5bd3a038115235c06aac483dab6f82fbc0257d07dd5036`
- historical checkpoint schema: `astra-synthetic-data-diversity-s9-pilot-v1`
- historical training steps: 500
- state threshold: **0.50**
- onset threshold: **0.50**
- decoder: frozen event-decoder V2 same-fret rising-edge rule
- threshold search: **none**
- threshold retuning: **none**
- candidate reselection: **none**

## Primary V1.1 results

| Metric | Result |
|---|---:|
| Trusted high+medium pitch landmarks hit | **1 / 72** |
| Trusted high+medium landmark hit rate | **1.389%** |
| High-confidence pitch landmarks hit | **1 / 68** |
| High-confidence landmark hit rate | **1.471%** |
| Negative-only false-positive events | **1** |
| Negative-only duration | **41.367 s** |
| Negative-only FP rate | **0.0242 events/s** |

Sensitivity including the 12 low-confidence landmarks:
- **1 / 84 = 1.190%**

## Per-clip behavior

The candidate admitted only four guitar events across all 18 positive clips:
- P01: 3 decoded events, 1 trusted landmark hit;
- every other positive clip: 0 decoded events.

All six onset-only/polyphonic clips produced 0 admitted events.

Negative-only clips:
- N01: 0
- N02: 1
- N03: 0
- N04: 0
- N05: 0
- N06: 0

The N02 false positive was:
- string 0 / fret 9 / MIDI pitch 49;
- start 4.0867 s;
- end 4.1332 s.

## Interpretation

The frozen S9 synthetic checkpoint shows **very low false-positive activity** on this small independent negative set, but it also **almost completely fails to admit real guitar events** under the frozen 0.50/0.50 thresholds.

Under the V1.1 contract, the direct supported conclusion is:

> The pinned synthetic S9 candidate does not transfer adequately to this independently sourced real-development audio under its frozen decoder and thresholds.

This is a transfer result, not an architecture-causality result. It does not prove that S9's chord-voicing intervention caused the failure, nor does it isolate frontend mismatch, domain shift, model calibration, representation limits, or historical-runtime differences.

## Runtime qualification

The original historical lock specified:
- Python 3.10.15 workflow;
- torch 1.11.0+cpu;
- librosa 0.9.1;
- numpy 1.21.6.

The local evaluation runtime available for the uploaded audio was:
- Python 3.13.5;
- torch 2.10.0+cpu;
- librosa 0.11.0;
- numpy 2.3.5.

The evaluation preserved:
- exact checkpoint bytes;
- exact model architecture;
- frozen frontend mathematics;
- frozen decoder semantics;
- frozen thresholds;
- frozen crops;
- frozen landmark references.

Because package versions differ, this run is **not claimed to be bit-for-bit historical-runtime reproduction**. The direction and magnitude of the observed admission collapse are still strong diagnostic evidence, but a future exact-lock rerun would be needed to exclude runtime-version effects completely.

## No tuning after result

No:
- threshold lowering;
- decoder adjustment;
- gain experiment;
- candidate replacement;
- retraining/fine-tuning;
- A2;
- P1/P2/P3 access;
- repeated run selected by outcome.

was performed after seeing the result.

## Decision boundary

The current evidence says the project should **not treat the synthetic S9 checkpoint as a product-relevant transcription model**.

The smallest scientifically useful next research question is now a real-domain transfer/calibration diagnosis performed without using this same V1.1 set as a tuning target unless a new prospectively frozen development/training split is created.

Do not automatically start that program from this result.
