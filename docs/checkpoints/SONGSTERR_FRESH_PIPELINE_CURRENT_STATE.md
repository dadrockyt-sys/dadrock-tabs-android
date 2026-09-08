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
- `a0fbc5fc54aa1bf91a7cc199f373d5018d158a11` — first-class musical event + rhythm notation layer;
- `9ce440755d1d70813d1043210d8bd8a28a650cd3` — six rhythm/event-schema invariant tests;
- `3bc1c36c4d3fbeefe3a1243415de72b1a4a5a8cd` — checkpoint recording first proven 13/13 local clean-suite pass;
- `e9b56a0fdceed2dafc9715f22b5c93954098877e` — first-class `structureMap` implementation and structure-conditioned note core;
- `71e553f13aa37a4c30615c094c2679b1e9504475` — six `structureMap`/structure-conditioned core tests.

### Deterministic core

`songsterr_pipeline/index.mjs` provides the original clean deterministic baseline:
- explicit structure/instrument conditioning;
- pickup-aware measure timing;
- stable simultaneous-onset clustering;
- joint unique-string playable chord-shape solving;
- exact MIDI reconstruction checks;
- no intentional note dropping;
- raw diagnostics for event count, pitch preservation, timing movement, and unresolved playable assignments.

This original `structurePrior` path remains temporarily for backward compatibility and its original tests.

### Musical event / notation layer

`songsterr_pipeline/rhythmNotation.mjs` preserves one source note = one stable event identity while notation may contain multiple tied segments.

Current behavior includes source `end`/`duration`, unresolved missing duration, structure-grid duration projection, minimum subdivision duration for collapsed snaps, beat/measure tie splitting, rest-gap diagnostics without fake MIDI notes, and straight/triplet subdivision behavior.

### First-class `structureMap`

`songsterr_pipeline/structureMap.mjs` now makes structure explicit before note placement.

It currently provides:
- tempo segments with confidence/provenance;
- meter segments with confidence/provenance;
- straight/triplet feel segments with confidence/provenance;
- explicit pickup duration;
- materialized pickup/full measures;
- explicit measure start/end boundaries;
- materialized downbeats;
- beat boundaries;
- subdivision timestamps inside beats;
- map-level confidence/provenance;
- continuity/non-overlap validation;
- rejection of tempo/meter/feel changes that do not align to a measure boundary;
- half-open segment semantics so a structural change takes effect exactly at its boundary;
- `locateInStructureMap(...)`;
- `snapTimestampToStructureMap(...)`;
- `runStructureMappedCore(...)`, whose note timing consumes the map directly before fretboard assignment.

The structure-conditioned core preserves source event identity/MIDI and uses the same deterministic unique-string shape solver after map-based timing is resolved.

## VALIDATION STATUS

### Original clean 13-test surface — PROVEN PASSING

On 2026-09-08, the exact branch-current original `songsterr_pipeline/` implementation and both committed original test files were mirrored into an isolated local Node runtime and executed with:

`node --test tests/pipeline.test.mjs tests/rhythmNotation.test.mjs`

Result: **13/13 pass, 0 fail**.

This proves the committed original invariants for exact MIDI preservation, zero source-event-count drift in tested fixtures, stable non-chain onset clustering, unique-string playable chord assignment, tuning/capo reconstruction, pickup-aware positioning, beat/measure ties, rest diagnostics without note inflation, straight/triplet subdivision behavior, and explicit unresolved duration.

### Expanded structure-first clean surface — PROVEN PASSING

After implementing `structureMap`, the exact local implementation corresponding to commits `e9b56a0` + `71e553f` was executed with:

`node --test tests/pipeline.test.mjs tests/rhythmNotation.test.mjs tests/structureMap.test.mjs`

Final result:
- tests: **19**
- pass: **19**
- fail: **0**
- cancelled: **0**
- skipped: **0**

The first expanded run intentionally caught a real boundary defect: a tempo/meter segment ending exactly at a change timestamp was still selected at that timestamp. The interval lookup was corrected to half-open `[start, end)` semantics, after which all 19 tests passed.

New proven structure-first behavior includes:
- pickup/downbeat/measure/beat/subdivision materialization;
- explicit map-driven snapping/location;
- tempo change applied exactly at a measure boundary;
- meter change applied exactly at a measure boundary;
- slightly spread chord attacks clustered musically then snapped against the map;
- exact MIDI/event-count preservation through the structure-conditioned note stage;
- unique-string playable chord assignment after structural timing;
- rejection of mid-measure structural changes instead of silently warping notation.

No Production/main state, model/GPU workflow, professional scorer, training path, real-audio canary, or archived V143/Gomyway pipeline was touched during either validation.

## CURRENT ENGINEERING MILESTONE

Complete the **structure-first synthetic fixture surface** and connect `structureMap` into the musical-event/rhythm notation path so duration, ties, rests, and syncopation are derived from the same first-class structure contract rather than the old compatibility grid.

Still needed in the next clean step:
- syncopated attacks around beat boundaries;
- notes crossing beat/measure boundaries using `structureMap` directly;
- straight vs triplet structure-map fixtures;
- pickup edge cases using explicit map boundaries;
- explicit quantization displacement diagnostics at event/phrase level;
- structure-map-driven duration/end projection and rest spelling diagnostics.

## NEXT EXECUTION ORDER

1. Finish structure-first synthetic fixtures and make musical event/rhythm notation consume `structureMap` directly.
2. Harden contextual rhythm spelling: beat-strength-aware ties, dotted values, explicit rest spelling, syncopation, pickup edge cases, phrase feel consistency, quantization displacement diagnostics.
3. Upgrade local chord/shape decoding: stronger fret-span/stretch constraints, role-aware open-string preference, impossible-shape rejection, deterministic tie-breaking, neighboring hand-position context. Never drop pitches merely to make fingering easier.
4. Add phrase-level fretboard path optimization with pitch correctness and physical playability ahead of movement aesthetics.
5. Define a fresh evaluator that reports raw structure, event, pitch, timing, playability, motion, notation, tie/rest, and unresolved-duration diagnostics before any composite score.
6. Only after the deterministic structure/notation/fretboard system is stable, connect real-audio evidence in this order: **full-mixture structure analysis → structureMap → role-conditioned note evidence → clean event schema → notation → fretboard decoding**.
7. Map clean analyzer output into the existing `/ai-tab` metadata/render/PDF contract.
8. Define the no-human-correction product acceptance gate across multiple real songs/roles before changing public copy.

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
