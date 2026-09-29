# V2C Calibration Diagnostic Result V1

Date: 2026-09-28  
Status: **COMPLETED — NO CALIBRATION CANDIDATE**

## What was run

V2C was explicitly authorized and executed only on the fresh V2B calibration-development set.

Frozen candidate:
- S9 30-voicing intervention
- checkpoint SHA-256 `8428e7ced49331153e5bd3a038115235c06aac483dab6f82fbc0257d07dd5036`

Frozen grid:
- state thresholds: 0.20, 0.30, 0.40, 0.50
- onset thresholds: 0.20, 0.30, 0.40, 0.50
- exactly 16 pairs

Eligibility rule frozen before output:
- negative false-positive rate <= **0.10 events/s**
- among eligible pairs, maximize trusted high+medium landmark hit rate
- then fewer negative events
- then higher state threshold
- then higher onset threshold

V1.1 was not used for threshold selection.

## Preflight correction

One high-confidence C06 landmark at MIDI 37 was discovered to be outside the pinned six-string model's representable output range.

It was excluded as **unscorable**, not counted as a miss.

Scorable V2B pitch landmarks:
- **56 high+medium total**
- **49 high-confidence**
- **7 medium-confidence**

The correction was frozen before any grid metric was produced.

## Historical 0.50 / 0.50 diagnosis

At the 56 true, representable pitch landmarks:

- joint state+onset pass: **0 / 56**
- state-gate failure only: **2 / 56**
- onset-gate failure only: **1 / 56**
- both gates fail: **53 / 56 (94.64%)**

Raw probability summaries at true landmarks:

| Quantity | Median | Mean | Maximum |
|---|---:|---:|---:|
| Max compatible active-state probability | **1.33e-9** | 0.03445 | 0.63777 |
| Max compatible onset probability | **5.23e-14** | 0.03462 | 0.88764 |

This is a severe admission/domain mismatch, not a small threshold offset.

At 0.50/0.50:
- trusted landmark hits: **0 / 56**
- high-confidence hits: **0 / 49**
- negative false positives: **14 in 31.858 s**
- negative FP rate: **0.4395 events/s**

All 14 baseline negative events occurred on D02 (Ancient War Drums).

## Frozen grid outcome

No one of the 16 threshold pairs met the <=0.10 events/s negative-FP constraint.

The most permissive 0.20/0.20 pair:
- trusted hits: **1 / 56 (1.79%)**
- high-confidence hits: **0 / 49**
- negative false positives: **38**
- negative FP rate: **1.193 events/s**

All pairs with onset threshold >=0.30 produced **0 trusted landmark hits**.

The three pairs with onset threshold 0.20 and state threshold 0.20/0.30/0.40/0.50 produced only **1 / 56** hits each, and none of those hits was high-confidence.

## Result

**V2C selects no calibration candidate.**

Lowering the frozen thresholds does not recover useful real-guitar landmark admission. It mainly increases false positives on negative audio.

The evidence therefore does not support a simple threshold-calibration explanation for the observed transfer failure.

## What this suggests

Within the current local runtime, the dominant issue is more consistent with:
- representation/domain mismatch;
- frontend-to-model distribution mismatch;
- synthetic-to-real feature mismatch;
- or another upstream transfer failure,

rather than thresholds merely being too conservative.

This does not isolate which of those mechanisms is causal.

The historical-runtime mismatch remains unresolved because V2A was infrastructure-blocked.

## Boundaries preserved

No:
- training;
- fine-tuning;
- decoder change;
- frontend change;
- gain experiment;
- candidate reselection;
- V1.1 tuning use;
- P1/P2/P3;
- A2;
- main/Production mutation.

## Decision boundary

V2D should **not** run because V2C produced no eligible calibration pair to confirm.

The next scientifically useful project would need to diagnose the upstream representation/frontend/domain mismatch on a fresh, prospectively designed experiment rather than continuing to lower thresholds.
