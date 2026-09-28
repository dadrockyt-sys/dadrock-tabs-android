# Astra synthetic onset-envelope diversity S12 design V1

Date: 2026-09-28
Status: DESIGN FROZEN BEFORE MODEL EXECUTION

## Question

With model architecture, labels, sampler, optimizer, thresholds, chord-voicing diversity, split membership and held-out baseline data fixed, does training-only onset-envelope randomization improve robustness to a prospectively defined soft-onset synthetic challenge without materially degrading ordinary synthetic competence?

This experiment follows the frozen P1/P2 integrity audit only at the level of a qualitative hypothesis: real-guitar note onsets can be softer and more variable than the original procedural generator. No P1/P2 numeric target, waveform, feature, threshold or capture is used to choose S12 generator parameters or to score S12.

P1/P2/P3 are forbidden inputs.

## Common starting dataset

Both arms begin from the frozen S9 diversified synthetic corpus:
- 294 clips / 588 logical seconds;
- 30 unique training chord voicings;
- validation/test arrays fixed;
- no external audio.

Regenerate the S0 control corpus and then deterministically build the frozen S9 30-voicing intervention corpus. That S9 corpus is the S12 control dataset.

## Intervention

Only training features are re-rendered. State, onset, references, family, split and negative-structure arrays must remain bit-identical.

Use the same template/voicing, note timing/duration, timbre RNG key, damping, pick-position, brightness, body filter, phase and noise RNG draws.

Use a separate deterministic envelope RNG so timbre RNG consumption is unchanged.

For each training clip with attacked notes, draw one clip-level profile:
- attacked-note rise time: log-uniform from 2.5 ms to 35 ms;
- transient burst amplitude: uniform from 0.02 to 0.16.

These bounds are frozen engineering priors spanning crisp through soft note onsets. They were not fit to P1/P2 measurements.

Legato/non-attacked note semantics stay unchanged. Palm-mute damping stays unchanged.

## Synthetic soft-onset challenge

Create a third dataset used for evaluation only.

It is identical to the S12 control dataset except test features are re-rendered with one fixed soft-onset profile:
- attacked-note rise time 30 ms;
- transient burst amplitude 0.03.

All test labels/references remain bit-identical. Training and validation arrays in the challenge copy are irrelevant and must not be used for optimization or model selection.

The challenge profile is fixed prospectively and is not a numerical match to any real P1/P2 metric.

## Model/training

Use exactly the frozen S11/S9 model and regimen:
- 5-frame / 960-feature input;
- shared encoder Linear(960,128) -> ReLU;
- state head Linear(128,128) -> ReLU -> Linear(128,126);
- onset head Linear(128,6);
- state active weight 9.0;
- onset pos_weight 8.0;
- onset loss multiplier 4.0;
- uniform onset-aware 32/32/32/32 sampler;
- Adam lr 0.003;
- batch size 128;
- exactly 500 optimizer steps/model;
- decoder V2;
- state/onset thresholds 0.50 / 0.50;
- zero threshold search/retuning.

Use exactly three paired seeds:
- 20260927
- 20260928
- 20260929

Within each seed, control/intervention initialization and minibatch indices are identical. Labels are identical. Only training features differ.

Exactly 6 models total / 3,000 optimizer steps.

## Required measurements

For each seed, evaluate both arms on:
1. ordinary frozen synthetic test set;
2. frozen soft-onset challenge test set.

Report pooled pitch-onset precision/recall/F1, onset+offset F1, repeated-note recall, family onset F1s, exact state admission, exact joint admission and negative-only false positives/sec.

## Frozen S12 gate

All must pass:
1. challenge onset F1 gain > 0 in 3/3 seeds;
2. challenge onset recall gain > 0 in 3/3 seeds;
3. mean challenge onset F1 gain >= +0.05;
4. mean challenge onset recall gain >= +0.08;
5. no seed loses > 0.03 ordinary-test onset F1;
6. no seed loses > 0.03 ordinary-test state admission;
7. no seed loses > 0.04 ordinary-test joint admission;
8. no seed loses > 0.05 challenge onset precision;
9. challenge negative-only FP <= 0.10 events/s in every intervention seed;
10. no ordinary-test non-chord family loses > 0.15 F1 in more than one seed;
11. all six models complete exactly 500 steps with finite metrics, paired initialization/batches, fixed thresholds and no threshold search.

The gate tests robustness to a prospectively frozen synthetic domain shift. It does not establish real-guitar transfer.

## Decision branches

- Gate passes: onset-envelope diversity is supported as a synthetic robustness intervention. Freeze and stop. Any later real transfer test requires a separate design and fresh P1/P2 authorization.
- Challenge improves but ordinary synthetic competence regresses: reject the intervention as unstable.
- No robust challenge gain: reject onset-envelope randomization under this fixed model/training regime.
- Any identity/runtime failure: freeze and stop; no automatic retry.

## Hard execution ceiling

- no P1/P2/P3 access;
- no external audio;
- exactly 6 models;
- exactly 3,000 total optimizer steps;
- CPU-only GitHub Actions;
- <=90 fit/eval CPU minutes;
- <=20 render CPU minutes;
- $0 paid compute;
- automatic model retries 0;
- threshold tuning 0;
- no Codespaces;
- no Vercel;
- no main/Production/customer delivery.

## Authorization

The user explicitly authorized continuation on 2026-09-28. This authorization is scoped to one S12 synthetic-only model execution under the frozen design above. It does not authorize P1/P2/P3 access.
