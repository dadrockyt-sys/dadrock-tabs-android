# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families #1–#13 are consumed/sealed. Accepted baseline remains family #10. Family #14 is preregistered/frozen. Its policy/tests are blob-locked. The first branch-scoped CPU proof trigger was created exactly once, but this connector cannot enumerate the resulting private push-triggered Actions run; a local CPU reconstruction of the same family #14 logic/tests passed 9/9 but is intentionally not accepted as the definitive branch proof. No FIT search has run. Next safe step is a self-reporting, branch-scoped CPU proof that verifies exact dependency blobs and writes its own success/run identity only after the exact tests pass, then checkpoint before search implementation.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`; render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark, not unseen holdout. V5 holdout permanently consumed.
- Split seed 144: 60 fit / 20 validation / 20 canary. FIT constructs/ranks only; later stages gate one locked winner. FIT pitch gain >=0.005; no musical regression; critical delta <=0; PDF fidelity 1.0. Failure => accepted-baseline fallback, never alternate.
- No Modal/L4/GPU without fresh explicit authorization. `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.

## Permanent progress-percentage reporting — USER MOTIVATION / UPDATE FORMAT
- In future Rhythm calibration updates, always include easy-to-read scorer percentages alongside technical metrics so progress toward a professionally rendered/transcribed PDF remains visible and motivating.
- Headline Rhythm note-detection percentage = **Pitch Content F1 × 100**. Current accepted family #10 baseline = **35.4%** (`0.35406698564593303`).
- Also report, when relevant: **Pitch + timing 6.7%** (`0.06698564593301436`), **String/fret + timing 5.5%** (`0.05454545454545454`), **Chord/voicing 5.8%** (`0.0580511402902557`), **Measure coverage 100%** (`1.0`), and **PDF event fidelity 100%** (`1.0`).
- Keep these dimensions separate; never invent a combined overall percentage.
- Whenever the accepted baseline changes, recompute every percentage from the new accepted scorer values and report the percentage-point change versus the previous accepted baseline.
- Keep Pitch Content F1 as the headline unless the scorer contract materially changes; explain before changing headline metric.

## Accepted baseline — LOCKED / UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- Manifest commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- 1144 events / 113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity 1.0.
- Full gold: critical 1712; pitch 0.35406698564593303; pitch/timing 0.06698564593301436; string/fret/timing 0.05454545454545454; chord/voicing 0.0580511402902557; coverage 1.0.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
- Families #1–#13 are consumed/sealed.
- Family #11 report blob `9d1b46d8fcc45465a55f018363fd32e22e120068`; no FIT winner; family #10 fallback.
- Family #12 one-shot run `32999986666` / job `98278991573`; report `debug/v144-rhythm-calibration/candidates/atomic-generated-only-dyad-onset-prune-search.json`; report blob `9a4d17622047db77e373a21c40036adc42297482`; no FIT winner; validation/canary/full stayed closed; workflow deleted `ff854c37b98fca82eb1a1c0552cfbaa382bcdf6e`; trigger deleted `994164b4d760d62098bbcb2cbae38dfdc95d4a55`.
- Family #13 details are sealed below.
- Never use consumed-family candidate rankings, runners-up, gate outcomes, candidate identities, or observed candidate behavior to shape/rank a successor family.

## Current accepted-baseline FIT residual diagnostic — SEALED / CURRENT
- `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`; blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.
- Aggregate topology includes: g1-r0=203, g2-r0=79, g3-r0=12, g5-r0=1; g2-r1=26; shared generated-heavier onsets=27; shared reference-heavier onsets=57; generated-only onsets=295; reference-only onsets=180.
- Aggregate mechanism counts include 467 pitch-content false-positive notes, 418 pitch-content false-negative notes, 431 same-onset extra generated slots, and 382 same-onset missing reference slots.
- Family #13 did not change the accepted baseline, therefore this diagnostic remains the current aggregate-only accepted-baseline residual. Do **not** create a replacement diagnostic yet.
- Any successor family must be preregistered from permitted aggregate evidence only, without inspecting/using consumed-family candidate behavior.

## Family #14 — PREREGISTERED / FROZEN / POLICY IMPLEMENTED / SEARCH NOT RUN
### Independent structural rationale
- Family shape was selected only from the still-permitted aggregate accepted-baseline residual and independent structural reasoning, not from any consumed-family candidate result.
- The residual contains **26 `g2-r1` shared onsets** and **27 shared generated-heavier onsets**. A generated-heavy shared onset can contain one correct note plus one surplus note; deleting only a demonstrably surplus member is materially distinct from whole-onset generated-only pruning and preserves the shared onset.
- No family #13 zero-candidate result, ranking, candidate identity, or behavior was used to choose this family.

### Frozen family contract
- Name/shape: **atomic shared dyad-to-singleton surplus-note prune**.
- FIT construction unit: an onset with exactly **2 generated notes / 1 reference note**, where exactly one generated note has exact MIDI equality with the sole reference note. The exact-MIDI-matched generated note is the immutable survivor; the other generated note is the FIT-labeled surplus correction target.
- Ambiguous cases are excluded: zero exact-MIDI matches, two exact-MIDI matches, duplicate/indistinguishable source identities, invalid source positions, linked pitch semantics, or a prune target referenced by another event.
- Minimum FIT correction support **3**, maximum candidate rules **256**; frozen before any family #14 search.
- Rule identity: exactly one allowed structural onset context signature + the two sorted source note identities `(sourceStringIndex, sourcePitchClass)` + the specific surplus/prune source identity. The prune identity must be exactly one member of the dyad identity and must uniquely identify one onset member.
- Runtime application is **reference-free**. A rule may act only on an exact two-note generated onset whose structural context and complete dyad identity match the frozen rule; it removes only the uniquely identified surplus member. The survivor is otherwise byte-for-byte/source-order immutable.
- Runtime reference input is forbidden. No pitch shifting, timing shifting, string/fret rewriting, onset creation, or survivor mutation is permitted.
- Safety guards: source positions valid under the fixed tuning; prune target has no pitch linkage; prune target is not referenced by another event; the operation must not erase a generated measure. Result must preserve exactly **113 generated measures**.
- Candidate construction/ranking is FIT-only. Validation/canary may gate only one locked FIT winner. Any failure or no qualifying FIT winner => deterministic family #10 fallback; never alternate.
- Promotion gates remain unchanged: FIT Pitch Content F1 gain >=0.005, no musical regression, critical delta <=0, exact 113-measure coverage, independent PDF event fidelity 1.0.

### Family #14 implementation/proof status
- Policy path `modal/v144_rhythm_shared_dyad_surplus_prune_policy.py`; blob **`1f6cc7fcaf2d4ac7838b48b839c617b04cb1c34e`**; creation commit `3833c7dc08f0ae8366132b3e7268f3b22d876767`.
- Synthetic policy tests path `modal/tests/test_v144_rhythm_shared_dyad_surplus_prune_policy.py`; blob **`38d6804560755fcb0bcf26eeda5e1a5b77f31231`**; creation commit `38ebdf635c5ae3673d5eebc58466f887c75a7a5b`.
- First one-use CPU proof workflow path `.github/workflows/v144-shared-dyad-surplus-prune-policy-cpu.yml`; blob **`ab443d87a53d7affdba23b86f22ec4a4f2035da8`**; creation commit `3ef18442ac8ca12b681f09f7c08d1af8daabf80c`.
- First trigger path `debug/v144-rhythm-calibration/triggers/shared-dyad-surplus-prune-policy-cpu.txt`; exact trigger commit **`221d5edb332746b41a24b21f7fd69a030f260258`**. Trigger was created once and must not be changed/retriggered.
- Limitation: the available connector cannot enumerate private push-triggered workflow runs for this repository; classic commit status for `221d5edb...` returned no status entries, which is inconclusive rather than a pass/fail.
- Independent local CPU reconstruction of the family #14 policy behavior and synthetic cases passed **9/9 tests**. Because that reconstruction did not execute the exact repository blobs in an authenticated checkout, it is supporting evidence only and is **not** the definitive blob proof.
- Exact direct dependencies are still `modal/v144_rhythm_context_split_policy.py` blob `2da58508f2132660ad317ee63d5cb043d58285f0` and `modal/v144_rhythm_pitch_shift_policy.py` blob `d9998c59acddba070069668d62bcb1c3cdaf2b05`.
- Definitive proof requirement is now explicit: a new self-reporting CPU-only workflow must verify the exact policy/test/dependency blobs, compile and run the exact unittest module, and only on success write a proof result containing its trigger SHA and run identity back to this branch. No FIT data/search may be accessed by that proof.
- Next planned implementation paths after definitive CPU proof: `validation/v144_rhythm_calibration/search_atomic_shared_dyad_surplus_prunes.py` and `modal/tests/test_v144_rhythm_shared_dyad_surplus_prune_search.py`.
- **Do not run FIT search until the definitive CPU-only policy proof is complete and checkpointed.**

## Family #13 — CONSUMED / SEALED / NO SCORE CHANGE
### Frozen family
- Shape: **atomic exact-three-note generated-only whole-onset prune**.
- Construction: exactly 3 generated notes / 0 reference notes at one FIT onset.
- Support **3**, cap **256**, frozen before search.
- Rule identity: one structural onset context + three sorted `(sourceStringIndex, sourcePitchClass)` identities.
- Atomic all-3 deletion only; runtime reference forbidden; linked/referenced/invalid-position/measure-erasing targets ineligible; survivors immutable/source-ordered.
- Count-changing allowed only with exact 113 generated measures. Deterministic family #10 fallback required.

### Preregistered implementation proofs
- Policy `modal/v144_rhythm_generated_only_triad_prune_policy.py`; blob `622c839d0a833c3541007309ebf1203f1547b365`.
- Policy tests `modal/tests/test_v144_rhythm_generated_only_triad_prune_policy.py`; blob `5adbcd39aacc181a6c0917654e754b582f8cca2e`; definitive policy CPU proof run `33006494479` / job `98301477632`: SUCCESS; never rerun.
- Search `validation/v144_rhythm_calibration/search_atomic_generated_only_triad_prunes.py`; blob `e262057db95b297c9dc411f963476bae593553f1`; report schema `14425`.
- Search tests `modal/tests/test_v144_rhythm_generated_only_triad_prune_search.py`; blob `a5238673b466cbba6f69c6fa17587ebdb2d3402e`.
- Broad CPU workflow blob `94b546cf0b3a2ab2bc3a15d0a292a09c2bb6fb01`; definitive search CPU proof run `33007127855` / job `98303667684`: SUCCESS; never rerun.

### One-shot execution — EXACTLY ONCE
- One-shot workflow path `.github/workflows/v144-atomic-generated-only-triad-onset-prune-search.yml`; creation commit `318fc7bfcaee75b10d9ae70eb64a50175ea1a119`; exact workflow blob `b319441e8225513c510d6f46c19ccce9cd055662`.
- Required pre-arm checkpoint commit `174b2254761b1d0dccdf27107d73ce88b17b8ff0` recorded the exact workflow blob before trigger creation.
- Exact trigger commit SHA `2477a1e15a455edf6108ecf6e67070c5e47ddc0c`; exact message `v144 execute atomic generated-only triad onset prune one-shot`; trigger changed exactly one path.
- One-shot run **`33008934470`**, job **`98309848693`**, exact trigger SHA `2477a1e15a455edf6108ecf6e67070c5e47ddc0c`: SUCCESS. All steps completed successfully: immutable identity verification, fixed family #13 search, staged semantics proof, independent PDF-event identity, final invariant wrapper, immutable recheck, report-only persistence.
- Report path `debug/v144-rhythm-calibration/candidates/atomic-generated-only-triad-onset-prune-search.json`.
- Report persistence commit `e9bc29ada3a0e21250006d11735488857340395d`; report blob **`bb95b99f64a757b4bc96c86f4392e1e453e3b721`**.
- Report result: `rankedRuleCount=0`, `evaluatedCandidateCount=0`, locked `accepted-v144-baseline`, locked reason `deterministic-no-prune-fallback`, `stoppedAt=fit`, validation/canary/full calibration all remained closed, `calibrationPromotionAllowed=false`.
- Locked baseline remained 1144 events / 113 generated measures / SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; removedEventCount=0; removedOnsetCount=0.
- Independent locked PDF proof passed with `pdfEventFidelity=1.0`; runtime-reference false; Modal GPU false; V5/main/Production unchanged.
- Workflow deleted/sealed commit `e6195eab074d44d1a5d4bb34722e8a0a3f4a64bd`.
- Trigger deleted/sealed commit `142bdfad0a9d3be628de2fb0e18e9701c1df9f57`.
- **Never rerun/retrigger/retry family #13.** Do not use its zero-candidate outcome to shape/rank the next family.

## Verified one-shot dependency identities used for family #13
- Accepted residual analyzer `27ac8699279db8fc0208d067479ad3751da1a630`.
- Singleton reconstruction search `70880d26418d907cc702233af37bcc4b643e3a57`; singleton policy `1e05e66a3523f98944370837a59e5d6e7293f9ac`.
- Pitch-position shift `f69755b61bdcdf3a669847ce7e425289b4b0927f`; pitch shift `d9998c59acddba070069668d62bcb1c3cdaf2b05`; triple conjunction `ef9768a127472d7ce0746fdf21164d33e5117ea4`.
- Staged selector `d176a9a69366e192e6fa75bc1039661e977f0bfa`; measure guard `4a1364204dd1e720c09d835ec3995c165047de98`; context split `2da58508f2132660ad317ee63d5cb043d58285f0`; config `9b93205cb47bc7718685b9d41b263778107801ce`.
- Split analysis `1569bf01554be345ca9199a85f700db7743501a5`; signature prune scoring `699dd1a16725ecf11797e42829aa409ee5909000`; selected candidate scoring `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`.
- Canonical `088d44827fb23e20d9aeeb4944a672989af5846c`; scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`; freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`; PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`; render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.
- Historical filename assumption corrected: current freeze dependency is `validation/rhythm_holdout/freeze_rhythm_analysis.py`; PDF verifier is `validation/rhythm_holdout/verify_pdf_event_fidelity.py`; render contract is `lib/v143RenderContract.js`.

## EXPLICIT NEXT STEPS — CONTINUATION CONTRACT
1. Re-read this checkpoint and stay on `v143-contextual-prune-lobo` only.
2. Never rerun/retrigger/reselect/retune families #1–#13 or established CPU proofs. Do not alter/retrigger the first family #14 trigger `221d5edb...`.
3. Accepted baseline remains family #10; headline scorer remains **35.4% Pitch Content F1**. Do not claim a gain from family #13 or family #14 unless all gates pass and the accepted baseline actually changes.
4. Current aggregate residual diagnostic `b9794a7b...` remains valid/current because baseline did not change.
5. Family #14 is frozen exactly as preregistered above. Do not retune its shape/support/cap/rule identity after looking at family #14 candidate outcomes.
6. Build/blob-lock/checkpoint one self-reporting CPU proof workflow that verifies exact family #14 policy/test/dependency blobs, then trigger it once. Accept proof only if its success file appears and identifies the exact trigger/run. Seal/checkpoint the proof before search implementation.
7. Only after definitive policy proof succeeds, implement FIT-only search + synthetic invariants; prove them; checkpoint. Only after those proofs may a one-shot FIT execution be armed.
8. Candidate construction/ranking must remain FIT-only. Validation/canary may gate only one locked FIT winner. Any failure => family #10 fallback; never alternate.
9. Promotion still requires FIT pitch gain >=0.005, no musical regression, critical delta <=0, coverage 1.0, exact 113 measures where applicable, and independent PDF event fidelity 1.0.
10. Whenever a future accepted baseline changes, immediately recompute and checkpoint the percentage view and create a new aggregate accepted-baseline FIT residual before shaping its successor.
11. Never modify main/Production/frontend/Bass/Lead or use Modal/L4/GPU without fresh explicit authorization.

## Current stop point
- Accepted baseline: family #10 / `4e6f9f...`.
- Motivational scorer view: **Pitch Content 35.4%**, Pitch+timing 6.7%, String/fret+timing 5.5%, Chord/voicing 5.8%, Measure coverage 100%, PDF event fidelity 100%.
- Families #1–#13 consumed/sealed.
- Family #14 frozen; policy/tests blob-locked; first trigger `221d5edb...` is sealed/inconclusive via connector; local reconstruction passed 9/9; definitive self-reporting CPU proof still required; no FIT search run.
- Current residual diagnostic remains `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.
- Safe continuation: build/checkpoint/trigger the self-reporting CPU-only family #14 policy proof, then continue only on recorded success.
