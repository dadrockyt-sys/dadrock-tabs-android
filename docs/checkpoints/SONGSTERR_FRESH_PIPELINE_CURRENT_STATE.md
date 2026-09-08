# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-08 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`

This is the **only canonical fresh-chat checkpoint for the new Songsterr-inspired pipeline**.

Do not use the generic `docs/checkpoints/CURRENT_STATE.md` for this project. Do not resume the old V143/Gomyway investigation unless the user explicitly asks to return to that archived work.

## PRODUCT TARGET

Build an AI-first guitar/bass tab creator that can go from uploaded audio to a usable finished tab without a mandatory human correction step.

The immediate engineering priority is musical correctness and stability, not a cosmetic score. Preserve detected musical identity while progressively making structure, timing, rhythm spelling, chord shapes, fretboard motion, techniques, and final rendering coherent enough for product use.

Do not change public accuracy promises yet. The current `/ai-tab` page copy still allows for occasional corrections; only change that wording after the clean pipeline earns a real no-human-correction acceptance standard.

## FOUNDATIONAL RULE — TIMING AND MEASURES COME FIRST

This is non-negotiable for the fresh pipeline.

Intended real-audio order:

**full-mixture audio → timing/measure map → structure-conditioned note evidence → rhythm/notation → playable tab → render metadata**

Not:

**audio → loose notes → attempt to repair timing afterward**

The structure layer must resolve or explicitly carry uncertainty for tempo/tempo changes, downbeats, meter/meter changes, measure boundaries, pickup/anacrusis, straight/triplet feel, beat/subdivision positions, confidence, and provenance. Downstream note/rhythm/tab stages must consume that resolved structure directly.

## EXISTING `/ai-tab` PRODUCT SHELL — PRESERVE IT

Replace the transcription brain; preserve the proven customer journey:

**audio upload → AI analysis → analyzer metadata → technique/render events → watermarked preview PDF → PayPal/free-token unlock reference → full tab PDF → browser download + email delivery**

Existing page-facing fields include `generatedTab`, `tuning`, `tempo`, `timeSignature`, `keySignature`, `analysisEngine`, `techniques`, `renderEvents`, `measureGrid`, `confidence`, `difficulty`, and PDF artifact metadata where available.

The fresh core must not bypass or discard the preview/paywall/full-PDF flow.

## PROJECT BOUNDARY

- Old branch `v143-contextual-prune-lobo` is archive/evidence only.
- Historical Gomyway/V143 values and scorer contracts are not fresh-pipeline acceptance criteria.
- Do not touch Production or main.
- Do not dispatch Modal/GPU/model-bearing workflows, professional scorers, training, optimizer sweeps, or real-audio canaries unless the user explicitly authorizes them.
- Old failed CI/tests do not become fresh blockers merely because they exist.

## FRESH IMPLEMENTATION PRESENT

Fresh namespace: `songsterr_pipeline/`

Recorded clean-line commits:
- `a51f87d24af0cbcb34d9bc477cdef6bef490c16d` — fresh reset checkpoint;
- `212be220b96de687f55cce2ca3e7698b1ac9dadb` — first isolated deterministic Songsterr core;
- `c682355c173f47dbb250175fb4eca718a8c91a20` — first seven synthetic tests;
- `f0ac845c2820acb301e801060920d97dd1d4f956` — fresh pipeline README;
- `c39943f176fb557ed9b4a68c1ec609ce1e698aa0` — manual-only CPU test workflow;
- `a0fbc5fc54aa1bf91a7cc199f373d5018d158a11` — compatibility musical-event + rhythm notation layer;
- `9ce440755d1d70813d1043210d8bd8a28a650cd3` — six compatibility rhythm/event-schema invariant tests;
- `3bc1c36c4d3fbeefe3a1243415de72b1a4a5a8cd` — checkpoint recording first proven 13/13 local clean-suite pass;
- `e9b56a0fdceed2dafc9715f22b5c93954098877e` — first-class `structureMap` implementation and structure-conditioned note core;
- `71e553f13aa37a4c30615c094c2679b1e9504475` — six `structureMap`/structure-conditioned core tests;
- `324420a20210a3cd88284b323968366d1e86773c` — checkpoint recording the 19/19 structure-first milestone;
- `89c6a12d604dd203b65f4e4015d7d1d246f05a9f` — structure-map-driven musical event/rhythm notation schema;
- `85b175f60406fb47a81bfebfe36ba99e52ed029f` — six structure-map-driven rhythm/notation tests;
- `d78b01c09707f3a11e876a9e500e788a2b6c4721` — checkpoint recording the 25/25 structure-driven baseline;
- `b6a3a70369c1d5af269b95428a4a67e0bb2a99d5` — contextual rhythm spelling layer;
- `15bc52616bee054acea6a4d58c7cfd918b578c13` — contextual rhythm spelling tests.

### Compatibility deterministic core

`songsterr_pipeline/index.mjs` provides the original clean deterministic baseline with explicit conditioning, pickup-aware timing, stable onset clustering, unique-string shape solving, exact MIDI reconstruction, no intentional note dropping, and raw count/pitch/timing/playability diagnostics.

Its `structurePrior` path remains temporarily for backward compatibility and the original tests. New work should use `structureMap` directly.

### Compatibility rhythm layer

`songsterr_pipeline/rhythmNotation.mjs` preserves one source note = one stable event identity while notation may contain multiple tied segments. It remains as compatibility evidence; the first-class structure path is now `structureRhythmNotation.mjs`.

### First-class `structureMap`

`songsterr_pipeline/structureMap.mjs` establishes structure before note placement and carries tempo/meter/feel segments, pickup, explicit measures/downbeats/beats/subdivisions, confidence/provenance, boundary validation, map-driven location/snapping, and a structure-conditioned note core.

### First-class structure-driven event / notation layer

`songsterr_pipeline/structureRhythmNotation.mjs` consumes `structureMap` directly for note starts, note ends, duration projection, beat/measure segmentation, pickup crossings, ties, rest gaps, feel, provenance, and onset/end displacement diagnostics while preserving exact MIDI and one source note = one event identity.

### Contextual rhythm spelling

`songsterr_pipeline/contextualRhythmSpelling.mjs` is a downstream readability layer. It does not change source MIDI or event identity.

Current behavior:
- recognizes standard note values in beat-relative units;
- recognizes dotted values;
- recognizes triplet values;
- can merge a mechanically split duration across a weak beat when one dotted value is musically cleaner;
- preserves ties across strong-beat boundaries such as beat 3 in 4/4;
- explicitly segments/spells rest gaps by beat boundaries without creating note events;
- reports phrase-level straight/triplet feel consistency/change diagnostics;
- leaves unresolved spellings visible rather than silently fabricating notation.

## VALIDATION STATUS

### Original clean surface

`node --test tests/pipeline.test.mjs tests/rhythmNotation.test.mjs`

Result: **13/13 pass, 0 fail**.

### First-class structure-map surface

Expanded suite result: **19/19 pass, 0 fail** after correcting exact-boundary lookup to half-open `[start, end)` semantics.

### Structure-driven rhythm/notation surface

Complete namespace result after `structureRhythmNotation.mjs`: **25/25 pass, 0 fail**.

### Contextual rhythm spelling surface — CURRENT PROVEN BASELINE

Before the chat interruption, the complete clean namespace suite including `contextualRhythmSpelling.test.mjs` was executed and reported:
- tests: **30**
- pass: **30**
- fail: **0**

The interruption occurred while writing this checkpoint, not while creating the implementation/tests. Branch head verification after resuming confirmed commit `15bc52616bee054acea6a4d58c7cfd918b578c13` is intact.

New proven contextual behavior includes:
- standard/dotted/triplet duration recognition;
- weak-beat dotted merge when cleaner than a tie;
- strong-beat tie preservation;
- explicit rest spelling without fake MIDI notes;
- phrase-level feel-change diagnostics;
- source event IDs and MIDI unchanged through contextual spelling.

No Production/main state, model/GPU workflow, professional scorer, training path, real-audio canary, or archived V143/Gomyway pipeline was touched.

## CURRENT ENGINEERING MILESTONE

Upgrade local playable chord/shape decoding while keeping pitch correctness and structure timing immutable.

Next clean goals:
- stronger fret-span/stretch constraints;
- role-aware open-string preference;
- impossible-shape rejection rather than forced awkward fingering;
- deterministic tie-breaking;
- previous/next hand-position context hooks;
- raw shape diagnostics including fret span, string span, open-string count, hand-position center, and rejection reason;
- never drop pitches merely to make fingering easier.

After local shape decoding is stable, add phrase-level fretboard path optimization over candidate playable states.

## NEXT EXECUTION ORDER

1. Upgrade local chord/shape decoding with stronger physical constraints and diagnostics.
2. Add phrase-level fretboard path optimization with pitch correctness and physical playability ahead of movement aesthetics.
3. Define a fresh evaluator that reports raw structure, event, pitch, timing, playability, motion, notation, tie/rest, and unresolved-duration diagnostics before any composite score.
4. Only after the deterministic structure/notation/fretboard system is stable, connect real-audio evidence in this order: **full-mixture structure analysis → structureMap → role-conditioned note evidence → clean event schema → notation → fretboard decoding**.
5. Map clean analyzer output into the existing `/ai-tab` metadata/render/PDF contract.
6. Define the no-human-correction product acceptance gate across multiple real songs/roles before changing public copy.

## NON-NEGOTIABLES

- Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`.
- Canonical branch: `songsterr-fresh-pipeline-v1`.
- Archived V143/Gomyway work remains archive/evidence only unless explicitly requested.
- Timing/measure structure precedes trusting note placement.
- `structureMap` is first-class and must be consumed by downstream note/rhythm/tab stages.
- Preserve detected MIDI/event identity; never silently alter notes to improve notation appearance.
- Preserve existing `/ai-tab` metadata → technique/render → watermarked preview → PayPal/free-token unlock reference → full PDF → email/download flow.
- No Production or main changes.
- No accidental Modal/GPU/model/professional-scorer/training/real-audio activity.
- Keep this checkpoint updated after each meaningful architecture, implementation, or validation milestone.
