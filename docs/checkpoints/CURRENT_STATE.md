# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families #1–#13 are consumed/sealed. Accepted baseline remains family #10. Family #14 is frozen; policy and search are definitively CPU-proven+sealed. Its one-shot CPU-only live FIT workflow is now created, blob-locked, and PRE-ARM checkpointed below. No live family #14 FIT search has run yet. The next branch commit must be exactly the single frozen trigger; no competing commit is allowed between this checkpoint and that trigger.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`; render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark, not unseen holdout. V5 holdout permanently consumed.
- Split seed 144: 60 fit / 20 validation / 20 canary. FIT constructs/ranks only; later stages gate one locked winner. FIT pitch gain >=0.005; no musical regression; critical delta <=0; PDF fidelity 1.0. Failure => accepted-baseline fallback, never alternate.
- No Modal/L4/GPU without fresh explicit authorization. `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.

## Permanent progress-percentage reporting
- Headline accepted Rhythm percentage = Pitch Content F1 ×100. Current accepted family #10 = **35.4%** (`0.35406698564593303`).
- Also: **Pitch + timing 6.7%**, **String/fret + timing 5.5%**, **Chord/voicing 5.8%**, **Measure coverage 100%**, **PDF event fidelity 100%**.
- Keep dimensions separate. On accepted-baseline change, recompute all percentages and percentage-point deltas immediately.

## Accepted baseline — LOCKED / UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- Manifest commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- 1144 events / 113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity 1.0.
- Full gold: critical 1712; pitch 0.35406698564593303; pitch/timing 0.06698564593301436; string/fret/timing 0.05454545454545454; chord/voicing 0.0580511402902557; coverage 1.0.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
- Families #1–#13 are consumed/sealed. Never use their candidate rankings, runners-up, gate outcomes, candidate identities, or observed candidate behavior to shape/rank a successor family.
- Family #11 report blob `9d1b46d8fcc45465a55f018363fd32e22e120068`; family #10 fallback.
- Family #12 run `32999986666` / job `98278991573`; report blob `9a4d17622047db77e373a21c40036adc42297482`; no FIT winner; sealed.
- Family #13 run `33008934470` / job `98309848693`; report blob `bb95b99f64a757b4bc96c86f4392e1e453e3b721`; no FIT winner; sealed. Its neutral workflow mechanics were reused only as infrastructure precedent.

## Current accepted-baseline FIT residual — CURRENT / SEALED
- `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`; blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.
- Aggregate topology: g1-r0=203, g2-r0=79, g3-r0=12, g5-r0=1; g2-r1=26; shared generated-heavier=27; shared reference-heavier=57; generated-only=295; reference-only=180.
- Aggregate mechanisms: pitch FP467, pitch FN418, same-onset extra generated slots431, same-onset missing reference slots382.
- Baseline unchanged, so diagnostic remains current until a promotion actually occurs.

## Family #14 — FROZEN CONTRACT
- Shape: **atomic shared dyad-to-singleton surplus-note prune**.
- FIT construction: exact 2 generated /1 reference same onset; exactly one generated exact-MIDI match is immutable survivor; other generated note is FIT-labeled surplus target.
- Exclude zero/two exact matches, duplicate source identities, invalid positions, linked pitch semantics, or referenced prune target.
- Support **3**, cap **256**, frozen.
- Rule: one structural onset context + two sorted `(sourceStringIndex, sourcePitchClass)` identities + unique prune identity that is a dyad member.
- Runtime reference-free; exact dyad/context/identity only; delete one prune member; survivor byte-for-byte/source-order immutable. No pitch/timing/string/fret rewrite or onset creation.
- Preserve exact 113 generated measures. FIT constructs/ranks only; one locked winner; validation/canary gate; any failure/no winner => family #10 fallback; never alternate.
- Promotion: FIT pitch gain >=0.005, no musical regression, critical delta <=0, exact 113 measures, independent PDF event fidelity1.0.

## Family #14 CPU proofs — COMPLETE / SUCCESS / SEALED
- Policy `modal/v144_rhythm_shared_dyad_surplus_prune_policy.py` blob `1f6cc7fcaf2d4ac7838b48b839c617b04cb1c34e`; tests blob `38d6804560755fcb0bcf26eeda5e1a5b77f31231`.
- Policy proof run `33025027635`, job `98364261256`: SUCCESS; proof blob `cafd2b51e75ba0895dde995f0730ef8554976516`; automation sealed.
- Search `validation/v144_rhythm_calibration/search_atomic_shared_dyad_surplus_prunes.py` blob `dd02c492ecfef26bbb15e8d345346ff75bb5fa30`; tests blob `77758ead57a2735ba653bbba64e78c4124d34798`; schema14427.
- Search synthetic proof run `33025495483`, job `98365711683`: SUCCESS; proof blob `73c2e863f5dc8404fab8985d05f360a2093f588c`; labels read=false; live search=false; automation sealed by workflow deletion `01e10bb92a4ec8a99286284692c848d197dcf733` and trigger deletion `0341e34c6793fe545f112befbef859833da12361`.

## Family #14 one-shot live FIT execution — PRE-ARMED / NOT TRIGGERED
- Workflow path `.github/workflows/v144-atomic-shared-dyad-surplus-prune-search.yml`.
- Workflow creation commit **`54e2bf16509e88ed8c18429788880269288117f4`**.
- Exact workflow blob **`44a5f44094a5c639b8ffef61938eb8be155bc179`**.
- Trigger path frozen as `debug/v144-rhythm-calibration/candidates/.v144-atomic-shared-dyad-surplus-prune-trigger`.
- Exact trigger commit message frozen as `v144 execute atomic shared dyad surplus prune one-shot`.
- Workflow is CPU-only Ubuntu/Python; no Modal/GPU.
- It rejects any trigger commit changing more than the trigger file, rejects preexisting report, verifies immutable V5/gold/baseline/residual/policy/search/proof/supporting dependency identities, verifies policy/search CPU proof IDs, verifies its own blob from the trigger, and requires `preArmCheckpointCommit == HEAD^` plus the workflow blob appearing in that parent checkpoint.
- It reruns fixed synthetic/staged/measure/reconstruction tests before opening live FIT search.
- Live search runs exactly once with support3/cap256. Candidate construction/ranking is FIT-only. Validation/canary open only for one FIT-locked candidate.
- It validates frozen report semantics, independently freezes/revalidates locked render events, re-proves PDF event fidelity1.0, applies final no-regression/critical<=0/coverage1.0/113-measure/count-change invariants, falls back to family #10 on any gate/invariant failure, rechecks immutables, and persists **only** `debug/v144-rhythm-calibration/candidates/atomic-shared-dyad-surplus-prune-search.json`.
- The workflow records GitHub one-shot execution identity in the report. After execution, family #14 is consumed regardless of outcome.
- **The trigger file does not exist yet. No family #14 candidate outcome has been observed.**

## Fixed supporting dependency identities
- Residual analyzer `27ac8699279db8fc0208d067479ad3751da1a630`; singleton reconstruction search `70880d26418d907cc702233af37bcc4b643e3a57`; singleton policy `1e05e66a3523f98944370837a59e5d6e7293f9ac`.
- Pitch-position shift `f69755b61bdcdf3a669847ce7e425289b4b0927f`; pitch shift `d9998c59acddba070069668d62bcb1c3cdaf2b05`; triple conjunction `ef9768a127472d7ce0746fdf21164d33e5117ea4`.
- Staged selector `d176a9a69366e192e6fa75bc1039661e977f0bfa`; measure guard `4a1364204dd1e720c09d835ec3995c165047de98`; context split `2da58508f2132660ad317ee63d5cb043d58285f0`; config `9b93205cb47bc7718685b9d41b263778107801ce`.
- Split analysis `1569bf01554be345ca9199a85f700db7743501a5`; signature prune scoring `699dd1a16725ecf11797e42829aa409ee5909000`; selected scoring `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`.
- Canonical `088d44827fb23e20d9aeeb4944a672989af5846c`; scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`; freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`; PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`; render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.

## EXPLICIT NEXT STEPS — CONTINUATION CONTRACT
1. This checkpoint commit must become the immediate parent of the single live trigger. Do not make any other branch commit first.
2. Create exactly one trigger file at the frozen path/message, containing baseline identities, frozen policy/search/proof blobs and CPU run/job IDs, workflow blob `44a5f440...`, this pre-arm checkpoint commit, support3/cap256, FIT-only/staged/count-change/runtime-reference/GPU/replay flags.
3. After trigger creation, make no competing branch commits until the one-shot workflow persists its report or definitively fails.
4. Never retry/retrigger family #14. One-shot observation consumes/seals the family regardless of outcome.
5. If report promotes family #14, update accepted baseline/scorer percentages and immediately compute a new aggregate accepted-baseline FIT residual before any successor design. If not promoted, family #10/scorers/current residual remain unchanged.
6. Seal/delete one-shot workflow and trigger after result is captured; preserve report and proofs; checkpoint final state.
7. Never use Modal/L4/GPU without fresh explicit authorization; never touch main/Production/frontend/Bass/Lead.

## Current stop point
- Accepted baseline family #10 / `4e6f9f...`.
- Scorer view: **Pitch Content35.4%**, Pitch+timing6.7%, String/fret+timing5.5%, Chord/voicing5.8%, coverage100%, PDF fidelity100%.
- Family #14 policy/search CPU proofs SUCCESS+SEALED.
- Family #14 one-shot workflow exact blob **`44a5f44094a5c639b8ffef61938eb8be155bc179`** is PRE-ARMED; trigger absent; no live FIT search yet.
- **Next commit must be the one trigger, and nothing else.**
