# Astra synthetic-to-real domain diagnostic proposal V1

Date: 2026-09-28
Status: **DESIGN ONLY — NEW P1/P2 ACCESS NOT AUTHORIZED**

## Question

Why does the frozen synthetic candidate achieve useful synthetic metrics yet produce zero true positives on both real P1 and P2?

## Scope

No training and no threshold changes.

Compare three fixed populations:
1. frozen synthetic S9/S11 test split;
2. exact four P1 prepared crops;
3. exact four P2 prepared crops.

Models:
- frozen V3 baseline;
- frozen failed-transfer candidate from run 36381769369.

## Measurements

For each population/model:
- CQT feature mean/std/RMS and per-bin quantiles;
- encoder hidden activation mean/std/sparsity;
- onset probability/logit distributions;
- best-active-state vs silence probability margins;
- true-reference fret probability and rank where references exist;
- exact onset/state/joint admission at reference frames;
- decoded event count and pitch histogram;
- cosine/L2 distance between population feature centroids;
- simple fixed z-score normalization *diagnostic only* may be reported as transformed statistics, but must not be fed through the model in this diagnostic.

## Critical guards

- optimizer steps: 0;
- model weights frozen;
- thresholds remain 0.50 / 0.50;
- no threshold search;
- no seed/model selection;
- no P3;
- no production claim;
- no automatic retry;
- no new synthetic tuning from P1/P2 metrics.

## Decision branches

- **Large feature-domain shift before encoder:** investigate synthetic generator/preprocessing realism offline without using P1/P2 for model tuning.
- **Feature statistics overlap but hidden/state/onset geometry diverges:** representation/training objective mismatch is more likely.
- **Onset admission healthy but state identity fails:** prioritize pitch/state representation diagnosis.
- **State identity healthy but onset fails:** prioritize attack representation diagnosis.
- **Mixed:** freeze as mixed; do not tune on eight examples.

## Authorization boundary

The completed transfer authorization is consumed.

Any new P1/P2 media access for this diagnostic requires fresh explicit authorization.

P3 remains sealed.
