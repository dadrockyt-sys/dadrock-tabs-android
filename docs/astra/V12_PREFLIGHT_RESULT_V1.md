# V12 positive-onset family-mixture preflight result V1

Date: 2026-09-29 UTC  
Status: **MODEL-FREE PREFLIGHT PASS — EMPIRICAL EXECUTION NOT AUTHORIZED**

The V12 family-mixture project has been prospectively frozen and its model-free preflight passed.

Frozen question:

> With the exact executed V9 dataset semantics and all non-positive batch selections fixed, does matching the historical comparator positive-onset family mixture materially recover common-population precision/F1?

## Preflight identity

- run **36537123050**
- job **109303603997**
- head `250b08ddd7aca913ea0382122a259ca6e7a50f2a`
- artifact **11018394264**
- digest `sha256:b50fe403922d929fb2864b77868f83f57af23b20b240fbfe42f6e8aa8224959e`
- conclusion **success**
- artifact retained through **2026-10-29**

All V12 contract/static tests passed.

## Frozen family allocation

Across exactly 16,000 positive-onset training slots:

- isolated **914**
- scales **3,657**
- chords **1,829**
- repeated **3,657**
- legato **914**
- palmmute **4,572**
- mixed-positive **457**

Total: **16,000**

The intervention changes only positive-onset selections. Non-positive selections and the per-step batch permutation remain identical to control.

Because chord onset frames carry three attacked note labels, attacked-note-label exposure will change as a downstream consequence and must be reported explicitly.

## Data-regeneration qualification

The original V9 artifact did not retain the dataset arrays. A future empirical V12 run must therefore deterministically regenerate the common 2-second comparator and one executed-V9 4-second dataset with the frozen V9 source/runtime.

This does not create separate audio arms: both V12 models train on the same regenerated V9 arrays. The scientific intervention remains positive-onset family selection only.

## Current execution counts

- waveform renders: **0**
- models trained: **0**
- optimizer steps: **0**
- model inference: **0**
- V2B inference: **0**

Empirical V12 execution remains blocked until a fresh explicit authorization is given after this frozen contract/preflight.
