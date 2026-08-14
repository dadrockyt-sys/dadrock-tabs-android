# Workflow Recovery Checkpoint — Jimmy Paige / GOMYWAY Rhythm24 Calibration

Last updated: 2026-08-14
Working branch: `jimmy-paige-v8-targeted-rhythm-corrections`
Repository: `dadrockyt-sys/dadrock-tabs-android`

## Non-negotiable safety rules

1. Frozen V17 is immutable. Never edit it in place.
2. The protected 949-event candidate must remain unchanged.
3. Production promotion remains disabled.
4. Outer/held-out labels may be used for diagnosis only, never to choose production parameters.
5. Any challenger evaluated on exposed folds/phases is exploratory only.
6. `validatedNewChampion` may become true only after a genuinely untouched confirmation succeeds.
7. Version every new diagnostic/challenger separately.
8. Preserve all benchmark JSON/manifest outputs under `public/`.
9. Never retune a policy after seeing its fresh confirmation family; derive a new version instead.
10. Reserve the next untouched confirmation family before interpreting a consumed confirmation to design the next challenger.

## Frozen historical reference

V17 remains immutable. Earlier progression V18–V117 is historical/exposed development material. V115/V116 are also frozen historical validated-champion checkpoints. Do not reinterpret any exposed family as fresh confirmation.

## Current validated champion — V118, confirmed by V119

V118 is now frozen as the validated rhythm24 champion policy.

Architecture:
- V96 backbone remains the default behavior.
- Frozen V115 selective-V112 gate applies the V112 low-band × rhythmic-phase interaction representation to the top 2/7 of folds ranked by the frozen training-context gate.
- V118 adds one frozen exclusion discovered after V116: when the selected fold has `originalQBucket=tight`, `v96Decision=revert-tight-to-anchor-low-dispersion`, `pairRadius=8`, and `lambda=1.0`, do not activate V112; fall back to V96.
- No production promotion is allowed.

### V119 fresh confirmation — SUCCESS

Fresh reserved family consumed for the first time by V119:
- 64 phases, numerators congruent to 3 mod 16 over 1024
- 320 folds total

Result:
- V28: 276/320 = 86.2500%
- V96: 285/320 = 89.0625%
- V115: 291/320 = 90.9375%
- V118: 293/320 = 91.5625%
- selected for V112 before held-out evaluation: 92/320
- V118 gains vs V115: 2
- V118 losses vs V115: 0
- V118 net vs V115: +2
- V118 gains vs V96: 8
- V118 losses vs V96: 0
- V118 net vs V96: +8
- V118 rescues vs V28: 17
- V118 regressions vs V28: 0
- dangerous-signature exclusions applied: 2
- excluded V115 gains: 0
- excluded V115 losses: 2
- minimum V118 phase passes: 3/5
- bottleneck phase: 0.7060546875
- confirmation success: True
- validated new champion: True
- protected 949-event candidate unchanged: True
- candidate events modified: False
- production promotion allowed: False

Authoritative committed V119 files:
- `public/gomyway-3676-patch-rhythm24-v118-reserved-3mod16-over1024-confirmation-v119.json`
- `public/gomyway-3676-patch-rhythm24-v118-reserved-3mod16-over1024-confirmation-v119-manifest.json`

V118/V119 are frozen. Do not modify them in place.

## Next untouched reserve — reserved BEFORE V120 interpretation

Reserve the following family now, before using V119 outcomes to design another challenger:

`phase_k = (5 + 16*k) / 1024`, for `k = 0..63`.

This is the 64-phase **numerators-5-mod-16-over-1024** family. All numerators are odd, so none reduces to a /512-or-coarser dyadic phase. It is disjoint from V116's 1-mod-16 family and V119's 3-mod-16 family.

Do not inspect, evaluate, or reference this reserve in V120 or any exploratory challenger. It may be consumed only after a later architecture is frozen and earns a genuinely fresh confirmation attempt under a predeclared gate.

## CURRENT NEXT STEP — V120 diagnostic

V120 should use only the now-exposed V119 output for diagnosis. It should characterize the 27 V118 failures and the 0.7060546875 bottleneck phase without model search or new held-out evaluation. In particular:
- summarize remaining failures by q bucket, V96 decision, pair radius, lambda, selected-for-V112 status, and final representation;
- identify repeated structural signatures among failures;
- compare failure signatures against pass prevalence to find high-lift but non-exclusive structural concentrations;
- report how many failures are V96 failures, V115 failures, and V118-only failures;
- keep the newly reserved 5-mod-16/1024 family completely untouched.

V120 is anatomy only. Any rule suggested by V120 is tainted and must become a separately versioned exploratory challenger on already exposed families before it may earn the new 5-mod-16/1024 reserve.

Safety for V120:
- reads only already-exposed V119 output
- must not reference the new 5-mod-16/1024 reserve
- no parameter tuning/search
- held-out labels diagnostic only
- no new production tuning
- protected candidate unchanged
- `productionPromotionAllowed = false`

## Recovery commands

```bash
cd /workspaces/dadrock-tabs-android
git fetch origin
git checkout jimmy-paige-v8-targeted-rhythm-corrections
git pull --rebase origin jimmy-paige-v8-targeted-rhythm-corrections
source .venv-jimmy311/bin/activate
git status
```

## Fresh-chat handoff

```text
Continue my GOMYWAY / Jimmy Paige rhythm24 calibration workflow from GitHub.
Repo: dadrockyt-sys/dadrock-tabs-android
Branch: jimmy-paige-v8-targeted-rhythm-corrections
Read analyzer/WORKFLOW_RECOVERY_CHECKPOINT.md first and treat it as the source of truth.
V118 is frozen and validated by V119 at 293/320 = 91.5625% on a fresh family.
Preserve frozen V17, frozen V118/V119, the protected 949-event candidate, leakage rules, the newly reserved untouched numerators-5-mod-16-over-1024 family, and production-promotion=false.
Continue from V120 without unnecessary pauses.
```
