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

Fresh work replaces the transcription brain, not the customer/paywall/PDF journey.

Read-only inspection on 2026-09-08 confirmed the current preview/final PDF boundary accepts:
- `generatedTab`;
- `transcriptionType`;
- `tuning`;
- `tempo`;
- `timeSignature`;
- `keySignature`;
- `analysisEngine`;
- `renderEvents`;
- `measureGrid`;
- `confidence`;
- `difficulty`;
- `techniques`.

The current structured renderer contract uses legacy-compatible events with `measure`, integer 16th-step `step`, string index, fret, MIDI, duration steps, and techniques. The current read-only measure-grid overlay requires `passed: true`, `measureGridVersion: 7`, `measuresPerRow: 6`, and row notes with `rowRatio`, string index, fret, `measureGridReadOnly: true`, and `musicallyFiltered: true`.

## PROJECT BOUNDARY

- Old branch `v143-contextual-prune-lobo` is archive/evidence only.
- Historical Gomyway/V143 scorer contracts are not fresh acceptance criteria.
- Do not touch Production or main.
- Do not dispatch Modal/GPU/model-bearing workflows, professional scorers, training, optimizer sweeps, or real-audio canaries without explicit user authorization.
- A generic request to “continue” is not authorization to dispatch model/GPU/real-audio work.
- Old failed CI/tests do not become fresh blockers merely because they exist.

## FRESH IMPLEMENTATION

Namespace: `songsterr_pipeline/`

Core architecture commits:
- `212be220b96de687f55cce2ca3e7698b1ac9dadb` — isolated deterministic core;
- `e9b56a0fdceed2dafc9715f22b5c93954098877e` — first-class `structureMap` + structure-conditioned note core;
- `89c6a12d604dd203b65f4e4015d7d1d246f05a9f` — structure-map-driven event/rhythm schema;
- `b6a3a70369c1d5af269b95428a4a67e0bb2a99d5` — contextual rhythm spelling;
- `e36d734076001767306f53f7bb56c75440787dbd` — constrained playable-shape decoder;
- `9f40ed825333e33f0e3f91571d08619d3f05977c` — multiple legal shape candidate states;
- `467fed67ef35f23a07e45aebfed340a259319b7d` — phrase-level fretboard path optimizer;
- `e4e991ad3cdfe5b24e0a198f954acbe77e5ac6e9` — structure-event → optimized fretboard integration;
- `bbc8eecc41f04906b59dac5e4764eee919d0e03f` — fresh raw evaluator;
- `9a9de7247973a127bc1f8b4709cd5956293e0dbb` — fresh analyzer → existing product-shell adapter.

Current test commits:
- `c682355c173f47dbb250175fb4eca718a8c91a20` — original deterministic tests;
- `9ce440755d1d70813d1043210d8bd8a28a650cd3` — compatibility rhythm tests;
- `71e553f13aa37a4c30615c094c2679b1e9504475` — structure-map tests;
- `85b175f60406fb47a81bfebfe36ba99e52ed029f` — structure-driven rhythm tests;
- `15bc52616bee054acea6a4d58c7cfd918b578c13` — contextual rhythm tests;
- `c3452d39702df616b52ecd0bac171af2bd099d12` — constrained decoder tests;
- `d684cd2a42ace038bff85637a2ef9a38b0c37371` — phrase optimizer tests;
- `1e0e9514193e76e0b80fd62415c53d801bccb234` — structure-fretboard invariance tests;
- `a49695e20ab20f830e31b9f160194cd5137e5f4d` — fresh raw evaluator tests;
- `f6e343f85c828318cf3a1d92982018a51b2a9a56` — product-shell adapter tests.

Recent checkpoint commits:
- `3bc1c36c4d3fbeefe3a1243415de72b1a4a5a8cd` — 13/13 proof;
- `324420a20210a3cd88284b323968366d1e86773c` — 19/19 structure milestone;
- `d78b01c09707f3a11e876a9e500e788a2b6c4721` — 25/25 structure-rhythm milestone;
- `19512a5477cea0845629e0a80723566e5ee41364` — repaired interrupted 30/30 contextual checkpoint;
- `59c1e4977d4f69a6eb83282c29670d972e84fea8` — constrained decoder checkpoint;
- `7a2c029d2c0fe6153a47ee43ad75f240385d5482` — phrase optimizer checkpoint;
- `9ea044b935b6cdf245b8cd580f27b61b7ebc6204` — structure/fretboard integration checkpoint;
- `156f448809f1627c653a7feae6c2fa20044d7a4e` — raw evaluator checkpoint.

## CURRENT CLEAN PIPELINE LAYERS

### Structure and notation

- `structureMap.mjs`: explicit timing/measure contract, confidence/provenance, change-boundary validation, map-driven snapping/location.
- `structureRhythmNotation.mjs`: map-driven starts/ends, pickup/measure/beat segmentation, ties, rests, syncopation, displacement diagnostics, stable source identity.
- `contextualRhythmSpelling.mjs`: readability only; standard/dotted/triplet values, weak-beat dotted merges, strong-beat ties, explicit rest spelling, phrase feel diagnostics.

### Playability and phrase motion

- `playableShapeDecoder.mjs`: exact-MIDI candidate states, unique strings, physical constraints, role-aware policies, explicit rejection reasons, no pitch dropping.
- `fretboardPathOptimizer.mjs`: deterministic phrase search over legal states using movement/string continuity only after playability is satisfied.
- `structureFretboardPath.mjs`: applies selected path back onto events while protecting event IDs, cluster identity, MIDI, timing, structure positions, notation, provenance, and rests.

### Raw evaluator

`freshEvaluator.mjs` is intentionally scoreless and reports independent raw structure/event/timing/rhythm/playability/path diagnostics and failure codes.

Evaluator metadata explicitly contains:
- `compositeScoreDefined: false`;
- `compositeScore: null`;
- `legacyV143ScorerImported: false`.

### Product-shell adapter

`productShellAdapter.mjs` maps clean final state into the existing `/ai-tab` boundary without importing the archived V143 scorer/pipeline.

Outputs include:
- `generatedTab` fallback text;
- `transcriptionType`;
- tuning label derived from configured MIDI tuning;
- first tempo/meter projection;
- optional key/difficulty/techniques/confidence;
- `analysisEngine: 'songsterr-fresh-pipeline-v1'`;
- internal events;
- legacy-compatible `renderEvents` when the projection is exact;
- V7-compatible read-only `measureGrid` when the projection is exact;
- full `structureMap` for fresh consumers;
- `freshDiagnostics` from the raw evaluator;
- payload contract flags for delivery readiness and structured-render eligibility.

Important fail-closed behavior:
- raw evaluator failure => `deliveryReady: false`, no structured render data;
- pickup/anacrusis => complete text fallback, no fake legacy structured projection;
- triplet/non-16th-compatible subdivision => complete text fallback, no false sixteenth quantization;
- unsupported legacy meter resolution => complete text fallback;
- incomplete fretboard/duration mapping => complete text fallback;
- no note is silently dropped or relocated to make the old renderer accept it.

The V7 measure-grid projection is generated directly from fresh structure/events with `legacyV143ScorerImported: false`. It does not call the archived V143 scorer or gate maze.

## VALIDATION STATUS

Earlier proven surfaces:
- original clean: **13/13 pass**;
- structure-first: **19/19 pass** after exact-boundary `[start, end)` fix;
- structure-driven event/rhythm: **25/25 pass**;
- contextual rhythm namespace run before interruption: **30/30 pass**.

New isolated proofs:
- constrained decoder: **5/5 pass**;
- decoder + candidate enumeration + phrase optimizer: **10/10 pass**;
- decoder + phrase optimizer + structure integration: **15/15 pass**;
- fresh raw evaluator: **6/6 pass**;
- fresh product-shell adapter: **6/6 pass**.

Product-shell adapter tests prove:
- clean straight 4/4 state maps to existing renderer/PDF fields;
- exact render event maps measure/step/string/fret/MIDI/duration correctly;
- read-only measure-grid projection satisfies the current V7 overlay shape;
- triplet timing fails closed to text instead of fake sixteenths;
- pickup timing fails closed to text instead of relocating pickup notes;
- raw evaluator failure blocks delivery readiness;
- custom tuning metadata projects without changing MIDI/fret identity;
- output is deterministic and explicitly declares no legacy scorer import.

The full branch-wide suite has not been re-executed after the newest decoder/path/integration/evaluator/adapter additions because this container cannot resolve GitHub directly. Do not claim a new branch-wide total yet.

No Production/main, model/GPU, professional scorer, training, real-audio canary, or archived V143/Gomyway path was touched.

## CURRENT ENGINEERING BOUNDARY

The deterministic structure → rhythm → playability → phrase-path → evaluator → product-shell contract is now defined far enough to begin the first real-audio adapter.

However, **do not start it without explicit user authorization**, because the next work can involve model-bearing/audio-analysis execution.

When explicitly authorized, the first clean real-audio adapter must follow:

**full-mixture structure analysis → `structureMap` → role-conditioned note evidence → clean event schema → contextual notation → constrained local shapes → phrase path → raw evaluator → product-shell adapter**

Do not import the old V143 scorer/gate maze.

## NEXT EXECUTION ORDER AFTER EXPLICIT REAL-AUDIO/MODEL AUTHORIZATION

1. Define the full-mixture structure-analysis adapter interface and provenance/confidence contract.
2. Connect structure-conditioned note evidence without changing structure after note inference.
3. Run only authorized clean real-audio fixtures/canaries; no legacy Gomyway percentages as gates.
4. Feed final clean state through `productShellAdapter.mjs` into the existing preview → unlock → full PDF → email/download flow.
5. Define the multi-song/role no-human-correction acceptance gate before changing public copy.

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
