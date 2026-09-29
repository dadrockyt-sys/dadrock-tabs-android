# V10 exposure-isolation preflight result V1

Date: 2026-09-29 UTC  
Status: **MODEL-FREE PREFLIGHT PASS — EMPIRICAL EXECUTION NOT AUTHORIZED**

The new V10 project was prospectively defined after the explicit user authorization to open a new project question.

Frozen study question:

> Does exact matching of sampled attacked-note-label exposure, while holding the frozen V9 dataset/model/loss/thresholds/update count/non-positive strata/per-step shuffle fixed, materially restore synthetic pitch-onset precision/F1?

Model-free preflight completed successfully:

- run **36527632335**
- job **109274053805**
- head `b55f2bebf1df366f08c5262815afe5dbbe82ca95`
- artifact **11014419820**
- digest `sha256:b62962f0715471d0a49e7402fa0cd6baa1383029db7d23db5ff26164c25a2dbd`
- conclusion **success**
- artifact retention through **2026-10-29**

Validated exposure arithmetic:
- 16,000 positive-onset frame slots/model
- control expected attacked-note labels: **17,676**
- intervention target attacked-note labels: **19,702**
- intervention multi-label positive frames: **1,851**
- intervention single-label positive frames: **14,149**
- 351 updates with 4 multi-label positive frames
- 149 updates with 3 multi-label positive frames

The intervention is designed to change only positive-onset frame selection. Non-positive stratum selections and the per-step batch shuffle remain identical between arms.

Preflight execution counts:
- waveform renders: **0**
- models trained: **0**
- optimizer steps: **0**
- model inference: **0**
- V2B inference: **0**

The empirical contract remains frozen and explicitly says empirical V10 execution is not authorized yet. A fresh authorization after the user can see this contract is required before rendering or training.
