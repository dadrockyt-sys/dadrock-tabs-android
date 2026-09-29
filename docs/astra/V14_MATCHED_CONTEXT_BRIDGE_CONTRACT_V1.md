# V14 2-second matched-context bridge — frozen prospective contract V1

Date: 2026-09-29 UTC  
Status: **FROZEN PROSPECTIVE CONTRACT — EMPIRICAL EXECUTION NOT AUTHORIZED**

## Question

Can the successful V9 acoustic-attack timing principles retain material benefit when returned to a **2-second comparator-like temporal/context construction**?

This is a **package recovery experiment**, not a single-factor causal isolation.

## Why V14 changed direction

V9 lost **0.3034148162 F1** and **0.5024955960 precision** on the common 2-second comparator population. V10-V13 recovered only about 1–8% of the F1 deficit individually. Source review also showed that the 4-second V9 construction materially changed boundary and inactive-context geometry; notably the negative-structure burst remains near 1.70 s, leaving ~2.30 s after it in V9 versus ~0.30 s in the 2-second comparator.

Therefore V14 tests a coherent 2-second recovery bridge rather than another marginal sampler-mixture restoration.

## Frozen control

Same-runtime historical 2-second comparator:
- 294 family/base/variant identities;
- 273 positive / 21 negative-only;
- 2.0 s each;
- historical S0 family/state semantics including non-attacked legato continuation;
- R3 renderer;
- frozen RMS normalization + CQT;
- same split by base identity.

## Frozen bridge timing identity

Positive attack groups per clip:
- isolated **1**
- scales **4**
- chords **2**
- repeated **5**
- legato **1**
- palmmute **6**
- mixed-positive **1**

Totals:
- positive seconds **546**
- attack groups **819**
- density **1.500000/s**
- positive within-clip gaps **546**

First-attack supports:
- isolated 0.30–0.34 s
- scales 0.20–0.24 s
- chords 0.30–0.34 s
- repeated 0.26–0.30 s
- legato 0.26–0.30 s
- palmmute 0.24–0.26 s
- mixed-positive 0.34–0.38 s

Gap supports:
- S **0.100–0.130 s**
- M **0.251–0.260 s**
- L **0.850–0.950 s**

Exact gap-class totals:
- S **252**
- M **225**
- L **69**
- total **546**

Exact family totals:
- scales: 58 S / 52 M / 16 L
- chords: 19 S / 18 M / 5 L
- repeated: 78 S / 68 M / 22 L
- palmmute: 97 S / 87 M / 26 L

Clip-type quotas:
- scales: 16 × [S,M,L], 16 × [S,S,M], 10 × [S,M,M]
- chords: 5 × [L], 19 × [S], 18 × [M]
- repeated: 22 × [S,S,M,L], 14 × [S,S,M,M], 6 × [S,M,M,M]
- palmmute: 26 × [S,S,S,M,L], 13 × [S,M,M,M,M], 3 × [S,S,M,M,M]

Root seed: **20260929**.

Assignment is deterministic by SHA-256 over exact positive clip identities (family/baseIndex/variant). There is no candidate sweep, search, retry, or best-of-N selection.

Final required margin after the last attack: **0.120 s**.

## Model-free frozen schedule measurements

The single frozen deterministic schedule gives:
- attack groups **819**
- gap count **546**
- density **1.500000/s**
- IOI p10 **0.1061617322 s**
- IOI p50 **0.2520127045 s**
- IOI p90 **0.8704418108 s**
- repeat250 **0.4615384615**
- longGap700 **0.1263736264**
- latest attack **1.7920413320 s**
- minimum post-last-attack margin **0.2079586680 s**
- corrected timing-distance V1 **0.0430642112**

These are model-free deterministic schedule values, not empirical model results.

## State/context semantics

The bridge returns to comparator-like state semantics:
- preserve historical family-specific state-duration intent;
- preserve the non-attacked legato continuation;
- if a same-string retrigger occurs before the historical state would end, truncate deterministically at the retrigger under one frozen rule;
- count and report every such truncation;
- no clipping/repair/search is permitted after schedule generation.

The 2-second bridge intentionally removes the 4-second V9 tail geometry. This is why V14 must be interpreted as a package recovery study rather than causal isolation.

## Frozen model/training settings for a later authorized empirical run

Both arms:
- S6 nonlinear five-frame model;
- state active weight 9.0;
- onset BCE positive weight 8.0;
- onset loss multiplier 4.0;
- Adam 0.003;
- batch size 128;
- four strata × 32 frames/update;
- state/onset thresholds 0.50 / 0.50;
- exactly 500 updates/model;
- exactly 2 models;
- maximum 1,000 total optimizer updates;
- no threshold search;
- no scientific retry.

Primary evaluation:
- exact frozen common 2-second comparator test.

No V2B or real-audio inference exists in V14.

## Frozen material-recovery gate

The bridge is supported only if all pass:
- common F1 **>= 0.5864900168** (at least 50% recovery of the V9 F1 deficit);
- common precision **>= 0.5756752789** (at least 50% recovery of the V9 precision deficit);
- recall decline versus successful comparator **<= 0.05**;
- negative-only false positives **<= 0.10/s**;
- exact 500 updates/model;
- exact 2 models;
- finite metrics;
- thresholds remain 0.50/0.50;
- no threshold search;
- no automatic scientific retry.

Do not weaken these gates after seeing a result.

## Preflight boundary

The current authorization permits:
- contract/spec creation;
- model-free schedule derivation;
- pure validator/tests;
- model-free preflight.

It does **not** permit:
- waveform rendering;
- dataset generation;
- optimizer steps;
- model inference;
- V2B;
- P1/P2/P3;
- main/Production mutation.

After the preflight is visible, fresh explicit authorization is required before empirical V14 execution.
