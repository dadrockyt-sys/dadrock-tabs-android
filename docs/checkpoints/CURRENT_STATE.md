# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V163 is terminal/consumed and failed its sole preregistered professional-reference score gate. Never rerun/rearm/repair/retune/regenerate/re-QC/rescore V163 and do not advance it to role/string/fret/technique/PDF. V164 is preregistered, its exact local-evidence numeric contract is sealed, all planned implementation/static-guard code is present, and the manual CPU-only static-preflight workflow is sealed but has NOT been dispatched. No V164 song processing, pitch inference, candidate, reference/scorer read, V163 artifact read, or GPU execution has occurred.**

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
- Frozen V162 pins used by V164: numeric contract `409da313ed03a6c232d6578d48b0da6aa35b000b`; event logic `9f9b33fd8c210ad581025b454cf69b6999aa544b`; timebase builder `f7e9483aea16af770bcffe01ad8cfaf689d693b9`; timebase QC `78acc9fd626039801011d039cca12686b72369c0`; transcriber `fa163cafe2131aa73cdbb50df10d4e4912cff53b`; structural QC `b7d3fa92fc9f3bed00931d19097e08cd91eab62b`; event fixture `e301f38db66f44193d799a9c1a02c99169823d45`; JSON fixture `654557363745f580f425252395542e9fb91adaad`; negative guard `8d40bc7f3dce9c9717e41fa1060c553434ad9959`.
- Event-local onset evidence: inclusive/clipped half-window `32` frames (up to `65` samples), finite positives only, q95 support, no-positive support `0.0` / threshold `null`.
- Beat-local subdivision q55 and event-step q95 support populations only. All unrelated V162 pitch/segmentation/register/admission/cap numerics remain frozen.
- Invariance factors: remote `1,000,000×`; local `0.1×` and `10×`; rel/abs tolerance `1e-12`.

## V164 implementation identities — all code present, no song execution
- `validation/v164_cpu_autonomous/event_logic_v164.py` blob `62303877a1971f75cacda002c5ad921680161674`.
- `validation/v164_cpu_autonomous/test_event_logic_v164.py` blob `13d29ef19a297d19469196cb2a23a4c0d6e040de`.
- `validation/v164_cpu_autonomous/build_timebase_v164.py` blob `170a7a15d68e271d93775c2aaba058fe3ebaa8bb`.
- `validation/v164_cpu_autonomous/timebase_qc_v164.py` blob `e59498e76d881f22ea405c81781ca2004ea8f53e`.
- `validation/v164_cpu_autonomous/transcribe_v164.py`: creation commit `73d952258aafcfc6e875514936099c812458096a`; Bass provenance-only follow-up `75c048ff07099d41c5eb376d92d733ad2399767a`; current blob `df1302216df404bc3368ff820f005d6b63ae100d`.
- `validation/v164_cpu_autonomous/structural_qc_v164.py`: commit `bba784a311653c4214b957d28f861aed4cbbd20d`; blob `c1a81c7a97e646398f5e50cbc63dae341cdc500b`.
- `validation/v164_cpu_autonomous/test_json_native_v164.py`: commit `9ed814225224197b3cf3deee48e8faa95c8b7560`; blob `a0b525485bbea933004045622bbf8c63527f123b`.
- `debug/v164-cpu-autonomous/negative-runtime-guard.py`: commit `8b4c3d42e774f1d7ea51b140eeefbba206fcb27f`; blob `230aa1efeb4640aabbb05720ead031e13cc57337`.

## Implementation notes
- V164 event logic pins exact frozen V162 event logic and reuses only unaffected pure helpers. V164-localized paths are supported attacks, Guitar segmentation/recovery, Bass proposals, onset-refinement q60, subdivision q55, and event-step q95.
- V164 timebase builder preserves exact frozen V162 beat/phase/source logic and substitutes only V164 subdivision-lattice logic. It has not run.
- V164 timebase QC independently recomputes the V164 subdivision lattice while preserving frozen V162 source/beat/QC criteria. It has not run; PASS remains required before pitch.
- V164 transcriber uses count-checked frozen-V162 source adaptation. Only the two onset-admission support sites become V164 local q95; `onsetNormalization` is carried, locality-sensitive helpers are patched to V164, and Bass rows carry `proposalNormalization`. No unrelated pitch/register/RMS/activity/admission/cap numeric is changed.
- V164 structural QC adapts exact frozen V162 structural QC, then independently verifies full V164 step-selection metadata, local support/provenance, onset-refinement populations, source/cap constraints, hash chains, one-run proof and safety.
- JSON-native fixture tests NumPy normalization plus V164 local-provenance/support metadata, exact round-trip, finite `[0,1]` support semantics and NaN/Inf rejection.
- Negative runtime guard AST/source-checks all static boundaries and exact frozen dependencies, and rejects reference/scorer/V163 artifact paths.

## V164 static preflight — SEALED / NOT DISPATCHED
- Workflow: `.github/workflows/v164-static-preflight.yml`.
- Initial commit `c885043320a12eb08da0213154068647c215e5c8`; hardened commit `91c52c55fbb42af8d69ed9262cba0143fcf65737`.
- Sealed workflow blob `b8d1d2d7236488974f4dc5431ce42cc380257a98`.
- Pre-dispatch checkpoint/branch head confirmed before this note: `4d17038b3a96c777ccf64b9a66aa3b689e7b598f`.
- Manual `workflow_dispatch` only; job runs only on `refs/heads/v143-contextual-prune-lobo`; `contents: read`; no branch-write step; `ubuntu-latest`; Python `3.11`; pinned static dependency `numpy==2.0.2`.
- Workflow syntax-compiles V164 implementation/guard files, then executes **only** `test_event_logic_v164.py`, `test_json_native_v164.py`, and `negative-runtime-guard.py` (including workflow self-inspection).
- It does **not** execute timebase builder/QC, transcriber, structural QC runtime, song audio, Demucs, pitch, scorer/reference, V163 artifacts, GPU/CUDA/Modal.

## Dispatch capability note
- The connected GitHub tools in this session expose workflow/job/run inspection and rerun operations but **do not expose a first-time `workflow_dispatch` action**.
- The available browser automation executable is not present in this runtime, so the GitHub UI could not be used as a fallback.
- Therefore the sealed preflight was intentionally **not** altered to add an automatic trigger and was **not** run. This preserves the preregistered manual/static boundary.

## Current V164 execution counters
- Static-preflight runs: `0`.
- Song audio reads: `0`.
- Demucs/pitch inference: `0`.
- V164 candidate generations: `0`.
- Professional-reference/scorer reads for V164: `0`.
- V163 candidate/score reads for V164: `0`.
- GPU/CUDA/Modal: `0`.
- `main`/Production modifications: `0`.

## Hard boundary — NEXT
1. Never reopen V163 for tuning/scoring.
2. Manually dispatch the exact sealed `V164 CPU Static Preflight` workflow on branch `v143-contextual-prune-lobo` **without modifying the workflow or V164 implementation files first**.
3. Once dispatched, make **zero branch writes while the workflow is active**; inspect only run/job/step/log status.
4. If PASS: checkpoint run ID, run number/attempt, job ID, head SHA and exact static outputs. Then separately build/seal V164 pre-run identity + CPU environment receipts before any song processing.
5. If FAIL: do not process song audio. Record the exact static failure; repair only static implementation defects under frozen contract blob `098f24282b59abba0f7cffa0793b344b76701724`; checkpoint before any fresh preflight attempt.
6. No V164 song processing until static-preflight PASS and pre-run identity are separately sealed.
7. No GPU/Modal/CUDA without fresh explicit authorization.
