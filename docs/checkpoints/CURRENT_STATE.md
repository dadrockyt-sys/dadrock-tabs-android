# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families #1–#12 are consumed/sealed. Accepted baseline remains family #10. Family #13 exact-three generated-only atomic whole-onset prune has CPU-proven policy/tests AND CPU-proven preregistered FIT-only search/tests. No family #13 candidate search has executed yet. Safe next action is to create a tightly locked CPU-only one-shot, checkpoint its exact workflow blob before arming, then create one trigger-only commit.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`; render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark, not unseen holdout. V5 holdout permanently consumed.
- Split seed 144: 60 fit / 20 validation / 20 canary. FIT constructs/ranks only; later stages gate one locked winner. FIT pitch gain >=0.005; no musical regression; critical delta <=0; PDF fidelity 1.0. Failure => accepted-baseline fallback, never alternate.
- No Modal/L4/GPU without fresh explicit authorization. `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.

## Permanent progress-percentage reporting — USER MOTIVATION / UPDATE FORMAT
- In future Rhythm calibration updates, always include easy-to-read scorer percentages alongside technical metrics so progress toward a professionally rendered/transcribed PDF remains visible and motivating.
- Primary motivational Rhythm note-detection percentage = **Pitch Content F1 × 100**. For the current accepted family #10 baseline this is **35.4%** (`0.35406698564593303`).
- Also report, when relevant: **Pitch + timing 6.7%** (`0.06698564593301436`), **String/fret + timing 5.5%** (`0.05454545454545454`), **Chord/voicing 5.8%** (`0.0580511402902557`), **Measure coverage 100%** (`1.0`), and **PDF event fidelity 100%** (`1.0`).
- Clearly label these as separate scorer dimensions; do not combine them into a made-up overall percentage.
- Whenever the accepted baseline changes, recompute these percentages from the newly accepted scorer values and state the change versus the previous accepted baseline (percentage points and direction) in the next user update and checkpoint.
- Keep **Pitch Content F1 percentage** as the headline Rhythm detection progress number unless the scorer contract changes materially; if it does, explain the change before switching the headline metric.

## Accepted baseline — LOCKED / UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- Manifest commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- 1144 events / 113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity 1.0.
- Full gold: critical 1712; pitch 0.35406698564593303; pitch/timing 0.06698564593301436; string/fret/timing 0.05454545454545454; chord/voicing 0.0580511402902557; coverage 1.0.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
- Families #1–#12 are consumed/sealed.
- Family #11 report blob `9d1b46d8fcc45465a55f018363fd32e22e120068`; no FIT winner; family #10 fallback.
- Family #12 one-shot `32999986666` / job `98278991573`; report `debug/v144-rhythm-calibration/candidates/atomic-generated-only-dyad-onset-prune-search.json`; report blob `9a4d17622047db77e373a21c40036adc42297482`; no FIT winner; family #10 fallback; validation/canary/full stayed closed.
- Family #12 executable workflow deleted at `ff854c37b98fca82eb1a1c0552cfbaa382bcdf6e`; trigger deleted at `994164b4d760d62098bbcb2cbae38dfdc95d4a55`.
- Never use consumed-family candidate rankings, runners-up, gate outcomes, or candidate identities to shape/rank family #13.

## Current accepted-baseline FIT residual diagnostic — SEALED / CURRENT
- `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`; blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.
- Generated-only onset cardinalities: g1-r0=203, g2-r0=79, **g3-r0=12**, g5-r0=1.
- This aggregate-only diagnostic was the sole permitted family #13 shape evidence. Baseline remains unchanged, so no new residual diagnostic yet.

## Family #13 — PRE-REGISTERED / SEARCH CPU SUCCESS / NOT EXECUTED
### Frozen family
- Shape: **atomic exact-three-note generated-only whole-onset prune**.
- Construction: exactly 3 generated notes / 0 reference notes at one FIT onset.
- Support **3**, cap **256**, frozen before search.
- Rule identity: one structural onset context + three sorted `(sourceStringIndex, sourcePitchClass)` identities.
- Atomic all-3 deletion only; runtime reference forbidden; linked/referenced/invalid-position/measure-erasing targets ineligible; survivors immutable/source-ordered.
- Count-changing allowed only with exact 113 generated measures. Deterministic family #10 fallback required.

### Policy + policy CPU proof
- Policy `modal/v144_rhythm_generated_only_triad_prune_policy.py`; blob `622c839d0a833c3541007309ebf1203f1547b365`.
- Policy tests `modal/tests/test_v144_rhythm_generated_only_triad_prune_policy.py`; corrected commit `2c42917563a6779a996f7168067ba2b8ba49d91f`; blob `5adbcd39aacc181a6c0917654e754b582f8cca2e`.
- Established broad gate policy wiring blob `4cd6f7f868c7d6434564668d0031029211b2e62f`.
- Definitive policy CPU proof run `33006494479` / job `98301477632`, head `2c42917563a6779a996f7168067ba2b8ba49d91f`: SUCCESS. Never rerun/retrigger.

### FIT-only search + synthetic invariants — CPU PROVEN
- Search `validation/v144_rhythm_calibration/search_atomic_generated_only_triad_prunes.py`; creation commit `561d938f72d468ef3cf1eac871151e2a35803c43`; blob `e262057db95b297c9dc411f963476bae593553f1`; report schema `14425`.
- Search tests `modal/tests/test_v144_rhythm_generated_only_triad_prune_search.py`; creation commit `21caae18b6b8d36cf4af1d6cd6c918a40cc7e365`; blob `a5238673b466cbba6f69c6fa17587ebdb2d3402e`.
- Search hard-locks support 3/cap 256; reconstructs family #10 reference-free and verifies exact 1144-event SHA + 113 measures before gold opens; constructs/ranks only from FIT; applies CPU-proven reference-free triad policy; exact 113-measure guard; deletion-only ordered-subsequence proof; `removedEventCount = 3 * removedOnsetCount`; deterministic family #10 fallback.
- Synthetic search invariants prove candidate-name permutation stability; exact-three atomic deletion; partial/non-triad rejection; survivor mutation/reorder/add rejection; locked-rule mismatch rejection; fixed support/cap; accepted-baseline identity; runtime-reference/GPU/main/Production/V5 safety false.
- Broad gate search wiring commit/head `053f67fb4cb6be870e0a23c514d46457f9327aac`; workflow blob `94b546cf0b3a2ab2bc3a15d0a292a09c2bb6fb01`.
- Definitive search CPU proof: **run `33007127855`, job `98303667684`, head `053f67fb4cb6be870e0a23c514d46457f9327aac`: SUCCESS.** All steps passed: checkout, immutable V5 identities, V144 provenance contract, compile including family #13 search, all CPU unit tests including family #13 search invariants, fallback-first config, cleanup.
- This broad gate only compiled/imported/tested helpers; it did **not** run family #13 search `main`, open candidate outputs, or inspect calibration candidate labels.
- **Search CPU prerequisite is satisfied. Do not rerun/retrigger this proof.**

## ONE-SHOT PREREGISTRATION REQUIREMENTS — NEXT
- One-shot must be CPU-only and path-triggered by a new family #13 trigger file. It must run only if exact trigger commit message matches the preregistered message and trigger commit changes exactly one path.
- It must lock: immutable V5/result/render/PDF identities; gold SHA; family #10 accepted manifest/blob/event SHA/count/measures; family #13 policy/test/search/test blobs; broad CPU workflow blob `94b546cf...`; search CPU run `33007127855` / job `98303667684`; reconstruction/scoring/staged-selector/measure/PDF dependencies; runtime-reference false; GPU false; replay false; support 3/cap 256; removed events per changed onset 3.
- Fixed trigger path: `debug/v144-rhythm-calibration/candidates/.v144-atomic-generated-only-triad-onset-prune-trigger`.
- Fixed report path: `debug/v144-rhythm-calibration/candidates/atomic-generated-only-triad-onset-prune-search.json`.
- Fixed exact trigger commit message: `v144 execute atomic generated-only triad onset prune one-shot`.
- Create workflow first. **Before trigger creation, save a pre-arm checkpoint containing exact one-shot workflow blob.**
- Then create exactly one trigger-only commit. Freeze branch and poll only that exact trigger SHA. No rerun/retrigger/retry.
- During one-shot: FIT ranks all preregistered candidates and locks at most one; no FIT winner => family #10 fallback+stop; validation fail => fallback+stop; canary fail => fallback+stop; never alternate. Full gold only after all split gates pass.
- Promotion requires no musical regression, critical delta <=0, coverage 1.0, exact 113 measures, exact atomic-three invariants, independent PDF event fidelity 1.0.
- Immediately after one-shot, persist only report, then delete workflow + trigger regardless outcome and mark family #13 consumed.

## EXPLICIT NEXT STEPS — CONTINUATION CONTRACT
1. Re-read checkpoint; verify branch, family #12 report blob, and deleted family #12 execution surfaces.
2. Never rerun families #1–#12; never tune family #13 from consumed-family outcomes.
3. Create tightly locked family #13 CPU-only one-shot workflow using exact identities above. Do not trigger it yet.
4. Fetch exact one-shot workflow blob and save a **pre-arm checkpoint** with it.
5. Create exactly one trigger-only commit at the fixed trigger path with exact fixed commit message. Trigger payload must self-record workflow/search/policy/test/CPU identities, support 3/cap 256, exact-three deletion, runtime-reference false, GPU false, replay false.
6. Freeze branch and poll only exact trigger SHA. Never rerun/retrigger/retry.
7. After completion persist only report, delete/seal workflow + trigger, and checkpoint run/job/report/deletion identities and accepted baseline result.
8. If family #13 changes accepted baseline, current residual `b9794a7b...` becomes historical immediately; create a new aggregate accepted-baseline FIT residual before any successor.
9. Never modify main/Production/frontend/Bass/Lead or use Modal/L4/GPU without fresh explicit authorization.

## Current stop point
- Accepted baseline: family #10 / `4e6f9f...`.
- Families #1–#12 consumed/sealed.
- Family #13 policy CPU SUCCESS and search CPU SUCCESS (`33007127855` / `98303667684`).
- Family #13 search has **not executed**; no candidate outcome inspected.
- Safe next action: create locked one-shot workflow, checkpoint its exact blob, then one trigger-only commit.
