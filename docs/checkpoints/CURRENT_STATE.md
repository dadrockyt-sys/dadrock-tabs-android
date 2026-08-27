# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm baseline preserved; Families #1–#14 fully consumed/sealed. V145 Stage 1 and Stage 2 are both preregistered, implemented, CPU-proven, and their temporary proof workflows are sealed. Next safe work is an offline benchmark adapter using already-saved V5 Rhythm output if available; no Modal/L4/GPU without fresh explicit authorization.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- No Modal/L4/GPU without fresh explicit authorization.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark only.

## Permanent progress percentages — ACCEPTED BASELINE UNCHANGED
- Family #10: **Pitch Content 35.4%**, **Pitch + timing 6.7%**, **String/fret + timing 5.5%**, **Chord/voicing 5.8%**, **Measure coverage 100%**, **PDF event fidelity 100%**.
- Exact: pitch `0.35406698564593303`; pitch/timing `0.06698564593301436`; string/fret/timing `0.05454545454545454`; chord/voicing `0.0580511402902557`.
- 1144 events /113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`.

## V144 consumed state
- Families #1–#14 consumed; never replay/reselect/retune or use their observed candidate outcomes to shape successors.
- Family #14 run `33025902769` / job `98367025091`; no qualifying FIT rule; baseline unchanged.
- Family #14 workflow deletion `443031fd2294e05b23290c71b0e2b712198d842a`; trigger deletion `e9536f2b4c122741f50aa317e2bbd332d0a9d03b`.
- Family #14 report blob `a13df8e17ae2c813d4602dd10dd642327a5d2b75`; proofs preserved.
- Current accepted-baseline FIT residual remains blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.

## V145 Stage 1 — FROZEN / CPU-PROVEN / SEALED
- Preregistration commit `5a5c59d305dffba16090bc7dc37d33ecbb17e295`.
- Core `modal/v145_rhythm_decoder.py`; frozen blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
- Tests blob `9d48b02316f4eb364b163b3027c6c4d79304ac27`.
- CPU proof run `33026865312`, job `98370167258`: SUCCESS.
- Proof blob `978c2b7cd984f2cece23d2bc152f6acca28980e1`; persistence commit `5878764dbc747b17578eeeb9955204459adce503`; schema14501.
- Proof workflow deletion `e802d7a867ee5f965be0c6abe51f70b6c0e6af6b`.

## V145 Stage 2 — FROZEN / CPU-PROVEN / SEALED
- Preregistration `docs/v145-rhythm-decoder-stage2-preregistration.md`; commit `9fe0396fc1c320e3da5f5955d823df615a787603`.
- Stage2 module `modal/v145_rhythm_sequence_decoder.py`; frozen blob **`5f86f57d0fd10774690d50528d51bad6e0392bf3`**.
- Stage2 tests `modal/tests/test_v145_rhythm_sequence_decoder.py`; frozen blob **`b16b8d2060e1ea3b47225f1c7c6072cb260c0db8`**.
- Architecture: generated Rhythm evidence -> frozen Stage1 normalization -> runtime timing-grid inference -> simultaneity clusters -> common-onset guitar-state options -> global bounded sequence search.
- Grid inference: quantum0.050..0.500s; candidates from generated consecutive onset deltas + median /1..4; support>=0.80 within normalized residual<=0.18; median<=0.12; min4 events.
- Cluster window `0.30*quantum`; common selected onset required for all cluster members; exact MIDI only; unique strings; max fret24/max span7.
- Global beam width64; strict increasing separate attack onsets; Stage1 continuity transition cost.
- Definitive CPU proof workflow run **`33027229509`**, job **`98371326572`**: **COMPLETED / SUCCESS**.
- Exact Stage1/Stage2/test identity verification, py_compile, all Stage2 contract tests, and proof persistence succeeded.
- Proof `debug/v145-rhythm-decoder/proofs/cpu-stage2-proof.json`; blob **`0522dd00598fcd5916349cb9747ca3588eaedb90`**; persistence commit **`e3ff86765cb4e072aef7b99f68435c1fb07400fc`**; schema14502.
- Proof states: cpuContractTestsPassed=true; runtimeReferenceInput=false; goldInputUsed=false; fit/validation/canary labels not read; newPitchGeneration=false; modalDependency=false; modalGpuUsed=false; liveAudioBenchmarkRun=false; acceptedBaselineChanged=false.
- Stage2 proof workflow creation commit `3ada879b29c1de58d62077494138a830f6c4ee27`; workflow blob `a354bc4fdc8927995de9d48ea90f810c9e74435d`; deletion/sealing commit **`68d1d95859e511f183bf857e5035b8b7635c8bc2`**. Never rerun it.
- Stage1 frozen blob remained unchanged through Stage2.

## Next safe hurdle — OFFLINE V145 TRIAL, NOT YET PREREGISTERED
- Before asking for Modal/GPU authorization, first determine whether the repository already contains the saved V5 Rhythm result and the calibration scorer/gold artifacts needed to evaluate Stage2 offline.
- If available, preregister an offline adapter that reads the saved generated V5 result, constructs a complete V145 candidate without reference input, locks it, then opens gold only in the external scorer stage.
- Offline trial must not change the accepted family #10 baseline merely by running. It is benchmark evidence only until all existing scorer/render/PDF gates are satisfied and explicitly promoted.
- If the saved V5 event schema lacks sufficient timing fields for Stage2, document that limitation rather than invoking Modal automatically.
- No live Modal/L4/GPU/audio benchmark is authorized.

## EXPLICIT NEXT STEPS
1. Stay only on `v143-contextual-prune-lobo`; preserve family #10, Stage1, and Stage2 frozen blobs.
2. Locate/verify the saved V5 result blob `511fd244...`, gold/calibration artifacts, and current scorer interfaces using repository data only.
3. If offline evaluation is feasible, preregister a CPU-only offline V145 adapter before implementation.
4. Keep candidate construction runtime-reference-free; open gold only after candidate lock for scoring.
5. Checkpoint before and after any offline trial.
6. No Modal/L4/GPU/live audio until separately and explicitly authorized.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V145 Stage1 and Stage2 CPU proofs both SUCCESS/sealed.
- Safe next action: investigate offline scoring feasibility from existing saved artifacts only.
