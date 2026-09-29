# V5 Target-Structure Adequacy Result V1

Date: 2026-09-28  
Status: **COMPLETED — NO DEVELOPMENT-INTERESTING TARGET OBJECTIVE**

## What changed

V5 kept the model architecture, parameter count, R3 renderer, synthetic corpus, splits, initialization, batch plan, optimizer, step count, onset loss, thresholds, and ordinary decoder fixed.

Only state supervision changed:

- **T0:** exact string/fret objective
- **T1:** pitch-equivalent noisy-OR coverage + unsupported-state suppression
- **T2:** fixed 50/50 exact + pitch-equivalent objective

All three arms completed exactly **500 optimizer steps**. Total optimizer work was **1500/1500 authorized steps**.

## Synthetic sanity

| Arm | Precision | Recall | F1 | Negative FP/s | Eligible for V2B |
|---|---:|---:|---:|---:|---|
| T0 | 0.7647 | 0.6047 | 0.6753 | 0.000 | Yes |
| T1 | 0.6721 | 0.3178 | 0.4316 | 0.000 | **No** |
| T2 | 0.6981 | 0.5736 | 0.6298 | 0.000 | **Yes** |

T1 failed both frozen degradation limits:
- F1 decline vs T0: **−0.2437**
- recall decline vs T0: **−0.2868**

T2 passed:
- F1 decline: **−0.0455**
- recall decline: **−0.0310**

Therefore only T0 and T2 were eligible for the V2B gate.

## Protocol note

During the first helper implementation, T1 was inadvertently evaluated on V2B before the synthetic-sanity decision was applied.

That readout is **quarantined**:
- it is not used in the V5 result;
- T1 remains ineligible because of its independently frozen synthetic-sanity failure;
- no objective, threshold, gate, architecture, renderer parameter, or model choice was changed after seeing it.

The helper was then corrected so T2 was evaluated on synthetic sanity first and only reached V2B after passing.

## V2B development comparison

Compatible-pitch diagnostic admission used the frozen bounded noisy-OR state aggregation and compatible-string maximum onset probability. Thresholds remained **0.50 / 0.50**.

| Metric | T0 | T2 |
|---|---:|---:|
| Trusted joint admission | **0/56 (0%)** | **0/56 (0%)** |
| High-confidence joint admission | **0/49 (0%)** | **0/49 (0%)** |
| State admission | 3.57% | **8.93%** |
| Onset admission | 1.79% | 1.79% |
| Negative events | 5 | 10 |
| Negative FP/s | **0.1569** | **0.3139** |

T2 increases compatible state admission by about **+5.36 percentage points**, but it does not recover a single joint landmark because onset admission remains only **1/56**.

It also doubles negative false positives and remains far above the frozen **0.10/s** ceiling.

## Gate result

T2 required:
- trusted joint gain >= +0.20 absolute;
- high-confidence joint admission >=25%;
- negative FP <=0.10/s;
- onset admission decline <=0.10.

Observed:
- trusted joint gain: **0.00**
- high-confidence joint admission: **0%**
- negative FP: **0.3139/s**
- onset decline: **0.00**

**T2 fails the V5 development-interest gate.**

## Supported interpretation

Exact string/fret specificity is not sufficient to explain the transfer collapse.

Relaxing the state target does increase compatible state probability on real audio, so target structure has some measurable effect on the state branch. But the dominant real-domain failure remains joint admission—especially the onset branch—and negative selectivity.

The evidence now points away from:
- threshold calibration;
- simple affine frontend mismatch;
- bounded acoustic/capture realism;
- exact string/fret target specificity as a sole explanation.

The remaining problem is more consistent with deeper learned representation/task/data adequacy, especially real-domain onset representation and synthetic-to-real event statistics.

No causal isolation is claimed.

## Boundary

No V5C fresh holdout is warranted because no alternative objective passed V5B.

V1.1 remains sealed. P1/P2/P3 remain closed. A2 remains closed. Main/Production are unchanged.

The next project decision should target **onset representation / synthetic event-statistics adequacy** or a prospectively designed fresh real-domain training study, not additional target relaxation.
