# V12 positive-onset family-mixture isolation contract V1

Date: 2026-09-29 UTC
Status: **FROZEN PREPARATION — EMPIRICAL EXECUTION NOT AUTHORIZED**

## Question

With the exact executed V9 dataset semantics and all non-positive batch selections fixed, does matching the historical 2-second comparator positive-onset family mixture materially recover common-population precision/F1?

This is synthetic-only. It does not reopen V9/V10/V11 and has no V2B stage.

## Data reuse constraint

The original V9 artifact did not retain comparator/intervention dataset arrays. If empirical V12 is later authorized, the common comparator and executed-V9 datasets must therefore be deterministically regenerated with the exact frozen V9 source/runtime.

Both V12 training arms will use the same single regenerated V9 dataset arrays. No intervention-specific waveform rendering or timing/state regeneration is allowed. The control must exactly reproduce frozen V9 common-test metrics before the intervention is interpretable.

## Arms

Control:
- exact executed V9 dataset
- exact V9 four-stratum batch-generation algorithm
- 32 positive-onset + 32 active-non-onset + 32 negative-structure-inactive + 32 other-inactive frames/update
- 500 updates

Intervention:
- same dataset arrays
- same non-positive selections as control at every update
- same per-step 128-frame permutation
- replace only the 32 positive-onset selections so aggregate family exposure matches the historical comparator mixture

## Frozen historical mixture

Historical comparator train positive-onset frame counts:
- isolated 30
- scales 120
- chords 60
- repeated 120
- legato 30
- palmmute 150
- mixed-positive 15
- total 525

Across exactly 16,000 positive-onset slots, use the frozen largest-remainder allocation:
- isolated **914**
- scales **3,657**
- chords **1,829**
- repeated **3,657**
- legato **914**
- palmmute **4,572**
- mixed-positive **457**
- total **16,000**

The 16,000 family labels are deterministically permuted with seed **20281928** and consumed 32 per update. Within each family pool, frame selection is deterministic with replacement using seed **20281929**.

## Fixed training settings

Exactly 2 models, same deterministic initialization, same executed-V9 dataset arrays, batch size 128, 500 updates/model, max 1,000 total updates, Adam lr 0.003, state active weight 9.0, onset positive weight 8.0, onset loss multiplier 4.0, thresholds 0.50/0.50, no threshold search, no scientific retry.

## Identity requirements

Before training:
- V9 positive-onset stratum size exactly **1,170**
- family pools exactly isolated 150, scales 240, chords 60, repeated 240, legato 120, palmmute 300, mixed-positive 60
- intervention aggregate family slots exactly match the frozen 16,000-slot allocation
- control and intervention non-positive selections identical
- same per-step shuffle
- same 16,000 positive-onset slots per arm

Because chord onset frames contain 3 attacked-note labels, the intervention's total attacked-note-label exposure is expected to change as a downstream consequence. It must be measured and reported; it is not itself the causal variable being isolated.

## Baseline reproduction gate

The control must exactly reproduce frozen V9 common comparator-test metrics within 1e-12:
- precision **0.3244274809160305**
- recall **0.6589147286821705**
- F1 **0.43478260869565216**

Failure invalidates the study.

## Support gate

Family-mixture hypothesis is supported only if all pass:
- common precision gain >= **+0.15**
- common F1 gain >= **+0.10**
- common recall decline <= **0.05**
- common negative-only FP <= **0.10/s**
- frozen-V9 test F1 decline <= **0.05**
- exact baseline reproduction
- exact historical family-slot totals
- identical non-positive selections
- same per-step shuffle
- exactly 500 steps/model
- exactly 2 models
- finite metrics
- no threshold search
- no scientific retry
- zero real-audio/V2B inference

## Source pins

- V12 project authorization: `cdbef30524a23788dbc54369f0a00a8cc88d30d3`
- V12 runner: `9aa5a381269f022eb75aa13308442250dd0e7a51`
- V12 static tests: `e385d0a6ae958f974dca832ab91ec7051de9568d`
- post-V11 causal review: `a817799cbb0047af113a24724b7ab057fe95bc2f`
- V11 result: `390ba1085a99d41da9fb4a07232f51e66f6c8e6f`
- V9 empirical source: `9f9af0e6d45ce2e4d284b41c2e8ebee534c26981`
- S1 sampler source: `bbb8321411142f4f0f3a65ee2b96d60a8db3fbbf`
- S6 model/training source: `142168784e3dfebf8a5221017e40c8aa73be1fa5`
- runtime lock: `174a5016cfe9e6c00816d2171210aa84c66081a8`

## Current boundary

The user's authorization opened this project and permits prospective/static preparation only. Empirical V12 execution is not yet authorized.

Current V12 execution counts: waveform renders 0, models trained 0, optimizer steps 0, model inference 0, V2B inference 0.

Fresh explicit authorization after this contract/preflight is required before deterministic dataset regeneration or training.
