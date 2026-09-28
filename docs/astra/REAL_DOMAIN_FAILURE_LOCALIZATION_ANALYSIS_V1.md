# Astra real-domain failure localization analysis V1

Date: 2026-09-28

## Outcome

The authorized zero-training localization run completed successfully:

- run 36392740663
- job 108832021154
- artifact 10957888924
- optimizer steps 0
- thresholds fixed 0.50 / 0.50
- no weight changes
- no normalization fed to models
- P3 remained sealed

## P1: candidate state representation is not real-domain compatible

Historical V3 baseline state geometry:
- exact string/fret top-1: 56.25%
- pitch-only top-1: 56.25%
- median absolute semitone error: 0
- median global true-state rank: 1
- true class in top-5: 87.5%
- mean true-state probability: 0.6068

Synthetic candidate:
- exact string/fret top-1: 6.25%
- pitch-only top-1: 31.25%
- wrong-string/correct-pitch top-1: 25%
- median absolute semitone error: 11.5 semitones
- median global true-state rank: 13.5
- true class in top-5: 31.25%
- mean true-state probability: 0.0305
- mean silence probability: 0.7171

This is not primarily a string-assignment mistake. Some pitch information survives on the wrong string, but the dominant pattern is diffuse state/pitch misrepresentation on real P1 inputs.

## P1 onset evidence

The same P1 attack frames are easy for the historical baseline:
- reference onset probability mean 0.6316
- threshold crossing within +/-1 frame: 100%

The candidate:
- reference onset probability mean 0.0748
- threshold crossing within +/-1 or +/-4 frames: 18.75%

So the candidate has both onset and state representation failure on P1.

## P2: not a small timing offset

Historical baseline P2:
- onset probability at reference mean 0.0049
- max within +/-4 frames mean 0.0190
- threshold crossing within +/-4 frames: 0%

Candidate P2:
- onset probability at reference mean 0.0441
- max within +/-4 frames mean 0.0642
- threshold crossing within +/-4 frames: 0%

Median local-max offsets are only 0-1 frame.

Therefore P2 failure is not explained by a small annotation/model timing offset.

## P2 attack-domain evidence

Attack novelty is weaker on P2:

Mean positive spectral flux:
- synthetic, k=1: 26.54
- P1, k=1: 14.42
- P2, k=1: 8.51

Mean frame-difference L2, k=1:
- synthetic: 2.923
- P1: 1.972
- P2: 1.419

This supports a P2 attack-domain mismatch: the reference attacks present substantially weaker spectral novelty than the synthetic training attacks and the P1 examples.

Because both the P1-trained V3 baseline and the synthetic candidate fail P2 onset admission, this shared bottleneck is more consistent with the P2 attack/capture domain than with one model's decoder.

## Conclusion

Two mechanisms are now localized:

1. **P1 candidate:** real-domain state/pitch representation collapse, with accompanying onset weakness.
2. **P2 both models:** attack/onset-domain mismatch, not a small timing offset.

Do not lower thresholds, retune on the eight crops, seed-pick, or open P3.

A next diagnostic should audit raw P2 attack/preparation integrity without training: waveform/transient energy around annotations, CQT preprocessing consistency, and source-to-prepared timing alignment.
