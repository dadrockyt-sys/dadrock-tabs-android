# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-07 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`

This is the **only canonical fresh-chat checkpoint for the new Songsterr-inspired pipeline**.

Do not use the generic `docs/checkpoints/CURRENT_STATE.md` for this project. Do not resume the old V143/Gomyway investigation unless the user explicitly asks to return to that archived work.

## PRODUCT TARGET

Build an AI-first guitar/bass tab creator that can go from audio evidence to usable tab without a mandatory human correction step.

The immediate engineering priority is not a cosmetic score. It is preserving detected musical identity while progressively making timing, rhythm spelling, chord shapes, fretboard motion, and later real-audio inference musically coherent enough for product use.

## PROJECT BOUNDARY

The old branch `v143-contextual-prune-lobo` is archive/evidence only.

The new branch intentionally does **not** inherit old V143 scorer contracts, Gomyway percentages, correction plans, canary gates, professional-reference workflows, model budgets, or stale failed-test expectations as acceptance criteria.

Historical values such as `100% pitch / 90.321% onset / 69.004% note-count` are old evidence only. They do not define success for this fresh pipeline.

**Do not touch Production or main.**

Do not dispatch Modal/GPU/model-bearing workflows, professional scorers, training, optimizer sweeps, or real-audio canaries unless the user explicitly authorizes them later.

## SONGSTERR-INSPIRED ARCHITECTURE CLUES

Carry forward architecture ideas only:

1. preserve full-mixture context for global musical structure;
2. allow a role-specific/local carrier for note evidence;
3. make structure first-class: tempo, meter, pickup, straight/triplet feel;
4. make instrument configuration first-class: lead/rhythm/bass, tuning, capo;
5. fuse structure + note evidence before final timing/tab decoding;
6. group simultaneous notes before fretboard assignment;
7. solve simultaneous notes as a playable chord/shape, not independently;
8. keep detected note identity separate from notation/render representation;
9. add phrase-aware rhythm spelling and fretboard continuity before real-audio promotion.

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

### 2. Harden rhythm spelling beyond raw boundary splitting

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

### 3. Upgrade chord/shape decoding

Improve joint shape selection with:
- stronger fret-span constraints;
- open-string preference by role/context;
- impossible/stretch-shape rejection;
- stable deterministic tie-breaking;
- previous/next hand-position context.

Do not drop pitches merely to create an easier shape.

### 4. Add phrase-level fretboard path optimization

Use deterministic phrase-level search (beam/Viterbi-style is acceptable) over playable states.

Priority order:
1. pitch correctness;
2. physical playability;
3. compact hand movement;
4. stable position choices;
5. chord-shape continuity;
6. role-specific behavior.

### 5. Define the fresh evaluator

Report raw metrics before any composite score:
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

### 6. Only after deterministic notation/fretboard behavior is stable, connect real model/audio output

The first real-audio adapter should map model evidence into the clean event schema. It must not import the old V143 scorer/gate maze.

Keep Production untouched until a deliberate later promotion decision.

## FRESH-CHAT START INSTRUCTION

When starting a new chat, use:

`Please continue from docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md on branch songsterr-fresh-pipeline-v1. Keep that file updated often while you work. Do not resume the archived V143/Gomyway pipeline unless I explicitly ask.`

## NON-NEGOTIABLES

- canonical checkpoint is `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`;
- branch is `songsterr-fresh-pipeline-v1`;
- old V143 branch remains archive/evidence only;
- no Production or main changes;
- no accidental Modal/GPU/model/professional scorer/training activity;
- no legacy scorer or old failed test becomes a fresh-pipeline gate merely because it exists;
- detected note identity must not be silently altered merely to improve notation appearance;
- checkpoint this file after each meaningful architecture, implementation, or validation milestone.
