# V11 state-duration / legato-continuation isolation contract V1

Date: 2026-09-29 UTC  
Status: **FROZEN PREPARATION — EMPIRICAL EXECUTION NOT AUTHORIZED**

## Question

With the already successful V9 attack timing/counts fixed, does restoring historical S0 family-specific state/audio duration semantics and the omitted non-attacked legato continuation materially recover the common 2-second comparator-test precision/F1 collapse?

This is a new synthetic-only study. It does not reopen V9 or V10 and has no V2B stage.

## Arms

Both arms use the same V9 attack timing, attacked note identities, R3/timbre process, nonlinear S6 model, optimizer, loss, thresholds, 500 updates/model, and the same sampling algorithm.

Control:
- exact executed V9 4-second template semantics.

Intervention:
- same attacked onsets and note identities;
- restore historical S0 target durations:
  - isolated 1.03 s
  - scales 0.27 s
  - chords 0.48 s
  - repeated 0.31 s
  - legato attacked state 0.50 s
  - palmmute 0.16 s
  - mixed-positive 0.86 s
- restore legato non-attacked continuation duration target 0.74 s.

## Retrigger/overlap rule

A state on a string may not overlap a later attack on the same string.

For every attacked event:
- desired end = onset + historical family duration;
- actual end = min(desired end, next attacked onset on the same string, 4.0 s).

For legato:
- attacked phase target = 0.50 s;
- if temporal room remains after that phase, create the historical non-attacked continuation on the same string/fret transition;
- continuation starts at onset + 0.50 s;
- continuation end = min(start + 0.74 s, next attacked onset on the same string, 4.0 s);
- if continuation end <= continuation start, omit that continuation for that attack only.

No clipping or timing movement of attack onsets is permitted. Truncation at a same-string retrigger is part of the frozen state-semantic rule, not a fallback.

## Identity requirements

Before rendering:
- 294 total clips
- 273 positive / 21 negative-only
- 1,638 attack groups in both 4-second arms
- 1,806 attacked note labels in both 4-second arms
- exact attacked tuple identity (string, fret, onset) across V9 control and V11 intervention
- at least one restored non-attacked legato continuation
- zero same-string state overlaps
- zero invalid string/fret/onset/end values
- all negative-only clips unchanged

The exact V9 timing generator/source remains frozen; no timing search or regeneration policy change is allowed.

## Training

Exactly 2 models:
- S6 nonlinear shared encoder/state head
- 500 updates/model
- maximum 1,000 total updates
- Adam lr 0.003
- batch size 128
- state active weight 9.0
- onset positive weight 8.0
- onset loss multiplier 4.0
- state/onset thresholds 0.50/0.50
- exact-string/fret state objective
- O0 exact-frame BCE onset objective
- no threshold search
- no scientific retry

Sampler:
- four frozen 32-frame strata
- same deterministic uniform quantiles and per-step shuffle across arms
- positive-onset frame indices must be identical because attack timing is frozen
- non-positive stratum membership may differ as a downstream consequence of changed state duration.

## Evaluation

Primary population:
- frozen 2-second comparator test set.

Secondary population:
- frozen executed-V9 4-second test set.

The V11 control must exactly reproduce frozen V9 common-test precision/recall/F1 within 1e-12:
- precision 0.3244274809160305
- recall 0.6589147286821705
- F1 0.43478260869565216

Failure of reproduction invalidates the study.

## Support gate

State-semantics hypothesis is supported only if all pass:

Primary common population:
- precision gain >= +0.15
- F1 gain >= +0.10
- recall decline <= 0.05
- joint-admission decline <= 0.05
- negative-only FP <= 0.10 events/s

Secondary frozen-V9 population:
- F1 decline <= 0.05

Identity/execution:
- exact baseline reproduction
- 500 updates/model
- 2 models
- finite metrics
- no threshold search
- no scientific retry
- zero real-audio/V2B inference

The +0.15 precision and +0.10 F1 thresholds correspond to material recovery of the large V9 common-population loss without demanding full restoration.

## Compute ceiling

If later authorized:
- exactly 3 regenerated synthetic datasets in one run: 2-second common eval, 4-second V9 control, 4-second V11 intervention
- exactly 2 trained models
- <= 1,000 optimizer steps total
- <= 30 CPU minutes render/data build
- <= 60 CPU minutes fit/evaluation
- <= 700 MiB persisted evidence
- $0 paid compute
- no automatic scientific retry

## Source pins

- project authorization: `3b44f4cb7d2fe233ae8c14ea9f51b292a0632e5e`
- V11 runner: `3d19a5e368955e083a740020b76d6fa248532eff`
- V11 static tests: `a675b17521e118936da0636f7533f74e352b9ef8`
- post-V10 integrity review: `6ae51fbd0189cfcaae388c43e26c37d92d8a728f`
- qualified V9 result: `4e08a77600976813c478ce5c55c8908cbe63f48f`
- qualified V10 result: `a92ce2b76cfcf4ac9a8372cf918d6495a164a460`
- V9 empirical source: `9f9af0e6d45ce2e4d284b41c2e8ebee534c26981`
- S0 template source: `c05b6f986186dbe96245875833ab9564df99d4fb`
- S1 sampler: `bbb8321411142f4f0f3a65ee2b96d60a8db3fbbf`
- S6 training/model: `142168784e3dfebf8a5221017e40c8aa73be1fa5`
- runtime lock: `174a5016cfe9e6c00816d2171210aa84c66081a8`

## Boundary

The user's authorization opened and allowed preparation of this new project. It does **not** authorize empirical V11 training because this exact contract did not exist when that authorization was given.

Allowed now:
- static validation
- model-free template audit
- source/contract pin verification

Not authorized now:
- waveform rendering
- optimizer steps
- model inference
- V2B or any real-audio evaluation
- V1.1/P1/P2/P3/A2
- main/Production mutation

A fresh explicit authorization after this contract and preflight are visible is required before empirical V11 execution.
