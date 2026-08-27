# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm baseline preserved; Families #1–#14 fully consumed/sealed. V145 Stage 1 and Stage 2 are preregistered, implemented, CPU-proven, and sealed. V145 Stage 3 offline trial is now preregistered before implementation/scoring; adapter, proof, and one-shot score are still pending. No Modal/L4/GPU without fresh explicit authorization.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- No Modal/L4/GPU/live audio without fresh explicit authorization.
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
- Saved V5 render stream: `debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json`.
- Git blob **`fe61f7ad53a4d71348a5113ecc9e3876eaad98d4`**; raw SHA256 **`7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`**.
- Exact source-only V5 renderer input: 1209 events /113 measures; tempo `129.19921875`; `4/4`; standard tuning.
- Absolute generated-only seconds can be reconstructed from `(measure, step, tempo)` without audio, gold, or labels.
- Frozen validation/render identities remain canonical `088d44827fb23e20d9aeeb4944a672989af5846c`, freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`, scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`, PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`, render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.
- Calibration reference path identified without opening contents: `debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json`; raw SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Generic holdout scorer CLI intentionally requires references under `validation/rhythm_holdout/reference`; Stage3 therefore preregisters an evaluation-only harness using frozen scorer primitives/full scoring function after freeze/PDF proof, rather than moving/copying gold.

## V145 Stage 3 — PREREGISTERED / NOT IMPLEMENTED / NOT SCORED
- Preregistration: `docs/v145-rhythm-decoder-stage3-offline-preregistration.md`.
- Preregistration creation commit **`64319400dcaa7d23850e8eda8985e823d24ff9a1`**.
- Preregistration blob **`bb60a3bcc5f6e136eb6efb5706828379e007ec1d`**.
- Frozen implementation path: `validation/v145_rhythm_decoder/offline_stage3_adapter.py`.
- Frozen tests path: `modal/tests/test_v145_rhythm_stage3_offline_adapter.py`.
- Exactly one decoder call on reconstructed generated-only V5 evidence; no candidate search/ranking/alternate.
- Event count fixed at 1209; eventIndex/list order/MIDI immutable; only unprotected atomic decoded groups may change `measure`, `step`, `stringIndex`, `fret`.
- Technique/bend/legato events and referenced link targets are protected; any selected group containing a protected event is copied source-exact.
- Selected seconds map back to source 16th grid with frozen half-up conversion and residual <=0.01 source steps; out-of-range/residual/collision groups preserve source unchanged.
- Physical pitch/string/fret inconsistency or new cell multiplicity/measure-set failure is fail-closed before scoring.
- Final generated measure set must equal source and contain all 113 measures; no additions/deletions/new pitches.
- Mandatory CPU proof before real candidate/score; proof cannot build/score the real V5 Stage3 candidate.
- One-shot real execution order is fixed: verify -> CPU tests -> build generated-only candidate -> invariant check -> freeze -> renderer contract -> PDF event fidelity1.0 -> scorer pre-reference validation -> only then open/hash/validate calibration gold -> score -> immutable recheck -> persist explicit Stage3 artifacts -> seal workflow/trigger.
- Score is calibration benchmark only, never unseen holdout; no score-driven retuning/replay; report must keep `acceptedBaselineChanged=false` and `promotionAllowed=false` regardless of result.

## EXPLICIT NEXT STEPS
1. Implement the preregistered CPU-only Stage3 adapter exactly; do not change Stage1/Stage2.
2. Add synthetic invariant tests at the frozen test path.
3. Create/run one definitive self-reporting CPU proof, persist proof, delete/seal proof workflow immediately, checkpoint.
4. Only after successful sealed proof, arm one one-shot offline Stage3 execution using the exact preregistered order.
5. Checkpoint immediately before and after the offline trial and after sealing.
6. No Modal/L4/GPU/live audio; do not touch main/Production/frontend/Bass/Lead/freezeReady=false.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V145 Stage1 and Stage2 CPU proofs SUCCESS/sealed.
- V145 Stage3 protocol is frozen before code/score; adapter/proof/trial still pending.
