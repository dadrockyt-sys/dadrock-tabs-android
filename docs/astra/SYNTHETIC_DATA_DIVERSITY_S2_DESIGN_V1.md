# Astra synthetic data diversity S2 design V1

Date: 2026-09-27
Status: DESIGN FROZEN — NOT AUTHORIZED FOR EXECUTION

## Question

With the S1 onset-aware frame sampler held fixed, does increasing only the active-state cross-entropy weight from 1.5 to 6.0 materially improve correct-state/joint admission and event recall without unacceptable precision, offset, or negative-audio degradation?

## Evidence motivating the single variable

S1 onset-aware test:
- onset precision 0.9677;
- onset recall 0.4651;
- onset F1 0.6283;
- repeated-note recall 0.5000;
- exact positive-frame onset admission 0.5814;
- exact correct-state admission 0.2093;
- exact joint admission 0.2093.

The frozen S1 sampler still yields only about 10.44% active state tokens in a typical 128-frame minibatch. Weight 1.5 gives active tokens about 14.9% of expected state-loss token weight. Weight 6.0 raises that to about 41.2%.

## Fixed data

Regenerate the same synthetic development corpus under a new authorization:
- generator code and seed unchanged;
- 98 template identities x 3 variants = 294 clips;
- 588 seconds total;
- train/validation/test 210 / 42 / 42;
- same 22.05 kHz 192-bin CQT;
- no external audio assets;
- no P1/P2/P3.

Before optimizer work, write content hashes for each uncompressed generated array (features, state, onset, split/template metadata) so within-run arm identity is explicit. Do not use the NPZ container hash as a numerical-array identity claim.

## Models

Exactly two identical five-frame temporal models:
- 5 x 192 input -> Linear(960,128) -> ReLU;
- identical six-string state head;
- identical onset head;
- identical initialization seed;
- Adam lr 0.003;
- exactly 500 optimizer steps/model;
- batch size 128;
- S1 onset-aware 32/32/32/32 frame sampler for both arms;
- onset BCE positive weight 8 for both;
- onset loss multiplier 4 for both;
- state threshold 0.50;
- onset threshold 0.50;
- decoder V2;
- zero threshold search.

Only changed variable:
- control state-active token weight = **1.5**;
- intervention state-active token weight = **6.0**.

## Required measurements

For validation and test, both arms report:
- pitch-onset TP/FP/FN, precision, recall, F1;
- pitch-onset+offset F1;
- repeated-note numerator/denominator/recall;
- family-level onset precision/recall/F1;
- negative-only FP events/second;
- exact positive-reference onset admission;
- exact positive-reference correct-state admission;
- exact joint onset+state admission;
- true-state versus silence probability/margin summary at positive references;
- strongest incorrect-state probability/margin summary;
- optimizer steps/runtime;
- all array content hashes and arm source/model identities.

No post-result threshold selection.

## Frozen S2 success criteria

The weight-6 intervention supports the state-weighting hypothesis only if all are true:

1. exact-reference correct-state admission gain versus weight-1.5 >= **+0.20**;
2. exact-reference joint-admission gain >= **+0.20**;
3. test onset recall gain >= **+0.10**;
4. test onset F1 gain >= **+0.08**;
5. absolute test onset recall >= **0.55**;
6. absolute test onset F1 >= **0.68**;
7. test onset precision >= **0.85**;
8. repeated-note recall >= **0.55**;
9. onset+offset F1 does not decline by more than **0.05** versus control;
10. negative-only FP rate <= **0.10 events/s**;
11. no supported family loses more than **0.15 F1** versus control;
12. both arms complete <=500 steps, all metrics finite, zero threshold search.

These are S2 diagnostic criteria. They do not rewrite the failed S0 or S1 gates.

## Decision branches

- All criteria pass: active-state under-weighting is supported as a meaningful contributor. Stop and design a separate synthetic competence gate; do not open P1/P2 automatically.
- State/joint admission rises but event floors fail: weighting helps but is insufficient; stop and isolate the next bottleneck.
- Precision, offsets, negative specificity, or family stability violates a guard: reject weight 6.0 under this setup.
- State/joint admission fails to improve materially: reject active-state under-weighting as the next primary lever.
- Any runtime/identity/preparation failure: freeze and stop; no retry.

## Hard execution ceiling if later authorized

- exactly 294 clips / 588 s;
- exactly 2 five-frame models;
- 500 optimizer steps/model, 1,000 total;
- render <=20 CPU min;
- fit/eval <=60 CPU min;
- $0 paid compute;
- zero automatic retries;
- no threshold tuning;
- no external audio assets;
- no P1/P2/P3;
- no deployment/main/customer delivery.

## Authorization boundary

This design does not authorize execution. Fresh explicit authorization is required before rendering or optimizer work.
