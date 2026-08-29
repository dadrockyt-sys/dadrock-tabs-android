# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V163 and V164 are terminal/consumed and permanently closed. V164’s sole CPU run reached fresh separation and independent timebase-QC PASS before pitch, then failed before pitch while constructing the frozen-source transcriber adapter (`event_logic_v162.py`: expected 2 occurrences, found 3). V164 produced no candidate, generation receipt, or structural-QC receipt; it self-froze and deleted its generation workflow. V165 is now preregistered and its pre-code implementation contract is sealed. No V165 implementation code or song processing has been created/executed yet. V165 is strictly an implementation-only adapter repair; every V164 musical/numeric setting remains frozen unchanged.**

## Standing safety
- CPU-only reference-free work authorized at assistant discretion.
- Fresh explicit authorization required immediately before Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159/V160/V161/V162/V163/V164 generation versions are closed forever.
- Never rerun/rearm/repair/retune/regenerate/re-QC/rescore a closed version.
- No professional-reference event/measure mining, candidate repair, score-informed retune, threshold sweep, variant selection, or human correction.
- V163 score/reference evidence may not shape V164/V165 design or numerics.

## V163 terminal anchors
- Generation run `33213512389`, attempt `1`, job `98991933938`; terminal commit `3b6f98750291a2f7b229c5e50cbf802752cf84d4`; structural QC PASS.
- Candidate blob `f4eafb1488f139198cb7860a76f294c0e1775df8`; SHA256 `cc55d596a05bd8e9c0a149f6ba8263375c26fbb7334139a75697b58ca23c8c19`; Guitar `1041`, Bass `404`.
- Sole score run `33214223643`, attempt `1`, job `98994146394`; terminal score commit `7bd8c813cac506811e3c144e5efe9edcd3abc561`; `SCORE_GATE_FAIL`.

## V164 frozen design/code
- Prereg blob `05d255d75a6c1947891fba38d96d9399e3f75f9c`.
- Numeric-contract blob `098f24282b59abba0f7cffa0793b344b76701724`.
- Event logic `62303877a1971f75cacda002c5ad921680161674`; event fixture `13d29ef19a297d19469196cb2a23a4c0d6e040de`.
- Timebase builder `170a7a15d68e271d93775c2aaba058fe3ebaa8bb`; timebase QC `e59498e76d881f22ea405c81781ca2004ea8f53e`.
- Transcriber `df1302216df404bc3368ff820f005d6b63ae100d`; structural QC `c1a81c7a97e646398f5e50cbc63dae341cdc500b`.
- JSON fixture `a0b525485bbea933004045622bbf8c63527f123b`; negative guard `230aa1efeb4640aabbb05720ead031e13cc57337`.
- Frozen V162 pins: contract `409da313ed03a6c232d6578d48b0da6aa35b000b`; event logic `9f9b33fd8c210ad581025b454cf69b6999aa544b`; timebase builder `f7e9483aea16af770bcffe01ad8cfaf689d693b9`; timebase QC `78acc9fd626039801011d039cca12686b72369c0`; transcriber `fa163cafe2131aa73cdbb50df10d4e4912cff53b`; structural QC `b7d3fa92fc9f3bed00931d19097e08cd91eab62b`; event fixture `e301f38db66f44193d799a9c1a02c99169823d45`; JSON fixture `654557363745f580f425252395542e9fb91adaad`; negative guard `8d40bc7f3dce9c9717e41fa1060c553434ad9959`.

## V164 pre-song seals
- Static PASS run `33221759016`, attempt `1`, job `99017084779`, head `720f26aa7f23fcdc127aa8cbe34e05e7ca63f215`; workflow blob `e6beec5526ed5e4925475eaab86f5ca78909a349`.
- Pre-run receipt blob `fa1942690b45bce35515abee35016f953fcccd45`, PASS.
- Environment run `33221962951`, run `1`, attempt `1`, job `99017692441`, PASS; environment receipt blob `25a7f5e2c692a6ac518ae1243ea812cf650f7278`.
- Verified CPU stack: Python `3.10.21`; torch `2.8.0+cpu`; CUDA unavailable/null; numpy `1.26.4`; scipy `1.13.1`; soundfile `0.12.1`; basic-pitch `0.4.0`; demucs `4.1.0`; imageio-ffmpeg `0.6.0`; librosa `0.11.0`.

## V164 sole generation — TERMINAL / CONSUMED
- Arm commit `984a542a846ff711600ef86c3114f48d4d0b5f89`.
- Run `33222155380`, run number `1`, attempt `1`, job `99018290109`.
- CPU only. Fresh source verified SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; normalization and Demucs separation executed once.
- Fresh timebase built: detected beats `448`, selected phase `1`, subdivisions `1805`.
- Independent timebase QC PASS before pitch; timebase SHA256 `1ce4e9e2214ec87a4ed378007b5d2dfa62a890dc5bd6a84244df6ead41e628d8`, blob `3ac889cd913bf6528741cb4df4f7b343014466f1`; QC blob `3ec4199f20ae7dc016395f41dcd527dbc20f3216`.
- QC safety: pitchInferenceInvoked=false, referenceRead=false, V163CandidateRead=false, V163ScoreRead=false, gpuUsed=false.
- Transcriber failed before adapted-module execution/pitch: `RuntimeError: V164 frozen-source transform drift for event-logic provenance path: expected 2, found 3`.
- No candidate, generation receipt, or structural-QC receipt exists.
- Terminal commit `5b63614b77a74777c50669d73c5c6607991df0a0`; terminal-freeze blob `e2203663df78d2dce5d17e65bd94f4a2bb685e27`; outcome `TRANSCRIBER_FAIL`; lastCompletedStage `TIMEBASE_QC_PASS`; candidateAuthoritative=false; `neverRearmV164=true`.
- Generation workflow blob `1e545e8ea54a5884007abbdcf08818e51e00073a` self-deleted and is absent at terminal head.
- Professional-reference/scorer/V163 candidate/score reads: `0`; GPU/CUDA/Modal: `0`; main/Production changes: `0`.

## V165 pre-code seals — COMPLETE
- V165 preregistration file `debug/v165-cpu-autonomous/preregistration.json`.
- Prereg commit `7f64743d34da39fb1abc3f542fd6fcec82e5f139`; blob `1ca5c7b91263c99c0150db085d12f4c0853940b7`.
- Schema `dadrock.tabs.v165.adapter-repair-preregistration.v1`; status `PREREGISTERED_BEFORE_NUMERIC_CONTRACT_OR_IMPLEMENTATION_CODE`; validation PASS.
- V165 implementation contract file `debug/v165-cpu-autonomous/implementation-contract.json`.
- Contract commit `07a2470a5a6b525ad175bdffc0a90c0c559eee6d`; blob `727782651e14699a0205ea97abc6e82b387299dc`.
- Schema `dadrock.tabs.v165.adapter-repair-implementation-contract.v1`; status `SEALED_BEFORE_IMPLEMENTATION_CODE`; validation PASS.
- Contract freezes every V164 musical/numeric setting. Allowed functional repair: count-checked provenance-path transform must replace exactly `3` occurrences of `event_logic_v162.py` with `event_logic_v165.py`; old occurrences must become `0`, new occurrences `3`; no unbounded replace.
- Mandatory new static boundary: song-blind test must actually call V165 `build_adapted_module()` without calling adapted `main`, loading song audio, Demucs, pitch, reference/scorer, V163 artifacts, or V164 runtime artifacts.
- At both V165 seals: no V165 implementation code, song processing, runtime artifacts, candidate, or generation workflow existed.

## Current counters
- V164 sole generation: `1` consumed; pitch inference `0`; candidate `0`; structural QC `0`.
- V165 song audio reads: `0`; normalization `0`; separation `0`; timebase `0`; pitch `0`; candidate `0`.
- V165 professional-reference/scorer reads: `0`; V163/V164 runtime-artifact reads for V165 tuning: `0`.
- GPU/CUDA/Modal: `0`; main/Production modifications: `0`.

## Hard boundary — NEXT
1. Never reopen V163 or V164.
2. Implement only version-isolated V165 adapter repair and static fixtures under sealed contract blob `727782651e14699a0205ea97abc6e82b387299dc`.
3. No V165 musical/numeric changes. Do not use V164 timebase/audio values for tuning.
4. Static preflight must compile all V165 modules, execute the new song-blind adapter-construction test, V164-equivalent invariance/JSON fixtures, and negative guard before any V165 song processing.
5. After static PASS, separately seal V165 pre-run identity and CPU environment before one-shot generation.
6. V165 generation maximum `1`; no rerun/repair after generation.
7. No GPU/Modal/CUDA without fresh explicit authorization. PR #22 remains unmerged; never modify `main` without explicit user direction.
