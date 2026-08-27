# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm baseline preserved; Families #1–#14 fully consumed/sealed. V145 Rhythm Decoder Stage 1 is preregistered, implemented, CPU-proven, and its proof workflow is sealed. Next safe work is a separate CPU-only Stage 2 for runtime timing-grid inference and global sequence decoding. No Modal/L4/GPU without fresh explicit authorization.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- No Modal/L4/GPU without fresh explicit authorization.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`; render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark, not unseen holdout. V5 holdout permanently consumed.

## Permanent progress-percentage reporting
- Accepted family #10: **Pitch Content 35.4%** (`0.35406698564593303`), **Pitch + timing 6.7%** (`0.06698564593301436`), **String/fret + timing 5.5%** (`0.05454545454545454`), **Chord/voicing 5.8%** (`0.0580511402902557`), **Measure coverage 100%**, **PDF event fidelity 100%**.
- Keep dimensions separate; recompute only if accepted baseline changes.

## Accepted baseline — LOCKED / UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- Manifest commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- 1144 events /113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity1.0.
- Full gold critical1712; pitch0.35406698564593303; pitch/timing0.06698564593301436; string/fret/timing0.05454545454545454; chord/voicing0.0580511402902557; coverage1.0.

## V144 consumed state
- Families #1–#14 are consumed. Never replay/reselect/retune them or use their candidate rankings/outcomes to shape a successor.
- Family #14 run `33025902769` / job `98367025091`; no qualifying FIT rule; accepted baseline unchanged.
- Family #14 one-shot workflow deletion `443031fd2294e05b23290c71b0e2b712198d842a`; trigger deletion `e9536f2b4c122741f50aa317e2bbd332d0a9d03b`.
- Family #14 report blob `a13df8e17ae2c813d4602dd10dd642327a5d2b75`; CPU proof JSONs preserved.
- Current accepted-baseline FIT residual remains `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`, blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.

## V145 Stage 1 — FROZEN / IMPLEMENTED / CPU-PROVEN
- Preregistration `docs/v145-rhythm-decoder-preregistration.md`; commit **`5a5c59d305dffba16090bc7dc37d33ecbb17e295`**.
- Frozen architecture: **V5 Rhythm-separated events -> normalized evidence -> timing/onset lattice -> pitch lattice -> constrained guitar-state decoder -> candidate event stream -> existing scorer/render/PDF gates**.
- Protected input: V5 Rhythm-separated output; V5 itself immutable. V5 is register-gated event separation, not waveform/stem separation; ranges bass28-51, rhythm52-63, lead64-76.
- Core `modal/v145_rhythm_decoder.py`; creation commit `17f08592ece48ee2519d3449f5f6f7d5ff8ffa39`; frozen blob **`2fd979aebb4685e86c7f24a0162f69de306c06e9`**.
- Tests `modal/tests/test_v145_rhythm_decoder.py`; creation commit `42cb52a86c4f364bdd042620ee13f65a8f43f971`; frozen blob **`9d48b02316f4eb364b163b3027c6c4d79304ac27`**.
- Implemented deterministic normalization; explicit-grid nearest+neighbor timing lattice; raw-onset preservation; generated-MIDI carry-through; valid standard-guitar positions; unique-string simultaneous states; fret-span guard; continuity-aware fingering; fail-closed undecoded onsets; input immutability; no Modal dependency.
- Definitive CPU proof workflow run **`33026865312`**, job **`98370167258`**: **COMPLETED / SUCCESS**.
- Exact identity verification, py_compile, all Stage 1 contract tests, and proof persistence succeeded.
- Proof `debug/v145-rhythm-decoder/proofs/cpu-core-proof.json`; blob **`978c2b7cd984f2cece23d2bc152f6acca28980e1`**; persistence commit **`5878764dbc747b17578eeeb9955204459adce503`**; schema14501.
- Proof states: cpuContractTestsPassed=true; runtimeReferenceInput=false; goldInputUsed=false; fitLabelsRead=false; validationLabelsRead=false; canaryLabelsRead=false; modalDependency=false; modalGpuUsed=false; liveAudioBenchmarkRun=false; acceptedBaselineChanged=false.
- Temporary CPU proof workflow creation commit `8aac002fd53ae65a245ffe932fc543909218b910`; workflow blob `bbe8dd88c50b16cd3151fca1ba02cbfdab3ed6ed`; deletion/sealing commit **`e802d7a867ee5f965be0c6abe51f70b6c0e6af6b`**. Never rerun that workflow.

## V145 next architectural hurdle — STAGE 2 NOT YET PREREGISTERED
- Stage 1 deliberately required caller-supplied timing quantum and chose each evidence event's nearest timing proposal independently.
- The next high-upside CPU-only hurdle is to infer timing-grid candidates from generated Rhythm evidence itself and select timing/fingering as a global sequence rather than independent nearest snaps.
- Stage 2 must remain runtime-reference-free and must be preregistered before implementation.
- Stage 2 should not invent new MIDI pitches yet; isolate timing/sequence gains first so pitch-generation changes remain separately attributable.
- Any later live audio/Modal/L4/GPU benchmark still requires fresh explicit user authorization.

## Fixed dependency identities
- Residual analyzer `27ac8699279db8fc0208d067479ad3751da1a630`; singleton reconstruction search `70880d26418d907cc702233af37bcc4b643e3a57`; singleton policy `1e05e66a3523f98944370837a59e5d6e7293f9ac`.
- Pitch-position shift `f69755b61bdcdf3a669847ce7e425289b4b0927f`; pitch shift `d9998c59acddba070069668d62bcb1c3cdaf2b05`; triple conjunction `ef9768a127472d7ce0746fdf21164d33e5117ea4`.
- Staged selector `d176a9a69366e192e6fa75bc1039661e977f0bfa`; measure guard `4a1364204dd1e720c09d835ec3995c165047de98`; context split `2da58508f2132660ad317ee63d5cb043d58285f0`; config `9b93205cb47bc7718685b9d41b263778107801ce`.
- Canonical `088d44827fb23e20d9aeeb4944a672989af5846c`; scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`; freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`; PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`; render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.

## EXPLICIT NEXT STEPS — CONTINUATION CONTRACT
1. Stay only on `v143-contextual-prune-lobo`; never main/Production/frontend/Bass/Lead.
2. Preserve family #10 accepted baseline and percentages **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
3. Preregister V145 Stage 2 before code: runtime-only timing-quantum inference + global sequence/beam decoding; no new MIDI pitches.
4. Implement Stage 2 CPU-only beside the frozen Stage 1 core; do not mutate Stage 1 blobs.
5. Add deterministic synthetic tests covering correct-grid recovery from jittered onsets, rejection of unsupported grids, one timing choice per source event, no duplicate event reuse, continuity-aware global choice, fail-closed behavior, and no label/reference inputs.
6. Run and seal a definitive CPU-only Stage 2 proof; checkpoint it.
7. No live Modal/L4/GPU/audio benchmark until separately and explicitly authorized.

## Current stop point
- V144 baseline unchanged and fully protected.
- V145 Stage 1 CPU proof SUCCESS and sealed.
- Immediate safe continuation: preregister V145 Stage 2 timing-grid inference + global sequence decoder, CPU-only.
