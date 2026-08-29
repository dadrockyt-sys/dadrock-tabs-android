# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V163 and V164 are terminal/consumed and permanently closed. V164’s sole CPU generation run reached fresh separation, built a fresh V164 timebase, and obtained independent timebase-QC PASS before any pitch inference. The V164 transcriber then failed immediately while constructing its frozen-source adapter because an exact-count transform expected 2 occurrences of `event_logic_v162.py` but the frozen source contains 3. No V164 candidate, generation receipt, or structural-QC receipt exists. V164 self-froze and deleted its generation workflow. Never rerun/rearm/repair V164. Next safe path is a fresh V165 implementation-only repair preregistered before code changes, with all V164 musical/numeric settings frozen and no professional-reference/scorer evidence used.**

## Standing safety
- CPU-only reference-free work authorized at assistant discretion.
- Fresh explicit authorization required immediately before Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159/V160/V161/V162/V163/V164 generation versions are closed forever.
- Never rerun/rearm/repair/retune/regenerate/re-QC/rescore a closed version.
- No professional-reference event/measure mining, candidate repair, score-informed retune, threshold sweep, variant selection, or human correction.
- V163 aggregate score was observed before V164 preregistration. V164/V165 design and numerics remain quarantined from V163 score/reference evidence.

## V163 terminal anchors
- Generation run `33213512389`, attempt `1`, job `98991933938`; terminal commit `3b6f98750291a2f7b229c5e50cbf802752cf84d4`; structural QC PASS.
- Candidate blob `f4eafb1488f139198cb7860a76f294c0e1775df8`; SHA256 `cc55d596a05bd8e9c0a149f6ba8263375c26fbb7334139a75697b58ca23c8c19`; Guitar `1041`, Bass `404`.
- Sole score run `33214223643`, attempt `1`, job `98994146394`; terminal score commit `7bd8c813cac506811e3c144e5efe9edcd3abc561`.
- Score terminal blob `b7e6634d67b89632389f2be3edfdbe0162ff98dd`; `SCORE_GATE_FAIL`; Guitar F1 `0.059983566146261304`, Bass F1 `0.21661409043112514`, gates `0.80/0.80`.

## V164 frozen design/code anchors
- Prereg blob `05d255d75a6c1947891fba38d96d9399e3f75f9c`.
- Numeric-contract blob `098f24282b59abba0f7cffa0793b344b76701724`.
- Event logic `62303877a1971f75cacda002c5ad921680161674`.
- Event fixture `13d29ef19a297d19469196cb2a23a4c0d6e040de`.
- Timebase builder `170a7a15d68e271d93775c2aaba058fe3ebaa8bb`.
- Timebase QC `e59498e76d881f22ea405c81781ca2004ea8f53e`.
- Transcriber `df1302216df404bc3368ff820f005d6b63ae100d`.
- Structural QC `c1a81c7a97e646398f5e50cbc63dae341cdc500b`.
- JSON-native fixture `a0b525485bbea933004045622bbf8c63527f123b`.
- Negative runtime guard `230aa1efeb4640aabbb05720ead031e13cc57337`.
- Frozen V162 pins remain: contract `409da313ed03a6c232d6578d48b0da6aa35b000b`; event logic `9f9b33fd8c210ad581025b454cf69b6999aa544b`; timebase builder `f7e9483aea16af770bcffe01ad8cfaf689d693b9`; timebase QC `78acc9fd626039801011d039cca12686b72369c0`; transcriber `fa163cafe2131aa73cdbb50df10d4e4912cff53b`; structural QC `b7d3fa92fc9f3bed00931d19097e08cd91eab62b`; event fixture `e301f38db66f44193d799a9c1a02c99169823d45`; JSON fixture `654557363745f580f425252395542e9fb91adaad`; negative guard `8d40bc7f3dce9c9717e41fa1060c553434ad9959`.

## V164 static and pre-song seals
- Authoritative static-preflight PASS run `33221759016`, attempt `1`, job `99017084779`, head `720f26aa7f23fcdc127aa8cbe34e05e7ca63f215`; workflow blob `e6beec5526ed5e4925475eaab86f5ca78909a349`.
- Pre-run identity receipt commit `918c2982f92afe1f21d9f36c776ca74ce894c87e`, blob `fa1942690b45bce35515abee35016f953fcccd45`, PASS.
- CPU environment seal run `33221962951`, run `1`, attempt `1`, job `99017692441`, head `8fb7dcb27b04139be31aee07ca0de1d965325d4b`, PASS.
- Environment receipt commit `2fdd87c083dc89d575209cbd8cc97e7265a28bd6`, blob `25a7f5e2c692a6ac518ae1243ea812cf650f7278`.
- Verified CPU environment: Python `3.10.21`; torch `2.8.0+cpu`; CUDA unavailable/null; numpy `1.26.4`; scipy `1.13.1`; soundfile `0.12.1`; basic-pitch `0.4.0`; demucs `4.1.0`; imageio-ffmpeg `0.6.0`; librosa `0.11.0`; deterministic threads/seeds fixed.

## V164 sole generation — TERMINAL / CONSUMED
- Arm commit `984a542a846ff711600ef86c3114f48d4d0b5f89`.
- Workflow run `33222155380`, run number `1`, attempt `1`, job `99018290109`.
- CPU only; no GPU/CUDA/Modal.
- Exact source materialized from historical blob path and verified at 3,478,611 bytes, SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Fresh normalization executed once.
- Fresh Demucs `htdemucs_6s`, CPU, shifts `1`, jobs `1` executed once successfully.
- Fresh V164 timebase built successfully: detected beats `448`, selected phase `1`, subdivision count `1805`.
- Independent V164 timebase QC PASS before pitch. Timebase SHA256 `1ce4e9e2214ec87a4ed378007b5d2dfa62a890dc5bd6a84244df6ead41e628d8`; timebase blob `3ac889cd913bf6528741cb4df4f7b343014466f1`; QC blob `3ec4199f20ae7dc016395f41dcd527dbc20f3216`, QC SHA256 `1cfda58a4a5bc7da9f6be84b7ed6193896fdd342dec540023f737334c4d7ea23`.
- QC safety explicitly records `pitchInferenceInvoked=false`, `referenceRead=false`, `V163CandidateRead=false`, `V163ScoreRead=false`, `gpuUsed=false`.
- Transcriber failed before adapted module execution/pitch inference with: `RuntimeError: V164 frozen-source transform drift for event-logic provenance path: expected 2, found 3`.
- No V164 candidate exists.
- No V164 generation receipt exists.
- No V164 structural-QC receipt exists.
- Terminal self-freeze commit `5b63614b77a74777c50669d73c5c6607991df0a0`.
- Terminal-freeze blob `e2203663df78d2dce5d17e65bd94f4a2bb685e27`; schema `dadrock.tabs.v164.terminal-freeze.v1`; status `TERMINAL`; outcome `TRANSCRIBER_FAIL`; last completed stage `TIMEBASE_QC_PASS`; candidateAuthoritative=false; professionalReferenceScoringAuthorized=false; `neverRearmV164=true`.
- V164 generation-workflow blob was `1e545e8ea54a5884007abbdcf08818e51e00073a`; workflow self-deleted in terminal commit and is absent at terminal head.
- No professional reference/scorer or V163 candidate/score artifact was read during V164 generation.
- `main`/Production remained untouched.

## V164 execution counters at terminal
- Static-preflight runs: `3` PASS.
- Pre-run identity seals: `1` PASS.
- CPU environment verification: `1` PASS.
- Sole generation runs: `1` CONSUMED.
- Song source materializations/reads: `1`.
- Normalizations: `1`.
- Demucs separations: `1`.
- Timebase builds: `1` PASS.
- Independent timebase QCs: `1` PASS.
- Pitch inference: `0`.
- V164 candidates: `0`.
- Structural-QC executions: `0`.
- Professional-reference/scorer reads: `0`.
- V163 candidate/score reads for V164: `0`.
- GPU/CUDA/Modal: `0`.
- `main`/Production modifications: `0`.

## Hard boundary — NEXT
1. Never reopen V163 or V164. V164 generation is consumed forever; do not rerun, rearm, repair, regenerate, or resume from its timebase.
2. If continuing, use a fresh V165 preregistration created before any V165 implementation code.
3. V165 may use only the V164 runtime failure as implementation evidence: the source adapter exact-count defect. It must not use V164 timebase values, stems, song evidence, V163 score/reference data, or professional reference/scorer evidence for musical/numeric changes.
4. Freeze all V164 musical/numeric behavior unchanged in V165. The permitted implementation repair is limited to making the transcriber source adaptation robust/correct for the known 3-occurrence provenance path and strengthening static validation to instantiate the adapted transcriber song-blind before runtime.
5. V165 requires a fresh static preflight PASS, fresh pre-run identity seal, fresh CPU-environment verification/seal, and a new one-shot CPU generation boundary.
6. No V165 song processing before those seals. No GPU/Modal/CUDA without fresh explicit authorization.
7. PR #22 remains unmerged; never merge or modify `main` without explicit user direction.
