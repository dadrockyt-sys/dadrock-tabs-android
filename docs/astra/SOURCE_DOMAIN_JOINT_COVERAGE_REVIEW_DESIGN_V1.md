# Astra source-domain joint-coverage review design V1

Date: 2026-09-28  
Status: **PROSPECTIVE MODEL-FREE REVIEW — NO TRAINING / NO PARAMETER CHANGES**

## Purpose

After source-domain training V1 failed its frozen scientific gate, quantify whether the fixed challenge occupies an unusual **joint combination** of the already-frozen source-domain simulator axes relative to the 210 intervention training rows.

This review is descriptive only. It may not select new simulator ranges, change the challenge, alter thresholds, or launch a model.

## Inputs

Use only:
- frozen source-domain simulator V1 parameter generator;
- frozen S9/control dataset identity;
- frozen source-domain intervention/challenge preparation artifact from run 36475263654 / artifact 10993531230.

No P1/P2/P3 data. No waveform rerender is required. No model loading/inference. Optimizer steps = 0.

## Parameter-space review

Reconstruct the exact deterministic source-domain parameter draw used for each of the 210 training rows.

For each numeric clip-level axis report:
- training minimum;
- training median;
- training maximum;
- fixed challenge value;
- empirical challenge percentile = fraction of training values <= challenge value.

Axes:
1. attackBaseRiseSeconds
2. transientNoiseGain
3. transientDecaySeconds
4. dampingMultiplier
5. brightness
6. pickPosition
7. lowpassCutoffHz
8. spectralTiltDb
9. highpassCornerHz
10. nonlinearDrive
11. nonlinearWet
12. broadbandNoiseRmsRelative

For booleans/categorical axes report training frequencies and the challenge state:
- nonlinearActive
- humActive
- humFundamentalHz

## Fixed challenge-side conjunction

Without changing any threshold after results, report how many training rows satisfy each cumulative condition in this exact order:

1. attackBaseRiseSeconds >= 0.045
2. transientNoiseGain <= 0.03
3. dampingMultiplier >= 1.45
4. brightness <= 0.60
5. pickPosition >= 0.42
6. lowpassCutoffHz <= 3500
7. spectralTiltDb <= -4.0
8. broadbandNoiseRmsRelative >= 0.001
9. nonlinearActive == true AND nonlinearWet >= 0.20

Report cumulative counts/fractions after condition 1, then 1+2, …, through all 9.

Repeat the final 9-condition conjunction count by musical family.

This conjunction is a descriptive representation of the fixed challenge's deliberately difficult direction. A count of zero does not imply the ranges should be widened.

## Feature-space review

Using only frozen prepared arrays:

### Onset positive flux

At every labeled attack frame f > 0:
`flux = sum(max(x[f] - x[f-1], 0))`.

For each family:
- intervention-training flux count/min/median/max;
- challenge-test flux count/min/median/max;
- for every challenge event, empirical percentile within the same-family intervention-training distribution;
- median challenge-event percentile.

Also report pooled values.

### Row-level prepared feature displacement

For every changed intervention training row:
`mean(abs(intervention_features - control_features))`.

For every changed challenge test row:
`mean(abs(challenge_features - control_features))`.

For each family:
- intervention-train displacement min/median/max;
- challenge-test displacement min/median/max;
- each challenge row's percentile within same-family intervention-train displacement;
- median challenge-row percentile.

Also report pooled values.

## Interpretation constraints

The review may state whether:
- challenge marginal values are central or tail-like;
- the exact challenge-side conjunction is common/rare/unseen among the 210 training draws;
- challenge feature shifts tend to lie inside or outside the empirical training-shift distribution.

It may not state that a new range, sampler, loss, threshold or architecture would solve the failure.

## Execution ceiling

- model loads 0
- inference 0
- optimizer steps 0
- waveform renders 0
- P1/P2/P3 access false
- CPU only
- <=10 minutes
- $0 paid compute
- no automatic retry
- no main/Production mutation

## Decision

Run this review once against the frozen artifact, save the exact result, and stop for interpretation.
