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

V17 remains immutable. V18–V121 are historical/exposed development or prior confirmation material. V115/V116 and V118/V119 are frozen prior validated-champion checkpoints. Do not reinterpret any exposed family as fresh confirmation.

## Current validated champion — V122, confirmed by V124

V122 is now frozen as the validated rhythm24 champion policy.

Architecture:
- V118 remains the baseline policy: V96 backbone + frozen V115 top-2/7 selective V112 gate + the frozen V118 dangerous-signature exclusion.
- V122 adds seven frozen structural representation switches selected only on exposed V119 development data and corroborated on exposed V116 reverse validation before fresh confirmation.
- Frozen structural groups:
  - anchor / keep-anchor / r4 / lambda1 -> cosine
  - anchor / keep-anchor / r4 / lambda100 -> v112_interactions
  - anchor / keep-anchor / r8 / lambda100 -> v112_interactions
  - broad / revert-broad-to-anchor-high-dispersion / r2 / lambda1 -> cosine
  - tight / keep-tight-high-dispersion / r8 / lambda1 -> base
  - tight / revert-tight-to-anchor-low-dispersion / r4 / lambda1 -> phase_col3
  - tight / revert-tight-to-anchor-low-dispersion / r4 / lambda100 -> base
- No production promotion is allowed.

### V123 corroborative reverse validation on prior V116 family

- reconstructed V118 baseline: 290/320 = 90.6250%
- frozen V122 policy: 307/320 = 95.9375%
- gains/losses vs V118: +19/-2, net +17
- policy-applied rows: 134/320
- corroborative only; not fresh confirmation

### V124 fresh confirmation — SUCCESS

Fresh reserved family consumed for the first time by V124:
- 64 phases, numerators congruent to 5 mod 16 over 1024
- 320 folds total

Result:
- V28: 274/320 = 85.6250%
- V96: 283/320 = 88.4375%
- V115: 289/320 = 90.3125%
- V118: 291/320 = 90.9375%
- V122: 308/320 = 96.2500%
- V122 gains/losses vs V118: +19/-2, net +17
- V122 gains/losses vs V96: +27/-2, net +25
- rescues/regressions vs V28: +36/-2
- structural policy applied: 137/320
- minimum V122 phase passes: 3/5
- bottleneck phases: 0.9423828125 and 0.9580078125
- crosses 95 percent: True
- confirmation success: True
- validated new champion: True
- protected 949-event candidate unchanged: True
- candidate events modified: False
- production promotion allowed: False

Authoritative committed V124 files:
- `public/gomyway-3676-patch-rhythm24-v122-reserved-5mod16-over1024-confirmation-v124.json`
- `public/gomyway-3676-patch-rhythm24-v122-reserved-5mod16-over1024-confirmation-v124-manifest.json`

V122/V124 are frozen. Do not modify them in place.

## Next untouched reserve — reserved BEFORE V125 interpretation

Reserve the following family now, before using V124 outcomes to design another challenger:

`phase_k = (7 + 16*k) / 1024`, for `k = 0..63`.

This is the 64-phase **numerators-7-mod-16-over-1024** family. All numerators are odd, so none reduces to a /512-or-coarser dyadic phase. It is disjoint from the consumed V116 1-mod-16, V119 3-mod-16, and V124 5-mod-16 families.

Do not inspect, evaluate, or reference this reserve in V125 or any exploratory challenger. It may be consumed only after a later architecture is frozen and earns a genuinely fresh confirmation attempt under a predeclared gate.

## CURRENT NEXT STEP — V125 diagnostic

V125 should use only the now-exposed V124 output. It should characterize the 12 remaining V122 failures without any model search or new held-out evaluation. In particular:
- summarize failures by structural key, final representation, selected-for-V112 status, phase and fold;
- identify which failures are regressions relative to V118/V96/V28 and which are shared hard failures;
- identify whether failures concentrate inside or outside the seven V122 structural switches;
- characterize the two 3/5 bottleneck phases;
- keep the newly reserved 7-mod-16/1024 family completely untouched.

V125 is anatomy only. Any rule suggested by V125 is tainted and must become a separately versioned exploratory challenger on already exposed families before it may earn the new 7-mod-16/1024 reserve.

Safety for V125:
- reads only already-exposed V124 output
- must not reference the new 7-mod-16/1024 reserve
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
V122 is frozen and validated by V124 at 308/320 = 96.2500% on a fresh family.
Preserve frozen V17, frozen V122/V124, the protected 949-event candidate, leakage rules, the newly reserved untouched numerators-7-mod-16-over-1024 family, and production-promotion=false.
Continue from V125 without unnecessary pauses.
```
