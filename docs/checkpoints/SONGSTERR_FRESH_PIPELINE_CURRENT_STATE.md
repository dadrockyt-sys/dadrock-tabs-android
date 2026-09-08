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

This is a **non-negotiable architectural rule** for the fresh pipeline.

The Songsterr-inspired public clues discussed with the user strongly reinforce that timing and measure structure belong at the beginning of transcription, not as cleanup after loose note detection. This is an architectural inference from public clues, not a claim about Songsterr's private implementation.

The intended real-audio processing order is:

1. analyze the **full mixture** for global musical structure;
2. resolve/estimate the timing scaffold:
   - tempo and later tempo changes;
   - downbeats;
   - time signature / meter and later meter changes;
   - measure boundaries;
   - pickup/anacrusis;
   - straight vs triplet feel;
   - beat/subdivision grid confidence;
3. materialize that result as a first-class **structure/measure map**;
4. obtain or interpret lead/rhythm/bass note evidence **conditioned on that structure map**;
5. group simultaneous attacks relative to the musical grid;
6. resolve durations, rests, ties, syncopation, and rhythmic spelling inside known beats/measures;
7. decode playable string/fret/chord shapes only after timing identity is established;
8. optimize phrase-level fretboard movement while preserving note identity and the structure map;
9. produce stable analyzer metadata/technique/render events for the existing product renderer.

Core principle:

**Audio → timing/measure map → conditioned note evidence → rhythm/notation → playable tab → render metadata.**

Not:

**Audio → loose notes → attempt to repair timing afterward.**

Why this is essential for a no-human-correction product:
- wrong downbeats or measure boundaries can corrupt an otherwise correct phrase;
- duration/rest notation cannot be reliable without beat/measure context;
- chord simultaneity depends on a stable timing reference;
- phrase-level fretboard choices become meaningful only after note groups and rhythmic positions are known;
- structural mistakes compound across a song, so structure uncertainty must be explicit early.

Future real-audio work must therefore keep separate confidence/provenance for **structure inference** and **note inference**, with the note stage consuming the resolved structure map directly.

## EXISTING `/ai-tab` PRODUCT SHELL — PRESERVE IT

The fresh work is replacing the **transcription brain**, not the existing customer/product shell in `app/ai-tab/page.js`.

Preserve this customer flow:

**audio upload → AI analysis → analyzer metadata → technique/render events → watermarked preview PDF → unlock/payment reference → full tab PDF → browser download + email delivery**

The current page passes analyzer output into preview/final PDF generation, including:
- `generatedTab`;
- `tuning`;
- `tempo`;
- `timeSignature`;
- `keySignature`;
- `analysisEngine`;
- `techniques`;
- `renderEvents`;
- `measureGrid`;
- `confidence`;
- `difficulty`;
- PDF artifact metadata where available.

The current product shell already supports:
- locked watermarked PDF preview;
- PayPal unlock using an order ID/reference;
- free-token unlock using a token reference;
- finished PDF generation;
- browser download;
- email delivery.

Treat the unlock reference/token behavior as a product boundary. A later unified purchase-token abstraction can be added if useful, but the fresh transcription core must **not bypass or discard** the preview/paywall/full-PDF flow.

Product rule:

**Replace the transcription brain; preserve the proven customer journey.**

## PROJECT BOUNDARY

The old branch `v143-contextual-prune-lobo` is archive/evidence only.

The fresh branch intentionally does **not** inherit old V143 scorer contracts, Gomyway percentages, correction plans, canary gates, professional-reference workflows, model budgets, or stale failed-test expectations as acceptance criteria.

Historical values such as `100% pitch / 90.321% onset / 69.004% note-count` are old evidence only. They do not define success for this fresh pipeline.

**Do not touch Production or main.**

Do not dispatch Modal/GPU/model-bearing workflows, professional scorers, training, optimizer sweeps, or real-audio canaries unless the user explicitly authorizes them later.

## FRESH IMPLEMENTATION PRESENT

Fresh namespace:
- `songsterr_pipeline/`

Key commits already recorded for this clean line:
- `a51f87d24af0cbcb34d9bc477cdef6bef490c16d` — fresh reset checkpoint;
- `212be220b96de687f55cce2ca3e7698b1ac9dadb` — first isolated deterministic Songsterr core;
- `c682355c173f47dbb250175fb4eca718a8c91a20` — first seven synthetic tests;
- `f0ac845c2820acb301e801060920d97dd1d4f956` — fresh pipeline README;
- `c39943f176fb557ed9b4a68c1ec609ce1e698aa0` — manual-only CPU test workflow;
- `a0fbc5fc54aa1bf91a7cc199f373d5018d158a11` — first-class musical event + rhythm notation layer;
- `9ce440755d1d70813d1043210d8bd8a28a650cd3` — six rhythm/event-schema invariant tests.

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

`songsterr_pipeline/rhythmNotation.mjs` keeps **one source note = one stable event identity** while allowing notation to contain multiple tied segments.

Current concepts include:
- stable event/source identity;
- chord-cluster identity;
- exact MIDI pitch;
- source and projected start/end/duration;
- measure/beat/fraction/pickup position;
- role/tuning/capo context;
- string/fret/reconstructed MIDI/shape state;
- straight/triplet feel;
- notation segments;
- ties;
- rest diagnostics;
- reference-blind provenance.

Current rhythm behavior:
- explicit source `end` or `duration` is accepted;
- missing duration remains unresolved rather than silently invented;
- duration ends use the structure grid;
- collapsed snapped durations receive a minimum subdivision duration;
- durations split at beat boundaries;
- beat/measure crossings become tied notation segments without duplicating source-note identity;
- silence between duration-resolved onset clusters is represented diagnostically, never as fake MIDI notes;
- triplet feel uses three subdivisions per beat unit;
- event-count and MIDI identity are intended to remain invariant through notation spelling.

### Fresh tests

Committed fresh synthetic/reference-blind tests: **13 total**.

Coverage includes:
- structure/role/tuning/capo serialization;
- pickup-aware measure-grid snapping;
- onset clustering without chain merge;
- exact playable-position MIDI reconstruction with capo;
- simultaneous unique-string chord assignment;
- end-to-end event/count/pitch preservation;
- invalid tuning rejection;
- stable source identity;
- beat-boundary ties;
- measure-boundary ties;
- rest-gap diagnostics without fake notes;
- triplet subdivision behavior;
- unresolved duration remaining explicit.

IMPORTANT: these tests are committed but have **not yet been executed in this chat/tool environment**. Do not claim they pass until an actual Node test run occurs.

The dedicated fresh workflow remains manual-only and has not been dispatched.

## NEXT SESSION — EXECUTION ORDER

### 1. Validate only the clean 13-test surface

When a safe execution path is available, run only `songsterr_pipeline/`.

First proof must establish:
- exact MIDI preservation;
- no source-event-count drift;
- stable simultaneous clustering;
- legal unique-string chord assignment;
- tuning/capo correctness;
- pickup-aware positioning;
- beat/measure tie segmentation;
- rest diagnostics without note inflation;
- straight/triplet grid behavior.

Old V143 CI failures are not blockers.

### 2. Make `structureMap` the first-class contract of the fresh analyzer

Before connecting new real-audio/model work, define a stable structure object capable of carrying:
- tempo segments / tempo changes;
- meter segments / meter changes;
- downbeat timestamps;
- measure start/end boundaries;
- pickup duration;
- beat/subdivision positions;
- straight/triplet feel;
- confidence and provenance for every structural decision.

The note stage must consume this object. Do not treat `measureGrid` as optional metadata generated after note inference.

### 3. Build structure-first synthetic fixtures

Add deterministic fixtures where pitches are intentionally simple but structure is challenging:
- pickup into measure 1;
- syncopated attacks around beat boundaries;
- notes crossing beats/measures;
- straight vs triplet ambiguity;
- tempo-change boundary;
- meter-change boundary;
- chord attacks slightly spread in raw time but musically simultaneous.

These tests should prove that the structure map controls musical interpretation before fretboard/render decisions.

### 4. Harden contextual rhythm spelling

Extend beyond raw boundary splitting with:
- beat-strength-aware ties;
- dotted values where cleaner than ties;
- explicit rest spelling by beat/measure;
- syncopation-aware notation;
- pickup edge cases;
- phrase-level straight/triplet consistency;
- quantization displacement diagnostics.

Preserve source MIDI and event identity.

### 5. Upgrade local chord/shape decoding

Improve joint shape selection with:
- stronger fret-span/stretch constraints;
- role-aware open-string preference;
- impossible-shape rejection;
- deterministic tie-breaking;
- previous/next hand-position context.

Do not drop pitches merely to make a fingering easier.

### 6. Add phrase-level fretboard path optimization

Use deterministic phrase-level search (beam/Viterbi-style is acceptable) over playable states.

Priority order:
1. pitch correctness;
2. physical playability;
3. compact hand movement;
4. stable position choices;
5. chord-shape continuity;
6. role-specific behavior.

### 7. Define a fresh evaluator based on raw musical diagnostics

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

Any later composite score formula must live in source control beside the raw metrics.

### 8. Only after the deterministic structure/notation/fretboard system is stable, connect real audio/model evidence

The first clean real-audio adapter must follow:

**full-mixture structure analysis → structure/measure map → role-conditioned note evidence → clean event schema → notation → fretboard decoding.**

Do not import the old V143 scorer/gate maze.

### 9. Map clean analyzer output into the existing `/ai-tab` page-facing contract

The fresh analyzer should emit stable fields that can feed the existing product shell without exposing internal model complexity.

End-to-end acceptance path:

**generate → timing/measure metadata → techniques/render events → watermarked preview → PayPal/free-token unlock reference → full PDF → email/download**

Specifically validate that the fresh analyzer can populate the existing render/PDF inputs:
- tuning;
- tempo;
- time signature;
- key signature if available;
- techniques;
- render events;
- measure grid/structure map projection;
- confidence;
- difficulty;
- final textual tab representation or its successor contract.

### 10. Define the no-human-correction product acceptance gate

Before changing the public product promise, establish a concrete acceptance standard across multiple real songs/roles.

The gate should require, at minimum:
- structurally correct measure/downbeat map;
- no unexplained dropped/added musical events;
- high pitch integrity;
- rhythm that reads naturally without manual respelling;
- physically playable/string-consistent fingering;
- techniques/render metadata that survives to the PDF;
- complete PDF generation from preview through paid/token unlock;
- no manual edit required to make the delivered tab usable.

Keep raw failure reasons visible; do not hide them behind a single score.

## FRESH-CHAT START INSTRUCTION

Use this exact instruction in a new chat:

`Please continue from docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md on branch songsterr-fresh-pipeline-v1. Keep that file updated often while you work. Timing/measure structure is foundational and must precede trusting note placement. Preserve the existing /ai-tab metadata -> technique/render -> watermarked preview -> PayPal/free-token unlock reference -> full PDF -> email/download customer flow. Do not resume the archived V143/Gomyway pipeline unless I explicitly ask.`

## NON-NEGOTIABLES

- canonical checkpoint is `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`;
- branch is `songsterr-fresh-pipeline-v1`;
- old V143 branch remains archive/evidence only;
- **timing/measure structure must be established before trusting note placement in real-audio processing**;
- the structure map must be first-class and consumed by downstream note/rhythm/tab stages;
- preserve the existing `/ai-tab` metadata → technique/render events → watermarked preview → unlock reference/token → full PDF → email/download customer journey;
- no Production or main changes;
- no accidental Modal/GPU/model/professional scorer/training activity;
- no legacy scorer or old failed test becomes a fresh-pipeline gate merely because it exists;
- detected note identity must not be silently altered merely to improve notation appearance;
- checkpoint this file after each meaningful architecture, implementation, or validation milestone.
