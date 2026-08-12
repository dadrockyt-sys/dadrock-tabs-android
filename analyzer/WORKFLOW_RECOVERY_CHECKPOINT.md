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

Local Codespace result on 2026-08-12:
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

Important leakage rule: the individual q values exposed by V29's held-out diagnostic sweep are tainted diagnostic information. They must NOT be used to choose V30 or any production parameter.

Conclusion: preserve V17 ranking/representation. The next challenger must change calibration architecture rather than retune q.

## CURRENT NEXT STEP — V30 — CREATED, NOT YET RUN

File:
`analyzer/benchmark_gomyway_3676_patch_rhythm24_oof_percentile_logit_calibration_v30.py`

V30 is a separately versioned calibration-only challenger. It does not edit V17 and it does not use the V29 diagnostic q values.

### V30 architecture frozen before its result

For each outer-training partition:
1. Use the frozen V17 rhythm24 representation and the existing V5 training-only model-selection path.
2. Generate training-only out-of-fold ranker scores across three predeclared inner partition families: normal, section, and shifted-window; 4 folds each.
3. Convert each inner validation score to an empirical percentile using only its corresponding inner-subtraining score distribution.
4. Fit a one-dimensional class-balanced logistic calibrator to those training-only OOF percentiles.
5. Fixed architecture constants, not searched on outer labels:
   - L2 = 1.0
   - probability cutoff = 0.5
   - 4 inner folds per partition family
6. Fit the final frozen-ranking model on the whole outer-training partition, percentile-map held-out scores using the outer-training score distribution, and apply the fixed calibrated probability cutoff.
7. No q search occurs in V30.

The already-exposed V28 phases are used only as an exploratory stress/evaluation set in V30. Their held-out labels are not used to fit calibration or select V30 parameters. V30 can therefore never set `validatedNewChampion: true`, regardless of its score.

Predeclared exploratory-promising gate:
- V30 total passes must exceed the V28 comparison total,
- minimum V30 phase passes must be at least 4 / 5,
- regressions versus V28 must not exceed rescues.

Even if this gate passes, V30 requires untouched confirmation before any validation claim.

Expected safety fields:
- `qSearchPerformed: false`
- `v29DiagnosticQValuesUsed: false`
- `outerHeldoutLabelsUsedToFitCalibration: false`
- `outerHeldoutLabelsUsedToChooseCalibrationParameters: false`
- `requiresUntouchedConfirmationBeforeValidation: true`
- `validatedNewChampion: false`
- `protected949CandidateHashUnchanged: true`
- `productionPromotionAllowed: false`

### Run V30 in the existing Codespace

```bash
cd /workspaces/dadrock-tabs-android
git checkout jimmy-paige-v8-targeted-rhythm-corrections
git pull origin jimmy-paige-v8-targeted-rhythm-corrections
source .venv-jimmy311/bin/activate

python -m py_compile analyzer/benchmark_gomyway_3676_patch_rhythm24_oof_percentile_logit_calibration_v30.py
python analyzer/benchmark_gomyway_3676_patch_rhythm24_oof_percentile_logit_calibration_v30.py
```

V30 writes:
- `public/gomyway-3676-patch-rhythm24-oof-percentile-logit-calibration-v30.json`
- `public/gomyway-3676-patch-rhythm24-oof-percentile-logit-calibration-v30-manifest.json`

## Reserved untouched confirmation family for a future V31

The following 1/32-offset phases are reserved now, before V30 is run, and must NOT be evaluated or inspected during V30:

`0.03125, 0.09375, 0.15625, 0.21875, 0.28125, 0.34375, 0.40625, 0.46875, 0.53125, 0.59375, 0.65625, 0.71875, 0.78125, 0.84375, 0.90625, 0.96875`

Purpose: preserve a genuinely untouched phase family for confirmation of a frozen challenger architecture.

Decision after V30:
- If V30 is exploratory-promising, freeze V30 architecture exactly as run, then create V31 to evaluate that frozen architecture on the reserved untouched 1/32 phase family. No V30 parameter may be changed using V30 held-out outcomes before V31.
- If V30 is not promising, retire V30. Do not consume the reserved V31 phase family. Diagnose the exposed V30 stress behavior only and create a separately versioned challenger using training-only evidence.
- Never promote to production during either path.

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
