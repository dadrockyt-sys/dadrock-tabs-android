# Astra synthetic onset-envelope diversity S12 design V1

Date: 2026-09-28
Status: **DESIGN FROZEN BEFORE MODEL EXECUTION**

## Question

With model architecture, labels, sampler, optimizer, thresholds, chord-voicing diversity, split membership and ordinary held-out data fixed, does training-only **CQT onset-transition softening** improve robustness to a prospectively defined soft-onset synthetic feature challenge without materially degrading ordinary synthetic competence?

The frozen P1/P2 integrity audit motivates only the qualitative hypothesis that real note-onset contrast can be weaker and more variable. **No P1/P2 numeric target, waveform, feature, threshold or capture is used to choose S12 transformation parameters or to score S12.** P1/P2/P3 are forbidden inputs.

## Common starting dataset

Both arms begin from the frozen S9 diversified synthetic corpus:
- 294 clips / 588 logical seconds;
- 30 unique training chord voicings;
- validation/test arrays fixed;
- no external audio.

Regenerate the S0 corpus, then deterministically build the frozen S9 30-voicing corpus. That S9 corpus is the S12 control dataset.

## Intervention

Only **training feature arrays** are changed. State, onset, references, family, split and negative-structure arrays remain bit-identical.

At every labeled onset frame, soften the CQT transition by blending that frame and the following frame toward the immediately preceding frame. For each training clip, draw one deterministic blend factor from a separate RNG:
- blend factor uniform from **0.25 to 0.75**;
- transformed frame = (1-blend) * original + blend * previous-frame value;
- apply at onset frame and onset+1 only;
- if multiple strings share the same onset frame, transform that feature frame only once;
- never alter frame 0;
- clip transformed CQT values to the original frozen range [0,1].

This changes only local onset contrast. It does not alter note identity, timing, sustain labels, voicings, or ordinary held-out examples.

The bounds are broad frozen engineering priors and are not fit to P1/P2 values.

## Synthetic soft-onset challenge

Create a third dataset used for evaluation only.

It is identical to the control dataset except **test feature arrays** receive the same transformation with a fixed blend factor **0.70** at every labeled onset frame and onset+1.

All labels/references are bit-identical. Training and validation arrays in the challenge copy are untouched.

The challenge factor is fixed prospectively and is not matched to any P1/P2 statistic.

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

Use exactly three paired seeds: 20260927, 20260928, 20260929.

Within each seed, control/intervention initialization and minibatch indices are identical. Labels are identical. Exactly 6 models / 3,000 total optimizer steps.

## Required measurements

For each seed evaluate both arms on:
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

Passing is synthetic robustness evidence only, not real-transfer evidence.

## Decision branches

- Gate passes: CQT onset-transition diversity is supported as a synthetic robustness intervention. Freeze and stop.
- Challenge improves but ordinary competence regresses: reject as unstable.
- No robust challenge gain: reject this fixed intervention.
- Identity/runtime failure: freeze and stop; no automatic retry.

Any later P1/P2 transfer test requires a separate design and fresh authorization. P3 remains sealed.

## Hard execution ceiling

- no P1/P2/P3 access;
- no external audio;
- exactly 6 models / 3,000 optimizer steps;
- CPU-only GitHub Actions;
- <=90 fit/eval CPU minutes;
- $0 paid compute;
- automatic model retries 0;
- threshold tuning 0;
- no Codespaces;
- no Vercel;
- no main/Production/customer delivery.

## Authorization

The user explicitly authorized continuation on 2026-09-28. This authorization is scoped to one S12 synthetic-only model execution under this frozen design. It does not authorize P1/P2/P3 access.
