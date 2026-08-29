# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V163, V164, and V165 generation are terminal/consumed and permanently closed. V165 completed its sole CPU-only generation successfully and is now the authoritative reference-blind candidate after independent structural QC PASS. V165 must never be rerun, rearmed, repaired, retuned, regenerated, or re-QC'd. No professional-reference/scorer read has occurred for V165 and professional-reference scoring is not yet authorized. `main`/Production remain untouched.**

## Standing safety
- CPU-only reference-free work is authorized at assistant discretion.
- Fresh explicit authorization is required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159/V160/V161/V162/V163/V164/V165 generation versions are closed forever; never rerun/rearm/repair/retune/regenerate/re-QC a closed version.
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
- Transcriber failed before pitch/candidate because the adapter expected `2` `event_logic_v162.py` occurrences and frozen source contained `3`.
- Terminal commit `5b63614b77a74777c50669d73c5c6607991df0a0`; terminal-freeze blob `e2203663df78d2dce5d17e65bd94f4a2bb685e27`; no candidate; `neverRearmV164=true`.

## V165 frozen design and implementation
- Prereg commit `7f64743d34da39fb1abc3f542fd6fcec82e5f139`; blob `1ca5c7b91263c99c0150db085d12f4c0853940b7`; PASS.
- Contract commit `07a2470a5a6b525ad175bdffc0a90c0c559eee6d`; blob `727782651e14699a0205ea97abc6e82b387299dc`; PASS.
- Sole functional repair: count-checked `event_logic_v162.py -> event_logic_v165.py`, required count `3`; every V164 musical/numeric behavior frozen unchanged.
- Event logic `b296b3c322c13f8963f253f9b0666db66766a178`.
- Event test `92bacaa37b4ccc7913309d677eeb88732132376d`.
- Timebase builder `62d67becb768e1e5e3e8de1cd3b121eb863b2a18`.
- Timebase QC `3c11a490d24d06647894ee8c3700d9ff7decd993`.
- Transcriber `45d595853302b077fbf4f3094e9a4922fba02435`.
- Structural QC `36b4738cc7c00fa32aa684b3d395a67d5294a61d`.
- Adapter construction test `b7f92b0c9ade4c76472499999b63414564a68530`.
- JSON test `dbff545295c97fe075462efce034f59394b6f1e3`.
- Negative guard `6c78189eb72a2017dd1bcdc35330cd14e8b4c274`.
- Static workflow `51d996c28ec0c10c5f7b4658ee50a9479e978fb6`.

## V165 static / pre-run / environment seals
- Static run #1 `33222786569` / job `99020200050`: substantive fixtures PASS but guard-only false positives made overall FAIL; no runtime work.
- Authoritative static run `33222844104`, run `2`, attempt `1`, job `99020375844`, head `cc886dd3786781101d4a25660cbcc368fde166db`: compile, invariance/regression, mandatory adapter construction (`3 -> 3`), JSON, and negative guard all PASS; `failures=[]`.
- Pre-run identity receipt commit `8665d164b1964e6d62efffc13b45da70dfcef794`; blob `a2acd7839a2ec05ca0be04c4ed38e532b9af3559`; PASS.
- CPU environment run `33223054612`, run `1`, attempt `1`, job `99021012645`, head `c7c3b7dd49e3743e8ff1e3306efaf5f52d77b0bf`; PASS.
- Environment workflow blob `24f4a0631229044e4d8990627b0f38c4f7edce8c`; receipt blob `84160ae885316450ad59c3dca5bbb9692e4dfdc9`.
- Verified Python `3.10.21`, torch `2.8.0+cpu`, CUDA unavailable/null; numpy `1.26.4`, scipy `1.13.1`, soundfile `0.12.1`, basic-pitch `0.4.0`, demucs `4.1.0`, imageio-ffmpeg `0.6.0`, librosa `0.11.0`.
- Determinism: seed `0`, torch deterministic algorithms true, Torch threads/inter-op `1`, math-library threads `1`; Demucs plan `htdemucs_6s`, CPU, shifts `1`, jobs `1`, repeat `1`.

## V165 sole generation — TERMINAL STRUCTURAL_QC_PASS
- One-shot workflow arm head `c04832da85afdd9a585141dd763dc3c1212ace6e`; workflow blob `a7dfc42450a160f8143d025d288f6e42103cf0d0`.
- Sole workflow run `33223256331`, run number `1`, attempt `1`, job `99021632117`; all steps PASS including identity/sealed-boundary guard, CPU pipeline, and terminal freeze/self-seal.
- Terminal commit `97c2efe6acf988a4535de1fff449194b7b2f7c2b`: `research: freeze sole V165 adapter-repair CPU candidate [skip ci]`; generation workflow self-deleted.
- Terminal freeze blob `857153fdaedd3c386d5802277cf60e68ae231dc6`; status `TERMINAL`; outcome `STRUCTURAL_QC_PASS`; last completed stage `STRUCTURAL_QC_PASS`; `candidateAuthoritative=true`; `neverRearmV165=true`; `professionalReferenceScoringAuthorized=false`.
- Candidate `debug/v165-cpu-autonomous/generated.json`: blob `e70a444cb7778a6f56988cf8cc69dccb9c1d89ce`; SHA256 `b1ad02001724750ea82d693591a7c0b1f214820de37a590871a6d78eef63e5cb`.
- Candidate counts: combined Guitar `1043`; Bass `405`.
- Evidence-step corrections: combined Guitar `17`; Bass `6`; pre-grid excluded `0` for both.
- Generation receipt blob `f539cd46d9e050ba2a13ed036f6e4528cb88bf1b`; SHA256 `2ea04a846079426677fcac5924d3e41c8026ed1d9c38c3d490003f8a1a0aa716`.
- Timebase blob `1e05842c10e4507f5e247e744d82ed03d21f9d8d`; SHA256 `eaef13457f7a2d357d9f288afdeb8b9d0364f85be29b367247245cf9ed636426`.
- Timebase-QC blob `abd04e343aae15c6012b8fbec03ed1fe19a6ab24`; SHA256 `8c4054decc381b862f95f32b4b95a43b05cb2108bc357b00e2d6b8c3d7e2002c`; independent PASS before pitch.
- Structural-QC blob `f411e6c98b8ae33ba6f545d1b4dea12c80019a94`; SHA256 `af2f88975b9681e256c01ca14586bc4dd50d8229dc455df057b2ffb75cc2cc57`; `validation=PASS`, `errors=[]`.
- Structural QC verifies candidate/generation/timebase hash chains, exact code pins, adapter repair identity, subdivision lattice, stream counts, Guitar polyphony cap 6, Bass monophony cap 1, single-run/write-once boundary, and reference-blind safety.
- Generation safety: professional reference/scorer reads `0`; V163 candidate/score reads false; V164 runtime-artifact read false; prior candidate/score reads false; threshold sweep/variant selection/human correction false; GPU/CUDA/Modal false; `main`/Production untouched.

## Current counters
- V164 generation runs `1` consumed; candidate `0`.
- V165 static-preflight runs `2`; authoritative run #2 PASS.
- V165 pre-run seals `1` PASS; CPU environment seals `1` PASS.
- V165 generation runs `1` consumed; candidate generations `1`; structural QC `1` PASS.
- V165 authoritative candidate: Guitar `1043`, Bass `405`.
- V165 professional-reference/scorer reads `0`; V163/V164 runtime-artifact reads `0`.
- GPU/CUDA/Modal `0`; `main`/Production modifications `0`.

## Hard boundary — NEXT
1. Never reopen or rerun V163, V164, or V165 generation. V165 generation is consumed forever.
2. V165 candidate is authoritative only as the exact hash-pinned candidate above; do not repair, retune, regenerate, re-QC, threshold-sweep, variant-select, or human-correct it.
3. Professional-reference scoring is currently **not authorized** by the V165 terminal freeze. Do not read professional reference/scorer or score V165 until a separately sealed scoring authorization/preregistration boundary explicitly permits the sole score opportunity.
4. Any future score, if separately authorized, must be read-only against the frozen V165 candidate and may not feed candidate repair/retuning.
5. No GPU/Modal/CUDA without fresh explicit user authorization. Never modify/merge `main`/Production without explicit user direction.
