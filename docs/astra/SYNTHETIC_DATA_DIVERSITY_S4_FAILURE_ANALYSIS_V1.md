# Astra S4 failure analysis V1

Date: 2026-09-27
Scope: offline review only. No model execution, rendering, optimizer work, threshold search, P1/P2/P3, Codespaces, or Vercel.

## Frozen S4 result

S4 validly isolated onset-loss gradient flow into the shared encoder.

Control:
- onset precision 0.8764
- recall 0.6047
- F1 0.7156
- onset+offset F1 0.5351
- repeated recall 0.5476
- exact onset admission 0.6279
- exact state/joint admission 0.3411

Detached-onset intervention:
- onset precision 0.4828
- recall 0.6512
- F1 0.5545
- onset+offset F1 0.3323
- repeated recall 0.6905
- exact onset admission 0.5581
- exact state/joint admission 0.3411

The state/joint bottleneck did not move. Precision collapsed and family stability deteriorated, so full onset-gradient detachment is rejected.

The repeated-recall gain is not a clean benefit because onset false positives rose from 11 to 90.

## What S2-S4 now imply

S2 changed state active-token weight 1.5 -> 6.0 and improved state/joint admission and event recall/F1.

S3 increased onset positive weight 8 -> 16. Exact onset admission increased, but event recall stayed flat and state/joint admission fell.

S4 removed onset-to-encoder gradients. State/joint admission stayed flat while onset precision/F1 collapsed.

Together, these results do not support further onset-weight escalation or full onset-gradient removal as the next lever.

They leave state-side silence dominance as the most directly supported remaining bounded hypothesis.

## State-token weighting geometry

Under the frozen 32/32/32/32 onset-aware sampler, expected active state-token share is about 10.4414%.

With active-state weight 6:
- expected active weighted state-loss share is about 41.16%.

The equal-mass crossover is at weight about 8.58.

Weight 9 is therefore the smallest integer weight that moves expected active state-token contribution just above half:
- expected active weighted state-loss share at weight 9 is about 51.20%.

This makes 6 -> 9 a smaller and more principled next intervention than jumping directly to 12 or changing architecture.

## Cross-experiment caution

S2, S3, and S4 used different deterministic initialization seeds. Their absolute metrics are useful context but are not controlled pairwise comparisons across experiments.

S5 must compare weight 6 versus 9 inside one run with identical initialization and identical minibatches.

## Chosen next hypothesis

Test **active-state loss weight only**:
- control = 6.0
- intervention = 9.0

Keep onset pos_weight 8, onset loss multiplier 4, the onset-aware sampler, five-frame architecture, learning rate, thresholds, decoder, and 500-step cap unchanged.

Hypothesis: residual state-silence imbalance is still materially limiting joint admission and event recall.

This remains unproven until a separately authorized S5 model run.
