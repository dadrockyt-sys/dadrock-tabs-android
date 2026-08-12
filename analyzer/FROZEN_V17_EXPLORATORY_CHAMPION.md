# Frozen V17 Exploratory Champion

Status: **FROZEN — exploratory champion, not production-promoted**

This document freezes the V17 policy as the current best defensible result for the GOMYWAY 36.76 patch/rhythm experiment sequence.

## Frozen policy

- Representation: existing protected patch features plus rhythm-phase features for periods `[2, 4]`.
- Base model-selection logic: the established V5 section-calibrated pairwise-rank training-only selection.
- Normal scheme: use the V14/V17 base-q behavior unchanged.
- Section scheme: use the V14/V17 base-q behavior unchanged.
- Shifted-window scheme: allow the V16/V17 training-only tight-q selector; choose the tighter operating point only when inner shifted-window training validation supports it.
- No professional reference is used to choose q.
- No outer held-out labels are used to choose q.
- Protected 949-event candidate set remains unchanged.
- No production separator, renderer, protected baseline, or candidate-event changes are included in this freeze.

## Frozen benchmark result

V17 nested benchmark:

- Normal: `5 / 5`
- Section: `5 / 5`
- Shifted-window: `5 / 5`
- Total: `15 / 15`
- Generalizes: `True`

## Post-freeze stress evidence

V18 fixed-policy boundary stress test:

- Stress folds passed: `18 / 20`
- sectionStressPhase0.25: `4 / 5`
- sectionStressPhase0.75: `5 / 5`
- shiftedStressPhase0.25: `4 / 5`
- shiftedStressPhase0.75: `5 / 5`

V19 showed the two V18 quarter-phase misses were the same underlying phase-0.25 fold geometry and were operating-point recoverable.

V20/V21/V22 explored whether a further training-only quarter-phase q rule was justified. V22 found no reliable training-geometry signal for choosing `q=0.025` versus `q=0.03`, so quarter-phase retuning is stopped rather than fitted post hoc.

## Freeze rule

Future experiments must treat V17 as an immutable comparison baseline. Do not modify V17 in place. Any new representation, selector, threshold policy, or calibration method must be implemented as a new version and compared against frozen V17.

Do not claim production readiness solely from the 15/15 nested result. The V18 stress result and subsequent quarter-phase diagnostics remain part of the evidence record.

Production promotion remains **disallowed** until a separate confirmation/promotion process explicitly authorizes it.
