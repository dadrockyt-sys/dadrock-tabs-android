# Astra synthetic data diversity S8 design V1

Date: 2026-09-28
Status: **DESIGN FROZEN — NOT AUTHORIZED FOR MODEL EXECUTION**

## Question

With the S6 nonlinear replacement state head fixed, does token-balanced sampling inside the positive-onset stratum improve chord/polyphonic supervision, state/joint admission and event transcription?

## Fixed model/training

Both arms use:
- shared encoder Linear(960,128) -> ReLU;
- nonlinear replacement state head Linear(128,128) -> ReLU -> Linear(128,126);
- onset head Linear(128,6);
- active-state weight 9.0;
- onset BCE pos_weight 8.0;
- onset loss multiplier 4.0;
- Adam lr 0.003;
- batch size 128;
- exactly 500 optimizer steps;
- thresholds 0.50 / 0.50;
- decoder V2;
- identical model initialization;
- identical generated corpus;
- zero threshold search.

Corpus remains 294 deterministic clips / 588 s. P1/P2/P3 remain sealed.

## Only changed variable

Each batch still contains:
- 32 positive-onset frames;
- 32 active non-onset frames;
- 32 inactive frames from negative-structure clips;
- 32 other inactive frames.

For the three non-positive strata, both arms use identical sampled indices.

For the 32 positive-onset frames:

### Control
Uniform sampling with replacement over all positive-onset train frames.

### Intervention
Sampling with replacement with frame probability proportional to:
`number of strings whose onset target is 1 in that frame`.

Thus a 3-string chord attack receives 3x the sampling weight of a one-string attack.

No family label itself is used for weighting.

## Frozen accounting

Train positive-onset frames = 525.
Train positive string-onset tokens = 645.

Chord attacks:
- 60 positive frames = 11.43% of positive frames;
- 180 positive string tokens = 27.91% of positive onset tokens.

Under token-weighted sampling, chord-frame selection probability becomes 27.91% rather than 11.43%.

Expected positive string tokens per selected positive frame:
- uniform frame sampler: 645 / 525 = 1.2286;
- token-balanced sampler: sum(k^2)/sum(k) = 1005 / 645 = 1.5581.

This is deliberately a positive-token-balanced sampling intervention, not a pure chord-only intervention.

## Identity controls

Before optimizer work:
- freeze generated-array hashes;
- initialize both models identically;
- verify pre-update state/onset logits identical;
- precompute both 500-batch plans;
- assert the 96 non-positive indices in every paired batch are identical;
- freeze hashes for both batch plans;
- record positive-stratum multiplicity distribution for both arms.

## Required measurements

Report validation/test:
- pitch-onset TP/FP/FN, precision, recall, F1;
- onset+offset F1;
- repeated recall;
- family onset metrics, especially chord F1/recall;
- negative-only FP/sec;
- exact onset/state/joint admission;
- true-state/silence probability and margins;
- optimizer/runtime;
- data/init/batch hashes.

## Frozen S8 success criteria

All must pass:

1. chord onset F1 gain >= **+0.15**;
2. chord recall gain >= **+0.15**;
3. exact state-admission gain >= **+0.06**;
4. exact joint-admission gain >= **+0.05**;
5. overall onset recall gain >= **+0.04**;
6. overall onset F1 gain >= **+0.03**;
7. absolute state admission >= **0.42**;
8. absolute onset recall >= **0.65**;
9. absolute onset F1 >= **0.75**;
10. repeated recall >= **0.55**;
11. onset precision >= **0.82**;
12. onset+offset F1 decline <= **0.03**;
13. negative-only FP <= **0.10 events/s**;
14. no non-chord supported family loses > **0.15 F1**;
15. both models complete <=500 steps with finite metrics, identical data/init, paired identical non-positive batch indices, fixed thresholds, zero threshold search.

## Decision branches

- All pass: positive-frame token imbalance is supported as meaningful; stop and design a separate synthetic competence confirmation.
- Chord improves but global/state floors fail: token-balanced sampling helps polyphony but is insufficient.
- Precision/non-chord stability collapses: reject this weighting.
- Chord and state/joint do not materially improve: reject positive-frame multiplicity weighting.
- Any identity/runtime failure: freeze and stop, no automatic model retry.

## Hard ceiling if later authorized

- 294 clips / 588 s;
- exactly 2 models;
- 500 optimizer steps/model, 1,000 total;
- <=20 CPU minutes render;
- <=60 CPU minutes fit/eval;
- $0 paid compute;
- zero automatic model retries;
- no threshold tuning;
- no P1/P2/P3;
- no Codespaces;
- no Vercel;
- no deployment/main/customer delivery.

## Authorization boundary

S8 requires fresh explicit authorization before any model execution.
