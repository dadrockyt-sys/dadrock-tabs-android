# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm baseline preserved. V145 Stage 1, Stage 2, Stage 3 generated-only adapter, and Stage 3 evaluation harness are CPU-proven/sealed. The first real V145 Stage3 calibration one-shot is consumed/sealed with no candidate or score. V146 artifact-first calibration is now preregistered before any V146 artifact construction; Phase A is generated-only and calibration-free. No Modal/L4/GPU/live audio without fresh explicit authorization.**

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
### Stage 1
- `modal/v145_rhythm_decoder.py` blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`; tests `9d48b02316f4eb364b163b3027c6c4d79304ac27`.
- Proof run `33026865312`, job `98370167258`: SUCCESS; proof blob `978c2b7cd984f2cece23d2bc152f6acca28980e1`.

### Stage 2
- `modal/v145_rhythm_sequence_decoder.py` blob `5f86f57d0fd10774690d50528d51bad6e0392bf3`; tests `b16b8d2060e1ea3b47225f1c7c6072cb260c0db8`.
- Proof run `33027229509`, job `98371326572`: SUCCESS; proof blob `0522dd00598fcd5916349cb9747ca3588eaedb90`.

### Stage 3 generated-only adapter
- Prereg blob `bb60a3bcc5f6e136eb6efb5706828379e007ec1d`.
- V5 stream Git blob `fe61f7ad53a4d71348a5113ecc9e3876eaad98d4`; raw SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; 1209 events /113 measures /tempo `129.19921875` /4/4 /E Standard.
- Adapter blob `434d4b2582991c216df411455f232b8d211337c6`; tests `3eee7ae5253ad0eecbeb492eaa24216f0fa21fee`.
- Proof run `33029862099`, job `98379640869`: SUCCESS; proof blob `f55dcd1087f108d0d93c4a5a1a86cb5058ef4eb4`.

### Stage 3 evaluation harness
- Prereg blob `9b3542f33fb0f9149056b1eafb8c5db1864299ca`.
- Evaluator blob `d208abb3f180f8375d57d786941ff49d6813de1c`; tests `d8b3770ac7f3ba18123122f19fad895257998c25`.
- Frozen order: candidate-only validation -> pre-reference freeze/PDF gate -> candidate/freeze/PDF identity -> accepted manifest -> only then gold bytes/hash/validate -> exactly one score.
- Proof run `33031101564`, job `98383566164`: SUCCESS; proof blob `81c10bdcc39ce9e371fda60d2c3d107e671b8790`; persistence commit `c392dc6e6aeb5f2831cc074bfca9abb3b8f31db7`.

## Frozen Stage 3 validation/render chain
- canonical `088d44827fb23e20d9aeeb4944a672989af5846c`
- freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`
- scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`
- full-score helper `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`
- PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`
- render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`

## First real V145 Stage3 calibration one-shot — CONSUMED / FAILED CLOSED / SEALED
- Real-trial prereg blob `b49c530ecfb32bdc6dc00f2be957f9754a6960d6`.
- Trigger commit `b0031639ea51c00bb0702c676b4bdcdfb428e04c`.
- Run `33031523386`, job `98384901171`: FAILURE at first substantive workflow-identity gate.
- Trigger expected workflow blob `81f16ce5c4a7ba6801cd0ceefd8858263ea21fd2`; trigger-time tree blob was `e68fce559a86b567d5d3b70ce6aaf263b477487f`.
- All candidate/calibration steps skipped. No candidate, freeze, gold read, score, or result existed.
- Failure checkpoint `41bfadd651f4228128647ba5d58b4c09a134dadd`; workflow deletion `0d83c411fcff78b7f7083d2a968f85bd9522870d`; trigger deletion `b3e407413b76138722699690c8f15ca67283ab72`.
- Never rerun/rearm/recreate this same V145 real one-shot.

## V146 artifact-first calibration — PREREGISTERED / PHASE A NOT YET RUN
- Prereg `docs/v146-rhythm-artifact-first-calibration-preregistration.md`.
- Creation commit `86729595bab64ac80b82180532ee4dc94fca9817`.
- Frozen prereg blob **`0125201e86389b21dee3ceb2e7ecd25dc67dfe84`**.
- V146 is materially distinct in execution protocol: generated-only construction is separated from any later calibration evaluation. No musical/model parameter changed from V145.
- Phase A reuses frozen Stage1/Stage2/adapter only and is explicitly calibration-free.
- Phase A must invoke the frozen adapter exactly once against the immutable V5 stream and persist:
  - `debug/v146-rhythm-artifact/generated-only-candidate.json`
  - `debug/v146-rhythm-artifact/generated-only-candidate-proof.json`
- Candidate contract: exactly1209 events, eventIndex0..1208, identical MIDI sequence to V5 source, exactly measures1..113, candidate metadata SHA equals canonical SHA, generated-only safety flags all correct.
- Proof schema14601; records candidate SHA/count, changed-event/field counts and frozen adapter statistics. It must state referenceFree=true, acceptedManifestRead=false, realGoldRead=false, calibrationScoreRun=false, candidateSearchRun=false, alternateCandidateConstructed=false, acceptedBaselineChanged=false, promotionAllowed=false, modalGpuUsed=false, liveAudioBenchmarkRun=false.
- Phase A may not read/hash/inspect accepted family #10 manifest or calibration gold, and may not import/invoke scoring code.
- Phase B is **NOT authorized yet**. It may only be separately preregistered after the Phase A candidate/proof are persisted and sealed.

## EXPLICIT NEXT STEPS
1. Create a one-purpose V146 Phase A CPU workflow whose creation triggers the single generated-only artifact construction. It must not contain calibration paths or scoring invocations.
2. Require exact frozen dependency verification, frozen CPU tests, exactly one adapter invocation, independent artifact invariants, and persistence of only the candidate + construction proof.
3. On success, delete/seal the Phase A workflow and checkpoint candidate/proof exact identities immediately.
4. Only then may a separate Phase B calibration-evaluation protocol be designed/preregistered; do not score or open gold during Phase A.
5. Accepted family #10 remains **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V145 components are CPU-proven/sealed; consumed V145 real execution remains sealed with no score.
- V146 artifact-first protocol is frozen before construction; Phase A workflow/artifact do not yet exist.
