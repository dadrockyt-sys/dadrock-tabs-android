# V6 Onset-Representation and Event-Statistics Adequacy Design V1

Date: 2026-09-29  
Status: **DESIGN FROZEN — EMPIRICAL EXECUTION NOT YET AUTHORIZED**

## Why V6 exists

V5 showed that relaxing exact string/fret state supervision increases compatible state admission but leaves V2B onset admission at only **1/56** and produces **0/56 joint hits**.

The next narrow question is:

> Is the real-domain transfer collapse dominated by mismatch in onset/event supervision and temporal event statistics rather than by the state target itself?

V6 tests onset-side task adequacy while keeping model architecture, renderer, state objective, thresholds, and decoder fixed.

## Frozen invariants

Across all V6 arms, do not change:
- S9/S6-style nonlinear architecture;
- parameter count;
- R3 renderer;
- synthetic examples, labels, splits, and state targets;
- exact-string/fret state objective;
- sampler and batch indices;
- optimizer, learning rate, and 500-step budget;
- state loss weighting;
- state/onset thresholds at **0.50 / 0.50**;
- production decoder;
- V2B annotations;
- V1.1 remains sealed.

Only the **onset target/loss interpretation** may differ.

## Frozen arms

### O0 — historical onset baseline

Use the original binary onset target:
- onset = 1 only on the exact labeled onset frame;
- historical BCE-with-logits onset loss;
- historical positive weighting.

### O1 — fixed temporal onset tolerance

Without changing event times or labels, spread each positive onset target over a fixed ±1 frame window:
- center frame target = 1.0
- adjacent frames target = 0.5
- all other frames = 0.0

Use BCE-with-logits against these frozen soft targets.

No window-size search is allowed.

Purpose: test whether exact single-frame onset supervision is too brittle for real timing/capture variation.

### O2 — fixed focal onset objective

Keep the original exact onset targets, but replace onset BCE with a single prospectively fixed focal formulation:
- gamma = **2.0**
- alpha-positive = **0.75**
- alpha-negative = **0.25**

No focal-parameter search.

Purpose: test whether extreme easy-negative dominance is suppressing real-domain onset activation.

### O3 — combined tolerant + focal onset objective

Use the O1 soft targets with the O2 fixed focal weighting:
- ±1 frame target spread
- gamma 2.0
- alpha-positive 0.75
- alpha-negative 0.25

No other loss weighting changes.

## V6A — synthetic sanity

Train exactly O0/O1/O2/O3 under identical initialization and batch plans.

For each arm, evaluate the frozen synthetic test set.

An alternative arm is synthetic-sanity eligible only if, relative to O0:
- pitch-onset F1 decline <= **0.08 absolute**;
- onset recall decline <= **0.08 absolute**;
- onset precision >= **0.70**;
- negative-only FP <= **0.10 events/s**;
- all 500 optimizer steps complete with finite losses.

No arm failing V6A may be evaluated on V2B.

## V6B — V2B onset-transfer development test

Eligible arms are evaluated on V2B at unchanged 0.50/0.50 gates.

Primary metrics:
- compatible-pitch state admission;
- compatible-string onset admission;
- trusted joint admission;
- high-confidence joint admission;
- ordinary-decoder negative FP events/sec.

For all arms, V2B onset admission is:
- maximum onset probability across physical strings compatible with the trusted MIDI pitch;
- threshold remains 0.50.

No temporal tolerance is granted during V2B scoring; O1/O3 must generalize from training.

## Frozen development-interest gate

An alternative onset arm is development-interesting only if, versus same-run O0:
- onset-admission gain >= **+0.20 absolute**;
- trusted joint-admission gain >= **+0.15 absolute**;
- high-confidence joint admission >= **20%**;
- negative-only decoded FP <= **0.10 events/s**;
- compatible state admission does not decline by more than **0.10 absolute**.

If no arm passes, V6 stops.

## V6C — event-statistics audit

Regardless of V6B success, produce a model-free comparison of synthetic vs V2B positive event statistics:
- onsets per second;
- median inter-onset interval;
- 10th/50th/90th percentile inter-onset interval;
- repeated-attack fraction within 250 ms;
- event-density distribution by clip;
- active-duration distribution where available;
- onset-to-sustain ratio.

This audit is descriptive only. It may motivate a later experiment but may not retroactively alter O1/O2/O3.

## Compute ceiling

Maximum:
- **4 models**
- **500 optimizer steps/model**
- **2000 optimizer steps total**
- zero retries
- zero threshold search
- zero loss-parameter search.

## Interpretation

If O1/O2/O3 substantially improve V2B onset and joint admission while state/task/model/rendering are fixed, that supports the narrower conclusion that **onset supervision contributes materially to the transfer failure**.

If they do not, the evidence shifts further toward broader representation/data adequacy or the need for fresh real-domain training.

V6 does not establish product readiness or production decoding quality.

## Fresh confirmation

Any V6B success requires a fresh prospectively collected holdout before adoption or broader claims.

V1.1 must not be repurposed as that holdout.

## Hard boundaries

Do not:
- change architecture or parameter count;
- change R3 renderer;
- change state objective;
- search onset windows, alpha, gamma, or loss weights;
- alter thresholds or decoder;
- add real audio to training;
- use V1.1 for selection;
- open P1/P2/P3;
- open A2;
- mutate main/Production.

## Exact next action

If V6 empirical execution is explicitly authorized:
1. implement O1/O2/O3 onset objectives plus focused tests;
2. freeze source hashes;
3. train O0/O1/O2/O3 once at 500 steps each;
4. apply V6A synthetic sanity before any V2B readout;
5. evaluate only sanity-eligible arms on V2B;
6. run the model-free V6C event-statistics audit;
7. freeze all results and stop before any fresh holdout.

Generic continuation does not authorize empirical V6 execution.
