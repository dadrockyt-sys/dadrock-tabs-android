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

Not:

**audio → loose notes → attempt to repair timing afterward**

`structureMap` must carry tempo/meter/feel segments, downbeats, explicit measure boundaries, pickup/anacrusis, beat/subdivision positions, confidence, and provenance. Downstream note/rhythm/tab stages consume this map directly.

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
- `e4e991ad3cdfe5b24e0a198f954acbe77e5ac6e9` — structure-event → optimized fretboard-path integration.

Current associated test commits:
- `c682355c173f47dbb250175fb4eca718a8c91a20` — original deterministic tests;
- `9ce440755d1d70813d1043210d8bd8a28a650cd3` — compatibility rhythm tests;
- `71e553f13aa37a4c30615c094c2679b1e9504475` — structure-map tests;
- `85b175f60406fb47a81bfebfe36ba99e52ed029f` — structure-driven rhythm tests;
- `15bc52616bee054acea6a4d58c7cfd918b578c13` — contextual rhythm tests;
- `c3452d39702df616b52ecd0bac171af2bd099d12` — constrained decoder tests;
- `d684cd2a42ace038bff85637a2ef9a38b0c37371` — phrase optimizer tests;
- `1e0e9514193e76e0b80fd62415c53d801bccb234` — structure-fretboard integration invariance tests.

Recent checkpoint commits:
- `3bc1c36c4d3fbeefe3a1243415de72b1a4a5a8cd` — 13/13 proof;
- `324420a20210a3cd88284b323968366d1e86773c` — 19/19 structure milestone;
- `d78b01c09707f3a11e876a9e500e788a2b6c4721` — 25/25 structure-rhythm milestone;
- `19512a5477cea0845629e0a80723566e5ee41364` — repaired interrupted 30/30 contextual checkpoint;
- `59c1e4977d4f69a6eb83282c29670d972e84fea8` — constrained decoder checkpoint;
- `7a2c029d2c0fe6153a47ee43ad75f240385d5482` — phrase optimizer checkpoint.

## CURRENT CLEAN PIPELINE LAYERS

### `structureMap.mjs`

Structure is explicit before note placement: tempo/meter/feel segments, pickup, measures, downbeats, beats/subdivisions, confidence/provenance, boundary validation, map-driven location/snapping.

### `structureRhythmNotation.mjs`

Uses the same structure map for onset/end projection, pickup/measure/beat segmentation, ties, rests, syncopation, provenance, and displacement diagnostics while preserving one source note = one event identity.

### `contextualRhythmSpelling.mjs`

Readability-only layer: standard/dotted/triplet values, weak-beat dotted merges, strong-beat tie preservation, explicit rest spelling, phrase feel diagnostics. It does not change MIDI/event identity.

### `playableShapeDecoder.mjs`

Enumerates exact-MIDI candidate shapes under tuning/capo, applies physical constraints, role-aware preferences, deterministic scoring, and explicit unresolved reasons. Never drops a pitch to make a shape easier.

### `fretboardPathOptimizer.mjs`

Dynamic-programming phrase search over only legal candidate states. Hard playability/pitch constraints precede movement/string-continuity costs. Unresolved onset aborts explicitly with source MIDI groups intact.

### `structureFretboardPath.mjs`

Pure downstream integration layer that maps the optimized phrase path back onto structure-first events.

Protected invariants:
- `eventId`;
- `sourceEventIndex`;
- `clusterId`;
- MIDI;
- source/projected starts and ends;
- measure/beat/fraction/pickup;
- tempo/time signature/feel;
- notation/ties;
- provenance;
- rests and structure map outside fretboard replacement.

Only fretboard assignment fields are replaced: string, fret, reconstructed MIDI, path metadata.

It refuses inconsistent timing inside a cluster instead of averaging or silently repairing it.

## VALIDATION STATUS

Earlier proven surfaces:
- original clean: **13/13 pass**;
- structure-first: **19/19 pass** after exact-boundary `[start, end)` fix;
- structure-driven event/rhythm: **25/25 pass**;
- contextual rhythm namespace run before interruption: **30/30 pass**.

New isolated proofs:
- constrained decoder: **5/5 pass**;
- decoder candidate enumeration + phrase optimizer combined: **10/10 pass**;
- decoder + phrase optimizer + structure integration combined: **15/15 pass**.

The 15-test combined proof establishes:
- targeted `[64] → [76] → [64]` phrase movement is reduced versus independent local choices;
- structure projected starts/ends and notation remain identical during fretboard optimization;
- rests remain unchanged;
- source event IDs/MIDI remain unchanged;
- simultaneous chord mapping preserves exact MIDI and unique strings;
- unresolved path leaves the event schema semantically untouched and reports failure explicitly;
- integration is deterministic;
- inconsistent projected timing within one cluster is rejected.

The full branch-wide suite has not been re-executed after the decoder/path/integration additions because this container cannot resolve GitHub directly. Do not claim a new branch-wide 45-test result yet.

No Production/main, model/GPU, professional scorer, training, real-audio canary, or archived V143/Gomyway path was touched.

## CURRENT ENGINEERING MILESTONE

Define a **fresh raw evaluator** for the clean structure-first pipeline. It must report diagnostics, not hide them behind a cosmetic composite score.

Required evaluator surface:
- structure-map completeness/confidence;
- tempo/meter/feel segment counts and measure/downbeat consistency;
- source vs output event count;
- exact MIDI preservation;
- onset/end displacement distribution;
- simultaneous-cluster preservation;
- unresolved duration count;
- notation segment/tie/rest completeness;
- unresolved rhythm spelling count;
- playable/unplayable assignment count;
- unique-string chord violations;
- fret-span/hand-position diagnostics;
- phrase total/max movement and string-set changes;
- explicit failure reasons array.

Any future composite score must be a later optional layer whose formula lives in source control next to these raw metrics.

## NEXT EXECUTION ORDER

1. Implement/test fresh raw evaluator.
2. Define a stable clean analyzer output contract for the existing `/ai-tab` renderer/PDF fields.
3. Only after deterministic structure/notation/fretboard stability, connect real audio in this order: **full-mixture structure analysis → structureMap → role-conditioned note evidence → clean event schema → notation → fretboard decoding**.
4. Map analyzer output into the existing preview → unlock → full PDF → email/download flow.
5. Define the no-human-correction real-song acceptance gate before changing public copy.

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
