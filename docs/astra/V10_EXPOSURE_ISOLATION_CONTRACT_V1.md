# V10 attack-label exposure isolation contract V1

Date: 2026-09-29 UTC  
Status: **FROZEN PREPARATION — EMPIRICAL EXECUTION NOT YET AUTHORIZED**

## Project question

V9 solved the common-unit timing-fit problem but failed synthetic sanity with a large precision/F1 collapse. One measured package difference was attacked-note-label exposure: both arms used 500 updates, 64,000 sampled frames, 16,000 sampled positive-onset frames and 1,486.077 sampled frame-seconds, but the 2-second comparator saw **19,702 attacked note labels** while V9 saw **17,676**.

V10 isolates one training variable:

> **Does exact matching of sampled attacked-note-label exposure, while holding the frozen V9 dataset, model, loss, thresholds, optimizer, update count, non-positive strata and per-step shuffle fixed, materially restore synthetic pitch-onset precision/F1?**

This is a new synthetic-only diagnostic. It is not a V9 retry and has no V2B stage.

## Frozen arms

Both arms train on the same regenerated frozen V9 4-second dataset.

- control: exact V9 positive-onset sampling plan
- intervention: replace only the 32 positive-onset selections per update to make total sampled attacked-note labels exactly **19,702**

All non-positive stratum selections are identical between arms.

Both arms:
- S6 nonlinear model
- same deterministic initialization
- same V9 features/targets
- same four 32-frame sampler strata
- batch size 128
- Adam lr 0.003
- state active weight 9.0
- onset positive weight 8.0
- onset loss multiplier 4.0
- state/onset thresholds 0.50/0.50
- exact-string/fret state objective
- O0 exact-frame BCE onset objective
- exactly 500 optimizer steps
- no threshold search or retuning

## Exact exposure construction

There are exactly **16,000 positive-onset frame slots** per model: 32 slots x 500 updates.

V9 positive-onset frames are required to have onset-label multiplicity exactly 1 or 3.

To produce exactly 19,702 attacked note labels:

- multi-label positive frames: **1,851**
- single-label positive frames: **14,149**
- total labels = 14,149 + 3 x 1,851 = **19,702**

Per-update multi-label schedule:
- 351 updates use 4 multi-label + 28 single-label positive frames
- 149 updates use 3 multi-label + 29 single-label positive frames
- the 500-update order is deterministically permuted with seed **20279928**

The intervention changes only which positive-onset frames are selected. It uses:
- the same selected active-non-onset frames
- the same selected negative-structure-inactive frames
- the same selected other-inactive frames
- the same per-step 128-frame shuffle

The control must reproduce the frozen V9 attacked-note-label exposure exactly: **17,676**. If it does not, the study is invalid and stops before interpretation.

## Dataset identity

The study regenerates, in one run, both:
- the frozen 2-second comparator dataset, evaluation only
- the frozen 4-second V9 dataset, training + evaluation

Both training arms use exactly the same V9 dataset arrays.

The 2-second comparator test split is used as the primary fixed common evaluation population because the frozen V9 failure was measured there. The V9 test split is a secondary same-domain population.

No real audio is used.

## Baseline reproduction gate

Before any scientific conclusion, the V10 control must reproduce frozen V9 common-population metrics exactly within 1e-12:

- precision **0.3244274809160305**
- recall **0.6589147286821705**
- F1 **0.43478260869565216**
- sampled attacked note labels **17,676**

Failure means invalid reproduction; stop without interpreting the exposure arm.

## Exposure-hypothesis support gate

The exposure hypothesis is supported only if **all** pass:

Primary common 2-second comparator test population:
- precision gain vs V10 control **>= +0.20**
- F1 gain vs V10 control **>= +0.15**
- recall decline vs V10 control **<= 0.08**
- negative-only false positives **<= 0.10 events/s**

Secondary V9 test population:
- precision decline vs V10 control **<= 0.05**
- F1 decline vs V10 control **<= 0.05**

Identity:
- control sampled attacked note labels exactly **17,676**
- intervention sampled attacked note labels exactly **19,702**
- exactly 500 updates/model
- exactly 2 models
- all metrics finite
- no threshold search
- no scientific retry

The +0.20 precision and +0.15 F1 thresholds correspond approximately to recovering at least 40% and 50% respectively of the V9 common-population losses (precision loss 0.5025; F1 loss 0.3034).

## Interpretation limits

A pass would support only the claim that positive attacked-note-label exposure materially contributed to the V9 synthetic failure.

A fail would weaken that explanation and point toward other package differences such as duration/context distribution, active/sustain-frame composition, attack-count allocation, or onset-state coupling.

Neither outcome:
- authorizes V2B inference
- proves anything about real-audio transfer
- changes V9's frozen result
- changes thresholds/decoder
- changes main/Production

## Compute ceiling if later authorized

- exactly 2 training models
- exactly 500 updates/model
- <=1,000 optimizer steps total
- one regenerated V9 dataset + one regenerated 2-second comparator evaluation dataset
- <=30 CPU minutes render/data build
- <=60 CPU minutes fit/evaluation
- <=700 MiB persisted synthetic evidence
- $0 paid compute
- no automatic scientific retry

## Frozen source pins

- V10 project authorization: `e32f9b87fe76eb9e90f3b5610110fb76c192327b`
- V10 runner: `2c25b80c553d600ba26d2a7729bc1f3d1050f944`
- V10 static tests: `7becffdd0ae821636d7935ea53b5ad9e0cb386c1`
- frozen V9 result: `d4d73b282915bb7073092cd1396cdfd11c2fa8a1`
- V9 empirical source: `9f9af0e6d45ce2e4d284b41c2e8ebee534c26981`
- S6 model/training source: `142168784e3dfebf8a5221017e40c8aa73be1fa5`
- S1 sampler source: `bbb8321411142f4f0f3a65ee2b96d60a8db3fbbf`
- exact runtime lock: `174a5016cfe9e6c00816d2171210aa84c66081a8`
- V10 contract validator: `34d248f74812652fcd213fc420506c3f82b5a6d1`
- V10 validator tests: `32d6dac52a2e388f507ac958aab4ec7f6bbfc9b1`

## Current boundary

The user's authorization is recorded as authorization to define and prepare this new project prospectively. It is **not** treated as informed authorization for empirical V10 execution because this contract did not yet exist when that authorization was given.

Current counts for V10:
- candidate timing generations: 0
- waveform renders: 0
- models trained: 0
- optimizer steps: 0
- model inference: 0
- V2B inference: 0

A fresh explicit authorization after this frozen contract is required before any V10 empirical execution.
