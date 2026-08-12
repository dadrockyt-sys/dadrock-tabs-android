# Workflow Recovery Checkpoint — Jimmy Paige / GOMYWAY Rhythm24 Calibration

Last updated: 2026-08-11
Working branch: `jimmy-paige-v8-targeted-rhythm-corrections`
Repository: `dadrockyt-sys/dadrock-tabs-android`

## Purpose

This file exists so the workflow can be recovered after a ChatGPT restart, app data clear, Codespace restart, or loss of conversation context. Treat this document as the handoff point for continuing the current experiment series.

## Non-negotiable safety rules

1. The protected 949-event candidate must remain unchanged.
2. Production promotion must remain disabled unless explicitly and separately approved later.
3. Do not modify frozen V17 in place. Any new idea must be a new version/challenger.
4. Do not use professional-reference or held-out labels to choose production parameters.
5. Diagnostic runs may inspect held-out behavior, but any parameter discovered that way must be frozen and confirmed on untouched data before it can be treated as validated.
6. Keep result JSON and manifest files under `public/` exactly as each benchmark writes them.
7. Future tests should compare against frozen V17 and preserve the 36.76 baseline anchor.

## Frozen exploratory champion: V17

File:
`analyzer/benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17.py`

Frozen V17 result:

- Outer folds passed: 15 / 15
- Normal: 5 / 5
- Section: 5 / 5
- Shifted-window: 5 / 5
- Generalizes: True
- Protected 949-event candidate unchanged: True
- Production promotion allowed: False

Freeze record:
`analyzer/FROZEN_V17_EXPLORATORY_CHAMPION.md`

V17 must not be edited in place.

## Key progression after V17

### V18 — fixed-policy boundary stress

Frozen V17 challenged on quarter/three-quarter boundary shifts.

Result:
- 18 / 20 total stress folds
- section phase 0.25: 4 / 5
- section phase 0.75: 5 / 5
- shifted phase 0.25: 4 / 5
- shifted phase 0.75: 5 / 5

Conclusion: strong but not perfect boundary robustness.

### V19 — quarter-phase failure anatomy

The two V18 misses were the same unique partition under two labels: phase 0.25, fold 0.

Both were operating-point recoverable. Approximate diagnostic:
- AUC ~0.594
- selected q ~0.05
- passing q ~0.03

Conclusion: calibration problem, not ranking failure.

### V20 — quarter-phase training-only q selector

Result:
- 4 / 5 quarter-phase folds
- exploratory success: False

Conclusion: still one residual failure; do not hard-code q=0.03 post hoc.

### V21 — remaining V20 failure anatomy

Remaining fold was again operating-point recoverable.
- selected q=0.025
- q=0.03 passed

Conclusion: ranking still viable; seek a principled training-only signal.

### V22 — training geometry q preference

Result:
- observations: 20
- both-pass: 12
- both-fail: 5
- q=0.025-only pass: 2
- q=0.03-only pass: 1
- training geometry signal ready: False

Conclusion: no defensible training-only geometry rule. Freeze V17 and stop quarter-phase retuning.

### V23 — frozen V17 unseen-phase confirmation

Untouched phases tested: 0.125, 0.375, 0.625, 0.875 across section-like and shifted-like partitions.

Result:
- 31 / 40 total
- minimum scheme passes: 3 / 5
- strong confirmation: False

Conclusion: V17 generalizes partially but has broader boundary sensitivity.

### V24 — V23 failure map

Result:
- V23 failures: 9
- unique failure partitions: 5
- duplicate evaluations: 4
- operating-point recoverable: 9 / 9
- non-recoverable ranking failures: 0

Conclusion: ranking remains good; problem is calibration across boundaries.

### V25 — training-only multiphase q selector

Result:
- 15 / 20 challenge folds
- phase 0.125: 4 / 5
- phase 0.375: 3 / 5
- phase 0.625: 4 / 5
- phase 0.875: 4 / 5
- minimum phase passes: 3 / 5
- exploratory success: False

Conclusion: selector was too aggressive and moved failures around.

### V26 — paired V17 vs V25 comparison

Result:
- Frozen V17: 15 / 20
- V25: 15 / 20
- Rescues: 2
- Regressions: 2
- Net gain: 0
- q changed: 15 partitions
- Narrow gate warranted: False
- Retire V25: True

Conclusion: retire V25.

### V27 — global q landscape diagnostic

Diagnostic only; held-out challenge labels were intentionally used to map q performance. No selector was trained and no production rule was created.

Result:
- q=0.20 produced 20 / 20 on the known 20 challenge partitions
- each phase: 5 / 5
- universal q promising: True

Important: q=0.20 was discovered using held-out challenge labels, so it was NOT considered validated.

### V28 — frozen q=0.20 unseen-phase confirmation

q=0.20 was frozen before the run. No q search in V28. Untouched phases:
`0.0625, 0.1875, 0.3125, 0.4375, 0.5625, 0.6875, 0.8125, 0.9375`

Result:
- 34 / 40 confirmation folds
- phase 0.0625: 4 / 5
- phase 0.1875: 4 / 5
- phase 0.3125: 3 / 5
- phase 0.4375: 4 / 5
- phase 0.5625: 5 / 5
- phase 0.6875: 4 / 5
- phase 0.8125: 5 / 5
- phase 0.9375: 5 / 5
- minimum phase passes: 3 / 5
- perfect confirmation: False
- strong confirmation: False
- protected 949-event candidate unchanged: True
- production promotion allowed: False

Conclusion: q=0.20 is promising but NOT confirmed as universal.

## CURRENT NEXT STEP — V29

V29 has already been created and committed. It diagnoses only the 6 V28 misses and does not tune or change production behavior.

File:
`analyzer/profile_gomyway_3676_patch_rhythm24_v28_failure_map_v29.py`

Commit that created V29:
`1c52afce957d9809af0c3da2996d00ab81e9b4b9`

Run after recovery:

```bash
cd /workspaces/dadrock-tabs-android
git checkout jimmy-paige-v8-targeted-rhythm-corrections
git pull origin jimmy-paige-v8-targeted-rhythm-corrections
source .venv-jimmy311/bin/activate

python -m py_compile analyzer/profile_gomyway_3676_patch_rhythm24_v28_failure_map_v29.py
python analyzer/profile_gomyway_3676_patch_rhythm24_v28_failure_map_v29.py
```

Expected ending fields:

```text
V28 failures: 6
Operating-point recoverable failures: X / 6
Non-recoverable ranking failures: X
All failures operating-point recoverable: True/False
```

## Decision rule after V29

- If all 6 are operating-point recoverable: preserve the ranking architecture and move to a more robust calibration architecture. Do NOT retune V17 in place.
- If any are non-recoverable: diagnose ranking/representation only for those residual partitions in a new version.
- Do not promote anything to production.
- Do not modify the protected 949-event candidate.

## Recovery commands for Codespace

Use this block after a Codespace restart:

```bash
cd /workspaces/dadrock-tabs-android
git fetch origin
git checkout jimmy-paige-v8-targeted-rhythm-corrections
git pull origin jimmy-paige-v8-targeted-rhythm-corrections
source .venv-jimmy311/bin/activate

git status
```

You should end up on:

```text
jimmy-paige-v8-targeted-rhythm-corrections
```

## Fresh-chat handoff prompt

Paste this into a new ChatGPT conversation if the current chat is lost:

```text
Please continue my GOMYWAY / Jimmy Paige rhythm24 calibration workflow from GitHub.

Repository: dadrockyt-sys/dadrock-tabs-android
Branch: jimmy-paige-v8-targeted-rhythm-corrections
Recovery file: analyzer/WORKFLOW_RECOVERY_CHECKPOINT.md

Read that file from GitHub first and treat it as the source of truth for current status, safety rules, frozen V17, V18-V28 results, and the next step. Do not modify frozen V17 in place. Do not alter the protected 949-event candidate. Do not allow production promotion.

The immediate next step should be V29 unless the recovery file has been updated after this checkpoint. Continue the experiment series without pausing for unnecessary confirmation, but keep each new challenger versioned and leakage-safe.
```

## Short branch pointer

If only the branch is needed:

```text
Repo: dadrockyt-sys/dadrock-tabs-android
Branch: jimmy-paige-v8-targeted-rhythm-corrections
Read: analyzer/WORKFLOW_RECOVERY_CHECKPOINT.md
```

This file should be updated again whenever a new major checkpoint is reached.
