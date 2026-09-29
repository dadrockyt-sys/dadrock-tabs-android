# V4 Synthetic-to-Real Rendering Adequacy Result V1

Date: 2026-09-28  
Status: **COMPLETED — R3 IMPROVES FEATURE MATCH BUT FAILS TRANSFER GATE**

## V4A model-free renderer screen

Frozen arms were evaluated against V2B with no model inference.

| Arm | Median |SMD| | Bins |SMD|>=1 | Median Wasserstein | Range overlap | Advances |
|---|---:|---:|---:|---:|---|
| R0 | 0.86648 | 0.39063 | 0.20251 | 0.88758 | No |
| R1 | 0.86695 | 0.37500 | 0.19704 | 0.90179 | No |
| R2 | 0.79400 | 0.27604 | 0.18162 | 0.89874 | No |
| R3 | **0.69539** | **0.17188** | **0.15755** | **0.90728** | **Yes** |

R3 improvements vs R0:
- median |SMD|: **19.75%**
- fraction bins |SMD|>=1: **56.0%**
- median Wasserstein: **22.20%**
- range overlap improved by **0.01970 absolute**

Only R3 met every frozen V4A advancement condition.

## V4B bounded paired training

Exactly two models were trained:
- R0 baseline reproduction: 500 optimizer steps
- R3 renderer arm: 500 optimizer steps

Total: **1000 optimizer steps**, below the authorized 1500-step ceiling.

Both used:
- identical S9 nonlinear architecture;
- identical initialization;
- identical targets;
- identical precomputed batch indices;
- same optimizer/loss;
- no retry;
- no threshold search.

Runtime qualification:
- Python 3.13.5
- torch 2.10.0+cpu
- librosa 0.11.0
- numpy 2.3.5

This is a paired local-runtime experiment, not a historical-runtime reproduction.

## V4C V2B transfer test

At frozen 0.50/0.50 thresholds:

| Model | Trusted hits | High-confidence hits | Negative events | Negative FP/s |
|---|---:|---:|---:|---:|
| R0-trained | 0/56 | 0/49 | 13 | 0.4081 |
| R3-trained | 0/56 | 0/49 | 5 | 0.1569 |

R3 reduced negative false positives by about **61.5%** relative to same-run R0, but produced **no trusted landmark recovery**.

Frozen V4C gate required:
- >= +0.20 trusted joint-admission gain;
- >=25% high-confidence admission;
- <=0.10 negative FP/s.

R3 fails all complete gate requirements:
- trusted gain: **0.00**
- high-confidence admission: **0%**
- negative FP: **0.1569/s**

## Supported conclusion

Adding the bounded R3 realism package makes synthetic frontend statistics substantially more similar to V2B real audio and reduces negative false positives after synthetic retraining.

However, it does **not** restore pitch-landmark admission. Therefore the observed transfer collapse is not solved by this bounded rendering-realism package.

This weakens the hypothesis that missing simple acoustic/capture realism alone is the dominant cause. The remaining problem is more consistent with deeper synthetic task/representation inadequacy, target/label structure mismatch, or another higher-order model-domain interaction.

No causal isolation is claimed.

## Boundary

V4D does not run because no V4C renderer-trained model is development-interesting.

V1.1 remains sealed. P1/P2/P3 remain closed. A2 remains closed. Main/Production are unchanged.

The next project decision should focus on **representation/task adequacy**, not further renderer parameter search.
