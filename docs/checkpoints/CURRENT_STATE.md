# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families 1–11 consumed/sealed. Accepted baseline remains family #10 `singleton-onset-replace-be9e9aa7a734e3cd` / `4e6f9f...`. Family #12 — atomic exact-two-note generated-only dyad whole-onset prune — is PRE-REGISTERED at policy/test level and its policy CPU gate is GREEN. No family #12 search exists and no family #12 candidate labels have been evaluated.**

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
- Reconstruction CPU `32996069426` / `98265545933` SUCCESS. Production/Rhythm-complete/near100/unseen-generalization all false.

## Consumed families
- Families 1–11 consumed; never replay/reselect/retune.
- Family #11 one-shot `32998471525` / `98273767947`; report commit `56e2035870b6439f68eb49ebae3489f982fca0c0`; blob `9d1b46d8fcc45465a55f018363fd32e22e120068`; 110 ranked / 109 evaluated; no FIT-qualified candidate; stoppedAt fit; validation/canary/full null; deterministic family #10 fallback; workflow deleted `a16c4ca689092335954b70f480791ad6668aa0e7`; trigger deleted `7cd464f3d10294a1b8c27a61e767e2a322629580`.

## Current accepted-baseline FIT residual diagnostic — SEALED / CURRENT
- Report `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`; commit `dd06bd96061170e6c25a8ffe6b4d91db941491fc`; blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`; candidate construction/ranking/selection false; validation/canary false; runtime reference/GPU false.
- FIT aggregate: generated 643 / reference 594; pitch matched 176; tight timing 41; gross timing 90; exact position/timing 34.
- Onsets: generated 485 / reference 370 / shared 190 / generated-only 295 / reference-only 180. Generated-only cardinalities: g1-r0=203, **g2-r0=79**, g3-r0=12, g5-r0=1. This diagnostic alone may inform family shape while baseline unchanged.

## Family #12 — atomic exact-two-note generated-only dyad whole-onset prune — POLICY CPU GREEN
### Fixed shape / policy
- Justified only by current aggregate g2-r0=79. Distinct from family #11 singleton deletion and family #9 shared dyad pitch rewrite.
- Policy `modal/v144_rhythm_generated_only_dyad_prune_policy.py`; commit `cc9370af575aa1dcc6a650eea8b0f4a16616742f`; blob `21ece8eaedc1210c9e55eedfd686163ae7f5e1f7`.
- Fixed support 3 / max candidates 256.
- Construction: exact 2 generated events + zero FIT reference notes at same onset. Rule identity: one structural context + two sorted `(sourceStringIndex, sourcePitchClass)` identities.
- Runtime reference forbidden; exact two-note onset/source identities required; entire dyad deleted atomically; no partial deletion; invalid/linked/referenced events excluded; measure-erasing deletion refused; survivors preserve all metadata/order/timing. Event count may decrease but later search must preserve exact 113 measures.
- Tests `modal/tests/test_v144_rhythm_generated_only_dyad_prune_policy.py`; commit `5325c25de53831ba148015875cca8875fa9c2c19`; blob `0ae23f3735b0ebca178eea81352ed2e83474f204`; seven synthetic tests.
- Broad wiring commit `885fa851e5a0d404fdfc41ff006448c8bc42c9b9`; workflow blob `84606b8425ba6227aa0454d35e9d3399a2728f8c`.
- Policy CPU run `32999064437`, job `98275778909`: **SUCCESS**. Logs explicitly show new policy compiled and all seven `GeneratedOnlyDyadPrunePolicyTests` passed; immutable V5/provenance/config guards passed.
- **No family #12 search exists. No candidate rules have been constructed/ranked/evaluated. Validation/canary closed.**

## Immediate next actions
1. Pre-register family #12 FIT-only search using fixed support 3/max256, accepted family #10 reference-free reconstruction, exact-two-note atomic deletion invariant, deletion-only survivor subsequence, exact 113-measure guard, fixed staged selector, deterministic family #10 fallback, and validation/canary no construction/ranking.
2. Add synthetic search invariant tests; broad CPU-gate search/tests before any one-shot.
3. Only after search CPU SUCCESS may a single locked CPU-only one-shot be pre-registered/armed.
4. Never use family #11 outcomes/runners-up to shape or rank family #12.
5. Never start Bass/Lead, main/Production, near-100 claims, or Modal/L4/GPU.
