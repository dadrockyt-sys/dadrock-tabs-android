# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families #1–#13 are consumed/sealed. Accepted baseline remains family #10. Family #14 is preregistered/frozen; its policy proof is SUCCESS+SEALED and its exact FIT-search implementation + synthetic search-invariant proof are now also SUCCESS. No live family #14 FIT search has run. Next safe step is to seal/remove the temporary search-proof workflow+trigger, checkpoint, then design/blob-lock/checkpoint a one-shot CPU-only live FIT execution workflow before creating exactly one trigger.**

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

## Family #14 — PREREGISTERED / FROZEN / POLICY PROVEN+SEALED / SEARCH PROVEN / LIVE SEARCH NOT RUN
### Independent structural rationale
- Family shape was selected only from the still-permitted aggregate accepted-baseline residual and independent structural reasoning, not from any consumed-family candidate result.
- The residual contains **26 `g2-r1` shared onsets** and **27 shared generated-heavier onsets**. A generated-heavy shared onset can contain one correct note plus one surplus note; deleting only a demonstrably surplus member is materially distinct from whole-onset generated-only pruning and preserves the shared onset.
- No consumed-family candidate result was used to choose this family.

### Frozen family contract
- Name/shape: **atomic shared dyad-to-singleton surplus-note prune**.
- FIT construction unit: exactly **2 generated notes / 1 reference note** at one onset, with exactly one generated exact-MIDI match to the sole reference note. Exact-MIDI-matched generated note is immutable survivor; other generated note is FIT-labeled surplus target.
- Exclude zero/two exact-MIDI matches, duplicate/indistinguishable source identities, invalid source positions, linked pitch semantics, or prune target referenced by another event.
- Minimum FIT correction support **3**, maximum candidate rules **256**; frozen before any family #14 search.
- Rule identity: exactly one allowed structural onset context + two sorted `(sourceStringIndex, sourcePitchClass)` identities + one specific unique prune identity that is a member of the dyad.
- Runtime is reference-free; exact two-note generated onset + exact structural context + complete dyad identity; remove only uniquely identified surplus member. Survivor byte-for-byte/source-order immutable. No pitch/timing/string/fret rewriting or onset creation.
- Count-changing safety: source positions valid under fixed tuning; no linked pitch semantics; prune target not referenced; operation cannot erase a generated measure; result must preserve exact **113 generated measures**.
- FIT constructs/ranks only; validation/canary gate one locked winner; any failure/no winner => deterministic family #10 fallback, never alternate.
- Promotion gates: FIT Pitch Content F1 gain >=0.005; no musical regression; critical delta <=0; exact 113-measure coverage; independent PDF event fidelity 1.0.

### Family #14 policy implementation/proof — COMPLETE + SEALED
- Policy `modal/v144_rhythm_shared_dyad_surplus_prune_policy.py`; blob **`1f6cc7fcaf2d4ac7838b48b839c617b04cb1c34e`**; creation commit `3833c7dc08f0ae8366132b3e7268f3b22d876767`.
- Policy tests `modal/tests/test_v144_rhythm_shared_dyad_surplus_prune_policy.py`; blob **`38d6804560755fcb0bcf26eeda5e1a5b77f31231`**; creation commit `38ebdf635c5ae3673d5eebc58466f887c75a7a5b`.
- Direct policy dependencies proven: context split `2da58508f2132660ad317ee63d5cb043d58285f0`; pitch-shift helper `d9998c59acddba070069668d62bcb1c3cdaf2b05`.
- Definitive policy proof run **`33025027635`**, job **`98364261256`**: SUCCESS. Immutable success proof `debug/v144-rhythm-calibration/proofs/shared-dyad-surplus-prune-policy-cpu.json`; blob **`cafd2b51e75ba0895dde995f0730ef8554976516`**; schema `14426`; runtimeReferenceInput=false; modalGpuUsed=false; fitSearchRun=false.
- Policy proof automation is sealed/deleted. Workflow deletion commits `67b1cf3e7c8b797b8ec19f4d1e1e07f0a0a1805c` and `f090d0ec4016f2f5db4bf4205770db770d8793bf`; trigger deletion commits `d74b62184486d18ca75038ffe166e129fd5c7ae6` and `df1349044be4a6d42229ca39e89e32cad197f7a0`. Never rerun policy proof.

### Family #14 FIT search implementation + synthetic proof — SUCCESS
- FIT-only search `validation/v144_rhythm_calibration/search_atomic_shared_dyad_surplus_prunes.py`; blob **`dd02c492ecfef26bbb15e8d345346ff75bb5fa30`**; creation commit **`1f1d69e0544a921a0a7cf06599c5c5b891188de1`**; report schema **`14427`**.
- Synthetic search invariant tests `modal/tests/test_v144_rhythm_shared_dyad_surplus_prune_search.py`; blob **`77758ead57a2735ba653bbba64e78c4124d34798`**; creation commit **`f504b9cdf6edb0a51cac151e5a07ba3f4c18509e`**.
- Search main reconstructs/verifies accepted family #10 before opening gold; candidate construction/ranking is FIT-only; validation/canary remain closed until one FIT winner is locked; exact 113-measure guard; deterministic family #10 fallback; runtime reference false.
- Search proof workflow `.github/workflows/v144-shared-dyad-surplus-prune-search-cpu-definitive.yml`; blob **`251b9f3a001ddd80d1045e5e80d2c833d0227f91`**; creation commit **`2366ee415e293edf2f86a96b7eafde5016439362`**.
- Search proof trigger commit **`fdd5006e58dc7ca3fbbbe3aaff2370fae2fbd2f2`**; trigger path `debug/v144-rhythm-calibration/triggers/shared-dyad-surplus-prune-search-cpu-definitive.txt`. Never alter/retrigger it.
- Definitive synthetic search CPU proof run **`33025495483`**, job **`98365711683`**: **COMPLETED / SUCCESS**. Every substantive step succeeded: exact frozen search/test/dependency blob verification, `py_compile`, exact synthetic search unittest execution, and success-proof persistence.
- Immutable success proof `debug/v144-rhythm-calibration/proofs/shared-dyad-surplus-prune-search-cpu.json`; blob **`73c2e863f5dc8404fab8985d05f360a2093f588c`**; schema `14428`; status success; runAttempt=1; exact trigger/search/test/policy identities; `fitLabelsRead=false`, `validationLabelsRead=false`, `canaryLabelsRead=false`, `runtimeReferenceInput=false`, `modalGpuUsed=false`, `liveSearchRun=false`.
- **No live FIT search has run and no family #14 candidate outcome has been observed. Accepted baseline/scorers are unchanged.**
- Next immediate safety step: delete/seal the temporary search-proof workflow and trigger while retaining proof JSON; checkpoint those deletion commits before designing a live one-shot.

## Family #13 — CONSUMED / SEALED / NO SCORE CHANGE
- Shape: atomic exact-three-note generated-only whole-onset prune; support 3, cap 256.
- Policy blob `622c839d0a833c3541007309ebf1203f1547b365`; policy tests blob `5adbcd39aacc181a6c0917654e754b582f8cca2e`; policy CPU proof run `33006494479` / job `98301477632`: SUCCESS; never rerun.
- Search blob `e262057db95b297c9dc411f963476bae593553f1`; search tests blob `a5238673b466cbba6f69c6fa17587ebdb2d3402e`; report schema `14425`; search CPU proof run `33007127855` / job `98303667684`: SUCCESS; never rerun.
- One-shot run `33008934470` / job `98309848693`: SUCCESS infrastructure, no FIT winner. Report `debug/v144-rhythm-calibration/candidates/atomic-generated-only-triad-onset-prune-search.json`; report blob `bb95b99f64a757b4bc96c86f4392e1e453e3b721`; ranked/evaluated count 0; family #10 fallback; validation/canary/full closed; no score change. Workflow/trigger sealed/deleted. Never rerun/retrigger/retry family #13 or use its candidate outcome to shape family #14.

## Fixed dependency identities retained for future one-shot wrappers
- Accepted residual analyzer `27ac8699279db8fc0208d067479ad3751da1a630`.
- Singleton reconstruction search `70880d26418d907cc702233af37bcc4b643e3a57`; singleton policy `1e05e66a3523f98944370837a59e5d6e7293f9ac`.
- Pitch-position shift `f69755b61bdcdf3a669847ce7e425289b4b0927f`; pitch shift `d9998c59acddba070069668d62bcb1c3cdaf2b05`; triple conjunction `ef9768a127472d7ce0746fdf21164d33e5117ea4`.
- Staged selector `d176a9a69366e192e6fa75bc1039661e977f0bfa`; measure guard `4a1364204dd1e720c09d835ec3995c165047de98`; context split `2da58508f2132660ad317ee63d5cb043d58285f0`; config `9b93205cb47bc7718685b9d41b263778107801ce`.
- Split analysis `1569bf01554be345ca9199a85f700db7743501a5`; signature prune scoring `699dd1a16725ecf11797e42829aa409ee5909000`; selected candidate scoring `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`.
- Canonical `088d44827fb23e20d9aeeb4944a672989af5846c`; scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`; freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`; PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`; render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.
- Current freeze dependency path `validation/rhythm_holdout/freeze_rhythm_analysis.py`; PDF verifier `validation/rhythm_holdout/verify_pdf_event_fidelity.py`; render contract `lib/v143RenderContract.js`.

## EXPLICIT NEXT STEPS — CONTINUATION CONTRACT
1. Stay on `v143-contextual-prune-lobo`; never main/Production/frontend/Bass/Lead.
2. Never rerun/retrigger/reselect/retune families #1–#13, family #14 policy proofs, or family #14 synthetic search proof run `33025495483` / job `98365711683`.
3. Accepted baseline remains family #10; headline scorer remains **35.4% Pitch Content F1**. Do not claim a family #14 gain until all gates pass and accepted baseline changes.
4. Current aggregate residual diagnostic `b9794a7b...` remains current until accepted baseline changes.
5. Family #14 shape/support/cap/rule identity are frozen; do not retune after observing any family #14 candidate outcome.
6. Delete/seal `.github/workflows/v144-shared-dyad-surplus-prune-search-cpu-definitive.yml` and its trigger file, retaining proof JSON `73c2e863...`; checkpoint deletion commits.
7. Then inspect the sealed family #13 one-shot workflow at its creation commit and adapt its immutable identity checks/staged semantics/PDF proof/final invariant/report-only persistence to family #14. Create one new family #14 one-shot workflow; blob-lock it in this checkpoint **before** creating any live trigger.
8. Only after pre-arm checkpoint may exactly one live family #14 FIT trigger be created. Make no competing branch commits while it runs. Candidate construction/ranking FIT-only; validation/canary gate one locked winner; failure/no winner => family #10 fallback; never alternate.
9. Promotion requires FIT pitch gain >=0.005, no musical regression, critical delta <=0, exact 113 measures, independent PDF event fidelity 1.0.
10. After one-shot, family #14 is consumed/sealed regardless of outcome. If baseline changes, immediately recompute scorer percentages and create a new aggregate accepted-baseline FIT residual before shaping any successor. If baseline does not change, current aggregate residual remains valid.
11. No Modal/L4/GPU without fresh explicit authorization.

## Current stop point
- Accepted baseline family #10 / `4e6f9f...`.
- Scorer view unchanged: **Pitch Content 35.4%**, Pitch+timing 6.7%, String/fret+timing 5.5%, Chord/voicing 5.8%, Measure coverage 100%, PDF event fidelity 100%.
- Families #1–#13 sealed.
- Family #14 policy proof SUCCESS+SEALED; search synthetic proof SUCCESS run `33025495483` / job `98365711683`, proof blob `73c2e863...`; temporary search proof automation still present pending immediate sealing; no live FIT search run.
- Safe continuation: seal search-proof workflow/trigger, checkpoint, then pre-arm a one-shot live FIT workflow from the established family #13 execution pattern.
