# Next chat: start here

S3 failed its frozen gate.

Offline review supports one S4 hypothesis: shared-encoder task competition.

S4 changes exactly one variable:
- control: both state and onset losses update the shared encoder;
- intervention: onset loss trains the onset head but its encoder activation is detached, so onset loss contributes zero encoder gradient.

Everything else uses the S3 control configuration:
- state weight 6
- onset pos_weight 8
- onset-aware sampler
- same five-frame architecture
- lr 0.003
- 500 steps/model
- thresholds 0.50 / 0.50
- decoder V2

Frozen design:
`docs/astra/SYNTHETIC_DATA_DIVERSITY_S4_DESIGN_V1.md`

Standing policy still applies: routine GitHub work is pre-authorized, but **S4 model execution requires explicit authorization**. P1/P2/P3 remain sealed.
