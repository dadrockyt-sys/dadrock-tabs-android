# Next chat: start here

S2 is frozen as a scientific fail, although state weight 6.0 helped.

Offline review found:
- state admission improved to 0.3101;
- exact onset admission stayed at 0.5736;
- repeated-note recall stayed at 0.5000.

Under the frozen onset-aware sampler, positive onset string/tokens are only about 5.119% of batch onset tokens. BCE pos_weight 8 gives them about 30.15% of expected weighted onset-loss mass.

One S3 hypothesis is now frozen:
`docs/astra/SYNTHETIC_DATA_DIVERSITY_S3_DESIGN_V1.md`

S3 changes only onset BCE positive weight:
- control 8
- intervention 16

State weight stays 6.0 and all data/sampler/architecture/lr/threshold/step settings remain fixed. It also reports repeated-reference preceding-frame onset probabilities to distinguish missed attacks from rising-edge/plateau behavior.

**S3 execution is not authorized. Fresh explicit authorization is required before rendering or optimizer work.**
