# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families #1–#12 are consumed/sealed. Accepted baseline remains family #10. Family #13 exact-three generated-only atomic whole-onset prune has CPU-proven policy/tests and now has preregistered FIT-only search + synthetic search invariants. The search has NOT executed and no candidate outcomes have been inspected. Search CPU proof is the next gate.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`; render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark, not unseen holdout. V5 holdout permanently consumed.
- Split seed 144: 60 fit / 20 validation / 20 canary. FIT constructs/ranks only; later stages gate one locked winner. FIT pitch gain >=0.005; no musical regression; critical delta <=0; PDF fidelity 1.0. Failure => accepted-baseline fallback, never alternate.
- No Modal/L4/GPU without fresh explicit authorization. `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.

## Accepted baseline — LOCKED / UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- Manifest commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- 1144 events / 113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity 1.0.
- Full gold: critical 1712; pitch 0.35406698564593303; pitch/timing 0.06698564593301436; string/fret/timing 0.05454545454545454; chord/voicing 0.0580511402902557; coverage 1.0.
- Reconstruction CPU `32996069426` / job `98265545933` SUCCESS.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
- Families #1–#12 are consumed/sealed.
- Family #11 one-shot `32998471525` / `98273767947`; report blob `9d1b46d8fcc45465a55f018363fd32e22e120068`; no FIT winner; family #10 fallback.
- Family #12 one-shot `32999986666` / job `98278991573`; report `debug/v144-rhythm-calibration/candidates/atomic-generated-only-dyad-onset-prune-search.json`; report blob `9a4d17622047db77e373a21c40036adc42297482`; no FIT winner; family #10 fallback. Validation/canary/full stayed closed.
- Family #12 executable workflow deleted at `ff854c37b98fca82eb1a1c0552cfbaa382bcdf6e`; trigger deleted at `994164b4d760d62098bbcb2cbae38dfdc95d4a55`.
- Never use consumed-family candidate rankings, runners-up, gate outcomes, context/string/pitch identities, or calibration behavior to shape/rank family #13.

## Current accepted-baseline FIT residual diagnostic — SEALED / CURRENT
- `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`; blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.
- Generated-only onset cardinalities: g1-r0=203, g2-r0=79, **g3-r0=12**, g5-r0=1.
- This aggregate-only diagnostic was the sole permitted shape evidence for family #13. Because accepted baseline did not change, do not create a new residual diagnostic yet.

## Family #13 — PRE-REGISTERED / POLICY CPU SUCCESS / SEARCH CPU PENDING
### Frozen shape and semantics
- Shape: **atomic exact-three-note generated-only whole-onset prune**.
- Exact onset construction: 3 generated notes / 0 reference notes.
- Minimum false-positive support **3**; maximum candidates **256**; frozen before search.
- Rule identity: one structural onset context + three sorted `(sourceStringIndex, sourcePitchClass)` identities.
- Whole-onset deletion atomic: all 3 or none. Runtime reference forbidden. Linked, externally referenced, invalid-position, and measure-erasing targets are ineligible. Survivors immutable and source-ordered.
- Event count may decrease only with exact accepted-baseline 113-measure preservation.
- Deterministic family #10 fallback required.

### Policy + deterministic synthetic policy proof
- Policy `modal/v144_rhythm_generated_only_triad_prune_policy.py`; blob `622c839d0a833c3541007309ebf1203f1547b365`.
- Corrected synthetic policy tests `modal/tests/test_v144_rhythm_generated_only_triad_prune_policy.py`; commit `2c42917563a6779a996f7168067ba2b8ba49d91f`; blob `5adbcd39aacc181a6c0917654e754b582f8cca2e`.
- Established gate `.github/workflows/v144-rhythm-cpu-gate.yml`; wiring commit `4c0f11d150f93234df32101beeee691eed919817`; workflow blob `4cd6f7f868c7d6434564668d0031029211b2e62f`.
- First gate `33006357625` / `98301012386` failed safely only because the synthetic test imported non-exported alias names; immutable V5/provenance/compile passed and no search/calibration labels were opened.
- Test-only correction left policy unchanged.
- Definitive policy CPU proof: run `33006494479` / job `98301477632`, head `2c42917563a6779a996f7168067ba2b8ba49d91f`: all job steps SUCCESS, including immutable V5, provenance, compile, all CPU tests, and fallback-first config. Never rerun/retrigger this proof.

### FIT-only search — PREREGISTERED / NOT EXECUTED
- Search path `validation/v144_rhythm_calibration/search_atomic_generated_only_triad_prunes.py`.
- Search creation commit `561d938f72d468ef3cf1eac871151e2a35803c43`; blob `e262057db95b297c9dc411f963476bae593553f1`.
- Report schema `14425`.
- Search hard-locks support 3 / cap 256, reconstructs accepted family #10 reference-free and verifies exact 1144-event SHA + 113 measures **before opening gold**, constructs/ranks only from FIT, hashes candidate identity from context + three sorted identities, applies only the CPU-proven reference-free triad policy, enforces exact 113-measure preservation, proves deletion-only ordered-subsequence semantics, and requires `removedEventCount = 3 * removedOnsetCount`.
- FIT may lock at most one candidate. If no FIT winner => family #10 fallback and stop. If validation fails => fallback. If canary fails => fallback. Never select a runner-up. Full gold is reachable only after FIT+validation+canary pass.
- Search reports validation/canary construction/ranking false, historical consumed-family results used false, runtime reference false, GPU false, main/Production/V5 modified false.
- **The search main has not been run. No family #13 candidate labels/outcomes have been inspected.**

### Synthetic search invariants — PREREGISTERED / NOT YET CPU-PROVEN
- Test path `modal/tests/test_v144_rhythm_generated_only_triad_prune_search.py`.
- Test creation commit `21caae18b6b8d36cf4af1d6cd6c918a40cc7e365`; blob `a5238673b466cbba6f69c6fa17587ebdb2d3402e`.
- Synthetic tests prove: three-note candidate-name permutation stability and field sensitivity; valid deletion-only subsequence with exactly 3 removed events per changed onset; partial/non-triad deletion rejection; survivor mutation/reordering/addition rejection; locked-rule mismatch rejection; support 3/cap 256 cannot be relaxed; accepted family #10 identity locked; runtime-reference/GPU/main/Production/V5 safety false.
- Tests use synthetic events only; no calibration labels/candidate outcomes.
- Current broad CPU workflow does **not yet** watch/compile/run these two new search paths, so creation of the search/tests did not execute family #13 search or CPU evaluation.

## EXPLICIT NEXT STEPS — CONTINUATION CONTRACT
1. Re-read this checkpoint. Verify branch exactly `v143-contextual-prune-lobo`, family #12 report blob `9a4d17622047db77e373a21c40036adc42297482`, and its workflow/trigger remain deleted.
2. Never rerun families #1–#12 and never use their candidate outcomes to tune family #13.
3. Wire exactly these preregistered family #13 search/test blobs into the established broad CPU gate: add paths, py_compile search, and run synthetic search test. Do not alter policy shape/support/cap from outcomes.
4. Require definitive CPU SUCCESS for search blob `e262057d...` + test blob `a5238673...` + policy blob `622c839d...` before any candidate search execution. If CPU fails, inspect only implementation/test logs; fix only implementation/tests; do not open calibration labels.
5. After search CPU success, checkpoint exact workflow/head/run/job/search/test identities before creating any executable one-shot.
6. Then create a tightly locked CPU-only one-shot. Lock immutable V5/result/render/PDF, gold SHA, accepted manifest, policy/tests/search/tests, CPU proof identities, reconstruction/scoring/staged-selector/measure/PDF dependencies, runtime-reference false, GPU false, replay false.
7. Save a **pre-arm checkpoint containing exact one-shot workflow blob** before trigger creation. Then create exactly one trigger-only commit with exact preregistered path/message. Freeze branch and poll only that trigger SHA. No rerun/retrigger/retry.
8. During one-shot: FIT ranks all preregistered candidates and locks at most one; no FIT winner => fallback+stop; validation fail => fallback+stop; canary fail => fallback+stop; never alternate. Full gold only after all split gates pass.
9. Promotion additionally requires no musical regression, critical delta <=0, coverage 1.0, exact 113 measures, family-specific atomic invariants, and independent PDF event fidelity 1.0.
10. After one-shot persist only report, then delete workflow + trigger regardless outcome and mark family #13 consumed.
11. If family #13 changes accepted baseline, current residual `b9794a7b...` becomes historical immediately; create a new accepted-baseline aggregate FIT residual diagnostic before proposing any successor.
12. Never start Bass/Lead, modify `main`/Production or `/ai-tab`, claim Rhythm-complete/near-100/unseen-generalization, or use Modal/L4/GPU without fresh explicit user authorization.

## Current stop point
- Accepted baseline: family #10 `singleton-onset-replace-be9e9aa7a734e3cd` / `4e6f9f...`.
- Families #1–#12: consumed/sealed.
- Family #13: policy blob `622c839d...` CPU-proven; search blob `e262057d...` preregistered; synthetic search test blob `a5238673...` preregistered; **search not executed; search CPU proof pending**.
- Safe next action: wire search + tests into the existing V144 broad CPU gate and obtain exact-revision CPU SUCCESS before any candidate evaluation.
