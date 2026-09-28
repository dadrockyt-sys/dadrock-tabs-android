# Astra S11 robustness analysis V1

Date: 2026-09-28
Scope: offline interpretation of the frozen three-seed paired robustness run.

## What reproduced

The 30-voicing intervention beat the 10-voicing control in all three seeds for:
- chord F1;
- chord recall;
- overall onset F1;
- overall onset recall.

That means the direction of the diversity effect is not a one-seed artifact.

Paired mean gains:
- chord F1 +0.0649;
- chord recall +0.1019;
- overall onset F1 +0.0190;
- overall onset recall +0.0543;
- state admission +0.0258.

## What did not reproduce robustly enough

The preregistered mean-effect floors were intentionally higher:
- chord F1 required +0.10;
- chord recall required +0.12;
- onset F1 required +0.04;
- onset recall required +0.06;
- joint admission required +0.03.

Observed mean joint-admission gain was only +0.0026.

One seed lost 0.1185 precision, exceeding the allowed 0.05 loss.

Therefore S11 fails the robustness gate.

## Scientific interpretation

Chord-voicing diversity is a **directionally consistent but magnitude-unstable** improvement under the current synthetic training system.

It is fair to retain these conclusions:
1. diversity is better than simply replaying the same ten chord voicings more often;
2. the improvement direction appears across the three tested seeds;
3. the current optimizer/model/data regime is still too initialization-sensitive to call the integrated synthetic result robust;
4. exact state/joint admission remains unresolved.

It is not justified to keep adding hidden width, loss weights, sampler variants or more synthetic chord tweaks after this result. That would turn the sequence into open-ended tuning on the same development split.

## Frozen stop

Close the S0-S11 synthetic tuning sequence here.

P3 remains sealed.

P1/P2 real-development transfer has not been accessed and is not authorized by the standing inexpensive synthetic-run policy.

The next scientifically meaningful boundary is a separately scoped P1/P2 transfer evaluation proposal, with no threshold tuning and no automatic return to synthetic hyperparameter search.
