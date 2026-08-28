# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V163 is terminal/consumed and permanently closed. V164 is preregistered; its numeric contract, implementation, final CPU static preflight, pre-run identity, and full CPU generation environment are all separately sealed PASS. No V164 song audio, normalization, separation, timebase, pitch inference, candidate generation, professional-reference/scorer read, V163 candidate/score read, or GPU execution has occurred. The next boundary is the one-shot CPU V164 generation arm after all preparatory branch writes are finished.**

## Standing safety
- CPU-only reference-free work authorized at assistant discretion.
- Fresh explicit authorization required immediately before Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159/V160/V161/V162/V163 generation versions closed forever; V163 score opportunity closed forever.
- Never rerun/rearm/repair/retune/regenerate/re-QC/rescore V163 or advance it downstream.
- No professional-reference event/measure mining, candidate repair, score-informed retune, threshold sweep, variant selection, or human correction.
- V163 aggregate score was observed before V164 preregistration. V164 does not claim reviewer score-blindness; V164 design/numerics remain quarantined from V163 score/reference evidence.

## V163 terminal anchors
- Generation run `33213512389`, attempt `1`, job `98991933938`; terminal commit `3b6f98750291a2f7b229c5e50cbf802752cf84d4`; `STRUCTURAL_QC_PASS`.
- Candidate blob `f4eafb1488f139198cb7860a76f294c0e1775df8`; SHA256 `cc55d596a05bd8e9c0a149f6ba8263375c26fbb7334139a75697b58ca23c8c19`; Guitar `1041`, Bass `404`.
- Sole score run `33214223643`, attempt `1`, job `98994146394`; terminal score commit `7bd8c813cac506811e3c144e5efe9edcd3abc561`.
- Score terminal blob `b7e6634d67b89632389f2be3edfdbe0162ff98dd`; `SCORE_GATE_FAIL`; Guitar F1 `0.059983566146261304`, Bass F1 `0.21661409043112514`, gates `0.80/0.80`.
- Score report blob `d10ae33aba35afd2547f94a3ec3dcd8443972fcf`; SHA256 `b87e745d1b3dafea2e99b841e8af028c55f8749341e5736fa5ec488ebf66cfd9`.

## V164 frozen design/code anchors
- Prereg blob `05d255d75a6c1947891fba38d96d9399e3f75f9c`.
- Numeric-contract blob `098f24282b59abba0f7cffa0793b344b76701724`.
- `event_logic_v164.py` blob `62303877a1971f75cacda002c5ad921680161674`.
- `test_event_logic_v164.py` blob `13d29ef19a297d19469196cb2a23a4c0d6e040de`.
- `build_timebase_v164.py` blob `170a7a15d68e271d93775c2aaba058fe3ebaa8bb`.
- `timebase_qc_v164.py` blob `e59498e76d881f22ea405c81781ca2004ea8f53e`.
- `transcribe_v164.py` blob `df1302216df404bc3368ff820f005d6b63ae100d`.
- `structural_qc_v164.py` blob `c1a81c7a97e646398f5e50cbc63dae341cdc500b`.
- `test_json_native_v164.py` blob `a0b525485bbea933004045622bbf8c63527f123b`.
- `negative-runtime-guard.py` blob `230aa1efeb4640aabbb05720ead031e13cc57337`.
- Frozen V162 pins: contract `409da313ed03a6c232d6578d48b0da6aa35b000b`; event logic `9f9b33fd8c210ad581025b454cf69b6999aa544b`; timebase builder `f7e9483aea16af770bcffe01ad8cfaf689d693b9`; timebase QC `78acc9fd626039801011d039cca12686b72369c0`; transcriber `fa163cafe2131aa73cdbb50df10d4e4912cff53b`; structural QC `b7d3fa92fc9f3bed00931d19097e08cd91eab62b`; event fixture `e301f38db66f44193d799a9c1a02c99169823d45`; JSON fixture `654557363745f580f425252395542e9fb91adaad`; negative guard `8d40bc7f3dce9c9717e41fa1060c553434ad9959`.

## Cellphone-safe V164 static preflight — PASS
- Current static workflow `.github/workflows/v164-static-preflight.yml` blob `e6beec5526ed5e4925475eaab86f5ca78909a349`; guarded-path narrowing commit `720f26aa7f23fcdc127aa8cbe34e05e7ca63f215`.
- Authoritative final static run `33221759016`, run number `3`, attempt `1`, job `99017084779`, head `720f26aa7f23fcdc127aa8cbe34e05e7ca63f215`.
- Syntax compile PASS; local-evidence invariance PASS; JSON-native provenance PASS; negative guard PASS with `failures=[]`.
- Safety: songAudioRead=false; demucsInvoked=false; pitchInferenceInvoked=false; professionalReferenceRead=false; frozenScorerRead=false; V163CandidateRead=false; V163ScoreRead=false; gpuUsed=false.
- Earlier redundant safe PASS runs: `33221653962` / `99016763456` and `33221718293` / `99016958023`.
- PR #22 remains unmerged and is only a visibility/check surface; `main` is untouched.

## V164 pre-run identity — SEALED PASS
- File `debug/v164-cpu-autonomous/pre-run-identity-receipt.json`.
- Commit `918c2982f92afe1f21d9f36c776ca74ce894c87e`; blob `fa1942690b45bce35515abee35016f953fcccd45`.
- Schema `dadrock.tabs.v164.pre-run-identity-receipt.v1`; status `SEALED_AFTER_STATIC_PREFLIGHT_BEFORE_SONG_PROCESSING`; validation PASS.
- Pins exact V164 code/static-workflow identities and final static run `33221759016` / job `99017084779`.
- At pre-run seal: environment/timebase/timebase-QC/candidate/generation receipt/structural-QC/terminal freeze/generation workflow absent; all runtime/reference/V163/GPU counters zero.

## V164 CPU environment — SEALED PASS
- Song-blind/read-only environment workflow `.github/workflows/v164-environment-seal.yml` created at commit `8fb7dcb27b04139be31aee07ca0de1d965325d4b`; workflow blob `a6b5c30293b3255ab7ce0e31fdc115c4aad24e9e`.
- Environment run ID `33221962951`, run number `1`, attempt `1`, job `99017692441`, head `8fb7dcb27b04139be31aee07ca0de1d965325d4b`; conclusion success.
- The job first verified pre-run blob `fa1942690b45bce35515abee35016f953fcccd45`, exact V164 code pins, and absence of environment/timebase/timebase-QC/candidate/generation/QC/terminal/generation-workflow artifacts before dependency installation.
- Verified Python `3.10.21`; torch `2.8.0+cpu`; `torch.version.cuda=null`; `torch.cuda.is_available()=false`.
- Exact dependencies: numpy `1.26.4`; scipy `1.13.1`; soundfile `0.12.1`; basic-pitch `0.4.0`; demucs `4.1.0`; imageio-ffmpeg `0.6.0`; librosa `0.11.0`.
- Determinism verified: seed `0`; Torch deterministic algorithms true; Torch threads/interops `1`; math-library threads `1`; `CUDA_VISIBLE_DEVICES` empty.
- Planned separation is frozen but not executed at seal: `htdemucs_6s`, CPU, shifts `1`, jobs `1`, repeat count `1`.
- Environment receipt file `debug/v164-cpu-autonomous/environment-receipt.json` committed at `2fdd87c083dc89d575209cbd8cc97e7265a28bd6`; blob `25a7f5e2c692a6ac518ae1243ea812cf650f7278`.
- Receipt schema `dadrock.tabs.v164.cpu-environment-receipt.v1`; status `VERIFIED_BEFORE_SONG_PROCESSING`; validation PASS.
- Receipt safety: referenceRead=false; professionalReferencePathsOpened=0; frozenScorerRead=false; V163CandidateRead=false; V163ScoreRead=false; prior candidate/score=false; songAudioRead=false; normalizationExecuted=false; demucsExecuted=false; pitchInferenceExecuted=false; cudaGpuUsed=false; modalUsed=false; mainOrProductionModified=false.
- Unrelated legacy cleanup workflow failure on the environment-seal push is not part of V164 and has no bearing on the PASS environment seal.

## Current V164 execution counters
- Static-preflight runs: `3` PASS.
- Pre-run identity seals: `1` PASS.
- CPU environment verification runs: `1` PASS.
- CPU environment receipts: `1` sealed PASS.
- Song audio reads: `0`.
- Normalization: `0`.
- Demucs separation: `0`.
- Timebase builds/QC: `0`.
- Pitch inference: `0`.
- V164 candidate generations: `0`.
- Professional-reference/scorer reads for V164: `0`.
- V163 candidate/score reads for V164: `0`.
- GPU/CUDA/Modal: `0`.
- `main`/Production modifications: `0`.

## Hard boundary — NEXT
1. Never reopen V163.
2. Both required pre-song seals are satisfied: pre-run blob `fa194269...` and environment blob `25a7f5e2...`.
3. Finish and checkpoint all preparatory branch writes before arming the one-shot `.github/workflows/v164-generate.yml`.
4. Generation must be CPU-only, exactly one run/attempt, rerun/duplicate/repair forbidden, and no assistant/manual branch writes while active.
5. The one-shot run must fresh-materialize the fixed source, fresh-normalize, fresh-separate with the verified environment, build fresh V164 timebase, run independent V164 timebase QC, and **must not invoke pitch before timebase-QC PASS**.
6. Only after timebase-QC PASS may fresh V164 pitch/transcription run, followed by fresh independent structural QC. Only structural-QC PASS can make the candidate authoritative.
7. Generation must not read professional reference/scorer or any V163 candidate/score artifact.
8. No GPU/Modal/CUDA without fresh explicit authorization.
9. Generation terminalization must freeze exact artifacts/run identities and prevent any second V164 generation.
