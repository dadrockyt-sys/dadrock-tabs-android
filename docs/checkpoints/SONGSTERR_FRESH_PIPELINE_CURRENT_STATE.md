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
- Do not dispatch Modal/GPU/model-bearing workflows, professional scorers, training, optimizer sweeps, or real-audio canaries without explicit user authorization.
- A generic request to “continue” is **not** authorization to dispatch model/GPU/real-audio work.
- CPU-only deterministic tests on the fresh branch are allowed.

## CURRENT FRESH PIPELINE

Namespace: `songsterr_pipeline/`

### Structure and notation
- `structureMap.mjs` — explicit tempo/meter/feel/pickup/measures/downbeats/beats/subdivisions, confidence/provenance, boundary validation.
- `structureRhythmNotation.mjs` — structure-map-driven starts/ends, ties, rests, syncopation, displacement diagnostics, stable source identity.
- `contextualRhythmSpelling.mjs` — standard/dotted/triplet values, weak-beat dotted merges, strong-beat tie preservation, explicit rest spelling, feel diagnostics.

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
- Explicit metadata: `modelOrAudioAnalyzerInvoked: false`, `legacyV143ScorerImported: false`.
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

Recent verification/guard commits:
- `acae3c6779feb61c8a06152a92df938667980de5` — cross-layer deterministic composition tests.
- `f6cc087abf5fdaf546e973b7b8c605dbf2e8266e` — automatic CPU-only fresh-branch CI.
- `28338aff0fb279e6af3742227629a3c7c07bbac9` — fresh namespace isolation boundary guard test.

## AUTOMATIC FRESH-BRANCH CI

Workflow: `.github/workflows/songsterr-fresh-pipeline-v1-tests.yml`.

It now runs on:
- manual dispatch;
- pushes to `songsterr-fresh-pipeline-v1` touching `songsterr_pipeline/**` or this workflow.

Runtime:
- GitHub-hosted Ubuntu 24.04;
- Node test runtime configured as Node `22` (green run used v22.23.2);
- command: `npm test` inside `songsterr_pipeline`;
- package command: `node --test tests/*.test.mjs`.

Permissions are read-only contents. No model, audio, GPU, scorer, deployment, training, or secret-consuming step is present.

## VALIDATION STATUS — CURRENT PROVEN BASELINE

### Branch-wide GitHub Actions proof

Run ID: `34191214663`
Job ID: `101949496020`
Tested commit: `28338aff0fb279e6af3742227629a3c7c07bbac9`

Actual Node TAP result from the GitHub Actions log:
- tests: **62**
- pass: **62**
- fail: **0**
- cancelled: **0**
- skipped: **0**
- todo: **0**

This is now the canonical deterministic baseline. It supersedes the earlier need to qualify later layers as isolated-only proofs.

The immediately preceding branch-wide run at `acae3c6779feb61c8a06152a92df938667980de5` also passed **61/61**; the 62nd test is the isolation boundary guard.

### What the 62-test baseline covers

The suite collectively proves synthetic/deterministic behavior for:
- structure conditioning and validation;
- pickup-aware measure timing;
- stable non-chain onset clustering;
- exact MIDI reconstruction;
- event-count and MIDI preservation;
- first-class pickup/downbeat/measure/beat/subdivision maps;
- tempo and meter changes at exact measure boundaries;
- rejection of illegal mid-measure structure changes;
- straight/triplet timing differences;
- beat/measure/pickup ties;
- rest diagnostics without fake notes;
- unresolved duration staying unresolved;
- contextual standard/dotted/triplet rhythm spelling;
- weak/strong beat tie decisions;
- explicit rest spelling;
- constrained chord/shape playability;
- role-aware open-string preferences;
- impossible-shape rejection without note dropping;
- multiple legal candidate shape states;
- deterministic phrase fretboard path optimization;
- reduced targeted hand movement versus independent local choices;
- structure/timing/notation invariance during fretboard optimization;
- raw scoreless evaluator and independent failure codes;
- product-shell mapping into the existing renderer/PDF boundary;
- fail-closed pickup/triplet legacy-render fallback;
- full deterministic cross-layer composition;
- unresolved phrase fingering remaining explicit end-to-end;
- deterministic repeated pipeline output;
- fresh namespace isolation from archived/model-bearing runtime dependencies.

## ISOLATION BOUNDARY GUARD

`tests/boundaryGuard.test.mjs` scans every root fresh `.mjs` source module and fails if the namespace:
- imports a non-local runtime dependency;
- imports a path containing archived/model-bearing identifiers such as V143, Gomyway, Modal, analyzer, professional, or reference;
- performs `fetch(...)` network calls;
- introduces `XMLHttpRequest`;
- uses child-process execution primitives.

The guard passed in the 62/62 branch-wide run.

This is a mechanical regression guard in addition to the written project rule; it helps prevent accidental contamination of the fresh deterministic namespace.

## CURRENT ENGINEERING BOUNDARY

The deterministic structure → rhythm → playability → phrase path → evaluator → product-shell path is composed behind one clean entry point, protected by automatic branch CI, and currently **62/62 green**.

The next meaningful phase is the first real-audio/model adapter, but that still requires **explicit user authorization**. Do not treat generic “continue” as authorization for model/GPU/real-audio execution.

When explicitly authorized, the clean real-audio path must be:

**full-mixture structure analysis → `structureMap` → role-conditioned note evidence → `deterministicPipeline.mjs` → product-shell output**

Do not import the archived V143 scorer/gate maze.

## NEXT SAFE WORK WITHOUT REAL-AUDIO AUTHORIZATION

The deterministic implementation is green and the remaining major engineering work crosses into the explicitly protected real-audio/model phase. Safe maintenance work may continue, but do not manufacture busywork or weaken the boundary merely to keep changing code.

## NON-NEGOTIABLES

- Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`.
- Canonical branch: `songsterr-fresh-pipeline-v1`.
- Archived V143/Gomyway remains archive/evidence only unless explicitly requested.
- Timing/measure structure precedes trusting note placement.
- Preserve detected MIDI/event identity; never silently alter notes for notation/fingering appearance.
- Never drop pitches merely to satisfy shape/path/legacy-render projection.
- Preserve existing `/ai-tab` preview → unlock → full PDF → email/download customer flow.
- No Production or main changes.
- No accidental Modal/GPU/model/professional-scorer/training/real-audio activity.
- Keep this checkpoint updated after each meaningful milestone.
