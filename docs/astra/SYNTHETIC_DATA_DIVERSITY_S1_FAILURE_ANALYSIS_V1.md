# Astra S1 failure analysis V1

Date: 2026-09-27
Scope: offline analysis only. No rendering, optimizer work, threshold search, P1/P2/P3 access, or model rerun.

## Frozen S1 outcome

Run 36370848921 / job 108766686822 completed successfully as a workflow but failed the frozen S1 scientific gate because absolute test onset recall was 0.4651 versus the required 0.55.

The onset-aware intervention nevertheless improved:
- onset F1 from 0.3226 to 0.6283;
- onset recall from 0.1938 to 0.4651;
- repeated-note recall from 0.1429 to 0.5000;
- precision from 0.9615 to 0.9677;
- negative-only FP rate remained 0.0 events/s.

Nine of ten S1 criteria passed.

## Exact-reference admission evidence

At the 129 positive test reference string/frame positions, the onset-aware model had:
- onset admission 0.5814;
- correct-state admission 0.2093;
- joint onset+state admission 0.2093.

Because joint admission equals state admission and state admission is far below onset admission, correct state is the tighter exact-frame admission bottleneck in this result.

This is descriptive evidence, not a causal proof.

## State-target imbalance under the frozen S1 sampler

The frozen training split has 109,620 string/frame state targets.

Exact target accounting from the frozen template rules:
- active string/state tokens: 11,145 = 10.1669%;
- inactive/silence string/state tokens: 98,475 = 89.8331%.

By family, active token counts are:
- isolated: 1,320
- scales: 1,440
- chords: 3,600
- repeated: 1,590
- legato: 1,590
- PalmMute: 1,050
- mixed: 555

The S1 stratified sampler balances frames, not strings. Positive-onset frames average 1.2286 active strings and active-non-onset frames average 1.2774 active strings. With 32 frames from each of the four strata, the expected active state-token share remains about 10.4414% of the 128 x 6 state tokens in a minibatch.

With the current active-state loss weight 1.5, the expected weighted active contribution is only about 14.885% of state-loss token weight.

A weight of 6.0 would move the expected weighted active contribution to about 41.16%, still below half, without changing the sampler, architecture, thresholds, onset loss, learning rate, or step count.

## Chosen next hypothesis

Test **state active-token weighting only**.

Keep the S1 onset-aware sampler fixed and compare two identical five-frame models:
- control: active-state weight 1.5;
- intervention: active-state weight 6.0.

Do not change onset positive weight, onset loss weight, learning rate, thresholds, decoder, data, architecture, step count, or sampling ratios.

The hypothesis is that under-weighted active state tokens are a meaningful remaining contributor to low joint admission and event recall.

This is not established until tested.
