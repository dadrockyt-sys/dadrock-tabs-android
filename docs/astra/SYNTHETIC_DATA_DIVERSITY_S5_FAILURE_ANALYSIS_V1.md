# Astra S5 failure analysis V1

Date: 2026-09-27
Scope: offline review only. No model execution, rendering, optimizer work, threshold search, P1/P2/P3, Codespaces, or Vercel.

## Frozen S5 result

S5 compared active-state weight 6 versus 9 under identical generated arrays, initialization and minibatches.

Weight 6:
- onset precision 0.9059
- recall 0.5969
- F1 0.7196
- onset+offset F1 0.4821
- repeated recall 0.5952
- onset admission 0.5659
- state admission 0.3333
- joint admission 0.3178

Weight 9:
- onset precision 0.8901
- recall 0.6279
- F1 0.7364
- onset+offset F1 0.5470
- repeated recall 0.6190
- onset admission 0.6124
- state admission 0.3333
- joint admission 0.3333

The intervention improved several event metrics but produced no exact state-admission gain. Seven of fourteen preregistered criteria passed.

## Why another state-weight increase is not justified

Weight 9 was chosen as the smallest integer above the approximate equal-mass crossover for active versus inactive weighted state-loss contribution.

Despite crossing that point:
- exact state admission remained exactly 0.3333;
- true-state probability at positive test references had median 0.1478;
- silence probability had median 0.5387;
- true-minus-silence margin had median -0.3248;
- strongest incorrect active-state probability had median only 0.0395.

This pattern means silence often dominates the correct fret, while confusion among active frets is usually smaller. More weighting alone did not change the admission fraction.

The evidence therefore supports stopping automatic state-weight escalation.

## Bounded next hypothesis

The current state branch is only a linear projection from the 128-dimensional shared encoder to 6 x 21 state logits.

A bounded next hypothesis is that **state-specific nonlinear capacity** is insufficient after the shared encoder.

Test one architectural variable:

- control state head: Linear(128, 126)
- intervention state head: Linear(128,128) -> ReLU -> Linear(128,126)

Keep the shared encoder, onset head, onset-aware sampler, state weight 9, onset pos_weight 8, onset loss multiplier 4, learning rate, thresholds, decoder and optimizer budget fixed.

This adds state-head capacity only. It does not alter temporal context, the onset branch, decoder, or thresholds.

## Identity caveat

Because the state-head architectures differ, whole-model initial logits cannot be identical.

A future S6 run must instead:
- initialize and hash the shared encoder identically across arms;
- initialize and hash the onset head identically across arms;
- verify pre-update onset logits are exactly identical;
- use identical data and minibatches;
- report parameter counts explicitly.

State-output differences before training are inherent to the architectural intervention and must not be hidden.
