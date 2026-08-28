# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V158 is permanently consumed/diagnosed. V159 reference-blind CPU preregistration and numeric implementation contract remain SEALED. V159 implementation is static-preflight PASS and the pre-run identity receipt is now SEALED. No V159 song audio processing, fresh Demucs separation, timebase, timebase-QC receipt, pitch inference, candidate, generation receipt, environment receipt, structural-QC receipt, or score has run/been produced. The one-shot CPU generation workflow does not exist yet. Professional-reference reads = 0; V159 reference-facing score calls = 0; GPU/Modal/CUDA executions = 0; main/Production modifications = 0.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; generation/transcription must not read them.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Never retune/correct/select a replacement for a consumed scored candidate.
- No branch writes while the eventual one-shot V159 generation workflow is active.
- Target remains fully automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Immutable song/reference identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Historical audio commit `74b0f815ff3f66f325220975c410621503de440f`.
- Audio SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; bytes `3478611`.
- Normalized WAV SHA256 `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`; blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference path `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`.
- Front-end gates: combined Guitar timing-aware pitch F1 >= `0.80` AND Bass >= `0.80` before role/string/fret/technique/PDF work.

## Closed historical versions
- V154: one score forever; Guitar `0.04915390813859791`, Bass `0.1116751269035533`; failed.
- V155: invalid duplicate generation; score count 0 forever.
- V156: aborted before candidate; score count 0 forever.
- V157: one score forever; Guitar `0.07692307692307694`, Bass `0.05757575757575757`; failed.
- **V158: one score forever; Guitar `0.007756948933419521`, Bass `0.001976284584980237`; failed/consumed; never modify/regenerate/rescore.**
- V158 frozen diagnosis: `debug/v158-cpu-autonomous/post-score-architecture-diagnosis.json`, freeze commit `8f2e03032cc5b323afd0b4668660199425bc585f`, blob `d7c5720b27f74f1f710b96a6b0da70569ae48bbc`.
- Proven V158 timebase failure: `2986` beats over ~`216.45s` ≈ `827.72 BPM`; signed robust-z beat envelope caused invalid `log1p`, and bar-phase Viterbi changed absolute ordinal/time scale. V158 score-derived pitch tuning remains forbidden.

## V159 sealed preregistration / numeric contract
- Preregistration: `debug/v159-cpu-autonomous/preregistration.json`; commit `6264131c2c515ae2ac9b7c64627cabc70382c825`; blob `2eca55dc344908a791ba7946f42d77fbd7b8926d`; schema `dadrock.tabs.v159.reference-blind-cpu-preregistration.v1`; status `PREREGISTERED_BEFORE_IMPLEMENTATION_CODE`.
- Numeric contract: `debug/v159-cpu-autonomous/implementation-contract.json`; commit `b8e8cba795c2aa0d7d3990265b2472af8d1d7e06`; blob `83dfee2d537d00dbced367bdbc467d167a96db2f`; schema `dadrock.tabs.v159.numeric-implementation-contract.v1`; status `SEALED_BEFORE_IMPLEMENTATION_CODE`.

### V159 timebase numerics — immutable
- SR `22050`, hop `256`; reject nonfinite onset arrays; clamp >=0; require positive max > `1e-12`; divide by max.
- Fused beat envelope = `0.5*unitMix + 0.5*unitDrums`.
- `librosa.beat.beat_track`: start BPM `120`, tightness `100`, sparse=true.
- Any captured `RuntimeWarning` during onset/beat/rhythm construction is fatal before successful timebase output.
- Minimum detected beats `8`; mean/median/count-duration implied BPM each `30..300`; median-IBI BPM / tracker BPM `0.5..2.0`.
- Static phase evidence weights: drums `1.0`, mix `0.5`, bass `0.5`, low-frequency flux `0.75`, harmonic-change `0.75`; low-frequency max `200Hz`, chroma `12`.
- Four static phases; tie tolerance `1e-12`, lower phase wins.
- `leadingBeatCount=(-selectedPhase)%4`; early period = median first up-to-8 positive IBIs; prepend exactly 0..3 extrapolated beats.
- Absolute beat ordinal is sequential over prefix+detected; grid step = `4*ordinal`; bar phase never changes ordinal.
- Quantize `int(round(rawGridStep))`; measure `absStep//16+1`; step `absStep%16`; generation uses no professional-reference meter map.

### V159 pitch numerics — immutable / unchanged from V158
- Harmonic template 36 bins/octave; harmonics 1..5 weights `[1,.5,.3333333333,.25,.2]`; radius 1.
- Bass MIDI `28..67`; onset backtrack true; min IOI `35ms`; pitch window `180ms`; pYIN frame `2048`, hop `256`; sigma `.75`; fusion `.75`; same V158 duration/scoring rules.
- Guitar MIDI `40..88`; Basic Pitch onset `.5`, frame `.3`, min length `90ms`, melodia=true; persistent track min3 frames/radius1/max6; same V158 register repair/harmonic rules; added-track duration `.07s`.
- Same grid/MIDI dedupe and source precedence.

## V159 implementation — final sealed Git blobs
- `validation/v159_cpu_autonomous/build_timebase_v159.py` → `45f0e5013f13064a71c854b2c0e026482a135a8b`.
- `validation/v159_cpu_autonomous/timebase_qc_v159.py` → `fae5054153c90360ed5ea3f504feb432ba73eaef`.
- `validation/v159_cpu_autonomous/transcribe_v159.py` → `290d26099f9ac082eb19173f03d1904f7fbab45d`.
- `validation/v159_cpu_autonomous/structural_qc_v159.py` → `a3fbf4e8d827aca955a0995fc31930a8c631c932`.
- `debug/v159-cpu-autonomous/negative-runtime-guard.py` → `6a068e4699dcbcac0e236a9c54ce10efe1c96d96`.
- `.github/workflows/v159-static-preflight.yml` → `28cc7d465a910dfdf1f919bc58e9696392ad718f`.

## CPU dependency / separation layout audit — COMPLETE
Reference-blind inspection of prior CPU setup established:
- Python `3.10`; `torch==2.8.0+cpu`; NumPy `1.26.4`; SciPy `1.13.1`; SoundFile `0.12.1`; Basic Pitch `0.4.0`; Demucs `4.1.0`; imageio-ffmpeg `0.6.0`; librosa `0.11.0`.
- CPU only: `torch.version.cuda is None`, `torch.cuda.is_available() is False`.
- Determinism: seed `0`; Torch threads/inter-op `1`; deterministic algorithms enabled; math library threads `1`.
- Fresh separation: `htdemucs_6s`, device `cpu`, shifts `1`, jobs `1`.
- V159 stem layout: `/tmp/v159-demucs/htdemucs_6s/v159-normalized/{guitar,bass,drums}.wav`.
- This audit did **not** execute Demucs or open song audio.

## Static preflight — PASS / CONSUMED
- Workflow commit `7482e15ec60f99001c61584dd167ef142d34e7f4`; run ID `33195208763`; run number `1`; attempt `1`; job `98930481313`; conclusion `success`; CPython `3.10.21`.
- Static boundary PASS; all five Python files compiled.
- Negative runtime guard schema `dadrock.tabs.v159.negative-runtime-guard.v1`: `validation=PASS`, failures `[]`.
- All checks true: no prior-version runtime paths; no professional-reference/scorer runtime paths; no pitch imports/calls in pre-pitch files; transcriber requires timebase-QC PASS before pitch.
- Final proof PASS: no timebase, timebase-QC, candidate, generation, environment, or structural-QC artifact created.
- Workflow was read-only and installed no project/audio dependencies. Do not re-run this consumed static workflow.

## Pre-run identity receipt — SEALED
- Path: `debug/v159-cpu-autonomous/pre-run-identity-receipt.json`.
- Seal commit: `f9916cdb3ae0cbc2eecb3325c01fbfcac22b6bb4`.
- Git blob: `9edb001227ce99570b0c4081102bf22276121499`.
- Schema: `dadrock.tabs.v159.pre-run-identity-receipt.v1`; validation `PASS`; status `SEALED_BEFORE_GENERATION`.
- `sealedAtBranchHeadBeforeThisReceipt`: `bacc4c2c6c5448f2e6dc2284dc5122619f369c48`.
- Pins preregistration, implementation contract, all four runtime modules, negative guard, and static-preflight workflow.
- At seal: timebase absent; timebase-QC receipt absent; candidate absent; generation receipt absent; environment receipt absent; structural-QC receipt absent; `.github/workflows/v159-generate.yml` absent.
- At seal: professional-reference reads `0`; reference-facing score calls `0`; GPU/Modal/CUDA executions `0`; main/Production untouched.
- Single-trigger contract: generation-workflow creation is the only arm; expected run count `1`; second arm forbidden; duplicate run aborts V159; workflow must self-seal after terminal freeze; branch writes while active forbidden.

## Timebase-QC / structural terminal policy
- Timebase QC is the hard pre-pitch boundary and writes its receipt even on FAIL; exit code nonzero on FAIL.
- **Any timebase-QC FAIL freezes V159 before authoritative candidate creation; no candidate; never re-arm V159.**
- Transcriber only runs after frozen timebase-QC `PASS` and then writes one candidate + generation receipt marked `PENDING_INDEPENDENT_STRUCTURAL_QC`.
- Structural QC independently recomputes hashes/grid/event invariants and writes PASS/FAIL; any structural-QC failure freezes V159 and ends the version.
- Only if timebase QC + structural QC pass is the single candidate eligible to freeze and later be scored exactly once.

## Current hard boundary
- No generation workflow exists yet.
- No song audio processing has occurred in V159.
- No branch writes are permitted once the generation workflow is armed until its run completes and terminal artifacts are frozen.
- No professional-reference/scorer reads during generation/QC.
- No GPU/Modal/CUDA without fresh explicit user authorization.

## Exact next steps — RESUME HERE
1. Re-fetch branch head/checkpoint before every write.
2. Finish reviewer-only design of `.github/workflows/v159-generate.yml` against the exact V159 script CLI contracts; do not execute audio yet.
3. Workflow must verify run number/attempt `1`, all sealed Git blobs including pre-run receipt `9edb001227ce99570b0c4081102bf22276121499`, absence of all generated artifacts, and negative-runtime guard before audio access.
4. Materialize exact historical audio → deterministic normalize with exact SHA → install exact CPU dependencies → deterministic fresh one-pass `htdemucs_6s` separation → write CPU environment receipt with positive integer `workflowRunId`, `workflowRunNumber=1`, `workflowRunAttempt=1`.
5. Build write-once timebase → independent timebase QC. If QC FAILS: freeze terminal failure artifacts, self-seal workflow, produce no candidate, end V159.
6. If timebase QC PASS: run transcriber → independent structural QC. PASS or FAIL is terminal for this single generated candidate; self-seal workflow and commit the frozen artifacts exactly once.
7. **Do not create `v159-generate.yml` until its complete one-shot mechanics have been reviewer-audited. Creation itself is the sole trigger.**
8. After the generation workflow completes, checkpoint immediately. If structural QC PASS, separately preregister/seal exactly one professional-reference scoring run. If it fails, end V159 without scoring.
9. Fresh explicit authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
