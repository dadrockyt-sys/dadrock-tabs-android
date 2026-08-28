# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V163 is terminal/consumed and failed its sole preregistered professional-reference score gate. Never rerun/rearm/repair/retune/regenerate/re-QC/rescore V163 and do not advance it downstream. V164 is preregistered, its exact local-evidence numeric contract is sealed, implementation/static-guard code is present, and the V164 CPU-only static preflight has now PASSED. No V164 song processing, pitch inference, candidate generation, professional-reference/scorer read, V163 artifact read, or GPU execution has occurred. Next boundary is to build and separately seal the V164 pre-run identity receipt and CPU environment receipt before any song processing.**

## Standing safety
- CPU-only reference-free static work authorized at assistant discretion.
- Fresh explicit authorization required immediately before Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159/V160/V161/V162/V163 generation versions closed forever; V163 score opportunity closed forever.
- No professional-reference event/measure mining, candidate repair, score-informed retune, threshold sweep, variant selection, human correction, or second V163 score.
- V163 aggregate score was observed before V164 preregistration. V164 does **not** claim reviewer score-blindness; V164 design/numerics remain quarantined from V163 score/reference evidence.

## V163 terminal anchors
- Generation run `33213512389`, attempt `1`, job `98991933938`; terminal generation commit `3b6f98750291a2f7b229c5e50cbf802752cf84d4`; `STRUCTURAL_QC_PASS`.
- Candidate blob `f4eafb1488f139198cb7860a76f294c0e1775df8`; SHA256 `cc55d596a05bd8e9c0a149f6ba8263375c26fbb7334139a75697b58ca23c8c19`; Guitar `1041`, Bass `404`.
- Sole score run `33214223643`, attempt `1`, job `98994146394`; terminal score commit `7bd8c813cac506811e3c144e5efe9edcd3abc561`.
- Score terminal blob `b7e6634d67b89632389f2be3edfdbe0162ff98dd`; `SCORE_GATE_FAIL`; Guitar F1 `0.059983566146261304`, Bass F1 `0.21661409043112514`, gates `0.80/0.80`.
- Score report blob `d10ae33aba35afd2547f94a3ec3dcd8443972fcf`; SHA256 `b87e745d1b3dafea2e99b841e8af028c55f8749341e5736fa5ec488ebf66cfd9`.

## V164 frozen design anchors
- Prereg `debug/v164-cpu-autonomous/preregistration.json`: commit `1f0b4a904227491cbd5c62039d1ecbd500453966`, blob `05d255d75a6c1947891fba38d96d9399e3f75f9c`.
- Numeric contract `debug/v164-cpu-autonomous/implementation-contract.json`: commit `174a1c3850b4eb30335c9afd0e0ada776de37a3b`, blob `098f24282b59abba0f7cffa0793b344b76701724`.
- Frozen V162 pins: numeric contract `409da313ed03a6c232d6578d48b0da6aa35b000b`; event logic `9f9b33fd8c210ad581025b454cf69b6999aa544b`; timebase builder `f7e9483aea16af770bcffe01ad8cfaf689d693b9`; timebase QC `78acc9fd626039801011d039cca12686b72369c0`; transcriber `fa163cafe2131aa73cdbb50df10d4e4912cff53b`; structural QC `b7d3fa92fc9f3bed00931d19097e08cd91eab62b`; event fixture `e301f38db66f44193d799a9c1a02c99169823d45`; JSON fixture `654557363745f580f425252395542e9fb91adaad`; negative guard `8d40bc7f3dce9c9717e41fa1060c553434ad9959`.
- Event-local onset evidence: inclusive/clipped half-window `32` frames, finite positives only, q95 support, no-positive support `0.0` / threshold `null`.
- Beat-local subdivision q55 and event-step q95 support populations only. All unrelated V162 pitch/segmentation/register/admission/cap numerics remain frozen.
- Invariance factors: remote `1,000,000×`; local `0.1×` and `10×`; rel/abs tolerance `1e-12`.

## V164 implementation identities
- `validation/v164_cpu_autonomous/event_logic_v164.py` blob `62303877a1971f75cacda002c5ad921680161674`.
- `validation/v164_cpu_autonomous/test_event_logic_v164.py` blob `13d29ef19a297d19469196cb2a23a4c0d6e040de`.
- `validation/v164_cpu_autonomous/build_timebase_v164.py` blob `170a7a15d68e271d93775c2aaba058fe3ebaa8bb`.
- `validation/v164_cpu_autonomous/timebase_qc_v164.py` blob `e59498e76d881f22ea405c81781ca2004ea8f53e`.
- `validation/v164_cpu_autonomous/transcribe_v164.py` current blob `df1302216df404bc3368ff820f005d6b63ae100d`.
- `validation/v164_cpu_autonomous/structural_qc_v164.py` blob `c1a81c7a97e646398f5e50cbc63dae341cdc500b`.
- `validation/v164_cpu_autonomous/test_json_native_v164.py` blob `a0b525485bbea933004045622bbf8c63527f123b`.
- `debug/v164-cpu-autonomous/negative-runtime-guard.py` blob `230aa1efeb4640aabbb05720ead031e13cc57337`.

## Static-preflight trigger adaptation
- Original workflow file `.github/workflows/v164-static-preflight.yml` was sealed as blob `b8d1d2d7236488974f4dc5431ce42cc380257a98` with manual `workflow_dispatch` only.
- GitHub does not expose a feature-branch-only `workflow_dispatch` in the mobile/default-branch Actions UI. After the user explicitly authorized whatever safe change was needed to make this cellphone-friendly, only the workflow trigger plumbing was changed; no V164 implementation/guard/numeric file was changed.
- Trigger commit: `9e25138d337608dc3676689a228cbe1b5f9979ac`.
- Current workflow blob: `38dfe27889a1644576093c429ef66fd57087fe94`.
- Current triggers retain `workflow_dispatch` and add `push` restricted to branch `v143-contextual-prune-lobo`.
- Job guard remains `github.ref == 'refs/heads/v143-contextual-prune-lobo'`; permissions remain `contents: read`; CPU/static commands remain unchanged.
- PR #22 exists only as a visibility/check surface and targets `main`; it has **not** been merged and `main` remains untouched.

## V164 CPU Static Preflight — PASS
- Workflow run ID `33221653962`, run number `1`, attempt `1`.
- Job ID `99016763456`, name `static-preflight`.
- Head SHA `9e25138d337608dc3676689a228cbe1b5f9979ac`.
- Event `push` on branch `v143-contextual-prune-lobo`.
- Runner Ubuntu `24.04.4`, Python `3.11.16`; installed only pinned static dependency `numpy==2.0.2`.
- Syntax compile: PASS.
- Song-blind local-evidence invariance fixture: `dadrock.tabs.v164.local-evidence-static-test.v2`, `validation=PASS`; remote/local-scale invariance, boundary clipping, nonfinite rejection, zero fallback and frozen V162 regressions all true. Safety: songAudioRead=false, professionalReferenceRead=false, V163CandidateRead=false, V163ScoreRead=false, gpuUsed=false.
- JSON-native local-provenance fixture: `dadrock.tabs.v164.json-native-local-provenance-static-test.v1`, `validation=PASS`; normalization metadata native, bounds preserved, exact round-trip, finite normalized support, NumPy types removed, nonfinite rejected. Safety: songAudioRead=false, demucsInvoked=false, pitchInferenceInvoked=false, professionalReferenceRead=false, frozenScorerRead=false, V163CandidateRead=false, V163ScoreRead=false, gpuUsed=false.
- Negative runtime guard: `dadrock.tabs.v164.negative-runtime-guard.v1`, `validation=PASS`, `failures=[]`.
- Negative guard checks all true: frozen V162 dependencies exact; pure local event logic; song-blind invariance fixtures; timebase-before-pitch boundary; transcriber QC-before-pitch/local adaptation; structural-QC local-evidence recomputation; JSON-native local-provenance boundary; no reference/scorer/V163 artifact paths; static workflow CPU-only.
- No song/runtime executable was invoked by the preflight.

## Current V164 execution counters
- Static-preflight runs: `1` PASS.
- Song audio reads: `0`.
- Demucs/pitch inference: `0`.
- V164 candidate generations: `0`.
- Professional-reference/scorer reads for V164: `0`.
- V163 candidate/score reads for V164: `0`.
- GPU/CUDA/Modal: `0`.
- `main`/Production modifications: `0`.

## Hard boundary — NEXT
1. Never reopen V163 for tuning/scoring.
2. Static preflight is satisfied by run `33221653962`; do not rerun unless a static implementation/guard/workflow change invalidates it.
3. Build and separately seal V164 pre-run identity receipt and CPU environment receipt, pinned to the exact static-PASS head/code identities, before any song processing.
4. No V164 song processing until those receipts are sealed and validated.
5. Timebase generation must occur before pitch, followed by independent V164 timebase QC PASS before transcriber pitch inference.
6. Professional reference/scorer and all V163 candidate/score artifacts remain forbidden for V164 generation.
7. No GPU/Modal/CUDA without fresh explicit authorization.
