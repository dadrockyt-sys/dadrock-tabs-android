# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm baseline preserved. V145 Stage1/Stage2/adapter/evaluator are CPU-proven/sealed. Consumed V145 real one-shot remains sealed with no candidate/score. V146 Phase A generated-only candidate is fixed/sealed. V146 Phase B fixed-artifact calibration evaluation is now preregistered after candidate sealing and before any Phase B calibration access. No Modal/L4/GPU/live audio without fresh explicit authorization.**

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

## V145 frozen/proven foundation
- Stage1 blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`; proof run `33026865312` SUCCESS.
- Stage2 blob `5f86f57d0fd10774690d50528d51bad6e0392bf3`; proof run `33027229509` SUCCESS.
- Stage3 adapter blob `434d4b2582991c216df411455f232b8d211337c6`; proof blob `f55dcd1087f108d0d93c4a5a1a86cb5058ef4eb4`; run `33029862099` SUCCESS.
- Stage3 evaluator blob `d208abb3f180f8375d57d786941ff49d6813de1c`; proof blob `81c10bdcc39ce9e371fda60d2c3d107e671b8790`; run `33031101564` SUCCESS.
- Frozen evaluator order: candidate-only validation -> pre-reference freeze/PDF gate -> candidate/freeze/PDF identity -> accepted manifest -> only then gold hash/validate -> exactly one score.

## First real V145 execution — CONSUMED / FAILED CLOSED / SEALED
- Run `33031523386`, job `98384901171`: workflow identity failure before candidate/calibration work.
- No candidate, gold read, score, or result existed. Workflow/trigger sealed. Never retry that execution.

## V146 artifact-first protocol
### Overall preregistration
- `docs/v146-rhythm-artifact-first-calibration-preregistration.md`; creation commit `86729595bab64ac80b82180532ee4dc94fca9817`; blob `0125201e86389b21dee3ceb2e7ecd25dc67dfe84`.
- V146 separates generated-only artifact construction from later evaluation; no musical parameter changed from V145.

### Phase A — GENERATED-ONLY ARTIFACT / SUCCESS / SEALED
- Workflow creation commit `246d7dba0f7b3d2955feed90446353de8302da6f`; workflow blob `63812af5182795995129b961f8926b9a2b04dd1d`.
- Run `33031802198`, job `98385781107`: SUCCESS; persistence commit `e5d7d9dd9bdce8bf0eeee7f2a8207475ddbd31d3`; workflow deletion `a79e9717e0dbebdd730dfabaef068c78b45a5109`.
- Candidate `debug/v146-rhythm-artifact/generated-only-candidate.json`; Git blob `61bda87e4a16b752bfaaf68c2d51e7020f31a7f8`.
- Construction proof `debug/v146-rhythm-artifact/generated-only-candidate-proof.json`; blob `abb8fcd1726bf9b8caa5bf8432adae2c6915a483`; schema14601.
- Candidate: **1209 events /113 measures / canonical event SHA `2de0a686cfd797a19aa02af735aa2bfaf0e65245ec85a5148c71f8b8b3a77c40`**.
- Generated-only changes vs V5 source: 871 events changed; stringIndex871; fret871; measure0; step0. MIDI/event count/order/measure set preserved.
- Phase A proof: referenceFree=true, acceptedManifestRead=false, realGoldRead=false, calibrationScoreRun=false, alternateCandidateConstructed=false, acceptedBaselineChanged=false, modalGpuUsed=false.

### Phase B — FIXED-ARTIFACT CALIBRATION / PREREGISTERED / NOT YET RUN
- Prereg `docs/v146-rhythm-phase-b-calibration-evaluation-preregistration.md`.
- Creation commit `791aef9a0e8f48cd7d1e3672b2fa0b2469fa6a2c`.
- Frozen prereg blob **`82bd04d819f26106a831f67a1a61ccba6e876c08`**.
- Phase B may consume only candidate blob `61bda87...` / canonical event SHA `2de0a686...`; no reconstruction, mutation, candidate search, ranking, fallback, retuning, or alternate selection.
- Mandatory order: exact candidate/proof/dependency identity -> independent candidate identity -> temporary freeze from persisted events -> renderer contract -> PDF fidelity exactly1.0 with identical 1209-event SHA -> only then invoke frozen evaluator -> evaluator pre-reference gate -> accepted manifest -> gold SHA/validate -> exactly one score -> observational proof.
- Frozen outputs: `debug/v146-rhythm-artifact/calibration-score.json` and `debug/v146-rhythm-artifact/calibration-evaluation-proof.json`; both must be absent before execution.
- Phase B is calibration benchmark only; promotionAllowed remains false regardless of score. If Phase B fails any gate, fail closed and never rerun that exact execution.

## Frozen validation/render identities
- canonical `088d44827fb23e20d9aeeb4944a672989af5846c`
- freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`
- scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`
- full-score helper `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`
- PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`
- render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`
- accepted manifest blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`
- calibration gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.

## EXPLICIT NEXT STEPS
1. Create exactly one V146 Phase B workflow whose creation triggers evaluation of the already-sealed candidate only; no workflow-blob self-binding or candidate construction.
2. Freeze/render/PDF-prove the persisted candidate before evaluator invocation.
3. Use the frozen evaluator exactly once; persist only calibration score + Phase B proof.
4. Seal/delete the Phase B workflow and checkpoint exact metrics/deltas and identities immediately.
5. Do not auto-promote or rerun regardless of result; accepted family #10 remains unchanged absent a later promotion protocol.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V146 candidate is fixed/sealed at SHA `2de0a686cfd797a19aa02af735aa2bfaf0e65245ec85a5148c71f8b8b3a77c40`.
- Phase B is frozen before calibration access; no V146 score exists yet.
