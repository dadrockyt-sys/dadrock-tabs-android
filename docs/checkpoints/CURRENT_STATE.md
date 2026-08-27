# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families #1–#13 are consumed/sealed. Accepted baseline remains family #10. Family #14 is preregistered/frozen; both its policy and FIT-search implementations are definitively CPU-proven and their temporary proof automation is sealed/deleted. No live family #14 FIT search has run. Next safe step is to inspect only the established family #13 execution-wrapper mechanics (not its consumed candidate outcome), create/blob-lock/checkpoint one family #14 one-shot CPU workflow, then create exactly one live trigger.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`; render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark, not unseen holdout. V5 holdout permanently consumed.
- Split seed 144: 60 fit / 20 validation / 20 canary. FIT constructs/ranks only; later stages gate one locked winner. FIT pitch gain >=0.005; no musical regression; critical delta <=0; PDF fidelity 1.0. Failure => accepted-baseline fallback, never alternate.
- No Modal/L4/GPU without fresh explicit authorization. `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.

## Permanent progress-percentage reporting — USER MOTIVATION / UPDATE FORMAT
- Headline Rhythm note-detection percentage = **Pitch Content F1 × 100**. Current accepted family #10 baseline = **35.4%** (`0.35406698564593303`).
- Also report, when relevant: **Pitch + timing 6.7%** (`0.06698564593301436`), **String/fret + timing 5.5%** (`0.05454545454545454`), **Chord/voicing 5.8%** (`0.0580511402902557`), **Measure coverage 100%** (`1.0`), and **PDF event fidelity 100%** (`1.0`).
- Keep these dimensions separate; never invent a combined overall percentage. On accepted-baseline change, recompute all percentages and percentage-point deltas immediately.

## Accepted baseline — LOCKED / UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- Manifest commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- 1144 events / 113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity 1.0.
- Full gold: critical 1712; pitch 0.35406698564593303; pitch/timing 0.06698564593301436; string/fret/timing 0.05454545454545454; chord/voicing 0.0580511402902557; coverage 1.0.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
- Families #1–#13 are consumed/sealed. Never use their candidate rankings, runners-up, gate outcomes, candidate identities, or observed candidate behavior to shape/rank a successor family.
- Family #11 report blob `9d1b46d8fcc45465a55f018363fd32e22e120068`; no FIT winner; family #10 fallback.
- Family #12 run `32999986666` / job `98278991573`; report blob `9a4d17622047db77e373a21c40036adc42297482`; no FIT winner; sealed.
- Family #13 run `33008934470` / job `98309848693`; report blob `bb95b99f64a757b4bc96c86f4392e1e453e3b721`; no FIT winner; family #10 fallback; sealed. Its **workflow mechanics** may be inspected as established infrastructure precedent, but its candidate result must not shape/rank family #14.

## Current accepted-baseline FIT residual diagnostic — SEALED / CURRENT
- `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`; blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.
- Aggregate topology: g1-r0=203, g2-r0=79, g3-r0=12, g5-r0=1; g2-r1=26; shared generated-heavier=27; shared reference-heavier=57; generated-only=295; reference-only=180.
- Aggregate mechanism counts: pitch FP 467, pitch FN 418, same-onset extra generated slots 431, same-onset missing reference slots 382.
- Baseline unchanged, so this diagnostic remains current; do not create a replacement yet.

## Family #14 — FROZEN CONTRACT
- Shape: **atomic shared dyad-to-singleton surplus-note prune**.
- FIT construction: exactly 2 generated / 1 reference at one onset; exactly one generated exact-MIDI match is immutable survivor; other generated note is FIT-labeled surplus target.
- Exclude zero/two exact matches, duplicate source identities, invalid positions, linked pitch semantics, or referenced prune target.
- Support exactly **3**; cap exactly **256**.
- Rule: one structural onset context + two sorted `(sourceStringIndex, sourcePitchClass)` identities + one unique prune identity that is a dyad member.
- Runtime reference-free exact dyad/context/identity match; delete only prune member; survivor immutable/source-order preserved; no pitch/timing/string/fret rewrite or onset creation.
- Count-changing safety: valid fixed-tuning positions; no pitch linkage; prune target unreferenced; cannot erase measure; exact 113 generated measures.
- FIT constructs/ranks only; validation/canary gate only one locked winner; failure/no winner => family #10 fallback, never alternate.
- Promotion: FIT pitch gain >=0.005; no musical regression; critical delta <=0; exact 113 measures; independent PDF event fidelity 1.0.

## Family #14 policy — COMPLETE / SUCCESS / SEALED
- Policy `modal/v144_rhythm_shared_dyad_surplus_prune_policy.py` blob `1f6cc7fcaf2d4ac7838b48b839c617b04cb1c34e`.
- Tests `modal/tests/test_v144_rhythm_shared_dyad_surplus_prune_policy.py` blob `38d6804560755fcb0bcf26eeda5e1a5b77f31231`.
- Definitive proof run `33025027635`, job `98364261256`: SUCCESS. Proof `debug/v144-rhythm-calibration/proofs/shared-dyad-surplus-prune-policy-cpu.json` blob `cafd2b51e75ba0895dde995f0730ef8554976516`, schema 14426; runtime reference false; Modal GPU false; FIT search false.
- Policy proof workflows/triggers deleted/sealed; never rerun.

## Family #14 FIT search — COMPLETE / SYNTHETIC CPU PROOF SUCCESS+SEALED / LIVE SEARCH NOT RUN
- Search `validation/v144_rhythm_calibration/search_atomic_shared_dyad_surplus_prunes.py`; blob **`dd02c492ecfef26bbb15e8d345346ff75bb5fa30`**; creation commit `1f1d69e0544a921a0a7cf06599c5c5b891188de1`; report schema 14427.
- Search tests `modal/tests/test_v144_rhythm_shared_dyad_surplus_prune_search.py`; blob **`77758ead57a2735ba653bbba64e78c4124d34798`**; creation commit `f504b9cdf6edb0a51cac151e5a07ba3f4c18509e`.
- Definitive synthetic search proof run **`33025495483`**, job **`98365711683`**: COMPLETED / SUCCESS. Exact blobs/dependencies verified, compiled, exact test module passed, proof persisted.
- Immutable proof `debug/v144-rhythm-calibration/proofs/shared-dyad-surplus-prune-search-cpu.json`; blob **`73c2e863f5dc8404fab8985d05f360a2093f588c`**; schema 14428; fit/validation/canary labels read=false; runtime reference=false; Modal GPU=false; live search=false.
- Proof workflow blob `251b9f3a001ddd80d1045e5e80d2c833d0227f91`; trigger commit `fdd5006e58dc7ca3fbbbe3aaff2370fae2fbd2f2`.
- Search-proof workflow deleted/sealed commit **`01e10bb92a4ec8a99286284692c848d197dcf733`**.
- Search-proof trigger deleted/sealed commit **`0341e34c6793fe545f112befbef859833da12361`**.
- Proof JSON remains. Never rerun/retrigger the synthetic search proof.
- **No live family #14 FIT search has run; no family #14 candidate outcome has been observed; accepted baseline/scorers remain unchanged.**

## Fixed dependency identities for one-shot wrapper
- Accepted residual analyzer `27ac8699279db8fc0208d067479ad3751da1a630`.
- Singleton reconstruction search `70880d26418d907cc702233af37bcc4b643e3a57`; singleton policy `1e05e66a3523f98944370837a59e5d6e7293f9ac`.
- Pitch-position shift `f69755b61bdcdf3a669847ce7e425289b4b0927f`; pitch shift `d9998c59acddba070069668d62bcb1c3cdaf2b05`; triple conjunction `ef9768a127472d7ce0746fdf21164d33e5117ea4`.
- Staged selector `d176a9a69366e192e6fa75bc1039661e977f0bfa`; measure guard `4a1364204dd1e720c09d835ec3995c165047de98`; context split `2da58508f2132660ad317ee63d5cb043d58285f0`; config `9b93205cb47bc7718685b9d41b263778107801ce`.
- Split analysis `1569bf01554be345ca9199a85f700db7743501a5`; signature prune scoring `699dd1a16725ecf11797e42829aa409ee5909000`; selected candidate scoring `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`.
- Canonical `088d44827fb23e20d9aeeb4944a672989af5846c`; scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`; freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`; PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`; render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.

## EXPLICIT NEXT STEPS — CONTINUATION CONTRACT
1. Stay only on `v143-contextual-prune-lobo`; never modify main/Production/frontend/Bass/Lead.
2. Never rerun/retrigger/reselect/retune families #1–#13 or any completed family #14 CPU proof.
3. Accepted baseline remains family #10; scorer view remains **35.4% Pitch Content**, 6.7% Pitch+timing, 5.5% String/fret+timing, 5.8% Chord/voicing, 100% coverage, 100% PDF event fidelity.
4. Family #14 is frozen; do not retune after any candidate observation.
5. Inspect family #13 one-shot workflow only for neutral execution/invariant mechanics. Do not use its candidate result or rankings.
6. Create one family #14 one-shot CPU workflow using exact frozen search/policy/dependency identities; include immutable identity verification, staged semantics, independent PDF event identity, final invariant/fallback wrapper, immutable recheck, and report-only persistence.
7. Fetch/blob-lock that workflow and update this checkpoint with its exact blob and creation commit **before** creating any live trigger.
8. After pre-arm checkpoint, create exactly one family #14 live trigger. Make no competing branch commits while it runs. No Modal/GPU.
9. After execution, family #14 is consumed/sealed regardless of outcome. If accepted baseline changes, recompute all scorer percentages + new accepted-baseline FIT residual immediately. If unchanged, retain current aggregate residual.

## Current stop point
- Accepted baseline family #10 / `4e6f9f...`.
- Scorer view unchanged: **Pitch Content 35.4%**, Pitch+timing 6.7%, String/fret+timing 5.5%, Chord/voicing 5.8%, Measure coverage 100%, PDF event fidelity 100%.
- Family #14 policy and search are both definitively CPU-proven and proof automation sealed.
- No live family #14 FIT search has run.
- Safe continuation: inspect sealed family #13 one-shot wrapper mechanics, build/blob-lock/checkpoint family #14 one-shot workflow, then trigger it exactly once.
