# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V159 is terminal/consumed forever. V160 preregistration and numeric implementation contract remain sealed. All five V160 Python modules now exist: timebase builder, independent pre-pitch timebase QC, frozen-timebase transcriber, JSON-safe structural QC, and song-blind JSON serializer test. V160 preserves V159 reference-blind generation/timebase/pitch numerics unchanged in substance; only version/schema/contract-layout wiring plus the preregistered independent-QC JSON serialization hardening were changed. Negative runtime guard and song-blind static-preflight workflow remain. No V160 song audio, Demucs, timebase, timebase QC, pitch inference, candidate, structural receipt, or score has run. Professional-reference reads/score calls remain 0; GPU/Modal/CUDA remain 0; main/Production remains untouched.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; generation/transcription/postmortem/successor implementation must not read them.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Never retune/correct/select a replacement for a consumed scored candidate.
- **V159 is closed forever: no re-arm, replay, regeneration, structural-QC rerun, repair-in-place, or score.**
- No V160 reference/scorer/prior-candidate/prior-score reads during implementation/generation/QC.
- No branch writes while an eventual one-shot V160 generation workflow is active.
- Target remains fully automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Immutable shared identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Historical audio commit `74b0f815ff3f66f325220975c410621503de440f`.
- Audio SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; bytes `3478611`.
- Normalized WAV SHA256 `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`; blob `9644e65719fbd361a9b39778ae9950c5e983e855` — scoring only.
- Frozen professional reference `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; blob `2fbed60b543c0488934d8642c488aa06bf31bbf5` — scoring only.
- Front-end score gates remain Guitar timing-aware pitch F1 >= `0.80` and Bass >= `0.80` before later role/string/fret/technique/PDF work.

## Closed historical versions
- V154: one score forever; Guitar `0.04915390813859791`, Bass `0.1116751269035533`; failed.
- V155: invalid duplicate generation; score count 0 forever.
- V156: aborted before candidate; score count 0 forever.
- V157: one score forever; Guitar `0.07692307692307694`, Bass `0.05757575757575757`; failed.
- V158: one score forever; Guitar `0.007756948933419521`, Bass `0.001976284584980237`; failed/consumed.
- **V159: one generation run forever; score count 0 forever; terminal `STRUCTURAL_QC_RUNTIME_FAIL`; candidate non-authoritative/ineligible for scoring; never re-arm.**

## V159 terminal evidence
- One-shot run ID `33195994387`, run #1 attempt #1, job `98933144549`; CPU-only.
- Fresh `htdemucs_6s` PASS; V159 timebase created with `448` detected beats and selected phase `1`.
- Independent timebase QC PASS, failed checks `[]`; receipt SHA256 `d8b5337d884258aaa9d9f3a3ed48493396e226077f480db0b56bca9e60ba2a01`.
- Candidate created once after timebase QC PASS; SHA256 `a2057b0f160f8f689ea7593acb277e8a6c56325ef3183cfef58e7196907fb36c`; combined Guitar `2276`, Bass `460`.
- Structural QC crashed before receipt write: `TypeError: Object of type bool_ is not JSON serializable`.
- Terminal freeze commit `e0ab58ef5766f6c1515453c05b80e86429140acb`; `debug/v159-cpu-autonomous/terminal-freeze.json` blob `e3cb31788a87921ed7ebc44db1f523e6e081e9b8`.
- Terminal outcome `STRUCTURAL_QC_RUNTIME_FAIL`; `candidateAuthoritative=false`; `eligibleForProfessionalReferenceScoring=false`; `neverRearmV159=true`.
- V159 reference reads 0; score calls 0; GPU/CUDA/Modal false; main/Production untouched.

## V159 serializer postmortem — FROZEN
- `debug/v159-cpu-autonomous/post-terminal-structural-runtime-diagnosis.json`; commit `1cb558d2865f96739ab5c9ef513d15c4d09f5ba4`; blob `95d89bec0c7571e84d945d812f968909ad475c39`.
- `debug/v159-cpu-autonomous/post-run-implementation-diagnosis.json`; commit `4094f636ee6ab13f6eca8d43b19823f845b143b0`; blob `6d01cd2b6f8f3f9df52277904b0f892df9ba8fc0`.
- Proven root cause: `checks["frozenGrid"]` ended in `np.all(np.diff(steps) == 4.0)`. Python `and` returned the final `numpy.bool_`; aggregate `bool()` coercion did not mutate raw checks; raw checks reached `json.dumps`.
- No professional reference/scorer/prior score/candidate-quality comparison was used.

## V160 preregistration — SEALED BEFORE IMPLEMENTATION
- `debug/v160-cpu-autonomous/preregistration.json`.
- Seal commit `0ab352eb781e31eb21d7329d6f08d894af02471a`; Git blob `cc238bcbf62c5defec410def962124d5012bd506`.
- Schema `dadrock.tabs.v160.reference-blind-cpu-preregistration.v1`; status `PREREGISTERED_BEFORE_IMPLEMENTATION_CODE`.
- V159 terminality preserved; V159 candidate may not be reused, re-QC'd, or scored.
- Fresh source materialization, normalization, Demucs, timebase, timebase QC, pitch inference, structural QC all required.
- Single fresh CPU generation run only; workflow creation sole trigger; second arm forbidden.
- V159 generation numerics carried forward unchanged in substance.
- Only permitted repair class: independent-QC JSON serialization hardening plus mandatory song-blind static coverage.

## V160 numeric implementation contract — SEALED BEFORE IMPLEMENTATION
- `debug/v160-cpu-autonomous/implementation-contract.json`.
- Seal commit `242fb649f0c01887d4de7961bb32c3d47de7ad7d`; Git blob `3d5ef47a998b638683c83ae08c92e45d5422f389`.
- Schema `dadrock.tabs.v160.numeric-implementation-contract.v1`; status `SEALED_BEFORE_IMPLEMENTATION_CODE`.
- Canonical schemas/paths frozen for timebase, timebase QC, candidate, generation/environment/structural/pre-run receipts and terminal freeze.

### V160 generation numerics — SEALED
- CPU dependencies: Python 3.10.x; `torch==2.8.0+cpu`; NumPy 1.26.4; SciPy 1.13.1; SoundFile 0.12.1; Basic Pitch 0.4.0; Demucs 4.1.0; imageio-ffmpeg 0.6.0; librosa 0.11.0.
- Fresh `htdemucs_6s`, CPU, shifts1/jobs1/repeat1; seed0; Torch threads/inter-op1; deterministic algorithms; math-library threads1.
- Timebase: SR22050/hop256; finite nonnegative positive-unit onsets; fused `0.5*unitMix+0.5*unitDrums`; beat start120/tightness100/sparse; RuntimeWarning fatal; >=8 beats; BPM 30..300; ratio 0.5..2.0; frozen static phase evidence/prefix/sequential-grid rules.
- Pitch unchanged: harmonic template 36 bins/octave, harmonics1..5 weights `[1,.5,.3333333333,.25,.2]`, radius1; Bass MIDI28..67 with frozen onset/pYIN/harmonic rules; Guitar MIDI40..88 with frozen Basic Pitch/persistent/register-repair rules.

### V160 JSON-native QC contract — SEALED
- Structural PASS/FAIL computed from original logical checks before normalization.
- `native_checks = {key: bool(value) for key, value in checks.items()}` goes into structural receipt.
- Recursive `json_native(value)`: native null/str/bool/int unchanged; native float finite-only; `numpy.generic -> .item()` recursively; ndarray -> `.tolist()` recursively; list/tuple -> list recursively; dict keys must be native strings; unsupported type raises.
- Serialization `json.dumps(..., indent=2, sort_keys=True, allow_nan=False)` + newline.
- Static fixture must reproduce raw V159 `numpy.bool_` failure then prove normalization and nonfinite rejection.

## V160 implementation progress — SAVED
- `validation/v160_cpu_autonomous/structural_qc_v160.py`
  - Introduced commit `6ff0ddd070e09395d76e04a0810d195d0812cd1d`; Git blob `679047e1e26b7ab4dff765dd05745317ce3f43e2`.
  - V159 structural event/hash/source/safety checks preserved in substance.
  - `frozenGrid` native bool; native check map; recursive `json_native()`; `allow_nan=False`.
- `validation/v160_cpu_autonomous/test_json_native_v160.py`
  - Commit `d49732b74cb59ab7fef73b5722434a1fb877fabe`; Git blob `f2cc178c4b6a6a771a0c8f8b1527d9742f13126e`.
  - Song-blind control reproduces V159 failure; tests NumPy scalar/array/nested normalization, exact round trip, and NaN/Inf rejection.
- `validation/v160_cpu_autonomous/build_timebase_v160.py`
  - Commit `d188c40a5bcc312f506729e7b9103a5e3c9b3c6a`; Git blob `b5aa459381da6a5d5379ed8bdb1a07ba26467b63`.
  - Semantic V159 timebase copy; V160 schemas/version messages and V160 contract-layout/source-identity lookups only.
  - Beat envelope, tracker, phase, prefix, ordinal, grid, warning rules unchanged.
- `validation/v160_cpu_autonomous/timebase_qc_v160.py`
  - Commit `dc1c8fe71ccb1a02894d95281dd2a5c28a51f052`; Git blob `a2dba655709572d5c50dd8d4ec8656fa96eb03a3`.
  - Independent pre-pitch QC preserved; V160 contract-layout lookups only plus native bool check map.
  - No pitch imports/calls.
- `validation/v160_cpu_autonomous/transcribe_v160.py`
  - Commit `9448c553b5ab4f11502be1a4267a3bae4d983358`; Git blob `864f0da266816e999cd6c2750dbceb27e870b67a`.
  - Semantic V159 pitch/event logic copy with V160 schemas/version/identity wiring only.
  - Bass/Guitar pitch thresholds, harmonic scoring, register repair, durations, dedupe/source precedence, and frozen-grid mapping unchanged.
  - `validate_runtime_boundary(args)` proves exact V160 timebase + independent QC `PASS`, pre-run pins, CPU environment, stem identities, and reference-blind safety before `bass_events()` or `guitar_events()` can run.
  - Candidate remains `PENDING_INDEPENDENT_STRUCTURAL_QC` until independent V160 structural QC.

## Validation status
- **No V160 song audio processing has run.**
- No V160 Demucs, timebase artifact, timebase-QC receipt, pitch inference, candidate, generation receipt, structural receipt, or score exists.
- V160 serializer test has not yet been executed by a trusted static workflow.
- No syntax/static PASS has yet been claimed for the full V160 implementation.
- Local sandbox cannot resolve github.com, so repository cloning/static execution there is unavailable and must not be falsely marked PASS.
- Professional-reference reads in V160 work: 0. Score calls: 0. GPU/Modal/CUDA: 0. main/Production modifications: 0.

## Current hard boundary
- V159 closed forever.
- V160 preregistration + implementation contract sealed; do not alter their semantics based on later output.
- Do not read V159 runtime artifacts from V160 generation.
- No pitch inference before fresh V160 timebase-QC PASS.
- Only a fresh V160 candidate with independent structural-QC PASS may become authoritative/scoring-eligible.
- No GPU/Modal/CUDA without fresh explicit user authorization.
- Never touch `main`/Production without explicit user direction.

## Exact next steps — RESUME HERE
1. Re-fetch branch head/checkpoint before every write.
2. Implement `debug/v160-cpu-autonomous/negative-runtime-guard.py` covering professional-reference/scorer/prior-version runtime leakage, pre-pitch pitch imports/calls, transcriber timebase-QC ordering, V160-only schemas/paths, and the JSON-native structural/static-test contract.
3. Add `.github/workflows/v160-static-preflight.yml`: song-blind only; compile all V160 Python files, run negative runtime guard, run `test_json_native_v160.py`, and prove no V160 generation artifacts/workflow exist. Install only NumPy 1.26.4 for the serializer test if needed; do not materialize song audio or install/run Demucs/Basic Pitch/librosa for preflight.
4. Run V160 static preflight exactly once and resolve implementation-only defects without changing sealed numerics.
5. Freeze final V160 code/blob identities and create `dadrock.tabs.v160.pre-run-identity-receipt.v1`, proving generation artifacts/workflow absent and reference/score/GPU counts zero.
6. Reviewer-audit the one-shot CPU generation workflow before creation. Creation is sole trigger; no branch writes while active; run number/attempt must equal 1.
7. Fresh CPU workflow order: source identity → normalize → fresh `htdemucs_6s` → environment receipt → timebase → independent timebase QC. QC FAIL terminal/no candidate. PASS → transcriber → independent structural QC. Structural FAIL/runtime FAIL terminal/no score. PASS → candidate authoritative.
8. Only after structural PASS separately preregister/seal exactly one professional-reference scoring run.
9. Fresh explicit authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
