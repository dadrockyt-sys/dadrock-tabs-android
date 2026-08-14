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

## Frozen historical reference

V17 remains immutable. Earlier progression V18–V114 is historical/exposed development material. Do not reinterpret any exposed family as fresh confirmation.

## Current validated champion — V115, confirmed by V116

V115 is now frozen as the validated rhythm24 champion architecture.

Development result on the already-exposed 280-fold V56/V57 families:
- V96 backbone: 247/280 = 88.2143%
- V115 selective V112 policy: 251/280 = 89.6429%
- selected for V112: 81/280
- gains vs V96: 6
- losses vs V96: 2
- net vs V96: +4
- rescues vs V28: 13
- regressions vs V28: 0
- gate fraction frozen before confirmation: 2/7

V115 policy:
- V96 backbone remains the default behavior.
- V112 low-band × rhythmic-phase interaction representation is applied only to the top 2/7 of folds ranked by the frozen training-context gate.
- Gate fit uses only previously exposed V56/V57 development data.
- Gate features: training-side low-band envelope statistics plus low-band × p2/p4 rhythmic-phase interactions.

### V116 fresh confirmation — SUCCESS

Fresh reserved family consumed for the first time by V116:
- 64 phases, numerators congruent to 1 mod 16 over 1024
- 320 folds total

Result:
- V28: 274/320 = 85.6250%
- V96: 283/320 = 88.4375%
- V115: 288/320 = 90.0000%
- selected for V112 before held-out evaluation: 92/320
- gains vs V96: 7
- losses vs V96: 2
- net vs V96: +5
- rescues vs V28: 14
- regressions vs V28: 0
- minimum V115 phase passes: 3/5
- minimum V96 phase passes: 3/5
- V115 bottleneck phase: 0.7041015625
- confirmation success: True
- validated new champion: True
- protected 949-event candidate unchanged: True
- candidate events modified: False
- production promotion allowed: False

Authoritative committed V116 files:
- `public/gomyway-3676-patch-rhythm24-v115-reserved-1over1024-stride16-confirmation-v116.json`
- `public/gomyway-3676-patch-rhythm24-v115-reserved-1over1024-stride16-confirmation-v116-manifest.json`

V115/V116 are frozen. Do not modify them in place.

## Recent committed lineage

- `c7e6dbaa` Record V110 low-band cross-source residual predictability
- `d0b0694f` Add V112 low-band phase interaction diagnostic
- `dd43d8ba` Record V111 low-band fallback utility diagnostic
- `376b4fc7` Add V113 rescue-vs-regression anatomy diagnostic
- `965532ce` Record V112 low-band rhythmic-phase interaction diagnostic
- `e239e137` Add V114 cross-source selective V112 gate diagnostic
- `514c6aeb` Record V113 V112 rescue regression anatomy
- `f36ae504` Add V115 selective V112 top-2over7 challenger
- `725cf972` Add V116 fixed V115 compact fresh confirmation
- `582442a9` Record V114 cross-source selective V112 gate diagnostic
- `2de578b2` Record regenerated V115 selective V112 challenger
- `078c7f98` Record V116 confirmation of validated V115 champion

## Next untouched reserve — reserve BEFORE V117 interpretation

Reserve the following family now, before using V116 outcomes to design another challenger:

`phase_k = (3 + 16*k) / 1024`, for `k = 0..63`.

This is the 64-phase **numerators-3-mod-16-over-1024** family. All numerators are odd, so none reduces to a /512-or-coarser dyadic phase. It is disjoint from V116's numerators-1-mod-16 family.

Do not inspect, evaluate, or reference this new reserve in V117 or any exploratory challenger. It may be consumed only after a later architecture is frozen and earns a genuinely fresh confirmation attempt under a predeclared gate.

## CURRENT NEXT STEP — V117 diagnostic

V117 should use only the now-exposed V116 confirmation output for diagnosis. It should characterize:
- the 7 V115 gains vs V96,
- the 2 V115 losses vs V96,
- the 0.7041015625 bottleneck phase,
- gate-score / chosen-model / q-bucket / decision structure of those changed folds,
- whether the two losses share a narrow, pre-actionable signature that can later be tested on exposed data.

V117 must not choose a new production threshold or gate from held-out labels. It is anatomy only. Any rule suggested by V117 is tainted and must become a separately versioned exploratory challenger on exposed families before it may earn the new 3-mod-16/1024 reserve.

Safety for V117:
- reads only already-exposed V116 output
- must not reference the new 3-mod-16/1024 reserve
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
V115 is frozen and validated by V116 at 288/320 = 90.0000% on a fresh family.
Preserve frozen V17, frozen V115/V116, the protected 949-event candidate, leakage rules, the newly reserved untouched numerators-3-mod-16-over-1024 family, and production-promotion=false.
Continue from V117 without unnecessary pauses.
```
