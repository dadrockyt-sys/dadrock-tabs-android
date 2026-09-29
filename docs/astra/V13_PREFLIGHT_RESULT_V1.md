# V13 active-non-onset family-mixture preflight result V1

Date: 2026-09-29 UTC  
Status: **MODEL-FREE PREFLIGHT PASS — EMPIRICAL EXECUTION NOT AUTHORIZED**

The V13 active-non-onset family-mixture study has been prospectively frozen and its model-free preflight passed.

Frozen question:

> With the exact executed V9 dataset and exact V9 batch plan fixed everywhere else, does matching only the historical comparator active-non-onset family mixture materially recover common-population precision/F1 without increasing negative-only false positives?

## Preflight identity

- run **36539873506**
- job **109312472318**
- head `98eaaeb87737582f59fde5755da88cb647af8c27`
- artifact **11019923191**
- digest `sha256:7d46e108c9fcfba1dbc3e1cfd767f62ffe8e3888cdfe3c98ef4da46044d6b96a`
- conclusion **success**
- artifact retained through **2026-10-29**

All V13 contract/static tests passed.

## Frozen active-non-onset allocation

Across exactly **16,000 active-non-onset slots**:

- isolated **2,511**
- scales **2,569**
- chords **2,219**
- repeated **2,861**
- legato **3,037**
- palm-mute **1,752**
- mixed-positive **1,051**

Only active-non-onset selection changes in the intervention.

The following remain identical to control:
- positive-onset selections;
- negative-structure-inactive selections;
- other-inactive selections;
- per-step batch permutation;
- attacked-note-label exposure;
- dataset arrays;
- model, initialization, loss, thresholds, optimizer and update count.

## Baseline reproduction gate

A future empirical V13 run must first reproduce frozen V9 common comparator-test metrics exactly within 1e-12:

- precision **0.3244274809160305**
- recall **0.6589147286821705**
- F1 **0.43478260869565216**

Failure invalidates the study.

## Frozen support gate

Support requires all:
- common precision gain >= **+0.15**
- common F1 gain >= **+0.10**
- common recall decline <= **0.05**
- common negative-only FP <= **0.10/s**
- frozen-V9 test F1 decline <= **0.05**
- identical sampled attacked-note-label exposure
- exact family-slot totals
- exactly 500 updates/model
- exactly 2 models
- no threshold search or scientific retry

There is no V2B stage.

## Current execution counts

- waveform renders **0**
- models trained **0**
- optimizer steps **0**
- model inference **0**
- V2B inference **0**

The authorization that opened V13 was used only for prospective definition and model-free preflight. A fresh explicit authorization after this frozen contract/preflight is required before deterministic dataset regeneration or training.
