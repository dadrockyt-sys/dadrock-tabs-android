# V13 active-non-onset family-mixture isolation contract V1

Date: 2026-09-29 UTC  
Status: **FROZEN PREPARATION — EMPIRICAL EXECUTION NOT AUTHORIZED**

## Question

With the exact executed V9 dataset and exact V9 batch plan fixed everywhere else, does matching only the historical 2-second comparator **active-non-onset family mixture** materially recover common-population precision/F1 without increasing negative-only false positives?

This is synthetic-only. It does not reopen V9–V12 and has no V2B stage.

## Arms

Control:
- exact executed-V9 4-second dataset arrays;
- exact V9 four-stratum batch-generation algorithm;
- 32 frames from each stratum per update;
- exact V9 random stream and per-step permutation;
- 500 updates.

Intervention:
- same exact V9 dataset arrays;
- same positive-onset selections as control at every update;
- same negative-structure-inactive selections as control at every update;
- same other-inactive selections as control at every update;
- same per-step 128-frame permutation;
- replace only the 32 active-non-onset selections so aggregate family exposure matches the historical comparator mixture.

## Frozen historical active-non-onset mixture

Historical comparator active-non-onset training counts:
- isolated 1,290
- scales 1,320
- chords 1,140
- repeated 1,470
- legato 1,560
- palmmute 900
- mixed-positive 540
- total 8,220

Across exactly 16,000 active-non-onset slots, use this frozen largest-remainder allocation:
- isolated **2,511**
- scales **2,569**
- chords **2,219**
- repeated **2,861**
- legato **3,037**
- palmmute **1,752**
- mixed-positive **1,051**
- total **16,000**

The 16,000 family labels are deterministically permuted with seed **20283928** and consumed 32 per update. Within each family pool, selection is deterministic with replacement using seed **20283929**.

## Fixed training settings

Exactly 2 models:
- nonlinear S6 architecture
- same deterministic initialization
- same executed-V9 dataset arrays
- batch size 128
- 500 updates/model
- max 1,000 total updates
- Adam lr 0.003
- state active weight 9.0
- onset positive weight 8.0
- onset loss multiplier 4.0
- state/onset thresholds 0.50/0.50
- no threshold search
- no scientific retry

## Identity requirements

Before training:
- V9 active-non-onset stratum size exactly **10,444**
- active-non-onset family pools exactly:
  - isolated 1,215
  - scales 2,079
  - chords 788
  - repeated 2,140
  - legato 1,163
  - palmmute 2,487
  - mixed-positive 572
- intervention aggregate family slots exactly match the frozen 16,000-slot allocation
- positive-onset selections identical across arms
- negative-structure-inactive selections identical across arms
- other-inactive selections identical across arms
- same per-step permutation
- exactly 16,000 active-non-onset slots per arm

Because positive-onset selections are identical, sampled attacked-note-label exposure must be identical across arms.

## Baseline reproduction gate

The control must exactly reproduce frozen V9 common comparator-test metrics within 1e-12:
- precision **0.3244274809160305**
- recall **0.6589147286821705**
- F1 **0.43478260869565216**

Failure invalidates the study.

## Support gate

The active-non-onset family-mixture hypothesis is supported only if all pass.

Primary common comparator test:
- precision gain >= **+0.15**
- F1 gain >= **+0.10**
- recall decline <= **0.05**
- negative-only FP <= **0.10/s**

Secondary frozen-V9 test:
- F1 decline <= **0.05**

Execution/identity:
- exact baseline reproduction
- exact historical active-non-onset family-slot totals
- identical positive-onset selections
- identical negative-structure-inactive selections
- identical other-inactive selections
- identical per-step shuffle
- identical sampled attacked-note-label exposure
- exactly 500 steps/model
- exactly 2 models
- finite metrics
- no threshold search
- no scientific retry
- zero real-audio/V2B inference

## Dataset regeneration

The original V9 artifact did not retain dataset arrays. If empirical V13 is later authorized:
- deterministically regenerate one frozen 2-second comparator dataset;
- deterministically regenerate one executed-V9 4-second dataset;
- train both arms on that same V9 dataset;
- no intervention-specific waveform rendering, timing generation, or state-semantic generation.

## Compute ceiling if later authorized

- exactly one regenerated common comparator dataset and one regenerated V9 dataset
- exactly 2 trained models
- <= 1,000 optimizer steps total
- <= 30 CPU minutes dataset regeneration
- <= 60 CPU minutes fit/evaluation
- <= 700 MiB persisted evidence
- $0 paid compute
- no automatic scientific retry

## Source pins

- V13 project authorization: `a22401e24e6e6a4b9783fa482a260a20920ec2ff`
- V13 runner: `61b239bdd83c91e0f12335b67c016567569c3bdf`
- V13 static tests: `147b7bad1fbb478bafd00b6110be481d47b6995f`
- post-V12 causal review: `86d7f3b8d9d1f6cdb085e248bb39972620bc4115`
- V12 result: `6cc49c6c7297406dcdebf95295ecbbecdd8f54f9`
- V9 empirical source: `9f9af0e6d45ce2e4d284b41c2e8ebee534c26981`
- S1 sampler source: `bbb8321411142f4f0f3a65ee2b96d60a8db3fbbf`
- S6 model/training source: `142168784e3dfebf8a5221017e40c8aa73be1fa5`
- runtime lock: `174a5016cfe9e6c00816d2171210aa84c66081a8`
- V13 contract validator: `92127b19b1941f5cc41121983b5287afe169462c`
- V13 validator tests: `0cba9a26c0ddaeae79210971a18ce5f9a928a1de`

## Current boundary

The user's authorization opened V13 and permits prospective/static preparation only. Empirical V13 execution is **not yet authorized**.

Current V13 execution counts:
- waveform renders 0
- models trained 0
- optimizer steps 0
- model inference 0
- V2B inference 0

Fresh explicit authorization after this contract and model-free preflight are visible is required before deterministic dataset regeneration or training.
