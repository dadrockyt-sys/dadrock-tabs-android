# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration baseline preserved; Families #1–#14 consumed and fully sealed. Family #14 one-shot workflow and trigger are now deleted. Accepted baseline remains family #10. Next work may begin a separate CPU-only V145 Rhythm-decoder architecture using the existing V5 three-way separation output as a protected front end. No Modal/L4/GPU without fresh explicit authorization.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- No Modal/L4/GPU without fresh explicit authorization.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`; render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark, not unseen holdout. V5 holdout permanently consumed.
- Split seed 144: 60 fit /20 validation /20 canary. FIT constructs/ranks only; later stages gate one locked winner. FIT pitch gain >=0.005; no musical regression; critical delta <=0; PDF fidelity1.0. Failure => family #10 fallback, never alternate.

## Permanent progress-percentage reporting
- Current accepted family #10: **Pitch Content 35.4%** (`0.35406698564593303`), **Pitch + timing 6.7%** (`0.06698564593301436`), **String/fret + timing 5.5%** (`0.05454545454545454`), **Chord/voicing 5.8%** (`0.0580511402902557`), **Measure coverage 100%**, **PDF event fidelity 100%**.
- Keep dimensions separate; never invent a combined overall percentage. Recompute only when the accepted baseline changes.

## Accepted baseline — LOCKED / UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- Manifest commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- 1144 events /113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity1.0.
- Full gold critical1712; pitch0.35406698564593303; pitch/timing0.06698564593301436; string/fret/timing0.05454545454545454; chord/voicing0.0580511402902557; coverage1.0.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
- Families #1–#14 are consumed. Never use their candidate rankings, runners-up, gate outcomes, candidate identities, or observed candidate behavior to shape/rank a successor.
- Family #12 run `32999986666` / job `98278991573`; no FIT winner; sealed.
- Family #13 run `33008934470` / job `98309848693`; no FIT winner; sealed.
- Family #14 run `33025902769` / job `98367025091`; infrastructure SUCCESS, zero qualifying FIT rules, accepted baseline unchanged; fully sealed below.

## Current accepted-baseline FIT residual — STILL CURRENT
- `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`; blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.
- Aggregate topology: g1-r0=203, g2-r0=79, g3-r0=12, g5-r0=1; g2-r1=26; shared generated-heavier=27; shared reference-heavier=57; generated-only=295; reference-only=180.
- Aggregate mechanisms: pitch FP467, pitch FN418, same-onset extra generated slots431, same-onset missing reference slots382.
- Because accepted baseline did not change through family #14, this residual remains the current permissible aggregate V144 evidence. Family #14's observed zero-rule outcome must not shape successor rules.

## Family #14 — CONSUMED / FULLY SEALED / NO SCORE CHANGE
- Frozen contract: atomic shared dyad-to-singleton surplus-note prune; exact g2-r1 FIT onset with one exact-MIDI survivor; support3/cap256; runtime reference-free; remove one member only; survivor immutable; exact113 measures; deterministic family #10 fallback.
- Policy blob `1f6cc7fcaf2d4ac7838b48b839c617b04cb1c34e`; tests blob `38d6804560755fcb0bcf26eeda5e1a5b77f31231`; policy proof run `33025027635` / job `98364261256`; proof blob `cafd2b51e75ba0895dde995f0730ef8554976516`.
- Search blob `dd02c492ecfef26bbb15e8d345346ff75bb5fa30`; tests blob `77758ead57a2735ba653bbba64e78c4124d34798`; search CPU proof run `33025495483` / job `98365711683`; proof blob `73c2e863f5dc8404fab8985d05f360a2093f588c`.
- One-shot report `debug/v144-rhythm-calibration/candidates/atomic-shared-dyad-surplus-prune-search.json`; persistence commit `2ebb31c85d4c164b24f929818d402c7fc763b49d`; report blob `a13df8e17ae2c813d4602dd10dd642327a5d2b75`.
- Result: rankedRuleCount0; evaluatedCandidateCount0; stoppedAt=fit; family #10 fallback; validation/canary/full unopened; split/calibration promotion false.
- One-shot workflow deletion commit **`443031fd2294e05b23290c71b0e2b712198d842a`**.
- One-shot trigger deletion commit **`e9536f2b4c122741f50aa317e2bbd332d0a9d03b`**.
- Report and CPU proof JSONs remain preserved. Never rerun/retrigger/reselect/retune Family #14.

## V145 direction — PREREGISTRATION STAGE ONLY
- Goal: get beyond local post-hoc prune/rewrite families by changing the Rhythm architecture while preserving V144 family #10 as immutable fallback.
- Protected front end: reuse current V5 three-way separation benchmark output for Rhythm. Existing V5 is register-gated event separation, not neural stem separation: bass MIDI28-51, rhythm52-63, lead64-76, each analyzer pass protected.
- Proposed architecture: **V5 separated Rhythm evidence -> timing/onset lattice -> pitch-candidate lattice -> constrained guitar-state decoder -> existing event/PDF contract**.
- Primary hurdle suggested by current accepted metrics: Pitch Content35.4% is much higher than Pitch+timing6.7%, so timing/onset alignment must be treated as a first-class decoding stage before string/fret/voicing assignment.
- Initial V145 implementation must be CPU-only and benchmark-only. It must not alter V5 analyzer, family #10 baseline, frontend, Bass, Lead, main, Production, or freeze state.
- Do not perform any Modal/L4/GPU execution until the user explicitly authorizes it after the CPU design/tests are frozen.
- V145 should be developed beside V144, not as Family #15, unless explicitly decided later. This avoids contaminating the consumed-family calibration protocol with an architectural experiment.

## Fixed dependency identities
- Residual analyzer `27ac8699279db8fc0208d067479ad3751da1a630`; singleton reconstruction search `70880d26418d907cc702233af37bcc4b643e3a57`; singleton policy `1e05e66a3523f98944370837a59e5d6e7293f9ac`.
- Pitch-position shift `f69755b61bdcdf3a669847ce7e425289b4b0927f`; pitch shift `d9998c59acddba070069668d62bcb1c3cdaf2b05`; triple conjunction `ef9768a127472d7ce0746fdf21164d33e5117ea4`.
- Staged selector `d176a9a69366e192e6fa75bc1039661e977f0bfa`; measure guard `4a1364204dd1e720c09d835ec3995c165047de98`; context split `2da58508f2132660ad317ee63d5cb043d58285f0`; config `9b93205cb47bc7718685b9d41b263778107801ce`.
- Split analysis `1569bf01554be345ca9199a85f700db7743501a5`; signature prune scoring `699dd1a16725ecf11797e42829aa409ee5909000`; selected scoring `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`.
- Canonical `088d44827fb23e20d9aeeb4944a672989af5846c`; scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`; freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`; PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`; render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.

## EXPLICIT NEXT STEPS — CONTINUATION CONTRACT
1. Stay only on `v143-contextual-prune-lobo`; never main/Production/frontend/Bass/Lead; no Modal/L4/GPU without fresh explicit authorization.
2. Family #14 is fully sealed. Preserve its report/proofs and never replay it.
3. Preserve accepted family #10 baseline and percentages **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
4. Create a frozen CPU-only V145 Rhythm-decoder architecture contract and tests beside V144.
5. Reuse V5 Rhythm-separated output as protected input; do not mutate V5 itself.
6. First CPU targets: deterministic onset-grid/lattice structures, pitch-candidate representation, and guitar-state decoder invariants. Tests must prove no gold/reference input is required at runtime and family #10 fallback is unchanged.
7. Checkpoint after each meaningful V145 implementation/proof step.
8. No live Modal/L4/GPU benchmark until separately and explicitly authorized.

## Current stop point
- V144 accepted baseline family #10 unchanged; Families #1–#14 fully consumed/sealed.
- Family #14 workflow deletion `443031fd...`; trigger deletion `e9536f2b...`.
- Safe next work: CPU-only V145 Rhythm-decoder preregistration and implementation using protected V5 separation output.
