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
- `deterministicPipeline.mjs` — new single non-model composition entry point:
  **structureMap + note evidence → structure-driven event schema → contextual rhythm spelling → optimized fretboard path → raw evaluator → product-shell payload**.
- It explicitly reports `modelOrAudioAnalyzerInvoked: false` and `legacyV143ScorerImported: false`.
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

Recent tests:
- `c3452d39702df616b52ecd0bac171af2bd099d12` — constrained shape decoder.
- `d684cd2a42ace038bff85637a2ef9a38b0c37371` — phrase optimizer.
- `1e0e9514193e76e0b80fd62415c53d801bccb234` — structure/fretboard invariance.
- `a49695e20ab20f830e31b9f160194cd5137e5f4d` — raw evaluator.
- `f6e343f85c828318cf3a1d92982018a51b2a9a56` — product-shell adapter.
- `acae3c6779feb61c8a06152a92df938667980de5` — cross-layer deterministic composition tests.

CI:
- `f6cc087abf5fdaf546e973b7b8c605dbf2e8266e` — fresh CPU-only workflow now runs automatically on pushes to `songsterr-fresh-pipeline-v1` that touch `songsterr_pipeline/**` or the fresh workflow file.
- Workflow: `.github/workflows/songsterr-fresh-pipeline-v1-tests.yml`.
- Runtime: Ubuntu + Node 22 + `npm test` in `songsterr_pipeline`.
- `npm test` is `node --test tests/*.test.mjs`, so it covers every committed fresh test file.
- No model/audio/GPU/scorer/secrets step is present.

## VALIDATION STATUS

Earlier proven surfaces:
- original clean: **13/13 pass**;
- structure-first: **19/19 pass** after exact-boundary `[start, end)` fix;
- structure-driven event/rhythm: **25/25 pass**;
- contextual rhythm namespace run before interruption: **30/30 pass**.

Later isolated proofs:
- constrained decoder: **5/5 pass**;
- decoder + candidate enumeration + phrase optimizer: **10/10 pass**;
- decoder + phrase optimizer + structure integration: **15/15 pass**;
- raw evaluator: **6/6 pass**;
- product-shell adapter: **6/6 pass**.

### Branch-wide CI — PENDING AT THIS CHECKPOINT

A true branch-wide CPU-only GitHub Actions run is now enabled. The latest run was triggered by commit `acae3c6779feb61c8a06152a92df938667980de5` and was still in progress when this checkpoint was written.

Do **not** claim a branch-wide pass count until that run reaches a final GitHub conclusion and its test log is inspected.

## CROSS-LAYER ORCHESTRATOR TEST INTENT

`deterministicPipeline.test.mjs` adds end-to-end synthetic coverage for:
- straight 4/4 input reaching a delivery-ready structured payload while preserving source MIDI/index/timing identity;
- triplet input staying delivery-ready but failing closed from the legacy 16th renderer;
- unresolved simultaneous fingering remaining explicit with both source pitches preserved and delivery blocked;
- deterministic repeated full-pipeline output.

## CURRENT ENGINEERING BOUNDARY

The deterministic structure → rhythm → playability → phrase path → evaluator → product-shell path is now composed behind one clean entry point and has automatic CPU-only branch CI.

The next **model/real-audio** phase still requires explicit user authorization. Do not treat generic “continue” as that authorization.

When explicitly authorized, the first clean real-audio path must be:

**full-mixture structure analysis → `structureMap` → role-conditioned note evidence → deterministic pipeline → product-shell adapter**

Do not import the archived V143 scorer/gate maze.

## NEXT SAFE WORK WITHOUT REAL-AUDIO AUTHORIZATION

1. Obtain and inspect the final branch-wide CPU-only CI result.
2. Fix any deterministic failures it exposes and rerun until green.
3. Keep this checkpoint synchronized with exact test counts and commits.
4. Do not cross into model/GPU/real-audio execution without explicit authorization.

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
