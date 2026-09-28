# Astra synthetic data diversity S11 design V1

Date: 2026-09-28
Status: **DESIGN FROZEN — NOT AUTHORIZED FOR MODEL EXECUTION**

## Question

Is the S9 benefit of increasing training chord voicing diversity from 10 to 30 robust across multiple deterministic model/minibatch seeds?

S11 is a **robustness confirmation**, not a tuning experiment.

## Fixed scientific comparison

For each seed, compare:
- control dataset: 10 unique training chord voicings across 30 clips;
- intervention dataset: 30 unique training chord voicings across 30 clips with paired timbre RNG keys.

Within each seed:
- validation/test and non-chord data are bit-identical;
- model initialization is identical across control/intervention;
- minibatch indices are identical across control/intervention.

Architecture is fixed to the S9/S6 nonlinear replacement state head:
- shared encoder Linear(960,128) -> ReLU;
- state head Linear(128,128) -> ReLU -> Linear(128,126);
- onset head Linear(128,6).

Training fixed:
- state active weight 9.0;
- onset BCE pos_weight 8.0;
- onset loss multiplier 4.0;
- uniform onset-aware 32/32/32/32 sampler;
- Adam lr 0.003;
- batch size 128;
- exactly 500 optimizer steps/model;
- thresholds 0.50 / 0.50;
- decoder V2;
- zero threshold search/retuning.

## Frozen seeds

Use exactly three deterministic run seeds:
- 20260927
- 20260928
- 20260929

The dataset construction root remains 20260927 so both datasets are identical across seed pairs. Only model initialization/minibatch RNG changes by the declared run seed.

Exactly 6 models total: 3 paired comparisons x 2 arms.

## Required measurements

For each seed and pooled summary:
- chord precision/recall/F1;
- overall onset precision/recall/F1;
- onset+offset F1;
- repeated recall;
- exact onset/state/joint admission;
- negative-only FP/sec;
- family F1s;
- paired deltas intervention minus control.

Report:
- mean paired delta;
- median paired delta;
- minimum paired delta;
- count of seeds with positive delta.

## Frozen S11 robustness criteria

All must pass:

1. chord F1 gain is positive in **3/3** seeds;
2. chord recall gain is positive in **3/3** seeds;
3. overall onset F1 gain is positive in **3/3** seeds;
4. overall onset recall gain is positive in **3/3** seeds;
5. mean chord F1 gain >= **+0.10**;
6. mean chord recall gain >= **+0.12**;
7. mean overall onset F1 gain >= **+0.04**;
8. mean overall onset recall gain >= **+0.06**;
9. mean joint-admission gain >= **+0.03**;
10. no seed loses > **0.05 precision**;
11. no seed has negative-only FP > **0.10 events/s**;
12. no non-chord family loses > **0.15 F1** in more than one seed;
13. all 6 models finish exactly 500 requested steps with finite metrics, paired data/init/batches, fixed thresholds and zero threshold search.

These criteria test robustness of the **diversity effect**. They do not require the 30-voicing arm to pass an absolute state-admission floor.

## Decision branches

- **All pass:** S9 chord-diversity effect is seed-robust synthetic development evidence. Stop and prepare a separate proposal for P1/P2 transfer; do not access P1/P2 automatically.
- **Mixed/seed-sensitive:** do not promote S9 as robust; stop architecture/data tuning and document instability.
- **Mostly negative:** reject chord-diversity effect as unreliable under current training.
- **Any identity/runtime failure:** freeze and stop; zero automatic retry.

## Hard ceiling if later authorized

- regenerate the two 294-clip / 588 s synthetic datasets once;
- exactly 6 models total;
- exactly 500 optimizer steps/model, 3,000 total;
- render <=20 CPU minutes;
- fit/eval <=90 CPU minutes;
- $0 paid compute;
- zero automatic retries;
- no threshold tuning;
- no P1/P2/P3;
- no Codespaces;
- no Vercel;
- no deployment/main/customer delivery.

## Authorization boundary

S11 requires fresh explicit authorization before model execution.
