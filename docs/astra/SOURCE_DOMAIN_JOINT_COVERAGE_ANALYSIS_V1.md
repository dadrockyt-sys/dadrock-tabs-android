# Astra source-domain joint-coverage analysis V1

Date: 2026-09-28  
Status: **MODEL-FREE RESULT FROZEN — NO FOLLOW-ON MODEL AUTHORIZED**

## Result

The prospective joint-coverage review completed successfully with zero model activity:
- run **36477515197**
- job **109114818877**
- head `6d8a9e71e36b862ce7324088bb1e99c6ff4b7d99`
- **4 focused tests passed**
- artifact **10993409802**
- digest `sha256:bfb07fbae8cd7d2b1f59228362104abca0c55240cf89e388ef9ad1b94b77b56b`
- result SHA-256 `89ec82452ed3440af9d7935696f3bc66b0076c4c63c584b815780f9ea6f650ba`

No waveform was rendered. No model was loaded or run. Optimizer steps = 0. P1/P2/P3 were not accessed.

## Marginal coverage

The challenge is not outside the frozen one-dimensional parameter ranges. However, several challenge values lie in tails of the 210 deterministic training draws:

- attack rise 0.045 s: **96.2nd percentile**
- transient-noise gain 0.03: **13.8th percentile**
- damping 1.45: **79.0th percentile**
- brightness 0.60: **14.8th percentile**
- pick position 0.42: **85.2nd percentile**
- low-pass 3500 Hz: **11.4th percentile**
- spectral tilt -4 dB: **15.2nd percentile**
- broadband noise 0.001: **81.4th percentile**

Other challenge values are more central, including nonlinear drive/wet and high-pass corner.

## Joint coverage

Using the prospectively frozen challenge-side conjunction:

1. attack rise >= 0.045: **8 / 210** rows
2. plus transient-noise gain <= 0.03: **1 / 210**
3. plus damping >= 1.45: **0 / 210**
4–9. all later cumulative conjunctions remain **0 / 210**

No family has a training row satisfying the full nine-condition conjunction.

Therefore the challenge is **marginally in-range but jointly unrepresented** in the deterministic training sample.

This is a property of the V1 experimental design. It is not permission to oversample that exact corner after seeing the failed model result.

## Feature-space coverage

Pooled onset positive flux:
- intervention train median **20.658**
- challenge test median **12.749**
- median challenge-event percentile within intervention-training flux: **0.133**

Family median challenge flux percentiles:
- chords **0.267**
- isolated **0.033**
- legato **0.033**
- mixed **0.000**
- palmmute **0.143**
- repeated **0.108**
- scales **0.0125**

Thus most challenge attack frames lie near the low tail of the intervention-training onset-flux distribution.

Row-level mean absolute feature displacement:
- intervention train median **0.0410**
- challenge test median **0.0578**
- median challenge-row percentile: **0.833**

Family median challenge displacement percentiles range from **0.533** (mixed) to **0.967** (palmmute), with most families at or above approximately 0.85.

The challenge is therefore typically a larger representation shift while simultaneously producing lower attack flux.

## Relation to the failed training result

The source-domain-trained model increased challenge precision while reducing challenge recall in all seeds. The coverage result makes a joint train/challenge mismatch a supported **experimental-design limitation**: the fixed challenge combines several tail-like conditions in a way absent from training.

This does not prove the mismatch caused the model's precision/recall tradeoff. Other unresolved factors remain:
- source-domain randomization may make the fixed S11 model more conservative;
- legato ordinary regression indicates a family-specific robustness problem;
- architecture/loss/sampler inductive biases remain unresolved.

## Decision

Do not rescue V1 by:
- forcing training examples into the observed challenge corner;
- weakening the challenge;
- widening parameter ranges;
- changing threshold/loss/sampler;
- adding seeds;
- swapping architecture.

A scientifically defensible future protocol would need to be prospective and independently motivated. It should explicitly define **joint** source-domain coverage before training, rather than relying only on independent marginal draws, and it should separate simulator-coverage questions from architecture questions.

No new model experiment is justified automatically from this review.

## Resume instruction

Stop model execution. The next work, if continuing, is design-only: formulate an independent prospective experimental protocol for joint source-domain coverage, with no parameter values selected from the failed V1 scores. Keep P1/P2 closed and P3 sealed.
