# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-08 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`

This is the **only canonical fresh-chat checkpoint for the new Songsterr-inspired pipeline**.

Do not use the generic `docs/checkpoints/CURRENT_STATE.md` for this project. Do not resume the old V143/Gomyway investigation unless the user explicitly asks to return to that archived work.

## PRODUCT TARGET

Build an AI-first guitar/bass tab creator that can go from uploaded audio to a usable finished tab without a mandatory human correction step.

Engineering priority: musical correctness and stability before cosmetic scores. Preserve detected musical identity while making structure, timing, rhythm spelling, chord shapes, fretboard motion, techniques, and final rendering coherent enough for product use.

Do not change public accuracy promises yet. Only change `/ai-tab` wording after the clean pipeline earns a real no-human-correction acceptance standard.

## FOUNDATIONAL RULE — TIMING AND MEASURES COME FIRST

Non-negotiable real-audio order:

**full-mixture audio → timing/measure map → structure-conditioned note evidence → rhythm/notation → playable tab → render metadata**

`structureMap` is first-class and downstream stages consume it directly. Do not return to loose-note-first/post-hoc timing repair.

## EXISTING `/ai-tab` PRODUCT SHELL — PRESERVE IT

Preserve:

**audio upload → AI analysis → analyzer metadata → technique/render events → watermarked preview PDF → PayPal/free-token unlock reference → full tab PDF → browser download + email delivery**

The current preview/final PDF boundary accepts `generatedTab`, `transcriptionType`, tuning, tempo, time signature, key signature, `analysisEngine`, `renderEvents`, `measureGrid`, confidence, difficulty, and techniques.

The legacy structured renderer uses measure + integer 16th-step placement. The fresh adapter fails closed to complete textual tab output for pickup/triplet/other structures that cannot be represented losslessly by that legacy projection.

## PROJECT BOUNDARY

- Old branch `v143-contextual-prune-lobo` is archive/evidence only.
- Historical Gomyway/V143 scorer contracts are not fresh acceptance criteria.
- Do not touch Production or main.
- Do not dispatch Modal/GPU/model-bearing workflows, professional scorers, training, optimizer sweeps, or unapproved real-audio fixtures without explicit user authorization.
- A generic request to “continue” is **not** authorization to dispatch model/GPU/real-audio work.
- CPU-only deterministic tests on the fresh branch are allowed.

## CURRENT AUTHORIZED REAL-AUDIO SCOPE

On 2026-09-08 the user explicitly authorized the `gomywaymidterm` audio in the public folder for the fresh pipeline.

Resolved exact fixture on `main`:
- path: `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`;
- Git blob SHA: `4dd709e3fa177b4daeed71ca97f0199757729d4b`;
- size: 3,464,988 bytes.

The fresh branch does **not** copy/merge/cherry-pick main. The authorized canary downloads only that exact public fixture and verifies its Git blob SHA before analysis.

The filename containing “gomyway” does **not** authorize resuming archived Gomyway/V143 code, scorer percentages, gates, or references. It is only an audio fixture.

Current authorization is being used for **CPU-only reference-blind audio structure analysis**. No Modal/GPU/model-bearing note inference has been authorized or run in this phase.

## CURRENT FRESH PIPELINE

Namespace: `songsterr_pipeline/`

### Structure and notation
- `structureMap.mjs` — explicit tempo/meter/feel/pickup/measures/downbeats/beats/subdivisions, confidence/provenance, boundary validation.
- `structureRhythmNotation.mjs` — structure-map-driven starts/ends, ties, rests, syncopation, displacement diagnostics, stable source identity.
- `contextualRhythmSpelling.mjs` — standard/dotted/triplet values, weak-beat dotted merges, strong-beat tie preservation, explicit rest spelling, feel diagnostics.

### Real-audio structure boundary
- `audioStructureAdapter.mjs` — validates reference-blind full-mixture timing evidence and converts it into the first-class `structureMap` contract.
- Requires explicit quarter-note tempo semantics and currently supports conservative 3/4 or 4/4 quarter-note meter projection only; unsupported beat-unit/meter semantics fail closed.
- Preserves raw tempo/meter/feel confidence, meter candidates, upstream diagnostics, provenance, and observed beat alignment diagnostics.
- Emits `structureFrozenBeforeNoteInference: true` and `legacyV143ScorerImported: false`.

CPU analyzer outside the pure deterministic namespace:
- `scripts/songsterr-fresh/analyze_full_mixture_structure.py` — reference-blind full-mixture beat/tempo, conservative 3/4-vs-4/4 bar-phase, and straight/triplet feel evidence; no note inference and no legacy scorer.
- `scripts/songsterr-fresh/build_structure_map.mjs` — reads the raw audio-analysis JSON, applies `audioStructureAdapter.mjs`, writes the frozen structure-map evidence, and prints raw alignment/confidence diagnostics.

### Playability and phrase motion
- `playableShapeDecoder.mjs` — exact-MIDI candidate positions/shapes, unique strings, physical constraints, role-aware policies, explicit rejection reasons, no pitch dropping.
- `fretboardPathOptimizer.mjs` — deterministic phrase search over legal shape states using hand movement/string continuity only after pitch/playability constraints are satisfied.
- `structureFretboardPath.mjs` — maps selected phrase path onto events while protecting event IDs, clusters, MIDI, timing, notation, provenance, rests.

### Evaluation and product projection
- `freshEvaluator.mjs` — scoreless raw structure/event/timing/rhythm/playability/path diagnostics with explicit failure codes. `compositeScore: null`; legacy V143 scorer import false.
- `productShellAdapter.mjs` — maps fresh final state to existing `/ai-tab` fields. Structured legacy render data is emitted only when lossless; otherwise full text fallback remains available.

### Deterministic orchestration
- `deterministicPipeline.mjs` — single non-model composition entry point:
  **structureMap + note evidence → structure-driven event schema → contextual rhythm spelling → optimized fretboard path → raw evaluator → product-shell payload**.
- It does not infer audio, call a model, touch a reference tab, or dispatch any remote analyzer.

## IMPORTANT COMMITS

Core architecture:
- `212be220b96de687f55cce2ca3e7698b1ac9dadb` — initial deterministic core.
- `e9b56a0fdceed2dafc9715f22b5c93954098877e` — first-class `structureMap`.
- `89c6a12d604dd203b65f4e4015d7d1d246f05a9f` — structure-driven event/rhythm schema.
- `b6a3a70369c1d5af269b95428a4a67e0bb2a99d5` — contextual rhythm spelling.
- `9f40ed825333e33f0e3f91571d08619d3f05977c` — multiple legal playable-shape candidates.
- `467fed67ef35f23a07e45aebfed340a259319b7d` — phrase fretboard optimizer.
- `e4e991ad3cdfe5b24e0a198f954acbe77e5ac6e9` — structure/fretboard integration.
- `bbc8eecc41f04906b59dac5e4764eee919d0e03f` — raw evaluator.
- `9a9de7247973a127bc1f8b4709cd5956293e0dbb` — product-shell adapter.
- `d22a82b0fb947aa83c35c2f707bf1126256d4ccb` — deterministic end-to-end orchestrator.

Real-audio structure phase:
- `34c8b507865d37415c074db3d631fada403fd3ac` — clean full-mixture structure adapter.
- `9c8e420ff2ccf52adca277bb9335c7feb45f5db2` — five structure-adapter contract tests.
- `73c95d8e3d99df6f31df2f2ed10dc950393bc1bd` — CPU-only reference-blind full-mixture structure analyzer.
- `edeb37ccbbb9c79a84786b966ed683ecc6c48e5c` — raw-analysis → frozen-structure-map runner.
- `f868dc8d18d6bda0a0392755f4a74a60220deecb` — first authorized real-audio structure canary workflow.
- `0ac5936e0c9640dbd0ab2fbf5bab740e6c24d798` — canary fix to install the audio decoder explicitly.

Recent verification/guard commits:
- `acae3c6779feb61c8a06152a92df938667980de5` — cross-layer deterministic composition tests.
- `f6cc087abf5fdaf546e973b7b8c605dbf2e8266e` — automatic CPU-only fresh-branch CI.
- `28338aff0fb279e6af3742227629a3c7c07bbac9` — fresh namespace isolation boundary guard test.

## AUTOMATIC FRESH-BRANCH CI

Workflow: `.github/workflows/songsterr-fresh-pipeline-v1-tests.yml`.

It runs on manual dispatch and pushes to `songsterr-fresh-pipeline-v1` touching `songsterr_pipeline/**` or the workflow.

Runtime is GitHub-hosted Ubuntu + Node 22, running `npm test` inside `songsterr_pipeline` (`node --test tests/*.test.mjs`). Permissions are read-only contents.

## VALIDATION STATUS — CURRENT PROVEN BASELINE

### Branch-wide deterministic GitHub Actions proof

Adapter test run ID: `34191759524`
Job ID: `101951099988`
Tested commit: `9c8e420ff2ccf52adca277bb9335c7feb45f5db2`

Actual Node TAP result:
- tests: **67**
- pass: **67**
- fail: **0**
- cancelled: **0**
- skipped: **0**
- todo: **0**

The five new tests prove:
- reference-blind audio structure evidence becomes a first-class map aligned to observed beats;
- raw confidence/candidates/diagnostics/provenance remain visible rather than being converted into a legacy score;
- non-reference-blind input is rejected;
- unsupported tempo beat-unit or meter denominator semantics fail closed;
- adapter output is deterministic.

This supersedes the prior 62/62 deterministic baseline while preserving all earlier coverage.

### First authorized real-audio canary attempt

Workflow: `.github/workflows/songsterr-fresh-gomyway-midterm-structure-canary.yml`.

Run ID: `34191849623`
Tested commit: `f868dc8d18d6bda0a0392755f4a74a60220deecb`

Verified before failure:
- exact authorized fixture downloaded successfully;
- `git hash-object` matched `4dd709e3fa177b4daeed71ca97f0199757729d4b`.

Failure was environment-only before analysis:
- runner did not have `ffmpeg` installed;
- decode step failed with `ffmpeg: command not found`;
- no structure inference, note inference, or model execution occurred in that failed run.

Fix commit `0ac5936e0c9640dbd0ab2fbf5bab740e6c24d798` installs `ffmpeg` explicitly before decoding. Retry run `34191909876` is the current authorized canary run; do not claim its musical result until it completes and the raw artifact/log is inspected.

## ISOLATION BOUNDARY GUARD

`tests/boundaryGuard.test.mjs` scans every root fresh `.mjs` source module and fails if the deterministic namespace imports non-local/archived/model-bearing runtime dependencies, performs network fetches, or launches external processes.

The real-audio ingestion/analyzer scripts live outside `songsterr_pipeline/`; the deterministic namespace receives only validated JSON evidence through `audioStructureAdapter.mjs`.

## CURRENT ENGINEERING BOUNDARY

The deterministic structure → rhythm → playability → phrase path → evaluator → product-shell path is composed and **67/67 green**.

The user has now explicitly authorized the exact `gomyway-midterm-source.m4a` fixture for real-audio work. The current implementation is intentionally executing **structure first** and freezing that map before any note inference.

Do not proceed to a model/GPU-bearing note-evidence stage unless separately and explicitly authorized. A CPU/reference-blind note-evidence experiment may only follow after the real-audio structure map itself is validated and must not rewrite the frozen structure.

Clean authorized order remains:

**full-mixture structure analysis → `structureMap` → role-conditioned note evidence → `deterministicPipeline.mjs` → product-shell output**

Do not import the archived V143 scorer/gate maze.

## NON-NEGOTIABLES

- Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`.
- Canonical branch: `songsterr-fresh-pipeline-v1`.
- Archived V143/Gomyway remains archive/evidence only unless explicitly requested.
- Timing/measure structure precedes trusting note placement.
- Preserve detected MIDI/event identity; never silently alter notes for notation/fingering appearance.
- Never drop pitches merely to satisfy shape/path/legacy-render projection.
- Preserve existing `/ai-tab` preview → unlock → full PDF → email/download customer flow.
- No Production or main changes.
- No accidental Modal/GPU/model/professional-scorer/training activity.
- Real-audio work must stay within explicit user authorization.
- Keep this checkpoint updated after each meaningful milestone.
