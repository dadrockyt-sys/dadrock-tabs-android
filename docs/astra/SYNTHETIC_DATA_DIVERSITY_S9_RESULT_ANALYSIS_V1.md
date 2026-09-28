# Astra S9 result analysis V1

Date: 2026-09-28
Scope: offline review only.

## S9 outcome

S9 is a formal gate failure, but it is the strongest positive controlled result in the current synthetic sequence.

The intervention changed only training chord voicing diversity:
- control: 10 unique voicings across 30 chord clips;
- intervention: 30 unique voicings across 30 chord clips;
- paired control timbre RNG keys preserved;
- validation/test and all non-chord data bit-identical;
- model initialization and batch indices identical.

Test changes:
- chord F1: 0.4906 -> 0.6769 (+0.1864)
- chord recall: 0.3611 -> 0.6111 (+0.2500)
- overall recall: 0.6047 -> 0.7364 (+0.1318)
- overall F1: 0.7123 -> 0.7917 (+0.0793)
- joint admission: 0.3256 -> 0.3953 (+0.0698)
- state admission: 0.3798 -> 0.4109 (+0.0310)
- repeated recall: 0.5238 -> 0.6429
- onset+offset F1: 0.6079 -> 0.6265
- precision: 0.8667 -> 0.8559

Fourteen of sixteen frozen criteria passed.

The only failures:
- state-admission gain required +0.05; observed +0.0310;
- absolute state admission required 0.42; observed 0.4109.

## Interpretation

Chord voicing diversity is supported as a meaningful synthetic-data contributor.

The intervention improves not just chord metrics but overall recall/F1 and joint admission while preserving precision and negative-only specificity.

However, the remaining bottleneck is still exact state identity.

The next experiment should not discard the successful 30-voicing dataset.

## Next bounded hypothesis

S6 showed that replacing the linear state head with a nonlinear 128-unit state-specific hidden layer improved state confidence/admission.

S9 shows that better chord diversity lifts the same state admission further to 0.4109.

A clean next test is therefore a small **identity-preserving state-head widening** on the diversified S9 dataset.

Control:
- state hidden width 128.

Intervention:
- state hidden width 192;
- first 128 hidden units exactly copy the control hidden layer;
- their output weights/bias contribution exactly copy control;
- the extra 64 hidden units use deterministic initialization;
- output weights from the extra 64 units initialize exactly zero.

Therefore control and intervention state logits are bit-identical before optimization, while the intervention has 64 learnable extra nonlinear state features.

Shared encoder/onset head, data, batches, loss weights, thresholds and optimizer budget remain identical.

This directly tests whether modest additional state-specific capacity can close the residual state-admission gap without sacrificing the S9 event gains.
