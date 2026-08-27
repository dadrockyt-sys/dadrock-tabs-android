# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families #1–#14 are now consumed/sealed from candidate reuse; accepted baseline remains family #10. Family #14 one-shot executed exactly once and completed successfully at the infrastructure level, but produced no qualifying FIT rule, so validation/canary/full stayed closed and family #10 remained selected. No scorer changed. Immediate next step: delete/seal the family #14 one-shot workflow+trigger, preserve its report/proofs, checkpoint, then any successor must be preregistered only from the still-current aggregate accepted-baseline FIT residual—not from family #14's observed outcome.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`; render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark, not unseen holdout. V5 holdout permanently consumed.
- Split seed 144: 60 fit /20 validation /20 canary. FIT constructs/ranks only; later stages gate one locked winner. FIT pitch gain >=0.005; no musical regression; critical delta <=0; PDF fidelity1.0. Failure => family #10 fallback, never alternate.
- No Modal/L4/GPU without fresh explicit authorization. `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.

## Permanent progress-percentage reporting
- Current accepted family #10: **Pitch Content 35.4%** (`0.35406698564593303`), **Pitch + timing 6.7%** (`0.06698564593301436`), **String/fret + timing 5.5%** (`0.05454545454545454`), **Chord/voicing 5.8%** (`0.0580511402902557`), **Measure coverage 100%**, **PDF event fidelity 100%**.
- Keep dimensions separate; never invent a combined overall percentage. Recompute all percentages and percentage-point deltas only when accepted baseline changes.

## Accepted baseline — LOCKED / UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- Manifest commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- 1144 events /113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity1.0.
- Full gold critical1712; pitch0.35406698564593303; pitch/timing0.06698564593301436; string/fret/timing0.05454545454545454; chord/voicing0.0580511402902557; coverage1.0.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
- Families #1–#14 are consumed. Never use their candidate rankings, runners-up, gate outcomes, candidate identities, or observed candidate behavior to shape/rank a successor.
- Family #12 run `32999986666` / job `98278991573`; no FIT winner; sealed.
- Family #13 run `33008934470` / job `98309848693`; no FIT winner; sealed.
- Family #14 details/results are sealed below. Its observed zero-rule outcome must not shape/rank family #15 or later.

## Current accepted-baseline FIT residual — STILL CURRENT
- `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`; blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.
- Aggregate topology: g1-r0=203, g2-r0=79, g3-r0=12, g5-r0=1; g2-r1=26; shared generated-heavier=27; shared reference-heavier=57; generated-only=295; reference-only=180.
- Aggregate mechanisms: pitch FP467, pitch FN418, same-onset extra generated slots431, same-onset missing reference slots382.
- Because accepted baseline did not change through family #14, this residual remains the current permissible aggregate evidence. Do not replace it yet.

## Family #14 — CONSUMED / ONE-SHOT COMPLETE / NO SCORE CHANGE
### Frozen contract
- Atomic shared dyad-to-singleton surplus-note prune; exact g2-r1 FIT onset with one exact-MIDI survivor; support3/cap256; one structural context + sorted dyad source identities + unique prune identity; runtime reference-free; remove one member only; survivor immutable; exact113 measures; deterministic family #10 fallback.

### Proven implementation
- Policy blob `1f6cc7fcaf2d4ac7838b48b839c617b04cb1c34e`; policy tests blob `38d6804560755fcb0bcf26eeda5e1a5b77f31231`.
- Policy proof run `33025027635` / job `98364261256`: SUCCESS; proof blob `cafd2b51e75ba0895dde995f0730ef8554976516`; automation sealed.
- Search blob `dd02c492ecfef26bbb15e8d345346ff75bb5fa30`; search tests blob `77758ead57a2735ba653bbba64e78c4124d34798`; report schema14427.
- Search synthetic proof run `33025495483` / job `98365711683`: SUCCESS; proof blob `73c2e863f5dc8404fab8985d05f360a2093f588c`; automation sealed.

### One-shot execution — EXACTLY ONCE
- One-shot workflow `.github/workflows/v144-atomic-shared-dyad-surplus-prune-search.yml`; creation commit `54e2bf16509e88ed8c18429788880269288117f4`; blob **`44a5f44094a5c639b8ffef61938eb8be155bc179`**.
- Required pre-arm checkpoint commit **`d896af950c84f608fe6ab66edf6522ad80419c12`**.
- Exact trigger commit **`949a630a6b631c5fde0cb5cdf916dc03c306a116`**; exact message `v144 execute atomic shared dyad surplus prune one-shot`; trigger was sole changed path and must never be changed/retriggered.
- One-shot workflow run **`33025902769`**, job **`98367025091`**, attempt1: **COMPLETED / SUCCESS**. Every step succeeded: exact trigger + immutable implementation proof, fixed search/staged gates, staged semantics verification, independent PDF-event identity, final invariant wrapper, immutable recheck, report-only persistence.
- Report `debug/v144-rhythm-calibration/candidates/atomic-shared-dyad-surplus-prune-search.json`; persistence commit **`2ebb31c85d4c164b24f929818d402c7fc763b49d`**; report blob **`a13df8e17ae2c813d4602dd10dd642327a5d2b75`**.
- Result: `rankedRuleCount=0`; `evaluatedCandidateCount=0`; FIT lock `accepted-v144-baseline`; locked reason `deterministic-no-prune-fallback`; selected reason `fit-no-qualified-atomic-shared-dyad-surplus-prune-candidate`; `stoppedAt=fit`; validation=null; canary=null; fullCalibration=null; splitPromotionAllowed=false; calibrationPromotionAllowed=false.
- Locked result remains exactly 1144 events /113 generated measures / SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; removedEventCount=0; removedOnsetCount=0; measure set preserved.
- Independent locked PDF proof passed: `pdfEventFidelity=1.0`, same event count/SHA, reference not opened during PDF fidelity check.
- Safety: runtimeReferenceInputUsed=false; modalGpuInvoked=false; mainModified=false; productionModified=false; v5Modified=false.
- **Accepted baseline remains family #10; no scorer percentage changed. Family #14 is consumed regardless of the zero-rule result.**
- Immediate sealing still pending at this checkpoint: delete one-shot workflow and trigger, preserve report/proofs.

## Fixed dependency identities
- Residual analyzer `27ac8699279db8fc0208d067479ad3751da1a630`; singleton reconstruction search `70880d26418d907cc702233af37bcc4b643e3a57`; singleton policy `1e05e66a3523f98944370837a59e5d6e7293f9ac`.
- Pitch-position shift `f69755b61bdcdf3a669847ce7e425289b4b0927f`; pitch shift `d9998c59acddba070069668d62bcb1c3cdaf2b05`; triple conjunction `ef9768a127472d7ce0746fdf21164d33e5117ea4`.
- Staged selector `d176a9a69366e192e6fa75bc1039661e977f0bfa`; measure guard `4a1364204dd1e720c09d835ec3995c165047de98`; context split `2da58508f2132660ad317ee63d5cb043d58285f0`; config `9b93205cb47bc7718685b9d41b263778107801ce`.
- Split analysis `1569bf01554be345ca9199a85f700db7743501a5`; signature prune scoring `699dd1a16725ecf11797e42829aa409ee5909000`; selected scoring `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`.
- Canonical `088d44827fb23e20d9aeeb4944a672989af5846c`; scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`; freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`; PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`; render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.

## EXPLICIT NEXT STEPS — CONTINUATION CONTRACT
1. Stay only on `v143-contextual-prune-lobo`; never main/Production/frontend/Bass/Lead; no Modal/L4/GPU without fresh explicit authorization.
2. Delete/seal family #14 one-shot workflow `44a5f440...` and exact trigger from `949a630a...`; preserve report `a13df8e...` and CPU proof JSONs; checkpoint deletion commits.
3. Never rerun/retrigger/reselect/retune family #14. Families #1–#14 are consumed.
4. Accepted baseline remains family #10 and percentages remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100** in their separate dimensions.
5. Current aggregate residual `b9794a7b...` remains current because baseline did not change.
6. Any family #15 design must use only permitted aggregate accepted-baseline evidence + independent structural reasoning. Do not use family #14 zero-rule outcome, candidate identity, or behavior.
7. Preregister/freeze family #15 before any family #15 candidate search; then CPU-only policy/test proof, checkpoint; FIT-only search/test proof, checkpoint; only then one-shot live FIT execution.

## Current stop point
- Accepted baseline: family #10 / `4e6f9f...`; scorer percentages unchanged.
- Families #1–#14 consumed; family #14 live one-shot report captured at blob `a13df8e...` with zero qualifying FIT rules.
- Family #14 one-shot workflow+trigger are still present solely pending immediate deletion/sealing.
- Safe continuation: seal those two files, checkpoint, then shape family #15 only from aggregate residual evidence.
