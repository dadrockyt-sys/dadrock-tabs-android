# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V163 is terminal/consumed and failed its sole preregistered professional-reference score gate. Never rerun/rearm/repair/retune/regenerate/re-QC/rescore V163 and do not advance it to role/string/fret/technique/PDF. V164 is preregistered, its exact local-evidence numeric contract is sealed, and all planned version-isolated implementation/static-guard code is now present: event/subdivision logic + synthetic regressions, frozen-V162 timebase builder + independent timebase QC adapters, CPU transcriber, independent structural QC, JSON-native local-provenance fixture, and negative runtime guard. No V164 song processing, scorer/reference read, pitch inference, static workflow run, candidate, or GPU execution exists.**

## Standing safety
- CPU-only reference-free work authorized at assistant discretion.
- Fresh explicit authorization required immediately before Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159/V160/V161/V162/V163 generation versions closed forever; V163 score opportunity closed forever.
- No professional-reference event/measure mining, candidate repair, score-informed retune, threshold sweep, variant selection, human correction, or second V163 score.
- V163 aggregate score was observed before V164 preregistration. V164 does **not** claim reviewer score-blindness; V164 design/numerics are explicitly quarantined from V163 score/reference evidence.
- No GPU/Modal/CUDA without fresh explicit authorization.

## V163 frozen terminal facts
- Generation run `33213512389`, #1 attempt #1, job `98991933938`; terminal generation commit `3b6f98750291a2f7b229c5e50cbf802752cf84d4`; `STRUCTURAL_QC_PASS`.
- Candidate blob `f4eafb1488f139198cb7860a76f294c0e1775df8`; SHA256 `cc55d596a05bd8e9c0a149f6ba8263375c26fbb7334139a75697b58ca23c8c19`; Guitar `1041`, Bass `404`.
- Structural-QC blob `35624b8bfbb3580573bb49bd12049726ee364977`; SHA256 `ae899558f436c872e3a3ee306463fe62163652497f96d36cea2558be27aa2337`; PASS.
- Sole score run `33214223643`, #1 attempt #1, job `98994146394`; terminal score commit `7bd8c813cac506811e3c144e5efe9edcd3abc561`; score workflow self-deleted.
- Score terminal blob `b7e6634d67b89632389f2be3edfdbe0162ff98dd`; `SCORE_GATE_FAIL`; Guitar primary F1 `0.059983566146261304`, Bass `0.21661409043112514`, gates `0.80/0.80`; score opportunity consumed forever.
- Score report blob `d10ae33aba35afd2547f94a3ec3dcd8443972fcf`; SHA256 `b87e745d1b3dafea2e99b841e8af028c55f8749341e5736fa5ec488ebf66cfd9`.

## V164 preregistration + numeric contract — FROZEN
- Prereg `debug/v164-cpu-autonomous/preregistration.json`: commit `1f0b4a904227491cbd5c62039d1ecbd500453966`, blob `05d255d75a6c1947891fba38d96d9399e3f75f9c`, PASS before numerics/code.
- Numeric contract `debug/v164-cpu-autonomous/implementation-contract.json`: commit `174a1c3850b4eb30335c9afd0e0ada776de37a3b`, blob `098f24282b59abba0f7cffa0793b344b76701724`, PASS before implementation code.
- Allowed design evidence only: V162 contract blob `409da313ed03a6c232d6578d48b0da6aa35b000b`, event logic blob `9f9b33fd8c210ad581025b454cf69b6999aa544b`, song-blind fixture blob `e301f38db66f44193d799a9c1a02c99169823d45`.
- V163 score/reference/candidate rows and same-song behavior forbidden as V164 design evidence.
- Event-local onset evidence: half-window `32` frames inclusive/clipped, up to `65` frames; finite positives only; q95 support; no-positive support `0.0`/threshold `null`.
- Beat-local subdivision q55 and event-step q95 support populations only; all V162 thresholds/weights/pitch/segmentation/register/admission/caps remain frozen.
- Invariance factors: remote `1,000,000×`; local `0.1×` and `10×`; rel/abs tolerance `1e-12`.

## V164 event/subdivision layer
### `validation/v164_cpu_autonomous/event_logic_v164.py`
- Integrated locality commit `20e04b71257fc01c55ba2ba611bfed8ee712306b`.
- Current blob `62303877a1971f75cacda002c5ad921680161674`.
- Pins frozen V162 event logic blob `9f9b33fd8c210ad581025b454cf69b6999aa544b` at import; drift is terminal.
- Reuses only unaffected V162 pure helpers (recovery score, register context/selection, Bass median/state lookup, grid caps).
- V164-localized paths: supported attacks, Guitar segmentation/recovery, Bass state-change/detected-onset/same-pitch support, onset-refinement q60, subdivision q55, event-step q95.
- Onset refinement preserves V162 radius and `1.10×` move rule; RMS/activity support intentionally remains unchanged/global because it is outside the onset/subdivision hypothesis.

### `validation/v164_cpu_autonomous/test_event_logic_v164.py`
- Expanded commit `9324944dfcafe67831970a092ed396b03788343f`.
- Current blob `13d29ef19a297d19469196cb2a23a4c0d6e040de`.
- Carries V162 song-blind regressions for Guitar segmentation/recovery/register, Bass state/proposals, Guitar/Bass grid caps.
- Adds V164 remote invariance for supported attack, onset refinement, Bass onset/proposals, subdivision and event-step; plus local-scale invariance, zero fallback, boundary clipping, nonfinite rejection.
- Expected static result schema `dadrock.tabs.v164.local-evidence-static-test.v2`; GitHub static preflight not yet run.

## V164 timebase builder — IMPLEMENTED / NOT EXECUTED
### `validation/v164_cpu_autonomous/build_timebase_v164.py`
- Initial commit `3b8ef985cc023040ee7084019cdfc05b31cfb21b`; import-path hardening commit `4f0c50431dc5401f5133d4ff075b6409bdfcc590`.
- Current Git blob `170a7a15d68e271d93775c2aaba058fe3ebaa8bb`.
- V164 schema `dadrock.tabs.v164.local-evidence-timebase.v1`.
- Pins frozen V162 builder blob `f7e9483aea16af770bcffe01ad8cfaf689d693b9` and V162 contract blob `409da313ed03a6c232d6578d48b0da6aa35b000b`.
- Runs the exact frozen V162 beat/phase/source logic only through an ephemeral compatibility contract and substitutes **only** V164 `build_subdivision_lattice`.
- Frozen V162 sibling import directory is exposed only during pinned-module load, then removed.
- Frozen builder writes only to ephemeral temp output; V164 wrapper writes final V164 timebase once after adding V164 implementation/safety provenance.
- Final safety explicitly records no reference, prior candidate/score, V163 candidate/score, or GPU reads.

## V164 independent timebase QC — IMPLEMENTED / NOT EXECUTED
### `validation/v164_cpu_autonomous/timebase_qc_v164.py`
- Creation commit `3fc416dc7e74946d89d4ad3ef0312199d9dda364`.
- Current Git blob `e59498e76d881f22ea405c81781ca2004ea8f53e`.
- V164 QC schema `dadrock.tabs.v164.local-evidence-timebase-qc.v1`.
- Pins frozen V162 QC blob `78acc9fd626039801011d039cca12686b72369c0` and V162 contract blob `409da313ed03a6c232d6578d48b0da6aa35b000b`.
- Independently recomputes V164 subdivision lattice using V164 `build_subdivision_lattice`/`extrapolated_final_beat` while preserving all frozen V162 beat/source/QC criteria.
- Uses only ephemeral compatibility copies; final receipt points to and hashes the actual final V164 timebase and actual V164 prereg/contract.
- Safety explicitly records `pitchInferenceInvoked=false`, no reference/prior/V163 reads, GPU false.
- Timebase-QC PASS remains a hard prerequisite before any pitch inference.

## V164 transcriber — IMPLEMENTED / NOT EXECUTED
### `validation/v164_cpu_autonomous/transcribe_v164.py`
- Creation commit `73d952258aafcfc6e875514936099c812458096a`; Bass local-provenance propagation commit `75c048ff07099d41c5eb376d92d733ad2399767a`.
- Current Git blob `df1302216df404bc3368ff820f005d6b63ae100d`.
- V164 candidate schema `dadrock.tabs.v164.local-evidence-generated.v1`; generation receipt schema `dadrock.tabs.v164.cpu-generation-receipt.v1`.
- Pins exact frozen V162 transcriber blob `fa163cafe2131aa73cdbb50df10d4e4912cff53b`, V162 event-logic blob `9f9b33fd8c210ad581025b454cf69b6999aa544b`, and V162 numeric-contract blob `409da313ed03a6c232d6578d48b0da6aa35b000b`.
- Uses count-checked frozen-source adaptation so unchanged V162 audio/pitch/CQT/admission machinery remains exact; only the two onset-admission support sites are changed to V164 event-local q95 and annotated with local normalization provenance.
- Patches locality-sensitive runtime helpers to V164 segmentation/recovery/Bass proposals/onset refinement/event-step selection while preserving V162 register, pitch, RMS/activity, admission, and cap numerics.
- Bass candidate rows now carry `proposalNormalization` bounds emitted by the V164 proposal layer; this is provenance-only and does not change any selection/admission numeric.
- Runtime boundary requires exact V164 prereg/contract/timebase/timebase-QC/pre-run/environment identities; timebase-QC PASS is checked before any pitch inference path can execute.
- Candidate/receipt safety includes no reference/scorer, prior candidate/score, V163 candidate/score, GPU/Modal, threshold sweep, variant selection, or human correction.

## V164 structural QC — IMPLEMENTED / NOT EXECUTED
### `validation/v164_cpu_autonomous/structural_qc_v164.py`
- Creation commit `bba784a311653c4214b957d28f861aed4cbbd20d`.
- Current Git blob `c1a81c7a97e646398f5e50cbc63dae341cdc500b`.
- V164 schema `dadrock.tabs.v164.reference-blind-structural-qc.v1`.
- Pins exact frozen V162 structural-QC blob `b7d3fa92fc9f3bed00931d19097e08cd91eab62b` and V162 numeric-contract blob `409da313ed03a6c232d6578d48b0da6aa35b000b`.
- Preserves the frozen V162 candidate/hash-chain, one-run proof, source/cap, lattice recomputation, event-step recomputation, safety and JSON-native receipt checks through count-checked adaptation.
- Adds V164 independent full `stepSelection` metadata recomputation at `1e-12`, onset-refinement local-window/positive-count recomputation, event-local q95 admission-support recomputation, local support-scale/provenance checks, recovery/Bass proposal bounds, V164 source-path assertions, and V163/reference/timebase-QC-before-pitch safety checks.
- Requires all sealed `structuralQcRequirements` flags from the V164 contract and exact frozen V162 dependency pins.
- Structural QC has not been run on song/candidate data because no V164 song run or candidate exists.

## V164 JSON-native fixture — IMPLEMENTED / NOT EXECUTED
### `validation/v164_cpu_autonomous/test_json_native_v164.py`
- Creation commit `9ed814225224197b3cf3deee48e8faa95c8b7560`.
- Current Git blob `a0b525485bbea933004045622bbf8c63527f123b`.
- Pins exact frozen V162 JSON-native fixture blob `654557363745f580f425252395542e9fb91adaad`.
- Exercises the adapted structural-QC `json_native` boundary with NumPy scalars/arrays plus V164 `onsetNormalization`, `proposalNormalization`, finite support-scale and normalized `[0,1]` support metadata.
- Requires exact JSON round-trip, no remaining NumPy types, deterministic integer/range semantics, and rejection of NaN/Inf.
- Explicit static safety reports no song audio, Demucs, pitch, reference/scorer, V163 candidate/score, prior score, or GPU use.

## V164 negative runtime guard — IMPLEMENTED / NOT EXECUTED
### `debug/v164-cpu-autonomous/negative-runtime-guard.py`
- Creation commit `8b4c3d42e774f1d7ea51b140eeefbba206fcb27f`.
- Current Git blob `230aa1efeb4640aabbb05720ead031e13cc57337`.
- Pins exact frozen V162 negative guard, event logic, transcriber, structural QC, JSON fixture and numeric-contract blobs.
- AST/source-checks V164 local/beat normalization implementation, synthetic invariance coverage, pre-pitch timebase/QC wrappers, transcriber QC-before-pitch + count-checked local adaptation, structural local-evidence recomputation, JSON-native provenance handling, and forbidden reference/scorer/V163 artifact paths.
- Optional workflow guard requires manual `workflow_dispatch`, CPU/static fixture commands, and forbids direct execution of timebase builder/QC, transcriber or structural QC with runtime arguments.
- Explicit guard safety is song/audio/pitch/reference/scorer/V163/GPU blind.

## Current V164 execution state
- Preregistration: sealed.
- Numeric contract: sealed.
- Event/subdivision layer: implemented.
- Synthetic regression/invariance suite: implemented, not run in GitHub preflight yet.
- Timebase builder: implemented, not executed.
- Independent timebase QC: implemented, not executed.
- V164 transcriber: implemented, not executed.
- V164 structural QC: implemented, not executed.
- V164 JSON-native fixture: implemented, not executed.
- V164 negative runtime guard: implemented, not executed.
- GitHub static preflight workflow: not created/armed/run yet.
- Song audio reads `0`; Demucs/pitch inference `0`; V164 candidate `0`; professional-reference/scorer reads for V164 `0`; V163 candidate/score reads for V164 `0`; GPU/CUDA/Modal `0`; main/Production unchanged.
- V164 prereg/contract do not authorize professional-reference scoring.

## Hard boundary — NEXT
1. Never reopen V163 for tuning/scoring.
2. Continue V164 only from frozen contract blob `098f24282b59abba0f7cffa0793b344b76701724`.
3. Create `.github/workflows/v164-static-preflight.yml` as manual one-shot CPU-only static validation: syntax-compile V164 implementation files; run only `test_event_logic_v164.py`, `test_json_native_v164.py`, and `negative-runtime-guard.py`; do not execute timebase builder/QC, transcriber, structural QC, song audio, Demucs, or pitch.
4. Checkpoint the exact workflow blob and branch head before manually dispatching the preflight. Make **zero branch writes while that workflow is active**.
5. If static preflight is not PASS, do not process song audio; fix only static implementation defects, reseal/checkpoint, and run a fresh static-preflight attempt under the contract boundary.
6. No V164 song processing until static preflight PASS and pre-run identity are separately sealed.
7. No GPU/Modal/CUDA without fresh explicit authorization.
