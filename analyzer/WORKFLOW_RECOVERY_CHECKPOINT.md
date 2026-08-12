# Workflow Recovery Checkpoint — Jimmy Paige / GOMYWAY Rhythm24 Calibration

Last updated: 2026-08-12
Working branch: `jimmy-paige-v8-targeted-rhythm-corrections`
Repository: `dadrockyt-sys/dadrock-tabs-android`

## Purpose

This is the authoritative handoff for recovering the current rhythm24 calibration experiment after a ChatGPT, app, or Codespace restart. Read this file before continuing.

## Non-negotiable safety rules

1. The protected 949-event candidate must remain unchanged.
2. Production promotion remains disabled unless explicitly and separately approved later.
3. Frozen V17 is immutable. Never edit V17 in place; every new idea is a separately versioned challenger.
4. Professional-reference or outer/held-out labels must not be used to choose production parameters.
5. Diagnostic runs may inspect held-out behavior, but anything learned that way is tainted for selection and must be frozen before confirmation on untouched data.
6. Keep each benchmark result JSON and manifest under `public/` exactly as the benchmark writes them.
7. Preserve the frozen 36.76 baseline anchor and compare future work against frozen V17.
8. A benchmark on already-exposed folds/phases may be exploratory only; it cannot validate a new champion.
9. `validatedNewChampion` must remain false until a genuinely untouched confirmation succeeds.
10. `productionPromotionAllowed` must remain false throughout this experiment series.
11. The reserved 1/32-offset phase family listed below remains untouched. V31 is diagnostic only and must not consume it.

## Frozen exploratory champion — V17

File:
`analyzer/benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17.py`

Freeze record:
`analyzer/FROZEN_V17_EXPLORATORY_CHAMPION.md`

Frozen result:
- Outer folds: 15 / 15
- Normal: 5 / 5
- Section: 5 / 5
- Shifted-window: 5 / 5
- Generalizes: True
- Protected 949-event candidate unchanged: True
- Production promotion allowed: False

V17 must never be modified in place.

## Progression after V17

### V18 — fixed-policy boundary stress
- 18 / 20 total
- section phase 0.25: 4 / 5
- section phase 0.75: 5 / 5
- shifted phase 0.25: 4 / 5
- shifted phase 0.75: 5 / 5
Conclusion: strong but imperfect boundary robustness.

### V19 — quarter-phase failure anatomy
The two V18 misses represented the same unique phase-0.25/fold-0 partition and were operating-point recoverable. Approximate diagnostic AUC ~0.594. This diagnosed calibration, not ranking, and did not authorize hard-coding the diagnostic q.

### V20 — quarter-phase training-only q selector
- 4 / 5
- exploratory success: False
Conclusion: residual calibration failure remained.

### V21 — remaining V20 failure anatomy
The residual failure was again operating-point recoverable. Diagnostic q values were not authorized for production selection.

### V22 — training geometry q preference
- observations: 20
- both-pass: 12
- both-fail: 5
- q=0.025-only: 2
- q=0.03-only: 1
- training geometry signal ready: False
Conclusion: no defensible training-only geometry rule; stop quarter-phase retuning.

### V23 — frozen V17 unseen-phase confirmation
Untouched phases: 0.125, 0.375, 0.625, 0.875 across section-like and shifted-like partitions.
- 31 / 40
- minimum scheme passes: 3 / 5
- strong confirmation: False
Conclusion: broader boundary sensitivity.

### V24 — V23 failure map
- V23 failures: 9
- unique failure partitions: 5
- duplicate evaluations: 4
- operating-point recoverable: 9 / 9
- non-recoverable ranking failures: 0
Conclusion: ranking remained viable; calibration was the failure mode.

### V25 — training-only multiphase q selector
- 15 / 20
- phases 0.125/0.375/0.625/0.875: 4/5, 3/5, 4/5, 4/5
- exploratory success: False
Conclusion: selector moved failures around.

### V26 — paired V17 vs V25
- V17: 15 / 20
- V25: 15 / 20
- rescues: 2
- regressions: 2
- net gain: 0
- narrow gate warranted: False
- retire V25: True
Conclusion: V25 is retired and must not be revived as direct q selection.

### V27 — global-q landscape diagnostic
Held-out challenge labels were intentionally used for diagnosis only.
- q=0.20: 20 / 20 on the known 20 challenge partitions
- each phase: 5 / 5
- universal q promising: True
Important: q=0.20 was discovered with held-out labels and therefore was not validated.

### V28 — frozen q=0.20 unseen-phase confirmation
q=0.20 was frozen before V28; V28 performed no q search.
Untouched-at-the-time phases:
`0.0625, 0.1875, 0.3125, 0.4375, 0.5625, 0.6875, 0.8125, 0.9375`

Result:
- 34 / 40
- phase passes: 4/5, 4/5, 3/5, 4/5, 5/5, 4/5, 5/5, 5/5
- minimum phase passes: 3 / 5
- perfect confirmation: False
- strong confirmation: False
- protected 949-event candidate unchanged: True
- production promotion allowed: False
Conclusion: q=0.20 is promising but not universal.

### V29 — V28 failure map — COMPLETE
File:
`analyzer/profile_gomyway_3676_patch_rhythm24_v28_failure_map_v29.py`

Result:
- V28 failures: 6
- operating-point recoverable failures: 6 / 6
- non-recoverable ranking failures: 0
- all failures operating-point recoverable: True
- held-out labels used for diagnostic sweep: True
- new tuning performed: False
- protected 949-event candidate unchanged: True
- production promotion allowed: False

Outputs:
- `public/gomyway-3676-patch-rhythm24-v28-failure-map-v29.json`
- `public/gomyway-3676-patch-rhythm24-v28-failure-map-v29-manifest.json`

Important leakage rule: the individual q values exposed by V29's held-out diagnostic sweep are tainted diagnostic information. They must NOT be used to choose a challenger or any production parameter.

Conclusion: preserve V17 ranking/representation. Calibration architecture, not ranking, remains the target.

### V30 — training-only OOF percentile/logit calibration — COMPLETE AND RETIRED
File:
`analyzer/benchmark_gomyway_3676_patch_rhythm24_oof_percentile_logit_calibration_v30.py`

Architecture frozen before the result:
- frozen V17 rhythm24 representation
- existing V5 training-only model-selection path
- training-only OOF scores from normal, section, shifted-window inner partition families
- empirical percentile mapping using only inner-subtraining score distributions
- one-dimensional class-balanced logistic calibrator
- L2 = 1.0
- probability cutoff = 0.5
- 4 inner folds per partition family
- no q search
- no V29 diagnostic q values used
- V28 phases evaluation-only

Result on 2026-08-12:
- V30 passes: 29 / 40
- V28 comparison passes: 34 / 40
- minimum V30 phase passes: 3 / 5
- rescues vs V28: 1
- regressions vs V28: 6
- exploratory promising: False
- q search performed: False
- V29 diagnostic q values used: False
- outer held-out labels used to fit calibration: False
- validated new champion: False
- protected 949-event candidate hash unchanged: True
- production promotion allowed: False

Outputs committed to GitHub:
- `public/gomyway-3676-patch-rhythm24-oof-percentile-logit-calibration-v30.json`
- `public/gomyway-3676-patch-rhythm24-oof-percentile-logit-calibration-v30-manifest.json`

Conclusion: V30 failed its predeclared exploratory-promising gate and is retired. Do not confirm V30 on untouched phases. Do not change V30 parameters using its held-out outcomes.

## CURRENT NEXT STEP — V31 — CREATED, NOT YET RUN

File:
`analyzer/profile_gomyway_3676_patch_rhythm24_v30_calibration_failure_map_v31.py`

V31 is diagnostic only. It reads the committed V30 result and characterizes the six V30 regressions, the one rescue, both-pass folds, and both-fail folds on the already-exposed V28 phase family.

V31 does NOT rerun or inspect the reserved untouched 1/32 phase family. It does NOT choose a new q, probability cutoff, logistic regularization value, model, or production parameter.

Primary diagnostic quantities:
- V30 vs V28 pass status by phase/fold
- effective percentile cutoff implied by each training-only logistic calibrator (`-intercept/slope` where defined)
- implied selected top-fraction for each fold
- V30 selected-count vs V28 selected-count
- V30 vs V28 lift
- whether regressions predominantly select more, the same, or fewer candidates than V28
- spread of effective percentile cutoffs across exposed folds

Required safety fields:
- `diagnosticScope: already-exposed-V28-phases-only`
- `reservedUntouchedPhasesConsumed: false`
- `heldoutLabelsUsedForDiagnosticComparison: true`
- `newTuningPerformed: false`
- `qSearchPerformed: false`
- `calibrationParameterSearchPerformed: false`
- `v29DiagnosticQValuesUsed: false`
- `requiresTrainingOnlyEvidenceForNextChallenger: true`
- `validatedNewChampion: false`
- `protected949CandidateHashUnchanged: true`
- `productionPromotionAllowed: false`

### Run V31 in the existing Codespace

```bash
cd /workspaces/dadrock-tabs-android
git checkout jimmy-paige-v8-targeted-rhythm-corrections
git pull origin jimmy-paige-v8-targeted-rhythm-corrections
source .venv-jimmy311/bin/activate

python -m py_compile analyzer/profile_gomyway_3676_patch_rhythm24_v30_calibration_failure_map_v31.py
python analyzer/profile_gomyway_3676_patch_rhythm24_v30_calibration_failure_map_v31.py
```

V31 writes:
- `public/gomyway-3676-patch-rhythm24-v30-calibration-failure-map-v31.json`
- `public/gomyway-3676-patch-rhythm24-v30-calibration-failure-map-v31-manifest.json`

Decision after V31:
- Treat all V31 outcome comparisons as diagnostic/tainted because they use already-exposed held-out outcomes.
- Do not copy a V31-observed cutoff into a challenger.
- Use V31 only to identify the failure mechanism to test with training-only evidence in a separately versioned challenger (V32 or later).
- Do not consume the reserved untouched phase family until a separately frozen challenger first earns an exploratory confirmation attempt under a predeclared gate.

## Reserved untouched confirmation family — STILL UNCONSUMED

The following 1/32-offset phases were reserved before V30 and remain genuinely untouched:

`0.03125, 0.09375, 0.15625, 0.21875, 0.28125, 0.34375, 0.40625, 0.46875, 0.53125, 0.59375, 0.65625, 0.71875, 0.78125, 0.84375, 0.90625, 0.96875`

Do not evaluate, inspect, or use these phases during V31 or while designing the next challenger from V31. They are reserved for later confirmation of a frozen architecture only.

## Recovery commands

```bash
cd /workspaces/dadrock-tabs-android
git fetch origin
git checkout jimmy-paige-v8-targeted-rhythm-corrections
git pull origin jimmy-paige-v8-targeted-rhythm-corrections
source .venv-jimmy311/bin/activate
git status
```

## Fresh-chat handoff prompt

```text
Continue my GOMYWAY / Jimmy Paige rhythm24 calibration workflow from GitHub.
Repo: dadrockyt-sys/dadrock-tabs-android
Branch: jimmy-paige-v8-targeted-rhythm-corrections
Read analyzer/WORKFLOW_RECOVERY_CHECKPOINT.md first and treat it as the source of truth.
Preserve frozen V17, the protected 949-event candidate, leakage rules, the reserved untouched confirmation phases, and production-promotion=false. Continue from the CURRENT NEXT STEP without unnecessary pauses.
```
