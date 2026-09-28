# Astra synthetic data diversity S1 design V1

Date: 2026-09-27
Status: DESIGN FROZEN — NOT AUTHORIZED FOR EXECUTION

## Question

Does a fixed onset-aware training sampler materially improve the five-frame temporal model's synthetic onset recall and repeated-note recall versus the same model trained with the original uniform frame sampler, with every other experimental choice held fixed?

## Source evidence

S0 run 36369999876 showed:
- temporal model onset F1 0.4235 versus per-frame comparator 0.1304;
- temporal recall 0.2791 and precision 0.8780;
- repeated-note onset recall 0.2143;
- 93 FN versus 5 FP;
- zero negative-only false positives over 6 seconds;
- absolute S0 gate failed.

Offline target accounting shows only 645 positive string-onset positions among 109,620 training string/frame positions (0.5884%), and 525 positive-onset clip-frames among 18,270 training clip-frames (2.8736%).

## Fixed data and rendering

Reuse the exact deterministic S0 generator definition and split, regenerated only after fresh authorization:
- root seed 20260927;
- 98 template identities;
- 3 timbre variants/template;
- 294 clips x 2.0 s = 588 s;
- train/validation/test = 210 / 42 / 42;
- same 22.05 kHz frozen CQT, 192 bins;
- no external samples, IRs, pretrained audio generator, real corpus, P1, P2 or P3.

The S0 test split has already influenced this design, so it is development evidence rather than an untouched holdout.

## Models

Exactly two models, both identical five-frame temporal models:

5 frames x 192 bins -> Linear(960,128) -> ReLU -> identical state/onset heads.

Both use:
- Adam, lr 0.003;
- state active weight 1.5;
- onset BCE positive weight 8;
- onset loss weight 4;
- state threshold 0.50;
- onset threshold 0.50;
- decoder V2;
- exactly 500 requested optimizer steps;
- minibatch size 128;
- no architecture, loss, threshold, or learning-rate sweep.

The only changed variable is frame sampling.

## Control sampler

The exact S0 uniform sampler:
- flatten all training clip-frames;
- sample 128 frames uniformly with replacement per optimizer step.

## Intervention sampler

Every 128-frame minibatch contains:
- 32 positive-onset frames: at least one string onset target is 1;
- 32 active non-onset frames: at least one string active and no onset target is 1;
- 32 inactive frames from clips marked with a negative structure;
- 32 other inactive frames.

Sampling is with replacement within each stratum. If any stratum has zero members, fail before optimizer work; do not substitute another stratum.

No loss weighting changes.

## Measurements

For both models report on the fixed synthetic test split:
- pitch-onset TP/FP/FN, precision, recall, F1;
- pitch-onset+offset F1;
- repeated-note numerator/denominator/recall;
- family-level onset precision/recall/F1;
- negative-only decoded FP events/second;
- exact optimizer steps and runtime;
- fixed-threshold onset probability/logit summaries at positive reference frames;
- state-admission fraction at positive reference frames;
- joint onset+state admission fraction;
- no threshold sweep.

Also report validation metrics, with no post-result tuning.

## Frozen S1 success criteria

The onset-aware sampler supports the sampling hypothesis only if all are true:
1. onset F1 gain versus uniform >= +0.15;
2. onset recall gain versus uniform >= +0.20;
3. repeated-note recall gain versus uniform >= +0.20;
4. onset precision >= 0.80;
5. precision loss versus uniform <= 0.10;
6. negative-only FP rate <= 0.10 events/s;
7. absolute onset recall >= 0.55;
8. absolute onset F1 >= 0.60;
9. repeated-note recall >= 0.50;
10. all metrics finite; both models complete <=500 steps; zero threshold search.

These are new S1 diagnostic gates. They do not replace or relax the failed S0 absolute gate.

## Decision branches

- If all S1 criteria pass: sampling scarcity is supported as a meaningful contributor. Stop and design the next synthetic competence gate; do not open P1/P2 automatically.
- If relative recall improves but absolute floors fail: sampling helps but is insufficient. Stop and isolate one remaining cause.
- If precision or negative specificity deteriorates beyond the frozen limits: reject this sampling ratio.
- If there is no material recall gain: reject sampling scarcity as the primary next lever under this setup.
- Any guard/runtime/preparation failure: freeze failure and stop; zero automatic retry.

## Hard execution ceiling if later authorized

- exactly 294 synthetic clips / 588 s;
- no external audio assets;
- render <=20 CPU min;
- exactly 2 temporal models;
- <=500 optimizer steps/model, <=1,000 total;
- fit/eval <=60 CPU min;
- $0 paid compute;
- zero automatic retries;
- no threshold search or retuning;
- no P1/P2/P3 access;
- no deployment, main mutation, or customer delivery.

## Authorization boundary

This document does not authorize execution. Fresh explicit authorization is required before S1 rendering or optimizer work.
