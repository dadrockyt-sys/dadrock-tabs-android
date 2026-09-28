# Synthetic S13 positive-increment robustness design V1

Date: 2026-09-28
Status: **PROSPECTIVE DESIGN FROZEN — NO MODEL EXECUTION YET**

## Question

With the frozen S9/S11 model, clean corpus, sampler, optimizer, decoder, thresholds and seeds unchanged, does a **fixed family-balanced mixture of clean and positive-onset-increment-compressed training views** improve robustness to a prospectively corrected soft-onset representation challenge while preserving ordinary synthetic state/joint competence?

This is a synthetic representation-robustness experiment only. It is not a physical guitar/capture simulator and is not a real-domain validation.

## Prior model-free admission review

The only intervention transform admitted for S13 is the separately reviewed **positive-onset-increment compression** in:
- `docs/astra/SYNTHETIC_S13_TRANSFORM_DESIGN_REVIEW_V1.md`;
- `astra_backend/synthetic/s13_transform_design_review_v1.py`.

Focused model-free run **36456672322** passed **17 tests** with zero optimizer steps.

The admitted transform:
- changes only positive frame-to-frame increments at labeled onset frames;
- leaves flat/decreasing bins unchanged;
- does not modify the following frame;
- uses immutable source values, so adjacent onsets do not recursively couple;
- is not string-source-selective.

The previous S12 recursive frame-wide softening remains rejected and is not reused for S13 training or challenge construction.

## Single intervention

The intervention is one fixed data-view package only. There is:
- no new loss;
- no consistency objective;
- no architecture change;
- no sampler change;
- no decoder change;
- no threshold change.

For each selected training row and each labeled onset frame `f > 0`:

`positive_delta = max(x[f] - x[f-1], 0)`

`x_soft[f] = x[f] - 0.5 * positive_delta`

Thus the retain fraction is exactly **0.50**.

All other frames and arrays remain bit-identical.

### Training-row mixture

Keep clean examples present without changing row count or minibatch indices.

Within each synthetic family independently:
1. take training-row indices only;
2. rank them by SHA-256 of the UTF-8 string `astra-s13-soft-subset-v1|<rowIndex>`;
3. transform exactly `floor(n_family / 2)` lowest-ranked rows;
4. leave all remaining training rows clean.

Therefore the intervention changes approximately half of training clips in each family, with no stochastic choice at execution time and no dependence on P1/P2/P3.

Validation and ordinary test features are untouched.

## Corrected synthetic challenge

Construct a third evaluation-only dataset from the clean control corpus.

For **every test row only**, apply the admitted transform with retain fraction **0.50** at every labeled onset frame. Training and validation features remain clean. All state, onset, references, family, split and negative-structure arrays remain bit-identical.

This corrected challenge replaces the S12 recursive challenge for S13. Absolute S12 challenge scores are therefore not directly comparable to S13 challenge scores. The S12 numerical benefit floors are retained as minimum S13 gates, but no claim of an untouched confirmation set is allowed.

## Control

Frozen S9/S11 diversified synthetic path:
- 294 clips;
- same S9 diversified dataset construction;
- same S11 model;
- same labels and references;
- same train/validation/test membership.

## Model and training — unchanged

- 5-frame / 960-feature input via frozen `context5`;
- shared encoder Linear(960,128) -> ReLU;
- state head Linear(128,128) -> ReLU -> Linear(128,126);
- onset head Linear(128,6);
- state active weight 9.0;
- onset positive weight 8.0;
- onset loss multiplier 4.0;
- frozen onset-aware 32/32/32/32 sampler;
- Adam learning rate 0.003;
- batch size 128;
- exactly 500 optimizer steps/model;
- decoder V2;
- state threshold 0.50;
- onset threshold 0.50;
- threshold search/retuning: none.

Seeds exactly:
- 20260927
- 20260928
- 20260929

Within each seed:
- control/intervention initial weights must be byte-identical before update;
- clean minibatch row indices must be identical;
- transformed subset is fixed globally by the hash rule above and has no execution RNG.

Exactly six trained models / 3,000 optimizer steps total.

## Required evaluation

For each seed report absolute control and intervention results on:

### Ordinary clean test
- pitch-plus-onset TP / FP / FN;
- precision / recall / F1;
- onset+offset F1;
- repeated-reference attack recall;
- every family pitch-plus-onset F1;
- state-admission fraction;
- joint-admission fraction;
- negative-only false positives and seconds;
- negative-only FP events/sec.

### Corrected challenge test
Report the same absolute metrics and denominators.

Report paired intervention-minus-control deltas after absolute values.

## Frozen S13 gate

Every criterion must pass.

### Corrected-challenge robustness
1. pitch-onset F1 delta > 0 in 3/3 seeds;
2. pitch-onset recall delta > 0 in 3/3 seeds;
3. mean pitch-onset F1 gain >= +0.05;
4. mean pitch-onset recall gain >= +0.08;
5. no seed challenge precision loss > 0.05;
6. intervention challenge negative-only FP <= 0.10 events/sec in every seed.

### Ordinary-domain preservation
7. no seed ordinary pitch-onset F1 loss > 0.03;
8. no seed ordinary pitch-onset precision loss > 0.03;
9. no seed ordinary state-admission loss > 0.03;
10. no seed ordinary joint-admission loss > 0.04;
11. intervention ordinary negative-only FP <= 0.10 events/sec in every seed;
12. no ordinary non-chord family loses > 0.15 F1 in more than one seed.

### Identity/runtime admission
13. all non-feature arrays are bit-identical across control, intervention and challenge;
14. intervention validation/test features equal control exactly;
15. challenge train/validation features equal control exactly;
16. transformed row set exactly matches the frozen per-family hash rule;
17. every transformed onset obeys the positive-increment formula and all non-rising bins remain exact;
18. paired initialization and batch indices match within seed;
19. all required per-seed/per-arm metrics are finite;
20. all six models complete exactly 500 optimizer steps;
21. model count = 6 and total optimizer steps = 3,000;
22. thresholds remain 0.50/0.50 with zero search or retuning;
23. no automatic retry and no reused launch identity.

`s13GatePassed` is true only if all 23 criteria are true.

## Hard ceiling

- CPU-only GitHub Actions;
- <= 6 trained models;
- <= 500 optimizer steps/model;
- <= 3,000 optimizer steps total;
- <= 90 fit/eval CPU minutes;
- one launch attempt only;
- no automatic retry;
- $0 paid compute;
- no external/corpus audio acquisition;
- no P1/P2/P3 access;
- no Codespaces;
- no Vercel;
- no main/Production mutation.

## Execution-control requirements before launch

Implementation must:
- refuse any existing evidence/output path;
- use a unique launch/run directory;
- reject GitHub run attempts > 1;
- reject a launch identity already present in the durable execution receipt/history;
- use read-only repository permissions;
- validate branch, launch/spec identities and complete imported source dependency pins before expensive work;
- save a failure receipt on any closed failure path;
- upload partial diagnostics with an always-run artifact step;
- never delete old evidence to make a run fit;
- assert the corrected challenge's train/validation features are unchanged at execution entry.

## Decision

- **Pass:** synthetic development evidence that the admitted nonrecursive transform can improve robustness without exceeding frozen ordinary-domain regressions. Stop; do not automatically evaluate P1/P2/P3 or promote anything.
- **Fail:** freeze failure and perform project-level simulator/representation review before another model experiment. No automatic S14.
- **Identity/runtime failure:** freeze as execution failure; fix only concrete implementation defects under a newly verified source identity. Do not weaken the scientific gate.

P1/P2 remain closed development data. P3 remains sealed.
