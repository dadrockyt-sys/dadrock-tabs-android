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

V17 remains immutable. V18–V133 are historical/exposed development, diagnostics, reverse-validation, or prior confirmation material. V115/V116, V118/V119, V122/V124, and V127/V128 are frozen checkpoints. Do not reinterpret any exposed family as fresh confirmation.

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
- V127 guard:
  - structural key: tight / revert-tight-to-anchor-low-dispersion / r4 / lambda1
  - representation: phase_col3
  - condition: `selectedForV112 == true`
  - action: fall back to frozen V118 baseline
- No production promotion is allowed.

### V128 fresh confirmation — SUCCESS

Fresh 7-mod-16-over-1024 family, 64 phases / 320 folds:
- V122 baseline: 307/320 = 95.9375%
- guarded V128: 309/320 = 96.5625%
- +2/-0 vs V122, net +2
- minimum V128 phase passes: 4/5
- confirmation success: True
- validated new champion: True
- protected 949-event candidate unchanged: True
- production promotion allowed: False

Authoritative files:
- `public/gomyway-3676-patch-rhythm24-v127-guarded-v122-reserved-7mod16-over1024-confirmation-v128.json`
- `public/gomyway-3676-patch-rhythm24-v127-guarded-v122-reserved-7mod16-over1024-confirmation-v128-manifest.json`

V122/V124 and V127/V128 are frozen. Do not modify them in place.

## Post-V128 exposed development: V129–V133

All work below uses already-consumed V128 and older consumed V116 data only. None of it is fresh confirmation.

### V129
- V128 failure anatomy on 11 remaining failures.
- No new reserve referenced.

### V130
- Representation rescue ceiling on the 11 exposed failures:
  - base rescues 7/11
  - phase_col3 rescues 5/11
  - full_phase rescues 0/11
  - cosine rescues 0/11
  - v112_interactions rescues 4/11
  - per-failure oracle 318/320 = 99.3750%
  - 2 failures not rescued by any tested representation
- Failure-only diagnostic; losses on the 309 passes were not measured here.

### V131
- Full consumed-V128 gain/loss utility for V130-motivated structural switches.
- No whole structural-group switch was positive:
  - best intervention: +2/-2 net 0
  - next: +2/-3 net -1
- Therefore broad structural replacement is rejected.

### V132
- Near-neutral intervention selectivity anatomy.
- For target `anchor / keep-anchor / r4 / lambda1`, candidate `v112_interactions`:
  - 2 gains cluster at early phase and stronger-negative gate score
  - 3 losses cluster at late phase and weaker gate score
- No guard chosen by V132.

### V133 corroborative selective-guard test

Target structural key:
- anchor / keep-anchor / r4 / lambda1

Candidate representation:
- `v112_interactions` instead of frozen V128 final choice for selected rows

Three selectors were evaluated on consumed V128 and reverse-validated on consumed V116:

1. gate: `gateScore <= -5.4`
   - consumed V128: 309 -> 311, +2/-0, applied 14
   - reverse V116: 309 -> 311, +2/-0, applied 13
2. phase: `phase < 0.5`
   - consumed V128: 309 -> 311, +2/-0, applied 19
   - reverse V116: 309 -> 311, +2/-0, applied 19
3. conjunction: `gateScore <= -5.4 AND phase < 0.5`
   - consumed V128: 309 -> 311, +2/-0, applied 6
   - reverse V116: 309 -> 311, +2/-0, applied 6

V133 chose no selector. For the next frozen challenger, choose the **conjunction** because it reproduces the full +2/-0 benefit on both exposed families while modifying the fewest rows (6), making it the most conservative of the equally successful selectors.

## Next untouched reserve — PREDECLARED BEFORE V129 INTERPRETATION

`phase_k = (9 + 16*k) / 1024`, for `k = 0..63`.

This is the 64-phase numerators-9-mod-16-over-1024 family, disjoint from consumed 1-, 3-, 5-, and 7-mod-16 families.

It remains untouched through V133. Do not inspect or reference it outside the frozen V134 confirmation.

## CURRENT NEXT STEP — V134 fresh confirmation

Freeze the current validated V128 architecture plus exactly one additional selective intervention:

- target key: anchor / keep-anchor / r4 / lambda1
- candidate representation: `v112_interactions`
- selector: `gateScore <= -5.4 AND phase < 0.5`
- otherwise retain frozen V128 behavior unchanged

V134 may consume the predeclared 9-mod-16-over-1024 reserve exactly once.

Predeclared validation gate:
- V134 passes > frozen V128 baseline passes on the same fresh family
- gains vs V128 > losses vs V128
- minimum V134 phase passes >= 3/5
- protected candidate unchanged
- no tuning after held-out evaluation begins
- production promotion remains false

If the gate passes, V134 may set `validatedNewChampion = true`. If it fails, V128 remains champion and the V134 family is permanently consumed/exposed.

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
Current validated champion: frozen V122 + V127 guard, confirmed by V128 at 309/320 = 96.5625%.
V129-V133 are exposed development/reverse-validation only.
V133 showed three equally successful +2/-0 selectors on consumed V128 and reverse V116; the frozen V134 challenger uses the conservative conjunction gateScore <= -5.4 AND phase < 0.5 because it applies to only 6 rows on each exposed family.
The untouched 9-mod-16-over-1024 reserve was predeclared before V129 and remains sealed until V134.
Preserve frozen V17, V122/V124, V127/V128, protected 949-event candidate, leakage rules, and production-promotion=false.
```
