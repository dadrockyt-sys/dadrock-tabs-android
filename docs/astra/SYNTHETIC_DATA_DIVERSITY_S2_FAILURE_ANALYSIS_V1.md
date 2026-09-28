# Astra S2 failure analysis V1

Date: 2026-09-27
Scope: offline analysis only. No rendering, optimizer work, threshold search, P1/P2/P3 access, or model rerun.

## Frozen S2 outcome

Corrected S2 run 36372725350 / job 108772201562 compared active-state weight 1.5 versus 6.0 under identical generated arrays, identical initialization, and an identical 500-minibatch plan.

Weight 6.0 improved:
- state admission: 0.2403 -> 0.3101 (+0.0698)
- joint admission: 0.2403 -> 0.3023 (+0.0620)
- onset recall: 0.4574 -> 0.5581 (+0.1008)
- onset F1: 0.6243 -> 0.67925 (+0.0549)
- onset+offset F1: 0.4767 -> 0.5561 (+0.0794)

But the frozen S2 gate failed. In particular:
- state/joint gains were below +0.20;
- absolute onset F1 was 0.67925 < 0.68;
- repeated-note recall remained 0.5000.

Weight 6.0 therefore helps but is not a sufficient state-side repair.

## Remaining onset evidence

At exact positive test reference string/frames, the S2 control and weight-6 arms had essentially unchanged onset admission:

- control onset admission: 0.5736
- weight-6 onset admission: 0.5736

The weight-6 intervention moved state admission but did not move exact onset admission. Repeated-note recall also remained exactly 0.5000.

This leaves missed onset admission as a live independent bottleneck after the state-side intervention.

## Effective onset class balance under the frozen sampler

The frozen training split has:
- 525 positive-onset clip-frames;
- 645 positive string/onset tokens across those frames;
- mean positive strings per positive-onset frame = 645 / 525 = 1.228571.

The S1/S2 onset-aware sampler fixes 32 positive-onset frames in each 128-frame batch.

Expected positive string/onset tokens per batch:
- 32 x 1.228571 = 39.3143.

Total string/onset tokens per batch:
- 128 frames x 6 strings = 768.

Expected positive onset-token share:
- 39.3143 / 768 = 5.119%.

With ordinary negative token weight 1:
- current BCE pos_weight 8 gives positive tokens about 30.15% of expected weighted onset-loss mass;
- pos_weight 16 gives positive tokens about 46.33% of expected weighted onset-loss mass.

This calculation uses frozen target/sampler counts only. It is not a model rerun.

## Chosen next hypothesis

Test **onset positive-token BCE weight only**.

Keep the better S2 state-side setting (active-state weight 6.0) and the S1 onset-aware sampler fixed.

Compare two otherwise identical models:
- control onset pos_weight = 8;
- intervention onset pos_weight = 16.

Do not change:
- generated corpus or split;
- five-frame architecture;
- state active weight 6.0;
- sampler or sampled minibatch indices;
- onset loss multiplier 4.0;
- learning rate 0.003;
- thresholds 0.50 / 0.50;
- decoder V2;
- 500-step/model budget.

The hypothesis is that remaining onset-positive underweighting contributes to low exact onset admission and repeated-note/event recall.

This remains unproven until a separately authorized controlled S3 run.
