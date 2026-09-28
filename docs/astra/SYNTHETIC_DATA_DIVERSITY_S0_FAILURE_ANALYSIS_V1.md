# Astra S0 failure analysis V1

Date: 2026-09-27
Scope: offline review of frozen S0 code/results only. No rendering, optimizer work, threshold search, P1/P2/P3 access, or model rerun.

## Frozen evidence

S0 run 36369999876 / job 108764124344:
- five-frame model onset F1: 0.4235
- per-frame model onset F1: 0.1304
- five-frame recall: 0.2791
- five-frame precision: 0.8780
- repeated-note onset recall: 0.2143
- false positives on negative-only test audio: 0

The five-frame model clearly improved over the per-frame comparator, but the remaining errors were dominated by missed references: 93 FN versus 5 FP.

## Training-target sparsity from the frozen generator

The training split contains 210 clips x 87 frames x 6 string-onset targets = 109,620 binary onset positions.

The frozen templates create exactly 645 positive onset positions:
- isolated: 30
- scales: 120
- chords: 180
- repeated: 120
- legato: 30
- PalmMute: 150
- mixed: 15

Positive onset prevalence is therefore 645 / 109,620 = 0.5884%.

At the frame level, 525 of 18,270 training clip-frames contain at least one positive onset target = 2.8736%. The S0 optimizer sampled frames uniformly.

This makes sparse exposure to positive-onset frames a plausible bounded hypothesis. It is not proven to be the cause.

Other live explanations remain generator acoustics, state-head admission, fixed step budget, loss calibration, model capacity, and decoder admission.

## Chosen next hypothesis

Change only the minibatch sampling policy.

Keep the five-frame architecture, generator, split, loss weights, learning rate, thresholds, decoder, and 500-step cap unchanged. Compare:
- control: current uniform frame sampling;
- intervention: fixed onset-aware stratified frame sampling.

No threshold adjustment or extra-step rescue is part of the hypothesis.
