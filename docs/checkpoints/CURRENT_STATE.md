# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families 1–12 are consumed/sealed. Accepted baseline remains family #10 `singleton-onset-replace-be9e9aa7a734e3cd` / SHA `4e6f9f...`. Family #12 atomic exact-two-note generated-only dyad whole-onset prune completed its single authorized one-shot and STOPPED AT FIT with deterministic family #10 fallback; validation/canary/full were never opened. Family #12 execution surfaces are deleted. No family #13 is pre-registered.**

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
- Report `debug/v144-rhythm-calibration/candidates/atomic-generated-only-dyad-onset-prune-search.json`; persistence commit `4b5cbe7aeed712917432943dda6cd116618049f5`; report blob `9a4d17622047db77e373a21c40036adc42297482`; bot commit added only the 1300-line report.
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

## Immediate next actions
1. Use only sealed current residual aggregate `b9794a7b...` to assess a materially distinct family #13. Do NOT use family #11/#12 candidate outcomes.
2. Aggregate-only candidate unit to assess: atomic exact-three-note generated-only whole-onset prune, because current diagnostic independently reports `g3-r0=12`. Keep cardinality exactly 3; do not mix with g5-r0=1.
3. If justified, pre-register policy shape/support/cap and synthetic tests before any search; CPU-gate policy/tests first.
4. If no clear distinct unit is justified, stop rather than retune consumed shapes.
5. Never start Bass/Lead, main/Production, near-100 claims, or Modal/L4/GPU.
