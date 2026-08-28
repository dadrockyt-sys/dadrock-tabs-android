# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V163 is terminal/consumed and permanently closed. V164 is preregistered, its numeric contract and implementation are frozen, the final CPU-only static preflight passed, and the V164 pre-run identity receipt is now separately sealed. No V164 song audio, normalization, separation, pitch inference, candidate generation, professional-reference/scorer read, V163 candidate/score read, or GPU execution has occurred. Next boundary: independently verify and seal the full CPU generation environment before any song processing.**

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

## Cellphone-safe V164 static preflight
- Original feature-branch-only `workflow_dispatch` was invisible in the mobile/default-branch Actions UI. User explicitly authorized a safe cellphone-friendly workaround.
- Automatic feature-branch push trigger was added without changing V164 implementation/numerics or `main`.
- Trigger was then narrowed to the V164 workflow/code/guard and frozen-dependency paths so ordinary checkpoint/receipt commits do not retrigger it.
- Current workflow `.github/workflows/v164-static-preflight.yml` blob `e6beec5526ed5e4925475eaab86f5ca78909a349`; narrowing commit `720f26aa7f23fcdc127aa8cbe34e05e7ca63f215`.
- PR #22 remains an unmerged visibility/check surface targeting `main`; `main` is untouched.

## Final V164 CPU Static Preflight — PASS
- Authoritative final guarded run: ID `33221759016`, run number `3`, attempt `1`, job `99017084779`, head SHA `720f26aa7f23fcdc127aa8cbe34e05e7ca63f215`.
- Ubuntu `24.04.4`; Python `3.11.16`; static dependency `numpy==2.0.2`.
- Syntax compile: PASS.
- Local-evidence invariance fixture `dadrock.tabs.v164.local-evidence-static-test.v2`: PASS.
- JSON-native provenance fixture `dadrock.tabs.v164.json-native-local-provenance-static-test.v1`: PASS.
- Negative guard `dadrock.tabs.v164.negative-runtime-guard.v1`: PASS, `failures=[]`.
- All safety checks true: exact frozen V162 deps; local event logic; remote/local-scale invariance; timebase-before-pitch; transcriber QC-before-pitch/local adaptation; structural-QC local-evidence recomputation; JSON-native provenance; no reference/scorer/V163 artifact paths; CPU-only static workflow.
- Safety outputs: songAudioRead=false; demucsInvoked=false; pitchInferenceInvoked=false; professionalReferenceRead=false; frozenScorerRead=false; V163CandidateRead=false; V163ScoreRead=false; gpuUsed=false.
- Earlier redundant safe PASS runs caused by initial broad push trigger: run `33221653962` / job `99016763456`, and run `33221718293` / job `99016958023`.

## V164 pre-run identity — SEALED
- File `debug/v164-cpu-autonomous/pre-run-identity-receipt.json`.
- Commit `918c2982f92afe1f21d9f36c776ca74ce894c87e`.
- Blob `fa1942690b45bce35515abee35016f953fcccd45`.
- Schema `dadrock.tabs.v164.pre-run-identity-receipt.v1`; validation PASS; status `SEALED_AFTER_STATIC_PREFLIGHT_BEFORE_SONG_PROCESSING`.
- Pins exact V164 code/workflow blobs and final static run `33221759016` / job `99017084779`.
- At seal: environment/timebase/timebase-QC/candidate/generation receipt/structural-QC/terminal freeze/generation workflow all absent.
- At seal counters: song audio 0; Demucs 0; Basic Pitch 0; pyin 0; pitch inference 0; professional-reference/scorer 0; V163 candidate/score reads 0; GPU/CUDA/Modal 0; main/Production modifications 0.

## CPU environment design basis
- Frozen structural QC requires environment schema PASS, `device=cpu`, `cudaAvailable=false`, `torchCudaVersion=null`, and later byte-for-byte embedding of the same environment receipt in the one-shot generation receipt.
- It does not require song/separation hashes merely to establish the environment.
- Last verified CPU generation stack (V163, exact frozen V162 algorithm): Python `3.10`; torch `2.8.0+cpu`; numpy `1.26.4`; scipy `1.13.1`; soundfile `0.12.1`; basic-pitch `0.4.0`; demucs `4.1.0`; imageio-ffmpeg `0.6.0`; librosa `0.11.0`.
- Determinism basis: CUDA disabled; seed 0; deterministic Torch algorithms; Torch/math-library threads 1; Demucs plan `htdemucs_6s`, CPU, shifts 1, jobs 1.
- V164 environment must be independently verified without reading song audio before the next runtime stage.

## Current V164 execution counters
- Static-preflight runs: `3` PASS (two redundant safe passes + authoritative narrowed-trigger pass).
- Pre-run identity seals: `1` PASS.
- Song audio reads: `0`.
- Normalization/separation: `0`.
- Demucs/pitch inference: `0`.
- V164 candidate generations: `0`.
- Professional-reference/scorer reads for V164: `0`.
- V163 candidate/score reads for V164: `0`.
- GPU/CUDA/Modal: `0`.
- `main`/Production modifications: `0`.

## Hard boundary — NEXT
1. Never reopen V163.
2. Verify the full pinned V164 CPU generation dependency stack in a song-blind, read-only environment-seal job; do not read/materialize song audio.
3. Seal `debug/v164-cpu-autonomous/environment-receipt.json` against pre-run blob `fa1942690b45bce35515abee35016f953fcccd45` and the verified CPU job.
4. No V164 song processing until the environment receipt is sealed and validated.
5. After both receipts are sealed, one-shot CPU generation may be armed only after all branch writes are complete. It must fresh-materialize/normalize/separate, build fresh V164 timebase, obtain independent timebase-QC PASS before pitch, then run fresh transcriber and independent structural QC.
6. Professional reference/scorer and V163 candidate/score artifacts remain forbidden during V164 generation.
7. V164 generation maximum remains one; rerun/duplicate/repair forbidden.
8. No GPU/Modal/CUDA without fresh explicit authorization.
