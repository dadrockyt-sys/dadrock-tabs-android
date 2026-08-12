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

## Key progression through V43

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
V41 diagnosed broadening support. Strict support histogram 0:22, 1:15, 2:3, 3:0. Soft support histogram 0:11, 1:13, 2:15, 3:1.
V42 used fixed q=0.225 when >=2/3 schemes gave soft training-only support: 35/40, minimum 3/5, 1 rescue, 0 regressions, 16 broadened folds; exploratory promising true.
V43 broadened when >=1 strict scheme OR >=2 soft schemes: 35/40, minimum 4/5, 1 rescue, 0 regressions, 23 broadened folds; exploratory promising true.

## V44 — reserved 1/32 confirmation — COMPLETE, FAILED

Consumed 16 previously untouched 1/32 phases.
Result:
- V43 architecture: 66/80
- V28 comparison: 67/80
- minimum phase: 3/5
- rescues: 1
- regressions: 2
- confirmation success: False
- validated new champion: False
- protected candidate unchanged
- production promotion false

The 1/32 family is exposed from V44 onward.

## V45–V56 exploratory redesign on exposed data

V45 diagnosed V44 gate subtypes: both regressions came from `two-soft-only`; the one rescue came from `strict-only`.
V46 removed `two-soft-only` and broadened only on >=1 strict training scheme: 103/120 vs V28 101/120, minimum 3/5, 2 rescues, 0 regressions, 45 broadened folds.
V47 isolated the only 3/5 bottleneck phase at 0.09375.
V48 showed the two remaining bottleneck failures had strict-support=0 and stayed at q=0.20.
V49 found no useful soft-support signature for those failures.
V50 showed both failures were recoverable on both sides of q=0.20 in diagnostic sweeps; diagnostic q values remain tainted.
V51 confirmed q=0.20 sat inside isolated failure holes for both failures.
V52 added a symmetric training-only anchor-hole escape (q=0.175/0.20/0.225): 103/120, minimum 3/5, 2 rescues, 0 regressions; tied V46.
V53 showed V52 changed no outcomes vs V46.
V54/V55 examined bottleneck inner margins and per-scheme signatures.
V56 preserved V46 broadening and added a conservative q=0.175 tight escape only when all three training schemes said tight was pass-count non-worse and had better mean lift than anchor.
V56 result on exposed 120 partitions:
- 102/120
- V28 comparison 101/120
- minimum phase 4/5
- rescues 3
- regressions 2
- chosen q counts: tight 25, anchor 50, broad 45
- unanimous tight-escape folds 25
- exploratoryPromising True
- protected candidate unchanged
- production promotion false

V56 therefore earned a fresh untouched confirmation attempt.

## V57 — reserved 1/64 odd-offset confirmation — COMPLETE, FAILED

The previously reserved 32-phase 1/64 odd-offset family was consumed for the first time by V57:
`0.015625, 0.046875, 0.078125, 0.109375, 0.140625, 0.171875, 0.203125, 0.234375, 0.265625, 0.296875, 0.328125, 0.359375, 0.390625, 0.421875, 0.453125, 0.484375, 0.515625, 0.546875, 0.578125, 0.609375, 0.640625, 0.671875, 0.703125, 0.734375, 0.765625, 0.796875, 0.828125, 0.859375, 0.890625, 0.921875, 0.953125, 0.984375`

Result:
- V57 / frozen V56 architecture: 135/160
- V28 comparison: 137/160
- minimum phase: 3/5
- rescues vs V28: 3
- regressions vs V28: 5
- chosen q counts: tight 42, anchor 65, broad 53
- unanimous tight-escape folds: 42
- architecture frozen before confirmation: True
- parameter search performed: False
- confirmation success: False
- validated new champion: False
- 1/64 reserve consumed: True
- protected 949-event candidate unchanged: True
- production promotion allowed: False

Conclusion: V56 does not validate. The 1/64 odd-offset family is now exposed and may only be used diagnostically/exploratorily.

## NEW untouched reserve — 1/128 odd-numerator family

Before using V57 post-hoc outcomes to design another challenger, reserve the following 64 phases as the next genuinely untouched family:

`0.0078125, 0.0234375, 0.0390625, 0.0546875, 0.0703125, 0.0859375, 0.1015625, 0.1171875, 0.1328125, 0.1484375, 0.1640625, 0.1796875, 0.1953125, 0.2109375, 0.2265625, 0.2421875, 0.2578125, 0.2734375, 0.2890625, 0.3046875, 0.3203125, 0.3359375, 0.3515625, 0.3671875, 0.3828125, 0.3984375, 0.4140625, 0.4296875, 0.4453125, 0.4609375, 0.4765625, 0.4921875, 0.5078125, 0.5234375, 0.5390625, 0.5546875, 0.5703125, 0.5859375, 0.6015625, 0.6171875, 0.6328125, 0.6484375, 0.6640625, 0.6796875, 0.6953125, 0.7109375, 0.7265625, 0.7421875, 0.7578125, 0.7734375, 0.7890625, 0.8046875, 0.8203125, 0.8359375, 0.8515625, 0.8671875, 0.8828125, 0.8984375, 0.9140625, 0.9296875, 0.9453125, 0.9609375, 0.9765625, 0.9921875`

These 64 phases are reserved now, before V58 interpretation. Do not inspect, evaluate, or reference them in V58 or any exploratory challenger. They may be consumed only after a later architecture is frozen and earns a new confirmation attempt under a predeclared gate.

## CURRENT NEXT STEP — V58 diagnostic

V58 should analyze only the now-exposed V57 1/64 confirmation outcomes and determine which V56 branch (`tight`, `anchor`, `broad`) produced the 3 rescues and 5 regressions, plus phase-floor/bottleneck structure. Any architecture idea derived from V57/V58 is tainted for all exposed families and must first be tested on exposed data before it can earn the reserved 1/128 family.

Safety for V58:
- reads only already-exposed V57 output
- must not reference the new 1/128 reserve
- no parameter tuning/search
- held-out labels diagnostic only
- protected candidate unchanged
- validatedNewChampion false
- productionPromotionAllowed false

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
Preserve frozen V17, the protected 949-event candidate, leakage rules, the newly reserved untouched 1/128 odd-numerator confirmation family, and production-promotion=false. Continue from V58 without unnecessary pauses.
```
