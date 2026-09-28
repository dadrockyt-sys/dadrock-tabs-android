# Next chat: start here

S4 is frozen as a scientific fail. Full onset-gradient detachment did not improve state/joint admission and caused a precision/F1 collapse.

Offline review froze one S5 hypothesis:

- control state active weight: 6
- intervention state active weight: 9

Why 9:
- active state tokens are ~10.44% of state tokens under the frozen sampler;
- weight 6 gives them ~41.16% of weighted state-loss mass;
- equal-mass crossover is ~8.58;
- weight 9 is the smallest integer above that crossover.

Everything else remains fixed: shared multitask encoder, onset-aware sampler, onset pos_weight 8, onset multiplier 4, lr 0.003, 500 steps/model, thresholds 0.50/0.50, decoder V2.

Frozen design:
`docs/astra/SYNTHETIC_DATA_DIVERSITY_S5_DESIGN_V1.md`

Standing policy remains:
- routine non-model GitHub work is pre-authorized;
- model execution, Codespaces and potentially billable Vercel work require explicit authorization.

**S5 model execution is not authorized yet.**
