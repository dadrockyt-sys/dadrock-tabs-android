# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm baseline preserved; Families #1–#14 fully consumed/sealed. V145 Stage 1, Stage 2, and Stage 3 generated-only adapter are CPU-proven/sealed. Stage 3 evaluation harness is preregistered/implemented; its definitive synthetic CPU-proof workflow is frozen but NOT YET ARMED. No real Stage 3 candidate/score has run. No Modal/L4/GPU/live audio without fresh explicit authorization.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- No Modal/L4/GPU/live audio without fresh explicit authorization.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark only, never unseen holdout.

## Permanent accepted Rhythm baseline — UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- **Pitch Content 35.4%**, **Pitch + timing 6.7%**, **String/fret + timing 5.5%**, **Chord/voicing 5.8%**, **Measure coverage 100%**, **PDF event fidelity 100%**.
- Exact: pitch `0.35406698564593303`; pitch/timing `0.06698564593301436`; string/fret/timing `0.05454545454545454`; chord/voicing `0.0580511402902557`; chord pitch-set and exact voicing both `0.0580511402902557`; coverage/PDF `1.0`.
- 1144 events /113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; critical mismatch count 1712.
- Accepted manifest blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.

## V144 consumed state
- Families #1–#14 consumed/sealed; never replay/reselect/retune or use observed consumed-family outcomes to shape successors.
- Family #14 report blob `a13df8e17ae2c813d4602dd10dd642327a5d2b75`; workflow deletion `443031fd2294e05b23290c71b0e2b712198d842a`; trigger deletion `e9536f2b4c122741f50aa317e2bbd332d0a9d03b`.
- Current accepted-baseline FIT residual blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.

## V145 Stage 1 — FROZEN / CPU-PROVEN / SEALED
- `modal/v145_rhythm_decoder.py` blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`; tests `9d48b02316f4eb364b163b3027c6c4d79304ac27`.
- Proof run `33026865312`, job `98370167258`: SUCCESS; proof blob `978c2b7cd984f2cece23d2bc152f6acca28980e1`; proof workflow deletion `e802d7a867ee5f965be0c6abe51f70b6c0e6af6b`.

## V145 Stage 2 — FROZEN / CPU-PROVEN / SEALED
- `modal/v145_rhythm_sequence_decoder.py` blob `5f86f57d0fd10774690d50528d51bad6e0392bf3`; tests blob `b16b8d2060e1ea3b47225f1c7c6072cb260c0db8`.
- Proof run `33027229509`, job `98371326572`: SUCCESS; proof blob `0522dd00598fcd5916349cb9747ca3588eaedb90`; workflow deletion `68d1d95859e511f183bf857e5035b8b7635c8bc2`.

## V145 Stage 3 generated-only adapter — FROZEN / CPU-PROVEN / SEALED
- Main prereg `docs/v145-rhythm-decoder-stage3-offline-preregistration.md`; creation commit `64319400dcaa7d23850e8eda8985e823d24ff9a1`; blob `bb60a3bcc5f6e136eb6efb5706828379e007ec1d`.
- V5 stream `debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json`; git blob `fe61f7ad53a4d71348a5113ecc9e3876eaad98d4`; raw SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; 1209 events /113 measures /tempo `129.19921875` /4/4 /E Standard.
- Adapter `validation/v145_rhythm_decoder/offline_stage3_adapter.py`; frozen blob `434d4b2582991c216df411455f232b8d211337c6`.
- Synthetic tests `modal/tests/test_v145_rhythm_stage3_offline_adapter.py`; frozen blob `3eee7ae5253ad0eecbeb492eaa24216f0fa21fee`.
- Adapter uses exactly one Stage2 call and no gold/reference/labels. Event count/list order/eventIndex/MIDI remain immutable; protected technique/bend/legato groups remain source-exact; only atomic unprotected groups may change measure/step/stringIndex/fret; coverage remains exactly113; no add/delete/new pitch.
- Definitive CPU proof run `33029862099`, job `98379640869`, attempt1: SUCCESS.
- Proof `debug/v145-rhythm-decoder/proofs/cpu-stage3-offline-adapter-proof.json`; blob `f55dcd1087f108d0d93c4a5a1a86cb5058ef4eb4`; persistence commit `03a0cfcc5eceae64cc37a02e84481c5a8a2ec1de`; schema14503.
- Proof states realV5CandidateBuilt=false, calibrationScoreRun=false, reference/gold/labels=false, Modal/GPU/liveAudio=false, acceptedBaselineChanged=false.
- Proof workflow blob `1e1b386824ba4bcdab7e51a4ed14f361e39e2457`; deletion/sealing commit `39d20843a6d4211e2aa629afa3fedbc45c36e82a`. Never rerun it.

## Frozen Stage 3 validation/render chain
- canonical `088d44827fb23e20d9aeeb4944a672989af5846c`
- freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`
- scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`
- full-score helper `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`
- PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`
- render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`
- calibration gold path `debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json`, raw SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.

## V145 Stage 3 evaluation harness — PREREGISTERED / IMPLEMENTED / CPU PROOF PRE-ARMED
- Prereg `docs/v145-rhythm-decoder-stage3-evaluation-preregistration.md`.
- Creation commit `d40aecf6fdfd784b3c918c3ee2586fc5904cc147`; frozen prereg blob `9b3542f33fb0f9149056b1eafb8c5db1864299ca`.
- Implementation `validation/v145_rhythm_decoder/score_offline_stage3_candidate.py`; commit `11873b539784d997ff03749ac8c2bfd8e2cef99f`; frozen blob `d208abb3f180f8375d57d786941ff49d6813de1c`.
- Synthetic ordering/invariant tests `modal/tests/test_v145_rhythm_stage3_offline_score.py`; creation commit `6aea9f2435743c7399720d0b0c746a2bb68a1f4a`; frozen blob `d8b3770ac7f3ba18123122f19fad895257998c25`.
- Mandatory runtime order: candidate-only validation -> frozen `validate_pre_reference(freeze_dir)` -> candidate/freeze/PDF identity -> accepted baseline manifest -> only then read/hash/validate gold -> score already-frozen candidate exactly once -> deterministic report.
- Harness CLI remains exactly five positional paths. Synthetic dependency injection exists only to prove ordering without touching real gold.
- Candidate gate requires 1209 canonical events, exact metadata SHA, exact measures1..113, eventIndex0..1208, PDF/freeze SHA identity and fidelity1.0, and safety `referenceFree=true`, `professionalReferenceUsed=false`, `referenceRuntimeInputUsed=false`, `goldInputUsed=false`, `acceptedBaselineChanged=false`.
- Synthetic tests cover: valid ordered path with exactly one score and no mutation; failed pre-reference prevents both calibration reads; candidate/freeze mismatch prevents both calibration reads; wrong accepted manifest fails before gold; wrong gold SHA fails before parse/score; candidate-only safety failure prevents pre-reference/calibration reads.
- Definitive proof workflow `.github/workflows/v145-stage3-evaluation-harness-cpu-proof.yml`; creation commit `4e8e6481ea5e5d9ee70ff73c718598090b247434`; frozen blob `e87e9a53dbc7cdddcd9315ace3477a26a5af8d8a`.
- Proof workflow permits only synthetic harness tests; it explicitly forbids real gold read, real V5 candidate build, Modal/GPU, replay, and persists only `debug/v145-rhythm-decoder/proofs/cpu-stage3-evaluation-harness-proof.json` on success.
- **Workflow is frozen but not armed at this checkpoint. No real V5 Stage3 candidate has been built; no real calibration gold has been read/scored.**

## EXPLICIT NEXT STEPS
1. Arm the frozen harness CPU proof exactly once with sole trigger `debug/v145-rhythm-decoder/.v145-stage3-evaluation-harness-proof-trigger` and exact message `v145 prove stage3 evaluation harness cpu once`; trigger must bind this pre-arm checkpoint commit and workflow blob `e87e9a53dbc7cdddcd9315ace3477a26a5af8d8a`.
2. Observe proof; require exact synthetic test success and proof persistence. Delete/seal workflow + trigger; checkpoint immediately. Never rerun.
3. Only after harness proof is sealed: freeze one real Stage3 one-shot workflow + sole trigger and checkpoint before arming.
4. Real one-shot order: verify immutables/tests -> build generated-only V5 candidate once -> invariant validate -> freeze -> renderer contract -> PDF fidelity1.0 -> pre-reference scorer gate -> then accepted manifest -> gold read/hash/validate -> score -> immutable recheck -> persist explicit Stage3 candidate/report -> seal workflow/trigger -> checkpoint.
5. Regardless of score, do not retune/replay or auto-promote; family #10 remains accepted unless a separate later promotion protocol is frozen and succeeds.
6. No Modal/L4/GPU/live audio; protected surfaces stay untouched.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V145 Stage1/Stage2/Stage3-adapter proofs are SUCCESS/sealed.
- Stage3 evaluation harness/prereg/tests/proof-workflow are frozen; synthetic definitive CPU proof is the immediate next action.
- Real Stage3 candidate build/evaluation has not run.
