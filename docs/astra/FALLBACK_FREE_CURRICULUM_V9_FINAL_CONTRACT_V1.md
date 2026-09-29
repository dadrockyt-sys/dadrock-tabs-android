# V9 fallback-free curriculum — final empirical contract V1

Date: 2026-09-29 UTC  
Status: **FROZEN CONTRACT — EMPIRICAL EXECUTION NOT AUTHORIZED**

This document freezes one bounded V9 package before any V9 candidate timing output is generated. It uses the common-unit reference frozen in `PRE_V9_COMMON_UNIT_MEASUREMENT_V1`. It does not authorize generation, rendering, training, inference, or workflow dispatch.

## Question

Does one prospectively fixed **4.0-second fallback-free native timing package**, evaluated in acoustic-attack-group units while preserving note/string/fret labels separately, improve the corrected timing fit enough to justify one bounded paired synthetic training comparison?

This is a package comparison. It does not isolate duration from attack-count allocation, gap mixture, or sustain construction.

## Frozen reference

Common-unit V2B reference:
- attack-group density: **1.4905949321256224/s**
- IOI p50: **0.256 s**
- IOI p90: **0.882358 s**
- repeat250: **0.47019867549668876**
- longGap700: **0.12582781456953643**
- positive duration: **110.02318367346939 s**
- negative duration: **31.85795918367347 s**

Same-unit retained V8 L0 comparator:
- 273 positive clips / 546 s
- 735 attack groups
- density **1.3461538461538463/s**
- IOI p50 **0.360 s**
- IOI p90 **0.400 s**
- repeat250 **0**
- longGap700 **0.09090909090909091**

Historical V6/V7/V8 metrics remain archival and are not retroactively changed.

## One intervention arm only

Clip duration: **4.0 s**.

Keep the historical 294 clip slots and split-by-base identity:
- 210 train
- 42 validation
- 42 test
- 273 positive
- 21 negative-only

Base identity remains 14 bases x 3 variants x 7 families. Base indices 0-9 train, 10-11 validation, 12-13 test. No base/template identity crosses splits.

### Positive acoustic attack-group counts per clip

These counts are frozen before generation:

| Family | Positive clips | Attack groups / positive clip | Total attack groups |
|---|---:|---:|---:|
| isolated | 42 | 5 | 210 |
| scales | 42 | 8 | 336 |
| chords | 42 | 2 | 84 |
| repeated | 42 | 8 | 336 |
| legato | 42 | 4 | 168 |
| palmmute | 42 | 10 | 420 |
| mixed-positive | 21 | 4 | 84 |
| **total** | **273** | — | **1,638** |

This gives a frozen intervention attack-group density of **1.500000000/s** over 1,092 positive seconds, within 0.64% of the V2B reference.

Chord multiplicity remains three note labels per acoustic chord attack. Other attack groups carry one note label unless the frozen family template explicitly requires a non-attacked legato continuation. With two chord attack groups per chord clip, total attacked note-label count is frozen at **1,806**, exactly preserving the historical V8 L0 attacked-note-label density of **1.6538461538461537/s** when duration doubles.

Negative-only mixed clips remain zero attack groups and zero note labels.

## Frozen gap-class allocation

Gap classes are fixed by family before any random gap value is drawn. Class order inside a clip is a deterministic SHA-256 permutation keyed by:

`20260927|v9-gap-order|split|family|base|variant`

Class multisets:

- isolated, 4 gaps: **S,S,S,M**
- scales, 7 gaps: **S,S,S,M,M,M,L**
- chords, 1 gap: **M**
- repeated, 7 gaps: **S,S,S,M,M,M,L**
- legato, 3 gaps: **S,M,L**
- palmmute, 9 gaps: **S,S,S,S,M,M,M,M,L**
- mixed-positive, 3 gaps: **S,S,L**

Aggregate over the 273 positive clips:
- short S: **630 / 1,365 = 0.46153846153846156**
- medium M: **546 / 1,365 = 0.40000000000000000**
- long L: **189 / 1,365 = 0.13846153846153847**

Frozen gap supports:
- S: **[0.080, 0.250] s**
- M: **[0.251, 0.316] s**
- L: **[0.700, 1.360] s**

These disjoint supports prevent zero/simultaneous note multiplicity from entering IOIs and make `repeat250` correspond exactly to S-class gaps.

Algebraic mixture targets before candidate generation:
- repeat250 = **0.4615384615**
- linear-mixture p50 ≈ **0.25725 s**
- linear-mixture p90 ≈ **0.88333 s**
- longGap700 = **0.1384615385**

These are design expectations, not empirical V9 results.

## First attack, sustain, and feasibility

First attack:
- support **[0.050, 0.120] s**
- deterministic SHA-256 uniform keyed by `20260927|v9-first|split|family|base|variant`

Each gap value:
- deterministic SHA-256 uniform keyed by `20260927|v9-gap-value|split|family|base|variant|gap_index`
- mapped once into its frozen class support
- no retries, reseeding, clipping, compression, event deletion, or post-placement shift

Final required margin:
- **0.120 s**

Synthetic attacked-note sustain support:
- **[0.120, 0.480] s**
- deterministic SHA-256 uniform keyed by `20260927|v9-sustain|split|family|base|variant|attack_index|note_index`

For each note, the valid upper sustain is `min(0.480, 4.0 - onset)`. If that upper bound is below 0.120, the clip is infeasible and the timing gate fails closed.

The declared maximum support fits the highest-count palmmute schedule without correction:

`0.120 first + 4*0.250 + 4*0.316 + 1*1.360 + 0.120 final = 3.864 s < 4.0 s`.

Therefore the design has no planned fallback path. Any implementation that introduces fallback is nonconforming.

## Note-label construction

Use the existing deterministic S0/S9 family pitch/string/fret construction rules as the content source, while placing attacks at V9 times.

For chords:
- preserve exactly three strings per acoustic chord attack;
- preserve valid string/fret ranges;
- all three chord notes share the same acoustic attack-group onset.

For repeated/palmmute/isolated/scales/mixed:
- preserve deterministic family string/fret semantics.

For legato:
- attacked acoustic groups are measured as attack groups;
- any non-attacked continuation remains a state-label event and is not counted as a new acoustic attack group.

No train/test base identity leakage is permitted.

## Corrected timing-distance V1

Freeze:

`D = |repeat250-r*| + |p50-p50*|/p50* + |p90-p90*|/p90* + 0.5*|density-d*|/d* + 0.5*|long700-l*|/l*`

where starred values are the frozen common-unit V2B reference.

The frozen same-unit V8 L0 comparator distance is **1.6103247396**.

## V9A pre-render gate

The single V9 timing manifest advances only if **all** conditions pass:

1. corrected timing-distance relative improvement vs V8 L0 **>= 0.60**;
2. attack-group density relative error vs V2B **<= 0.05**;
3. IOI p50 absolute error vs V2B **<= 0.050 s**;
4. IOI p90 absolute error vs V2B **<= 0.150 s**;
5. repeat250 absolute error vs V2B **<= 0.080**;
6. longGap700 absolute error vs V2B **<= 0.050**;
7. positive clip count exactly **273**;
8. negative-only clip count exactly **21**;
9. intervention attack-group count exactly **1,638**;
10. attacked note-label count exactly **1,806**;
11. zero infeasible clips;
12. zero onset/out-of-range labels;
13. zero invalid string/fret/pitch labels;
14. zero invalid offsets/sustains;
15. zero fallback/correction operations;
16. exact split/base identity and no base/template crossing train/validation/test;
17. all metrics finite;
18. source/spec/reference identities match the frozen pins.

If any condition fails: **stop with 0 waveform renders, 0 optimizer steps, and 0 model inference.**

No second timing arm, parameter search, alternative mixture, or post-hoc gate change is permitted.

## Rendering contract if V9A passes and empirical V9 has been authorized

Exactly two synthetic datasets:
- comparator: retained 2.0-second historical content baseline, regenerated in the same runtime;
- intervention: frozen 4.0-second V9 package.

Renderer:
- R3 transform fixed;
- S0 deterministic plucked-string content source fixed except for V9 timing/count placement;
- frozen RMS normalization and CQT frontend;
- no external audio assets;
- no real sound files in training.

Ceilings:
- datasets: exactly **2**
- examples/dataset: exactly **294**
- comparator logical audio: **588 s**
- intervention logical audio: **1,176 s**
- render wall-clock ceiling: **30 CPU minutes total**
- persisted synthetic dataset storage ceiling: **700 MiB total**
- paid compute: **$0**

Fail if output paths already exist.

## Training contract if render/data verification passes

Model package:
- S6 nonlinear shared encoder/state-head package
- shared encoder `Linear(960,128) -> ReLU`
- state head `Linear(128,128) -> ReLU -> Linear(128,126)`
- onset head `Linear(128,6)`
- active-state weight **9.0**
- onset BCE positive weight **8.0**
- onset loss multiplier **4.0**
- Adam learning rate **0.003**
- batch size **128**
- thresholds state/onset **0.50 / 0.50**
- production decoder unchanged
- O0 exact-frame BCE onset objective
- exact-string/fret state objective

Models:
- exactly **2**
- exactly **500 optimizer updates/model**
- maximum **1,000 total updates**
- zero automatic scientific retries

Initialization:
- initialize comparator and intervention from the same deterministic state;
- verify module hash and pre-update logits before optimizer step 1.

Sampling:
- preserve the same declared four sampler strata;
- pair by stratum and update index;
- because sequence lengths differ, report actual sampled frames, attacked-note labels, attack groups, positive seconds represented, and fit time for each arm;
- do not claim equal compute/exposure from equal update count.

Fit/evaluation wall-clock ceiling:
- **60 CPU minutes total**

## Synthetic sanity gate

Use one fixed same-runtime synthetic evaluation population not used for training. It must be frozen before optimizer step 1.

Intervention advances to V2B development evaluation only if all pass:
- onset precision **>= 0.70**
- pitch-onset F1 decline vs comparator **<= 0.08**
- onset recall decline vs comparator **<= 0.08**
- negative-only false positives **<= 0.10 events/s**
- exact 500 updates/model
- finite losses/metrics
- fixed 0.50/0.50 thresholds
- no decoder change
- all source/dataset/model identities verified

Failure technically blocks V2B inference.

## V2B development gate

Use exactly the frozen C01-C13 positive and D01-D04 negative-only development set. No V1.1, P1, P2, or P3.

Scoring population:
- 56 trusted scorable pitch landmarks
- 49 high-confidence scorable pitch landmarks
- the excluded unrepresentable C06/0.042667/MIDI37 landmark remains excluded
- negative duration **31.857959184 s**
- thresholds **0.50 / 0.50**
- ordinary production decoder for negative FP counting

The intervention is development-interesting only if all pass:
- onset admission absolute gain vs same-runtime comparator **>= +0.15**
- trusted joint admission absolute gain vs comparator **>= +0.10**
- high-confidence joint admission **>= 0.15**
- negative false-positive rate **<= 0.10 events/s**
- state admission decline vs comparator **<= 0.10**
- exact per-clip results retained
- all metrics finite

Passing is development evidence only, not product readiness.

## Fresh confirmation boundary

No fresh holdout is acquired or evaluated automatically.

If V9 passes the V2B development gate:
- freeze model/settings;
- stop;
- any new real confirmation set requires a separately reviewed source/creator-grouped acquisition, annotation, and authorization plan.

V1.1 remains exposed and closed to further confirmation use.

## Frozen source/reference pins at contract time

- `astra_backend/synthetic/s0_pilot_v1.py` blob: `c05b6f986186dbe96245875833ab9564df99d4fb`
- `astra_backend/synthetic/s6_pilot_v1.py` blob: `142168784e3dfebf8a5221017e40c8aa73be1fa5`
- `astra_backend/synthetic/v4_rendering_adequacy_v1.py` blob: `badedb6c36ad389093b6f74b97f4452c44518501`
- `astra_backend/synthetic/v9_measurement_contract_v1.py` blob: `3ecd574e533d28871959a44fa5007ff2901fc1d1`
- `astra_backend/synthetic/pre_v9_common_unit_measurement_v1.py` blob: `98e777bce7ebf6d7990319f21cbdb0b6028bad12`
- `docs/astra/PRE_V9_COMMON_UNIT_MEASUREMENT_V1.json` blob: `9d68a5049209b0392fc7c7907ed6b0db76781b2b`
- V2B manifest blob: `c2912b1e2ba84ca28d67e1573dee6034210c0366`
- V2B duration-correction blob: `1262937be952a72fa94196959d1bc7fd2759eee9`
- V2B annotation blob: `e95ced7525ed48de18e41c60d0b8904f90087dd8`
- V2C result blob: `490ea778085d9141d953580db59614cbd22da378`

A future implementation source must be added and its blob pinned in a launch scope **before authorization is consumed or candidate output is generated**.

## Launch integrity contract

No launch is armed by this file.

A future empirical launch must:
- use one unique launch identity;
- bind exact branch head, final spec blob, implementation source blobs, workflow blob, and reference blobs;
- use a durable execution-history ledger;
- reject an already consumed launch identity;
- reject `GITHUB_RUN_ATTEMPT != 1`;
- reject wrong branch/ref;
- refuse existing result/model/dataset output paths;
- record infrastructure failure separately from scientific failure;
- permit no automatic scientific retry;
- enforce render/fit/inference deadlines;
- emit a partial-failure receipt if stopped after launch consumption;
- retain source/spec/manifests/dataset hashes/model checkpoints/raw result JSON in durable authorized storage;
- never put original real audio or credentials in Git.

## Current authorization boundary

This contract is frozen preparation only.

**Not authorized yet:**
- V9 candidate timing generation;
- workflow dispatch;
- waveform rendering;
- model training;
- model inference;
- V2B scoring;
- new sound collection/annotation;
- V1.1/P1/P2/P3/A2;
- main or Production mutation.

The next empirical action requires an explicit user decision authorizing V9 execution under this exact frozen contract.
