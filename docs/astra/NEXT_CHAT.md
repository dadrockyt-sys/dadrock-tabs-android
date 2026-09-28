# Next chat: start here

S1 is frozen as a scientific fail: nine of ten criteria passed, but absolute test onset recall was 0.4651 < 0.55.

Offline review shows the onset-aware model's exact positive-frame admission was:
- onset 0.5814
- correct state 0.2093
- joint 0.2093

The frozen S1 sampler still exposes only about 10.44% active state tokens per batch; state active weight 1.5 gives them only about 14.9% of expected weighted state-loss contribution.

One S2 hypothesis is frozen:
`docs/astra/SYNTHETIC_DATA_DIVERSITY_S2_DESIGN_V1.md`

S2 changes only active-state weight:
- control 1.5
- intervention 6.0

All other data/model/sampler/loss/lr/threshold/step settings stay fixed.

**S2 execution is not authorized. Fresh explicit authorization is required.**
