# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V159 is terminal/consumed forever. V160 preregistration + numeric implementation contract + implementation identities remain sealed. The V160 static preflight is consumed/PASS. The immutable nested pre-run identity receipt remains sealed at commit `97333e9533b5ab4d40d2f29c31cfab771fa1e3e9`, blob `699dda80f25e0222dc7ef2f857fa65327f2d49db`, and its runtime-compatible flat projection remains sealed at commit `c27f19c2bcb07b7b45342cecede56cee8ebbf6be`, blob `a1cd82c8c5b5dc150d051b3f013ff4eb208b36a8`. The proposed V160 one-shot CPU generation workflow has now passed reviewer audit without being created. `.github/workflows/v160-generate.yml` still does not exist and no V160 song processing has run. Next: re-fetch branch/checkpoint, prove the generation workflow and all runtime artifacts are still absent, substitute that exact checkpoint commit as the workflow's expected parent, re-audit that exact substitution, and create the workflow exactly once. That single creation commit is the sole V160 generation arm. Professional-reference reads/score calls remain 0; GPU/Modal/CUDA remain 0; main/Production remains untouched.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; generation/transcription/postmortem/successor implementation must not read them.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Never retune/correct/select a replacement for a consumed scored candidate.
- **V159 is closed forever: no re-arm, replay, regeneration, structural-QC rerun, repair-in-place, or score.**
- No V160 reference/scorer/prior-candidate/prior-score reads during implementation/generation/QC.
- No assistant/manual branch writes while the eventual one-shot V160 generation workflow is active.
- Target remains fully automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Immutable shared identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Historical audio commit `74b0f815ff3f66f325220975c410621503de440f`.
- Audio SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; bytes `3478611`.
- Normalized WAV SHA256 `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`; blob `9644e65719fbd361a9b39778ae9950c5e983e855` — scoring only.
- Frozen professional reference `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; blob `2fbed60b543c0488934d8642c488aa06bf31bbf5` — scoring only.
- Front-end score gates remain Guitar timing-aware pitch F1 >= `0.80` and Bass >= `0.80` before role/string/fret/technique/PDF work.

## Closed historical versions
- V154: one score forever; Guitar `0.04915390813859791`, Bass `0.1116751269035533`; failed.
- V155: invalid duplicate generation; score count 0 forever.
- V156: aborted before candidate; score count 0 forever.
- V157: one score forever; Guitar `0.07692307692307694`, Bass `0.05757575757575757`; failed.
- V158: one score forever; Guitar `0.007756948933419521`, Bass `0.001976284584980237`; failed/consumed.
- **V159: one generation run forever; score count 0 forever; terminal `STRUCTURAL_QC_RUNTIME_FAIL`; candidate non-authoritative/ineligible for scoring; never re-arm.**

## V159 terminal evidence / frozen postmortem
- V159 one-shot run ID `33195994387`, run #1 attempt #1, job `98933144549`, CPU-only.
- Fresh `htdemucs_6s` PASS; timebase `448` detected beats, selected phase `1`; independent timebase QC PASS.
- Candidate created once, SHA256 `a2057b0f160f8f689ea7593acb277e8a6c56325ef3183cfef58e7196907fb36c`; Guitar `2276`, Bass `460`.
- Structural QC crashed before receipt write: `TypeError: Object of type bool_ is not JSON serializable`.
- Terminal freeze commit `e0ab58ef5766f6c1515453c05b80e86429140acb`; `terminal-freeze.json` blob `e3cb31788a87921ed7ebc44db1f523e6e081e9b8`; candidateAuthoritative=false; scoringEligible=false; neverRearmV159=true.
- Frozen diagnoses: `post-terminal-structural-runtime-diagnosis.json` commit `1cb558d2865f96739ab5c9ef513d15c4d09f5ba4`, blob `95d89bec0c7571e84d945d812f968909ad475c39`; `post-run-implementation-diagnosis.json` commit `4094f636ee6ab13f6eca8d43b19823f845b143b0`, blob `6d01cd2b6f8f3f9df52277904b0f892df9ba8fc0`.
- Proven root cause: `checks["frozenGrid"]` ended in `np.all(...)`; Python `and` returned `numpy.bool_`; raw checks reached `json.dumps`.
- V159 reference reads 0; score calls 0; GPU/CUDA/Modal 0; main/Production untouched.

## V160 sealed preregistration / numeric contract
- Preregistration: `debug/v160-cpu-autonomous/preregistration.json`; seal commit `0ab352eb781e31eb21d7329d6f08d894af02471a`; blob `cc238bcbf62c5defec410def962124d5012bd506`; schema `dadrock.tabs.v160.reference-blind-cpu-preregistration.v1`; status `PREREGISTERED_BEFORE_IMPLEMENTATION_CODE`.
- Numeric contract: `debug/v160-cpu-autonomous/implementation-contract.json`; seal commit `242fb649f0c01887d4de7961bb32c3d47de7ad7d`; blob `3d5ef47a998b638683c83ae08c92e45d5422f389`; schema `dadrock.tabs.v160.numeric-implementation-contract.v1`; status `SEALED_BEFORE_IMPLEMENTATION_CODE`.
- V159 terminality preserved; V159 candidate may not be reused, re-QC'd, or scored.
- V159 reference-blind generation numerics carried forward unchanged in substance.
- Only permitted V160 implementation repair class remains independent-QC JSON serialization hardening + song-blind static coverage.

### V160 sealed generation numerics
- Python 3.10.x; `torch==2.8.0+cpu`; NumPy 1.26.4; SciPy 1.13.1; SoundFile 0.12.1; Basic Pitch 0.4.0; Demucs 4.1.0; imageio-ffmpeg 0.6.0; librosa 0.11.0.
- Fresh `htdemucs_6s`; CPU; shifts1/jobs1/repeat1; seed0; Torch/math-library threads1; deterministic algorithms.
- Timebase: SR22050/hop256; finite nonnegative positive-unit onset envelopes; fused `0.5*unitMix+0.5*unitDrums`; beat start120/tightness100/sparse; RuntimeWarning fatal; >=8 beats; BPM 30..300; tempo ratio 0.5..2.0; frozen phase/prefix/sequential-grid rules; Python round; 16-step measure mapping.
- Pitch unchanged: 36 bins/octave; harmonics1..5 weights `[1,.5,.3333333333,.25,.2]`, radius1; Bass MIDI28..67 frozen onset/pYIN/harmonic rules; Guitar MIDI40..88 frozen Basic Pitch/persistent/register-repair rules.

### V160 sealed JSON-native QC repair
- Structural logical PASS/FAIL is computed before receipt normalization.
- `native_checks = {key: bool(value) ...}` goes into structural receipt.
- Recursive `json_native`: native null/str/bool/int unchanged; finite float only; `numpy.generic -> .item()` recursively; ndarray -> `.tolist()` recursively; list/tuple -> list; string-key dict recursively; unsupported/nonfinite values fail before write.
- Structural receipt uses `json.dumps(..., sort_keys=True, allow_nan=False)`.
- Mandatory fixture reproduces raw `numpy.bool_` JSON failure, then tests NumPy bool/int/float/array/nested normalization, exact round-trip, native bool checks, and NaN/Inf rejection.

## V160 final implementation identities
- `validation/v160_cpu_autonomous/build_timebase_v160.py` — commit `d188c40a5bcc312f506729e7b9103a5e3c9b3c6a`; blob `b5aa459381da6a5d5379ed8bdb1a07ba26467b63`.
- `validation/v160_cpu_autonomous/timebase_qc_v160.py` — commit `dc1c8fe71ccb1a02894d95281dd2a5c28a51f052`; blob `a2dba655709572d5c50dd8d4ec8656fa96eb03a3`.
- `validation/v160_cpu_autonomous/transcribe_v160.py` — commit `9448c553b5ab4f11502be1a4267a3bae4d983358`; blob `864f0da266816e999cd6c2750dbceb27e870b67a`.
- `validation/v160_cpu_autonomous/structural_qc_v160.py` — commit `6ff0ddd070e09395d76e04a0810d195d0812cd1d`; blob `679047e1e26b7ab4dff765dd05745317ce3f43e2`.
- `validation/v160_cpu_autonomous/test_json_native_v160.py` — commit `d49732b74cb59ab7fef73b5722434a1fb877fabe`; blob `f2cc178c4b6a6a771a0c8f8b1527d9742f13126e`.
- `debug/v160-cpu-autonomous/negative-runtime-guard.py` — commit `761ef8f2253c7330cc5e1da7eb8a98f9bd7a08c5`; blob `e6cd45c7d8bd23a92100847f3a219c84524cbbc2`.
- `.github/workflows/v160-static-preflight.yml` — arm commit `6e6cff4c73e1a951d4154f1ddbce8550576d8cbb`; blob `1e2e16a68f72c2f7265a584256fc2402049cf940`.

## V160 static preflight — PASS / CONSUMED
- Workflow `V160 static reference-blind preflight`.
- Run ID `33197726025`; run number `1`; attempt `1`; job `98939034732`; conclusion `success`; head `6e6cff4c73e1a951d4154f1ddbce8550576d8cbb`.
- Sealed preregistration and implementation-contract Git blobs matched exactly.
- NumPy `1.26.4` was the only serializer-test dependency explicitly installed by the workflow.
- All six V160 Python files compiled: builder, timebase QC, transcriber, structural QC, serializer test, negative guard.
- Negative runtime + serializer-contract guard: PASS.
- Song-blind JSON-native serializer fixture: PASS.
- Final absence proof: PASS; no V160 timebase/timebase-QC/candidate/generation/environment/structural/pre-run/terminal artifacts and no V160 generation workflow existed during the run.
- No song audio, Demucs, pitch inference, candidate generation, professional-reference read, score call, GPU/Modal/CUDA, or Production modification occurred.
- **Never rerun the V160 static preflight.**

## V160 immutable pre-run identity receipt — PASS / SEALED
- `debug/v160-cpu-autonomous/pre-run-identity-receipt.json`.
- Seal commit `97333e9533b5ab4d40d2f29c31cfab771fa1e3e9`; blob `699dda80f25e0222dc7ef2f857fa65327f2d49db`; schema `dadrock.tabs.v160.pre-run-identity-receipt.v1`; status/validation PASS.
- Receipt created while `.github/workflows/v160-generate.yml` and all V160 runtime artifacts were absent.
- Exact prereg/contract/builder/timebase-QC/transcriber/structural-QC/serializer-test/negative-guard/static-workflow Git blobs are frozen in the receipt.
- Consumed static preflight identity frozen: run `33197726025`, run #1 attempt #1, job `98939034732`, success, head `6e6cff4c73e1a951d4154f1ddbce8550576d8cbb`; never rerun.
- Receipt freezes expected generation run #1 attempt #1; second arm, duplicate run, rerun, and branch writes while generation is active are forbidden.
- Receipt records referenceRead=false; professional paths opened=0; score calls=0; frozen scorer read=false; GPU/CUDA/Modal executions=0; main/Production untouched.
- **This immutable nested receipt must not be edited.**

## V160 reviewer-audit control-plane projection — PASS / SEALED
- Audit finding: `transcribe_v160.py` and `structural_qc_v160.py` require flat pre-run keys (`pinnedGitBlobs`, `timebaseMustNotExistAtSeal`, `candidateMustNotExistAtSeal`, `generationReceiptMustNotExistAtSeal`, `referenceReadAtSeal`, `professionalReferencePathsOpenedAtSeal`) while the immutable identity receipt stores equivalent facts under nested sections.
- If generation had been armed with the nested receipt directly, the sealed transcriber would have rejected the pre-run boundary after expensive upstream CPU work. The reviewer audit therefore correctly blocked arming.
- Original sealed receipt was left untouched.
- Derived runtime projection: `debug/v160-cpu-autonomous/pre-run-runtime-envelope.json`; seal commit `c27f19c2bcb07b7b45342cecede56cee8ebbf6be`; blob `a1cd82c8c5b5dc150d051b3f013ff4eb208b36a8`; schema remains `dadrock.tabs.v160.pre-run-identity-receipt.v1`; validation PASS; status `DERIVED_RUNTIME_ENVELOPE_BEFORE_GENERATION`.
- Envelope pins the immutable source receipt blob `699dda80f25e0222dc7ef2f857fa65327f2d49db` and exposes the exact sealed code/input blobs expected by the transcriber and structural QC.
- Classification is control-plane schema projection only: original receipt modified=false; generation numerics/timebase/pitch/structural logic/code changed=false.
- At projection seal: songAudioRead=false; Demucs=false; pitchInference=false; professional reference/scorer/prior candidate/prior score/V159 runtime reads=false; GPU/CUDA/Modal=false; main/Production=false.
- The generation workflow must verify BOTH the immutable nested receipt blob and the runtime-envelope blob before processing and must pass the runtime envelope to sealed V160 transcriber/structural QC.

## V160 one-shot generation workflow reviewer audit — PASS / NOT ARMED
- Proposed workflow path: `.github/workflows/v160-generate.yml`; it has **not** been created during the audit.
- Proposed workflow is a single `push` path trigger on its own workflow file only; no `workflow_dispatch` or pull-request trigger.
- Guard requires `GITHUB_RUN_NUMBER=1`, `GITHUB_RUN_ATTEMPT=1`, exact `GITHUB_SHA`, exact expected parent, and exactly one changed path: `.github/workflows/v160-generate.yml`.
- Guard pins exact Git blobs for preregistration, numeric contract, immutable nested pre-run receipt, runtime pre-run envelope, builder, timebase-QC, transcriber, structural-QC, serializer fixture, negative guard, and consumed static-preflight workflow.
- Guard verifies all V160 runtime artifacts are absent before execution and statically runs the sealed negative runtime guard against the proposed workflow; no forbidden professional-reference/scorer or prior-version runtime paths are present.
- Guard mechanically cross-checks the runtime envelope against the immutable nested receipt: code pins, absence facts, reference-blind safety facts, one-shot trigger facts, and control-plane-only repair classification.
- Runtime dependency plan is CPU-only: Python 3.10, Torch `2.8.0+cpu` from the PyTorch CPU index, NumPy 1.26.4, SciPy 1.13.1, SoundFile 0.12.1, Basic Pitch 0.4.0, Demucs 4.1.0, imageio-ffmpeg 0.6.0, librosa 0.11.0; `CUDA_VISIBLE_DEVICES=""`; deterministic seed/thread settings remain sealed.
- Runtime order is sealed source materialization + identity check → deterministic normalized WAV + identity check → fresh CPU `htdemucs_6s` → CPU environment receipt → fresh timebase → independent timebase QC. Pitch inference is impossible until the independent timebase-QC receipt is frozen PASS.
- Timebase-QC FAIL freezes terminal V160 with no candidate. PASS alone permits transcriber. The transcriber and structural QC both receive `pre-run-runtime-envelope.json`; structural PASS alone marks the candidate authoritative/scoring-eligible.
- Structural FAIL/runtime FAIL or any other pipeline failure self-freezes V160 as terminal/non-authoritative/non-scoring and forbids rerun.
- Terminal step re-fetches the branch and requires it still equals the generation head, writes `terminal-freeze.json`, deletes the generation workflow, permits only V160 runtime artifact paths + workflow deletion in the self-seal commit, pushes exactly one bot terminal commit, and exits failure unless outcome is `STRUCTURAL_QC_PASS`.
- Proposed YAML parses successfully. Reviewer checklist for trigger, exact identities, CPU-only execution, source/normalization/Demucs/timebase/QC/pitch/structural ordering, reference isolation, terminal self-seal, and no-rerun semantics is PASS.
- The only value intentionally left for final substitution is `EXPECTED_PARENT_HEAD`. After this checkpoint commit becomes the branch head, substitute that exact SHA and re-run the same reviewer checks locally before creation. This parent substitution changes no runtime semantics.

## Validation status
- **No V160 song audio processing has run.**
- No V160 Demucs, timebase artifact, timebase-QC receipt, pitch inference, candidate, generation receipt, environment receipt, structural receipt, terminal freeze, or score exists.
- `.github/workflows/v160-generate.yml` does not exist yet.
- Static syntax/boundary/serializer validation PASS; immutable pre-run identity seal PASS; runtime projection PASS; proposed generation-workflow reviewer audit PASS.
- Professional-reference reads in V160 work: 0. Score calls: 0. GPU/Modal/CUDA: 0. main/Production modifications: 0.

## Current hard boundary
- V159 closed forever.
- V160 preregistration + implementation contract + immutable nested pre-run identity receipt + derived runtime envelope are sealed.
- Do not edit the immutable nested receipt. Do not change V160 generation numerics or sealed implementation code.
- Static preflight consumed/pass; do not rerun it.
- Generation workflow reviewer audit is PASS but the workflow is not armed yet.
- Generation must verify both pre-run seal blobs and use `pre-run-runtime-envelope.json` as the transcriber/structural-QC `--pre-run-receipt` input.
- Do not read V159 runtime artifacts from V160 generation.
- No pitch inference before fresh V160 timebase-QC PASS.
- Only a fresh V160 candidate with independent structural-QC PASS may become authoritative/scoring-eligible.
- No assistant/manual branch writes while the one-shot generation workflow is active. The workflow's own terminal self-seal commit is the only intended write during the run.
- No GPU/Modal/CUDA without fresh explicit user authorization.
- Never touch `main`/Production without explicit user direction.

## Exact next steps — RESUME HERE
1. Re-fetch branch head/checkpoint before the arm write.
2. Verify `.github/workflows/v160-generate.yml` is absent and runtime artifacts `environment-receipt.json`, `timebase.json`, `timebase-qc.json`, `generated.json`, `generation-receipt.json`, `structural-qc.json`, `terminal-freeze.json` are all absent.
3. Use the freshly fetched branch head as the workflow's exact `EXPECTED_PARENT_HEAD`, then re-run the reviewer checklist on that exact final workflow text. No other change is permitted.
4. Create `.github/workflows/v160-generate.yml` exactly once. **That creation commit is the sole V160 generation arm.**
5. After creation, perform no assistant/manual branch writes while the workflow is active. Read-only observation only.
6. Observe the sole workflow run to terminal completion and preserve workflow/run/job/head identities. Never rerun it.
7. After the workflow's own terminal self-seal commit lands, re-fetch terminal artifacts and update this checkpoint.
8. Only if terminal outcome is `STRUCTURAL_QC_PASS`, separately preregister/seal exactly one professional-reference scoring run. Do not score otherwise.
9. Fresh explicit authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
