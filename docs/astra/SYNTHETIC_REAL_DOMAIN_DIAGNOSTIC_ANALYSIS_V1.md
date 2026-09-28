# Astra synthetic/real domain diagnostic analysis V1

Date: 2026-09-28

## Outcome

The authorized zero-optimizer diagnostic completed successfully.

- run: 36386315576
- job: 108812332904
- artifact: 10955243031
- optimizer steps: 0
- model weights changed: no
- threshold search: no
- P1 accessed: yes
- P2 accessed: yes
- P3 opened: no

## Raw feature-domain evidence

Synthetic features have higher mean/RMS energy than either real population:

- synthetic mean/std/RMS: 0.1823 / 0.2297 / 0.2932
- P1: 0.1439 / 0.2111 / 0.2555
- P2: 0.1383 / 0.1998 / 0.2430

Centroid distance:
- synthetic -> P1: L2 1.1617, cosine distance 0.0740
- synthetic -> P2: L2 1.1906, cosine distance 0.0833
- P1 -> P2: L2 0.6698, cosine distance 0.0381

There is a real synthetic-to-real feature shift, and P1/P2 are materially closer to each other than either is to synthetic.

## Candidate reference-frame behavior

Exact admission:

Synthetic candidate:
- onset 0.6744
- state 0.3256
- joint 0.3101

P1 candidate:
- onset 0.0625
- state 0.0000
- joint 0.0000

P2 candidate:
- onset 0.0000
- state 0.2667
- joint 0.0000

This is not one uniform failure mode.

### P1

The candidate loses both attack admission and exact pitch-state identity.

At true reference frames:
- mean onset probability falls from 0.6583 synthetic to 0.0748 P1;
- mean true-state probability falls from 0.3355 to 0.0305;
- mean silence probability rises from 0.4725 to 0.7171.

The historical V3 baseline remains healthy on P1:
- onset admission 0.625
- state admission 0.625
- joint admission 0.5625

Therefore the P1 candidate failure is candidate-specific representation/domain mismatch, not simply bad real P1 preprocessing.

### P2

Both frozen models show:
- onset admission 0.0000
- state admission 0.2667
- joint admission 0.0000

That makes onset/attack localization the immediate shared P2 bottleneck.

The candidate retains some correct state identity on P2, particularly in the scale crop, but does not fire usable onset evidence at the annotated attacks.

## Important non-calibration finding

The candidate is not globally suppressed on real inputs.

Global candidate onset-probability mean:
- synthetic 0.0119
- P1 0.0519
- P2 0.0241

Global candidate best-active probability is also higher on real data than synthetic.

So simply lowering thresholds would be scientifically unjustified: activation exists, but it is misplaced relative to true reference events.

## Conclusion

Freeze the diagnosis as **mixed feature-domain and representation-alignment failure**:

1. measurable synthetic-to-real input shift exists;
2. candidate P1 failure includes severe state-identity collapse;
3. P2 failure is immediately dominated by onset/attack localization for both models;
4. global threshold/calibration rescue is contradicted by the spatial/temporal mislocalization evidence.

Do not:
- threshold-rescue;
- z-score/normalize model inputs post hoc;
- seed-pick;
- tune on the eight real crops;
- open P3.

The next defensible diagnostic is zero-training localization of:
- P1 pitch/state error geometry;
- P2 onset timing/attack novelty geometry.
