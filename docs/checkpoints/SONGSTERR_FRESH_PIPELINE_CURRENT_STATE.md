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

## PROJECT BOUNDARY

- Old branch `v143-contextual-prune-lobo` is archive/evidence only.
- Historical Gomyway/V143 scorer contracts are not fresh acceptance criteria.
- Do not touch Production or main.
- Do not dispatch Modal/GPU/model-bearing workflows, professional scorers, training, optimizer sweeps, or real-audio canaries without explicit user authorization.
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
- `bbc8eecc41f04906b59dac5e4764eee919d0e03f` — fresh raw evaluator.

Current test commits:
- `c682355c173f47dbb250175fb4eca718a8c91a20` — original deterministic tests;
- `9ce440755d1d70813d1043210d8bd8a28a650cd3` — compatibility rhythm tests;
- `71e553f13aa37a4c30615c094c2679b1e9504475` — structure-map tests;
- `85b175f60406fb47a81bfebfe36ba99e52ed029f` — structure-driven rhythm tests;
- `15bc52616bee054acea6a4d58c7cfd918b578c13` — contextual rhythm tests;
- `c3452d39702df616b52ecd0bac171af2bd099d12` — constrained decoder tests;
- `d684cd2a42ace038bff85637a2ef9a38b0c37371` — phrase optimizer tests;
- `1e0e9514193e76e0b80fd62415c53d801bccb234` — structure-fretboard invariance tests;
- `a49695e20ab20f830e31b9f160194cd5137e5f4d` — fresh raw evaluator tests.

Recent checkpoint commits:
- `3bc1c36c4d3fbeefe3a1243415de72b1a4a5a8cd` — 13/13 proof;
- `324420a20210a3cd88284b323968366d1e86773c` — 19/19 structure milestone;
- `d78b01c09707f3a11e876a9e500e788a2b6c4721` — 25/25 structure-rhythm milestone;
- `19512a5477cea0845629e0a80723566e5ee41364` — repaired interrupted 30/30 contextual checkpoint;
- `59c1e4977d4f69a6eb83282c29670d972e84fea8` — constrained decoder checkpoint;
- `7a2c029d2c0fe6153a47ee43ad75f240385d5482` — phrase optimizer checkpoint;
- `9ea044b935b6cdf245b8cd580f27b61b7ebc6204` — structure/fretboard integration checkpoint.

## CURRENT CLEAN PIPELINE LAYERS

### Structure and notation

- `structureMap.mjs`: explicit timing/measure contract, confidence/provenance, change-boundary validation, map-driven snapping/location.
- `structureRhythmNotation.mjs`: map-driven starts/ends, pickup/measure/beat segmentation, ties, rests, syncopation, displacement diagnostics, stable source identity.
- `contextualRhythmSpelling.mjs`: downstream readability only; standard/dotted/triplet values, weak-beat dotted merges, strong-beat ties, explicit rest spelling, phrase feel diagnostics.

### Playability and phrase motion

- `playableShapeDecoder.mjs`: exact-MIDI candidate states, unique strings, physical constraints, role-aware policies, explicit rejection reasons, no pitch dropping.
- `fretboardPathOptimizer.mjs`: deterministic phrase search over legal states using movement/string continuity only after playability is satisfied.
- `structureFretboardPath.mjs`: applies the selected path back onto events while protecting event IDs, cluster identity, MIDI, timing, structure positions, notation, provenance, and rests.

### Raw evaluator

`freshEvaluator.mjs` is intentionally scoreless.

Reports:
- structure-map presence/completeness;
- measure boundary consistency;
- downbeat consistency;
- tempo/meter/feel/measure/downbeat counts and confidence;
- source/output event counts and source-identity drift;
- exact MIDI preservation;
- onset/end displacement distributions;
- cluster timing consistency;
- resolved/unresolved duration counts;
- notation/tie/rest counts and incomplete notation;
- unresolved rhythm spelling;
- playable/unplayable assignments;
- unique-string chord violations;
- per-cluster fretted span/string span/center/open-string diagnostics;
- phrase movement, string-set changes, candidate counts, and unresolved path state;
- explicit independent failure codes.

Evaluator metadata explicitly contains:
- `compositeScoreDefined: false`;
- `compositeScore: null`;
- `legacyV143ScorerImported: false`.

No composite score formula exists in this fresh evaluator.

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
- fresh raw evaluator: **6/6 pass**.

Raw evaluator tests prove separately visible failures for:
- event-count drift;
- MIDI identity mismatch;
- source identity drift;
- structure boundary/downbeat/incomplete map problems;
- unplayable assignment;
- unique-string chord violation;
- unresolved duration;
- unresolved rhythm spelling;
- unresolved fretboard path.

A clean fixture produces zero failures and no composite score. Evaluation is deterministic and preserves raw movement diagnostics.

The full branch-wide suite has not been re-executed after the newest decoder/path/integration/evaluator additions because this container cannot resolve GitHub directly. Do not claim a new branch-wide total yet.

No Production/main, model/GPU, professional scorer, training, real-audio canary, or archived V143/Gomyway path was touched.

## CURRENT ENGINEERING MILESTONE

Define a stable **fresh analyzer → existing `/ai-tab` product-shell adapter** without changing the customer flow.

The adapter must project clean internal state into the existing page-facing fields, including where available:
- `generatedTab` or a stable successor textual representation;
- tuning;
- tempo;
- time signature;
- key signature if known;
- `analysisEngine`;
- techniques;
- render events;
- legacy `measureGrid` projection plus full `structureMap` for fresh consumers;
- confidence;
- difficulty;
- raw evaluator diagnostics/failure reasons for internal use;
- PDF artifact metadata where produced later.

It must not expose internal path/model complexity as a requirement for the existing preview/paywall/PDF code.

## NEXT EXECUTION ORDER

1. Inspect current `/ai-tab` analyzer/render/PDF input boundary read-only and implement/test the fresh adapter contract.
2. Only after deterministic structure/notation/fretboard stability, connect real audio in this order: **full-mixture structure analysis → structureMap → role-conditioned note evidence → clean event schema → notation → fretboard decoding**.
3. Map the fresh adapter into the existing preview → unlock → full PDF → email/download path.
4. Define the no-human-correction real-song acceptance gate before changing public copy.

## NON-NEGOTIABLES

- Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`.
- Canonical branch: `songsterr-fresh-pipeline-v1`.
- Archived V143/Gomyway remains archive/evidence only unless explicitly requested.
- Timing/measure structure precedes trusting note placement.
- Preserve detected MIDI/event identity; never silently alter notes for notation/fingering appearance.
- Never drop pitches merely to satisfy shape/path optimization.
- Preserve existing `/ai-tab` preview → unlock → full PDF → email/download customer flow.
- No Production or main changes.
- No accidental Modal/GPU/model/professional-scorer/training/real-audio activity.
- Keep this checkpoint updated after each meaningful milestone.
