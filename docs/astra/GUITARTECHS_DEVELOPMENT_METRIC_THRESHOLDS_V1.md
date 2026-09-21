# Guitar-TECHS Development Metric Thresholds V1

Date: 2026-09-21  
Candidate: `astra_guitartechs_tabcnn_v1`

## Why thresholds are frozen now

These thresholds are frozen **before Astra runs any real Guitar-TECHS model training**. They therefore cannot be tuned to a favorable Astra result.

The ICASSP 2025 Guitar-TECHS paper provides a directional external anchor. Its Table III reports, for the model trained with Guitar-TECHS included, tablature precision **0.809 ± 0.018**, recall **0.699 ± 0.048**, F1 **0.747 ± 0.031**, and TDR **0.905 ± 0.015**.

Astra does **not** claim those published metrics are directly equivalent to the stricter evaluator frozen here. The paper's validation design and tablature metrics differ from Astra's exact onset + physical-string + fret event metrics. The published values are used only to keep the preregistered floors in a plausible range rather than inventing targets from future Astra outputs.

## Evaluation population

Only the exact alignment-accepted primary set may enter development evaluation:

- 256 aligned capture paths;
- chords, scales, ordinary single notes and PalmMute only;
- exact accepted-set SHA-256 `f520f5ffe3daf44da9bad1d145adaa1c9ff0bb662141b027f85b8c7bc827eabc`;
- P3 excluded.

Correlated capture paths do not receive independent weighting. Metrics first average accepted views within each underlying performance, then macro-average performances.

## Exact metric definitions

Onset string/fret events are contiguous non-silent string/fret runs. A prediction matches a reference only when physical string and fret are exact and onset error is <=50 ms. Matching is one-to-one, maximizing match count and then minimizing total onset error.

Note-event completeness is duration-aware: temporal intersection of onset-matched exact-string/fret events divided by total reference-event duration.

Frame string/fret accuracy is measured only on the active-union frames for each string—frames where either reference or prediction is non-silent—so long silent regions cannot inflate the score.

Abstention rate measures eligible evaluation frames where an explicit guard produces no usable six-string state.

## Frozen acceptance thresholds

Every performer-disjoint fold must independently meet:

- onset string/fret precision >= **0.75**;
- recall >= **0.60**;
- F1 >= **0.67**;
- note-event completeness >= **0.60**;
- active-union frame string/fret accuracy >= **0.70**;
- abstention rate <= **0.10**;
- each primary content class onset string/fret F1 >= **0.55**.

Across both folds:

- macro onset string/fret F1 >= **0.70**;
- macro note-event completeness >= **0.65**;
- absolute cross-performer F1 gap <= **0.10**;
- absolute cross-performer frame-accuracy gap <= **0.10**.

Missing, non-finite or empty required metrics fail closed. A threshold failure blocks the development candidate and **does not authorize P3**.

## Checkpoint selection

Within each fold, select the validation checkpoint with highest onset string/fret F1 among checkpoints satisfying all hard gates that are computable at checkpoint time. Ties resolve by higher completeness, then lower abstention, then earlier checkpoint.

Threshold retuning after seeing real training results is forbidden.

Frozen receipt: `docs/astra/GUITARTECHS_DEVELOPMENT_METRIC_THRESHOLDS_V1.json`  
SHA-256: **`fba6c921f17ec2ba3bace55b50823ea33bbf7828b61c0705da78b48ac8cfbe15`**

This receipt authorizes no training, paid compute, P3 access, Production mutation or customer delivery.
