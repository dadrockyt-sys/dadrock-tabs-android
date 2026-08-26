# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families 1–11 consumed/sealed. Accepted baseline remains family #10 `singleton-onset-replace-be9e9aa7a734e3cd` / SHA `4e6f9f...`. Family #12 — atomic exact-two-note generated-only dyad whole-onset prune — has pre-registered policy/search implementations and synthetic policy/search tests; BOTH broad CPU gates are GREEN. No family #12 one-shot exists yet and no family #12 candidate evaluation has executed.**

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

## Consumed families
- Families 1–11 consumed; never replay/reselect/retune.
- Family #11 one-shot `32998471525` / job `98273767947`; report commit `56e2035870b6439f68eb49ebae3489f982fca0c0`; blob `9d1b46d8fcc45465a55f018363fd32e22e120068`; 110 ranked / 109 evaluated; no FIT-qualified candidate; stoppedAt fit; validation/canary/full null; deterministic family #10 fallback; workflow deleted `a16c4ca689092335954b70f480791ad6668aa0e7`; trigger deleted `7cd464f3d10294a1b8c27a61e767e2a322629580`.

## Current accepted-baseline FIT residual diagnostic — SEALED / CURRENT
- Report `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`; commit `dd06bd96061170e6c25a8ffe6b4d91db941491fc`; blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`; candidate construction/ranking/selection false; validation/canary false; runtime reference/GPU false.
- FIT aggregate: generated 643 / reference 594; pitch matched 176; tight timing 41; gross timing 90; exact position/timing 34.
- Onsets: generated 485 / reference 370 / shared 190 / generated-only 295 / reference-only 180. Generated-only cardinalities: g1-r0=203, **g2-r0=79**, g3-r0=12, g5-r0=1. This diagnostic alone may inform family shape while baseline unchanged.

## Family #12 — atomic exact-two-note generated-only dyad whole-onset prune
### Policy — PRE-REGISTERED / CPU GREEN
- Justified only by current aggregate `g2-r0=79`; distinct from family #11 singleton deletion and family #9 shared-dyad pitch rewrite.
- Policy `modal/v144_rhythm_generated_only_dyad_prune_policy.py`; commit `cc9370af575aa1dcc6a650eea8b0f4a16616742f`; blob `21ece8eaedc1210c9e55eedfd686163ae7f5e1f7`.
- Fixed support `3`; max candidates `256`.
- Construction: exact 2 generated events + zero FIT reference notes at same onset. Rule identity: one structural context + two sorted `(sourceStringIndex, sourcePitchClass)` identities.
- Runtime reference forbidden; entire dyad deleted atomically; no partial deletion; invalid/linked/referenced events excluded; measure-erasing deletion refused; survivors preserve all metadata/order/timing. Event count may decrease but exact 113 generated measures are required.
- Policy tests `modal/tests/test_v144_rhythm_generated_only_dyad_prune_policy.py`; commit `5325c25de53831ba148015875cca8875fa9c2c19`; blob `0ae23f3735b0ebca178eea81352ed2e83474f204`; seven synthetic tests.
- Policy CPU wiring commit `885fa851e5a0d404fdfc41ff006448c8bc42c9b9`; workflow blob `84606b8425ba6227aa0454d35e9d3399a2728f8c`.
- Policy CPU run `32999064437`, job `98275778909`: SUCCESS; policy compile + all seven policy tests + immutable/provenance/config guards passed.

### FIT-only search — PRE-REGISTERED / CPU GREEN / NOT EXECUTED
- Search `validation/v144_rhythm_calibration/search_atomic_generated_only_dyad_prunes.py`; creation commit `9dfafbbe460974b316f5ccd8a6c3f1a103ab60ac`; blob `6870c1ba34e0b3d9baa63c7f9bb036851ccca0ac`.
- Search tests `modal/tests/test_v144_rhythm_generated_only_dyad_prune_search.py`; creation commit `f6358e99d4df4bc2e73f5d7bedbaeaae8c45cf82`; blob `2b45a35b75e340e21343d06728c1768325040be9`; seven synthetic invariant tests.
- Search locks family #10 accepted baseline name/SHA/1144/113 and reconstructs it reference-free before opening gold.
- Fixed support 3/max256 cannot be relaxed. FIT-only construction/ranking; validation/canary cannot construct/rank. Any later failure deterministically falls back to family #10 and never selects an alternate.
- Deletion invariant: candidate is a survivor-identical ordered subsequence; no additions/mutations; removed event count must be even; every changed onset had exactly two baseline events and matches the locked rule; `removedEventCount = 2 * removedOnsetCount`; exact 113-measure guard.
- Report schema `14424`; classification `v144-rhythm-fit-only-atomic-generated-only-dyad-onset-prune-search`; runtime reference false; GPU false.
- Broad search-gate wiring/current head commit `d6f1f7cbc61c3c7a4b6a880b6f60a89e59acf9ed`; workflow blob `d607707fb802808c194137544aa68472e6ec49fb`.
- Search CPU run `32999506459`, job `98277305962`: **SUCCESS**. Search compiled; all seven `AtomicGeneratedOnlyDyadPruneSearchInvariantTests` passed; all seven family #12 policy tests passed; accepted family #10 reconstruction tests passed; immutable V5/provenance/config guards passed.
- Broad gate does NOT execute family #12 search. **No family #12 candidate rules have been constructed/ranked/evaluated. Validation/canary remain closed.**

## Immediate next actions
1. Pre-register exactly one tightly locked CPU-only family #12 one-shot, unarmed first. It must pin accepted manifest `acd12...`, family #12 policy `21ece8...`, policy tests `0ae23f...`, search `6870c1...`, search tests `2b45a3...`, CPU workflow `d607707...`, CPU run/job `32999506459`/`98277305962`, support 3/max256, runtime reference/GPU/replay false.
2. One-shot independent PDF proof must use the actual locked count-changing stream event count/SHA. Final promotion invariant requires non-baseline locked candidate, removedEventCount>0 even, removedOnsetCount*2=removedEventCount, eventCount=1144-removedEventCount, exact 113 measures, no musical regressions, critical delta<=0, coverage 1.0, PDF fidelity 1.0, exact atomic-two-note deletion semantics.
3. Save checkpoint with unarmed workflow commit/blob before creating one trigger-only commit.
4. Execute at most once; immediately delete workflow+trigger regardless outcome and mark family #12 consumed. Never select a runner-up.
5. If no FIT winner/later failure, family #10 remains accepted. If fully passing, create a separate calibration-only promotion manifest + reference-free reconstruction proof before calling family #12 accepted.
6. Never start Bass/Lead, main/Production, near-100 claims, or Modal/L4/GPU.
