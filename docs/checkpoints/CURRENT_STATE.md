# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm baseline preserved; Families #1–#14 fully consumed/sealed. V145 Stage 1, Stage 2, and the preregistered Stage 3 offline adapter are implemented, CPU-proven, and sealed. The real Stage 3 V5 candidate/calibration trial has NOT run yet. No Modal/L4/GPU/live audio without fresh explicit authorization.**

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
- Stage2 `modal/v145_rhythm_sequence_decoder.py`; frozen blob `5f86f57d0fd10774690d50528d51bad6e0392bf3`.
- Stage2 tests blob `b16b8d2060e1ea3b47225f1c7c6072cb260c0db8`.
- Proof run `33027229509`, job `98371326572`: SUCCESS.
- Proof `debug/v145-rhythm-decoder/proofs/cpu-stage2-proof.json`; blob `0522dd00598fcd5916349cb9747ca3588eaedb90`; persistence `e3ff86765cb4e072aef7b99f68435c1fb07400fc`; schema14502.
- Proof workflow deletion/sealing commit `68d1d95859e511f183bf857e5035b8b7635c8bc2`. Never rerun it.

## V145 Stage 3 offline source / fixed validation chain
- V5 stream path `debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json`.
- Git blob `fe61f7ad53a4d71348a5113ecc9e3876eaad98d4`; raw SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`.
- Source-only V5 renderer input: 1209 events /113 measures; tempo `129.19921875`; `4/4`; E Standard.
- Calibration reference path `debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json`; raw SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`. Reference contents are evaluation-only after freeze/PDF gate.
- Frozen validation/render identities: canonical `088d44827fb23e20d9aeeb4944a672989af5846c`; freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`; scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`; full-score helper `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`; PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`; render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.

## V145 Stage 3 — PREREGISTERED / ADAPTER CPU-PROVEN / SEALED / REAL TRIAL NOT RUN
- Preregistration `docs/v145-rhythm-decoder-stage3-offline-preregistration.md`.
- Prereg creation commit `64319400dcaa7d23850e8eda8985e823d24ff9a1`; frozen blob `bb60a3bcc5f6e136eb6efb5706828379e007ec1d`.
- Adapter `validation/v145_rhythm_decoder/offline_stage3_adapter.py`.
- Initial creation `65ce96f716b44d07c93affa5676d7508b59cb7ad`; source-schema tempo-key correction before proof `5388ebd4ff0b617ae54d40270c799f5a3150e500`.
- Frozen adapter blob **`434d4b2582991c216df411455f232b8d211337c6`**.
- Synthetic tests `modal/tests/test_v145_rhythm_stage3_offline_adapter.py`; frozen blob **`3eee7ae5253ad0eecbeb492eaa24216f0fa21fee`**.
- Adapter contract: exactly one Stage2 call; generated-only seconds from source grid; event count/eventIndex/list order/MIDI immutable; technique/bend/legato/link targets protected; decoded common-onset groups applied atomically; only `measure`,`step`,`stringIndex`,`fret` may change; 0.01-step conversion residual; collision/range groups preserve source; physical-position and coverage failures fail closed; exactly 113 generated measures; no add/delete/new pitch.
- Definitive CPU proof workflow creation/head commit **`d034b96bc97b76df2046ddd41423b48c03199d5a`**; workflow blob **`1e1b386824ba4bcdab7e51a4ed14f361e39e2457`**.
- CPU proof run **`33029862099`**, job **`98379640869`**, attempt1: **COMPLETED / SUCCESS**.
- Every proof step succeeded: exact identity/isolation checks, compile, constructor API anti-reference proof, Stage1 tests, Stage2 tests, Stage3 synthetic invariant tests, proof persistence.
- Proof `debug/v145-rhythm-decoder/proofs/cpu-stage3-offline-adapter-proof.json`; blob **`f55dcd1087f108d0d93c4a5a1a86cb5058ef4eb4`**; persistence commit **`03a0cfcc5eceae64cc37a02e84481c5a8a2ec1de`**; schema14503.
- Proof explicitly states realV5CandidateBuilt=false, calibrationScoreRun=false, candidateConstructorApiHasReferenceInput=false, runtimeReferenceInput=false, goldInputUsed=false, modalGpuUsed=false, liveAudioBenchmarkRun=false, acceptedBaselineChanged=false.
- Proof workflow deletion/sealing commit **`39d20843a6d4211e2aa629afa3fedbc45c36e82a`**. Never rerun it.
- No real Stage3 candidate, PDF-fidelity trial, or calibration score exists yet.

## EXPLICIT NEXT STEPS
1. Preserve frozen Stage1/Stage2/Stage3 adapter/test/prereg/proof identities exactly.
2. Implement/freeze the evaluation-only Stage3 score harness before the real one-shot; it must first validate the completed freeze/PDF gate, then and only then open/hash/validate the V144 calibration gold and score the frozen candidate.
3. Checkpoint the evaluation harness identity before arming the one-shot.
4. Arm exactly one CPU-only Stage3 real execution workflow with sole trigger; verify all frozen identities, re-run CPU tests, build the real generated-only V5 candidate once, validate invariants, freeze, renderer-contract proof, PDF event fidelity=1.0, scorer pre-reference gate, then calibration score.
5. Persist explicit Stage3 candidate/report artifacts, seal/delete workflow and trigger immediately, checkpoint.
6. Regardless of score: no retune/replay, `acceptedBaselineChanged=false`, `promotionAllowed=false`; family #10 remains accepted unless a separate later promotion protocol is frozen and succeeds.
7. No Modal/L4/GPU/live audio; do not touch main/Production/frontend/Bass/Lead/freezeReady=false.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V145 Stage1/Stage2/Stage3-adapter CPU proofs all SUCCESS and sealed.
- Next safe step is the evaluation-only harness; real Stage3 V5 candidate/score has not run.
