# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-07 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`

This is the **only canonical fresh-chat checkpoint for the new Songsterr-inspired pipeline**.

Do not use the generic `docs/checkpoints/CURRENT_STATE.md` for this project. Do not resume the old V143/Gomyway investigation unless the user explicitly asks to return to that archived work.

## PRODUCT TARGET

Build an AI-first guitar/bass tab creator that can go from audio evidence to usable tab without a mandatory human correction step.

The immediate engineering priority is not a cosmetic score. It is preserving detected musical identity while progressively making timing, rhythm spelling, chord shapes, fretboard motion, and later real-audio inference musically coherent enough for product use.

## FOUNDATIONAL PROCESSING ORDER — TIMING AND MEASURES FIRST

This is a **non-negotiable architectural rule** for the fresh pipeline.

The Songsterr-inspired public clues discussed with the user strongly reinforce that timing and measure structure belong at the beginning of transcription, not as a cleanup stage after note detection. This is an architectural inference from public clues, not a claim about Songsterr's private implementation.

When real audio is introduced, the pipeline should conceptually operate in this order:

1. **Analyze the full mixture for global structure before trusting individual note placement.**
2. Resolve or estimate the song's timing scaffold:
   - tempo / tempo changes;
   - downbeats;
   - time signature / meter;
   - measure boundaries;
   - pickup/anacrusis;
   - straight vs triplet feel;
   - beat/subdivision grid confidence.
3. Represent this as an explicit structure/measure map that becomes the coordinate system for the rest of transcription.
4. Perform or interpret role-specific note evidence **conditioned on that structure map**, rather than independently detecting notes and snapping them afterward.
5. Group simultaneous attacks relative to the musical grid.
6. Resolve durations, rests, ties, syncopation, and rhythmic spelling inside known beats/measures.
7. Decode playable string/fret/chord shapes only after musical timing identity is established.
8. Optimize phrase-level fretboard movement while preserving the timing/measure map and note identity.

The core principle is:

**Audio → timing/measure map → conditioned note evidence → rhythm/notation → playable tab.**

Not:

**Audio → loose notes → attempt to repair timing afterward.**

Why this matters for a no-human-correction product:
- a wrong measure boundary can make many otherwise correct pitches look wrong;
- a wrong downbeat can shift an entire phrase musically;
- duration and rest notation cannot be reliable without beat/measure context;
- chord simultaneity depends on a stable timing reference;
- phrase-aware fretboard choices are more meaningful once note groups and rhythmic positions are known;
- timing errors compound across a song, so structural uncertainty must be surfaced early rather than hidden downstream.

Future real-audio work should therefore maintain separate confidence/provenance for **structure inference** and **note inference** and allow the note stage to consume the resolved structure map directly.

## PROJECT BOUNDARY

The old branch `v143-contextual-prune-lobo` is archive/evidence only.

The new branch intentionally does **not** inherit old V143 scorer contracts, Gomyway percentages, correction plans, canary gates, professional-reference workflows, model budgets, or stale failed-test expectations as acceptance criteria.

Historical values such as `100% pitch / 90.321% onset / 69.004% note-count` are old evidence only. They do not define success for this fresh pipeline.

**Do not touch Production or main.**

Do not dispatch Modal/GPU/model-bearing workflows, professional scorers, training, optimizer sweeps, or real-audio canaries unless the user explicitly authorizes them later.

## SONGSTERR-INSPIRED ARCHITECTURE CLUES

Carry forward architecture ideas only:

1. timing/measure structure is foundational and should be established before trusting note placement;
2. preserve full-mixture context for global musical structure;
3. allow a role-specific/local carrier for note evidence;
4. make structure first-class: tempo, tempo changes, downbeat, meter, measures, pickup, straight/triplet feel;
5. make instrument configuration first-class: lead/rhythm/bass, tuning, capo;
6. condition/fuse note evidence with the structure map before final timing/tab decoding;
7. group simultaneous notes before fretboard assignment;
8. solve simultaneous notes as a playable chord/shape, not independently;
9. keep detected note identity separate from notation/render representation;
10. add phrase-aware rhythm spelling and fretboard continuity before real-audio promotion.

Public Songsterr observations are clues only, not claims about Songsterr private implementation.

## FRESH IMPLEMENTATION PRESENT

Fresh namespace:
- `songsterr_pipeline/`

Key commits:
- `a51f87d24af0cbcb34d9bc477cdef6bef490c16d` — fresh reset checkpoint
- `212be220b96de687f55cce2ca3e7698b1ac9dadb` — first isolated deterministic Songsterr core
- `c682355c173f47dbb250175fb4eca718a8c91a20` — first seven synthetic tests
- `f0ac845c2820acb301e801060920d97dd1d4f956` — fresh pipeline README
- `c39943f176fb557ed9b4a68c1ec609ce1e698aa0` — manual-only CPU test workflow
- `a0fbc5fc54aa1bf91a7cc199f373d5018d158a11` — first-class musical event + rhythm notation layer
- `9ce440755d1d70813d1043210d8bd8a28a650cd3` — six rhythm/event-schema invariant tests

### Deterministic core

`songsterr_pipeline/index.mjs` currently provides:
- explicit structure/instrument conditioning;
- pickup-aware measure timing;
- stable simultaneous-onset clustering;
- joint unique-string playable chord-shape solving;
- exact MIDI reconstruction checks;
- no intentional note dropping;
- raw diagnostics for event count, pitch preservation, timing movement, and unresolved playable assignments.

### First-class musical event / notation layer

`songsterr_pipeline/rhythmNotation.mjs` was added as a separate layer above the deterministic core.

The module intentionally keeps **one source note = one event identity** while allowing notation to contain multiple tied segments.

Current schema fields include:
- stable `eventId` and `sourceEventIndex`;
- chord `clusterId`;
- exact MIDI pitch;
- source start/end/duration;
- projected start/end/duration;
- onset/end movement flags;
- measure/beat/fraction/pickup position;
- role/tuning/capo context;
- string/fret/reconstructed MIDI/shape state;
- straight/triplet feel;
- notation segments;
- tie-from-previous / tie-to-next flags;
- reference-blind provenance.

Current rhythm behavior:
- source `end` or `duration` is accepted explicitly;
- missing duration stays unresolved rather than being silently invented;
- duration ends snap to the same structure grid as onsets;
- a collapsed snapped duration receives a minimum one-subdivision duration;
- durations are split at beat boundaries;
- crossing a beat or measure boundary creates tied notation segments without duplicating the source event;
- silence between duration-resolved onset clusters is represented as a `rests` diagnostic, never as a fake MIDI note;
- triplet feel uses three subdivisions per beat unit;
- event-count and MIDI identity are designed to remain invariant through notation spelling.

### Fresh tests

Original core test surface:
- 7 synthetic/reference-blind tests.

New notation test surface:
- 6 additional synthetic/reference-blind tests covering:
  1. one source identity / exact MIDI preservation;
  2. beat-boundary tie splitting;
  3. measure-boundary tie splitting;
  4. rest-gap diagnostics without fake notes;
  5. triplet subdivision behavior;
  6. unresolved duration remaining explicit.

Total committed fresh tests: **13**.

IMPORTANT: these tests are committed but have **not yet been executed in this chat/tool environment**. Do not claim they pass until an actual Node test run occurs.

The dedicated workflow remains manual-only and has not been dispatched.

## NEXT STEPS — IN ORDER

### 1. Execute only the fresh 13-test synthetic suite when a safe execution path is available

Run only `songsterr_pipeline/`.

Required proof:
- exact MIDI pitch preservation;
- no event-count drift;
- stable simultaneous clustering;
- legal unique-string chord assignment;
- tuning/capo correctness;
- pickup-aware positioning;
- beat/measure tie segmentation;
- rest diagnostics without note inflation;
- straight/triplet grid behavior.

Do not let old V143 CI failures block this proof.

### 2. Make the structure map a first-class object before any real-audio adapter

Before connecting actual audio/model evidence, define an explicit structure representation capable of carrying:
- tempo and later tempo changes;
- time signature and later meter changes;
- downbeat locations;
- measure start/end boundaries;
- pickup duration;
- beat/subdivision positions;
- straight/triplet feel;
- confidence and provenance per structural decision.

The note/audio adapter must consume this structure map rather than treating it as optional postprocessing metadata.

### 3. Harden rhythm spelling beyond raw boundary splitting

Current rhythm notation is deliberately conservative. Next add contextual spelling for:
- syncopation preference;
- beat-strength-aware tie decisions;
- dotted values where cleaner than ties;
- explicit rest spelling by measure/beat;
- pickup edge cases;
- phrase-level straight/triplet consistency;
- quantization displacement diagnostics;
- preservation of source identity while notation is rewritten.

Keep source MIDI/count invariant.

### 4. Upgrade chord/shape decoding

Improve joint shape selection with:
- stronger fret-span constraints;
- open-string preference by role/context;
- impossible/stretch-shape rejection;
- stable deterministic tie-breaking;
- previous/next hand-position context.

Do not drop pitches merely to create an easier shape.

### 5. Add phrase-level fretboard path optimization

Use deterministic phrase-level search (beam/Viterbi-style is acceptable) over playable states.

Priority order:
1. pitch correctness;
2. physical playability;
3. compact hand movement;
4. stable position choices;
5. chord-shape continuity;
6. role-specific behavior.

### 6. Define the fresh evaluator

Report raw metrics before any composite score:
- structure-map completeness/confidence;
- measure/downbeat consistency;
- source notes vs output events;
- exact MIDI preservation;
- onset-cluster preservation;
- onset/end displacement distributions;
- simultaneous-group preservation;
- playable/unplayable assignments;
- fret-span and hand-motion diagnostics;
- notation completeness by measure;
- ties/rests/duration consistency;
- unresolved-duration count.

Any later composite score formula must live in source control beside these raw metrics.

### 7. Only after deterministic structure/notation/fretboard behavior is stable, connect real model/audio output

The first real-audio adapter should follow the foundational order:

**full-mixture structure analysis → structure/measure map → conditioned note evidence → clean event schema → notation → fretboard decoding.**

It must not import the old V143 scorer/gate maze.

Keep Production untouched until a deliberate later promotion decision.

## FRESH-CHAT START INSTRUCTION

When starting a new chat, use:

`Please continue from docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md on branch songsterr-fresh-pipeline-v1. Keep that file updated often while you work. Timing/measure structure is foundational and must precede trusting note placement. Do not resume the archived V143/Gomyway pipeline unless I explicitly ask.`

## NON-NEGOTIABLES

- canonical checkpoint is `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`;
- branch is `songsterr-fresh-pipeline-v1`;
- old V143 branch remains archive/evidence only;
- **timing/measure structure must be established before trusting note placement in real-audio processing**;
- the structure map must be first-class and consumed by downstream note/rhythm/tab stages;
- no Production or main changes;
- no accidental Modal/GPU/model/professional scorer/training activity;
- no legacy scorer or old failed test becomes a fresh-pipeline gate merely because it exists;
- detected note identity must not be silently altered merely to improve notation appearance;
- checkpoint this file after each meaningful architecture, implementation, or validation milestone.
