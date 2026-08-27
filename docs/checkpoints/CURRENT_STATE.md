# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm baseline preserved; Families #1–#14 fully consumed/sealed. V145 Stage 1 and Stage 2 are preregistered, implemented, CPU-proven, and sealed. Offline Stage 3 feasibility is now established from the already-saved V5 Rhythm render stream; Stage 3 adapter/scoring protocol is not yet preregistered or run. No Modal/L4/GPU without fresh explicit authorization.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- No Modal/L4/GPU without fresh explicit authorization.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; V5 holdout-result metadata blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
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
- Proof `debug/v145-rhythm-decoder/proofs/cpu-stage2-proof.json`; blob **`0522dd00598fcd5916349cb9747ca3588eaedb90`**; persistence commit **`e3ff86765cb4e072aef7b99f68435c1fb07400fc`**; schema14502.
- Proof states: cpuContractTestsPassed=true; runtimeReferenceInput=false; goldInputUsed=false; fit/validation/canary labels not read; newPitchGeneration=false; modalDependency=false; modalGpuUsed=false; liveAudioBenchmarkRun=false; acceptedBaselineChanged=false.
- Stage2 proof workflow creation commit `3ada879b29c1de58d62077494138a830f6c4ee27`; workflow blob `a354bc4fdc8927995de9d48ea90f810c9e74435d`; deletion/sealing commit **`68d1d95859e511f183bf857e5035b8b7635c8bc2`**. Never rerun it.
- Stage1 frozen blob remained unchanged through Stage2.

## V145 Stage 3 offline feasibility — ESTABLISHED / SCORE-FREE
- Saved V5 render stream located at `debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json`.
- Git blob **`fe61f7ad53a4d71348a5113ecc9e3876eaad98d4`**; pre-existing raw stream SHA256 **`7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`**.
- Stream is the exact source-only frozen V5 renderer input previously validated at 1209 events /113 measures; tempo `129.19921875`, time signature `4/4`, standard tuning.
- Each event has `measure`, 16-step `step`, `midi`, `durationSteps`; many also carry `durationSeconds`. Therefore absolute generated-only seconds can be reconstructed deterministically as `((measure-1)*16 + step) * (60/tempo/4)` without audio, gold, or labels.
- Stage1/Stage2 can consume reconstructed `{midi,onset,duration}` evidence. Stage1 guitar string numbers are human 1..6, so renderer `stringIndex` mapping is frozen as `decoded.string - 1`.
- Frozen validation/render identities reverified on branch:
  - canonical `validation/rhythm_holdout/canonical.py` blob `088d44827fb23e20d9aeeb4944a672989af5846c`;
  - freeze `validation/rhythm_holdout/freeze_rhythm_analysis.py` blob `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`;
  - scorer `validation/rhythm_holdout/score_rhythm_holdout.py` blob `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`;
  - PDF fidelity `validation/rhythm_holdout/verify_pdf_event_fidelity.py` blob `5e1564216873046237fb545078a04a6b18f72b27`;
  - render contract `lib/v143RenderContract.js` blob `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.
- Investigation opened no gold/reference data and produced no V145 score/candidate.

## EXPLICIT NEXT STEPS
1. Stay only on `v143-contextual-prune-lobo`; preserve family #10, Stage1, and Stage2 frozen blobs.
2. Preregister the CPU-only V145 Stage 3 offline adapter/scoring protocol **before implementation or scoring**.
3. Adapter must use only the pinned saved V5 generated stream for candidate construction; no reference/gold/FIT/validation/canary input may enter Stage1/Stage2.
4. Freeze the complete V145 candidate and prove render/PDF event identity before any calibration reference is opened by the external scorer.
5. Treat any Stage 3 result as benchmark evidence only; accepted family #10 baseline changes only through explicit later promotion.
6. Checkpoint before and after the offline trial.
7. No Modal/L4/GPU/live audio until separately and explicitly authorized.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V145 Stage1 and Stage2 CPU proofs both SUCCESS/sealed.
- Offline V5 input feasibility is confirmed, but Stage3 is not yet preregistered, implemented, or scored.
