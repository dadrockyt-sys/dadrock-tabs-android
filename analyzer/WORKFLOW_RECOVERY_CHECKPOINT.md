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

V17 remains immutable. V18–V133 are historical/exposed development, diagnostics, reverse-validation, or prior confirmation material. V115/V116, V118/V119, V122/V124, V127/V128, and V133/V134 are frozen checkpoints. Do not reinterpret any exposed family as fresh confirmation.

## Current validated champion — V133 selective conjunction guard, confirmed by V134

The current validated rhythm24 champion is the frozen V128 architecture plus the frozen V133 selective intervention, freshly confirmed by V134.

### Frozen architecture

Base validated architecture carried forward from V128:
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
- V133 selective intervention:
  - target structural key: anchor / keep-anchor / r4 / lambda1
  - candidate representation: `v112_interactions`
  - selector: `gateScore <= -5.4 AND phase < 0.5`
  - otherwise retain frozen V128 behavior unchanged
- No production promotion is allowed.

### V134 fresh confirmation — SUCCESS

Fresh 9-mod-16-over-1024 family, 64 phases / 320 folds:
- frozen V128 baseline: 309/320 = 96.5625%
- V134 selective champion: 311/320 = 97.1875%
- +2/-0 vs V128, net +2
- selective intervention applied rows: 5/320
- minimum V134 phase passes: 4/5
- confirmation success: True
- validated new champion: True
- reserved untouched phases consumed: True
- new tuning performed: False
- protected 949-event candidate unchanged: True
- production promotion allowed: False

Authoritative files:
- `public/gomyway-3676-patch-rhythm24-v133-conjunction-guard-reserved-9mod16-over1024-confirmation-v134.json`
- `public/gomyway-3676-patch-rhythm24-v133-conjunction-guard-reserved-9mod16-over1024-confirmation-v134-manifest.json`

V133/V134 are now frozen. Do not modify them in place.

## Motivating validated-score milestones

These percentages are fresh-confirmed validated checkpoints, not exposed-development ceilings:
- V118/V119 era: 291/320 on the later V124 comparison family = 90.9375% baseline reference
- V122/V124: 308/320 = 96.2500%
- V127/V128: 309/320 = 96.5625%
- V133/V134: 311/320 = 97.1875% — CURRENT VALIDATED CHAMPION

Current fresh-family error count: 9/320.

## Post-V128 exposed development leading to V134

### V129
- V128 failure anatomy on 11 remaining failures.
- No fresh reserve referenced.

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
- Therefore broad structural replacement was rejected.

### V132
- Near-neutral intervention selectivity anatomy.
- For target `anchor / keep-anchor / r4 / lambda1`, candidate `v112_interactions`:
  - 2 gains clustered at early phase and stronger-negative gate score
  - 3 losses clustered at late phase and weaker gate score
- No guard chosen by V132.

### V133 corroborative selective-guard test

Target structural key:
- anchor / keep-anchor / r4 / lambda1

Candidate representation:
- `v112_interactions`

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

The conjunction was frozen for V134 because it reproduced the full +2/-0 benefit on both exposed families while modifying the fewest rows.

## Consumed fresh confirmation families

The following are permanently exposed/consumed and must never be reused as fresh confirmation:
- 1-mod-16-over-1024
- 3-mod-16-over-1024
- 5-mod-16-over-1024
- 7-mod-16-over-1024
- 9-mod-16-over-1024

## Next untouched reserve — PREDECLARED BEFORE V134 FAILURE INTERPRETATION

`phase_k = (11 + 16*k) / 1024`, for `k = 0..63`.

This is the 64-phase numerators-11-mod-16-over-1024 family, disjoint from all consumed 1-, 3-, 5-, 7-, and 9-mod-16 families.

It is now sealed. Do not inspect or reference it during V135+ diagnosis/development. It may be consumed only by a future fully frozen confirmation challenger.

## CURRENT NEXT STEP — V135 anatomy only

V134 is frozen and preserved. The 11-mod-16 reserve was declared before interpreting its remaining 9 failures.

V135 should inspect only the already-exposed V134 result and characterize the 9 remaining failures. It must not:
- reference the 11-mod-16 reserve,
- perform production tuning,
- alter V133/V134,
- modify the protected 949-event candidate,
- permit production promotion.

The goal is to determine whether the 9 remaining failures are shared hard failures, representation-rescuable failures, or candidates for another conservative pre-held-out selector.

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
Current validated champion: frozen V128 architecture + V133 conjunction selector, confirmed by V134 at 311/320 = 97.1875%.
V134 fresh 9-mod-16 confirmation: +2/-0 vs V128, minimum phase passes 4/5, validatedNewChampion=True.
The 9-mod-16 family is consumed. The next untouched reserve, 11-mod-16-over-1024, was predeclared before V134 failure interpretation and must remain sealed during V135+ development.
Preserve frozen V17, V122/V124, V127/V128, V133/V134, protected 949-event candidate, leakage rules, and production-promotion=false.
Immediate next step: V135 anatomy-only on the 9 remaining exposed V134 failures.
```
