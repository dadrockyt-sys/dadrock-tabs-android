# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families 1–12 are consumed/sealed. Accepted baseline remains family #10 `singleton-onset-replace-be9e9aa7a734e3cd` / SHA `4e6f9f...`. Family #12 atomic exact-two-note generated-only dyad whole-onset prune completed its single authorized one-shot and STOPPED AT FIT with deterministic family #10 fallback; validation/canary/full were never opened. Family #12 execution surfaces are deleted. Family #13 is pre-registered as an atomic exact-three-note generated-only whole-onset prune; its deterministic synthetic-only policy tests are frozen, but no exact-revision broad CPU proof, search, evaluation, or execution authorization exists yet.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`; render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark, not unseen holdout. V5 holdout permanently consumed.
- Split measure+step seed 144: 60 fit / 20 validation / 20 canary. FIT constructs/ranks only; validation/canary gate one locked winner. FIT pitch gain >=0.005; no musical regression; critical delta <=0; PDF fidelity 1.0. Gate order fit→validation→canary→full→independent PDF; later failure => accepted-baseline fallback, never alternate.
- No Modal/L4/GPU without fresh explicit authorization. `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.

## Accepted baseline — LOCKED / UNCHANGED
- `singleton-onset-replace-be9e9aa7a734e3cd`; manifest commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- 1144 events / 113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity 1.0.
- Full gold: critical 1712; pitch 0.35406698564593303; pitch/timing 0.06698564593301436; string/fret/timing 0.05454545454545454; chord/voicing 0.0580511402902557; coverage 1.0.
- Reconstruction CPU `32996069426` / job `98265545933` SUCCESS. Production/Rhythm-complete/near100/unseen-generalization all false.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
- Families 1–12 are consumed.
- Family #11: one-shot `32998471525` / `98273767947`; report blob `9d1b46d8fcc45465a55f018363fd32e22e120068`; no FIT-qualified candidate; family #10 fallback; sealed.
- Family #12: atomic exact-two-note generated-only dyad whole-onset prune; one-shot and report details below. Never use its candidate outcomes/runners-up to shape or rank a successor.

## Current accepted-baseline FIT residual diagnostic — SEALED / CURRENT
- Report `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`; commit `dd06bd96061170e6c25a8ffe6b4d91db941491fc`; blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`; candidate construction/ranking/selection false; validation/canary false; runtime reference/GPU false.
- FIT aggregate: generated 643 / reference 594; pitch matched 176; tight timing 41; gross timing 90; exact position/timing 34.
- Onsets: generated 485 / reference 370 / shared 190 / generated-only 295 / reference-only 180. Generated-only cardinalities: g1-r0=203, g2-r0=79, **g3-r0=12**, g5-r0=1. This diagnostic alone may inform next family shape while baseline unchanged.

## Family #12 — COMPLETE / CONSUMED / SEALED / FIT FALLBACK
### Policy/search preregistration and CPU proofs
- Policy `modal/v144_rhythm_generated_only_dyad_prune_policy.py`; commit `cc9370af575aa1dcc6a650eea8b0f4a16616742f`; blob `21ece8eaedc1210c9e55eedfd686163ae7f5e1f7`.
- Policy tests commit `5325c25de53831ba148015875cca8875fa9c2c19`; blob `0ae23f3735b0ebca178eea81352ed2e83474f204`; seven tests.
- Policy CPU `32999064437` / `98275778909`: SUCCESS.
- Search `validation/v144_rhythm_calibration/search_atomic_generated_only_dyad_prunes.py`; commit `9dfafbbe460974b316f5ccd8a6c3f1a103ab60ac`; blob `6870c1ba34e0b3d9baa63c7f9bb036851ccca0ac`.
- Search tests commit `f6358e99d4df4bc2e73f5d7bedbaeaae8c45cf82`; blob `2b45a35b75e340e21343d06728c1768325040be9`; seven tests.
- Search CPU workflow commit `d6f1f7cbc61c3c7a4b6a880b6f60a89e59acf9ed`; workflow blob `d607707fb802808c194137544aa68472e6ec49fb`; run `32999506459` / job `98277305962`: SUCCESS.

### Fixed family #12 semantics
- FIT construction: exact two generated notes and zero reference notes at one onset; support 3; max candidates 256.
- Rule identity: structural onset context + two sorted `(sourceStringIndex, sourcePitchClass)` identities.
- Runtime reference forbidden; whole dyad deletion atomic; no partial deletion; linked/referenced/measure-erasing targets ineligible; survivors immutable/in-order.
- Count-changing allowed only with exact 113-measure preservation; `removedEventCount = 2 * removedOnsetCount`.

### One-shot identity / result
- One-shot workflow `.github/workflows/v144-atomic-generated-only-dyad-onset-prune-search.yml`; preregistration commit `a9ddb15614cc25a8c58b1aa1a417f81909ee2c6e`; workflow blob `cc3b07f3a6799dff75bb7052683f6722e56e7ff7`.
- Pre-arm checkpoint `cd614a3e2f43acf741dd84c18fb92c2bda322be1`.
- Trigger commit `42264c68844b78ec8de28b12fb74f92abfd7608e`; trigger blob `28f8bbbe21ac447bb672c445ee2ef068db922861`; exact message `v144 execute atomic generated-only dyad onset prune one-shot`; trigger-only commit.
- One-shot run `32999986666`, job `98278991573`: **SUCCESS infrastructure/end-to-end**. All steps passed, including immutable trigger verification, fixed search, staged-stop semantics, independent PDF proof, final invariant wrapper, immutable recheck, report-only persistence.
- Report `debug/v144-rhythm-calibration/candidates/atomic-generated-only-dyad-onset-prune-search.json`; persistence commit `4b5cbe7aeed712917432943dda6cd116618049f5`; report blob `9a4d17622047db77e373a21c40036adc42297482`; bot commit added only the report.
- `rankedRuleCount=23`; `evaluatedCandidateCount=23`; FIT-only construction/ranking; validation/canary construction/ranking false; consumed-family outcomes excluded.
- **FIT RESULT: no candidate qualified.** `fitLock.locked=accepted-v144-baseline`; `lockedReason=deterministic-no-prune-fallback`; `selected=accepted-v144-baseline`; `selectedReason=fit-no-qualified-atomic-generated-only-dyad-prune-candidate`; `stoppedAt=fit`.
- `validation=null`; `canary=null`; `fullCalibration=null`; `splitPromotionAllowed=false`; `calibrationPromotionAllowed=false`.
- Locked fallback is exact family #10: 1144 events / 113 measures / SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; removed events/onsets 0.
- Independent PDF proof PASSED for fallback: fidelity 1.0, exact event count/SHA, professional reference not opened during PDF check.
- Safety clean: V5/main/Production false; runtime reference false; GPU false; deterministic true.

### Sealing / replay refusal
- Executable family #12 workflow deleted at commit `ff854c37b98fca82eb1a1c0552cfbaa382bcdf6e`.
- Trigger deleted at commit `994164b4d760d62098bbcb2cbae38dfdc95d4a55`.
- **Family #12 is consumed. Never rerun/replay/retune and never select a runner-up from its 23 candidates.**
- Accepted baseline remains family #10, so current FIT residual diagnostic `b9794a7b...` remains current.

## Family #13 — PRE-REGISTERED / POLICY TESTS FROZEN / CPU PENDING
### Aggregate-only shape decision
- The sole permitted current shape evidence remains the sealed accepted-baseline FIT residual diagnostic `b9794a7b...`.
- `g3-r0=12` is a non-empty, materially distinct onset cardinality from consumed family #12 (`g2-r0`) and is large enough to preserve the established minimum support without relaxing it.
- `g5-r0=1` remains excluded. Cardinalities may not be combined. No family #11/#12 candidate outcomes, runner-ups, gate behavior, context/string/pitch identities, or calibration labels were used for this decision.
- Therefore family #13 is pre-registered as **atomic exact-three-note generated-only whole-onset prune**. This decision does not authorize candidate search or execution.

### Fixed family #13 semantics — FROZEN BEFORE SEARCH
- Policy path: `modal/v144_rhythm_generated_only_triad_prune_policy.py`; current policy blob `622c839d0a833c3541007309ebf1203f1547b365`.
- Exact cardinality: 3 generated notes and 0 reference notes at one FIT onset.
- Minimum false-positive support: **3**. Maximum candidate count: **256**. These are frozen now and may not be changed after seeing search outcomes.
- Rule identity: exactly one structural onset context plus three sorted source `(stringIndex,pitchClass)` identities.
- Whole-onset deletion is atomic: either all three notes are deleted or none are. Partial deletion is forbidden.
- Runtime reference is forbidden. Linked, externally referenced, invalid-position, and measure-erasing targets are ineligible. Survivors must remain immutable and in source order.
- Any eventual search must enforce exact 113-measure preservation and deterministic family #10 fallback.
- No candidate-specific search file exists by authorization at this checkpoint. No family #13 candidate labels/outcomes may be inspected until policy tests and the broad CPU gate succeed at the exact policy/test revision.

### Deterministic synthetic-only policy tests — FROZEN
- Tests: `modal/tests/test_v144_rhythm_generated_only_triad_prune_policy.py`.
- Exact frozen test commit: `9da8733dbcef8b226c562470b39b17577c450f8a`; test blob `f6055f83e522cf2fcec441368fe201a2db28f566`.
- Tests assert frozen constants `TARGET_GENERATED_NOTE_COUNT=3`, `MIN_SUPPORT=3`, `MAX_CANDIDATES=256`; exact generated-only triad construction; deterministic reversal-invariant ranking; fixed support/cap and three-identity rule shape; exact runtime context/identity matching; atomic three-event deletion; survivor immutability/order; refusal of linked/referenced/measure-erasing triads; invalid rule input rejection.
- Tests are synthetic-only and contain no calibration labels/candidate outcomes.
- Querying Actions for exact test revision `9da8733d...` returned zero workflow runs, so no accidental CPU/search execution occurred. Broad CPU proof is still pending and must be tied to the exact policy/test revision before any search file may exist.

## EXPLICIT NEXT STEPS — CONTINUATION CONTRACT
1. **Re-read this checkpoint first.** Verify branch is exactly `v143-contextual-prune-lobo`, family #12 report blob is `9a4d17622047db77e373a21c40036adc42297482`, and both family #12 execution surfaces remain deleted.
2. **Never rerun families #1–#12.** Do not use their candidate rankings, failed/passed gates, validation/canary/full outcomes, or runner-up behavior to construct/rank/retune family #13.
3. Because family #12 did not change the accepted baseline, **do not create a new residual diagnostic yet**. The sealed current accepted-baseline FIT residual report `b9794a7b...` remains the sole permitted current shape evidence.
4. Family #13 shape decision, support/cap preregistration, policy, and deterministic synthetic policy tests are now frozen as recorded above. Do not revise them from candidate outcomes.
5. Identify the established broad CPU gate used by the immediately preceding safe V144 families, wire the family #13 policy/tests into it if needed, and require definitive **CPU SUCCESS** for policy blob `622c839d...` + test blob `f6055f83...` before a search file may exist. Do not create a substitute ad-hoc gate if the established gate can be reused.
6. Only after policy CPU success, pre-register a FIT-only family #13 search. It must reconstruct accepted family #10 `4e6f9f...` reference-free before opening gold, construct/rank only from FIT, enforce exact 113-measure preservation, and use deterministic family #10 fallback.
7. Add synthetic search invariant tests proving deletion-only ordered-subsequence semantics, exactly 3 removed events per changed onset, locked rule identity, no survivor mutation/addition/reordering, and fixed support/cap. Broad CPU-gate the exact search/test revision.
8. **Do not execute candidate search until the exact search code/tests are CPU green.** If CPU fails, fix only implementation/tests; do not inspect calibration labels to debug it.
9. After search CPU success, create a tightly locked CPU-only one-shot. Lock immutable V5/result/render/PDF, gold SHA, accepted manifest, family #13 policy/tests/search/tests, CPU workflow/run/job, reconstruction/scoring/staged-selector/measure/PDF dependencies, runtime-reference false, GPU false, and replay false.
10. Save a **pre-arm checkpoint containing the exact one-shot workflow blob**. Then create exactly one trigger-only commit with the exact preregistered message/path. Freeze the branch and poll only that exact trigger SHA. No rerun/retrigger/retry.
11. During the one-shot: FIT may rank all preregistered candidates and lock at most one. If no FIT winner, stop at FIT and fall back to family #10. If validation fails, fall back immediately. If canary fails, fall back immediately. Never select a runner-up after any failure.
12. Only if FIT+validation+canary pass may full gold be read for the locked candidate. Calibration promotion additionally requires zero musical regressions, critical mismatch delta <=0, coverage 1.0, exact 113 generated measures, family-specific atomic invariants, and independent PDF-event fidelity 1.0.
13. Immediately after the one-shot, persist only its report, then delete/seal the executable workflow and trigger regardless outcome. Mark family #13 consumed and checkpoint run ID, job ID, report commit/blob, workflow deletion commit, trigger deletion commit, and accepted-baseline result.
14. If family #13 (or any future family) actually becomes the accepted calibration baseline, **the current residual report becomes historical immediately**. Before proposing another family, create a new accepted-baseline FIT-only aggregate residual diagnostic with synthetic tests, CPU pre-label gate, one-shot execution, report-only persistence, and immediate sealing.
15. Never start Bass/Lead, modify `main`/Production or `/ai-tab` frontend, claim Rhythm-complete/near-100/unseen-generalization, or use Modal/L4/GPU without fresh explicit user authorization.

## Current stop point
- Accepted calibration baseline: family #10 `singleton-onset-replace-be9e9aa7a734e3cd` / `4e6f9f...`.
- Families #1–#12: consumed/sealed.
- Family #12: no FIT winner; baseline unchanged.
- Family #13: **aggregate-only shape decision complete; policy semantics frozen; policy blob `622c839d...`; synthetic policy tests frozen at commit `9da8733d...` / blob `f6055f83...`; support 3; cap 256; no policy CPU proof yet; no search; no evaluation; no execution authorization.**
- Safe next action: identify/reuse the established broad CPU gate and obtain exact-revision CPU SUCCESS before any family #13 search file exists.
