# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families 1–11 consumed/sealed. Accepted baseline remains family #10 `singleton-onset-replace-be9e9aa7a734e3cd` / `4e6f9f...`. Family #12 — atomic exact-two-note generated-only dyad whole-onset prune — is PRE-REGISTERED at policy/test level and broad-CPU-gate wired; no search exists and no family #12 labels/candidates have been evaluated.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`; render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Gold reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark, not unseen holdout. V5 holdout permanently consumed.
- Split measure+step seed 144: 60 fit / 20 validation / 20 canary. FIT constructs/ranks only; validation/canary gate one locked winner. FIT pitch gain >=0.005; no musical regression; critical mismatch delta <=0; PDF fidelity 1.0. Gate order fit→validation→canary→full→independent PDF. Any later failure => accepted-baseline fallback; never alternate.
- No Modal/L4/GPU without fresh explicit authorization. `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.

## Accepted V144 Rhythm calibration baseline — LOCKED
- `singleton-onset-replace-be9e9aa7a734e3cd`; manifest `debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json`; commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- 1144 events / 113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity 1.0.
- Full gold: critical 1712; pitch 0.35406698564593303; pitch/timing 0.06698564593301436; string/fret/timing 0.05454545454545454; chord/voicing 0.0580511402902557; coverage 1.0.
- Reconstruction CPU `32996069426` / `98265545933` SUCCESS. Production false; Rhythm complete false; near-100 false; unseen-generalization false.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
1 single-event prune; 2 two-signature prune; 3 triple prune; 4 four-signature prune; 5 same-string pitch; 6 pitch+step; 7 pitch+adjacent-string; 8 pitch+step+position; 9 atomic shared dyad pitch rewrite; 10 atomic singleton replacement; 11 atomic generated-only singleton prune.
- Family #10 one-shot `32995503662`; report blob `92de07b1cac11cba87e923c18eebf9cce7b0cea7`; consumed.
- Family #11 one-shot `32998471525` / job `98273767947`; report commit `56e2035870b6439f68eb49ebae3489f982fca0c0`; blob `9d1b46d8fcc45465a55f018363fd32e22e120068`; 110 ranked / 109 evaluated; **no FIT-qualified candidate**, deterministic family #10 fallback; validation/canary/full null; PDF fallback fidelity 1.0. Workflow deleted `a16c4ca689092335954b70f480791ad6668aa0e7`; trigger deleted `7cd464f3d10294a1b8c27a61e767e2a322629580`. Never use its candidate outcomes/runners-up for successor construction.

## Current accepted-baseline FIT residual diagnostic — SEALED / CURRENT
- Diagnostic blob `27ac8699279db8fc0208d067479ad3751da1a630`; report `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`; commit `dd06bd96061170e6c25a8ffe6b4d91db941491fc`; blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`; one-shot `32996989280` SUCCESS and sealed.
- Candidate construction/ranking/selection false; no rule/shift histogram; validation/canary false; runtime reference false; GPU false.
- FIT aggregate: generated 643 / reference 594; pitch matched 176; tight timing 41; gross timing 90; exact position/timing 34.
- Onsets: generated 485 / reference 370 / shared 190 / generated-only 295 / reference-only 180.
- Generated-only cardinalities: `g1-r0=203`, **`g2-r0=79`**, `g3-r0=12`, `g5-r0=1`; shared cardinality mismatch 84; same-onset extra-generated slots 431.
- This diagnostic alone may inform family shape while baseline remains `4e6f9f...`; consumed-family outcomes may not.

## Family #12 — atomic exact-two-note generated-only dyad whole-onset prune — PRE-REGISTERED / PRE-CPU
### Why permitted / materially distinct
- Shape comes only from current sealed aggregate diagnostic: 79 generated-only dyad onsets, the dominant multi-note generated-only cardinality.
- Distinct from family #11: exactly two generated notes deleted atomically, not one.
- Distinct from family #9: family #9 was a shared generated/reference dyad **pitch rewrite**; family #12 is a generated-only dyad **whole-onset deletion** with zero reference notes used only during FIT construction.
- Does not mix dyads with triads/5-note onsets; cardinality fixed at exactly 2 before search.

### Fixed policy before any candidate search
- Policy `modal/v144_rhythm_generated_only_dyad_prune_policy.py`.
- Pre-registration commit `cc9370af575aa1dcc6a650eea8b0f4a16616742f`; blob `21ece8eaedc1210c9e55eedfd686163ae7f5e1f7`.
- Fixed minimum false-positive support `3`; max candidates `256`.
- Construction: same FIT onset has exactly 2 generated events and 0 reference notes; source positions valid; linked pitch events excluded.
- Rule identity: one structural onset context (`measurePhase`, `section16`, `stepParity`, `stepQuarter`, `measurePhaseStep`) + two **sorted** `(sourceStringIndex, sourcePitchClass)` identities.
- Runtime receives generated events + locked rule only; reference forbidden. Runtime onset must contain exactly 2 generated events at same measure/step and exact sorted identities/context.
- Atomic whole-onset deletion only; partial deletion impossible. Both events must have valid tuning positions, no pitch linkage, and no event-reference dependency. Rule refuses deletion if the dyad is the entire remaining measure. Survivors preserve order/timing/duration/techniques/all metadata.
- Event count may decrease; later search must require exact 113 generated-measure preservation.

### Synthetic tests / CPU wiring
- Tests `modal/tests/test_v144_rhythm_generated_only_dyad_prune_policy.py`; commit `5325c25de53831ba148015875cca8875fa9c2c19`; blob `0ae23f3735b0ebca178eea81352ed2e83474f204`.
- Seven synthetic tests cover: exact generated-only dyad construction; deterministic reversal; fixed support/cap/rule shape; exact dyad/context/two-note identity matching; atomic two-event deletion + survivor preservation; measure-erasure/link/reference refusal; invalid rule rejection.
- Broad CPU gate wiring commit `885fa851e5a0d404fdfc41ff006448c8bc42c9b9`; workflow blob `84606b8425ba6227aa0454d35e9d3399a2728f8c`.
- Wiring adds only family #12 policy/test paths, policy `py_compile`, and synthetic test execution. **No family #12 search or calibration-label execution surface exists.**

## Immediate next actions
1. Require the broad CPU gate for commit `885fa851...` to finish SUCCESS and explicitly verify policy compile + all seven family #12 synthetic tests.
2. If gate fails, fix policy/tests only; do not create search.
3. Only after CPU SUCCESS, pre-register family #12 FIT-only search with fixed support 3/max256, accepted family #10 reconstruction, deletion-only exact-dyad invariant, exact 113-measure guard, fixed staged selector, deterministic fallback, and no validation/canary construction/ranking.
4. Add synthetic search invariant tests and broad CPU-gate them before any one-shot evaluation.
5. Never start Bass/Lead, main/Production, near-100 claims, or Modal/L4/GPU.
