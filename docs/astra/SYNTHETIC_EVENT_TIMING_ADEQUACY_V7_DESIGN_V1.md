# V7 Synthetic Event-Timing Adequacy Design V1

Date: 2026-09-29  
Status: **DESIGN FROZEN — EMPIRICAL EXECUTION NOT YET AUTHORIZED**

## Why V7 exists

V6 showed that onset-loss changes do not repair real transfer, while its model-free event audit found a clear timing-shape mismatch:

- synthetic repeated-attack fraction within 250 ms: **26.67%**
- V2B repeated-attack fraction within 250 ms: **47.02%**
- synthetic IOI p90: **0.418 s**
- V2B IOI p90: **0.882 s**

Aggregate onset density is similar, so V7 changes only temporal event structure rather than overall event count.

The V7 causal question is:

> Does a synthetic onset-time distribution with more short-gap repetition and a longer sparse-event tail improve real-domain onset transfer under otherwise fixed training?

## Frozen invariants

Across all V7 arms, keep fixed:
- S9/S6-style nonlinear model architecture and parameter count;
- frozen R3 waveform renderer;
- exact string/fret state objective;
- historical O0 exact-frame BCE onset loss;
- optimizer, learning rate, batch size, and 500-step budget;
- train/validation/test example counts;
- pitch/fret/chord-content template pools;
- negative-only template count and structure;
- RMS normalization and CQT frontend;
- state/onset thresholds **0.50 / 0.50**;
- production decoder;
- V2B annotations.

Only positive-event timing may differ.

## Frozen timing arms

### E0 — historical timing baseline

Current synthetic event-time generator unchanged.

### E1 — repeated-attack enriched

Keep total positive events per clip unchanged.

For eligible multi-event clips:
- deterministically assign **45%** of positive adjacent event pairs to an IOI uniformly sampled from **80–220 ms**;
- remaining positive pairs use the historical timing rule;
- preserve event ordering;
- reject/resample only if an event would exceed clip bounds.

No timing parameter search.

### E2 — sparse-tail enriched

Keep total positive events per clip unchanged.

For eligible multi-event clips:
- deterministically assign **20%** of positive adjacent event pairs to an IOI uniformly sampled from **700–1100 ms**;
- remaining pairs use the historical timing rule;
- preserve event ordering and clip bounds.

No timing parameter search.

### E3 — combined bimodal timing

Keep total positive events per clip unchanged.

For eligible multi-event clips:
- **45%** of positive adjacent pairs use the E1 short-gap range **80–220 ms**;
- **20%** use the E2 sparse-tail range **700–1100 ms**;
- the remaining **35%** use the historical timing rule.

Assignments and draws are deterministic from the frozen root seed and template identity.

No V2B clip is copied or resampled directly. V2B contributes only the already-frozen aggregate diagnostic targets from V6C.

## V7A — model-free timing screen

Generate E0/E1/E2/E3 timing manifests **without model training or inference**.

For each arm measure:
- aggregate onsets/sec;
- per-clip onset-rate p10/p50/p90;
- IOI p10/p50/p90;
- repeated-attack fraction <=250 ms;
- fraction IOI >=700 ms;
- simultaneous-event fraction;
- clip-boundary rejection/resample count.

### Frozen distance score

Compare each arm to the frozen V2B targets using:

`timingDistance = |repeat250 - 0.4701986755|
                + |IOI50 - 0.2560| / 0.2560
                + |IOI90 - 0.882358| / 0.882358
                + 0.5 * |rate - 1.4905949321| / 1.4905949321`

Lower is better.

### V7A advancement rule

A non-baseline timing arm advances only if all are true versus E0:
- timingDistance improves by at least **30% relative**;
- repeated-attack fraction absolute error improves by at least **0.10**;
- IOI p90 absolute error improves by at least **0.20 s**;
- aggregate onsets/sec remains within **±15%** of V2B;
- no clip exceeds its fixed duration;
- labels remain finite and internally valid.

Advance at most **one** non-baseline arm: the qualifying arm with the lowest timingDistance.

If none qualify, V7 stops before training.

## V7B — bounded paired training

Only if V7A advances one arm.

Train exactly:
- E0 baseline
- one advancing event-timing arm

Freeze:
- R3 renderer;
- exact state objective;
- O0 exact-frame BCE onset loss;
- identical initialization;
- paired batch-index generation;
- 500 optimizer steps/model;
- no retries;
- no threshold search.

Maximum:
- **2 models**
- **1000 optimizer steps total**.

## V7C — synthetic sanity

Before V2B, the advancing model must satisfy versus E0:
- synthetic pitch-onset F1 decline <= **0.08 absolute**;
- onset recall decline <= **0.08 absolute**;
- onset precision >= **0.70**;
- synthetic negative FP <= **0.10 events/s**;
- all 500 steps complete with finite losses.

Failure stops V7 before V2B evaluation.

## V7D — V2B development transfer

At frozen 0.50/0.50 thresholds, compare E0 and the advancing model on V2B.

Primary metrics:
- compatible-string onset admission;
- exact-string/fret state admission;
- trusted joint admission;
- high-confidence joint admission;
- ordinary-decoder negative FP events/sec.

Development-interest gate versus same-run E0:
- onset-admission gain >= **+0.15 absolute**;
- trusted joint-admission gain >= **+0.10 absolute**;
- high-confidence joint admission >= **15%**;
- negative FP <= **0.10 events/s**;
- state admission decline <= **0.10 absolute**.

If the arm fails, no fresh holdout is warranted.

## Interpretation

If a timing arm passes V7D while all non-timing components are fixed, that supports the narrower conclusion that **synthetic event-time distribution materially contributes to the transfer failure**.

If V7A improves model-free timing match but V7D still fails, that is evidence that event statistics alone are insufficient and that broader representation/data-domain mismatch remains.

V7 does not establish product readiness.

## Fresh confirmation

Any V7D success requires a fresh prospectively collected holdout.

V1.1 remains sealed and must not be used as confirmation or tuning data.

## Hard boundaries

Do not:
- change event counts per clip;
- change pitch/fret/chord content distributions;
- change R3 renderer;
- change model architecture or parameter count;
- change state or onset loss;
- search timing percentages or IOI ranges;
- change thresholds or decoder;
- add real audio to training;
- use V1.1 for selection;
- open P1/P2/P3;
- open A2;
- mutate main/Production.

## Exact next action

If V7 empirical execution is explicitly authorized:
1. implement E1/E2/E3 timing generators and focused deterministic tests;
2. run V7A only;
3. freeze timing manifests and V7A result;
4. if exactly one arm advances, train E0 + that arm once;
5. apply V7C synthetic sanity before any V2B readout;
6. if eligible, run V7D once;
7. freeze result and stop before fresh holdout collection.

Generic continuation does not authorize empirical V7 execution.
