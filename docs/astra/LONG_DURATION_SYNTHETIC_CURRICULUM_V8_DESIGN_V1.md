# V8 Longer-Duration Synthetic Curriculum Design V1

Date: 2026-09-29  
Status: **FROZEN BEFORE V8 OUTPUT**

## Authorization

The user explicitly authorized the next project after the V7A no-advance boundary.

## Question

V7 showed that the frozen 2-second clip structure cannot represent the V2B-like long IOI tail while preserving event counts/content.

V8 asks:

> Does a longer deterministic synthetic clip curriculum produce a materially better real-like timing distribution, and if so does training on it improve V2B onset transfer under otherwise fixed conditions?

## Invariants

Keep fixed:
- S9/S6 nonlinear model architecture and parameter count;
- R3 renderer;
- exact string/fret state objective;
- O0 exact-frame BCE onset loss;
- optimizer, learning rate, sampler logic, batch size;
- 500 optimizer steps/model;
- pitch/fret/chord family generators;
- negative-only semantics;
- CQT frontend and RMS normalization;
- thresholds 0.50/0.50;
- production decoder;
- no V1.1 use.

V8 changes only clip/curriculum structure and event placement.

## Frozen curriculum arms

### L0 — 2-second historical baseline

Historical R3 synthetic corpus/timing.

### L1 — 4-second two-motif curriculum

For every positive base template:
- total clip duration = **4.0 s**;
- place two deterministic motif instances using the same family/content generator;
- first motif begins in the first second;
- second motif begins after a deterministic inter-motif gap sampled uniformly from **0.70–1.10 s** after the first motif's last attack;
- within each motif, preserve historical event-relative timing except repeated-attack family uses fixed **0.18 s** adjacent spacing;
- motif 2 uses the next deterministic base-content draw from the same family distribution;
- total event count approximately doubles with duration.

Negative-only clips remain negative-only and scale to 4.0 s.

### L2 — 6-second three-motif curriculum

For every positive base template:
- total clip duration = **6.0 s**;
- place three deterministic motif instances;
- inter-motif gaps independently/deterministically sampled from **0.70–1.10 s**;
- repeated-attack family uses fixed **0.18 s** adjacent spacing;
- each motif draws from the same frozen family/content generator;
- total event count approximately triples with duration.

Negative-only clips remain negative-only and scale to 6.0 s.

No V2B clip timing sequence is copied.

## V8A — model-free timing screen

Generate timing manifests only; no waveform rendering, model training, or inference.

Compare L0/L1/L2 to the frozen V2B targets:
- aggregate onset density 1.4905949321/s
- IOI p50 0.2560 s
- IOI p90 0.882358 s
- repeated-attack fraction <=250 ms 0.4701986755

Use the same V7 timingDistance formula.

### Advancement rule

A longer arm advances only if all are true versus L0:
- timingDistance improves by >= **35% relative**;
- repeated-attack absolute error improves by >= **0.10**;
- IOI p90 absolute error improves by >= **0.25 s**;
- aggregate onsets/sec remains within **±15%** of V2B;
- clip-boundary fallback rate <= **2% of positive clips**;
- no invalid/overlapping label state on the same string.

Advance at most **one** arm, lowest timingDistance.

If none qualifies, V8 stops with **0 optimizer steps**.

## V8B — paired corpus render and training

Only if V8A advances one arm.

Render:
- L0 R3 baseline;
- one advancing longer curriculum with R3.

Train exactly two models:
- same initialization;
- same architecture;
- same loss;
- paired sampler policy;
- 500 steps/model;
- max **1000 optimizer steps total**;
- zero retries.

Because clip/frame counts differ, exact batch indices cannot be identical. Instead freeze a **paired stratum schedule**: the same sequence of four stratum choices and the same within-stratum RNG seed stream per step.

## V8C — synthetic sanity

Advancing model must satisfy versus same-run L0:
- pitch-onset F1 decline <= **0.08 absolute**;
- onset recall decline <= **0.08 absolute**;
- onset precision >= **0.70**;
- negative-only FP <= **0.10 events/s**;
- all 500 steps finite.

Failure stops before V2B.

## V8D — V2B development transfer

At unchanged 0.50/0.50:
- onset-admission gain vs L0 >= **+0.15 absolute**;
- trusted joint gain >= **+0.10 absolute**;
- high-confidence joint admission >= **15%**;
- negative FP <= **0.10/s**;
- state admission decline <= **0.10 absolute**.

Any success still requires a fresh holdout.

## Compute ceiling

- maximum 2 models
- maximum 500 optimizer steps/model
- maximum 1000 optimizer steps total
- no retries
- no threshold/loss/curriculum parameter search.

## Boundaries

Do not:
- tune L1/L2 after V8A output;
- add real audio to training;
- use V1.1;
- change architecture/loss/renderer/thresholds/decoder;
- open P1/P2/P3 or A2;
- mutate main/Production.

