# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V163 and V164 are terminal/consumed and permanently closed. V165 is a preregistered implementation-only repair of the V164 frozen-source adapter failure; every V164 musical/numeric setting is frozen unchanged. V165 implementation is complete and its authoritative CPU-only song-blind static preflight PASSED, including the new mandatory test that actually constructs the adapted transcriber before any audio exists. No V165 song audio, normalization, separation, timebase, pitch inference, candidate generation, professional-reference/scorer read, V163/V164 runtime-artifact use, or GPU execution has occurred. Next boundary: separately seal V165 pre-run identity and CPU environment before any song processing.**

## Standing safety
- CPU-only reference-free work authorized at assistant discretion.
- Fresh explicit authorization required immediately before Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159/V160/V161/V162/V163/V164 generation versions are closed forever.
- Never rerun/rearm/repair/retune/regenerate/re-QC/rescore a closed version.
- No professional-reference event/measure mining, candidate repair, score-informed retune, threshold sweep, variant selection, or human correction.
- V163 score/reference evidence may not shape V164/V165 design or numerics.
- PR #22 remains unmerged and is only a visibility/check surface; `main` is untouched.

## V163 terminal anchors
- Generation run `33213512389`, attempt `1`, job `98991933938`; terminal commit `3b6f98750291a2f7b229c5e50cbf802752cf84d4`; structural QC PASS.
- Candidate blob `f4eafb1488f139198cb7860a76f294c0e1775df8`; SHA256 `cc55d596a05bd8e9c0a149f6ba8263375c26fbb7334139a75697b58ca23c8c19`; Guitar `1041`, Bass `404`.
- Sole score run `33214223643`, attempt `1`, job `98994146394`; terminal score commit `7bd8c813cac506811e3c144e5efe9edcd3abc561`; `SCORE_GATE_FAIL`.

## V164 terminal summary
- Prereg blob `05d255d75a6c1947891fba38d96d9399e3f75f9c`; contract blob `098f24282b59abba0f7cffa0793b344b76701724`.
- Sole generation arm `984a542a846ff711600ef86c3114f48d4d0b5f89`; run `33222155380`, run `1`, attempt `1`, job `99018290109`.
- CPU-only fresh normalization/separation succeeded; fresh V164 timebase built and independent timebase QC PASSED before pitch.
- Timebase SHA256 `1ce4e9e2214ec87a4ed378007b5d2dfa62a890dc5bd6a84244df6ead41e628d8`; blob `3ac889cd913bf6528741cb4df4f7b343014466f1`; QC blob `3ec4199f20ae7dc016395f41dcd527dbc20f3216`.
- V164 failed before pitch while constructing its transcriber adapter: `event_logic_v162.py` expected count `2`, actual `3`.
- No V164 candidate, generation receipt, or structural-QC receipt exists.
- Terminal commit `5b63614b77a74777c50669d73c5c6607991df0a0`; terminal-freeze blob `e2203663df78d2dce5d17e65bd94f4a2bb685e27`; outcome `TRANSCRIBER_FAIL`; last stage `TIMEBASE_QC_PASS`; `neverRearmV164=true`.
- V164 generation workflow self-deleted. V164 is consumed forever.

## V165 pre-code seals
- Prereg `debug/v165-cpu-autonomous/preregistration.json`: commit `7f64743d34da39fb1abc3f542fd6fcec82e5f139`, blob `1ca5c7b91263c99c0150db085d12f4c0853940b7`, PASS.
- Contract `debug/v165-cpu-autonomous/implementation-contract.json`: commit `07a2470a5a6b525ad175bdffc0a90c0c559eee6d`, blob `727782651e14699a0205ea97abc6e82b387299dc`, PASS.
- Contract freezes every V164 musical/numeric setting.
- Sole permitted functional repair: count-checked provenance transform `event_logic_v162.py -> event_logic_v165.py` requires exactly `3` occurrences; no unbounded replacement.
- Mandatory added static boundary: actually call V165 `build_adapted_module()` song-blind without calling adapted `main` or loading audio/Demucs/pitch/reference/scorer/V163/V164 runtime artifacts.

## V165 implementation identities
- `validation/v165_cpu_autonomous/event_logic_v165.py` blob `b296b3c322c13f8963f253f9b0666db66766a178` — exact pinned V164 behavior adapter.
- `validation/v165_cpu_autonomous/transcribe_v165.py` blob `45d595853302b077fbf4f3094e9a4922fba02435` — exact pinned V164 transcriber adapter plus sole preregistered count `2 -> 3` repair.
- `validation/v165_cpu_autonomous/build_timebase_v165.py` blob `62d67becb768e1e5e3e8de1cd3b121eb863b2a18` — exact pinned V164 behavior adapter.
- `validation/v165_cpu_autonomous/timebase_qc_v165.py` blob `3c11a490d24d06647894ee8c3700d9ff7decd993` — exact pinned V164 behavior adapter.
- `validation/v165_cpu_autonomous/structural_qc_v165.py` blob `36b4738cc7c00fa32aa684b3d395a67d5294a61d` — V164 QC adapter with wrapper-aware adapter-repair identity checks.
- `validation/v165_cpu_autonomous/test_event_logic_v165.py` blob `92bacaa37b4ccc7913309d677eeb88732132376d` — preserved V164 song-blind behavior/invariance expectations.
- `validation/v165_cpu_autonomous/test_transcriber_adapter_v165.py` blob `b7f92b0c9ade4c76472499999b63414564a68530` — new mandatory constructor regression test.
- `validation/v165_cpu_autonomous/test_json_native_v165.py` blob `dbff545295c97fe075462efce034f59394b6f1e3` — preserved V164 JSON-native expectations.
- `debug/v165-cpu-autonomous/negative-runtime-guard.py` current blob `6c78189eb72a2017dd1bcdc35330cd14e8b4c274`.
- `.github/workflows/v165-static-preflight.yml` blob `51d996c28ec0c10c5f7b4658ee50a9479e978fb6`.

## V165 static preflight history
### Run 1 — implementation/tests PASS; guard-only false positives
- Run `33222786569`, run number `1`, attempt `1`, job `99020200050`, head `f044678d6daeaede7fa71a8a25b078a2930d3c01`.
- Syntax PASS; preserved behavior/invariance PASS; new adapter-construction fixture PASS; JSON-native PASS.
- Core repair was proven: frozen V162 provenance occurrences `3`, required V165 occurrences `3`, `adapterConstructionSucceeded=true`, adapted main not called, all song/reference/V163/V164-runtime/GPU safety flags false.
- Overall run failed only because the first negative guard produced two false positives: intentional pinned V164 source access inside the adapter test and an over-specific source-string shape check.
- Only the static guard was corrected; no V165 algorithm, transcriber, numeric contract, or fixture behavior changed.

### Run 2 — AUTHORITATIVE PASS
- Run `33222844104`, run number `2`, attempt `1`, job `99020375844`.
- Head SHA `cc886dd3786781101d4a25660cbcc368fde166db`.
- Ubuntu `24.04.4`; Python `3.11.16`; static dependency only `numpy==2.0.2`.
- Syntax compile PASS.
- Preserved V164 behavior/invariance fixture through V165: `dadrock.tabs.v165.local-evidence-static-test.v2`, validation PASS. Remote/local-scale/zero/boundary/nonfinite and frozen V162 regression checks all true.
- Mandatory transcriber adapter construction fixture: `dadrock.tabs.v165.transcriber-adapter-static-test.v1`, PASS. Frozen V162 occurrences `3`; required V165 occurrences `3`; adapter construction succeeded; adapted main not called.
- JSON-native local-provenance fixture: `dadrock.tabs.v165.json-native-local-provenance-static-test.v1`, PASS.
- Negative guard: `dadrock.tabs.v165.negative-runtime-guard.v1`, PASS, `failures=[]`.
- Guard checks all true: pre-code seals exact; implementation pins exact; repair contract exact; frozen V164 source adapters pinned; constructor fixture present; V165 runtime artifacts absent; no professional-reference/V164-runtime paths; workflow CPU/static only.
- Safety across static run: songAudioRead=false; normalizationExecuted=false; demucsInvoked=false; pitchInferenceInvoked=false; professionalReferenceRead=false; frozenScorerRead=false; V163CandidateRead=false; V163ScoreRead=false; V164RuntimeArtifactRead=false; gpuUsed=false.

## Current counters
- V164 sole generation: `1` consumed; V164 pitch inference `0`; candidate `0`; structural QC `0`.
- V165 static-preflight runs: `2` total; authoritative run #2 PASS.
- V165 song audio reads: `0`; normalization `0`; separation `0`; timebase `0`; pitch `0`; candidate `0`; structural QC `0`.
- V165 professional-reference/scorer reads: `0`; V163/V164 runtime-artifact reads: `0`.
- GPU/CUDA/Modal: `0`; main/Production modifications: `0`.

## Hard boundary — NEXT
1. Never reopen V163 or V164.
2. Treat run `33222844104` / job `99020375844` / head `cc886dd3786781101d4a25660cbcc368fde166db` as the authoritative V165 static PASS.
3. Seal a V165 pre-run identity receipt pinned to exact prereg/contract/implementation/guard/workflow identities before any song processing.
4. Independently verify and seal the full CPU generation environment after the pre-run identity seal, still song-blind.
5. No V165 song processing until both receipts are sealed PASS.
6. Then arm exactly one CPU V165 generation after all preparatory branch writes are complete. Fresh source/normalize/separate/timebase/QC required; pitch forbidden before fresh independent V165 timebase-QC PASS.
7. Generation may not read professional reference/scorer, V163 artifacts, or V164 runtime artifacts. V165 maximum generation runs `1`; rerun/repair after generation forbidden.
8. No GPU/Modal/CUDA without fresh explicit authorization. Never modify/merge `main` without explicit user direction.
