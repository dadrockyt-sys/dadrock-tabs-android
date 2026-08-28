# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V159 is terminal/consumed forever. V160 is now preregistered and its numeric implementation contract is sealed before implementation. V160 carries the V159 reference-blind generation/timebase/pitch numerics forward unchanged in substance and changes only the independent-QC JSON serialization boundary. The V160 JSON-safe structural-QC module and mandatory song-blind serializer test are implemented. The unchanged V160 timebase builder, timebase QC, transcriber, negative runtime guard, static-preflight workflow, final static validation, code-identity seal, and one-shot generation workflow remain. No V160 song audio, Demucs, pitch inference, candidate, QC receipt, or score has run. Professional-reference reads/score calls remain 0; GPU/Modal/CUDA remain 0; main/Production remains untouched.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; generation/transcription/postmortem/successor implementation must not read them.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Never retune/correct/select a replacement for a consumed scored candidate.
- **V159 is closed forever: no re-arm, replay, regeneration, structural-QC rerun, repair-in-place, or score.**
- No V160 reference/scorer/prior-candidate/prior-score reads during implementation/generation/QC.
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
- Proven root cause: `checks["frozenGrid"]` ended in `np.all(np.diff(steps) == 4.0)`. Python `and` returned the final `numpy.bool_`; `passed = all(bool(value)...)` normalized only aggregate control flow, not raw `checks`; receipt embedded raw checks and `json.dumps` failed.
- No other direct NumPy scalar/array check assignment found in V159 structural QC.
- Diagnosis used no professional reference/scorer/prior score/candidate-quality comparison.

## V160 preregistration — SEALED BEFORE IMPLEMENTATION
- `debug/v160-cpu-autonomous/preregistration.json`.
- Seal commit `0ab352eb781e31eb21d7329d6f08d894af02471a`.
- Git blob `cc238bcbf62c5defec410def962124d5012bd506`.
- Schema `dadrock.tabs.v160.reference-blind-cpu-preregistration.v1`; status `PREREGISTERED_BEFORE_IMPLEMENTATION_CODE`.
- Explicitly preserves V159 terminality; V159 candidate may not be reused, re-QC'd, or scored.
- Fresh source materialization, normalization, Demucs, timebase, timebase QC, pitch inference, structural QC all required for V160.
- Single fresh CPU generation run only; workflow creation sole trigger; second arm forbidden.
- V159 generation numerics carried forward unchanged in substance.
- Only permitted repair class: independent-QC JSON serialization hardening plus mandatory song-blind static coverage.

## V160 numeric implementation contract — SEALED BEFORE IMPLEMENTATION
- `debug/v160-cpu-autonomous/implementation-contract.json`.
- Seal commit `242fb649f0c01887d4de7961bb32c3d47de7ad7d`.
- Git blob `3d5ef47a998b638683c83ae08c92e45d5422f389`.
- Schema `dadrock.tabs.v160.numeric-implementation-contract.v1`; status `SEALED_BEFORE_IMPLEMENTATION_CODE`.
- Canonical V160 schemas/paths frozen for timebase, timebase QC, candidate, generation/environment/structural/pre-run receipts and terminal freeze.
- V159 generation/timebase/pitch numerics preserved exactly in substance.

### V160 generation numerics — SEALED
- CPU dependencies: Python 3.10.x; `torch==2.8.0+cpu`; NumPy 1.26.4; SciPy 1.13.1; SoundFile 0.12.1; Basic Pitch 0.4.0; Demucs 4.1.0; imageio-ffmpeg 0.6.0; librosa 0.11.0.
- Fresh `htdemucs_6s`, CPU, shifts1/jobs1/repeat1; seed0; Torch threads/inter-op1; deterministic algorithms; math-library threads1.
- Timebase: SR22050/hop256; finite nonnegative positive-unit onsets; fused `0.5*unitMix+0.5*unitDrums`; beat start120/tightness100/sparse; RuntimeWarning fatal; >=8 beats; BPM 30..300; ratio 0.5..2.0; static four-phase evidence; prefix 0..3; sequential ordinal; grid `4*ordinal`; Python round; 16-step measure mapping.
- Pitch unchanged: harmonic template 36 bins/octave, harmonics1..5 weights `[1,.5,.3333333333,.25,.2]`, radius1; Bass MIDI28..67 with frozen onset/pYIN/harmonic rules; Guitar MIDI40..88 with frozen Basic Pitch/persistent/register-repair rules.

### V160 JSON-native QC contract — SEALED
- Structural PASS/FAIL computed from original logical checks before normalization.
- `native_checks = {key: bool(value) for key, value in checks.items()}` goes into receipt.
- Recursive `json_native(value)` rules: native null/str/bool/int unchanged; native float finite-only; `numpy.generic -> .item()` recursively; ndarray -> `.tolist()` recursively; list/tuple -> list recursively; dict keys must be native strings; unsupported type raises before write.
- Serialization `json.dumps(..., indent=2, sort_keys=True, allow_nan=False)` + newline.
- Mandatory static fixture must reproduce V159 raw `numpy.bool_` failure, then prove bool/int/float/array/nested normalization, native bool check values, exact round trip, and nonfinite rejection.

## V160 implementation progress — SAVED
- `validation/v160_cpu_autonomous/structural_qc_v160.py` introduced commit `6ff0ddd070e09395d76e04a0810d195d0812cd1d`; current Git blob `679047e1e26b7ab4dff765dd05745317ce3f43e2`.
  - V159 structural event/hash/source/safety checks preserved in substance.
  - `frozenGrid` explicitly coerced to native bool.
  - PASS/FAIL computed before serialization normalization.
  - native check map and recursive `json_native()` added.
  - `allow_nan=False` receipt serialization.
- `validation/v160_cpu_autonomous/test_json_native_v160.py` introduced commit `d49732b74cb59ab7fef73b5722434a1fb877fabe`; Git blob `f2cc178c4b6a6a771a0c8f8b1527d9742f13126e`.
  - Song-blind control reproduces V159 raw `numpy.bool_` `json.dumps` failure.
  - Tests NumPy bool/int/float/ndarray plus nested dict/list/tuple normalization.
  - Requires all synthetic structural checks to be native bool.
  - Requires exact JSON round trip and rejection of NaN/+Inf/-Inf.
  - Declares no audio, Demucs, pitch, reference, prior-candidate, or prior-score use.

## Validation status
- **No V160 song audio processing has run.**
- No V160 Demucs, timebase, timebase QC, pitch inference, candidate, generation receipt, structural receipt, or score exists.
- V160 structural serializer test has been added but has not yet been executed by a trusted static workflow.
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
2. Implement fresh V160 `build_timebase_v160.py`, `timebase_qc_v160.py`, and `transcribe_v160.py` as semantic copies of the sealed V159 generation logic with V160 schemas/paths only; no numeric drift and no V159 runtime imports/reads.
3. Implement `debug/v160-cpu-autonomous/negative-runtime-guard.py` covering reference/scorer/prior-version runtime leakage, pre-pitch import/call separation, transcriber timebase-QC ordering, and V160 JSON serializer/static-test contract.
4. Add `.github/workflows/v160-static-preflight.yml`: song-blind only; compile all V160 Python files, run negative runtime guard, run `test_json_native_v160.py`, and prove no V160 generation artifacts exist. Do not install project/audio dependencies beyond what the serializer test needs; NumPy pin may be installed for the test.
5. Run static preflight exactly once and resolve implementation-only defects without changing sealed V160 numerics.
6. Seal final code/blob identities and create V160 pre-run identity receipt proving generation artifacts/workflow absent and reference/score/GPU counts zero.
7. Reviewer-audit the one-shot CPU generation workflow. Creation is sole trigger; no branch writes while active; run number/attempt must equal 1.
8. Fresh CPU workflow order: source identity → normalize → fresh `htdemucs_6s` → environment receipt → timebase → independent timebase QC. QC FAIL terminal/no candidate. PASS → transcriber → independent structural QC. Structural FAIL/runtime FAIL terminal/no score. PASS → candidate authoritative.
9. Only after structural PASS separately preregister/seal exactly one professional-reference scoring run.
10. Fresh explicit authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
