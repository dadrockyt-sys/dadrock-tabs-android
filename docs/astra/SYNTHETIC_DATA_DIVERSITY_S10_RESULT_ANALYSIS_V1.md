# Astra S10 result analysis V1

Date: 2026-09-28
Scope: offline review only.

## S10 outcome

S10 validly isolated state-head width using an identity-preserving widening:
- the first 128 hidden units and their output columns were copied exactly;
- the extra 64 output columns started at zero;
- pre-update state and onset logits were bit-identical;
- the extra pathway learned (final norm 12.9889).

Test control 128 -> width 192:
- state admission 0.2791 -> 0.3256 (+0.0465)
- joint admission 0.2791 -> 0.3256 (+0.0465)
- onset recall 0.5659 -> 0.6357
- onset F1 0.6759 -> 0.6979
- chord F1 0.3019 -> 0.3934
- repeated recall 0.5952 -> 0.6429
- precision 0.8391 -> 0.7736
- onset+offset F1 0.6250 -> 0.5892

S10 passed 7/16 frozen criteria and failed the integrated gate.

## Interpretation

Wider state-specific capacity can improve exact state admission, but width 192 does not preserve enough event quality under this run.

Do not continue automatic widening.

## Important robustness signal

The S10 control used the same diversified 30-voicing dataset and the same training recipe class as S9, but a different deterministic initialization. Its test F1/state admission (0.6759 / 0.2791) were far below S9's 30-voicing arm (0.7917 / 0.4109).

That means the strongest positive S9 result may be materially initialization-sensitive.

Before any further architecture search or P1/P2 transfer, the next scientific question should be robustness of the S9 data-diversity effect across a small frozen set of seeds.

This is a confirmation experiment, not another performance-tuning experiment.
