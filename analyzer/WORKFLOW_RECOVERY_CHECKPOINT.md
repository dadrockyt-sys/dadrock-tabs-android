# Workflow Recovery Checkpoint — Jimmy Paige / GOMYWAY Rhythm24 Calibration

Last updated: 2026-08-12
Working branch: `jimmy-paige-v8-targeted-rhythm-corrections`
Repository: `dadrockyt-sys/dadrock-tabs-android`

## Non-negotiable safety rules

1. Frozen V17 is immutable. Never edit it in place.
2. The protected 949-event candidate must remain unchanged.
3. Production promotion remains disabled.
4. Outer/held-out labels may be used for diagnosis only, never to choose production parameters.
5. Any challenger evaluated on exposed folds/phases is exploratory only.
6. `validatedNewChampion` remains false unless a genuinely untouched confirmation succeeds.
7. Version every new diagnostic/challenger separately.
8. Preserve all benchmark JSON/manifest outputs under `public/`.

## Frozen reference

V17 remains the frozen exploratory reference:
- 15/15 outer folds
- normal 5/5, section 5/5, shifted-window 5/5
- protected candidate unchanged
- production promotion false

## Key progression

V18: 18/20 boundary stress.
V23: 31/40 unseen-phase confirmation; minimum 3/5.
V27 diagnostic discovered global q=0.20, but that value was tainted until frozen.
V28 froze q=0.20 before confirmation and scored 34/40 on then-untouched 1/16-style phases; minimum 3/5.
V29 showed all 6 V28 failures were operating-point recoverable; diagnostic q values remain tainted.
V30 training-only OOF percentile/logit calibration: 29/40, 1 rescue, 6 regressions; retired.
V31 diagnosed V30 regressions as over-broad selection.
V32 robust threshold consensus: 23/40; retired.
V33 diagnosed V32 as over-broad.
V34 conservative all-scheme consensus: 24/40; retired.
V35 showed V34 tightened 38/40 folds but still had 11 regressions.
V36 V28 percentile-floor anchor: 34/40, 3 rescues, 3 regressions, but 0 true training-only tightenings.
V37 showed percentile>=0.80 is not equivalent to exact q=0.20 top-fraction semantics.
V38 restored exact V28 semantics: 34/40, no changes; unanimous tightening never activated.
V39 showed no inner scheme supported tightening below q=0.20.
V40 tested predeclared q=0.225 broadening under unanimous scheme support: 34/40; gate never activated.
V41 diagnosed broadening support. Strict support histogram: 0:22, 1:15, 2:3, 3:0. Soft support histogram: 0:11, 1:13, 2:15, 3:1.
V42 used fixed q=0.225 when >=2/3 schemes gave soft training-only support: 35/40, minimum 3/5, 1 rescue, 0 regressions, 16 broadened folds; exploratory promising true.
V43 broadened when >=1 strict scheme OR >=2 soft schemes: 35/40, minimum 4/5, 1 rescue, 0 regressions, 23 broadened folds; exploratory promising true. This earned one untouched confirmation attempt.

## V44 — reserved 1/32 confirmation — COMPLETE, FAILED

File:
`analyzer/confirm_gomyway_3676_patch_rhythm24_v43_reserved_1over32_v44.py`

The previously reserved 1/32 phase family was consumed for the first time by V44:
`0.03125, 0.09375, 0.15625, 0.21875, 0.28125, 0.34375, 0.40625, 0.46875, 0.53125, 0.59375, 0.65625, 0.71875, 0.78125, 0.84375, 0.90625, 0.96875`

Result:
- V44 / frozen V43 architecture: 66 / 80
- V28 comparison: 67 / 80
- minimum phase passes: 3 / 5
- rescues vs V28: 1
- regressions vs V28: 2
- folds broadened above V28 q: 39
- confirmation success: False
- validated new champion: False
- reserved 1/32 phases consumed: True
- protected 949-event candidate unchanged: True
- production promotion allowed: False

Conclusion: V43 does not validate. The 1/32 family is now exposed and may only be used diagnostically/exploratorily from this point onward.

## NEW untouched reserve — 1/64 odd-offset family

Before any V44 post-hoc diagnostic is used to design another challenger, reserve the following 32 phases as the next genuinely untouched family:

`0.015625, 0.046875, 0.078125, 0.109375, 0.140625, 0.171875, 0.203125, 0.234375, 0.265625, 0.296875, 0.328125, 0.359375, 0.390625, 0.421875, 0.453125, 0.484375, 0.515625, 0.546875, 0.578125, 0.609375, 0.640625, 0.671875, 0.703125, 0.734375, 0.765625, 0.796875, 0.828125, 0.859375, 0.890625, 0.921875, 0.953125, 0.984375`

These phases are reserved now, before V45 interpretation. Do not inspect, evaluate, or reference them in V45 or any exploratory challenger. They may be consumed only after a later architecture is frozen and earns a fresh confirmation attempt under a predeclared gate.

## CURRENT NEXT STEP — V45 — CREATED, NOT YET RUN

File:
`analyzer/profile_gomyway_3676_patch_rhythm24_v44_confirmation_failure_map_v45.py`

Purpose: diagnostic-only characterization of V44's exposed 1/32 outcomes. It classifies each fold by V43 gate subtype (`anchor`, `strict-only`, `two-soft-only`, `strict-and-two-soft`) and reports where the one rescue and two regressions occurred.

Safety:
- reads only the already-exposed V44 1/32 output
- does not reference the new 1/64 reserve
- performs no parameter search or tuning
- held-out labels are diagnostic only
- protected candidate must remain unchanged
- validatedNewChampion remains false
- productionPromotionAllowed remains false

After V45, any architecture idea derived from V44/V45 is tainted for the 1/32 family. It must first be tested exploratorily on already-exposed data, then frozen before touching the reserved 1/64 odd-offset family.

## Recovery commands

```bash
cd /workspaces/dadrock-tabs-android
git fetch origin
git checkout jimmy-paige-v8-targeted-rhythm-corrections
git pull origin jimmy-paige-v8-targeted-rhythm-corrections
source .venv-jimmy311/bin/activate
git status
```

## Fresh-chat handoff

```text
Continue my GOMYWAY / Jimmy Paige rhythm24 calibration workflow from GitHub.
Repo: dadrockyt-sys/dadrock-tabs-android
Branch: jimmy-paige-v8-targeted-rhythm-corrections
Read analyzer/WORKFLOW_RECOVERY_CHECKPOINT.md first and treat it as the source of truth.
Preserve frozen V17, the protected 949-event candidate, leakage rules, the new reserved untouched 1/64 odd-offset confirmation family, and production-promotion=false. Continue from the CURRENT NEXT STEP without unnecessary pauses.
```
