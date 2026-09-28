# Astra S7 failure analysis V1

Date: 2026-09-28
Scope: offline review only.

## Frozen S7 result

The residual branch began as an exact no-op: shared encoder, onset head, base linear state head, state logits and onset logits were bit-identical before optimization.

After 500 steps its residual parameter norm was 17.6719, so the branch learned rather than remaining inactive.

Yet versus the identical linear control:
- state admission: 0.3256 -> 0.2946 (-0.0310)
- joint admission: 0.3178 -> 0.2868 (-0.0310)
- onset recall: unchanged at 0.5969
- onset F1: 0.7230 -> 0.7130
- repeated recall: 0.5714 -> 0.5952
- median true-state probability: 0.1382 -> 0.0503
- median silence probability: 0.6562 -> 0.8106

S7 therefore rejects adding nonlinear residual capacity beside the direct linear state shortcut.

## Cross-run signal

S6 replacement nonlinear state head improved state admission and state confidence. S7's residual version did the opposite. The evidence does not justify deeper residual state architecture.

Across recent controlled runs, the chord family remains the clearest persistent weak family. S7 control chord onset F1 was 0.383 while most monophonic families were much higher.

## Frozen training-frame accounting

The deterministic train split contains 30 clips per family except mixed positives are present only for odd base templates.

Positive-onset frame counts:
- isolated: 30
- scales: 120
- chords: 60
- repeated: 120
- legato: 30
- palmmute: 150
- mixed: 15
- total: 525

Positive string-onset token counts:
- isolated: 30
- scales: 120
- chords: 180
- repeated: 120
- legato: 30
- palmmute: 150
- mixed: 15
- total: 645

Chords therefore represent:
- 60 / 525 = 11.43% of positive onset frames;
- 180 / 645 = 27.91% of positive string-onset tokens.

The current positive-onset stratum samples frames uniformly, so simultaneous multi-string attacks are underrepresented relative to the number of supervised positive string tokens they carry.

## Chosen next hypothesis

Use the S6 replacement nonlinear state head as the fixed architecture, because it was the only recent architectural intervention to materially improve state admission.

Change only the sampling probability **within the existing 32-positive-onset-frame stratum**:

- control: uniform over positive-onset frames;
- intervention: probability proportional to the number of positive onset strings in the frame.

The other 96 frames per batch remain the same 32 active-non-onset / 32 negative-structure-inactive / 32 other-inactive strata.

This is a token-balanced positive-frame sampler. It intentionally gives multi-string attack frames more representation without changing corpus, batch size, number of positive frames, loss weights, architecture, thresholds or optimizer budget.

Because weighted frame sampling also raises the expected number of positive string tokens seen in those 32 frames, S8 tests the combined hypothesis that frame-uniform sampling underweights multi-string positive supervision. It must not be described as a pure chord-only causal test.
