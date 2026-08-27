# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm baseline preserved. V145 Stage1/Stage2/adapter/evaluator are CPU-proven/sealed. Consumed V145 real one-shot remains sealed with no candidate/score. V146 artifact-first Phase A has now succeeded, persisted one generated-only candidate, and is sealed. Phase B calibration evaluation is not yet preregistered. No Modal/L4/GPU/live audio without fresh explicit authorization.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- No Modal/L4/GPU/live audio without fresh explicit authorization.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark only, never unseen holdout.
- No automatic promotion. Family #10 remains accepted unless a separate later promotion protocol is frozen and succeeds.

## Accepted Rhythm baseline — UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- **Pitch Content 35.4%**, **Pitch + timing 6.7%**, **String/fret + timing 5.5%**, **Chord/voicing 5.8%**, **Measure coverage 100%**, **PDF event fidelity 100%**.
- Exact: pitch `0.35406698564593303`; pitch/timing `0.06698564593301436`; string/fret/timing `0.05454545454545454`; chord pitch-set `0.0580511402902557`; exact voicing `0.0580511402902557`; coverage/PDF `1.0`.
- 1144 events /113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; critical mismatch count 1712.
- Accepted manifest blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.

## V144 consumed state
- Families #1–#14 consumed/sealed; never replay/reselect/retune or use consumed-family observed outcomes to shape successors.
- Family #14 report blob `a13df8e17ae2c813d4602dd10dd642327a5d2b75`.
- Current accepted-baseline aggregate FIT residual blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.

## V145 proven components
- Stage1 blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`; proof run `33026865312` SUCCESS.
- Stage2 blob `5f86f57d0fd10774690d50528d51bad6e0392bf3`; proof run `33027229509` SUCCESS.
- Stage3 generated-only adapter blob `434d4b2582991c216df411455f232b8d211337c6`; proof blob `f55dcd1087f108d0d93c4a5a1a86cb5058ef4eb4`; proof run `33029862099` SUCCESS.
- Stage3 evaluator blob `d208abb3f180f8375d57d786941ff49d6813de1c`; proof blob `81c10bdcc39ce9e371fda60d2c3d107e671b8790`; proof run `33031101564` SUCCESS.
- Frozen evaluation order remains candidate-only validation -> pre-reference freeze/PDF gate -> candidate/freeze/PDF identity -> accepted manifest -> only then gold bytes/hash/validate -> exactly one score.

## Frozen validation/render chain
- canonical `088d44827fb23e20d9aeeb4944a672989af5846c`
- freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`
- scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`
- full-score helper `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`
- PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`
- render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`

## First real V145 Stage3 calibration one-shot — CONSUMED / FAILED CLOSED / SEALED
- Run `33031523386`, job `98384901171`: failure at first workflow-identity gate before candidate/calibration work.
- No candidate, freeze, gold read, score, or result existed.
- Workflow deletion `0d83c411fcff78b7f7083d2a968f85bd9522870d`; trigger deletion `b3e407413b76138722699690c8f15ca67283ab72`.
- Never rerun/rearm/recreate this same V145 execution.

## V146 artifact-first calibration
### Preregistration
- `docs/v146-rhythm-artifact-first-calibration-preregistration.md`
- creation commit `86729595bab64ac80b82180532ee4dc94fca9817`
- prereg blob `0125201e86389b21dee3ceb2e7ecd25dc67dfe84`
- V146 separates generated-only artifact construction from any later calibration evaluation; no musical parameter change was made.

### Phase A — GENERATED-ONLY ARTIFACT / SUCCESS / SEALED
- Workflow creation/trigger commit `246d7dba0f7b3d2955feed90446353de8302da6f`; workflow blob `63812af5182795995129b961f8926b9a2b04dd1d`.
- Run `33031802198`, job `98385781107`, attempt1: **SUCCESS**.
- Every step passed: immutable generated-only identities, constructor isolation, frozen Stage1/Stage2/adapter CPU tests, exactly one adapter invocation, independent artifact invariants, persistence.
- Persistence commit `e5d7d9dd9bdce8bf0eeee7f2a8207475ddbd31d3`.
- Candidate `debug/v146-rhythm-artifact/generated-only-candidate.json`; Git blob `61bda87e4a16b752bfaaf68c2d51e7020f31a7f8`.
- Construction proof `debug/v146-rhythm-artifact/generated-only-candidate-proof.json`; Git blob `abb8fcd1726bf9b8caa5bf8432adae2c6915a483`; schema14601.
- Candidate canonical event identity: **1209 events /113 measures / SHA256 `2de0a686cfd797a19aa02af735aa2bfaf0e65245ec85a5148c71f8b8b3a77c40`**.
- Decoder grid: quantum `0.1161`, phase `0.115791`, support `1.0`, evidenceCount1209, candidateCount13244, median normalized residual `0.0008091976383478138`.
- Decoder decoded all 1209 notes /891 groups; undecodedSourceCount0.
- Adapter applied 1163 notes across 851 groups; 40 protected groups/sources preserved; no collisions/residual failures.
- Generated-only descriptive changes vs V5 source: **871 changed events; fret changed871; stringIndex changed871; measure changed0; step changed0**.
- Therefore this frozen candidate is a string/fret/voicing reinterpretation of the V5 event stream; it did not change MIDI evidence or timing cells during Phase A.
- Proof explicitly states `referenceFree=true`, `acceptedManifestRead=false`, `realGoldRead=false`, `calibrationScoreRun=false`, `candidateSearchRun=false`, `alternateCandidateConstructed=false`, `acceptedBaselineChanged=false`, `promotionAllowed=false`, `modalGpuUsed=false`, `liveAudioBenchmarkRun=false`.
- Phase A workflow deletion/sealing commit `a79e9717e0dbebdd730dfabaef068c78b45a5109`. Never rerun Phase A.

### Phase B boundary — NOT YET PREREGISTERED
- Phase B may only consume the exact persisted candidate event SHA `2de0a686...`; it may not reconstruct, mutate, search, rank, or select another candidate.
- Any Phase B must independently freeze the persisted artifact, validate renderer/PDF event identity, then use the already-proven evaluator to open calibration inputs only after pre-reference gates.
- Phase B result remains calibration benchmark evidence only; no automatic promotion.

## EXPLICIT NEXT STEPS
1. Design and preregister V146 Phase B around exact Phase A candidate/proof identities before any calibration access.
2. Phase B must freeze/render/PDF-prove exactly the persisted 1209-event candidate; no reconstruction or mutation.
3. Only after those gates may the frozen evaluator open accepted family #10 manifest and gold, and score exactly once.
4. Persist only the Phase B calibration report/proof, seal its workflow, and checkpoint immediately.
5. Regardless of score, accepted family #10 remains **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100** absent a separate promotion protocol.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V146 Phase A candidate is now fixed and sealed at event SHA `2de0a686cfd797a19aa02af735aa2bfaf0e65245ec85a5148c71f8b8b3a77c40`.
- No V146 calibration score exists yet; Phase B has not opened calibration material.
