# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V163, V164, and V165 generation are terminal/consumed and permanently closed. V165 completed its sole CPU-only generation successfully and is the authoritative reference-blind candidate after independent structural QC PASS. A separate V165 score preregistration is now sealed, and the exact frozen scorer/professional-reference identities have been verified read-only and sealed before any score execution. V165 generation must never be rerun/rearmed/repaired/retuned/regenerated/re-QC'd. The next boundary is exactly one read-only CPU professional-reference score, after score-workflow audit/arming. `main`/Production remain untouched.**

## Standing safety
- CPU-only reference-free work is authorized at assistant discretion.
- Fresh explicit authorization is required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159/V160/V161/V162/V163/V164/V165 generation versions are closed forever; never rerun/rearm/repair/retune/regenerate/re-QC a closed generation.
- No professional-reference event/measure mining, candidate repair, score-informed retune, threshold sweep, variant selection, or human correction.
- V163 score/reference evidence and V164 runtime/audio/timebase values did not shape V165 musical/numeric behavior.
- PR #22 remains open/unmerged and is only a visibility/check surface.

## V163 terminal anchors
- Generation run `33213512389`, attempt `1`, job `98991933938`; terminal commit `3b6f98750291a2f7b229c5e50cbf802752cf84d4`; structural QC PASS.
- Candidate blob `f4eafb1488f139198cb7860a76f294c0e1775df8`; SHA256 `cc55d596a05bd8e9c0a149f6ba8263375c26fbb7334139a75697b58ca23c8c19`; Guitar `1041`, Bass `404`.
- Sole score run `33214223643`, attempt `1`, job `98994146394`; terminal score commit `7bd8c813cac506811e3c144e5efe9edcd3abc561`; `SCORE_GATE_FAIL`.

## V164 terminal summary
- Prereg blob `05d255d75a6c1947891fba38d96d9399e3f75f9c`; contract blob `098f24282b59abba0f7cffa0793b344b76701724`.
- Sole generation run `33222155380`, run `1`, attempt `1`, job `99018290109`, arm head `984a542a846ff711600ef86c3114f48d4d0b5f89`.
- CPU normalization/separation + fresh timebase + independent timebase QC PASS before pitch.
- Transcriber failed before pitch/candidate because adapter expected `2` `event_logic_v162.py` occurrences while frozen source contained `3`.
- Terminal commit `5b63614b77a74777c50669d73c5c6607991df0a0`; terminal-freeze blob `e2203663df78d2dce5d17e65bd94f4a2bb685e27`; no candidate; `neverRearmV164=true`.

## V165 frozen design and implementation
- Prereg commit `7f64743d34da39fb1abc3f542fd6fcec82e5f139`; blob `1ca5c7b91263c99c0150db085d12f4c0853940b7`; PASS.
- Contract commit `07a2470a5a6b525ad175bdffc0a90c0c559eee6d`; blob `727782651e14699a0205ea97abc6e82b387299dc`; PASS.
- Sole functional repair: count-checked `event_logic_v162.py -> event_logic_v165.py`, required count `3`; every V164 musical/numeric behavior frozen unchanged.
- Event logic `b296b3c322c13f8963f253f9b0666db66766a178`; event test `92bacaa37b4ccc7913309d677eeb88732132376d`.
- Timebase builder `62d67becb768e1e5e3e8de1cd3b121eb863b2a18`; timebase QC `3c11a490d24d06647894ee8c3700d9ff7decd993`.
- Transcriber `45d595853302b077fbf4f3094e9a4922fba02435`; structural QC `36b4738cc7c00fa32aa684b3d395a67d5294a61d`.
- Adapter test `b7f92b0c9ade4c76472499999b63414564a68530`; JSON test `dbff545295c97fe075462efce034f59394b6f1e3`; negative guard `6c78189eb72a2017dd1bcdc35330cd14e8b4c274`; static workflow `51d996c28ec0c10c5f7b4658ee50a9479e978fb6`.

## V165 static / pre-run / environment seals
- Static run #1 `33222786569` / job `99020200050`: substantive fixtures PASS but guard-only false positives made overall FAIL; no runtime work.
- Authoritative static run `33222844104`, run `2`, attempt `1`, job `99020375844`, head `cc886dd3786781101d4a25660cbcc368fde166db`: compile, invariance/regression, adapter construction `3 -> 3`, JSON, negative guard all PASS; `failures=[]`.
- Pre-run identity receipt commit `8665d164b1964e6d62efffc13b45da70dfcef794`; blob `a2acd7839a2ec05ca0be04c4ed38e532b9af3559`; PASS.
- CPU environment run `33223054612`, run `1`, attempt `1`, job `99021012645`, head `c7c3b7dd49e3743e8ff1e3306efaf5f52d77b0bf`; PASS.
- Environment workflow blob `24f4a0631229044e4d8990627b0f38c4f7edce8c`; receipt blob `84160ae885316450ad59c3dca5bbb9692e4dfdc9`.
- Verified Python `3.10.21`; torch `2.8.0+cpu`; CUDA unavailable/null; numpy `1.26.4`; scipy `1.13.1`; soundfile `0.12.1`; basic-pitch `0.4.0`; demucs `4.1.0`; imageio-ffmpeg `0.6.0`; librosa `0.11.0`.
- Determinism: seed `0`; torch deterministic algorithms true; Torch threads/inter-op `1`; math-library threads `1`; Demucs `htdemucs_6s`, CPU, shifts `1`, jobs `1`, repeat `1`.

## V165 sole generation — TERMINAL STRUCTURAL_QC_PASS
- One-shot arm head `c04832da85afdd9a585141dd763dc3c1212ace6e`; workflow blob `a7dfc42450a160f8143d025d288f6e42103cf0d0`.
- Sole run `33223256331`, run `1`, attempt `1`, job `99021632117`; all steps PASS including identity guard, CPU pipeline, terminal freeze/self-seal.
- Terminal commit `97c2efe6acf988a4535de1fff449194b7b2f7c2b`; generation workflow self-deleted.
- Terminal freeze blob `857153fdaedd3c386d5802277cf60e68ae231dc6`; `TERMINAL`, `STRUCTURAL_QC_PASS`, `candidateAuthoritative=true`, `neverRearmV165=true`, generation-terminal `professionalReferenceScoringAuthorized=false` (later superseded only by the separately sealed score preregistration below, not by any generation change).
- Candidate blob `e70a444cb7778a6f56988cf8cc69dccb9c1d89ce`; SHA256 `b1ad02001724750ea82d693591a7c0b1f214820de37a590871a6d78eef63e5cb`; Guitar `1043`, Bass `405`.
- Generation receipt blob `f539cd46d9e050ba2a13ed036f6e4528cb88bf1b`; SHA256 `2ea04a846079426677fcac5924d3e41c8026ed1d9c38c3d490003f8a1a0aa716`.
- Timebase blob `1e05842c10e4507f5e247e744d82ed03d21f9d8d`; SHA256 `eaef13457f7a2d357d9f288afdeb8b9d0364f85be29b367247245cf9ed636426`.
- Timebase-QC blob `abd04e343aae15c6012b8fbec03ed1fe19a6ab24`; SHA256 `8c4054decc381b862f95f32b4b95a43b05cb2108bc357b00e2d6b8c3d7e2002c`; independent PASS before pitch.
- Structural-QC blob `f411e6c98b8ae33ba6f545d1b4dea12c80019a94`; SHA256 `af2f88975b9681e256c01ca14586bc4dd50d8229dc455df057b2ffb75cc2cc57`; PASS, `errors=[]`.
- Generation safety: no professional reference/scorer, V163 candidate/score, V164 runtime artifact, prior candidate/score, threshold sweep, variant selection, human correction, GPU/CUDA/Modal, or main/Production modification.

## V165 score boundary — SEALED BEFORE SCORE EXECUTION
- Score preregistration `debug/v165-cpu-autonomous/score-preregistration.json` committed at `f7d9320cb1b96c38fc3d2cabc85b1f554046d4fe`; blob `c5e44f8e60da4e7d68e71f384b702149b327a840`.
- Schema `dadrock.tabs.v165.score-preregistration.v1`; PASS; sealed before any V165 scorer/reference read.
- Fixed score gates frozen before scorer/reference read: Guitar F1 `>=0.80`, Bass F1 `>=0.80`, both must pass.
- Sole score contract: CPU, maximum `1` run / `1` attempt; rerun/duplicate/second score forbidden; score read-only against exact V165 candidate; candidate mutation/repair/retune/regeneration/re-QC forbidden; threshold sweep/variant selection/human correction/post-score repair/rescore forbidden.
- Professional reference may be used only for the sole aggregate score; event/measure mining and reference-guided candidate changes forbidden.
- After prereg seal, read-only identity verification confirmed frozen scorer path `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference path `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`, blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- Candidate identity rechecked after prereg: blob still `e70a444cb7778a6f56988cf8cc69dccb9c1d89ce`.
- Before identity seal: `.github/workflows/v165-score.yml`, `reference-score.json`, and `score-terminal-freeze.json` all absent.
- Score identity receipt `debug/v165-cpu-autonomous/score-identity-receipt.json` committed at `831ca7d94fbd2698c2dd4641a37991a3aca07123`; schema `dadrock.tabs.v165.score-identity-receipt.v1`; PASS.
- Identity-read accounting: scorer/reference identity reads performed only after score prereg seal; score execution still `0`; no candidate change; no V163 candidate/score or V164 runtime-artifact read; no GPU/CUDA/Modal; main/Production untouched.

## Current counters
- V164 generation `1` consumed; candidate `0`.
- V165 generation `1` consumed; candidate `1`; structural QC `1` PASS; authoritative Guitar `1043`, Bass `405`.
- V165 professional-reference/scorer identity verification: `1` constrained read-only boundary completed after prereg.
- V165 reference-facing score executions: `0`.
- V165 candidate modifications after structural PASS: `0`.
- GPU/CUDA/Modal `0`; main/Production modifications `0`.

## Hard boundary — NEXT
1. Never reopen/rerun V163, V164, or V165 generation. V165 generation is consumed forever.
2. V165 candidate is immutable at blob `e70a444...` / SHA256 `b1ad0200...`; no repair, retune, regenerate, re-QC, threshold sweep, variant selection, or human correction.
3. Score preregistration and scorer/reference identity receipt are now sealed PASS. The only next reference-facing action permitted is **exactly one read-only CPU score execution** using scorer blob `9644e657...` and reference blob `2fbed60b...` against the exact frozen V165 candidate.
4. Before score execution, audit/create `.github/workflows/v165-score.yml` as the sole trigger; verify all pinned identities and absence of score receipt/terminal; finish all preparatory writes; then make zero branch writes while the score workflow is active.
5. Score workflow must self-seal `reference-score.json` + `score-terminal-freeze.json`, self-delete, and consume the sole V165 score opportunity regardless of PASS/FAIL. Never rerun/rescore.
6. Score result may not feed any candidate repair or retuning. Only the predeclared aggregate score output may be retained.
7. No GPU/Modal/CUDA without fresh explicit user authorization. Never modify/merge `main`/Production without explicit user direction.
