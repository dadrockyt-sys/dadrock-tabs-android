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

V17 remains immutable. V18–V127 are historical/exposed development, diagnostics, reverse-validation, or prior confirmation material. V115/V116, V118/V119, V122/V124, and V127/V128 are frozen checkpoints. Do not reinterpret any exposed family as fresh confirmation.

## Current validated champion — guarded V122 policy, confirmed by V128

The current validated rhythm24 champion is the frozen V122 structural policy plus the frozen V127 guard, freshly confirmed by V128.

Architecture:
- V118 baseline: V96 backbone + frozen V115 top-2/7 selective V112 gate + frozen V118 dangerous-signature exclusion.
- V122 adds seven frozen structural representation switches:
  - anchor / keep-anchor / r4 / lambda1 -> cosine
  - anchor / keep-anchor / r4 / lambda100 -> v112_interactions
  - anchor / keep-anchor / r8 / lambda100 -> v112_interactions
  - broad / revert-broad-to-anchor-high-dispersion / r2 / lambda1 -> cosine
  - tight / keep-tight-high-dispersion / r8 / lambda1 -> base
  - tight / revert-tight-to-anchor-low-dispersion / r4 / lambda1 -> phase_col3
  - tight / revert-tight-to-anchor-low-dispersion / r4 / lambda100 -> base
- V127 adds one frozen surgical guard inside the phase_col3 group:
  - structural key: tight / revert-tight-to-anchor-low-dispersion / r4 / lambda1
  - representation: phase_col3
  - condition: `selectedForV112 == true`
  - action: fall back to frozen V118 baseline
- No production promotion is allowed.

### V127 corroborative guard evidence

Guard chosen from consumed V124 diagnostics, then reverse-validated on consumed V116:
- consumed V124: V122 308/320 -> guarded 310/320; +2/-0, net +2
- reverse V116: V122 307/320 -> guarded 309/320; +2/-0, net +2
- corroborative only; not fresh confirmation

### V128 fresh confirmation — SUCCESS

Fresh reserved family consumed for the first time by V128:
- 64 phases, numerators congruent to 7 mod 16 over 1024
- 320 folds total

Result:
- V28: 276/320 = 86.2500%
- V96: 284/320 = 88.7500%
- V115: 289/320 = 90.3125%
- V118: 291/320 = 90.9375%
- V122 baseline: 307/320 = 95.9375%
- guarded V128: 309/320 = 96.5625%
- V128 gains/losses vs V122: +2/-0, net +2
- V128 gains/losses vs V118: +18/-0, net +18
- V128 gains/losses vs V96: +25/-0, net +25
- rescues/regressions vs V28: +33/-0
- structural policy applied: 137/320
- V127 guard applied: 2/320
- minimum V128 phase passes: 4/5
- bottleneck phases: 0.0224609375, 0.0380859375, 0.1005859375, 0.1162109375, 0.2099609375, 0.2255859375, 0.2724609375, 0.3193359375, 0.7724609375, 0.9443359375, 0.9599609375
- crosses 95 percent: True
- confirmation success: True
- validated new champion: True
- policy and guard frozen before held-out evaluation: True
- new tuning performed: False
- candidate events modified: False
- protected 949-event candidate unchanged: True
- production promotion allowed: False

Authoritative committed V128 files:
- `public/gomyway-3676-patch-rhythm24-v127-guarded-v122-reserved-7mod16-over1024-confirmation-v128.json`
- `public/gomyway-3676-patch-rhythm24-v127-guarded-v122-reserved-7mod16-over1024-confirmation-v128-manifest.json`

V122/V124 and V127/V128 are frozen. Do not modify them in place.

## Next untouched reserve — reserved BEFORE V129 interpretation

Reserve now, before using V128 failures to design another challenger:

`phase_k = (9 + 16*k) / 1024`, for `k = 0..63`.

This is the 64-phase **numerators-9-mod-16-over-1024** family. It is disjoint from the consumed 1-mod-16 V116, 3-mod-16 V119, 5-mod-16 V124, and 7-mod-16 V128 families.

Do not inspect, evaluate, or reference this reserve in V129 or any exploratory challenger. It may be consumed only after a later architecture is frozen and earns a genuinely fresh confirmation attempt under a predeclared gate.

## CURRENT NEXT STEP — V129 diagnostic

V129 should read only the now-exposed V128 output and characterize the 11 remaining guarded-champion failures without any new held-out evaluation or model search.

Required questions:
- Which failures are regressions relative to V122/V118/V96/V28, and which are shared hard failures?
- How many sit inside versus outside the seven V122 structural groups?
- How many are in rows where the V127 guard fired?
- How are failures distributed by final representation, structural key, selected-for-V112 status, phase and fold?
- Which of the 4/5 bottleneck phases contain the remaining failure and what structural state produced it?

V129 is anatomy only. Any rule suggested by V129 is tainted and must become a separately versioned exploratory challenger on already exposed families before it may earn the new 9-mod-16/1024 reserve.

Safety for V129:
- reads only already-exposed V128 output
- must not reference the new 9-mod-16/1024 reserve
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
The current frozen validated champion is V122 + V127 guard, confirmed by V128 at 309/320 = 96.5625% on a fresh family.
Preserve frozen V17, frozen V122/V124, frozen V127/V128, the protected 949-event candidate, leakage rules, the newly reserved untouched numerators-9-mod-16-over-1024 family, and production-promotion=false.
Continue from V129 without unnecessary pauses.
```
