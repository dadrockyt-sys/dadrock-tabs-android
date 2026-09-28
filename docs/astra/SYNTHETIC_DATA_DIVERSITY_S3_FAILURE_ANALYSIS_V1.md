# Astra S3 failure analysis V1

Date: 2026-09-27
Scope: offline result review only. No model execution, rendering, optimizer work, threshold search, P1/P2/P3 access, Codespaces, or Vercel use.

## Frozen S3 result

Run 36373550895 / job 108774667718 compared onset BCE positive weight 8 versus 16 under identical initialization and identical minibatch indices, with active-state weight fixed at 6.0.

Control pos_weight 8:
- test onset precision 0.9036
- test onset recall 0.5814
- test onset F1 0.7075
- repeated-note event recall 0.5714
- exact onset admission 0.5891
- exact state admission 0.3333
- exact joint admission 0.3333
- repeated-reference onset admission 0.5000

Intervention pos_weight 16:
- test onset precision 0.8721
- test onset recall 0.5814
- test onset F1 0.6977
- repeated-note event recall 0.5238
- exact onset admission 0.6744
- exact state admission 0.2868
- exact joint admission 0.2868
- repeated-reference onset admission 0.6212

## What changed

Increasing onset positive weight:
- increased exact onset admission by +0.0853;
- increased repeated-reference onset admission by +0.1212;
- did not change matched event recall;
- reduced event F1 by 0.0099;
- reduced state and joint admission by 0.0465;
- reduced repeated-note event recall by 0.0476.

The extra onset admissions therefore did not become extra correct decoded events.

## Rising-edge hypothesis is not the leading explanation

For repeated references, preceding-frame onset probability remained low:

- control mean 0.0297;
- intervention mean 0.0333;
- intervention maximum stayed below the frozen 0.50 onset threshold.

That means the decoder's same-fret rising-edge plateau rule was generally presented with a below-threshold preceding frame at these references. The S3 evidence does not support plateau suppression as the dominant repeated-note bottleneck.

## Shared-encoder coupling is now a bounded hypothesis

The five-frame model has one shared encoder feeding both the state and onset heads.

S2 showed that strengthening the state objective improved state/joint admission and event recall.

S3 showed that strengthening the onset objective increased onset admission while state/joint admission moved in the opposite direction, with no event-recall gain.

This pattern is **compatible with** negative transfer / gradient competition in the shared encoder. It is not proof: different initialization, finite optimization, generator acoustics, and head calibration remain possible explanations.

The next controlled intervention should therefore change only whether the onset loss is allowed to update the shared encoder.

## Chosen next hypothesis

Keep the strongest current development configuration from the S3 control:

- five-frame shared encoder;
- active-state weight 6.0;
- onset pos_weight 8;
- onset loss multiplier 4.0;
- onset-aware 32/32/32/32 sampler;
- lr 0.003;
- thresholds 0.50 / 0.50;
- decoder V2;
- 500 optimizer steps/model.

Compare:

1. **control:** ordinary multitask backpropagation; state and onset losses both update the shared encoder.
2. **intervention:** state loss updates the shared encoder, while the onset head receives a detached encoder representation. The onset head itself still trains; only onset-to-encoder gradient flow is blocked.

This changes one training-coupling variable without changing parameter count, forward architecture, data, sampler, thresholds, loss weights, or optimizer budget.
